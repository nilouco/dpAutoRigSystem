# importing libraries:
from maya import cmds
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


    def build_tool(self, *args):
        # call main function
        if self.ar.data.ui_state:
            self.ar.copy_paste_attr_ui.create_ui()
