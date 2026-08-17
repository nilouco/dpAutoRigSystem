class BaseLibrary(object):
    def __init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI):
        """ Declare the base variables.
        """
        self.ar = ar
        self.name = CLASS_NAME
        self.title = TITLE
        self.description = DESCRIPTION
        self.wiki = WIKI
        self.custom_name = None
