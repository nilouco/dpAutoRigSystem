# importing libraries:
from maya import cmds
from functools import partial
from ..util import controllers
from ..base import base
from importlib import reload

# global variables to this module:    
CLASS_NAME = "CopyPasteAttr"
TITLE = "m135_copyPasteAttr"
DESCRIPTION = "m136_copyPasteAttrDesc"
WIKI = "06-‐-Tools#-copy-paste-attribute"



class CopyPasteAttr(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
            reload(controllers)

#        self.ar.ctrls = controllers.Controllers(self.ar)


    def build_tool(self, *args):
        # call main function
        if self.ar.data.ui_state:
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
        self.ar.utils.close_ui("dpCopyPasteAttrWin")


        # UI:
        dpCopyPasteAttrWin = cmds.window('dpCopyPasteAttrWin', title='CopyPasteAttr - v'+str(self.ar.data.version), width=200, height=75, sizeable=True, minimizeButton=False, maximizeButton=False)
        # UI elements:
        mainLayout  = cmds.columnLayout('mainLayout', width=150, height=75, adjustableColumn=True, parent=dpCopyPasteAttrWin)
        cmds.button('copyButton', label=self.ar.data.lang['i122_copyAttr'], command=partial(self.ar.ctrls.copyAttr, verbose=True), backgroundColor=(0.7, 1.0, 0.7), parent=mainLayout)
        cmds.button('pasteButton', label=self.ar.data.lang['i123_pasteAttr'], command=partial(self.ar.ctrls.pasteAttr, verbose=True), backgroundColor=(1.0, 1.0, 0.7), parent=mainLayout)
        cmds.button('copyAndPasteButton', label=self.ar.data.lang['i124_copyPasteAttr'], command=partial(self.ar.ctrls.copyAndPasteAttr, True), backgroundColor=(0.7, 0.9, 1.0), parent=mainLayout)
        # calling UI:
        cmds.showWindow(dpCopyPasteAttrWin)