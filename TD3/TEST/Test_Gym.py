import TD3.TEST.Test_mem as mem
import gym
env = gym.make("LunarLander-v2")
print(env.observation_space)
print(env.action_space)

# 1. replay buffer 선언
replay_buffer = mem.ReplayBuffer()

# 2. 훈련 시 에피소트의 횟수를 카운팅하기 위한 변수 선언
total_time_steps = 0    # 현재까지 훈련한 시간
time_steps_since_eval = 0   # 네트워크 평가를 위한 카운팅 용
episode_num = 0     # 에피소드 넘버

# 2.1. 1번째 환경을 초기화 한다.
print('Env initial')
obs = env.reset()   # 환경을 초기화 시키고 현재 상태를 받는다.
done = False
episode_reward = 0
episode_time_steps = 0

while total_time_steps < 1000:  # 전체 훈련 시간이 1000초 미만까지 훈련을 수행함.
    env.render()
    # 3. 게임이 종결 되었는지 확인한다. 또는 첫 게임인 경우 이전에 종료되어 한번 패스한다.
    if done:
        if total_time_steps != 0:
            print("Toral T: {}, Ep nub: {}, Ep T:{}, Reward: {}".format(total_time_steps, episode_num,
                                                                        episode_time_steps, episode_reward))
            # 3.1. 정책을 훈련 시킴
            # ...
        if time_steps_since_eval > 100:     # 100초 마다 훈련을 평가함
            time_steps_since_eval %= 100    # time steps since eval이 100인 경우 0으로 초기화
            # 3.2. 검증에 해당되는 경우 검증한다.
            print('Evaluation')

        # 3.3. 환경 초기화
        print('Env initial')
        obs = env.reset()   # 환경을 초기화 시키고 현재 상태를 받는다.
        done = False
        episode_reward = 0
        episode_time_steps = 0

    # 4. 만약 게임이 종료되지 않았다면 현재 상태에 대한 액션을 취한다.
    action = env.action_space.sample()  # 네트워크로 예측한 값임.

    # 5. 선정된 액션을 환경에 넣고 다음 상태, 보상, 게임의 종료 여부를 확인한다.
    new_obs, reward, done, _ = env.step(action)
    done_bool = 0 if done == False else 1   # done이 false면 0, 아니면 1로 반환하는 식
    episode_reward += reward
    # 6. 데이터를 메모리에 저장한다.
    replay_buffer.add((obs, new_obs, action, reward, done_bool))
    # 7. 새로운 상태는 현재 상태가 된다.
    obs = new_obs
    # 8. 1스텝씩 더한다.
    total_time_steps += 1
    time_steps_since_eval += 1
    episode_time_steps += 1



# observation = env.reset()
# for _ in range(1000):

#     action = env.action_space.sample() # your agent here (this takes random actions)
#     observation, reward, done, info = env.step(action)
#     if done:
#         observation = env.reset()
# env.close()