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

    # def getItemFilter(self, *args, **kwargs):
    #     """ Create a selection filter by transform type excluding the ignoreIt list.
    #     """
    #     self.itemF = cmds.itemFilter(byName= "")
    #     for ignoreIt in IGNORE_LIST:
    #         self.itemF = cmds.itemFilter(difference=(self.itemF, cmds.itemFilter(byName=ignoreIt)))
    #     return self.itemF
    
    def dpJointDisplayUI(self, *args):
        """ Create a window in order to load the joints in the scene.
        """
        # call close UI function
        self.dpCloseJointDisplayUI(self)
        # ctarting UI
        jointDisplay_winWidth  = 500
        jointDisplay_winHeight = 175
        dpJointDisplayWin = cmds.window('dpJointDisplayWindow', title=self.dpUIinst.lang["m098_jointDisplay"]+" "+str(DP_JOINTDISPLAY_VERSION), widthHeight=(jointDisplay_winWidth, jointDisplay_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)

        # creating Main layout:
        jointDisplayMainLayout = cmds.columnLayout('jointDisplayMainLayout', columnOffset=('both', 5), adjustableColumn=True)
        
        # filter
        filterLayout = cmds.columnLayout("filterLayout", adjustableColumn=True, parent=jointDisplayMainLayout)
        self.jointFilter = cmds.textFieldButtonGrp("jointFilter", label=self.dpUIinst.lang['i268_filterByName'], text="", buttonLabel=self.dpUIinst.lang['m004_select']+" "+self.dpUIinst.lang['i211_all'], buttonCommand="Test", changeCommand=lambda:self.refreshLists(), adjustableColumn=2, parent=filterLayout)

        # creating column Layout
        columnLayout = cmds.rowColumnLayout('scrollLayout', numberOfColumns=4, rowOffset=[1,'both', 5] ,columnWidth=[(1, 150), (2, 150), (3, 150), (4, 150)], columnSpacing=[(1, 5), (2, 5), (3, 5), (4, 5)], parent=jointDisplayMainLayout, adjustableColumn=True)

        # creating titles
        cmds.text('boneTitle', label='Bone',parent=columnLayout)
        cmds.text('multiChildTitle',label='Multi-Child as box',parent=columnLayout)
        cmds.text('noneTitle', label='None',parent=columnLayout)
        cmds.text('jointTitle',label='Joint',parent=columnLayout)
        

        # bone display panels
        # boneFieldcolumn = cmds.textScrollList('boneFieldcolumn', parent=columnLayout, allowMultiSelection=True, append=self.boneLabelList, enable=True)
        self.boneFieldcolumn = cmds.textScrollList(self.allBoardList[0], enable=True, parent=columnLayout, allowMultiSelection=True, selectCommand=lambda: self.activeSelection(self.boneFieldcolumn), deselectAll=True)
        self.multiChildFieldcolumn = cmds.textScrollList(self.allBoardList[1], enable=True, parent=columnLayout, allowMultiSelection=True, selectCommand=lambda: self.activeSelection(self.multiChildFieldcolumn), deselectAll=True)
        self.noneFieldcolumn = cmds.textScrollList(self.allBoardList[2],enable=True, parent=columnLayout, allowMultiSelection=True, selectCommand=lambda: self.activeSelection(self.noneFieldcolumn), deselectAll=True)
        self.jointFieldcolumn = cmds.textScrollList(self.allBoardList[3],enable=True, parent=columnLayout, allowMultiSelection=True, selectCommand=lambda: self.activeSelection(self.jointFieldcolumn), deselectAll=True)
        
    
        # bottom layout for buttons
        cmds.separator(style='none', height=10, parent=jointDisplayMainLayout)
        buttonLayout = cmds.rowColumnLayout("buttonLayout", childArray=True ,numberOfColumns=4, columnWidth=[(1, 80), (2, 80), (3, 100),(3, 100)], columnOffset=[(1, "both", 5), (2, "both", 5), (3, "both", 10), (4, "left", 250)], parent=jointDisplayMainLayout, adjustableColumn=True)
        
        # defining move buttons
        cmds.button("moveLeft", label=self.dpUIinst.lang['c034_move'] + ' <<<', backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.moveToLeft, parent=buttonLayout)
        cmds.button("moveRight", label=self.dpUIinst.lang['c034_move'] + ' >>>', backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.moveToRight, parent=buttonLayout)
        self.changeAllMenu = cmds.optionMenu('changeAll',label=self.dpUIinst.lang['m098_jointDisplay']+' :', width = 200, parent=buttonLayout, changeCommand= self.changeAllButton)
        cmds.menuItem( label='Bone', parent=self.changeAllMenu)
        cmds.menuItem( label='Multi-Child as box', parent=self.changeAllMenu )
        cmds.menuItem( label='None', parent=self.changeAllMenu )
        cmds.menuItem( label='Joint', parent=self.changeAllMenu )
        
        cmds.button("cancel", label=self.dpUIinst.lang['i132_cancel'], backgroundColor=(0.5, 0.5, 0.5), width=100, command=self.dpCloseJointDisplayUI, parent=buttonLayout)
        cmds.separator(style='none', height=10, parent=buttonLayout)

        # call dpJointDisplayUI Window:
        cmds.showWindow(dpJointDisplayWin)
    

    def refreshLists(self,*args, **kwargs):
        """ Refresh the code
        """
        self.cleanAllLists(self)
        self.getAllJointList(self)
        print(f'GetAllJointList ---- OK')
        self.populateLabelList(self)
        print(f'PopulateLabelList ---- OK')
        

        self.refreshPreview(self)
        print(f'RefreshPreview ---- OK')



    def getAllJointList(self, *args, **kwargs):
        """ Get all joints in the scene
        """
        getlistPass = 0
        jointList = cmds.ls(type='joint')
        if jointList:
            for joint in jointList:
                self.allJointsList.append(joint)
            print(f'All joints List : {self.allJointsList}')
            print(f'Pass Get List : {getlistPass}')

    
    def populateLabelList(self, *args, **kwargs):
        """ Populate each list with label joint type
        """
        
        if self.allJointsList:
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


    def refreshPreview(self, *args):
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
        """ """
        # Get active selection of button list
        print(f'Move to Right called')
        self.selectionUiList
        print(f'Move to Right Selected Board ---------{self.selectedBoard}')
        if self.selectionUiList:
            for jnt in self.selectionUiList:
                currentDrawStyle = cmds.getAttr(jnt +'.drawStyle')
                if currentDrawStyle < 3:
                    print(f'DrawStyle atual {currentDrawStyle}')
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
        """ """
        # Get active selection of button list
        print(f'Move to Left called')
        self.selectionUiList
        print(f'Move to Left Selected Board ---------{self.selectedBoard}')

        if self.selectionUiList:
            for jnt in self.selectionUiList:
                currentDrawStyle = cmds.getAttr(jnt +'.drawStyle')
                if currentDrawStyle > 0 < 3 :
                    print(f'DrawStyle atual {currentDrawStyle}')
                    cmds.setAttr(jnt +'.drawStyle', currentDrawStyle - 1)
                    self.destinationBoard = self.searchBoardIndex() - 1
                else: 
                    currentDrawStyle = 3
                    cmds.setAttr(jnt +'.drawStyle', currentDrawStyle)
                    self.destinationBoard = 0          
            self.refreshLists(self)
            self.keepSelectedObj(self)  

    def changeAllButton(self, *args):
        selectedLabel = cmds.optionMenu(self.changeAllMenu, query=True, value=True)
        print(f'BUTON PRESSED {selectedLabel}')
        if selectedLabel == 'Bone':
            self.setAllDrawstyle(0)
        elif selectedLabel == 'Multi-Child as box':
            self.setAllDrawstyle(1)
        elif selectedLabel == 'None':
            self.setAllDrawstyle(2)
        elif selectedLabel == 'Joint':
            self.setAllDrawstyle(3)


    def setAllDrawstyle(self, drawStyleIndex, *args):
        self.allJointsList
        if self.allJointsList:
            for jnt in self.allJointsList:
                cmds.setAttr(f"{jnt}.drawStyle", drawStyleIndex)
                self.selectionUiList.append(jnt)
        self.destinationBoard = drawStyleIndex
        self.refreshLists()
        #self.keepSelectedObj()
                

    def searchBoardIndex(self, *args):
        index = 0
        for board in self.allBoardList:
            if board == self.selectedBoard:
                return index
            index += 1

        print( f'Active Index Board {index}')

    
    def keepSelectedObj(self, *args):
        """Mantain ative selected joints"""

        selectedItems = self.selectionUiList
        print(f'keepSelectedObj Called________!!!!!!!')
        #print(f'DESTINATION BOARD >>>>>> {self.allBoardList[self.destinationBoard]}')
        if selectedItems:
            cmds.textScrollList(self.allBoardList[self.destinationBoard], edit=True, selectItem=selectedItems)
            print(f'Selected Items {selectedItems}')

 



    def deselectOtherBoards(self, board, *args, **kwargs):
        ''' Figure out which board column is selected'''
        self.board = board
        boardList = self.allBoardList # ['boneFieldcolumn', 'jointFieldcolumn', 'multiChildFieldcolumn', 'noneFieldcolumn']
        board=[]
        for item in boardList:
            if item == self.board[self.board.rfind("|")+1:]:
                board.append(item)
            if item != self.board[self.board.rfind("|")+1:]:
                cmds.textScrollList(item, edit=True, deselectAll=True) 
        

    # def searchdeselectOtherBoards(self,):
    

    def activeSelection(self, selectedBoard, *args):
        """Get the active selection"""
        print(f'BOARD SELECIONADO {selectedBoard[selectedBoard.rfind("|")+1:]}')
        
        self.selectedBoard = selectedBoard[selectedBoard.rfind("|")+1:]
        print(f'self.selectedBoard {self.selectedBoard}')
        self.deselectOtherBoards(board=self.selectedBoard)
        self.selectionUiList = cmds.textScrollList(selectedBoard, query=True, selectItem=True)
        print(f'SELECAO ATIVA ______ {self.selectionUiList}')
        return self.selectionUiList





# TODO
# - create a filter: To populate list that will be searched
# - make the heitght of the window responsive.
