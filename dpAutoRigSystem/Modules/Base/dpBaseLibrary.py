# importing libraries:
from maya import cmds
from maya import mel

DP_BASETEMPLATE_VERSION = 1.00


class BaseLibrary(object):
    def __init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, ICON, WIKI):
        """ Initialize the module class creating a button in createGuidesLayout in order to be used to start the guide module.
        """
        # defining variables:
        self.ar = ar
        self.name = CLASS_NAME
        self.title = TITLE
        self.description = DESCRIPTION
        self.icon = ICON
        self.wiki = WIKI


    def ask_build_detail(self, title, opt1, opt2, cancel, default, message):
        """ Ask user the detail level we'll create the guides by a confirm dialog box window.
            Options:
                Simple
                Complete
            Returns the user choose option or None if canceled.
        """
        return cmds.confirmDialog(title=title, message=message, button=[opt1, opt2, cancel], defaultButton=default, cancelButton=cancel, dismissString=cancel)
