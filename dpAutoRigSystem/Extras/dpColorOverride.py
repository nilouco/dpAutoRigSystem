# importing libraries:
import maya.cmds as cmds
from functools import partial

# global variables to this module:    
CLASS_NAME = "ColorOverride"
TITLE = "m047_colorOver"
DESCRIPTION = "m048_coloOverDesc"
ICON = "/Icons/dp_colorOverride.png"

DPCO_VERSION = "1.1"

class ColorOverride():
    def __init__(self, dpUIinst, langDic, langName):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        # call main function
        self.dpMain(self)
    
    
    def dpMain(self, *args):
        """ Main function.
            Call UI.
        """
        self.dpColorizeUI()
    
    
    def dpColorShape(self, objList, color, *args):
        """Create a color override for all shapes from a objList.
        """
        i = color
        # find the color index by names:
        if color   == 'yellow':   i = 17
        elif color == 'red':      i = 13
        elif color == 'blue':     i = 6
        elif color == 'cian':     i = 18
        elif color == 'green':    i = 7
        elif color == 'darkRed':  i = 4
        elif color == 'darkBlue': i = 15
        elif color == 'white':    i = 16
        elif color == 'black':    i = 1
        elif color == 'gray':     i = 3
        elif color == 'none':     i = 0
        # find shapes and apply the color override:
        shapeTypeList = ['nurbsCurve', 'nurbsSurface', 'mesh', 'subdiv']
        if objList:
            for objName in objList:
                objType = cmds.objectType(objName)
                # verify if the object is the shape type:
                if objType in shapeTypeList:
                    # set override as enable:
                    cmds.setAttr(objName+".overrideEnabled", 1)
                    # set color override:
                    cmds.setAttr(objName+".overrideColor", i)
                # verify if the object is a transform type:
                elif objType == "transform":
                    # find all shapes children of the transform object:
                    shapeList = cmds.listRelatives(objName, shapes=True, children=True, fullPath=True)
                    if shapeList:
                        for shape in shapeList:
                            # set override as enable:
                            cmds.setAttr(shape+".overrideEnabled", 1)
                            # set color override:
                            cmds.setAttr(shape+".overrideColor", i)
    
    
    def dpSetColorToSelect(self, colorIndex, *args):
        """ Get the selection list and set the color to each shape
        """
        selList = cmds.ls(selection=True)
        self.dpColorShape(selList, colorIndex)
    
    
    def dpColorizeUI(self, *args):
        """ Show a little window to choose the color of the button and the override the guide.
        """
        # declaring the index color list to override and background color of buttons:
        colorList = [   [0.627, 0.627, 0.627],
                        [0, 0, 0],
                        [0.247, 0.247, 0.247],
                        [0.498, 0.498, 0.498],
                        [0.608, 0, 0.157],
                        [0, 0.016, 0.373],
                        [0, 0, 1],
                        [0, 0.275, 0.094],
                        [0.145, 0, 0.263],
                        [0.780, 0, 0.78],
                        [0.537, 0.278, 0.2],
                        [0.243, 0.133, 0.122],
                        [0.600, 0.145, 0],
                        [1, 0, 0],
                        [0, 1, 0],
                        [0, 0.255, 0.6],
                        [1, 1, 1],
                        [1, 1, 0],
                        [0.388, 0.863, 1],
                        [0.263, 1, 0.635],
                        [1, 0.686, 0.686],
                        [0.890, 0.675, 0.475],
                        [1, 1, 0.384],
                        [0, 0.6, 0.325],
                        [0.627, 0.412, 0.188],
                        [0.620, 0.627, 0.188],
                        [0.408, 0.627, 0.188],
                        [0.188, 0.627, 0.365],
                        [0.188, 0.627, 0.627],
                        [0.188, 0.404, 0.627],
                        [0.435, 0.188, 0.627],
                        [0.627, 0.188, 0.412] ]
                            
        # creating colorIndex Window:
        if cmds.window('dpColorIndexWindow', query=True, exists=True):
            cmds.deleteUI('dpColorIndexWindow', window=True)
        colorIndex_winWidth  = 305
        colorIndex_winHeight = 250
        dpColorIndexWin = cmds.window('dpColorIndexWindow', title='Color Index '+DPCO_VERSION, iconName='dpColorIndex', widthHeight=(colorIndex_winWidth, colorIndex_winHeight), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        colorIndexLayout = cmds.gridLayout('colorIndexLayout', numberOfColumns=8, cellWidthHeight=(20,20))
        
        # creating buttons:
        for colorIndex, colorValues in enumerate(colorList):
            cmds.button('indexColor_'+str(colorIndex)+'_BT', label=str(colorIndex), backgroundColor=(colorValues[0], colorValues[1], colorValues[2]), command=partial(self.dpSetColorToSelect, colorIndex), parent=colorIndexLayout)
        # call colorIndex Window:
        cmds.showWindow(dpColorIndexWin)