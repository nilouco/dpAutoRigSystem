# importing libraries:
from maya import cmds
from maya import mel
from functools import partial

# global variables to this module:
CLASS_NAME = "JointDisplay"
TITLE = "m098_jointDisplay"
DESCRIPTION = "m169_jointDisplayDesc"
ICON = "/Icons/dp_reorderAttr.png"



IGNORE_LIST = ['persp', 'top', 'front', 'side'] # WIP To Delete



DP_JOINTDISPLAY_VERSION = 1.0


class JointDisplay(object):
    def __init__(self, dpUIinst, ui=True, *args, **kwargs):
        self.dpUIinst = dpUIinst
        # call main function
        if ui:
            self.dpJointDisplayUI(self)
    
    
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
        jointDisplay_winWidth  = 675
        jointDisplay_winHeight = 175
        dpJointDisplayWin = cmds.window('dpJointDisplayWindow', title=self.dpUIinst.lang["m098_jointDisplay"]+" "+str(DP_JOINTDISPLAY_VERSION), widthHeight=(jointDisplay_winWidth, jointDisplay_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)

        # creating layout:
        jointDisplayLayout = cmds.columnLayout('jointDisplayLayout', columnOffset=("both", 5), adjustableColumn=True)
        mainLayout = cmds.columnLayout('mainLayout', adjustableColumn=True, columnOffset=("both", 5), parent=jointDisplayLayout)
        # cmds.separator(style='none', height=7, parent=jointDisplayLayout)
        # cmds.button(label=self.dpUIinst.lang["i154_up"], annotation=self.dpUIinst.lang["i155_upDesc"], width=110, backgroundColor=(0.45, 1.0, 0.6), command=partial(self.dpMoveAttr, 1, None, None, True), parent=jointDisplayLayout)
        # cmds.separator(style='in', height=10, width=110, parent=jointDisplayLayout)
        # cmds.button(label=self.dpUIinst.lang["i156_down"], annotation=self.dpUIinst.lang["i157_downDesc"], width=110, backgroundColor=(1.0, 0.45, 0.45), command=partial(self.dpMoveAttr, 0, None, None, True), parent=jointDisplayLayout)

        # filter
        filterLayout = cmds.columnLayout("filterLayout", adjustableColumn=True, parent=mainLayout)
        self.itemFilterTFG = cmds.textFieldButtonGrp("itemFilterTFG", label=self.dpUIinst.lang['i268_filterByName'], text="", buttonLabel=self.dpUIinst.lang['m004_select']+" "+self.dpUIinst.lang['i211_all'], buttonCommand="TESTEEE####", changeCommand=self.dpMoveAttr, adjustableColumn=2, parent=filterLayout)
        cmds.separator(style='none', height=5, parent=filterLayout)

        # items and attributes layout
        tablePaneLayout = cmds.paneLayout("tablePaneLayout", parent=mainLayout)
        self.itemSC = cmds.selectionConnection(activeList=True)
        self.mainSSE = cmds.spreadSheetEditor(mainListConnection=self.itemSC, fixedAttrList=['drawStyle'], niceNames=False, keyableOnly=False, parent=tablePaneLayout)
        # bottom layout for buttons
        cmds.separator(style='none', height=10, parent=mainLayout)
        buttonLayout = cmds.rowColumnLayout("buttonLayout", childArray=True ,numberOfColumns=3, columnWidth=[(1, 80), (2, 80), (3, 100)], columnOffset=[(1, "both", 5), (2, "both", 5), (3, "both", 5)], parent=mainLayout)
        cmds.button("addButton", label=self.dpUIinst.lang['i063_skinAddBtn'], backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.dpMoveAttr, parent=buttonLayout)
        cmds.button("removeButton", label=self.dpUIinst.lang['i064_skinRemBtn'], backgroundColor=(0.4, 0.4, 0.4), width=70, command=self.dpMoveAttr, parent=buttonLayout)
        cmds.button("updateIDButton", label=self.dpUIinst.lang['i089_update'], backgroundColor=(0.5, 0.5, 0.5), width=100, command=self.dpMoveAttr, parent=buttonLayout)

        
        # call dpJointDisplayUI Window:
        cmds.showWindow(dpJointDisplayWin)
    
    
    def dpMoveAttr(self, mode, objList=None, attrList=None, verbose=False, *args):
        """ Change order of attributes in order to move it to up or down in the list position.
        """
        # do ScriptEditor do not print Undo messages:
        cmds.scriptEditorInfo(suppressInfo=False)
        if not objList:
            # get current selected objects:
            objList = cmds.channelBox('mainChannelBox', query=True, mainObjectList=True)
        if objList:
            if not attrList:
                # get selected attributes from channelBox
                attrList = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)
            if attrList:
                for obj in objList:
                    userDefAttrList = cmds.listAttr(obj, userDefined=True)
                    if userDefAttrList:
                        if not attrList[0] in userDefAttrList:
                            if verbose:
                                mel.eval("warning \"Selected attribute "+str(attrList)+" is static and can not be moved, sorry.\";")
                        else:
                            cmds.scriptEditorInfo(suppressInfo=True)
                            # unlock all user defined attibutes before start the changing position:
                            lockAttrList = cmds.listAttr(obj, userDefined=True, locked=True)
                            if lockAttrList:
                                for lockAttr in lockAttrList:
                                    cmds.setAttr(obj+"."+lockAttr, lock=False)
                            # start moving attributes
                            if mode == 0: #down
                                if len(attrList) > 1:
                                    attrList.reverse()
                                    sortedList = attrList
                                if len(attrList) == 1:
                                    sortedList = attrList
                                for i in sortedList:
                                    attrLs = cmds.listAttr(obj, userDefined=True)
                                    attrSize = len(attrLs)
                                    attrPos = attrLs.index(i)
                                    cmds.deleteAttr(obj,at=attrLs[attrPos])
                                    cmds.undo()
                                    for x in range(attrPos+2,attrSize,1):
                                        cmds.deleteAttr(obj,at=attrLs[x])
                                        cmds.undo()
                                        
                            elif mode == 1: #up
                                for i in attrList:
                                    attrLs = cmds.listAttr(obj, userDefined=True)
                                    attrSize = len(attrLs)
                                    attrPos = attrLs.index(i)
                                    if attrLs[attrPos-1]:
                                        cmds.deleteAttr(obj, at=attrLs[attrPos-1])
                                        cmds.undo()
                                    for x in range(attrPos+1,attrSize,1):
                                        cmds.deleteAttr(obj, at=attrLs[x])
                                        cmds.undo()
                            
                            # lock all user defined attibutes after the changing position:
                            if lockAttrList:
                                for lockAttr in lockAttrList:
                                    cmds.setAttr(obj+"."+lockAttr, lock=True)
                    else:
                        if verbose:
                            mel.eval("warning \"We can only reorder added attributes by user.\";")
            else:
                if verbose:
                    mel.eval("warning \"Select one or more attributes in the Channel Box, please.\";")
        else:
            if verbose:
                mel.eval("warning \"Select one or more transform nodes to reorder attributes, please.\";")
        # back ScritpEditor to show info:
        cmds.scriptEditorInfo(suppressInfo=True)
 