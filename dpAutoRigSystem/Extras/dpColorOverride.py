# importing libraries:
import maya.cmds as cmds
from functools import partial
from ..Modules.Library import dpControls

# global variables to this module:    
CLASS_NAME = "ColorOverride"
TITLE = "m047_colorOver"
DESCRIPTION = "m048_coloOverDesc"
ICON = "/Icons/dp_colorOverride.png"

DPCO_VERSION = "2.0"

class ColorOverride():
    def __init__(self, dpUIinst, presetDic, presetName, *args, **kwargs):
        # defining variables
        self.dpUIinst = dpUIinst
        self.presetDic = presetDic
        self.presetName = presetName
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
        # call main function
        self.dpColorizeUI(self)


    def dpSetColorIndexToSelect(self, colorIndex, *args):
        """ Get the selection list and set the color index to each shape
        """
        selList = cmds.ls(selection=True)
        self.ctrls.colorShape(selList, colorIndex)
        
        
    def dpSetColorRGBToSelect(self, *args):
        """ Get the selection list and set the color RGB to each shape
        """
        selList = cmds.ls(selection=True)
        colorRGB = cmds.colorSliderGrp(self.colorRGBSlider, query=True, rgbValue=True)
        self.ctrls.colorShape(selList, colorRGB, True)
        
        
    def dpColorizeUI(self, *args):
        """ Show a little window to choose the color of the button and the override the guide.
        """
        #Get Maya colors
        #Manually add the "none" color
        colorList = [[0.627, 0.627, 0.627]]
        #WARNING --> color index in maya start to 1
        colorList += [cmds.colorIndex(iColor, q=True) for iColor in range(1,32)]
        
        # creating colorOverride Window:
        if cmds.window('dpColorOverrideWindow', query=True, exists=True):
            cmds.deleteUI('dpColorOverrideWindow', window=True)
        colorOverride_winWidth  = 170
        colorOverride_winHeight = 115
        dpColorOverrideWin = cmds.window('dpColorOverrideWindow', title='Color Override '+DPCO_VERSION, iconName='dpColorOverride', widthHeight=(colorOverride_winWidth, colorOverride_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        
        # creating layout:
        colorTabLayout = cmds.tabLayout('colorTabLayout', innerMarginWidth=5, innerMarginHeight=5, parent=dpColorOverrideWin)
        
        # Index layout:
        colorIndexLayout = cmds.gridLayout('colorIndexLayout', numberOfColumns=8, cellWidthHeight=(20,20), parent=colorTabLayout)
        # creating buttons
        for colorIndex, colorValues in enumerate(colorList):
            cmds.button('indexColor_'+str(colorIndex)+'_BT', label=str(colorIndex), backgroundColor=(colorValues[0], colorValues[1], colorValues[2]), command=partial(self.dpSetColorIndexToSelect, colorIndex), parent=colorIndexLayout)
        
        # RGB layout:
        colorRGBLayout = cmds.columnLayout('colorRGBLayout', adjustableColumn=True, columnAlign='left', rowSpacing=10, parent=colorTabLayout)
        cmds.separator(height=10, style='none', parent=colorRGBLayout)
        self.colorRGBSlider = cmds.colorSliderGrp('colorRGBSlider', label='Color', columnAlign3=('right', 'left', 'left'), columnWidth3=(30, 60, 50), columnOffset3=(10, 10, 10), rgbValue=(0, 0, 0), changeCommand=self.dpSetColorRGBToSelect, parent=colorRGBLayout)
        
        # renaming tabLayouts:
        cmds.tabLayout(colorTabLayout, edit=True, tabLabel=((colorIndexLayout, "Index"), (colorRGBLayout, "RGB")))
        # call colorIndex Window:
        cmds.showWindow(dpColorOverrideWin)