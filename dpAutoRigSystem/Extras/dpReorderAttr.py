# importing libraries:
import maya.cmds as cmds
import maya.mel as mel
from functools import partial

# global variables to this module:
CLASS_NAME = "ReorderAttr"
TITLE = "m087_reorderAttr"
DESCRIPTION = "m088_reoderAttrDesc"
ICON = "/Icons/dp_reorderAttr.png"


DPRA_VERSION = "1.0"

class ReorderAttr():
    def __init__(self, ui=True, *args, **kwargs):
        # call main function
        if ui:
            self.dpReorderAttrUI(self)
    
    
    def dpCloseReorderAttrUI(self, *args):
        if cmds.window('dpReorderAttrWindow', query=True, exists=True):
            cmds.deleteUI('dpReorderAttrWindow', window=True)
    
    
    def dpReorderAttrUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        # creating dpReorderAttrUI Window:
        self.dpCloseReorderAttrUI()
        reorderAttr_winWidth  = 175
        reorderAttr_winHeight = 75
        dpReorderAttrWin = cmds.window('dpReorderAttrWindow', title="Reorder Attribute 1.0", widthHeight=(reorderAttr_winWidth, reorderAttr_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)

        # creating layout:
        reorderAttrLayout = cmds.columnLayout('reorderAttrLayout', columnOffset=("left", 30))
        cmds.separator(style='none', height=7, parent=reorderAttrLayout)
        cmds.button(label="Up", annotation="Move attribute to up", width=110, backgroundColor=(0.45, 1.0, 0.6), command=partial(self.dpMoveAttr, 1, None, None, True), parent=reorderAttrLayout)
        cmds.separator(style='in', height=10, width=110, parent=reorderAttrLayout)
        cmds.button(label="Down", annotation="Move attribute to down", width=110, backgroundColor=(1.0, 0.45, 0.45), command=partial(self.dpMoveAttr, 0, None, None, True), parent=reorderAttrLayout)
        
        # call dpReorderAttrUI Window:
        cmds.showWindow(dpReorderAttrWin)
    
    
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
 