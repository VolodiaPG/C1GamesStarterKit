from RL import *

### Training Pong ###

# Hyperparameters
learning_rate=1e-4
MAX_ITERS = 10000 # increase the maximum number of episodes, since Pong is more complex!

# Model and optimizer
pong_model = create_pong_model()
optimizer = tf.keras.optimizers.Adam(learning_rate)

# plotting
smoothed_reward = mdl.util.LossHistory(smoothing_factor=0.9)
plotter = mdl.util.PeriodicPlotter(sec=5, xlabel='Iterations', ylabel='Rewards')
memory = Memory()

for i_episode in range(MAX_ITERS):

  plotter.plot(smoothed_reward.get())

  # Restart the environment
  observation = env.reset()
  previous_frame = mdl.lab3.preprocess_pong(observation)

  while True:
      # Pre-process image 
      current_frame = mdl.lab3.preprocess_pong(observation)
      
      '''TODO: determine the observation change
      Hint: this is the difference between the past two frames'''
      obs_change = current_frame - previous_frame
      
      '''TODO: choose an action for the pong model, using the frame difference, and evaluate'''
      action = choose_action(pong_model, obs_change)
      # Take the chosen action
      next_observation, reward, done, info = env.step(action)

      '''TODO: save the observed frame difference, the action that was taken, and the resulting reward!'''
      memory.add_to_memory(obs_change, action, reward)
      
      # is the episode over? did you crash or do so well that you're done?
      if done:
          # determine total reward and keep a record of this
          total_reward = sum(memory.rewards)
          smoothed_reward.append( total_reward )

          # begin training
          train_step(pong_model, 
                     optimizer, 
                     observations = np.stack(memory.observations, 0), 
                     actions = np.array(memory.actions),
                     discounted_rewards = discount_rewards(memory.rewards))
          
          memory.clear()
          break

      observation = next_observation
      previous_frame = current_frame
