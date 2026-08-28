# importing libraries:
from maya import cmds
from maya import mel
from ..base import base
from importlib import reload

# global variables to this module:    
CLASS_NAME = "PrintSelection"
TITLE = "m053_printSel"
DESCRIPTION = "m054_printSelDesc"
WIKI = "06-‐-Tools#-print-selection"



class PrintSelection(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        

    def build_tool(self, *args):
        # call main function
        self.get_selection_and_run()
    
    
    def get_selection_and_run(self):
        """ Get selection and call the print function.
        """
        # get selection list
        selection = cmds.ls(selection=True)
        if selection:
            data = self.get_data(selection)
            if data:
                self.run_printing(data)
        else:
            mel.eval("warning \""+self.ar.data.lang['i042_notSelection']+"\";")
    
    
    def get_data(self, selection):
        """ Recept the selection list and mount the result dictionary in order to print it.
        """
        data = {}
        if selection:
            text = ""
            for i, item in enumerate(selection):
                text = text + str(item)
                if i < len(selection):
                    text = text + ";"
            data['string'] = text
            data['list'] = selection
        return data
    
    
    def run_printing(self, data):
        """ Recept the resultDictionary and print it.
        """
        if data:
            # log
            print("\n-------")
            print("Print Selection Result:")
            print("List:")
            print(data['list'])
            print("String:")
            print(data['string'])
            print("-------")
        else:
            mel.eval("warning \""+self.ar.data.lang['i042_notSelection']+"\";")
