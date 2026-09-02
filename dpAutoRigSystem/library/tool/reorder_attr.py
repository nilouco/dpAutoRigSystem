# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
from ..base import base
from importlib import reload

# global variables to this module:
CLASS_NAME = "ReorderAttr"
TITLE = "m087_reorderAttr"
DESCRIPTION = "m088_reoderAttrDesc"
WIKI = "06-‐-Tools#-reorder-attributes"



class ReorderAttr(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        self.next_attr_types = ["message", "typed"]
        

    def build_tool(self, *args):
        # call main function
        if self.ar.data.ui_state:
            self.ar.reorder_attr_ui.create_ui(self)
    
    
    def move_attr(self, mode, items=None, attributes=None, verbose=False, skip_hidden=False, *args):
        """ Change order of attributes in order to move it to up or down in the list position.
        """
        # do ScriptEditor do not print Undo messages:
        cmds.scriptEditorInfo(suppressInfo=False)
        if not items:
            # get current selected objects:
            items = cmds.channelBox('mainChannelBox', query=True, mainObjectList=True)
        if items:
            if not attributes:
                # get selected attributes from channelBox
                attributes = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)
            if attributes:
                for item in items:
                    user_def_attrs = cmds.listAttr(item, userDefined=True)
                    if user_def_attrs:
                        if not attributes[0] in user_def_attrs:
                            if verbose:
                                mel.eval("warning \""+self.ar.data.lang["m235_selectedStaticAttr"]+"\";")
                        else:
                            cmds.scriptEditorInfo(suppressInfo=True)
                            # unlock all user defined attibutes before start the changing position:
                            lock_attrs = cmds.listAttr(item, userDefined=True, locked=True)
                            if lock_attrs:
                                for lock_attr in lock_attrs:
                                    cmds.setAttr(item+"."+lock_attr, lock=False)

                            # start moving attributes
                            if mode == 0: #down
                                if len(attributes) > 1:
                                    attributes.reverse()
                                    sorted_items = attributes.copy()
                                if len(attributes) == 1:
                                    sorted_items = attributes.copy()
                                for i in sorted_items:
                                    user_defs = cmds.listAttr(item, userDefined=True)
                                    attr_size = len(user_defs)
                                    attr_pos = user_defs.index(i)
                                    cmds.deleteAttr(item, attribute=user_defs[attr_pos])
                                    cmds.undo()
                                    for x in range(attr_pos+2,attr_size,1):
                                        cmds.deleteAttr(item, attribute=user_defs[x])
                                        cmds.undo()
                                if skip_hidden:
                                    if attr_pos < attr_size-1:
                                        next_attr_type = cmds.attributeQuery(user_defs[attr_pos+1], node=item, attributeType=True)
                                        if next_attr_type in self.next_attr_types or (not cmds.getAttr(item+"."+user_defs[attr_pos+1], channelBox=True) and not cmds.getAttr(item+"."+user_defs[attr_pos+1], keyable=True)):
                                            self.move_attr(mode, items, attributes, False, True)
                                        
                            elif mode == 1: #up
                                for i in attributes:
                                    user_defs = cmds.listAttr(item, userDefined=True)
                                    attr_size = len(user_defs)
                                    attr_pos = user_defs.index(i)
                                    if user_defs[attr_pos-1]:
                                        cmds.deleteAttr(item, at=user_defs[attr_pos-1])
                                        cmds.undo()
                                    for x in range(attr_pos+1,attr_size,1):
                                        cmds.deleteAttr(item, at=user_defs[x])
                                        cmds.undo()
                                if skip_hidden:
                                    if attr_pos > 1:
                                        next_attr_type = cmds.attributeQuery(user_defs[attr_pos-1], node=item, attributeType=True)
                                        if next_attr_type in self.next_attr_types or (not cmds.getAttr(item+"."+user_defs[attr_pos-1], channelBox=True) and not cmds.getAttr(item+"."+user_defs[attr_pos-1], keyable=True)):
                                            self.move_attr(mode, items, attributes, False, True)
                            
                            # lock all user defined attibutes after the changing position:
                            if lock_attrs:
                                for lock_attr in lock_attrs:
                                    cmds.setAttr(item+"."+lock_attr, lock=True)
                    else:
                        if verbose:
                            mel.eval("warning \""+self.ar.data.lang["m236_canReorderUserDefAttr"]+"\";")
            else:
                if verbose:
                    mel.eval("warning \""+self.ar.data.lang["m237_selectChannelBoxAttr"]+"\";")
        else:
            if verbose:
                mel.eval("warning \""+self.ar.data.lang["m238_selectTransform"]+"\";")
        # back ScritpEditor to show info:
        cmds.scriptEditorInfo(suppressInfo=True)
 