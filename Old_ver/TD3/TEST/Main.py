import gym
env = gym.make("LunarLander-v2")
print(env.observation_space)
print(env.action_space)

observation = env.reset()
for _ in range(1000):
    env.render()
    action = env.action_space.sample() # your agent here (this takes random actions)
    observation, reward, done, info = env.step(action)
    print(observation)

    if done:
        observation = env.reset()
env.close()