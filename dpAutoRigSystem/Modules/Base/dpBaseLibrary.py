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
