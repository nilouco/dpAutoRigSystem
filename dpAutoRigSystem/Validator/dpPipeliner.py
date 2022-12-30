# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
from os import walk
from ..Modules.Library import dpUtils


DPPIPELINER_VERSION = 1.0

PIPE_FOLDER = "_dpPipeline"

class Pipeliner(object):
    def __init__(self, dpUIinst, ui=True, verbose=True):
        """ Initialize the module class loading variables.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        self.langDic = dpUIinst.langDic
        self.langName = dpUIinst.langName
        self.ui = ui
        self.verbose = verbose

        

        self.currentAssetName = None
        self.shortAssetName = None

        

    def getAddOnsFolder():
        #(self, *args):
        """
        """
        print("passed by here")
        return PIPE_FOLDER

