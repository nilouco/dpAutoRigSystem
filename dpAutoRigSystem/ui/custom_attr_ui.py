#import libraries
from maya import cmds
from functools import partial


class CustomAttrUI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self, app):
        """ This is the main method to load the Custom Attr UI.
        """
        self.app = app
        self.ar.ui_manager.close_ui('dpCustomAttributesWindow')
        self.ar.ui_manager.close_ui('dpAddCustomAttributesWindow')
        self.ar.ui_manager.close_ui('dpRemoveCustomAttributesWindow')
        self.ar.ui_manager.close_ui('dpIDCustomAttributesWindow')
        self.get_item_filter()
        # window
        width  = 380
        height = 350
        cmds.window("dpCustomAttributesWindow", title=self.ar.data.lang['m212_customAttr']+" "+str(self.ar.data.version), widthHeight=(width, height), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        # create UI layout and elements:
        cmds.columnLayout('custom_attr_cl', adjustableColumn=True, columnOffset=("both", 10))
        cmds.columnLayout('custom_attr_main_cl', adjustableColumn=True, columnOffset=("both", 10), parent='custom_attr_cl')
        cmds.text('custom_attr_header_txt', label=self.ar.data.lang['i267_customAttrHeader']+' "'+self.app.start_attr+'"', align="left", height=30, font='boldLabelFont', parent='custom_attr_main_cl')
        # filter
        cmds.columnLayout('custom_attr_filter_cl', adjustableColumn=True, parent='custom_attr_main_cl')
        cmds.textFieldButtonGrp('custom_attr_item_filter_tfbg', label=self.ar.data.lang['i268_filterByName'], text="", buttonLabel=self.ar.data.lang['m004_select']+" "+self.ar.data.lang['i211_all'], buttonCommand=self.app.select_nodes, changeCommand=self.filter_by_name, adjustableColumn=2, parent='custom_attr_filter_cl')
        cmds.separator(style='none', height=5, parent='custom_attr_filter_cl')
        # items and attributes layout
        cmds.paneLayout('custom_attr_table_pl', parent='custom_attr_main_cl')
        cmds.spreadSheetEditor('custom_attr_main_sse', mainListConnection=self.item_sc, filter=self.item_f, attrRegExp=self.app.start_attr, niceNames=False, keyableOnly=False, parent='custom_attr_table_pl')
        # bottom layout for buttons
        cmds.separator(style='none', height=10, parent='custom_attr_main_cl')
        cmds.rowColumnLayout('custom_attr_buttons_rcl', numberOfColumns=4, columnWidth=[(1, 80), (2, 80), (3, 120), (4, 100)], columnOffset=[(1, "both", 5), (2, "both", 5), (3, "both", 5), (4, "both", 5)], parent='custom_attr_main_cl')
        cmds.button('custom_attr_add_bt', label=self.ar.data.lang['i063_skinAddBtn'], backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.add_attr_ui, parent='custom_attr_buttons_rcl')
        cmds.button('custom_attr_remove_bt', label=self.ar.data.lang['i064_skinRemBtn'], backgroundColor=(0.4, 0.4, 0.4), width=70, command=self.remove_attr_ui, parent='custom_attr_buttons_rcl')
        cmds.button('custom_attr_update_id_bt', label=self.ar.data.lang['i089_update']+" "+self.app.dpid_attr, backgroundColor=(0.5, 0.5, 0.5), width=100, command=self.app.update_id, parent='custom_attr_buttons_rcl')
        cmds.button('custom_attr_reveal_id_bt', label=self.ar.data.lang['i340_reveal']+" "+self.app.dpid_attr, backgroundColor=(0.5, 0.5, 0.5), width=100, command=partial(self.app.reveal_id, None, True), parent='custom_attr_buttons_rcl')
        cmds.separator(style='none', height=15, parent='custom_attr_main_cl')
        # settings - frameLayout:
        cmds.frameLayout('custom_attr_settings_fl', label=self.ar.data.lang['i215_setAttr'], collapsable=True, collapse=True, parent='custom_attr_main_cl')
        cmds.columnLayout('custom_attr_settings_cl', adjustableColumn=True, columnOffset=('left', 5), parent='custom_attr_settings_fl')
        # type
        cmds.text('custom_attr_type_txt', align='left', label=self.ar.data.lang['i138_type'], height=30, font='boldLabelFont', parent='custom_attr_settings_cl')
        cmds.checkBox('custom_attr_type_all_cb', label=self.ar.data.lang['i339_any'].capitalize(), align='left', value=0, changeCommand=partial(self.update_type, "any"), parent='custom_attr_settings_cl')
        cmds.checkBox('custom_attr_type_transform_cb', label="transform", align='left', value=1, changeCommand=partial(self.update_type, "transform"), parent='custom_attr_settings_cl')
        cmds.checkBox('custom_attr_type_network_cb', label="network", align='left', value=1, changeCommand=partial(self.update_type, "network"), parent='custom_attr_settings_cl')
        cmds.separator(style='in', height=15, parent='custom_attr_settings_cl')
        # display
        cmds.text('custom_attr_display_txt', align='left', label=self.ar.data.lang['m217_suffix']+" "+self.ar.data.lang['c126_display'], height=30, font='boldLabelFont', parent='custom_attr_settings_cl')
        cmds.rowColumnLayout('custom_attr_display_rcl', numberOfColumns=6, columnWidth=[(1, 70), (2, 70), (3, 70), (4, 70), (5, 70), (6, 70)], columnAlign=[(1, 'left'), (2, 'left'), (3, 'left'), (4, 'left'), (5, 'left'), (6, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 10), (3, 'left', 10), (4, 'left', 10), (5, 'left', 10), (6, 'left', 10)], parent='custom_attr_settings_cl')
        cmds.checkBox('custom_attr_display_grp_cb', label="Grp", annotation="Group", align='left', value=1, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_ctrl_cb', label="Ctrl", annotation="Controller", align='left', value=1, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_jnt_cb', label="Jnt", annotation="Skinned joint", align='left', value=1, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_pac_cb', label="PaC", annotation="Parent constraint", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_poc_cb', label="PoC", annotation="Point constraint", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_orc_cb', label="OrC", annotation="Orient constraint", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_scc_cb', label="ScC", annotation="Scale constraint", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_aic_cb', label="AiC", annotation="Aim constraint", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_pvc_cb', label="PVC", annotation="Pole Vector Constraint", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_jxt_cb', label="Jxt", annotation="Extra joint", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_jar_cb', label="Jar", annotation="Ariticulation joint", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_jad_cb', label="Jad", annotation="Additional joint", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_jcr_cb', label="Jcr", annotation="Corrective joint", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_jis_cb', label="Jis", annotation="Indirect skinning joint", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_jax_cb', label="Jax", annotation="Extra articulation joint", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_jzt_cb', label="Jzt", annotation="Zero out joint", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_jend_cb', label="JEnd", annotation="End joint", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_eff_cb', label="Eff", annotation="Effector", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_ikh_cb', label="IkH", annotation="Ik Handle", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.checkBox('custom_attr_display_handle_cb', label="Handle", annotation="Deformer Handle", align='left', value=0, changeCommand=self.update_name_display, parent='custom_attr_display_rcl')
        cmds.separator(style='none', height=15, parent='custom_attr_main_cl')
        # storing checkBoxes lists
        self.type_cbs = ['custom_attr_type_transform_cb', 'custom_attr_type_network_cb']
        self.display_cbs = ['custom_attr_display_grp_cb', 'custom_attr_display_ctrl_cb', 'custom_attr_display_jnt_cb', 'custom_attr_display_pac_cb', 'custom_attr_display_poc_cb', 'custom_attr_display_orc_cb', 'custom_attr_display_scc_cb', 'custom_attr_display_aic_cb', 'custom_attr_display_pvc_cb', 'custom_attr_display_jxt_cb', 'custom_attr_display_jar_cb', 'custom_attr_display_jad_cb', 'custom_attr_display_jcr_cb', 'custom_attr_display_jis_cb', 'custom_attr_display_jax_cb', 'custom_attr_display_jzt_cb', 'custom_attr_display_jend_cb', 'custom_attr_display_eff_cb', 'custom_attr_display_ikh_cb', 'custom_attr_display_handle_cb']
        # call window
        cmds.showWindow("dpCustomAttributesWindow")
        self.update_name_display()


    def update_ui(self):
        self.get_item_filter()
        cmds.spreadSheetEditor('custom_attr_main_sse', edit=True, mainListConnection=self.item_sc, filter=self.item_f, attrRegExp=self.app.start_attr, niceNames=False, keyableOnly=False)


    def update_name_display(self, *args):
        """ Update item filter name display argument.
        """
        self.app.do_not_display_suffixes = []
        for cb in self.display_cbs:
            suffix = cmds.checkBox(cb, query=True, label=True)
            if not cmds.checkBox(cb, query=True, value=True):
                self.app.do_not_display_suffixes.append(suffix)
            elif suffix in self.app.do_not_display_suffixes:
                self.app.do_not_display_suffixes.remove(suffix)
        self.update_ui()


    def get_item_filter(self):
        """ Create a selection filter by node type excluding the ignore_it list.
        """
        self.item_sc = cmds.selectionConnection(activeList=True)
        self.item_f = cmds.itemFilter(byType=self.app.types)
        for ignore_it in self.app.ignores:
            self.item_f = cmds.itemFilter(difference=(self.item_f, cmds.itemFilter(byName=ignore_it)))
        for suffix in self.app.do_not_display_suffixes:
            self.item_f = cmds.itemFilter(difference=(self.item_f, cmds.itemFilter(byName="*"+suffix)))


    def filter_by_name(self, filter_name=None, *args):
        """ Sort items by name filter.
        """
        if not filter_name:
            filter_name = cmds.textFieldButtonGrp('custom_attr_item_filter_tfbg', query=True, text=True)
        if filter_name:
            current_items = cmds.selectionConnection(self.item_sc, query=True, object=True)
            if current_items:
                filtered_items = self.ar.naming.filter_name(filter_name, current_items, " ")
                filtered_items = list(set(filtered_items) - set(self.app.ignores))
                filtered_items.sort()
                cmds.selectionConnection(self.item_sc, edit=True, clear=True)
                for item in filtered_items:
                    cmds.selectionConnection(self.item_sc, edit=True, select=item)
        cmds.textFieldButtonGrp('custom_attr_item_filter_tfbg', edit=True, text="")


    def add_attr_ui(self, *args):
        """ Create a window with buttons to add new attributes.
        """
        self.ar.ui_manager.close_ui('dpAddCustomAttributesWindow')
        widht  = 220
        height = 260
        cmds.window('dpAddCustomAttributesWindow', title=self.ar.data.lang['m212_customAttr']+" "+str(self.ar.data.version), widthHeight=(widht, height), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.columnLayout('custom_attr_add_cl', adjustableColumn=True, columnOffset=("both", 10))
        cmds.text('custom_attr_add_header_txt', label=self.ar.data.lang['i045_add']+" "+self.ar.data.lang['m212_customAttr'], align="left", height=30, font='boldLabelFont', parent='custom_attr_add_cl')
        cmds.separator(style='none', height=10, parent='custom_attr_add_cl')
        for a, attr in enumerate(self.app.attributes):
            cmds.button("custom_attr_add_"+str(a)+"_bt", label=attr, backgroundColor=(0.6, 0.6, 0.6), command=partial(self.app.add_attr, a), parent='custom_attr_add_cl')
            cmds.separator(style='none', height=5, parent='custom_attr_add_cl')
        cmds.separator(style='in', height=10, parent='custom_attr_add_cl')
        cmds.text("custom_attr_add_txt", label=self.ar.data.lang['m212_customAttr']+":", align="left", height=30, parent='custom_attr_add_cl')
        cmds.textFieldButtonGrp('custom_attr_add_tfbg', label="", text="", buttonLabel=self.ar.data.lang['i045_add'], buttonCommand=partial(self.app.add_attr, "custom"), adjustableColumn=2, columnWidth=[(1, 0), (2, 50), (3, 30)], parent='custom_attr_add_cl')
        cmds.showWindow('dpAddCustomAttributesWindow')


    def id_ui(self, id_data):
        """ Create a window with exposed dpID attributes.
        """
        if id_data:
            self.ar.ui_manager.close_ui('dpIDCustomAttributesWindow')
            width  = 780
            height = 350
            cmds.window('dpIDCustomAttributesWindow', title=self.ar.data.lang['m212_customAttr']+" "+str(self.ar.data.version), widthHeight=(width, height), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
            cmds.columnLayout('custom_attr_id_cl', adjustableColumn=True, columnOffset=("both", 10))
            cmds.text('custom_attr_id_header_txt', label=self.app.dpid_attr+" "+self.ar.data.lang['m212_customAttr'], align="left", height=30, font='boldLabelFont', parent='custom_attr_id_cl')
            cmds.separator(style='none', height=10, parent='custom_attr_id_cl')
            cmds.rowLayout('custom_attr_id_refresh_rl', numberOfColumns=2, width=400, columnWidth2=(200, 200), adjustableColumn=2, columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 10), (2, 'both', 10)], parent='custom_attr_id_cl')
            cmds.button('custom_attr_id_bt', label=self.ar.data.lang['m181_refresh'], width=80, command=self.populate_id_ui, backgroundColor=(0.5, 0.5, 0.5), parent='custom_attr_id_refresh_rl')
            cmds.separator(style='in', height=30, parent='custom_attr_id_cl')
            cmds.scrollLayout('custom_attr_id_sl', width=300, parent='custom_attr_id_cl')
            self.populate_id_ui(id_data)
            cmds.separator(style='none', height=30, parent='custom_attr_id_sl')
            cmds.showWindow('dpIDCustomAttributesWindow')


    def populate_id_ui(self, id_data, *args):
        """ Fill UI with nodes of decomposed dpID info.
        """
        if not id_data:
            id_data = self.app.reveal_id()
        if id_data:
            cmds.deleteUI('custom_attr_id_sl')
            cmds.scrollLayout('custom_attr_id_sl', width=300, parent='custom_attr_id_cl')
            for node in list(id_data.keys()):
                # layout
                cmds.rowColumnLayout('custom_attr_id_'+node+'_rl', numberOfColumns=3, adjustableColumn=3, columnWidth=[(1, 200), (2, 80), (3, 500)], columnAlign=[(1, 'center'), (2, 'right'), (3, 'left')], columnAttach=[(1, 'both', 10), (2, 'both', 10), (3, 'both', 10)], parent='custom_attr_id_sl')
                # button
                if node == id_data[node]["name"]:
                    cmds.button('custom_attr_id_select_'+node+'_bt', label=node, command=partial(self.ar.ctrls.select_controller, node, False), parent='custom_attr_id_'+node+'_rl')
                else: #supposed renamed node
                    cmds.button('custom_attr_id_select_'+node+'_bt', label=node, command=partial(self.ar.ctrls.select_controller, node, False), backgroundColor=(0.8, 0.5, 0.5), parent='custom_attr_id_'+node+'_rl')
                # data
                cmds.text('custom_attr_id_attr_'+node+'_txt', label=self.app.dpid_attr, parent='custom_attr_id_'+node+'_rl')
                cmds.text('custom_attr_id_id_'+node+'_txt', label=id_data[node][self.app.dpid_attr], parent='custom_attr_id_'+node+'_rl')
                cmds.text(label="", parent='custom_attr_id_'+node+'_rl')
                cmds.text('custom_attr_id_name_'+node+'_txt', label=self.ar.data.lang['m006_name'], parent='custom_attr_id_'+node+'_rl')
                cmds.text('custom_attr_id_node_'+node+'_txt', label=id_data[node]["name"], parent='custom_attr_id_'+node+'_rl')
                cmds.text(label="", parent='custom_attr_id_'+node+'_rl')
                cmds.text('custom_attr_id_date_'+node+'_txt', label=self.ar.data.lang['i341_date'], parent='custom_attr_id_'+node+'_rl')
                cmds.text('custom_attr_id_node_date_'+node+'_txt', label=id_data[node]["date"], parent='custom_attr_id_'+node+'_rl')
                cmds.separator(style='none', height=5, parent='custom_attr_id_sl')
            cmds.separator(style='none', height=10, parent='custom_attr_id_sl')


    def remove_attr_ui(self, *args):
        """ Create a window showing the current dp custom attributes to delete them.
        """
        self.ar.ui_manager.close_ui('dpRemoveCustomAttributesWindow')
        widht  = 200
        height = 250
        cmds.window('dpRemoveCustomAttributesWindow', title=self.ar.data.lang['m212_customAttr']+" "+str(self.ar.data.version), widthHeight=(widht, height), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.columnLayout('custom_attr_remove_cl', adjustableColumn=True, columnOffset=("both", 10))
        cmds.text('custom_attr_remove_header_txt', label=self.ar.data.lang['i046_remove']+" "+self.ar.data.lang['m212_customAttr'], align="left", height=30, font='boldLabelFont', parent='custom_attr_remove_cl')
        cmds.separator(style='none', height=10, parent='custom_attr_remove_cl')
        to_remove_attrs = self.app.get_custom_attrs()
        if to_remove_attrs:
            to_remove_attrs = list(set(to_remove_attrs))
            to_remove_attrs.sort()
            for rem_attr in to_remove_attrs:
                cmds.button("custom_attr_remove_"+rem_attr+"_bt", label=rem_attr, backgroundColor=(0.6, 0.6, 0.6), command=partial(self.app.remove_attr, rem_attr), parent='custom_attr_remove_cl')
                cmds.separator(style='none', height=5, parent='custom_attr_remove_cl')
        else:
            cmds.text("custom_attr_not_found_txt", label=self.ar.data.lang['i062_notFound']+" "+self.ar.data.lang['m212_customAttr'])
        cmds.showWindow('dpRemoveCustomAttributesWindow')


    def update_type(self, type_name, value, *args):
        """ Change node type to display in the UI.
        """
        if type_name == "any":
            if value:
                confirm = cmds.confirmDialog(title=self.ar.data.lang["m212_customAttr"], icon="question", message=self.ar.data.lang['m098_confirmSelectAny'], button=[self.ar.data.lang['i071_yes'], self.ar.data.lang['i072_no']], defaultButton=self.ar.data.lang['i072_no'], cancelButton=self.ar.data.lang['i072_no'], dismissString=self.ar.data.lang['i072_no'])
                if confirm == self.ar.data.lang['i071_yes']:
                    self.types = []
                    for cb_item in self.type_cbs:
                        cmds.checkBox(cb_item, edit=True, value=1, enable=0)
            else:
                self.types = self.original_types.copy()
                for cb_item in self.type_cbs:
                    cmds.checkBox(cb_item, edit=True, value=1, enable=1)
        else:
            if value and not type_name in self.types:
                self.types.append(type_name)
            elif type_name in self.types:
                self.types.remove(type_name)
        self.update_ui()
