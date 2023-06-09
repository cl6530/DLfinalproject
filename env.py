import gym
import numpy as np
import pywt

class StockTradingEnv(gym.Env):
    '''
    Trading Simulator
    
    '''
    def __init__(self, stock_returns, transaction_cost, init_port):
        '''
        init methods, takes an array of returns as input
        '''
        super(StockTradingEnv, self).__init__()

        self.transaction_cost = transaction_cost
        self.init_port = init_port
        self.current_portfolio = init_port #Initialize the portforlio
        self.portfolio_history = [init_port, init_port]  # Add portfolio_history
        self.returns = stock_returns
        self.current_step = 4
        self.position = 0
        try:
          self.current_state = self._get_next_state()
        except:
          pass

        # Action space: {0: 'short', 1: 'stay', 2: 'long'}
        self.action_space = gym.spaces.Discrete(3)

        # State space: [1-day return, 5-day return]
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(2,), dtype=np.float32)


    def _get_next_state(self):
      '''
      using 1-day and 5-day return as the next state
      '''
      one_day_return = self.returns[self.current_step]
      five_day_return = self.returns[self.current_step - 4]
      return np.array([one_day_return, five_day_return])

    
    def _get_reward(self):
      '''
      #calculate reward
      #when posiiton is long, use 1 day return as reward
      #when position is short, use negative 1 day return as reward
      #FIXME: modify this function for experiment
      '''
      one_day_return = self.returns[self.current_step]
      if self.position == 1:
        return one_day_return
      elif self.position == -1:
        return -one_day_return
      else:
        return 0
    

    def step(self, action):
      ''' 
      step function
      1. change the position based on given action
      2. calculate next state
      3. get reward from state transition (one day return)
      4. return a transition tuple
      '''
      assert self.action_space.contains(action), f"{action} is an invalid action"

      # current state
      state = self.current_state

      # Calculate reward based on the chosen action

      # FIXED: Modify this part to add transcation cost
      # Calculate reward based on the chosen action
      #one_day_return = self.returns[self.current_step]
      if action == 0:  # short
          
          if self.position != -1:
             self.position = -1
             self.current_portfolio = (self.current_portfolio * (1 + self._get_reward())) * (1 - self.transaction_cost)
          else:
             self.current_portfolio = (self.current_portfolio * (1 + self._get_reward())) 

          self.portfolio_history.append(self.current_portfolio)  # Add current_portfolio to portfolio_history

      elif action == 1:  # stay
          if self.position != 0:
             self.position = 0
             self.current_portfolio = (self.current_portfolio * (1 + self._get_reward())) * (1 - self.transaction_cost)
          else:
             pass
          self.portfolio_history.append(self.current_portfolio)  # Add current_portfolio to portfolio_history

      elif action == 2:  # long
          if self.position != 1:
             self.position = 1
             self.current_portfolio = (self.current_portfolio * (1 + self._get_reward())) * (1 - self.transaction_cost)
          else:
             self.current_portfolio = (self.current_portfolio * (1 + self._get_reward())) 
          self.portfolio_history.append(self.current_portfolio)  # Add current_portfolio to portfolio_history
      
      # Calculate reward based on portfolio_history
      current_portfolio = self.current_portfolio
      previous_portfolio = self.portfolio_history[-2]
      reward = (current_portfolio - previous_portfolio) / previous_portfolio
      
      
      #next_state
      next_state = self._get_next_state()
      self.current_state = next_state

      # Update the current step
      self.current_step += 1

      #reward
      #reward = self._get_reward()

      # Check if the episode is done (reached the end of the stock prices data)
      done = self.current_step >= len(self.returns) - 1
      return state, action,reward,next_state, done

    def reset(self,stock_returns):
      '''
      reset the env with a new series of returns
      '''
      self.returns = stock_returns
      self.current_step = 5
      return self._get_next_state()


    def close(self):
      pass