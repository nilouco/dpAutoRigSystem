# importing libraries:
from functools import partial

import maya.cmds as cmds

from ..Modules.Library import dpControls as ctrlUtil


# global variables to this module:    
CLASS_NAME = "ColorOverride"
TITLE = "m047_colorOver"
DESCRIPTION = "m048_coloOverDesc"
ICON = "/Icons/dp_colorOverride.png"

DPCO_VERSION = "1.1"

class ColorOverride():
    def __init__(self, *args, **kwargs):
        # call main function
        self.dpColorizeUI(self)


    def dpSetColorToSelect(self, colorIndex, *args):
        """ Get the selection list and set the color to each shape
        """
        selList = cmds.ls(selection=True)
        ctrlUtil.colorShape(selList, colorIndex)
    

    def dpColorizeUI(self, *args):
        """ Show a little window to choose the color of the button and the override the guide.
        """
        #Get Maya colors
        #Manually add the "none" color
        colorList = [[0.627, 0.627, 0.627]]
        #WARNING --> color index in maya start to 1
        colorList += [cmds.colorIndex(iColor, q=True) for iColor in range(1,32)]
                            
        # creating colorIndex Window:
        if cmds.window('dpColorIndexWindow', query=True, exists=True):
            cmds.deleteUI('dpColorIndexWindow', window=True)
        colorIndex_winWidth  = 305
        colorIndex_winHeight = 250
        dpColorIndexWin = cmds.window('dpColorIndexWindow', title='Color Index '+DPCO_VERSION, iconName='dpColorIndex', widthHeight=(colorIndex_winWidth, colorIndex_winHeight), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        colorIndexLayout = cmds.gridLayout('colorIndexLayout', numberOfColumns=8, cellWidthHeight=(20,20))

        # creating buttons
        for colorIndex, colorValues in enumerate(colorList):
            cmds.button('indexColor_'+str(colorIndex)+'_BT', label=str(colorIndex), backgroundColor=(colorValues[0], colorValues[1], colorValues[2]), command=partial(self.dpSetColorToSelect, colorIndex), parent=colorIndexLayout)
        # call colorIndex Window:
        cmds.showWindow(dpColorIndexWin)