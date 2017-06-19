import math
import gym
from gym import spaces
from gym.utils import seeding
import numpy as np

def _isIn(pos, region):
    if pos[0] >= region[0] and pos[0] <= region[1] and\
        pos[1] >= region[2] and pos[1] <= region[3]:
        return True
    else:
        return False

class ObjectTransitionEnv(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 30
    }

    def __init__(self):
        self.min_f = -2.0
        self.max_f = 2.0
        self.region = [0, 80, 0, 40]
        # self.min_x = 0
        # self.max_x = 80
        # self.min_y = 0
        # self.max_y = 40

        self.obstacles = []
        self.obstacles.append([40, 50, 15, 25])
        
        self.goal = [64, 70, 17, 23]

        self.friction = 1.0

        self.low_state = np.array([self.region[0], self.region[2]])
        self.high_state = np.array([self.region[1], self.region[3]])

        self.min_action = np.repeat(self.min_f, 4)
        self.max_action = np.repeat(self.max_f, 4)       

        self.viewer = None

        self.observation_space = spaces.Box(self.low_state, self.high_state)
        self.action_space = spaces.Box(self.min_action, self.max_action)

        self._seed()
        self.reset()

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _step(self, action):
        #x = self.state[0]
        #y = self.state[1]
        position = [self.state[0], self.state[1]]
        f_x = action[0] + action[2]
        f_y = action[1] + action[3]
        v_x = 0
        v_y = 0

        f_sig = math.sqrt(math.pow(f_x, 2) + math.pow(f_x, 2))
        if f_sig > self.friction:
            v_x = v_x * (f_sig - self.friction) / f_sig
            v_y = v_y * (f_sig - self.friction) / f_sig

        position[0] += v_x
        position[1] += v_y

        is_in_goal = _isIn(position, self.goal)
        is_in_obstacles = False
        for obstacle in self.obstacles:
            if _isIn(position, obstacle) is True:
                is_in_obstacles = True
                break

        if (position[0] < self.region[0]): position[0] = self.region[0]
        if (position[0] > self.region[1]): position[0] = self.region[1]
        if (position[1] < self.region[2]): position[1] = self.region[2]
        if (position[1] > self.region[3]): position[1] = self.region[3]        

        done = is_in_goal or is_in_obstacles

        reward = 0
        if is_in_goal:
            reward += 1.0
        if is_in_obstacles:
            reward -= 1.0

        self.state = np.array(position)
        return self.state, reward, done, {}

    def _reset(self):
        self.state = np.array([self.np_random.uniform(low=0, high=20), self.np_random.uniform(low=0, high=40)])
        return np.array(self.state)

#    def get_state(self):
#        return self.state

    def _render(self, mode='human', close=False):
        if close:
            if self.viewer is not None:
                self.viewer.close()
                self.viewer = None
            return

        screen_width = 800
        screen_height = 400

        world_width = self.region[1] - self.region[10]
        scale = screen_width/world_width
        objwidth=40
        objheight=40

        if self.viewer is None:
            from gym.envs.classic_control import rendering
            self.viewer = rendering.Viewer(screen_width, screen_height)

            self.objtrans = rendering.Transform()

            l,r,t,b = -objwidth/2, objwidth/2, -objheight/2, objheight/2
            self.obj = rendering.FilledPolygon([(l,b), (l,t), (r,t), (r,b)])            
            self.obj.add_attr(self.objtrans)
            self.obj.set_color(255,0,0)
            self.viewer.add_geom(self.obj)

            self.render_obts = []
            for obstacle in self.obstacles:
                l,r,t,b = obstacle[0]*scale, obstacle[1]*scale, obstacle[2]*scale, obstacle[3]*scale
                render_obt = rendering.FilledPolygon([(l,b), (l,t), (r,t), (r,b)])
                render_obt.set_color(0,0,0)
                self.viewer.add_geom(render_obt)
                self.render_obts.append(render_obt)

            l,r,t,b = self.region[0]*scale, self.region[1]*scale, self.region[2]*scale, self.region[3]*scale
            self.goal = rendering.FilledPolygon([(l,b), (l,t), (r,t), (r,b)])
            self.goal.set_color(0,255,0)
            self.viewer.add_geom(self.goal)

        self.objtrans.set_translation(self.state[0]*scale, self.state[1]*scale)

        return self.viewer.render(return_rgb_array = mode=='rgb_array')
