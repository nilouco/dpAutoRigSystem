# importing libraries:
import maya.cmds as cmds
from functools import partial
from ..Modules.Library import dpControls

# global variables to this module:
CLASS_NAME = "Renamer"
TITLE = "m178_renamer"
DESCRIPTION = "m179_renamerDesc"
ICON = "/Icons/dp_renamer.png"

DPRENAMER_VERSION = "0.1"


# import libraries
import maya.cmds as cmds


class Renamer():
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, ui=True, *args, **kwargs):
        # defining variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
        # call main function
        if ui:
            self.renamerUI()
    
    
    def closeRenamerUI(self, *args):
        """ Check if the UI exists then close it.
        """
        if cmds.window('dpRenamerWin', exists=True):
            cmds.deleteUI('dpRenamerWin', window=True)
    
    
    def renamerUI(self, *args):
        """ UI (window).
        """
        self.closeRenamerUI()
        # UI:
        dpRenamerWin = cmds.window('dpRenamerWin', title='Renamer - v '+DPRENAMER_VERSION, width=200, height=75, sizeable=True, minimizeButton=False, maximizeButton=False)
        # UI elements:
        mainLayout  = cmds.columnLayout('mainLayout', width=150, height=75, adjustableColumn=True, parent=dpRenamerWin)
        #copyButton         = cmds.button('copyButton', label=self.langDic[self.langName]['i122_copyAttr'], command=partial(self.ctrls.copyAttr, verbose=True), backgroundColor=(0.7, 1.0, 0.7), parent=mainLayout)
        #pasteButton        = cmds.button('pasteButton', label=self.langDic[self.langName]['i123_pasteAttr'], command=partial(self.ctrls.pasteAttr, verbose=True), backgroundColor=(1.0, 1.0, 0.7), parent=mainLayout)
        #copyAndPasteButton = cmds.button('copyAndPasteButton', label=self.langDic[self.langName]['i124_copyPasteAttr'], command=partial(self.ctrls.copyAndPasteAttr, True), backgroundColor=(0.7, 0.9, 1.0), parent=mainLayout)
        cmds.text('dpRenamer - WIP')
        textButton = cmds.button('testButton', label="testButton")#self.langDic[self.langName]['i124_copyPasteAttr']"", command=partial(self.ctrls.copyAndPasteAttr, True), backgroundColor=(0.7, 0.9, 1.0), parent=mainLayout)
        # calling UI:
        cmds.showWindow(dpRenamerWin)