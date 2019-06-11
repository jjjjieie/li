
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import platform
import os
import time

from scipy import misc
from io import BytesIO

from PIL import Image
import base64

import atexit

from PIL import ImageGrab

class SF3Env():
    def __init__(self):
        # Load Webdrivers
        # Make sure that the driver files are located in working_dir/driver/
        if platform.system() == 'Darwin':
            self.driver = webdriver.Chrome(os.path.join('driver','chromedriver_mac'))
        elif platform.system() == 'Linux':
            self.driver = webdriver.Chrome(os.path.join('driver','chromedriver_linux'))
        elif platform.system() == 'Windows':
            self.driver = webdriver.Chrome(os.path.join('driver','chromedriver_win.exe'))
        else:
            raise Exception('Unknown OS') 
    
        self.driver.implicitly_wait(3)

        # Recommended window size to run SF3 on web.
        self.driver.set_window_size(1024, 720)
    
        self.driver.get('https://mlcs.yonsei.ac.kr/sf3/index.html')
        
        # Waiting until the page if fully loaded.
        delay = 10 # seconds
        try:
            myElem = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.ID, 'game_frame')))
            print("Page is ready!")
        except TimeoutException:
            print("Timeout")
            exit(0)
        
        # DOM elements on SF3 web
        self.game_frame = self.driver.find_element_by_id('game_frame')
        self.battle_image = self.driver.find_element_by_id('battle_image')
        self.left_blood = self.driver.find_element_by_id('left_blood')
        self.right_blood = self.driver.find_element_by_id('right_blood')

        # Close the chrome at exit.
        def closeWeb(driver):
            driver.close()
        atexit.register(closeWeb, self.driver)

    def _capture(self):
        '''
        Returns the image(PNG format, ndarray) of the webpage.
        The image should be cropped, since it contains useless area.
        '''
        # bim = self.driver.get_screenshot_as_png()
        # im = misc.imread(BytesIO(bim))

        data = self.battle_image.get_attribute("src")
        im = misc.imread(BytesIO(base64.b64decode(data.split(',')[1])))
        
        return im

    def getImage(self):
        '''
        It is recommended to manipulate the image here.
        '''
        im = self._capture()
        return im

    def getBlood(self, p=None):
        '''
        Returns how much blood left in given player.
        '''

        if p=='player1':
            return int(self.left_blood.get_attribute('innerHTML'))
        elif p=='player2':
            return int(self.right_blood.get_attribute('innerHTML'))
        
    def enableAI(self, target=None):
        '''
        Turning on the AI on given side (Left or Right).
        If the side is not given, it turns off AI for both sides.
        '''
        if target == 'left':
            self.send_key(a='left_ai')
        elif target == 'right':
            self.send_key(a='right_ai')
        else:
            # Disable both sides
            self.send_key(a='disable_ai')

    def reward(self, obs):
        '''
        Reward function
        '''
        return obs[0]

    def reset(self):
        '''
        Reset the SF3 environment.
        '''
        self.enableAI(target=None)
        time.sleep(3)
        self.send_key(a='reset')
        time.sleep(1)
    
    def step(self, action):
        '''
        Example code for step.
        It is not allowed to edit the name and the arguments of the function.
        '''

        if action == 0:
            self.send_key(p='player1', a='light_punch')
        elif action == 1:
            self.send_key(p='player1', a='right')
        elif action == 2:
            self.send_key(p='player1', a='heavy_kick')
        else:
            raise Exception('Invalid action input.')

        # Example of the observations
        p1_blood = self.getBlood(p="player1")
        p2_blood = self.getBlood(p="player2")
        print("Left: {}, Right: {}".format(p1_blood, p2_blood))
        
        obs = [p1_blood, p2_blood, self.getImage()]

        # Example of the reward
        reward = self.reward(obs)

        # Example of the reset condition
        if p1_blood <= 0 or p2_blood <= 0:
            done = True
        else:
            done = False

        return obs, reward, done

    def send_key(self, p=None, a=None):
        '''
        Key inputs.
        It is not allowed to edit this part.
        '''
        elem = self.driver.find_element_by_tag_name('body')
        if p=='player1':
            if a=='up':
                elem.send_keys('w')
            if a=='down':
                elem.send_keys('s')
            if a=='right':
                elem.send_keys('d')
            if a=='left':
                elem.send_keys('a')
            if a=='light_punch':
                elem.send_keys('j')
            if a=='heavy_punch':
                elem.send_keys('k')
            if a=='light_kick':
                elem.send_keys('u')
            if a=='heavy_kick':
                elem.send_keys('i')
        elif p=='player2':
            if a=='up':
                elem.send_keys(Keys.ARROW_UP)
            if a=='down':
                elem.send_keys(Keys.ARROW_DOWN)
            if a=='right':
                elem.send_keys(Keys.ARROW_RIGHT)
            if a=='left':
                elem.send_keys(Keys.ARROW_LEFT)
            if a=='light_punch':
                elem.send_keys(Keys.NUMPAD1)
            if a=='heavy_punch':
                elem.send_keys(Keys.NUMPAD2)
            if a=='light_kick':
                elem.send_keys(Keys.NUMPAD4)
            if a=='heavy_kick':
                elem.send_keys(Keys.NUMPAD5)
        else:
            if a=='left_ai':
                elem.send_keys('q')
            if a=='right_ai':
                elem.send_keys('e')
            if a=='disable_ai':
                elem.send_keys('r')
            if a=='reset':
                elem.send_keys('2')
            if a=='pause':
                elem.send_keys(Keys.F2)


'''
Example function to get an action.
'''
import random
def example_func():
    return random.choice([0,1,2])

if __name__ == "__main__":
    '''
    Example of how you should write your own main code for RL.
    '''

    #Initiate the environment
    env = SF3Env()

    # Let's just wait for a few seconds before get started.
    time.sleep(3)

    # For this example, we will run the env for two episodes.
    # In the real training, it should be while loop for with greater episode number.
    for i in range(2):
        print("Episode {}".format(i))

        # For this example, we will run 100 steps.
        # In the real training, it should be while loop for with greater step_per_episode number.
        for j in range(100):
            print("Step {}".format(j))

            # Get an action from the RL network.
            action = example_func()

            # Run the step and take back what you need.
            obs, reward, done = env.step(action=action)

            # If reset condition is met, finish the episode and reset the environment.
            if done:
                print("Done!")
                env.reset()
                break
    
