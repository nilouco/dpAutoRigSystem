# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
from ..base import base
from importlib import reload

# global variables to this module:
CLASS_NAME = "TargetMirror"
TITLE = "m055_tgtMirror"
DESCRIPTION = "m056_tgtMirrorDesc"
WIKI = "06-‐-Tools#-target-mirror"



class TargetMirror(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
    
    
    def build_tool(self, *args):
        self.ar.target_mirror_ui.create_ui(self)
    
    
    def check_geometry(self, item):
        is_geometry = False
        if item:
            if cmds.objExists(item):
                children = cmds.listRelatives(item, children=True)
                if children:
                    try:
                        item_type = cmds.objectType(children[0])
                        if item_type == "mesh" or item_type == "nurbsSurface" or item_type == "subdiv":
                            if cmds.checkBox('target_mirror_check_hist_cb', query=True, value=True):
                                hist_items = cmds.listHistory(children[0])
                                if len(hist_items) > 1:
                                    dialog_result = cmds.confirmDialog(title=self.ar.data.lang["i159_historyFound"], message=self.ar.data.lang["i160_historyDesc"]+"\n\n"+item+"\n\n"+self.ar.data.lang["i161_historyMessage"], button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No')
                                    if dialog_result == "Yes":
                                        is_geometry = True
                                else:
                                    is_geometry = True
                            else:
                                is_geometry = True
                        else:
                            mel.eval("warning \""+item+" "+self.ar.data.lang["i058_notGeo"]+"\";")
                    except:
                        mel.eval("warning \""+self.ar.data.lang["i163_sameName"]+" "+item+"\";")
                else:
                    mel.eval("warning \""+self.ar.data.lang["i059_selTransform"]+" "+item+" "+self.ar.data.lang["i060_shapePlease"]+"\";")
            else:
                mel.eval("warning \""+item+" "+self.ar.data.lang["i061_notExists"]+"\";")
        else:
            mel.eval("warning \""+self.ar.data.lang["i062_notFound"]+" "+item+"\";")
        return is_geometry
    
    
    def run_target_mirror(self, original_model=None, target_items=None, *args):
        """ Create the mirrored targets.
        """
        # declaring variables
        attributes = ["tx", "ty", "tz"]
        # get loaded original node
        orig_node = original_model
        if not orig_node:
            orig_node = cmds.textField('target_mirror_orig_model_tf', query=True, text=True)
        if orig_node:
            if self.check_geometry(orig_node):
                # get target list:
                targets = target_items
                if not targets:
                    targets = cmds.textScrollList('target_mirror_targets_tsl', query=True, allItems=True)
                if targets:
                    self.ar.utils.set_progress('Target: '+self.ar.data.lang['c110_start'], self.ar.data.lang["m055_tgtMirror"], len(targets), add_one=False, add_number=False)
                    cancelled = False
                    self.to_ids = []
                    # get mirror information from UI
                    selected_mirror = cmds.radioCollection('target_mirror_axis_rc', query=True, select=True)
                    axis = cmds.radioButton(selected_mirror, query=True, annotation=True)
                    clear_undo = cmds.checkBox('target_mirror_clear_undo_cb', query=True, value=True)
                    # clear selection
                    cmds.select(clear=True)
                    for item in targets:
                        # check if the dialog has been cancelled
                        if cmds.progressWindow(query=True, isCancelled=True):
                            cancelled = True
                            break
                        self.ar.utils.set_progress("Target: "+item)
                        if not item == orig_node:
                            # start copying
                            if self.check_geometry(item):
                                # naming
                                new_target_name = item+"_Mirror"+axis
                                if cmds.checkBox('target_mirror_auto_rename_cb', query=True, value=True):
                                    from_name = cmds.textField('target_mirror_from_tf', query=True, text=True)
                                    to_name = cmds.textField('target_mirror_to_tf', query=True, text=True)
                                    if from_name in item:
                                        new_target_name = item.replace(from_name, to_name)
                                # duplicate original model
                                temp_dup = cmds.duplicate(orig_node, name="temp_dupOrig")[0]
                                # create a temporary blendShape node
                                temp_to_wrap_bs = cmds.blendShape(item, temp_dup, topologyCheck=False, name="temp_toWRAP_BS")[0]
                                # make a duplicated model group
                                bs_mirror_grp = cmds.group(temp_dup, name="temp_bsMirrorGrp")
                                # apply mirror
                                cmds.setAttr(bs_mirror_grp+".scale"+axis, -1)
                                # create a new copy of the original model in order to be the mirrored target
                                new_target = cmds.duplicate(orig_node, name=new_target_name)[0]
                                self.to_ids.append(new_target)
                                # create a wrap deformer from bs_mirror_grp to new_target
                                cmds.select([new_target, bs_mirror_grp])
                                mel.eval("CreateWrap;")
                                # set blendShape slider as 1
                                cmds.setAttr(temp_to_wrap_bs+"."+item, 1)
                                # clear history and temporary  group
                                cmds.delete(new_target, constructionHistory=True)
                                cmds.delete(bs_mirror_grp)
                                # position:
                                if cmds.checkBox('target_mirror_pos_cb', query=True, value=True):
                                    try:
                                        for attr in attributes:
                                            cmds.setAttr(new_target+"."+attr, cmds.getAttr(item+"."+attr))
                                        axis_value = cmds.getAttr(item+".translate"+axis)*(-1)
                                        cmds.setAttr(new_target+".translate"+axis, axis_value)
                                    except:
                                        pass
                                # clear undo
                                if clear_undo:
                                    mel.eval("flushUndo;")
                    self.ar.utils.set_progress(end_it=True)
                    self.ar.custom_attr.add_attr(0, self.to_ids, descendents=True) #dpID
                cmds.select(clear=True)
