# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "PrintSelection"
TITLE = "m053_printSel"
DESCRIPTION = "m054_printSelDesc"
ICON = "/Icons/dp_printSelection.png"


class PrintSelection():
    def __init__(self, dpUIinst, langDic, langName, *args):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
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
            mel.eval("warning \""+self.langDic[self.langName]['i042_notSelection']+"\";")
    
    
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
            print "\n-------"
            print "Print Selection Result:"
            print "List:"
            print resultDic['list']
            print "String:"
            print resultDic['string']
            print "-------"
        else:
            mel.eval("warning \""+self.langDic[self.langName]['i042_notSelection']+"\";")
