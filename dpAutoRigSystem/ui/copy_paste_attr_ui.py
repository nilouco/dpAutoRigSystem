#import libraries
from maya import cmds
from functools import partial


class CopyPasteAttrUI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self):
        """ This is the main method to load the Copy Paste Attr UI.
        """
        self.ar.utils.close_ui('dpCopyPasteAttrWin')
        cmds.window('dpCopyPasteAttrWin', title='CopyPasteAttr - v'+str(self.ar.data.version), width=200, height=75, sizeable=True, minimizeButton=False, maximizeButton=False)
        cmds.columnLayout('copy_paste_attr_cl', width=150, height=75, adjustableColumn=True, parent='dpCopyPasteAttrWin')
        cmds.button('copy_attr_bt', label=self.ar.data.lang['i122_copyAttr'], command=partial(self.ar.ctrls.copy_attr, verbose=True), backgroundColor=(0.7, 1.0, 0.7), parent='copy_paste_attr_cl')
        cmds.button('paste_attr_bt', label=self.ar.data.lang['i123_pasteAttr'], command=partial(self.ar.ctrls.paste_attr, verbose=True), backgroundColor=(1.0, 1.0, 0.7), parent='copy_paste_attr_cl')
        cmds.button('copy_paste_attr_bt', label=self.ar.data.lang['i124_copyPasteAttr'], command=partial(self.ar.ctrls.copy_and_paste_attr, True), backgroundColor=(0.7, 0.9, 1.0), parent='copy_paste_attr_cl')
        cmds.showWindow('dpCopyPasteAttrWin')
