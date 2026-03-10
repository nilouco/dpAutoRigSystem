# importing libraries:
from maya import cmds
from functools import partial
from ..Modules.Library import dpControls
from ..Modules.Base import dpBaseLibrary
from importlib import reload

# global variables to this module:    
CLASS_NAME = "CopyPasteAttr"
TITLE = "m135_copyPasteAttr"
DESCRIPTION = "m136_copyPasteAttrDesc"
ICON = "/Icons/dp_copyPasteAttr.png"
WIKI = "06-‐-Tools#-copy-paste-attribute"

DP_COPYPASTEATTR_VERSION = 2.04


class CopyPasteAttr(dpBaseLibrary.BaseLibrary):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        kwargs["WIKI"] = WIKI
        dpBaseLibrary.BaseLibrary.__init__(self, *args, **kwargs)
        if self.ar.dev:
            reload(dpBaseLibrary)
            reload(dpControls)

#        self.ar.ctrls = dpControls.ControlClass(self.ar)


    def build_tool(self):
        # call main function
        self.copyPasteAttrUI()
    
    
    # def closeCopyPasteAttrUI(self, *args):
    #     """ Check if the UI exists then close it.
    #     """
    #     if cmds.window('dpCopyPasteAttrWin', exists=True):
    #         cmds.deleteUI('dpCopyPasteAttrWin', window=True)
    
    
    def copyPasteAttrUI(self, *args):
        """ UI (window).
        """
#        self.closeCopyPasteAttrUI()
        self.ar.utils.closeUI("dpCopyPasteAttrWin")


        # UI:
        dpCopyPasteAttrWin = cmds.window('dpCopyPasteAttrWin', title='CopyPasteAttr - v'+str(DP_COPYPASTEATTR_VERSION), width=200, height=75, sizeable=True, minimizeButton=False, maximizeButton=False)
        # UI elements:
        mainLayout  = cmds.columnLayout('mainLayout', width=150, height=75, adjustableColumn=True, parent=dpCopyPasteAttrWin)
        cmds.button('copyButton', label=self.ar.data.lang['i122_copyAttr'], command=partial(self.ar.ctrls.copyAttr, verbose=True), backgroundColor=(0.7, 1.0, 0.7), parent=mainLayout)
        cmds.button('pasteButton', label=self.ar.data.lang['i123_pasteAttr'], command=partial(self.ar.ctrls.pasteAttr, verbose=True), backgroundColor=(1.0, 1.0, 0.7), parent=mainLayout)
        cmds.button('copyAndPasteButton', label=self.ar.data.lang['i124_copyPasteAttr'], command=partial(self.ar.ctrls.copyAndPasteAttr, True), backgroundColor=(0.7, 0.9, 1.0), parent=mainLayout)
        # calling UI:
        cmds.showWindow(dpCopyPasteAttrWin)