# importing libraries:
from maya import cmds
from functools import partial
from ..base import base
from importlib import reload

# global variables to this module:
CLASS_NAME = "CustomAttr"
TITLE = "m212_customAttr"
DESCRIPTION = "m213_customAttrDesc"
WIKI = "06-‐-Tools#-custom-attributes"

ATTR_START = "dp"
ATTR_DPID = "dpID"
ATTR_LIST = [ATTR_DPID, "dpControl", "dpDoNotProxyIt", "dpDoNotSkinIt", "dpIgnoreIt", "dpKeepIt", "dpDeleteIt", "dpHeadDeformerInfluence", "dpJawDeformerInfluence", "dpNotTransformIO", "dpHolder"]
DEFAULTIGNORE_LIST = ['persp', 'top', 'front', 'side']
DEFAULTTYPE_LIST = ['transform', 'network']



class CustomAttr(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        self.do_not_display_suffixes = []
        self.start_attr = ATTR_START
        self.dpid_attr = ATTR_DPID
        self.attributes = ATTR_LIST.copy()
        self.ignores = DEFAULTIGNORE_LIST.copy()
        self.types = DEFAULTTYPE_LIST.copy()
        self.original_types = DEFAULTTYPE_LIST.copy()


    def build_tool(self, *args):
        # call main UI function
        if self.ar.data.ui_state:
            self.ar.custom_attr_ui.create_ui(self)


    def select_nodes(self, *args):
        """ Select the desired type nodes in the scene.
        """
        to_select_items = []
        if self.types:
            nodes = cmds.ls(type=self.types)
        else:
            nodes = cmds.ls(defaultNodes=False)
        if nodes:
            for item in nodes:
                if not item in to_select_items:
                    add_this_item = True
                    for suffix in self.do_not_display_suffixes:
                        if item.endswith(suffix):
                            add_this_item = False
                    if add_this_item:
                        to_select_items.append(item)
            if to_select_items:
                to_select_items.sort()
            cmds.select(to_select_items)
            self.update_ui()


    def get_descendents(self, items, shapes=True):
        """ Returns the children nodes or shapes from given item list.
        """
        results = []
        for item in items:
            if cmds.objExists(item):
                children = cmds.listRelatives(item, allDescendents=True, children=True)
                if shapes:
                    children = cmds.listRelatives(item, allDescendents=True, children=True, shapes=True)
                if children:
                    results.extend(children)
        return results


    def add_attr(self, attr_index, items=None, attr_name=None, shapes=True, descendents=False, *args):
        """ Create attributes in the selected node if they don't exists yet.
            Return a list of created dpID.
        """
        ids = []
        attr = None
        if not items:
            items = cmds.ls(selection=True)
        if items:
            if shapes:
                items.extend(self.get_descendents(items))
            if descendents:
                items.extend(self.get_descendents(items, False))
            items = list(set(items)) # just remove duplicated items
            for item in items:
                if cmds.objExists(item):
                    if attr_index == "custom":
                        if attr_name:
                            attr = attr_name
                        elif self.ar.data.ui_state:
                            attr = cmds.textFieldButtonGrp('custom_attr_add_tfbg', query=True, text=True)
                            if attr:
                                if not attr == self.start_attr:
                                    if not attr.startswith(self.start_attr):
                                        attr = self.start_attr+attr[0].capitalize()+attr[1:]
                                    else:
                                        point = len(self.start_attr)
                                        attr = attr[:point]+attr[point].capitalize()+attr[point+1:]
                                else:
                                    attr = None
                    elif attr_index == 0: #dpID
                        #if not cmds.objExists(item+"."+ATTR_DPID):
                        #if not ATTR_DPID in (cmds.listAttr(item, userDefined=True) or []):
                        if not cmds.attributeQuery(self.dpid_attr, node=item, exists=True):
                            id = self.ar.utils.generateID(item)
                            cmds.addAttr(item, longName=self.dpid_attr, dataType="string")
                            cmds.setAttr(item+"."+self.dpid_attr, id, type="string", lock=True)
                            ids.append(id)
                        elif not self.ar.utils.validateID(item):
                            ids.extend(self.update_id([item]))
                    else:
                        attr = self.attributes[attr_index]
                    if attr:
                        if not cmds.attributeQuery(attr, node=item, exists=True):
                            cmds.addAttr(item, longName=attr, attributeType="bool", defaultValue=1, keyable=False)
                            cmds.setAttr(item+"."+attr, edit=True, channelBox=False)
            if self.ar.data.ui_state and cmds.textFieldButtonGrp("addCustomAttrTFG", exists=True):
                cmds.textFieldButtonGrp('custom_attr_add_tfbg', edit=True, text="")
        return ids


    def remove_attr(self, attr, items=None, *args):
        """ Delete the given attribute and reload the remove_attr_ui.
        """
        items = self.get_valid_items(items)
        if items:
            for item in items:
                if cmds.attributeQuery(attr, node=item, exists=True):
                    cmds.setAttr(item+"."+attr, edit=True, lock=False)
                    cmds.deleteAttr(item+"."+attr)
                    if self.ar.data.ui_state:
                        if cmds.button("custom_attr_remove_"+attr+"_bt", query=True, exists=True):
                            cmds.deleteUI("custom_attr_remove_"+attr+"_bt")


    def get_custom_attrs(self, items=None, *args):
        """ Return all boolean attributes starting with "dp".
        """
        custom_attributes = []
        items = self.get_valid_items(items)
        if items:    
            for item in items:
                current_item_attrs = cmds.listAttr(item)
                if current_item_attrs:
                    if self.dpid_attr in current_item_attrs:
                        custom_attributes.append(self.dpid_attr)
                    for attr in current_item_attrs:
                        if attr.startswith(self.start_attr):
                            if cmds.getAttr(item+"."+attr, type=True) == "bool":
                                custom_attributes.append(attr)
        return custom_attributes


    def get_valid_items(self, items=None):
        """ Check if the items is a valid item or select all type to return it.
        """
        if not items:
            return cmds.ls(selection=True, type=self.types)
        return items


    def update_id(self, items=None, *args):
        """ Remove and Add a new dpID attribute.
        """
        self.remove_attr(self.dpid_attr, items)
        return self.add_attr(0, items)


    def reveal_id(self, items=None, win=False, *args):
        """ If UI, it opens a window to reveal the decomposed ID.
            Returns a dictionary with the IDs data.
        """
        id_data = {}
        if not items:
            items = [node for node in cmds.ls(selection=True) for suffix in self.do_not_display_suffixes if not node.endswith(suffix) and not node in self.ignores]
        if items:
            for item in items:
                decomposed_ids = self.ar.utils.decomposeID(item)
                id_data[item] = {#"node" : item,
                                self.dpid_attr : cmds.getAttr(item+"."+self.dpid_attr),
                                "name" : decomposed_ids[1],
                                "date" : decomposed_ids[2]
                               }
            if win:
                if id_data:
                    self.ar.custom_attr_ui.id_ui(id_data)
        return id_data
