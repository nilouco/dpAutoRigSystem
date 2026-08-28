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
        # call main function
        self.dpTargetMirrorUI(self)
    
    
    def dpTargetMirrorUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        self.ar.utils.close_ui('dpTargetMirrorWindow')
        # creating targetMirrorUI Window:
        width  = 305
        height = 250
        cmds.window('dpTargetMirrorWindow', title=self.ar.data.lang["m055_tgtMirror"]+" "+str(self.ar.data.version), widthHeight=(width, height), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        cmds.columnLayout('target_mirror_main_cl')
        cmds.rowColumnLayout('target_mirror_header_rcl', numberOfColumns=2, columnWidth=[(1, 120), (2, 190)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 20)], parent='target_mirror_main_cl')
        cmds.button('target_mirror_load_orig_model_bt', label=self.ar.data.lang["i043_origModel"]+" >", annotation=self.ar.data.lang["i044_origDesc"], backgroundColor=(1.0, 1.0, 0.7), width=120, command=self.load_original_model, parent='target_mirror_header_rcl')
        cmds.textField('target_mirror_orig_model_tf', width=160, text="", parent='target_mirror_header_rcl')
        cmds.columnLayout('target_mirror_cl', columnOffset=('left', 10), width=310, parent='target_mirror_main_cl')
        cmds.text('target_mirror_targets_txt', label=self.ar.data.lang["i047_targetList"], height=30, parent='target_mirror_cl')
        cmds.textScrollList('target_mirror_targets_tsl', width=290, height=100, allowMultiSelection=True, parent='target_mirror_cl')
        cmds.separator(style='none', parent='target_mirror_cl')
        cmds.rowColumnLayout('target_mirror_middle_rcl', numberOfColumns=2, columnWidth=[(1, 150), (2, 150)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 0)], parent='target_mirror_cl')
        cmds.button('target_mirror_add_bt', label=self.ar.data.lang["i045_add"], annotation=self.ar.data.lang["i048_addDesc"], width=140, command=self.add_selected, parent='target_mirror_middle_rcl')
        cmds.button('target_mirror_remove_bt', label=self.ar.data.lang["i046_remove"], annotation=self.ar.data.lang["i051_removeDesc"], width=140, command=self.remove_selected, parent='target_mirror_middle_rcl')
        cmds.separator(style='none', height=15, parent='target_mirror_middle_rcl')
        cmds.rowColumnLayout('target_mirror_rename_rcl', numberOfColumns=3, columnWidth=[(1, 100), (2, 100), (3, 100)], columnAlign=[(1, 'left'), (2, 'left'), (3, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 0), (3, 'left', 0)], parent='target_mirror_cl')
        cmds.checkBox('target_mirror_auto_rename_cb', label=self.ar.data.lang["i056_autoRename"], value=1, onCommand=partial(self.change_rename, 1), offCommand=partial(self.change_rename, 0), parent='target_mirror_rename_rcl')
        cmds.text('target_mirror_from_txt', label="from", parent='target_mirror_rename_rcl')
        cmds.text('target_mirror_to_txt', label="to", parent='target_mirror_rename_rcl')
        cmds.separator(style='none', height=15, parent='target_mirror_rename_rcl')
        cmds.textField('target_mirror_from_tf', width=80, text="L_", parent='target_mirror_rename_rcl')
        cmds.textField('target_mirror_to_tf', width=80, text="R_", parent='target_mirror_rename_rcl')
        cmds.text('target_mirror_axis_txt', label="Axis:", height=20, parent='target_mirror_cl')
        cmds.rowColumnLayout('target_mirror_axis_rcl', numberOfColumns=3, columnWidth=[(1, 100), (2, 100), (3, 100)], columnAlign=[(1, 'left'), (2, 'left'), (3, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 0), (3, 'left', 0)], parent='target_mirror_cl')
        cmds.radioCollection('target_mirror_axis_rc', parent='target_mirror_axis_rcl')
        cmds.radioButton('target_mirror_axis_x_rb', label="X = YZ", annotation="X", align="left", collection="target_mirror_axis_rc", parent='target_mirror_axis_rcl')
        cmds.radioButton('target_mirror_axis_y_rb', label="Y = XZ", annotation="Y", align="left", collection="target_mirror_axis_rc", parent='target_mirror_axis_rcl')
        cmds.radioButton('target_mirror_axis_z_rb', label="Z = XY", annotation="Z", align="left", collection="target_mirror_axis_rc", parent='target_mirror_axis_rcl')
        cmds.radioCollection('target_mirror_axis_rc', edit=True, select='target_mirror_axis_x_rb')
        cmds.separator(style='none', height=15, parent='target_mirror_cl')
        cmds.checkBox('target_mirror_pos_cb', label=self.ar.data.lang["i057_mirrorPosition"], value=1, parent='target_mirror_cl')
        cmds.checkBox('target_mirror_clear_undo_cb', label=self.ar.data.lang["i049_clearUndo"], annotation=self.ar.data.lang["i050_clearUndoDesc"], align="left", value=1, parent='target_mirror_cl')
        cmds.checkBox('target_mirror_check_hist_cb', label=self.ar.data.lang["i162_checkHistory"], annotation=self.ar.data.lang["i161_historyMessage"], align="left", value=0, parent='target_mirror_cl')
        cmds.button('target_mirror_run_bt', label=self.ar.data.lang["i054_targetRun"], annotation=self.ar.data.lang["i053_targetRunDesc"], width=290, backgroundColor=(0.6, 1.0, 0.6), command=self.run_target_mirror, parent='target_mirror_cl')
        # call targetMirrorUI Window:
        cmds.showWindow('dpTargetMirrorWindow')
    
    
    def load_original_model(self, *args):
        """ Load selected object as original model
        """
        selected_nodes = cmds.ls(selection=True)
        if selected_nodes:
            if self.check_geometry(selected_nodes[0]):
                cmds.textField('target_mirror_orig_model_tf', edit=True, text=selected_nodes[0])
        else:
            print("Original Model > None")
    
    
    def add_selected(self, *args):
        """ Add selected items to target textscroll list
        """
        # declare variables
        meshes = []
        # get selection
        selection = cmds.ls(selection=True)
        # check if there is any selected object in order to continue
        if selection:
            # find meshes transforms
            for item in selection:
                if not item in meshes:
                    if self.check_geometry(item):
                        meshes.append(item)
                    else:
                        return
            if meshes:
                # get current list
                current_items = cmds.textScrollList('target_mirror_targets_tsl', query=True, allItems=True)
                if current_items:
                    # clear current list
                    cmds.textScrollList('target_mirror_targets_tsl', edit=True, removeAll=True)
                    # avoid repeated items
                    for item in meshes:
                        if not item in current_items:
                            current_items.append(item)
                    # refresh textScrollList
                    cmds.textScrollList('target_mirror_targets_tsl', edit=True, append=current_items)
                else:
                    # add selected items in the empyt target scroll list
                    cmds.textScrollList('target_mirror_targets_tsl', edit=True, append=meshes)
            else:
                mel.eval("warning \""+self.ar.data.lang["i055_tgtSelect"]+"\";")
        else:
            mel.eval("warning \""+self.ar.data.lang["i055_tgtSelect"]+"\";")
    
    
    def remove_selected(self, *args):
        """ Remove selected items from target scroll list.
        """
        selItemList = cmds.textScrollList('target_mirror_targets_tsl', query=True, selectItem=True)
        if selItemList:
            for item in selItemList:
                cmds.textScrollList('target_mirror_targets_tsl', edit=True, removeItem=item)
    
    
    def change_rename(self, value, *args):
        """ Enable or disable text fields
        """
        cmds.text('target_mirror_from_txt', edit=True, enable=value)
        cmds.text('target_mirror_to_txt', edit=True, enable=value)
        cmds.textField('target_mirror_from_tf', edit=True, enable=value)
        cmds.textField('target_mirror_to_tf', edit=True, enable=value)
    
    
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
    
    
    def run_target_mirror(self, *args):
        """ Create the mirrored targets.
        """
        # declaring variables
        attributes = ["tx", "ty", "tz"]
        # get loaded original node
        origNode = cmds.textField('target_mirror_orig_model_tf', query=True, text=True)
        if self.check_geometry(origNode):
            # get target list:
            targets = cmds.textScrollList('target_mirror_targets_tsl', query=True, allItems=True)
            if targets:
                self.ar.utils.setProgress('Target: '+self.ar.data.lang['c110_start'], self.ar.data.lang["m055_tgtMirror"], len(targets), add_one=False, add_number=False)
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
                    self.ar.utils.setProgress("Target: "+item)
                    if not item == origNode:
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
                            temp_dup = cmds.duplicate(origNode, name="temp_dupOrig")[0]
                            # create a temporary blendShape node
                            temp_to_wrap_bs = cmds.blendShape(item, temp_dup, topologyCheck=False, name="temp_toWRAP_BS")[0]
                            # make a duplicated model group
                            bs_mirror_grp = cmds.group(temp_dup, name="temp_bsMirrorGrp")
                            # apply mirror
                            cmds.setAttr(bs_mirror_grp+".scale"+axis, -1)
                            # create a new copy of the original model in order to be the mirrored target
                            new_target = cmds.duplicate(origNode, name=new_target_name)[0]
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
                self.ar.utils.setProgress(endIt=True)
                self.ar.custom_attr.add_attr(0, self.to_ids, descendents=True) #dpID
            cmds.select(clear=True)
