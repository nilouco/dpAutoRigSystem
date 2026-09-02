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
        

    def build_tool(self, *args):
        # get selected item to create isolate setup on it
        self.selected = self.get_selected_item()
        if self.selected:
            # check if the selected item has a grand father node in hierarchy
            self.grandfather = self.get_grandfather_item()
            if self.grandfather:
                # call main function
                self.check_and_run_isolate()
    
    
    def get_selected_item(self):
        """ Get selected item
            Return selected item found
        """
        selected_items = cmds.ls(selection=True)
        if selected_items:
            return selected_items[0]
            
    
    def get_grandfather_item(self):
        """ Get grandfather node from selected item
            Return grandfather node found
        """
        fathers = cmds.listRelatives(self.selected, allParents=True, type="transform")
        if fathers:
            grandfathers = cmds.listRelatives(fathers[0], allParents=True, type="transform")
            if grandfathers:
                return grandfathers[0]
        
        
    def check_and_run_isolate(self):
        """ Main function.
            Check existing nodes and call the scripted function.
            # nodes[0] = Root_Ctrl
            # nodes[1] = Grand Father transform from selected item
            # nodes[2] = Selected item (control)
        """
        # declaring nodes to create the isolate setup:
        nodes = [self.ar.utils.get_node_by_message("rootCtrl"), self.grandfather, self.selected]
        if len(nodes) == 3:
            for node in nodes:
                if not cmds.objExists(node):
                    print(self.ar.data.lang['e004_objNotExist'], node)
                    return
        # call scripted function
        self.run_isolate(self.ar.data.lang['m095_isolate'].lower(), nodes)
        
        
    def run_isolate(self, attr_name, nodes):
        """ Function to run isolate setup.
        """
        # get father zero out transform node
        zero_grp = cmds.listRelatives(nodes[2], allParents=True, type="transform")[0]
        # create parent constraint
        pac = cmds.parentConstraint(nodes[0], nodes[1], zero_grp, maintainOffset=True, skipTranslate=["x", "y", "z"], name=zero_grp+"_PaC")[0]
        cmds.setAttr(pac+".interpType", 0) #noFlip
        # add isolate attribute to selected control
        cmds.addAttr(nodes[2], longName=attr_name, defaultValue=1.0, minValue=0, maxValue=1, keyable=True) 
        # create reverse node
        rev = cmds.createNode('reverse', name=nodes[2]+"_"+attr_name.capitalize()+"_Rev")
        self.ar.custom_attr.add_attr(0, [pac, rev]) #dpID
        # do isolate connections
        cmds.connectAttr(nodes[2]+"."+attr_name, pac+"."+nodes[0]+"W0", force=True)
        cmds.connectAttr(nodes[2]+"."+attr_name, rev+".inputX", force=True)
        cmds.connectAttr(rev+".outputX", pac+"."+nodes[1]+"W1", force=True)
        cmds.select(nodes[2])
