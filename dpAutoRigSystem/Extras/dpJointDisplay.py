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

IGNORE_LIST = ['persp', 'top', 'front', 'side'] # WIP To Delete

boneLabelList = []
jointLabelList = []
multiChildLabelList = []
noneLabelList = []


class JointDisplay(object):
    def __init__(self, dpUIinst, ui=True, *args, **kwargs):
        self.dpUIinst = dpUIinst
        # call main function
        if ui:
            print(f'boneLabelList {boneLabelList}, jointLabelList {jointLabelList}, multiChildLabelList {multiChildLabelList}, noneLabelList {noneLabelList}')
            self.refreshLists(self)
            print('\nCalled Refresh Function\n')
            self.dpJointDisplayUI(self)
            
            print(f'boneLabelList {boneLabelList}, jointLabelList {jointLabelList}, multiChildLabelList {multiChildLabelList}, noneLabelList {noneLabelList}')
            
    
    def refreshLists(self,*args, **kwargs):
        """ Refresh the code
        """
        self.getJointList(self)
        self.populateLabelList(self)
    
    def dpCloseJointDisplayUI(self, *args):
        if cmds.window('dpJointDisplayWindow', query=True, exists=True):
            cmds.deleteUI('dpJointDisplayWindow', window=True)

    def getItemFilter(self, *args):
        """ Create a selection filter by transform type excluding the ignoreIt list.
        """
        self.itemF = cmds.itemFilter(byType="joint")
        for ignoreIt in IGNORE_LIST:
            self.itemF = cmds.itemFilter(difference=(self.itemF, cmds.itemFilter(byName=ignoreIt)))
        return self.itemF
    
    def dpJointDisplayUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        # creating dpJointDisplayUI Window:
        self.dpCloseJointDisplayUI()
        jointDisplay_winWidth  = 500
        jointDisplay_winHeight = 175
        dpJointDisplayWin = cmds.window('dpJointDisplayWindow', title=self.dpUIinst.lang["m098_jointDisplay"]+" "+str(DP_JOINTDISPLAY_VERSION), widthHeight=(jointDisplay_winWidth, jointDisplay_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)

        # creating Main layout:
        jointDisplayMainLayout = cmds.columnLayout('jointDisplayMainLayout', columnOffset=('both', 5), adjustableColumn=True)
        
        # filter
        filterLayout = cmds.columnLayout("filterLayout", adjustableColumn=True, parent=jointDisplayMainLayout)
        self.jointFilter = cmds.textFieldButtonGrp("jointFilter", label=self.dpUIinst.lang['i268_filterByName'], text="", buttonLabel=self.dpUIinst.lang['m004_select']+" "+self.dpUIinst.lang['i211_all'], buttonCommand="TESTEEE####", changeCommand=self.refreshLists, adjustableColumn=2, parent=filterLayout)

        # creating column Layout
        colunmLayout = cmds.rowColumnLayout('scrollLayout', numberOfColumns=4, rowOffset=[1,'both', 5] ,columnWidth=[(1, 150), (2, 150), (3, 150), (4, 150)], columnSpacing=[(1, 5), (2, 5), (3, 5), (4, 5)], parent=jointDisplayMainLayout)

        # creating titles
        boneTitle = cmds.text('boneTitle', label='Bone',parent=colunmLayout)
        jointTitle = cmds.text('jointTitle',label='Joint',parent=colunmLayout)
        multiChildTitle = cmds.text('multiChildTitle',label='Multi-Child as box',parent=colunmLayout)
        noneTitle = cmds.text('noneTitle', label='None',parent=colunmLayout)

        boneFieldColunm = cmds.textScrollList('boneFieldColunm', parent=colunmLayout, allowMultiSelection=True, append=boneLabelList)
        jointFieldColunm = cmds.textScrollList('jointFieldColunm',parent=colunmLayout, allowMultiSelection=True, append=jointLabelList)
        multiChildFieldColunm = cmds.textScrollList('multiChildFieldColunm',parent=colunmLayout, allowMultiSelection=True, append=multiChildLabelList)
        noneFieldColunm = cmds.textScrollList('noneFieldColunm',parent=colunmLayout, allowMultiSelection=True, append=noneLabelList)

        # bottom layout for buttons
        cmds.separator(style='none', height=10, parent=jointDisplayMainLayout)
        buttonLayout = cmds.rowColumnLayout("buttonLayout", childArray=True ,numberOfColumns=3, columnWidth=[(1, 80), (2, 80), (3, 100)], columnOffset=[(1, "both", 5), (2, "both", 5), (3, "both", 5)], parent=jointDisplayMainLayout)
        cmds.button("moveRight", label=self.dpUIinst.lang['c034_move'] + ' <<<', backgroundColor=(0.6, 0.6, 0.6), width=70, command='MovedToRight', parent=buttonLayout)
        cmds.button("moveLeft", label=self.dpUIinst.lang['c034_move'] + ' >>>', backgroundColor=(0.6, 0.6, 0.6), width=70, command='MovedLeft', parent=buttonLayout)
        cmds.button("Cancel", label=self.dpUIinst.lang['i132_cancel'], backgroundColor=(0.5, 0.5, 0.5), width=100, command='Cancel', parent=buttonLayout)
        cmds.separator(style='none', height=10, parent=buttonLayout)

        # call dpJointDisplayUI Window:
        cmds.showWindow(dpJointDisplayWin)
    
    def getJointList(self, *args, **kwargs):
        """ Get all joints in the scene
        """
        jointList = cmds.ls(type='joint')
        if cmds.objExists(jointList[0]):
            return jointList
    
    def populateLabelList(self, *args, **kwargs):
        """ Populate each list with label joint type
        """
        
        if cmds.objExists(self.getJointList(self)[0]):
            for jnt in self.getJointList(self):
                if cmds.getAttr(jnt +'.drawStyle') == 0:
                    try:
                        boneLabelList.append(jnt)
                        print(f'{jnt} was appended to boneLabelList')
                    except:
                        pass
                if cmds.getAttr(jnt +'.drawStyle') == 1:
                    try:
                        multiChildLabelList.append(jnt)
                        print(f'{jnt} was appended to multiChildLabelList')
                    except:
                        pass
                if cmds.getAttr(jnt +'.drawStyle') == 2:
                    try:
                        noneLabelList.append(jnt)
                        print(f'{jnt} was appended to noneLabelList')
                    except:
                        pass
                if cmds.getAttr(jnt +'.drawStyle') == 3:
                    try:
                        jointLabelList.append(jnt)
                        print(f'{jnt} was appended to jointLabelList')
                    except:
                        pass


    # def mainfilter():
    #     """ Filter list to populate the 
    #     """

    #     #TODO
    #     # create a filter to populate list that will be searched 

    
    # def refreshLists(self,*args, **kwargs):
    #     """ Refresh the code
    #     """
    #     self.getJointList()
    #     self.populateLabelList()


        
        #TODO
        # read all joints
        # populate fields

    # def activeSelectionBoard():
    #     """ Find the active selection and indicate the board
    #     """




