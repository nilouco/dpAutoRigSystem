#import libraries
from maya import cmds
from maya import mel
from functools import partial


class TargetMirrorUI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self, app):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        self.app = app
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
        cmds.button('target_mirror_run_bt', label=self.ar.data.lang["i054_targetRun"], annotation=self.ar.data.lang["i053_targetRunDesc"], width=290, backgroundColor=(0.6, 1.0, 0.6), command=self.app.run_target_mirror, parent='target_mirror_cl')
        # call targetMirrorUI Window:
        cmds.showWindow('dpTargetMirrorWindow')


    def load_original_model(self, *args):
        """ Load selected object as original model
        """
        selected_nodes = cmds.ls(selection=True)
        if selected_nodes:
            if self.app.check_geometry(selected_nodes[0]):
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
                    if self.app.check_geometry(item):
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
        selected_items = cmds.textScrollList('target_mirror_targets_tsl', query=True, selectItem=True)
        if selected_items:
            for item in selected_items:
                cmds.textScrollList('target_mirror_targets_tsl', edit=True, removeItem=item)
    
    
    def change_rename(self, value, *args):
        """ Enable or disable text fields
        """
        cmds.text('target_mirror_from_txt', edit=True, enable=value)
        cmds.text('target_mirror_to_txt', edit=True, enable=value)
        cmds.textField('target_mirror_from_tf', edit=True, enable=value)
        cmds.textField('target_mirror_to_tf', edit=True, enable=value)
