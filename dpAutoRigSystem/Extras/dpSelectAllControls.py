# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "SelectAllControls"
TITLE = "m166_selAllControls"
DESCRIPTION = "m167_selAllControlsDesc"
ICON = "/Icons/dp_selAllControls.png"


class SelectAllControls():
    def __init__(self, dpUIinst, langDic, langName, *args):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.allGrp = "All_Grp"
        self.masterAttr = "masterGrp"
        self.ctrlsAttr = "controlList"
        # call main function
        self.dpMain(self)
    
    
    def dpMain(self, *args):
        """ Main function.
            Check existen nodes and call the scripted function.
        """
        callAction = False
        self.allGrp = self.dpFindAllGrpBySelection()
        if self.allGrp:
            callAction = True
        else:
            allGrpList = self.dpCountAllGrp()
            if allGrpList:
                if len(allGrpList) > 1:
                    self.allGrp = cmds.confirmDialog(title=self.langDic[self.langName]["m166_selAllControls"], message=self.langDic[self.langName]["m168_wichAllGrp"], button=allGrpList)
                else:
                    self.allGrp = self.dpCheckAllGrp(self.allGrp)
                if self.allGrp:
                    callAction = True
                else:
                    self.allGrp = self.dpFindAllGrp()
                    if self.allGrp:
                        callAction = True
        if callAction:
            self.dpSelectAllCtrls(self.allGrp)
        else:
            mel.eval("warning \""+self.langDic[self.langName]["e019_notFoundAllGrp"]+"\";")
    
    
    def dpCountAllGrp(self, *args):
        """ Count the number of active All_Grp and return them in a list.
        """
        allGrpNodeList = []
        allNodeList = cmds.ls(selection=False, type="transform")
        for nodeName in allNodeList:
            allGrp = self.dpCheckAllGrp(nodeName)
            if allGrp:
                allGrpNodeList.append(allGrp)
        return allGrpNodeList
    
    
    def dpSelectAllCtrls(self, allGrpNode, *args):
        """ Select all controls using All_Grp.
        """
        ctrlsToSelectList = []
        if cmds.objExists(allGrpNode+"."+self.ctrlsAttr):
            ctrlsAttr = cmds.getAttr(allGrpNode+"."+self.ctrlsAttr)
            if ctrlsAttr:
                currentNamespace = ""
                if ":" in allGrpNode:
                    currentNamespace = allGrpNode[:allGrpNode.find(":")]
                ctrlsList = ctrlsAttr.split(";")
                if ctrlsList:
                    for ctrlName in ctrlsList:
                        if ctrlName:
                            if currentNamespace:
                                ctrlsToSelectList.append(currentNamespace+":"+ctrlName)
                            else:
                                ctrlsToSelectList.append(ctrlName)
                    cmds.select(ctrlsToSelectList)
                    print self.langDic[self.langName]["m169_selectedCtrls"]+str(ctrlsToSelectList)
            else:
                mel.eval("warning \""+self.langDic[self.langName]["e019_notFoundAllGrp"]+"\";")
    
    
    def dpFindAllGrpBySelection(self, *args):
        """ Try to find All_Grp by selected hierarchy.
        """
        selList = cmds.ls(selection=True)
        if selList:
            for item in selList:
                if self.dpCheckAllGrp(item):
                    return item
            for item in selList:
                relativeList = cmds.listRelatives(item, allParents=True, type="transform")
                while relativeList:
                    if self.dpCheckAllGrp(relativeList[0]):
                        return relativeList[0]
                    relativeList = cmds.listRelatives(relativeList[0], allParents=True, type="transform")
        return False
        
        
    def dpFindAllGrp(self, *args):
        """ Try to find All_Grp without selection searching for all nodes in the scene.
            Returns the first one found.
        """
        allNodeList = cmds.ls(selection=False)
        if allNodeList:
            for item in allNodeList:
                if self.dpCheckAllGrp(item):
                    return item
        return False
        
        
    def dpCheckAllGrp(self, nodeName, *args):
        """ Verify if this given node is a masterGrp in order to return True.
        """
        if cmds.objExists(nodeName):
            if cmds.objExists(nodeName+"."+self.masterAttr):
                if cmds.getAttr(nodeName+"."+self.masterAttr) == 1:
                    return nodeName
        return False
        