# importing libraries:
from maya import cmds
from maya import mel
from functools import partial

# global variables to this module:
CLASS_NAME = "JointDisplay"
TITLE = "m233_jointDisplay"
DESCRIPTION = "m234_jointDisplayDesc"
ICON = "/Icons/dp_jointDisplay.png"


DP_JOINTDISPLAY_VERSION = 1.0


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
        self.selectionUiList = []
        self.selectedBoard = 0
        self.allBoardList = ['boneFieldcolumn', 'multiChildFieldcolumn', 'noneFieldcolumn', 'jointFieldcolumn']
        self.destinationBoardIndex = 0
        # call main function
        if self.ui:
            self.dpJointDisplayUI()
            self.refreshLists()
            cmds.scriptJob(event=('SelectionChanged', self.refreshLists), parent='dpJointDisplayWindow', replacePrevious=True, killWithScene=True, compressUndo=True, force=True)


    def dpJointDisplayUI(self, *args):
        """ Create a window in order to load the joints in the scene.
        """
        # call close UI function
        self.dpUIinst.utils.closeUI('dpJointDisplayWindow')
        # starting UI
        jointDisplay_winWidth  = 660
        jointDisplay_winHeight = 410
        dpJointDisplayWin = cmds.window('dpJointDisplayWindow', title=self.dpUIinst.lang["m233_jointDisplay"]+" "+str(DP_JOINTDISPLAY_VERSION), widthHeight=(jointDisplay_winWidth, jointDisplay_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)

        # creating Main layout:
        jointDisplayMainLayout = cmds.columnLayout('jointDisplayMainLayout', columnOffset=('both', 5), adjustableColumn=True)
        
        # filter
        cmds.separator(style='none', height=10, parent=jointDisplayMainLayout)
        filterLayout = cmds.columnLayout("filterLayout", adjustableColumn=True, parent=jointDisplayMainLayout)
        self.jointFilter = cmds.textFieldGrp("jointFilter", label=self.dpUIinst.lang['i268_filterByName'], text="", textChangedCommand=self.refreshLists, adjustableColumn=2, parent=filterLayout)
        cmds.separator(style='none', height=5, parent=filterLayout)

        # bone display panels
        scrollLayout = cmds.paneLayout("scrollLayout", configuration="vertical4", separatorThickness=5.0, width=400, parent=jointDisplayMainLayout)
        boneColumnLayout = cmds.columnLayout('boneColumnLayout', columnOffset=('both', 1), adjustableColumn=True, parent=scrollLayout)
        multiColumnLayout = cmds.columnLayout('multiColumnLayout', columnOffset=('both', 1), adjustableColumn=True, parent=scrollLayout)
        noneColumnLayout = cmds.columnLayout('noneColumnLayout', columnOffset=('both', 1), adjustableColumn=True, parent=scrollLayout)
        jointColumnLayout = cmds.columnLayout('jointColumnLayout', columnOffset=('both', 1), adjustableColumn=True, parent=scrollLayout)
        cmds.text('boneTitleTXT', label='Bone', font="boldLabelFont", parent=boneColumnLayout)
        cmds.text('multiChildTitleTXT', label='Multi-Child as box', font="boldLabelFont", parent=multiColumnLayout)
        cmds.text('noneTitleTXT', label='None', font="boldLabelFont", parent=noneColumnLayout)
        cmds.text('jointTitleTXT', label='Joint', font="boldLabelFont", parent=jointColumnLayout)
        cmds.separator(style='none', height=5, parent=boneColumnLayout)
        cmds.separator(style='none', height=5, parent=multiColumnLayout)
        cmds.separator(style='none', height=5, parent=noneColumnLayout)
        cmds.separator(style='none', height=5, parent=jointColumnLayout)
        self.boneFieldcolumn = cmds.textScrollList(self.allBoardList[0], enable=True, parent=boneColumnLayout, allowMultiSelection=True, selectCommand=partial(self.activeSelection, 0), deselectAll=True, height=300)
        self.multiChildFieldcolumn = cmds.textScrollList(self.allBoardList[1], enable=True, parent=multiColumnLayout, allowMultiSelection=True, selectCommand=partial(self.activeSelection, 1), deselectAll=True, height=300)
        self.noneFieldcolumn = cmds.textScrollList(self.allBoardList[2],enable=True, parent=noneColumnLayout, allowMultiSelection=True, selectCommand=partial(self.activeSelection, 2), deselectAll=True, height=300)
        self.jointFieldcolumn = cmds.textScrollList(self.allBoardList[3],enable=True, parent=jointColumnLayout, allowMultiSelection=True, selectCommand=partial(self.activeSelection, 3), deselectAll=True, height=300)
    
        # bottom layout for buttons
        cmds.separator(style='none', height=10, parent=jointDisplayMainLayout)
        buttonLayout = cmds.rowColumnLayout("buttonLayout", childArray=True, numberOfColumns=3, columnWidth=[(1, 160), (2, 100), (3, 160)], columnOffset=[(1, "both", 5), (2, "both", 80), (3, "both", 5)], adjustableColumn=2, parent=jointDisplayMainLayout)
        
        # defining move buttons
        cmds.button("moveRightBT", label=self.dpUIinst.lang['c034_move']+' >>', backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.moveToRight, parent=buttonLayout)
        self.changeAllToMenu = cmds.optionMenu('chabgeAllTo',label=self.dpUIinst.lang['i359_changeTo']+' :', width = 200, parent=buttonLayout, changeCommand= self.changeAllToButton)
        cmds.menuItem( label='Bone', parent=self.changeAllToMenu)
        cmds.menuItem( label='Multi-Child as box', parent=self.changeAllToMenu )
        cmds.menuItem( label='None', parent=self.changeAllToMenu )
        cmds.menuItem( label='Joint', parent=self.changeAllToMenu )
        cmds.button("moveLeftBT", label='<< '+self.dpUIinst.lang['c034_move'], backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.moveToLeft, parent=buttonLayout)

        # call dpJointDisplayUI Window:
        cmds.showWindow(dpJointDisplayWin)
    

    def refreshLists(self, *args):
        """ Refresh the code
        """
        self.cleanAllLists()
        self.updateAllJointList()
        self.populateLabelList()
        self.refreshPreview()


    def updateAllJointList(self, *args):
        """ Get all joints in the scene and update the allJointsList variable.
        """
        self.allJointsList = cmds.ls(selection=False, type='joint')
        writtenValue = cmds.textFieldGrp(self.jointFilter, query=True, text=True)
        if not writtenValue == "" and not writtenValue == " ":
            self.allJointsList = self.dpUIinst.utils.filterName(writtenValue, cmds.ls(selection=False, type='joint'), " ")


    def populateLabelList(self, *args):
        """ Populate each list with label joint type.
        """
        if self.allJointsList:
            for jnt in self.allJointsList:
                if cmds.getAttr(jnt +'.drawStyle') == 0:
                    self.boneLabelList.append(jnt)
                    self.selectedBoard = 0
                elif cmds.getAttr(jnt +'.drawStyle') == 1:
                    self.multiChildLabelList.append(jnt)                    
                    self.selectedBoard = 1
                elif cmds.getAttr(jnt +'.drawStyle') == 2:
                    self.noneLabelList.append(jnt)
                    self.selectedBoard = 2
                elif cmds.getAttr(jnt +'.drawStyle') == 3:
                    self.jointLabelList.append(jnt)
                    self.selectedBoard = 3


    def refreshPreview(self, *args):
        """ Refresh the preview of each board.
        """
        # BoneFieldcolumn board
        cmds.textScrollList(self.boneFieldcolumn, edit=True, removeAll=True)
        cmds.textScrollList(self.boneFieldcolumn, edit=True, append=self.boneLabelList)
        # BultiChildFieldcolumn board
        cmds.textScrollList(self.multiChildFieldcolumn, edit=True, removeAll=True)
        cmds.textScrollList(self.multiChildFieldcolumn, edit=True, append=self.multiChildLabelList)
        # BoneFieldcolumn board
        cmds.textScrollList(self.noneFieldcolumn, edit=True, removeAll=True)
        cmds.textScrollList(self.noneFieldcolumn, edit=True, append=self.noneLabelList)
        # JointFieldcolumn board
        cmds.textScrollList(self.jointFieldcolumn, edit=True, removeAll=True)
        cmds.textScrollList(self.jointFieldcolumn, edit=True, append=self.jointLabelList)
    

    def cleanAllLists(self, *args):
        """ Clear all Lists
        """
        self.allJointsList.clear()
        self.boneLabelList.clear()
        self.multiChildLabelList.clear()
        self.noneLabelList.clear()
        self.jointLabelList.clear()


    def moveToRight(self, *args):
        """ Button to move the selected joints to the right board
        """
        # Get active selection of button list
        if self.selectionUiList:
            currentDrawStyle = cmds.getAttr(self.selectionUiList[0]+'.drawStyle')
            if currentDrawStyle < 3:
                for jnt in self.selectionUiList:
                    cmds.setAttr(jnt +'.drawStyle', currentDrawStyle + 1)
                self.destinationBoardIndex = currentDrawStyle + 1
            else:
                currentDrawStyle = 0
                for jnt in self.selectionUiList: 
                    cmds.setAttr(jnt +'.drawStyle', currentDrawStyle)
                self.destinationBoardIndex = 0
            self.refreshLists()
            self.keepSelectedObj()
    
    
    def moveToLeft(self, *args):
        """ Button to move the selected joints to the left board 
        """
        # Get active selection of button list
        if self.selectionUiList:
            currentDrawStyle = cmds.getAttr(self.selectionUiList[0]+'.drawStyle')
            if currentDrawStyle > 0 < 3:
                for jnt in self.selectionUiList:
                    cmds.setAttr(jnt +'.drawStyle', currentDrawStyle - 1)
                self.destinationBoardIndex = currentDrawStyle - 1
            else: 
                currentDrawStyle = 3
                for jnt in self.selectionUiList:
                    cmds.setAttr(jnt +'.drawStyle', currentDrawStyle)
                self.destinationBoardIndex = 3
            self.refreshLists()
            self.keepSelectedObj()


    def changeAllToButton(self, *args):
        """ Change all joints to the selected drawStyle.
        """
        selectedLabel = cmds.optionMenu(self.changeAllToMenu, query=True, value=True)
        if selectedLabel == 'Bone':
            self.setAllDrawStyle(0)
        elif selectedLabel == 'Multi-Child as box':
            self.setAllDrawStyle(1)
        elif selectedLabel == 'None':
            self.setAllDrawStyle(2)
        elif selectedLabel == 'Joint':
            self.setAllDrawStyle(3)


    def setAllDrawStyle(self, drawStyleIndex, *args):
        """ Set all joints to the selected drawStyle.
        """        
        self.allJointsList
        if self.allJointsList:
            for jnt in self.allJointsList:
                cmds.setAttr(f"{jnt}.drawStyle", drawStyleIndex)
                self.selectionUiList.append(jnt)
        self.destinationBoardIndex = drawStyleIndex
        self.refreshLists()
                
    
    def keepSelectedObj(self, *args):
        """ Mantain ative selected joints.
        """
        selectedItems = self.selectionUiList
        if selectedItems:
            cmds.textScrollList(self.allBoardList[self.destinationBoardIndex], edit=True, selectItem=selectedItems)

 
    def deselectOtherBoards(self, boardIndex, *args):
        """ Figure out which board column is selected.
        """
        for b, board in enumerate(self.allBoardList):
            if not b == boardIndex:
                cmds.textScrollList(self.allBoardList[b], edit=True, deselectAll=True)
        

    def activeSelection(self, boardIndex, *args):
        """ Get the active selection.
        """
        self.selectedBoard = boardIndex
        self.deselectOtherBoards(boardIndex)
        self.selectionUiList = cmds.textScrollList(self.allBoardList[boardIndex], query=True, selectItem=True)
