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
        jointDisplay_winWidth  = 500
        jointDisplay_winHeight = 175
        dpJointDisplayWin = cmds.window('dpJointDisplayWindow', title=self.dpUIinst.lang["m098_jointDisplay"]+" "+str(DP_JOINTDISPLAY_VERSION), widthHeight=(jointDisplay_winWidth, jointDisplay_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)

        # creating Main layout:
        jointDisplayMainLayout = cmds.columnLayout('jointDisplayMainLayout', columnOffset=('both', 5), adjustableColumn=True)
        
        # filter
        filterLayout = cmds.columnLayout("filterLayout", adjustableColumn=True, parent=jointDisplayMainLayout)
        self.jointFilter = cmds.textFieldButtonGrp("jointFilter", label=self.dpUIinst.lang['i268_filterByName'], text="", buttonLabel=self.dpUIinst.lang['m004_select']+" "+self.dpUIinst.lang['i211_all'], buttonCommand="TESTEEE####", changeCommand=self.dpMoveAttr, adjustableColumn=2, parent=filterLayout)

        # column Layout
        colunmLayout = cmds.rowColumnLayout('scrollLayout', numberOfColumns=4, rowOffset=[1,'both', 5] ,columnWidth=[(1, 150), (2, 150), (3, 150), (4, 150)], columnSpacing=[(1, 5), (2, 5), (3, 5), (4, 5)], parent=jointDisplayMainLayout)

        title1 = cmds.text('boneTitle', label='Bone',parent=colunmLayout)
        title2 = cmds.text('jointTitle',label='Joint',parent=colunmLayout)
        title3 = cmds.text('multiChildAsBoxTitle',label='Multi-Child as box',parent=colunmLayout)
        title4 = cmds.text('noneTitle', label='None',parent=colunmLayout)

        cmds.scrollField(parent=colunmLayout)
        cmds.scrollField(parent=colunmLayout)
        cmds.scrollField(parent=colunmLayout)
        cmds.scrollField(parent=colunmLayout)

        # bottom layout for buttons
        cmds.separator(style='none', height=10, parent=jointDisplayMainLayout)
        buttonLayout = cmds.rowColumnLayout("buttonLayout", childArray=True ,numberOfColumns=3, columnWidth=[(1, 80), (2, 80), (3, 100)], columnOffset=[(1, "both", 5), (2, "both", 5), (3, "both", 5)], parent=jointDisplayMainLayout)
        cmds.button("moveRight", label=self.dpUIinst.lang['c034_move'] + ' <<<', backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.dpMoveAttr, parent=buttonLayout)
        cmds.button("moveLeft", label=self.dpUIinst.lang['c034_move'] + ' >>>', backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.dpMoveAttr, parent=buttonLayout)
        cmds.button("Cancel", label=self.dpUIinst.lang['i132_cancel'], backgroundColor=(0.5, 0.5, 0.5), width=100, command=self.dpMoveAttr, parent=buttonLayout)
        cmds.separator(style='none', height=10, parent=buttonLayout)

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
 