#import libraries
from maya import cmds
from maya import mel
from functools import partial


class RivetUI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self, app):
        """ This is the main method to load the Rivet UI.
        """
        self.app = app
        # creating dpRivetUI Window:
        self.ar.ui_manager.close_ui('dpRivetWindow')
        width  = 305
        height = 470
        cmds.window('dpRivetWindow', title=self.ar.data.lang["m083_rivet"]+" "+str(self.ar.data.version), widthHeight=(width, height), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        cmds.tabLayout('rivet_main_tl', innerMarginWidth=5, innerMarginHeight=5, parent="dpRivetWindow")
        cmds.columnLayout('rivet_add_cl', columnOffset=("left", 10), parent='rivet_main_tl')
        cmds.text('rivet_load_geo_txt', label=self.ar.data.lang["m145_loadGeo"], height=30, font='boldLabelFont', parent='rivet_add_cl')
        cmds.rowColumnLayout('rivet_geo_rcl', numberOfColumns=2, columnWidth=[(1, 100), (2, 210)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 20)], parent='rivet_add_cl')
        cmds.button('rivet_geo_bt', label=self.ar.data.lang["m146_geo"]+" >", annotation="Load the Geometry here in order to be used to attach.", backgroundColor=(1.0, 0.7, 1.0), width=100, command=self.load_geo_to_attach, parent='rivet_geo_rcl')
        cmds.textField('rivet_geo_to_attach_tf', width=180, text="", changeCommand=partial(self.load_geo_to_attach, None, True), parent='rivet_geo_rcl')
        cmds.rowColumnLayout('rivet_use_set_rcl', numberOfColumns=2, columnWidth=[(1, 110), (2, 210)], columnAlign=[(1, 'right'), (2, 'left')], columnAttach=[(1, 'right', 1), (2, 'left', 10)], parent='rivet_add_cl')
        cmds.text('rivet_uv_set_txt', label="UV Set:", font='obliqueLabelFont', parent='rivet_use_set_rcl')
        cmds.textField('rivet_uv_set_tf', width=180, text="", editable=False, parent='rivet_use_set_rcl')
        cmds.separator(style='in', height=15, width=300, parent='rivet_add_cl')
        cmds.text('rivet_follow_geo_txt', label=self.ar.data.lang["m147_itemsFollowGeo"], height=30, font='boldLabelFont', parent='rivet_add_cl')
        cmds.columnLayout('rivet_items_cl', columnOffset=('left', 10), width=310, parent='rivet_add_cl')
        cmds.textScrollList('rivet_items_tsl', width=290, height=100, allowMultiSelection=True, parent='rivet_items_cl')
        cmds.separator(style='none', height=5, parent='rivet_items_cl')
        cmds.rowColumnLayout('rivet_middle_rcl', numberOfColumns=2, columnWidth=[(1, 150), (2, 150)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 0)], parent='rivet_items_cl')
        cmds.button('rivet_add_bt', label=self.ar.data.lang["i045_add"], annotation=self.ar.data.lang["i045_add"], width=140, command=self.add_selected_item, parent='rivet_middle_rcl')
        cmds.button('rivet_remove_bt', label=self.ar.data.lang["i046_remove"], annotation=self.ar.data.lang["i046_remove"], width=140, command=self.remove_selected_item, parent='rivet_middle_rcl')
        cmds.separator(style='in', height=15, width=300, parent='rivet_add_cl')
        cmds.text('rivet_options_txt', label=self.ar.data.lang["i002_options"]+":", height=30, font='boldLabelFont', parent='rivet_add_cl')
        cmds.columnLayout('rivet_father_cl', columnOffset=("left", 10), parent='rivet_add_cl')
        cmds.checkBox('rivet_attach_t_cb', label=self.ar.data.lang["m148_attach"]+" Translate", value=True, parent='rivet_father_cl')
        cmds.checkBox('rivet_attach_r_cb', label=self.ar.data.lang["m148_attach"]+" Rotate", value=False, parent='rivet_father_cl')
        cmds.checkBox('rivet_father_grp_cb', label=self.ar.data.lang["m149_createGroupConst"], value=True, parent='rivet_father_cl')
        cmds.columnLayout('rivet_invert_cl', columnOffset=("left", 10), parent='rivet_add_cl')
        cmds.checkBox('rivet_add_invert_cb', label=self.ar.data.lang["m150_avoidDoubleTransf"], height=20, value=True, changeCommand=self.change_invert, parent='rivet_invert_cl')
        cmds.rowColumnLayout('rivet_translate_rcl', numberOfColumns=2, columnWidth=[(1, 30), (2, 150)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 5)], height=20, parent='rivet_add_cl')
        cmds.separator(style='none', parent='rivet_translate_rcl')
        cmds.checkBox('rivet_invert_t_cb', label=self.ar.data.lang["m151_invert"]+" Translate", value=True, parent='rivet_translate_rcl')
        cmds.rowColumnLayout('rivet_rotate_rcl', numberOfColumns=2, columnWidth=[(1, 30), (2, 150)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 5)], height=20, parent='rivet_add_cl')
        cmds.separator(style='none', parent='rivet_rotate_rcl')
        cmds.checkBox('rivet_invert_r_cb', label=self.ar.data.lang["m151_invert"]+" Rotate", value=False, parent='rivet_rotate_rcl')
        cmds.columnLayout('rivet_face_to_rivet_cl', columnOffset=("left", 10), parent='rivet_add_cl')
        cmds.checkBox('rivet_face_to_rivet_cb', label=self.ar.data.lang["m226_createFaceToRivet"], height=20, value=True, changeCommand=self.change_deformer, parent='rivet_face_to_rivet_cl')
        cmds.columnLayout('rivet_deformer_cl', columnOffset=("left", 20), parent='rivet_face_to_rivet_cl')
        cmds.radioCollection('rivet_deformer_rc', parent='rivet_deformer_cl')
        cmds.radioButton('rivet_morph_def_rb', label=self.ar.data.lang["m232_morphDeformer"], annotation=self.app.morph_deformer, enable=self.app.maya_required_version, collection='rivet_deformer_rc')
        cmds.radioButton('rivet_wrap_def_rb', label=self.ar.data.lang["m172_wrapDeformer"], annotation=self.app.wrap_deformer, enable=self.app.maya_required_version, collection='rivet_deformer_rc')
        cmds.radioCollection('rivet_deformer_rc', edit=True, select='rivet_morph_def_rb')
        if not self.app.maya_required_version:
            cmds.radioCollection('rivet_deformer_rc', edit=True, select='rivet_wrap_def_rb')
        cmds.separator(style='none', height=15, parent='rivet_add_cl')
        cmds.columnLayout('rivet_create_cl', columnOffset=("left", 10), parent='rivet_add_cl')
        cmds.button('rivet_create_bt', label=self.ar.data.lang["i158_create"]+" "+self.ar.data.lang["m083_rivet"], annotation=self.ar.data.lang["i158_create"]+" "+self.ar.data.lang["m083_rivet"], width=290, backgroundColor=(0.20, 0.7, 1.0), command=self.create_rivet_from_ui, parent='rivet_create_cl')
        # tab layout - remove tab
        cmds.columnLayout('rivet_remove_cl', columnOffset=("left", 10), parent='rivet_main_tl')
        cmds.separator(style='none', height=10, parent='rivet_remove_cl')
        cmds.rowLayout('rivet_remove_rl', numberOfColumns=2, columnAlign=[(1, 'left'), (2, 'right')], parent='rivet_remove_cl')
        cmds.button('rivet_select_all_bt', label=self.ar.data.lang["i314_selectAll"], width=153, command=self.select_ctrl_items, parent='rivet_remove_rl')
        cmds.button('rivet_refresh_bt', label=self.ar.data.lang["m181_refresh"], width=153, command=self.refresh_rivets, parent='rivet_remove_rl')
        cmds.separator(style='none', height=5, parent='rivet_remove_cl')
        cmds.textField("rivet_filter_tf", width=310, changeCommand=self.refresh_rivets, parent='rivet_remove_cl')
        cmds.separator(style='none', height=5, parent='rivet_remove_cl')
        cmds.textScrollList('rivet_filter_controller_tsl', width=310, height=410, allowMultiSelection=True, selectCommand=self.rivet_item_select, parent='rivet_remove_cl')
        cmds.separator(style='none', height=5, parent='rivet_remove_cl')
        cmds.button('rivet_remove_it_bt', label=f"{self.ar.data.lang['i046_remove']} {self.ar.data.lang['m083_rivet']}", width=310, command=self.remove_rivet_from_ui, backgroundColor=(1, .56, 0.48), parent='rivet_remove_cl')
        cmds.tabLayout('rivet_main_tl', edit=True, changeCommand=self.change_tab, tabLabel=(('rivet_add_cl', self.ar.data.lang["i158_create"]), ('rivet_remove_cl', self.ar.data.lang["i046_remove"])))
        # call dpRivetUI Window:
        cmds.showWindow('dpRivetWindow')


    def fill_ui(self):
        """ Try to auto fill UI elements from selection.
        """
        selection = cmds.ls(selection=True)
        if selection:
            if len(selection) > 1:
                items = selection[:-1]
                items.sort()
                geo = selection[-1]
                self.load_geo_to_attach(geo)
                self.add_selected_item(items)


    def select_ctrl_items(self, *args):
        """ Select all items from rivet controllers list.
        """
        items = cmds.textScrollList('rivet_filter_controller_tsl', query=True, allItems=True)
        if items:
            cmds.textScrollList('rivet_filter_controller_tsl', edit=True, selectItem=items)


    def rivet_item_select(self, *args):
        """ Select items on viewport that has been selected on controllers list.
        """
        selection = cmds.textScrollList('rivet_filter_controller_tsl', query=True, selectItem=True)
        cmds.select(selection)


    def remove_rivet_from_list(self, indexes, items):
        """ Receive two lists, the item list has the node with rivet and the index list has the correct index to find the network node.
        """
        self.app.disable_pac(indexes)
        for i, index in enumerate(indexes):
            self.ar.ui_manager.set_progress(self.ar.data.lang['i315_removing'])
            net = self.app.rivet_nets[index]
            if net:
                self.app.remove_rivet_from_net(net)
            else:
                mel.eval('print \"dpAR: '+self.ar.data.lang['m204_unableRemRivet']+items[i]+'\\n\";')
        self.refresh_rivets()
        cmds.select(clear=True)


    def remove_rivet_from_ui(self, *args):
        """ Remove selected rivets on the controllers list in the ui.
        """
        selection = cmds.textScrollList('rivet_filter_controller_tsl', query=True, selectItem=True)
        selection_indexes = cmds.textScrollList('rivet_filter_controller_tsl', query=True, selectIndexedItem=True)
        if selection and selection_indexes:
            true_indexes = list(map(lambda n : n-1, selection_indexes))
            self.ar.ui_manager.set_progress(self.ar.data.lang['i315_removing'], self.ar.data.lang['i315_removing']+" "+self.ar.data.lang['m083_rivet'], len(true_indexes), add_one=False, add_number=False)
            self.remove_rivet_from_list(true_indexes, selection)
            self.app.remove_rivet_grp()
            self.ar.ui_manager.set_progress(end_it=True)
        else:
            mel.eval('print \"dpAR: '+self.ar.data.lang['m169_noItemSelect']+'\\n\";')
        cmds.textScrollList('rivet_filter_controller_tsl', edit=True, deselectAll=True)


    def refresh_rivets(self, *args):
        """ Refresh the rivets list in the ui.
        """
        cmds.textScrollList('rivet_filter_controller_tsl', edit=True, removeAll=True)
        rivet_ctrl_items = self.app.get_ctrl_items()
        filter = cmds.textField('rivet_filter_tf', query=True, text=True)
        if rivet_ctrl_items:
            if filter:
                sorted_rivets = self.app.filter_name(filter, rivet_ctrl_items, " ")
                cmds.textScrollList('rivet_filter_controller_tsl', edit=True, append=sorted_rivets)
            else:
                cmds.textScrollList('rivet_filter_controller_tsl', edit=True, append=rivet_ctrl_items)
    

    def change_tab(self):
        """ Intermediate method to control rivet ui tab change.
        """
        if cmds.tabLayout('rivet_main_tl', query=True, selectTabIndex=True) == 2:
            self.refresh_rivets()
        else:
            self.fill_ui()


    def create_rivet_from_ui(self, *args):
        """ Just collect all information from UI and call the main function to create Rivet setup.
        """
        # getting UI values
        geo_to_attach = cmds.textField('rivet_geo_to_attach_tf', query=True, text=True)
        uv_set = cmds.textField('rivet_uv_set_tf', query=True, text=True)
        items = cmds.textScrollList('rivet_items_tsl', query=True, allItems=True)
        attatch_translate = cmds.checkBox('rivet_attach_t_cb', query=True, value=True)
        attach_rotate = cmds.checkBox('rivet_attach_r_cb', query=True, value=True)
        add_father_grp = cmds.checkBox('rivet_father_grp_cb', query=True, value=True)
        add_invert = cmds.checkBox('rivet_add_invert_cb', query=True, value=True)
        inv_t = cmds.checkBox('rivet_invert_t_cb', query=True, value=True)
        inv_r = cmds.checkBox('rivet_invert_r_cb', query=True, value=True)
        face_to_rivet = cmds.checkBox('rivet_face_to_rivet_cb', query=True, value=True)

        need_to_remove = None
        has_rivets_items = self.app.get_ctrl_items()
        if has_rivets_items:
            has_rivet_set = set(has_rivets_items)
            to_create_set = set(items)
            need_to_remove = to_create_set & has_rivet_set
        if need_to_remove:
            if len(need_to_remove) > 0:
                remove_existing_rivet = cmds.confirmDialog(title=self.ar.data.lang['i074_attention'], icon="warning", message=self.ar.data.lang['i316_rivetNotFine'], button=[self.ar.data.lang['i071_yes'], self.ar.data.lang['i072_no'], self.ar.data.lang['i132_cancel']], defaultButton=self.ar.data.lang['i071_yes'], cancelButton=self.ar.data.lang['i132_cancel'], dismissString=self.ar.data.lang['i132_cancel'])
                if remove_existing_rivet == self.ar.data.lang['i071_yes']:
                    need_to_remove_items, true_indexes = self.get_to_remove_indexes(need_to_remove, has_rivets_items)
                    self.ar.ui_manager.set_progress(self.ar.data.lang['i315_removing'], self.ar.data.lang['i315_removing']+" "+self.ar.data.lang['m083_rivet'], len(need_to_remove_items), add_one=False, add_number=False)
                    self.remove_rivet_from_list(true_indexes, need_to_remove_items)
                    self.ar.ui_manager.set_progress(end_it=True)
                elif remove_existing_rivet == self.ar.data.lang['i072_no']:
                    pass
                else:
                    return

        # call run function to create Rivet setup using UI values
        self.ar.ui_manager.set_progress(self.ar.data.lang['i318_working'], self.ar.data.lang['i317_creatingRivet'], len(items), add_one=False, add_number=False)
        self.app.create_rivet(geo_to_attach, uv_set, items, attatch_translate, attach_rotate, add_father_grp, add_invert, inv_t, inv_r, face_to_rivet, self.app.rivet_grp_name, True)
        self.ar.ui_manager.set_progress(end_it=True)
        self.ar.ui_manager.close_ui('dpRivetWindow')


    def select_uv_set_dialog(self, uv_sets, *args):
        """ Ask user the UV Set to use.
        """
        self.app.selected_uv_set = cmds.confirmDialog(title="Multiple UV Sets", message="Which UV Set do you want to use?", button=uv_sets)


    def load_uv_set(self, item, *args):
        """ Verify the UV sets for polygon mesh and show a dialog box in order to choose if there are more than one UVSet map.
        """
        if self.app.item_type == "mesh":
            uv_sets = cmds.polyUVSet(self.geo_to_attach, query=True, allUVSets=True)
            self.app.selected_uv_set = uv_sets[0]
            if len(uv_sets) > 1:
                self.select_uv_set_dialog(uv_sets)
            cmds.textField('rivet_uv_set_tf', edit=True, text=self.app.selected_uv_set)
        elif self.app.item_type == "nurbsSurface":
            cmds.textField('rivet_uv_set_tf', edit=True, text="nurbsSurface")
    
    
    def load_geo_to_attach(self, geo_name=None, geo_from_ui=None, *args):
        """ Load selected object a geometry to attach rivet.
        """
        if geo_name:
            selected_nodes = [geo_name]
        elif geo_from_ui:
            selected_nodes = [cmds.textField('rivet_geo_to_attach_tf', query=True, text=True)]
        else:
            selected_nodes = cmds.ls(selection=True)
        if selected_nodes:
            if self.ar.utils.check_geometry(selected_nodes[0]):
                self.app.geo_to_attach = selected_nodes[0]
                cmds.textField('rivet_geo_to_attach_tf', edit=True, text=self.app.geo_to_attach)
                self.load_uv_set(self.app.geo_to_attach)
        else:
            mel.eval("warning \"Select a geometry in order use it to attach rivets, please.\";")
    
    
    def add_selected_item(self, items=None, *args):
        """ Add selected items to target textscroll list
        """
        # declare variables
        selected_items = []
        # get selection
        if items:
            selection=items
        else:
            selection = cmds.ls(selection=True)
        # check if there is any selected object in order to continue
        if selection:
            # find transforms
            for item in selection:
                if not item in selected_items:
                    if cmds.objectType(item) == "transform":
                        if not item == self.app.geo_to_attach:
                            selected_items.append(item)
                    elif ".vtx" in item or ".cv" in item or ".pt" in item:
                        selected_items.append(item)
            if selected_items:
                # get current list
                current_items = cmds.textScrollList('rivet_items_tsl', query=True, allItems=True)
                if current_items:
                    # clear current list
                    cmds.textScrollList('rivet_items_tsl', edit=True, removeAll=True)
                    # avoid repeated items
                    for item in selected_items:
                        if not item in current_items:
                            current_items.append(item)
                    # refresh textScrollList
                    cmds.textScrollList('rivet_items_tsl', edit=True, append=current_items)
                else:
                    # add selected items in the empyt target scroll list
                    cmds.textScrollList('rivet_items_tsl', edit=True, append=selected_items)
            else:
                mel.eval("warning \"Please, select a tranform node, vertices or lattice points in order to add it in the item list.\";")
        else:
            mel.eval("warning \"Please, select a tranform node, vertices or lattice points in order to add it in the item list.\";")
    
    
    def remove_selected_item(self, *args):
        """ Remove selected items from target scroll list.
        """
        selected_items = cmds.textScrollList('rivet_items_tsl', query=True, selectItem=True)
        if selected_items:
            for item in selected_items:
                cmds.textScrollList('rivet_items_tsl', edit=True, removeItem=item)
      
    
    def change_invert(self, value, *args):
        cmds.checkBox('rivet_invert_t_cb', edit=True, enable=value)
        cmds.checkBox('rivet_invert_r_cb', edit=True, enable=value)


    def change_deformer(self, value, *args):
        if not self.app.maya_required_version:
            value = False
        cmds.radioButton('rivet_morph_def_rb', edit=True, enable=value)
        cmds.radioButton('rivet_wrap_def_rb', edit=True, enable=value)
