# importing libraries:
from maya import cmds
from ..base import base
from importlib import reload

# global variables to this module:    
CLASS_NAME = "Isolate"
TITLE = "m095_isolate"
DESCRIPTION = "m096_isolateDesc"
WIKI = "06-‐-Tools#-isolate"



class Isolate(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        self.rootName = "Root"
        self.isolateName = self.ar.data.lang['m095_isolate'].lower()
        # base item to isolate
        self.rootCtrl = self.rootName+"_Ctrl"
        

    def build_tool(self, *args):
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
        fatherList = cmds.listRelatives(self.selItem, allParents=True, type="transform")
        if fatherList:
            grandFatherList = cmds.listRelatives(fatherList[0], allParents=True, type="transform")
            if grandFatherList:
                return grandFatherList[0]
        
        
    def dpMain(self, *args):
        """ Main function.
            Check existen nodes and call the scripted function.
            # nodes[0] = Root_Ctrl
            # nodes[1] = Grand Father transform from selected item
            # nodes[2] = Selected item (control)
        """
        # declaring nodes to create the isolate setup:
        nodes = [self.rootCtrl, self.grandFatherItem, self.selItem]
        if len(nodes) == 3:
            for nodeName in nodes:
                if not cmds.objExists(nodeName):
                    print(self.ar.data.lang['e004_objNotExist'], nodeName)
                    return
        # call scripted function
        self.dpIsolate(self.isolateName, nodes)
        
        
    def dpIsolate(self, attr_name, nodes, *args):
        """ Function to run isolate setup.
        """
        # get father zero out transform node
        zero_grp = cmds.listRelatives(nodes[2], allParents=True, type="transform")[0]
        # create parent constraint
        pConst = cmds.parentConstraint(nodes[0], nodes[1], zero_grp, maintainOffset=True, skipTranslate=["x", "y", "z"], name=zero_grp+"_PaC")[0]
        cmds.setAttr(pConst+".interpType", 0) #noFlip
        # add isolate attribute to selected control
        cmds.addAttr(nodes[2], longName=attr_name, defaultValue=1.0, minValue=0, maxValue=1, keyable=True) 
        # create reverse node
        reverseNode = cmds.createNode('reverse', name=nodes[2]+"_"+attr_name.capitalize()+"_Rev")
        self.ar.custom_attr.add_attr(0, [pConst, reverseNode]) #dpID
        # do isolate connections
        cmds.connectAttr(nodes[2]+"."+attr_name, pConst+"."+nodes[0]+"W0", force=True)
        cmds.connectAttr(nodes[2]+"."+attr_name, reverseNode+".inputX", force=True)
        cmds.connectAttr(reverseNode+".outputX", pConst+"."+nodes[1]+"W1", force=True)
        cmds.select(nodes[2])
