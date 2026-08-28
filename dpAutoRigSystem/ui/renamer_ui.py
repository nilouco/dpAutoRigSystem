#import libraries
from maya import cmds
from functools import partial


class RenamerUI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self, app):
        """ This is the main method to load the Renamer UI.
        """
        self.app = app
        self.ar.utils.close_ui('dpRenamerWin')
        # UI:
        width = 530
        height = 280
        cmds.window('dpRenamerWin', title=self.ar.data.lang['m214_renamer']+' - v'+str(self.ar.data.version), width=width, height=height, sizeable=False, minimizeButton=False, maximizeButton=False)
        # UI elements:
        cmds.rowColumnLayout('renamer_main_rcl', numberOfColumns=2, columnWidth=[(1, 200), (2, 200)], columnSpacing=[(1, 10), (2, 10)])
        # fields
        cmds.columnLayout('renamer_fields_cl', adjustableColumn=True, width=150, parent='renamer_main_rcl')
        cmds.radioButtonGrp('renamer_select_rbg', labelArray2=[self.ar.data.lang["i266_selected"], self.ar.data.lang["m216_hierarchy"]], numberOfRadioButtons=2, select=self.app.sel_option, changeCommand=self.change_sel_option, parent='renamer_fields_cl')
        cmds.separator(style="in", height=20, parent='renamer_fields_cl')
        cmds.checkBox('renamer_sequence_cb', label=self.ar.data.lang['m220_sequence'], changeCommand=self.change_sequence, value=False, parent='renamer_fields_cl')
        cmds.textFieldGrp('renamer_sequence_tfg', label=self.ar.data.lang['m222_name'], textChangedCommand=self.change_name, columnAlign=[(1, "right"), (2, "right")], columnWidth=[(1, 30), (2, 100)], adjustableColumn2=True, parent='renamer_fields_cl')
        cmds.intFieldGrp('renamer_start_ifg', label=self.ar.data.lang['c110_start'], changeCommand=self.refresh_preview, value1=self.app.start, columnAlign=[(1, "right"), (2, "right")], columnWidth=[(1, 30), (2, 100)], adjustableColumn2=True, parent='renamer_fields_cl')
        cmds.intFieldGrp('renamer_padding_ifg', label=self.ar.data.lang['m221_padding'], changeCommand=self.refresh_preview, value1=self.app.padding, columnAlign=[(1, "right"), (2, "right")], columnWidth=[(1, 30), (2, 100)], adjustableColumn2=True, parent='renamer_fields_cl')
        cmds.separator(style="in", height=20, parent='renamer_fields_cl')
        cmds.rowColumnLayout('renamer_pre_pos_rc', numberOfColumns=2, columnWidth=[(1, 90), (2, 97)], columnSpacing=[(2, 5)], parent='renamer_fields_cl')
        cmds.checkBox('renamer_prefix_cb', label=self.ar.data.lang['i144_prefix'], changeCommand=self.refresh_preview, value=False, parent='renamer_pre_pos_rc')
        cmds.checkBox('renamer_suffix_cb', label=self.ar.data.lang['m217_suffix'], changeCommand=self.refresh_preview, value=False, parent='renamer_pre_pos_rc')
        cmds.textField('renamer_prefix_tf', textChangedCommand=self.change_prefix, parent='renamer_pre_pos_rc')
        cmds.textField('renamer_suffix_tf', textChangedCommand=self.change_suffix, parent='renamer_pre_pos_rc')
        cmds.separator(style="in", height=20, parent='renamer_fields_cl')
        cmds.checkBox('renamer_search_replace_cb', label=self.ar.data.lang['m218_search']+" - "+self.ar.data.lang['m219_replace'], changeCommand=self.change_search_replace, value=False, parent='renamer_fields_cl')
        cmds.textFieldGrp('renamer_search_tfg', label=self.ar.data.lang['i036_from'], textChangedCommand=self.change_search, columnAlign=[(1, "right"), (2, "right")], columnWidth=[(1, 30), (2, 136)], adjustableColumn2=True, parent='renamer_fields_cl')
        cmds.textFieldGrp('renamer_replace_tfg', label=self.ar.data.lang['i037_to'], textChangedCommand=self.change_search, columnAlign=[(1, "right"), (2, "right")], columnWidth=[(1, 30), (2, 136)], adjustableColumn2=True, parent='renamer_fields_cl')
        # loaded items
        cmds.columnLayout('renamer_items_cl', adjustableColumn=True, width=300, parent='renamer_main_rcl')
        cmds.text(label=self.ar.data.lang['m223_preview'], align="center", height=20, font="boldLabelFont", parent='renamer_items_cl')
        cmds.rowColumnLayout('renamer_items_scrolls_rcl', numberOfColumns=2, columnWidth=[(1, 140), (2, 140)], columnSpacing=[(1, 5), (2, 5)], columnAlign=[(1, "center"), (2, "center")], rowSpacing=[(1, 5), (2, 5)], parent='renamer_items_cl')
        cmds.text('renamer_current_txt', label=self.ar.data.lang['i276_current'], parent='renamer_items_scrolls_rcl')
        cmds.text('renamer_preview_txt', label=self.ar.data.lang['m224_rename']+" "+self.ar.data.lang['i037_to'], parent='renamer_items_scrolls_rcl')
        cmds.textScrollList('renamer_original_sl', width=130, height=193, enable=True, parent='renamer_items_scrolls_rcl')
        cmds.textScrollList('renamer_preview_sl', width=130, height=193, enable=True, parent='renamer_items_scrolls_rcl')
        # footer
        cmds.columnLayout('renamer_footer_cl', adjustableColumn=True, width=100, parent='renamer_items_cl')
        cmds.separator(style="none", height=5, parent='renamer_footer_cl')
        cmds.button('renamer_run_renamer_bt', label=self.ar.data.lang['m224_rename'], command=self.app.run_renamer_by_ui, parent='renamer_footer_cl')
        # calling UI:
        cmds.showWindow('dpRenamerWin')


    def edit_sequence_fields(self, value):
        """
        """
        cmds.textFieldGrp('renamer_sequence_tfg', edit=True, enable=value)
        cmds.intFieldGrp('renamer_start_ifg', edit=True, enable=value)
        cmds.intFieldGrp('renamer_padding_ifg', edit=True, enable=value)   


    def edit_search_replace_fields(self, value):
        """
        """
        cmds.textFieldGrp('renamer_search_tfg', edit=True, enable=value)
        cmds.textFieldGrp('renamer_replace_tfg', edit=True, enable=value)


    def change_sequence(self, value, *args):
        """ Active or desactive the search and replace field because it doesn't work well with sequence field.
        """
        if value:
            cmds.checkBox('renamer_search_replace_cb', edit=True, value=False)
            self.edit_search_replace_fields(False)
            self.edit_sequence_fields(True)
        else:
            self.edit_search_replace_fields(True)
        self.refresh_preview()


    def change_search_replace(self, value, *args):
        """ Active or desactive the sequence field because it doesn't work well with search and replace field.
        """
        if value:
            cmds.checkBox('renamer_sequence_cb', edit=True, value=False)
            self.edit_sequence_fields(False)
            self.edit_search_replace_fields(True)
        else:
            self.edit_sequence_fields(True)
        self.refresh_preview()


    def change_name(self, value, *args):
        """ Set sequence checkbox on or off.
        """
        if value == "":
            cmds.checkBox('renamer_sequence_cb', edit=True, value=False)
            self.edit_search_replace_fields(True)
        else:
            cmds.checkBox('renamer_sequence_cb', edit=True, value=True)
            cmds.checkBox('renamer_search_replace_cb', edit=True, value=False)
            self.edit_search_replace_fields(False)
        self.refresh_preview()


    def change_prefix(self, value, *args):
        """ Set prefix checkbox on or off.
        """
        if value == "":
            cmds.checkBox('renamer_prefix_cb', edit=True, value=False)
        else:
            cmds.checkBox('renamer_prefix_cb', edit=True, value=True)
        self.refresh_preview()


    def change_suffix(self, value, *args):
        """ Set suffix checkbox on or off.
        """
        if value == "":
            cmds.checkBox('renamer_suffix_cb', edit=True, value=False)
        else:
            cmds.checkBox('renamer_suffix_cb', edit=True, value=True)
        self.refresh_preview()


    def change_search(self, value, *args):
        """ Set search checkbox on or off.
        """
        if value == "":
            if cmds.textFieldGrp('renamer_search_tfg', query=True, text=True) == "":
                cmds.checkBox('renamer_search_replace_cb', edit=True, value=False)
                self.edit_sequence_fields(True)
        else:
            cmds.checkBox('renamer_search_replace_cb', edit=True, value=True)
            self.edit_sequence_fields(False)
        self.refresh_preview()


    def change_sel_option(self, *args):
        """ Read the current UI selected radio button option.
            Update self.sel_option queried value.
            Return the current value
        """
        self.app.sel_option = cmds.radioButtonGrp('renamer_select_rbg', query=True, select=True)
        self.refresh_preview()
        return self.app.sel_option

    
    def refresh_original(self):
        """ Refresh the original selected item list and update the UI textScrollList.
        """
        self.app.get_originals()
        if self.app.originals:
            cmds.textScrollList('renamer_original_sl', edit=True, removeAll=True)
            cmds.textScrollList('renamer_original_sl', edit=True, append=self.app.originals)


    def refresh_preview(self, *args):
        """ Reload the preview naming list and populate its UI textScrollList.
        """
        self.refresh_original()
        self.app.generate_previews()
        if self.app.previews:
            cmds.textScrollList('renamer_preview_sl', edit=True, removeAll=True)
            cmds.textScrollList('renamer_preview_sl', edit=True, append=self.app.previews)
    

    def get_info_from_ui(self):
        """ Just load the member variables with info from UI.
        """
        # checkBoxes
        self.app.add_sequence = cmds.checkBox('renamer_sequence_cb', query=True, value=True)
        self.app.add_prefix = cmds.checkBox('renamer_prefix_cb', query=True, value=True)
        self.app.add_suffix = cmds.checkBox('renamer_suffix_cb', query=True, value=True)
        self.app.search_replace = cmds.checkBox('renamer_search_replace_cb', query=True, value=True)
        # textFields
        self.app.sequence_name = cmds.textFieldGrp('renamer_sequence_tfg', query=True, text=True)
        self.app.prefix_name = cmds.textField('renamer_prefix_tf', query=True, text=True)
        self.app.suffix_name = cmds.textField('renamer_suffix_tf', query=True, text=True)
        self.app.search_name = cmds.textFieldGrp('renamer_search_tfg', query=True, text=True)
        self.app.replace_name = cmds.textFieldGrp('renamer_replace_tfg', query=True, text=True)
        # intFields
        self.app.start = cmds.intFieldGrp('renamer_start_ifg', query=True, value1=True)
        self.app.padding = cmds.intFieldGrp('renamer_padding_ifg', query=True, value1=True)

    
    def reset_ui(self):
        """ Just back UI to default initial values.
        """
        if self.ar.data.ui_state:
            cmds.radioButtonGrp('renamer_select_rbg', edit=True, select=1)
            # checkBoxes
            cmds.checkBox('renamer_sequence_cb', edit=True, value=False)
            cmds.checkBox('renamer_prefix_cb', edit=True, value=False)
            cmds.checkBox('renamer_suffix_cb', edit=True, value=False)
            cmds.checkBox('renamer_search_replace_cb', edit=True, value=False)
            # textFields
            cmds.textFieldGrp('renamer_sequence_tfg', edit=True, text="")
            cmds.textField('renamer_prefix_tf', edit=True, text="")
            cmds.textField('renamer_suffix_tf', edit=True, text="")
            cmds.textFieldGrp('renamer_search_tfg', edit=True, text="")
            cmds.textFieldGrp('renamer_replace_tfg', edit=True, text="")
            # intFields
            cmds.intFieldGrp('renamer_start_ifg', edit=True, value1=self.app.start)
            cmds.intFieldGrp('renamer_padding_ifg', edit=True, value1=self.app.padding)