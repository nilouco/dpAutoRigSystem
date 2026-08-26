#import libraries
from maya import cmds
from functools import partial


class MotionCaptureUI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self):
        """ This is the main method to load the Motion Capture UI.
        """
        print("WIP mocap")