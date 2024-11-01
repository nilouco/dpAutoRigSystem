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
        columnLayout = cmds.rowColumnLayout('scrollLayout', numberOfColumns=4, rowOffset=[1,'both', 5] ,columnWidth=[(1, 150), (2, 150), (3, 150), (4, 150)], columnSpacing=[(1, 5), (2, 5), (3, 5), (4, 5)], parent=jointDisplayMainLayout)

        # creating titles
        boneTitle = cmds.text('boneTitle', label='Bone',parent=columnLayout)
        multiChildTitle = cmds.text('multiChildTitle',label='Multi-Child as box',parent=columnLayout)
        noneTitle = cmds.text('noneTitle', label='None',parent=columnLayout)
        jointTitle = cmds.text('jointTitle',label='Joint',parent=columnLayout)
        

        # bone display panels
        # boneFieldcolumn = cmds.textScrollList('boneFieldcolumn', parent=columnLayout, allowMultiSelection=True, append=self.boneLabelList, enable=True)
        self.boneFieldcolumn = cmds.textScrollList(self.allBoardList[0], enable=True, parent=columnLayout, allowMultiSelection=True, selectCommand=lambda: self.activeSelection(self.boneFieldcolumn), deselectAll=True)
        self.multiChildFieldcolumn = cmds.textScrollList(self.allBoardList[1], enable=True, parent=columnLayout, allowMultiSelection=True, selectCommand=lambda: self.activeSelection(self.multiChildFieldcolumn), deselectAll=True)
        self.noneFieldcolumn = cmds.textScrollList(self.allBoardList[2],enable=True, parent=columnLayout, allowMultiSelection=True, selectCommand=lambda: self.activeSelection(self.noneFieldcolumn), deselectAll=True)
        self.jointFieldcolumn = cmds.textScrollList(self.allBoardList[3],enable=True, parent=columnLayout, allowMultiSelection=True, selectCommand=lambda: self.activeSelection(self.jointFieldcolumn), deselectAll=True)
        
    
        # bottom layout for buttons
        cmds.separator(style='none', height=10, parent=jointDisplayMainLayout)
        buttonLayout = cmds.rowColumnLayout("buttonLayout", childArray=True ,numberOfColumns=4, columnWidth=[(1, 80), (2, 80), (3, 100),(3, 100)], columnOffset=[(1, "both", 5), (2, "both", 5), (3, "both", 10), (4, "left", 250)], parent=jointDisplayMainLayout)
        
        # defining move buttons
        cmds.button("moveLeft", label=self.dpUIinst.lang['c034_move'] + ' <<<', backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.moveToLeft, parent=buttonLayout)
        cmds.button("moveRight", label=self.dpUIinst.lang['c034_move'] + ' >>>', backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.moveToRight, parent=buttonLayout)
        changeAllMenu = cmds.optionMenu('changeAll',label=self.dpUIinst.lang['m098_jointDisplay'], backgroundColor=(0.6, 0.6, 0.6), width = 100, parent=buttonLayout)
        cmds.menuItem( label='Bone', parent=changeAllMenu)
        cmds.menuItem( label='Multi-Child as box', parent=changeAllMenu )
        cmds.menuItem( label='None', parent=changeAllMenu )
        cmds.menuItem( label='Joint', parent=changeAllMenu )
        
        cmds.button("cancel", label=self.dpUIinst.lang['i132_cancel'], backgroundColor=(0.5, 0.5, 0.5), width=100, command='Cancel', parent=buttonLayout)
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
        print(f'Move to Right Pressed')
        selectedJoints = self.activeSelection(self.selectedBoard)
        print(selectedJoints)
        if selectedJoints:
            for jnt in selectedJoints:
                currentDrawStyle = cmds.getAttr(jnt +'.drawStyle')
                if currentDrawStyle < 3:
                    print(f'DrawStyle atual {currentDrawStyle}')
                    cmds.setAttr(jnt +'.drawStyle', currentDrawStyle + 1)
                else: 
                    currentDrawStyle = 0
                    cmds.setAttr(jnt +'.drawStyle', currentDrawStyle)
            self.refreshLists(self)
            self.keepSelectedObj(self)

            
    
    
    def moveToLeft(self, *args, **kwargs):
        """ """
        # Get active selection of button list
        print(f'Move to Right Pressed')
        selectedJoints = self.activeSelection(self.selectedBoard)
        print(selectedJoints)

        if selectedJoints:
            for jnt in selectedJoints:
                currentDrawStyle = cmds.getAttr(jnt +'.drawStyle')
                if currentDrawStyle > 0 < 3 :
                    print(f'DrawStyle atual {currentDrawStyle}')
                    cmds.setAttr(jnt +'.drawStyle', currentDrawStyle - 1)
                else: 
                    currentDrawStyle = 3
                    cmds.setAttr(jnt +'.drawStyle', currentDrawStyle)          
            self.refreshLists(self)
            self.keepSelectedObj(self)  



    
    
    def keepSelectedObj(self, *args):
        """ Mantain ative selected joints"""

        selectedUIJoints = self.selectionUiList
        selectedUIBoard = self.selectedBoard
        allboards = self.allBoardList
        selectedItens = []

        for board in allboards:
            #Existe algum objeto da lista selectedUIJoints?
            if selectedUIJoints:
                selectedItens.append(cmds.textScrollList(board, query=True, selectItem=True))
                for iten in selectedItens:
                    cmds.textScrollList(board, edit=True, selectItem=iten)
                selectedItens = []

            # Se existe, seleciona ele.
            # Se algum objeto contem no em algum board. Seleciona o objeto no respectivo board.
            



                
                


        """!!!!!!!!!!!!!  STOOPED: Parei tentando encontrar """
        
        # selectedList = cmds.textScrollList(obj, query=True, selectItem=True)
        # toSelectList = []
        # boardList = ['boneFieldcolumn', 'jointFieldcolumn', 'multiChildFieldcolumn', 'noneFieldcolumn']
        # print(f'KEEP SELECTED OBJ FUNCTION selectedUIJoints ======{selectedUIJoints}')
        # print(f'KEEP SELECTED OBJ FUNCTION selectedUIBoard ======{selectedUIBoard}')
        
        # for obj in boardList:
        #     for uiItem in selectedList:
        #         selectedList.append(uiItem)

                    
        #         print(f'Selected JOINTS KEEP SELECTED Function______{toSelectList}')


            

        # print(cmds.textScrollList(selectedUIBoard, edit=True, selectItem=selectedUIJoints))

        
        # if selectedUIJoints:
        #     print(f'Selected Joints UI ++++++++++++++{selectedUIJoints}')

        # If selected joint



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
        
        self.selectedBoard = selectedBoard
        self.deselectOtherBoards(board= self.selectedBoard)
        self.selectionUiList = cmds.textScrollList(selectedBoard, query=True, selectItem=True)
        print(f'SELECAO ATIVA ______ {self.selectionUiList}')
        return self.selectionUiList




    # def mainfilter():
    #     Filter list to populate the 
        
    #     #TODO
    #     # create a filter to populate list that will be searched 

    
    # def refreshLists(self,*args, **kwargs):
    #     

    #     self.getAllJointList()
    #     self.populateLabelList()

        
        #TODO
        # read all joints
        # populate fields

    # def activeSelectionBoard():
    #     Find the active selection and indicate the board
    #     


#Study 
