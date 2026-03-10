# importing libraries:
from maya import cmds
from maya import mel
from ..Modules.Base import dpBaseLibrary
from importlib import reload

# global variables to this module:    
CLASS_NAME = "PrintSelection"
TITLE = "m053_printSel"
DESCRIPTION = "m054_printSelDesc"
ICON = "/Icons/dp_printSelection.png"
WIKI = "06-‐-Tools#-print-selection"

DP_PRINTSELECTION_VERSION = 2.01


class PrintSelection(dpBaseLibrary.BaseLibrary):
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
        

    def build_tool(self, *args):
        # call main function
        self.dpMain(self)
    
    
    def dpMain(self, *args):
        """ Main function.
            Get selection and call the print function.
        """
        # get selection list
        self.selList = cmds.ls(selection=True)
        if self.selList:
            self.resultDic = self.dpDefineDic(self.selList)
            if self.resultDic:
                self.dpPrintResults(self.resultDic)
        else:
            mel.eval("warning \""+self.ar.data.lang['i042_notSelection']+"\";")
    
    
    def dpDefineDic(self, selList, *args):
        """ Recept the selection list and mount the result dictionary in order to print it.
        """
        toPrintDic = {}
        if selList:
            printString = ""
            for i, item in enumerate(selList):
                printString = printString + str(item)
                if i < len(selList):
                    printString = printString + ";"
            toPrintDic['string'] = printString
            toPrintDic['list'] = selList
        return toPrintDic
    
    
    def dpPrintResults(self, resultDic, *args):
        """ Recept the resultDictionary and print it.
        """
        if resultDic:
            # log
            print("\n-------")
            print("Print Selection Result:")
            print("List:")
            print(resultDic['list'])
            print("String:")
            print(resultDic['string'])
            print("-------")
        else:
            mel.eval("warning \""+self.ar.data.lang['i042_notSelection']+"\";")
