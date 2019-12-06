# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "Isolate"
TITLE = "m095_isolate"
DESCRIPTION = "m096_isolateDesc"
ICON = "/Icons/dp_isolate.png"

dpIsolateVersion = 1.0

class Isolate():
    def __init__(self, dpUIinst, langDic, langName, *args):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        
        self.rootName = "Root"
        self.isolateName = self.langDic[self.langName]['m095_isolate']
        
        # base item to isolate
        self.rootCtrl = self.rootName+"_Ctrl"
        # get selected item to create isolate setup on it
        self.selItem = self.dpGetSelItem()
        if self.selItem:
            # check if the selected item has a grand father node in hierarchy
            self.grandFatherItem = self.dpGetGrandFatherItem()
            if self.grandFatherItem:
                # call main function
                self.dpMain(self)
    
    
    def dpGetSelItem(self, *args):
        """ Get selected item
            Return selected item found
        """
        selList = cmds.ls(selection=True)
        if selList:
            return selList[0]
            
    
    def dpGetGrandFatherItem(self, *args):
        """ Get grandfather node from selected item
            Return grandfather node found
        """
        fatherItem = cmds.listRelatives(self.selItem, allParents=True, type="transform")[0]
        if fatherItem:
            grandFatherItem = cmds.listRelatives(fatherItem, allParents=True, type="transform")[0]
            if grandFatherItem:
                return grandFatherItem
        
        
    def dpMain(self, *args):
        """ Main function.
            Check existen nodes and call the scripted function.
            # nodeList[0] = Root_Ctrl
            # nodeList[1] = Grand Father transform from selected item
            # nodeList[2] = Selected item (control)
        """
        # declaring nodeList to create the isolate setup:
        nodeList = [self.rootCtrl, self.grandFatherItem, self.selItem]
        if len(nodeList) == 3:
            for nodeName in nodeList:
                if not cmds.objExists(nodeName):
                    print self.langDic[self.langName]['e004_objNotExist'], nodeName
                    return
        # call scripted function
        self.dpIsolate(self.isolateName, nodeList)
        
        
    def dpIsolate(self, attrName, nodeList, *args):
        """ Function to run isolate setup.
        """
        # get father zero out transform node
        zeroGrp = cmds.listRelatives(nodeList[2], allParents=True, type="transform")[0]
        # create parent constraint
        pConst = cmds.parentConstraint(nodeList[0], nodeList[1], zeroGrp, maintainOffset=True, skipTranslate=["x", "y", "z"])[0]
        # add isolate attribute to selected control
        cmds.addAttr(nodeList[2], longName=attrName, defaultValue=1.0, minValue=0, maxValue=1, keyable=True) 
        # create reverse node
        reverseNode = cmds.createNode('reverse', name=nodeList[2]+"_"+attrName.capitalize()+"_Rev")
        # do isolate connections
        cmds.connectAttr(nodeList[2]+"."+attrName, pConst+"."+nodeList[0]+"W0", force=True)
        cmds.connectAttr(nodeList[2]+"."+attrName, reverseNode+".inputX", force=True)
        cmds.connectAttr(reverseNode+".outputX", pConst+"."+nodeList[1]+"W1", force=True)
        cmds.select(nodeList[2])
