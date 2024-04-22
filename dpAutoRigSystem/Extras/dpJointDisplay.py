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

# IGNORE_LIST = ['persp', 'top', 'front', 'side'] # WIP To Delete


class JointDisplay(object):
    def __init__(self, dpUIinst, ui=True, *args, **kwargs):
        self.dpUIinst = dpUIinst
        self.ui = ui
        # joints lists 
        self.allJointsList = []
        self.boneLabelList = []
        self.jointLabelList = []
        self.multiChildLabelList = []
        self.noneLabelList = []
        # call main function
        if self.ui:
            self.refreshLists(self)
            self.dpJointDisplayUI(self)
            #cmds.scriptJob(event=('SelectionChanged', self.refreshLists), parent='dpJointDisplayWindow', replacePrevious=True, killWithScene=True, compressUndo=True, force=True)


    
    def dpCloseJointDisplayUI(self, *args):
        if cmds.window('dpJointDisplayWindow', query=True, exists=True):
            cmds.deleteUI('dpJointDisplayWindow', window=True)

    # def getItemFilter(self, *args, **kwargs):
    #     """ Create a selection filter by transform type excluding the ignoreIt list.
    #     """
    #     self.itemF = cmds.itemFilter(byName= "")
    #     for ignoreIt in IGNORE_LIST:
    #         self.itemF = cmds.itemFilter(difference=(self.itemF, cmds.itemFilter(byName=ignoreIt)))
    #     return self.itemF
    
    def dpJointDisplayUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        # call close UI function
        self.dpCloseJointDisplayUI()
        # ctarting UI
        jointDisplay_winWidth  = 500
        jointDisplay_winHeight = 175
        dpJointDisplayWin = cmds.window('dpJointDisplayWindow', title=self.dpUIinst.lang["m098_jointDisplay"]+" "+str(DP_JOINTDISPLAY_VERSION), widthHeight=(jointDisplay_winWidth, jointDisplay_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)

        # creating Main layout:
        jointDisplayMainLayout = cmds.columnLayout('jointDisplayMainLayout', columnOffset=('both', 5), adjustableColumn=True)
        
        # filter
        filterLayout = cmds.columnLayout("filterLayout", adjustableColumn=True, parent=jointDisplayMainLayout)
        self.jointFilter = cmds.textFieldButtonGrp("jointFilter", label=self.dpUIinst.lang['i268_filterByName'], text="", buttonLabel=self.dpUIinst.lang['m004_select']+" "+self.dpUIinst.lang['i211_all'], buttonCommand="Test", changeCommand=self.refreshLists, adjustableColumn=2, parent=filterLayout)

        # creating column Layout
        colunmLayout = cmds.rowColumnLayout('scrollLayout', numberOfColumns=4, rowOffset=[1,'both', 5] ,columnWidth=[(1, 150), (2, 150), (3, 150), (4, 150)], columnSpacing=[(1, 5), (2, 5), (3, 5), (4, 5)], parent=jointDisplayMainLayout)

        # creating titles
        boneTitle = cmds.text('boneTitle', label='Bone',parent=colunmLayout)
        jointTitle = cmds.text('jointTitle',label='Joint',parent=colunmLayout)
        multiChildTitle = cmds.text('multiChildTitle',label='Multi-Child as box',parent=colunmLayout)
        noneTitle = cmds.text('noneTitle', label='None',parent=colunmLayout)

        # bone display panels
        # boneFieldColunm = cmds.textScrollList('boneFieldColunm', parent=colunmLayout, allowMultiSelection=True, append=self.boneLabelList, enable=True)
        self.boneFieldColunm = cmds.textScrollList('boneFieldColunm', enable=True, append=self.boneLabelList, parent=colunmLayout, allowMultiSelection=True)
        self.jointFieldColunm = cmds.textScrollList('jointFieldColunm',enable=True, parent=colunmLayout, allowMultiSelection=True, append=self.jointLabelList)
        self.multiChildFieldColunm = cmds.textScrollList('multiChildFieldColunm', enable=True, parent=colunmLayout, allowMultiSelection=True, append=self.multiChildLabelList)
        self.noneFieldColunm = cmds.textScrollList('noneFieldColunm',enable=True, parent=colunmLayout, allowMultiSelection=True, append=self.noneLabelList)

        # bottom layout for buttons
        cmds.separator(style='none', height=10, parent=jointDisplayMainLayout)
        buttonLayout = cmds.rowColumnLayout("buttonLayout", childArray=True ,numberOfColumns=4, columnWidth=[(1, 80), (2, 80), (3, 100),(3, 100)], columnOffset=[(1, "both", 5), (2, "both", 5), (3, "both", 10), (4, "left", 250)], parent=jointDisplayMainLayout)
        
        # defining move buttons
        cmds.button("moveRight", label=self.dpUIinst.lang['c034_move'] + ' <<<', backgroundColor=(0.6, 0.6, 0.6), width=70, command='MovedToRight', parent=buttonLayout)
        cmds.button("moveLeft", label=self.dpUIinst.lang['c034_move'] + ' >>>', backgroundColor=(0.6, 0.6, 0.6), width=70, command='MovedLeft', parent=buttonLayout)
        changeAllMenu = cmds.optionMenu('changeAll',label=self.dpUIinst.lang['m098_jointDisplay'], backgroundColor=(0.6, 0.6, 0.6), width = 100, parent=buttonLayout)
        cmds.menuItem( label='Bone', parent=changeAllMenu)
        cmds.menuItem( label='Joint', parent=changeAllMenu )
        cmds.menuItem( label='Multi-Child as box', parent=changeAllMenu )
        cmds.menuItem( label='None', parent=changeAllMenu )
        cmds.button("cancel", label=self.dpUIinst.lang['i132_cancel'], backgroundColor=(0.5, 0.5, 0.5), width=100, command='Cancel', parent=buttonLayout)
        cmds.separator(style='none', height=10, parent=buttonLayout)

        # call dpJointDisplayUI Window:
        cmds.showWindow(dpJointDisplayWin)
    

    def refreshLists(self,*args, **kwargs):
        """ Refresh the code
        """
        self.getJointList(self)
        self.populateLabelList(self)
        self.dpJointDisplayUI(self)


    def getJointList(self, *args, **kwargs):
        """ Get all joints in the scene
        """
        getlistPass = 0
        jointList = cmds.ls(type='joint')
        if jointList:
            for joint in jointList:
                self.allJointsList.append(joint)
            print(f'All joints List : {self.allJointsList}')
            print(f'Pass Get List : {getlistPass}')

            return self.allJointsList
        else:
            return None

    
    def populateLabelList(self, *args, **kwargs):
        """ Populate each list with label joint type
        """
        if self.allJointsList:
            print(f'LIST ALL JOINT {self.allJointsList}')
            
            for jnt in self.allJointsList:
                if cmds.getAttr(jnt +'.drawStyle') == 0:
                    try:
                        self.boneLabelList.append(jnt)
                        print(f'{jnt} was appended to boneLabelList')
                    except:
                        pass
                if cmds.getAttr(jnt +'.drawStyle') == 1:
                    try:
                        self.multiChildLabelList.append(jnt)
                        print(f'{jnt} was appended to multiChildLabelList')
                    except:
                        pass
                if cmds.getAttr(jnt +'.drawStyle') == 2:
                    try:
                        self.noneLabelList.append(jnt)
                        print(f'{jnt} was appended to noneLabelList')
                    except:
                        pass
                if cmds.getAttr(jnt +'.drawStyle') == 3:
                    try:
                        self.jointLabelList.append(jnt)
                        print(f'{jnt} was appended to jointLabelList')
                    except:
                        pass

    def movedToRight(self):
        """ """
        # Get active selection of button list
        # Change the current joint drawStyle label
        # Call refresh list
        # 
    
    
    
    
    def activeSelection():
        """ Get the active selection
        """
    
        #TODO
        # - Search the active selection


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



    # LAST STOP
    
    # - Do the move button  function