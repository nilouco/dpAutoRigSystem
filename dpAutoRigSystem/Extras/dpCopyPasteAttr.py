# importing libraries:
import maya.cmds as cmds
from functools import partial
from ..Modules.Library import dpControls

# global variables to this module:    
CLASS_NAME = "CopyPasteAttr"
TITLE = "m135_copyPasteAttr"
DESCRIPTION = "m136_copyPasteAttrDesc"
ICON = "/Icons/dp_copyPasteAttr.png"

DPCP_VERSION = "2.0"


# import libraries
import maya.cmds as cmds


class CopyPasteAttr():
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, *args, **kwargs):
        # defining variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
        # call main function
        self.copyPasteAttrUI()
    
    
    def closeCopyPasteAttrUI(self, *args):
        """ Check if the UI exists then close it.
        """
        if cmds.window('dpCopyPasteAttrWin', exists=True):
            cmds.deleteUI('dpCopyPasteAttrWin', window=True)
    
    
    def copyPasteAttrUI(self, *args):
        """ UI (window).
        """
        self.closeCopyPasteAttrUI()
        # UI:
        dpCopyPasteAttrWin = cmds.window('dpCopyPasteAttrWin', title='CopyPasteAttr - v'+DPCP_VERSION, width=200, height=75, sizeable=True, minimizeButton=False, maximizeButton=False)
        # UI elements:
        mainLayout  = cmds.columnLayout('mainLayout', width=150, height=75, adjustableColumn=True, parent=dpCopyPasteAttrWin)
        copyButton         = cmds.button('copyButton', label=self.langDic[self.langName]['i122_copyAttr'], command=partial(self.ctrls.copyAttr, verbose=True), backgroundColor=(0.7, 1.0, 0.7), parent=mainLayout)
        pasteButton        = cmds.button('pasteButton', label=self.langDic[self.langName]['i123_pasteAttr'], command=partial(self.ctrls.pasteAttr, verbose=True), backgroundColor=(1.0, 1.0, 0.7), parent=mainLayout)
        copyAndPasteButton = cmds.button('copyAndPasteButton', label=self.langDic[self.langName]['i124_copyPasteAttr'], command=partial(self.ctrls.copyAndPasteAttr, True), backgroundColor=(0.7, 0.9, 1.0), parent=mainLayout)
        # calling UI:
        cmds.showWindow(dpCopyPasteAttrWin)