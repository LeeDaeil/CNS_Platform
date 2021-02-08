import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Normal, Categorical

LOG_SIG_MAX = 2
LOG_SIG_MIN = -20
epsilon = 1e-6


# Initialize Policy weights
def weights_init_(m):
    if isinstance(m, nn.Linear):
        torch.nn.init.xavier_uniform_(m.weight, gain=1)
        torch.nn.init.constant_(m.bias, 0)


class ValueNetwork(nn.Module):
    def __init__(self, num_inputs, hidden_dim):
        super(ValueNetwork, self).__init__()

        self.linear1 = nn.Linear(num_inputs, hidden_dim)
        self.linear2 = nn.Linear(hidden_dim, hidden_dim)
        self.linear3 = nn.Linear(hidden_dim, 1)

        self.apply(weights_init_)

    def forward(self, state):
        x = F.relu(self.linear1(state))
        x = F.relu(self.linear2(x))
        x = self.linear3(x)
        return x


class QNetwork(nn.Module):
    def __init__(self, num_inputs, num_actions, hidden_dim, discrete=False):
        super(QNetwork, self).__init__()

        self.discrete = discrete

        # Q1 architecture
        if self.discrete:
            self.linear1 = nn.Linear(num_inputs, hidden_dim)
        else:
            self.linear1 = nn.Linear(num_inputs + num_actions, hidden_dim)

        self.linear2 = nn.Linear(hidden_dim, hidden_dim)
        self.linear3 = nn.Linear(hidden_dim, 1)

        # Q2 architecture
        if self.discrete:
            self.linear4 = nn.Linear(num_inputs, hidden_dim)
        else:
            self.linear4 = nn.Linear(num_inputs + num_actions, hidden_dim)

        self.linear5 = nn.Linear(hidden_dim, hidden_dim)
        self.linear6 = nn.Linear(hidden_dim, 1)

        self.apply(weights_init_)

    def forward(self, state, action):
        if self.discrete:
            xu = state
        else:
            xu = torch.cat([state, action], 1)

        x1 = F.relu(self.linear1(xu))
        x1 = F.relu(self.linear2(x1))
        x1 = self.linear3(x1)

        x2 = F.relu(self.linear4(xu))
        x2 = F.relu(self.linear5(x2))
        x2 = self.linear6(x2)

        return x1, x2


class GaussianPolicy(nn.Module):
    def __init__(self, num_inputs, num_actions, hidden_dim, discrete=False, action_space=None):
        super(GaussianPolicy, self).__init__()

        self.linear1 = nn.Linear(num_inputs, hidden_dim)
        self.linear2 = nn.Linear(hidden_dim, hidden_dim)

        self.discrete_linear = nn.Linear(hidden_dim, num_actions)

        self.mean_linear = nn.Linear(hidden_dim, num_actions)
        self.log_std_linear = nn.Linear(hidden_dim, num_actions)

        self.apply(weights_init_)

        # discrete action space
        self.discrete = True if discrete else False

        # action rescaling
        if action_space is None:
            self.action_scale = torch.tensor(1.)
            self.action_bias = torch.tensor(0.)
        else:
            self.action_scale = torch.FloatTensor(
                (action_space.high - action_space.low) / 2.)
            self.action_bias = torch.FloatTensor(
                (action_space.high + action_space.low) / 2.)

    def forward(self, state):
        x = F.relu(self.linear1(state))
        x = F.relu(self.linear2(x))

        if self.discrete:
            x = self.discrete_linear(x)
            return x
        else:
            mean = self.mean_linear(x)
            log_std = self.log_std_linear(x)
            log_std = torch.clamp(log_std, min=LOG_SIG_MIN, max=LOG_SIG_MAX)
            return mean, log_std

    def sample(self, state):
        if self.discrete:
            action_prob = self.forward(state)
            action_prob = F.softmax(action_prob, dim=1)
            action_distribution = Categorical(action_prob)
            action = action_distribution.sample().view(-1, 1)  # pi_theta(s_t)

            # 0 값 방지
            z = (action_prob == 0.0).float() * 1e-8
            log_probs = torch.log(action_prob + z)  # log(pi_theta(s_t))
            """
            현재 액션 1개 Policy 2개 (up, down)
            action      : [[0]],        torch.Tensor
            action_prob : [[0.1, 0.9]], torch.Tensor
            log_prob    : [[0.1, 0.1]], torch.Tensor
            """
            return action, action_prob, log_probs
        else:
            mean, log_std = self.forward(state)
            std = log_std.exp()
            normal = Normal(mean, std)
            x_t = normal.rsample()  # for reparameterization trick (mean + std * N(0,1))
            y_t = torch.tanh(x_t)
            action = y_t * self.action_scale + self.action_bias
            log_prob = normal.log_prob(x_t)
            # Enforcing Action Bound
            log_prob -= torch.log(self.action_scale * (1 - y_t.pow(2)) + epsilon)
            log_prob = log_prob.sum(1, keepdim=True)
            mean = torch.tanh(mean) * self.action_scale + self.action_bias
            """
            action   : [[0.1, 0.1]], torch.Tensor
            log_prob : [[0.1]],      torch.Tensor
            mean     : [[0.1, 0.1]], torch.Tensor
            """
            return action, log_prob, mean


class AIEMSAC:
    def __init__(self, input_shape, output_shape, discrete_mode):
        self.discrete_mode = discrete_mode
        self.policy = GaussianPolicy(input_shape,
                                     output_shape,
                                     hidden_dim=256, discrete=self.discrete_mode)

    def agent_select_action(self, state, evaluate=False):
        state = torch.FloatTensor(state).unsqueeze(0)
        if evaluate is False:
            if self.discrete_mode:
                _, action_probs, _ = self.policy.sample(state)
                action = torch.argmax(action_probs, dim=1, keepdim=True)
            else:
                action, _, _ = self.policy.sample(state)
                """
                action : tensor([[-0.4534,  0.1533]], grad_fn=<AddBackward0>) <class 'torch.Tensor'>
                """
        else:
            _, _, action = self.policy.sample(state)
        return action.detach().cpu().numpy()[0]  # [ ], numpy[0.80986434 0.7939146 ] <class 'numpy.ndarray'>

    def agent_load_model(self, actor_path):
        print('Loading models from {}'.format(actor_path))
        if actor_path is not None:
            self.policy.load_state_dict(torch.load(actor_path))