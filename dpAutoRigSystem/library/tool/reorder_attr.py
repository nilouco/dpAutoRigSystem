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
            self.dpReorderAttrUI(self)
    
    
    def dpReorderAttrUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        # creating dpReorderAttrUI Window:
        self.ar.utils.close_ui('dpReorderAttrWindow')
        width  = 175
        height = 75
        cmds.window('dpReorderAttrWindow', title=self.ar.data.lang["m087_reorderAttr"]+" "+str(self.ar.data.version), widthHeight=(width, height), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        cmds.columnLayout('reorder_attr_cl', columnOffset=("left", 30))
        cmds.separator(style='none', height=7, parent='reorder_attr_cl')
        cmds.button('reorder_attr_up_bt', label=self.ar.data.lang["i154_up"], annotation=self.ar.data.lang["i155_upDesc"], width=110, backgroundColor=(0.45, 1.0, 0.6), command=partial(self.move_attr, 1, None, None, True, True), parent='reorder_attr_cl')
        cmds.separator(style='in', height=10, width=110, parent='reorder_attr_cl')
        cmds.button('reorder_attr_down_bt', label=self.ar.data.lang["i156_down"], annotation=self.ar.data.lang["i157_downDesc"], width=110, backgroundColor=(1.0, 0.45, 0.45), command=partial(self.move_attr, 0, None, None, True, True), parent='reorder_attr_cl')
        # call dpReorderAttrUI Window:
        cmds.showWindow('dpReorderAttrWindow')
    
    
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
                for obj in items:
                    user_def_attrs = cmds.listAttr(obj, userDefined=True)
                    if user_def_attrs:
                        if not attributes[0] in user_def_attrs:
                            if verbose:
                                mel.eval("warning \""+self.ar.data.lang["m235_selectedStaticAttr"]+"\";")
                        else:
                            cmds.scriptEditorInfo(suppressInfo=True)
                            # unlock all user defined attibutes before start the changing position:
                            lock_attrs = cmds.listAttr(obj, userDefined=True, locked=True)
                            if lock_attrs:
                                for lock_attr in lock_attrs:
                                    cmds.setAttr(obj+"."+lock_attr, lock=False)

                            # start moving attributes
                            if mode == 0: #down
                                if len(attributes) > 1:
                                    attributes.reverse()
                                    sorted_items = attributes.copy()
                                if len(attributes) == 1:
                                    sorted_items = attributes.copy()
                                for i in sorted_items:
                                    user_defs = cmds.listAttr(obj, userDefined=True)
                                    attr_size = len(user_defs)
                                    attr_pos = user_defs.index(i)
                                    cmds.deleteAttr(obj, attribute=user_defs[attr_pos])
                                    cmds.undo()
                                    for x in range(attr_pos+2,attr_size,1):
                                        cmds.deleteAttr(obj, attribute=user_defs[x])
                                        cmds.undo()
                                if skip_hidden:
                                    if attr_pos < attr_size-1:
                                        next_attr_type = cmds.attributeQuery(user_defs[attr_pos+1], node=obj, attributeType=True)
                                        if next_attr_type in self.next_attr_types or (not cmds.getAttr(obj+"."+user_defs[attr_pos+1], channelBox=True) and not cmds.getAttr(obj+"."+user_defs[attr_pos+1], keyable=True)):
                                            self.move_attr(mode, items, attributes, False, True)
                                        
                            elif mode == 1: #up
                                for i in attributes:
                                    user_defs = cmds.listAttr(obj, userDefined=True)
                                    attr_size = len(user_defs)
                                    attr_pos = user_defs.index(i)
                                    if user_defs[attr_pos-1]:
                                        cmds.deleteAttr(obj, at=user_defs[attr_pos-1])
                                        cmds.undo()
                                    for x in range(attr_pos+1,attr_size,1):
                                        cmds.deleteAttr(obj, at=user_defs[x])
                                        cmds.undo()
                                if skip_hidden:
                                    if attr_pos > 1:
                                        next_attr_type = cmds.attributeQuery(user_defs[attr_pos-1], node=obj, attributeType=True)
                                        if next_attr_type in self.next_attr_types or (not cmds.getAttr(obj+"."+user_defs[attr_pos-1], channelBox=True) and not cmds.getAttr(obj+"."+user_defs[attr_pos-1], keyable=True)):
                                            self.move_attr(mode, items, attributes, False, True)
                            
                            # lock all user defined attibutes after the changing position:
                            if lock_attrs:
                                for lock_attr in lock_attrs:
                                    cmds.setAttr(obj+"."+lock_attr, lock=True)
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
 