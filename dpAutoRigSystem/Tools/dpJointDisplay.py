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
        self.selectedBoard = []
        self.allBoardList = ['boneFieldcolumn', 'multiChildFieldcolumn', 'noneFieldcolumn', 'jointFieldcolumn']
        self.destinationBoard = ''
        
        # call main function
        if self.ui:
            self.dpJointDisplayUI(self)
            self.refreshLists(self)
            cmds.scriptJob(event=('SelectionChanged', self.refreshLists), parent='dpJointDisplayWindow', replacePrevious=True, killWithScene=True, compressUndo=True, force=True)


    def dpCloseJointDisplayUI(self, *args):
        if cmds.window('dpJointDisplayWindow', query=True, exists=True):
            cmds.deleteUI('dpJointDisplayWindow', window=True)


    def dpJointDisplayUI(self, *args):
        """ Create a window in order to load the joints in the scene.
        """
        # call close UI function
        self.dpCloseJointDisplayUI(self)
        # starting UI
        jointDisplay_winWidth  = 500
        jointDisplay_winHeight = 175
        dpJointDisplayWin = cmds.window('dpJointDisplayWindow', title=self.dpUIinst.lang["m233_jointDisplay"]+" "+str(DP_JOINTDISPLAY_VERSION), widthHeight=(jointDisplay_winWidth, jointDisplay_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)

        # creating Main layout:
        jointDisplayMainLayout = cmds.columnLayout('jointDisplayMainLayout', columnOffset=('both', 5), adjustableColumn=True)
        
        # filter
        filterLayout = cmds.columnLayout("filterLayout", adjustableColumn=True, parent=jointDisplayMainLayout)
        self.jointFilter = cmds.textFieldGrp("jointFilter", label=self.dpUIinst.lang['i268_filterByName'], text="", textChangedCommand=self.refreshLists, adjustableColumn=2, parent=filterLayout)

        # creating column Layout
        columnLayout = cmds.rowColumnLayout('scrollLayout', numberOfColumns=4, rowOffset=[1,'both', 5] ,columnWidth=[(1, 150), (2, 150), (3, 150), (4, 150)], columnSpacing=[(1, 5), (2, 5), (3, 5), (4, 5)], parent=jointDisplayMainLayout, adjustableColumn=4)

        # creating titles
        cmds.text('boneTitle', label='Bone',parent=columnLayout)
        cmds.text('multiChildTitle',label='Multi-Child as box',parent=columnLayout)
        cmds.text('noneTitle', label='None',parent=columnLayout)
        cmds.text('jointTitle',label='Joint',parent=columnLayout)

        # bone display panels
        self.boneFieldcolumn = cmds.textScrollList(self.allBoardList[0], enable=True, parent=columnLayout, allowMultiSelection=True, selectCommand=lambda: self.activeSelection(self.boneFieldcolumn), deselectAll=True, height=300)
        self.multiChildFieldcolumn = cmds.textScrollList(self.allBoardList[1], enable=True, parent=columnLayout, allowMultiSelection=True, selectCommand=lambda: self.activeSelection(self.multiChildFieldcolumn), deselectAll=True, height=300)
        self.noneFieldcolumn = cmds.textScrollList(self.allBoardList[2],enable=True, parent=columnLayout, allowMultiSelection=True, selectCommand=lambda: self.activeSelection(self.noneFieldcolumn), deselectAll=True, height=300)
        self.jointFieldcolumn = cmds.textScrollList(self.allBoardList[3],enable=True, parent=columnLayout, allowMultiSelection=True, selectCommand=lambda: self.activeSelection(self.jointFieldcolumn), deselectAll=True, height=300)
    
        # bottom layout for buttons
        cmds.separator(style='none', height=10, parent=jointDisplayMainLayout)
        buttonLayout = cmds.rowColumnLayout("buttonLayout", childArray=True ,numberOfColumns=4, columnWidth=[(1, 80), (2, 80), (3, 100),(3, 100)], columnOffset=[(1, "both", 5), (2, "both", 5), (3, "both", 10), (4, "left", 250)], parent=jointDisplayMainLayout, adjustableColumn=True)
        
        # defining move buttons
        cmds.button("moveLeft", label=self.dpUIinst.lang['c034_move'] + ' <<<', backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.moveToLeft, parent=buttonLayout)
        cmds.button("moveRight", label=self.dpUIinst.lang['c034_move'] + ' >>>', backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.moveToRight, parent=buttonLayout)
        self.chabgeAllToMenu = cmds.optionMenu('chabgeAllTo',label=self.dpUIinst.lang['i359_changeTo']+' :', width = 200, parent=buttonLayout, changeCommand= self.chabgeAllToButton)
        cmds.menuItem( label='Bone', parent=self.chabgeAllToMenu)
        cmds.menuItem( label='Multi-Child as box', parent=self.chabgeAllToMenu )
        cmds.menuItem( label='None', parent=self.chabgeAllToMenu )
        cmds.menuItem( label='Joint', parent=self.chabgeAllToMenu )
        
        cmds.button("cancel", label=self.dpUIinst.lang['c109_close'], backgroundColor=(0.5, 0.5, 0.5), width=100, command=self.dpCloseJointDisplayUI, parent=buttonLayout)
        cmds.separator(style='none', height=10, parent=buttonLayout)

        # call dpJointDisplayUI Window:
        cmds.showWindow(dpJointDisplayWin)
    

    def refreshLists(self,*args, **kwargs):
        """ Refresh the code
        """
        self.cleanAllLists(self)
        self.getAllJointList(self)
        self.getItemFilter(self)
        self.populateLabelList(self)
        self.refreshPreview(self)


    def getAllJointList(self, *args, **kwargs):
        """ Get all joints in the scene
        """
        jointList = cmds.ls(type='joint')
        if jointList:
            for joint in jointList:
                self.allJointsList.append(joint)

    def getItemFilter(self, *args, **kwargs):
        """ Create a selection filter by transform type excluding the ignoreIt list.
        """
        writtenFilter = cmds.textFieldGrp(self.jointFilter, query=True, text=True)
        filterList = []
        if writtenFilter:
            for item in self.allJointsList:
                if writtenFilter.lower() in item.lower():
                    filterList.append(item)
            self.allJointsList = filterList

                
    def populateLabelList(self, *args, **kwargs):
        """ Populate each list with label joint type
        """
        if self.allJointsList:
            for jnt in self.allJointsList:
                if cmds.getAttr(jnt +'.drawStyle') == 0:
                    try:
                        self.boneLabelList.append(jnt)
                    except:
                        pass
                if cmds.getAttr(jnt +'.drawStyle') == 1:
                    try:
                        self.multiChildLabelList.append(jnt)                    
                    except:
                        pass
                if cmds.getAttr(jnt +'.drawStyle') == 2:
                    try:
                        self.noneLabelList.append(jnt)
                    except:
                        pass
                if cmds.getAttr(jnt +'.drawStyle') == 3:
                    try:
                        self.jointLabelList.append(jnt)
                    except:
                        pass


    def refreshPreview(self, *args):
        """ Refresh the preview of each board"""
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
        """ Clear all Lists"""
        self.allJointsList.clear()
        self.boneLabelList.clear()
        self.multiChildLabelList.clear()
        self.noneLabelList.clear()
        self.jointLabelList.clear()


    def moveToRight(self,*args):
        """ Button to move the selected joints to the right board
        """
        # Get active selection of button list
        self.selectionUiList
        if self.selectionUiList:
            for jnt in self.selectionUiList:
                currentDrawStyle = cmds.getAttr(jnt +'.drawStyle')
                if currentDrawStyle < 3:
                    cmds.setAttr(jnt +'.drawStyle', currentDrawStyle + 1)
                    print (f' Returned Seach BOARD {self.searchBoardIndex()}')
                    self.destinationBoard = self.searchBoardIndex() + 1
                else: 
                    currentDrawStyle = 0
                    cmds.setAttr(jnt +'.drawStyle', currentDrawStyle)
                    self.destinationBoard = 0
            self.refreshLists(self)
            self.keepSelectedObj(self)
    
    
    def moveToLeft(self, *args, **kwargs):
        """ Button to move the selected joints to the left board 
        """
        # Get active selection of button list
        self.selectionUiList

        if self.selectionUiList:
            for jnt in self.selectionUiList:
                currentDrawStyle = cmds.getAttr(jnt +'.drawStyle')
                if currentDrawStyle > 0 < 3 :
                    cmds.setAttr(jnt +'.drawStyle', currentDrawStyle - 1)
                    self.destinationBoard = self.searchBoardIndex() - 1
                else: 
                    currentDrawStyle = 3
                    cmds.setAttr(jnt +'.drawStyle', currentDrawStyle)
                    self.destinationBoard = 0          
            self.refreshLists(self)
            self.keepSelectedObj(self)  


    def chabgeAllToButton(self, *args):
        """ Change all joints to the selected drawStyle"""
        selectedLabel = cmds.optionMenu(self.chabgeAllToMenu, query=True, value=True)
        if selectedLabel == 'Bone':
            self.setAllDrawstyle(0)
        elif selectedLabel == 'Multi-Child as box':
            self.setAllDrawstyle(1)
        elif selectedLabel == 'None':
            self.setAllDrawstyle(2)
        elif selectedLabel == 'Joint':
            self.setAllDrawstyle(3)


    def setAllDrawstyle(self, drawStyleIndex, *args):
        """ Set all joints to the selected drawStyle"""        
        self.allJointsList
        if self.allJointsList:
            for jnt in self.allJointsList:
                cmds.setAttr(f"{jnt}.drawStyle", drawStyleIndex)
                self.selectionUiList.append(jnt)
        self.destinationBoard = drawStyleIndex
        self.refreshLists()
                

    def searchBoardIndex(self, *args):
        index = 0
        for board in self.allBoardList:
            if board == self.selectedBoard:
                return index
            index += 1

    
    def keepSelectedObj(self, *args):
        """Mantain ative selected joints"""
        selectedItems = self.selectionUiList
        if selectedItems:
            cmds.textScrollList(self.allBoardList[self.destinationBoard], edit=True, selectItem=selectedItems)

 
    def deselectOtherBoards(self, board, *args, **kwargs):
        ''' Figure out which board column is selected'''
        self.board = board
        boardList = self.allBoardList
        board=[]
        for item in boardList:
            if item == self.board[self.board.rfind("|")+1:]:
                board.append(item)
            if item != self.board[self.board.rfind("|")+1:]:
                cmds.textScrollList(item, edit=True, deselectAll=True) 
        

    def activeSelection(self, selectedBoard, *args):
        """Get the active selection"""
        self.selectedBoard = selectedBoard[selectedBoard.rfind("|")+1:]
        self.deselectOtherBoards(board=self.selectedBoard)
        self.selectionUiList = cmds.textScrollList(selectedBoard, query=True, selectItem=True)
        return self.selectionUiList

#TODO
# - Fix the height of the textScrollList
# - Fix the responsivity of the lower buttons
# - Fix the buttons Move Left and Right to do nothing when there is no selection
