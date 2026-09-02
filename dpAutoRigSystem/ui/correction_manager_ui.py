#import libraries
from maya import cmds
from functools import partial


class CorrectionManagerUI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self, app):
        """ This is the main method to load the Correction Manager UI.
        """
        self.app = app
        self.ar.utils.close_ui("dpCorrectionManagerWindow")
        # window
        width = 380
        height = 300
        cmds.window('dpCorrectionManagerWindow', title=self.ar.data.lang['m068_correctionManager']+" "+str(self.ar.data.version), widthHeight=(width, height), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpCorrectionManagerWindow')
        # create UI layout and elements:
        cmds.columnLayout('correction_cl', adjustableColumn=True, columnOffset=("both", 10))
        cmds.text('correction_header_txt', label=self.ar.data.lang['m066_selectTwo'], align="left", height=30, font='boldLabelFont', parent='correction_cl')
        cmds.rowColumnLayout('correction_rcl', numberOfColumns=2, columnWidth=[(1, 100), (2, 280)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 10), (2, 'both', 10)], parent='correction_cl')
        cmds.button('correction_create_bt', label=self.ar.data.lang['i158_create'], command=partial(self.app.create_correction_manager_setup, from_ui=True), backgroundColor=(0.7, 1.0, 0.7), parent='correction_rcl')
        cmds.textField('correction_create_tf', editable=True, parent='correction_rcl')
        cmds.separator(style='none', height=10, width=100, parent='correction_cl')
        cmds.rowColumnLayout('correction_refresh_rcl', numberOfColumns=4, columnWidth=[(1, 50), (2, 150), (2, 100), (3, 80)], columnAlign=[(1, 'left'), (2, 'left'), (3, 'center'), (4, 'left')], columnAttach=[(1, 'both', 10), (2, 'left', 0), (3, 'left', 10), (4, 'left', 90)], parent='correction_cl')
        cmds.text('correction_type_txt', label=self.ar.data.lang['i138_type'], parent='correction_refresh_rcl')
        cmds.columnLayout('correction_radio_cl', parent='correction_refresh_rcl')
        cmds.radioCollection("correction_type_rc", parent='correction_radio_cl')
        cmds.radioButton('correction_type_angle_rb', label=self.ar.data.lang['c102_angle'].capitalize(), annotation=self.app.angle_name, collection='correction_type_rc')
        cmds.radioButton('correction_type_distance_rb', label=self.ar.data.lang['m182_distance'], annotation=self.app.distance_name, collection='correction_type_rc')
        cmds.radioCollection('correction_type_rc', edit=True, select='correction_type_angle_rb')
        cmds.checkBox('correction_rivet_cb', label="Rivet", parent='correction_refresh_rcl')
        cmds.button('correction_refresh_bt', label=self.ar.data.lang['m181_refresh'], command=self.refresh_ui, parent='correction_refresh_rcl')
        cmds.separator(style='in', height=15, width=100, parent='correction_cl')
        # existing:
        cmds.text('correction_existing_txt', label=self.ar.data.lang['m071_existing'], align="left", height=25, font='boldLabelFont', parent='correction_cl')
        cmds.textField('correction_filter_name_tf', width=30, changeCommand=self.populate_net_ui, parent='correction_cl')
        cmds.separator(style='none', height=10, width=100, parent='correction_cl')
        cmds.textScrollList('correction_existing_net_tsl', width=20, allowMultiSelection=False, selectCommand=self.update_edit_net_layout, parent='correction_cl')
        cmds.separator(style='none', height=10, width=100, parent='correction_cl')
        # edit selected net layout:
        cmds.frameLayout('correction_edit_selected_net_fl', label=self.ar.data.lang['i011_editSelected'], collapsable=True, collapse=False, parent='correction_cl')
        self.refresh_ui()


    def refresh_ui(self, *args):
        """ Just call populate UI and actualize layout methodes.
        """
        self.populate_net_ui()
        self.update_edit_net_layout()


    def recreate_selected_net_layout(self):
        """ It will recreate the edit layout for the selected network node.
        """
        if self.app.net:
            if cmds.objExists(self.app.net):
                # name:
                cmds.columnLayout('correction_selected_cl', adjustableColumn=True, parent='correction_edit_selected_net_fl')
                cmds.rowLayout('correction_name_rl', numberOfColumns=2, columnWidth2=(220, 50), columnAlign=[(1, 'left'), (2, 'right')], adjustableColumn=1, columnAttach=[(1, 'right', 50), (2, 'right', 2)], height=30, parent='correction_selected_cl')
                cmds.textFieldGrp('correction_name_tfg', label=self.ar.data.lang['m006_name'], text=cmds.getAttr(self.app.net+".name"), editable=True, columnWidth2=(40, 180), columnAttach=[(1, 'right', 2), (2, 'left', 2)], adjustableColumn2=2, changeCommand=self.app.change_name, parent='correction_name_rl')
                cmds.button('correction_delete_bt', label=self.ar.data.lang['m005_delete'], command=self.app.delete_setup, backgroundColor=(1.0, 0.7, 0.7), parent='correction_name_rl')
                # type:
                cmds.rowLayout('correction_type_rl', numberOfColumns=2, columnWidth2=(220, 50), columnAlign=[(1, 'left'), (2, 'right')], adjustableColumn=1, columnAttach=[(1, 'right', 50), (2, 'right', 2)], height=30, parent='correction_selected_cl')
                cmds.textFieldGrp("correction_type_tfg", label=self.ar.data.lang['i138_type'], text=cmds.getAttr(self.app.net+".type"), editable=False, columnWidth2=(40, 100), columnAttach=[(1, 'right', 2), (2, 'left', 2)], adjustableColumn2=2, changeCommand=self.app.change_name, parent='correction_type_rl')
                # axis:
                cmds.rowLayout('correction_axis_rl', numberOfColumns=5, columnWidth5=(85, 80, 80, 50, 10), columnAlign=[(1, 'right'), (2, 'left'), (3, 'right'), (4, 'left'), (5, 'left')], adjustableColumn=5, columnAttach=[(1, 'right', 2), (2, 'right', 2), (3, 'right', 2), (4, 'left', 2), (5, 'left', 10)], height=30, parent='correction_selected_cl')
                if cmds.getAttr(self.app.net+".type") == self.app.distance_name:
                    cmds.checkBox('correction_decompose_cb', label=self.ar.data.lang['m185_decompose'], value=cmds.getAttr(self.app.net+".decompose"), changeCommand=self.app.change_decompose, parent='correction_axis_rl')
                cmds.optionMenu("correction_axis_om", label=self.ar.data.lang['i052_axis'], changeCommand=self.app.change_axis, parent='correction_axis_rl')
                for axis in self.ar.data.axes:
                    cmds.menuItem(label=axis, parent='correction_axis_om')
                cmds.optionMenu('correction_axis_om', edit=True, value=self.ar.data.axes[cmds.getAttr(self.app.net+".axis")])
                if cmds.getAttr(self.app.net+".type") == self.app.angle_name:
                    # axis order:
                    cmds.text('correction_axis_order_txt', label=self.ar.data.lang['i052_axis']+" "+self.ar.data.lang['m045_order'], parent='correction_axis_rl')
                    cmds.optionMenu("correction_axis_order_om", label='', changeCommand=self.app.change_axis_order, parent='correction_axis_rl')
                    for axis_order in self.ar.data.axis_orders:
                        cmds.menuItem(label=axis_order, parent='correction_axis_order_om')
                    cmds.optionMenu('correction_axis_order_om', edit=True, value=self.ar.data.axis_orders[cmds.getAttr(self.app.net+".axisOrder")])
                else: #Distance
                    cmds.columnLayout('correction_distance_cl', adjustableColumn=True, height=30, parent='correction_selected_cl')
                    cmds.textFieldButtonGrp('correction_distance_tfbg', label=self.ar.data.lang['m182_distance'], text=str(round(self.app.get_distance(), 4)), buttonLabel=self.ar.data.lang['m183_readValue'], buttonCommand=self.read_distance, columnAlign=[(1, "left"), (2, "left"), (3, "left")], columnWidth=[(1, 50), (2, 60), (3, 80)], parent='correction_distance_cl')
                    if not cmds.getAttr(self.app.net+".decompose"):
                        cmds.optionMenu('correction_axis_om', edit=True, enable=False)
                # interpolation:
                cmds.columnLayout('correction_interpolation_cl', adjustableColumn=False, columnAlign="left", parent='correction_selected_cl')
                cmds.optionMenu('correction_interpolation_om', label=self.ar.data.lang['m210_interpolation'], changeCommand=self.app.change_interpolation, parent='correction_interpolation_cl')
                for interp in self.ar.data.interpolations:
                    cmds.menuItem(label=interp, parent='correction_interpolation_om')
                cmds.optionMenu('correction_interpolation_om', edit=True, value=self.ar.data.interpolations[cmds.getAttr(self.app.net+".interpolation")])
                # range:
                cmds.columnLayout('correction_range_cl', adjustableColumn=True, columnAlign="right", parent='correction_selected_cl')
                cmds.rowLayout('correction_range_rl', numberOfColumns=3, adjustableColumn=1, columnWidth=[(1, 10), (2, 58), (3, 80)], columnAttach=[(1, "right", 0), (2, "right", 20), (3, "right", 30)], parent='correction_range_cl')
                cmds.text('correction_range_txt', label=self.ar.data.lang['m072_range'], align="right", parent='correction_range_rl')
                cmds.text('correction_start_txt', label=self.ar.data.lang['c110_start'], align="right", parent='correction_range_rl')
                cmds.text('correction_end_txt', label=self.ar.data.lang['m184_end'], align="right", parent='correction_range_rl')
                cmds.floatFieldGrp("correction_input_ffg", label=self.ar.data.lang['m137_input'], numberOfFields=2, value1=cmds.getAttr(self.app.net+".inputStart"), value2=cmds.getAttr(self.app.net+".inputEnd"), columnWidth3=(40, 70, 70), columnAttach=[(1, 'right', 5), (2, 'left', 2), (3, 'left', 0)], adjustableColumn3=1, changeCommand=self.app.change_input_values, parent='correction_range_cl')
                cmds.floatFieldGrp("correction_output_ffg", label=self.ar.data.lang['m138_output'], numberOfFields=2, value1=cmds.getAttr(self.app.net+".outputStart"), value2=cmds.getAttr(self.app.net+".outputEnd"), columnWidth3=(40, 70, 70), columnAttach=[(1, 'right', 5), (2, 'left', 2), (3, 'left', 0)], adjustableColumn3=1, changeCommand=self.app.change_output_values, parent='correction_range_cl')

    
    def update_edit_net_layout(self):
        """ Clean up the current edit layout, check the selected node and update the UI.
        """
        if cmds.textScrollList('correction_existing_net_tsl', exists=True):
            self.clear_edit_net_layout()
            selection = cmds.textScrollList('correction_existing_net_tsl', query=True, selectItem=True)
            if selection:
                if cmds.objExists(selection[0]):
                    cmds.select(selection[0])
                    self.app.net = selection[0]
            self.recreate_selected_net_layout()


    def populate_net_ui(self, *args):
        """ Check existing network node to populate UI.
        """
        if cmds.textScrollList('correction_existing_net_tsl', exists=True):
            cmds.textScrollList('correction_existing_net_tsl', edit=True, deselectAll=True)
            cmds.textScrollList('correction_existing_net_tsl', edit=True, removeAll=True)
            current_nets = self.ar.utils.get_network_by_attr("dpCorrectionManager")
            if current_nets:
                self.nets = []
                filter_name = cmds.textField('correction_filter_name_tf', query=True, text=True)
                if filter_name:
                    self.app.net = None
                    self.clear_edit_net_layout()
                    current_nets = self.ar.utils.filter_name(filter_name, current_nets, " ")
                for item in current_nets:
                    if "dpNetwork" in cmds.listAttr(item):
                        if cmds.getAttr(item+".dpNetwork") == 1:
                            if "dpCorrectionManager" in cmds.listAttr(item):
                                if cmds.getAttr(item+".dpCorrectionManager") == 1:
                                    #TODO validate correctionManager node integrity here
                                    self.nets.append(item)
                if self.nets:
                    cmds.textScrollList('correction_existing_net_tsl', edit=True, append=self.nets)
                    if self.app.net:
                        if cmds.objExists(self.app.net):
                            cmds.textScrollList('correction_existing_net_tsl', edit=True, selectItem=self.app.net)


    def clear_edit_net_layout(self):
        """ Just clean up the selected layout.
        """
        if cmds.columnLayout('correction_selected_cl', query=True, exists=True):
            cmds.deleteUI('correction_selected_cl')


    def read_distance(self, *args):
        """ Update the UI text field with the current distance.
        """
        if cmds.getAttr(self.app.net+".type") == self.app.distance_name:
            cmds.textFieldButtonGrp("correction_distance_tfbg", edit=True, text=str(round(self.app.get_distance(), 4)))
