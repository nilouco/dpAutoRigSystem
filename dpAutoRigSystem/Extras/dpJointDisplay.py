# importing libraries:
from maya import cmds
from maya import mel
from functools import partial

# global variables to this module:
CLASS_NAME = "JointDisplay"
TITLE = "m098_jointDisplay"
DESCRIPTION = "m169_jointDisplayDesc"
ICON = "/Icons/dp_reorderAttr.png"



DP_JOINTDISPLAY_VERSION = 1.0


#Global Lists


class JointDisplay(object):
    def __init__(self, dpUIinst, ui=True, *args, **kwargs):
        self.dpUIinst = dpUIinst
        self.bonelabelList = []
        self.jointLabelList = []
        self.multiChildLabelList = []
        self.noneLabelList = []
        #start
        self.ui = ui
        self.closeUI()
        self.jointDisplayUI()
        
        # Call Main function
        if self.ui:
            self.jointDisplayUI()
            cmds.scriptJob(event=('SelectionChanged', self.refreshPreview), parent='dpRenamerWin', replacePrevious=True, killWithScene=True, compressUndo=True, force=True)

    def closeUI(self, *args, **kwargs):
        if cmds.window('jointDisplayWindow', query=True, exists=True):
            cmds.deleteUI('jointDisplayWindow', window=True)


    def jointDisplayUI(self, *args):

        # Creating window
        jointDisplay_winWidth = 500
        jointDisplay_winHeight = 175
        jointDisplayWindow = cmds.window('jointDisplayWindow', title=self.dpUIinst.lang["m098_jointDisplay"]+' '+str(DP_JOINTDISPLAY_VERSION), widthHeight=(jointDisplay_winWidth, jointDisplay_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)

        # Creating main Layout
        jointDisplayMainLayout = cmds.columnLayout('jointDisplayMainLayout', columnOffset=('both', 5), adjustableColumn=True)

        # Filter
        filterLayout = cmds.columnLayout('filterLayout', adjustableColumn=True, parent=jointDisplayMainLayout)
        jointFilter = cmds.textFieldButtonGrp('jointFilter', label=self.dpUIinst.lang['i268_filterByName'], text="", buttonLabel=self.dpUIinst.lang['m218_search'], buttonCommand="ButtonNone", adjustableColumn=2, parent=filterLayout)
        
        # Boards layout
        boardLayout = cmds.rowColumnLayout('scrollLayout', numberOfColumns=4, rowOffset=[1,'both', 5] ,columnWidth=[(1, 150), (2, 150), (3, 150), (4, 150)], columnSpacing=[(1, 5), (2, 5), (3, 5), (4, 5)], parent=jointDisplayMainLayout)
        
        # Creating boards titles
        cmds.text('boneTitle', label='Bone',parent=boardLayout)
        cmds.text('jointTitle',label='Joint',parent=boardLayout)
        cmds.text('multiChildTitle',label='Multi-Child as box',parent=boardLayout)
        cmds.text('noneTitle', label='None',parent=boardLayout)

        # Creating Boards
        self.boneFieldColunm = cmds.textScrollList('boneFieldColunm', enable=True, append=self.bonelabelList, parent=boardLayout)
        self.jointFieldColunm = cmds.textScrollList('jointFieldColunm', allowMultiSelection=True, append=self.jointLabelList, enable=True, parent=boardLayout)
        self.multiChildFieldColunm = cmds.textScrollList('multiChildFieldColunm', allowMultiSelection=True, append=self.multiChildLabelList, enable=True, parent=boardLayout)
        self.noneFieldColunm = cmds.textScrollList('noneFieldColunm', allowMultiSelection=True, append=self.noneLabelList, enable=True, parent=boardLayout)

        # Button layout
        cmds.separator(style='none', height=10, parent=jointDisplayMainLayout)
        buttonLayout = cmds.rowColumnLayout("buttonLayout", childArray=True ,numberOfColumns=4, columnWidth=[(1, 80), (2, 80), (3, 100),(3, 100)], columnOffset=[(1, "both", 5), (2, "both", 5), (3, "both", 10), (4, "left", 250)], parent=jointDisplayMainLayout)

        # Buttons
        moveRightButton = cmds.button("moveRight", label=self.dpUIinst.lang['c034_move'] + ' <<<', backgroundColor=(0.6, 0.6, 0.6), width=70, command='MovedToRight', parent=buttonLayout)
        moveLeftButton = cmds.button("moveLeft", label=self.dpUIinst.lang['c034_move'] + ' >>>', backgroundColor=(0.6, 0.6, 0.6), width=70, command='MovedLeft', parent=buttonLayout)
        changeAllMenu = cmds.optionMenu('changeAll',label=self.dpUIinst.lang['m098_jointDisplay'], backgroundColor=(0.6, 0.6, 0.6), width = 100, parent=buttonLayout)
        cmds.menuItem( label='Bone', parent=changeAllMenu)
        cmds.menuItem( label='Joint', parent=changeAllMenu )
        cmds.menuItem( label='Multi-Child as box', parent=changeAllMenu )
        cmds.menuItem( label='None', parent=changeAllMenu )
        cancelButton = cmds.button("cancel", label=self.dpUIinst.lang['i132_cancel'], backgroundColor=(0.5, 0.5, 0.5), width=100, command='Cancel', parent=buttonLayout)
        cmds.separator(style='none', height=10, parent=buttonLayout)

        # Call window
        cmds.showWindow(jointDisplayWindow)


    def originalJointList(self):
        """ Search all joints   """
        cmds.ls(type = 'joint')



#TODO
    # FUNCTIONS   
    # -> Build UI -- OK
    # -> List All joint In the scene
    # -> Create a script Job to search any modifications
        # - If selection change
        # - Update all lists
        # - Create active selection
        # - 
    # -> Creat a Function to change to Left or minus value Draw joint
    # -> Creat a Function to change to Right or Plus value Draw joint
    # -> Creat a Function to Set specific value for all selected joints


    # Algoritm

    # -> Populate OriginalList
    # -> Close UI if exists
    # -> Open UI
    # -> List All joints in the scene and show it
    # -> If the search field have any character filter it and populate in the boards.
    # -> If I select any joint in the some board, and press a button, Do this action
    # -> If I choose the button to change all joints, Do this action

    
