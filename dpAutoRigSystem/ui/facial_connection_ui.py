from functools import partial

from maya import cmds


class FacialConnectionUI:
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self, app):
        """ This is the main method to load the Facial Connection UI.
        """
        self.app = app
        self.ar.ui_manager.close_ui(self.ar.data.facial_connection_win_name)
        width  = 230
        height = 405
        cmds.window(self.ar.data.facial_connection_win_name, title=f"{self.ar.data.lang['m085_facialConnection']} {self.ar.data.version}", widthHeight=(width, height), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        cmds.columnLayout('facial_connect_cl', columnOffset=('both', 10), rowSpacing=10, parent=self.ar.data.facial_connection_win_name)
        cmds.separator(height=5, style='in', horizontal=True, parent='facial_connect_cl')
        cmds.button('facial_connect_create_targets_bt', label=self.ar.data.lang['m140_createTargets'], annotation=self.ar.data.lang['m141_createTargetsDesc'], width=220, command=self.app.create_targets_from_ui, align='center', parent='facial_connect_cl')
        cmds.checkBox('facial_connect_bs_cb', label=self.ar.data.lang['m258_createBSNode'], annotation=self.ar.data.lang['m259_createBSNodeDesc'], value=1, parent='facial_connect_cl')
        cmds.checkBox('facial_connect_comb_cb', label=self.ar.data.lang['m260_combinationTargets'], annotation=self.ar.data.lang['m261_combinationTargetsDesc'], value=1, parent='facial_connect_cl')
        cmds.checkBox('facial_connect_tweak_only_cb', label=self.ar.data.lang['m262_tweakTargetOnly'], annotation=self.ar.data.lang['m090_tweakTargetOnlyDesc'], value=0, changeCommand=self.disable_combination, parent='facial_connect_cl')
        cmds.separator(height=5, style='single', horizontal=True, parent='facial_connect_cl')
        cmds.text('facial_connect_recreate_txt', label=self.ar.data.lang['m091_rebuildTargetsText'], parent='facial_connect_cl')
        cmds.button('facial_connect_recreate_bt', label=self.ar.data.lang['m092_recreateTargets'], annotation=self.ar.data.lang['m093_recreateTargetsDesc'], width=220, command=self.app.recreate_targets, parent='facial_connect_cl')
        cmds.separator(height=5, style='single', horizontal=True, parent='facial_connect_cl')
        cmds.text('facial_connect_connect_txt', label=self.ar.data.lang['m142_connectFacialAttr'], parent='facial_connect_cl')
        cmds.button('facial_connect_bs_bt', label=f"{self.ar.data.lang['m170_blendShapes']} - {self.ar.data.lang['i185_animation']}", annotation='Create selected facial controls.', width=220, command=self.app.connect_to_blendshape, parent='facial_connect_cl')
        cmds.button('facial_connect_joint_bt', label=f"{self.ar.data.lang['i181_facialJoint']} - {self.ar.data.lang['i186_gaming']}", annotation='Create default facial controls package.', width=220, command=self.app.connect_to_joints, parent='facial_connect_cl')
        cmds.separator(height=5, style="in", horizontal=True, parent='facial_connect_cl')
        cmds.text('facial_cabibrate_joint_txt', label=self.ar.data.lang['i193_calibration'], parent='facial_connect_cl')
        cmds.button('facial_cabibrate_joint_bt', label=self.ar.data.lang['c111_calibrate']+" "+self.ar.data.lang['i181_facialJoint'], annotation="Calibrate facial joints for gaming.", width=220, command=self.calibrate_facial_joints_ui, parent='facial_connect_cl')
        # call facialControlUI Window:
        cmds.showWindow(self.ar.data.facial_connection_win_name)


    def disable_combination(self, value, *args):
        """ If the tweakTgtOnlyCB is checked, turn off and disable the combinationTgtCB.
        """
        if value:
            cmds.checkBox('facial_connect_comb_cb', edit=True, enable=False, value=False)
        else:
            cmds.checkBox('facial_connect_comb_cb', edit=True, enable=True)


    def calibrate_facial_joints_ui(self, *args):
        # creating targetMirrorUI Window:
        self.ar.ui_manager.close_ui(self.ar.data.calibrate_facial_joints_win_name)
        width  = 430
        height = 500
        cmds.window(self.ar.data.calibrate_facial_joints_win_name, title=f"{self.ar.data.lang['c111_calibrate']} {self.ar.data.lang['i181_facialJoint']} {self.ar.data.version}", widthHeight=(width, height), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        cmds.formLayout('calibrate_facial_joints_fl', numberOfDivisions=100)
        cmds.columnLayout('calibrate_facial_joints_cl', columnOffset=("both", 10), rowSpacing=10, adjustableColumn=True, parent='calibrate_facial_joints_fl')
        cmds.separator(height=5, style="none", horizontal=True, width=width, parent='calibrate_facial_joints_cl')
        cmds.rowColumnLayout('facial_ctrl_rcl', numberOfColumns=2, adjustableColumn=2, columnWidth=[(1, 150), (2, 130)], rowSpacing=(1, 10), columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 20)], parent='calibrate_facial_joints_cl')
        cmds.text("facial_ctrl_txt", label="Facial Ctrl", parent="facial_ctrl_rcl")
        cmds.text("attribute_txt", label="Attribute", parent="facial_ctrl_rcl")
        cmds.textScrollList("facial_ctrl_tsl", selectCommand=self.load_selected_attrs, allowMultiSelection=False, parent='facial_ctrl_rcl')
        cmds.textScrollList("attr_ctrl_tsl", selectCommand=self.load_selected_offsets, allowMultiSelection=False, parent='facial_ctrl_rcl')
        cmds.checkBox('facial_ctrl_auto_calibrate_cb', label=f"{self.ar.data.lang['c121_side']} {self.ar.data.lang['c119_auto']} {self.ar.data.lang['c111_calibrate']}", value=True, parent='calibrate_facial_joints_cl')
        cmds.separator(height=5, style="in", horizontal=True, width=width, parent='calibrate_facial_joints_cl')
        cmds.text(label=self.ar.data.lang['i193_calibration'], parent='calibrate_facial_joints_cl')
        cmds.separator(height=3, style="none", horizontal=True, width=width, parent='calibrate_facial_joints_cl')
        cmds.scrollLayout("calibrate_facial_joints_sl", childResizable=True, parent='calibrate_facial_joints_fl')
        cmds.columnLayout('calibrate_facial_joints_attributes_cl', columnOffset=("both", 10), rowSpacing=10, adjustableColumn=True, parent='calibrate_facial_joints_sl')
        cmds.formLayout('calibrate_facial_joints_fl', edit=True, attachForm=[('calibrate_facial_joints_cl', 'left', 0), ('calibrate_facial_joints_cl', 'right', 0), ('calibrate_facial_joints_cl', 'top', 0), ('calibrate_facial_joints_sl', 'left', 0), ('calibrate_facial_joints_sl', 'right', 0), ('calibrate_facial_joints_sl', 'bottom', 0)], attachControl=[('calibrate_facial_joints_sl', 'top', 0, 'calibrate_facial_joints_cl')])
        # call CalibrateFacialJointsUI Window:
        cmds.showWindow(self.ar.data.calibrate_facial_joints_win_name)
        # load data
        self.load_ui_data()


    def load_ui_data(self):
        facial_controllers = self.app.get_facial_controllers()
        if facial_controllers:
            tsl_height = (len(facial_controllers)+1)*15
            cmds.textScrollList('facial_ctrl_tsl', edit=True, height=tsl_height, append=facial_controllers)
            cmds.textScrollList('attr_ctrl_tsl', edit=True, height=tsl_height)


    def load_selected_attrs(self, *args):
        ctrl = cmds.textScrollList('facial_ctrl_tsl', query=True, selectItem=True)[0]
        attributes = self.app.get_facial_attributes(ctrl)
        cmds.textScrollList('attr_ctrl_tsl', edit=True, removeAll=True)
        cmds.textScrollList('attr_ctrl_tsl', edit=True, append=attributes)
        self.clear_facial_calibration_attributes_layout()


    def load_selected_offsets(self, *args):
        ctrl = cmds.textScrollList('facial_ctrl_tsl', query=True, selectItem=True)[0]
        attr = cmds.textScrollList('attr_ctrl_tsl', query=True, selectItem=True)[0]
        self.clear_facial_calibration_attributes_layout()
        calib_attrs = self.app.get_facial_calibration_attributes(ctrl, attr)
        for calib_attr in calib_attrs:
            offset_ctrl = calib_attr[:calib_attr.rfind("_")]
            offset_ctrl = f'{offset_ctrl[:offset_ctrl.rfind("_")]}_Ctrl'
            calib_attr_value = cmds.getAttr(f'{ctrl}.{calib_attr}')
            cmds.floatSliderButtonGrp(f'{calib_attr}_fsbg', label=calib_attr, field=True, buttonLabel=self.ar.data.lang['m004_select'], value=calib_attr_value, minValue=-360, maxValue=360, dragCommand=partial(self.app.set_facial_joint_calibration, ctrl, attr, calib_attr), changeCommand=partial(self.app.set_facial_joint_calibration, ctrl, attr, calib_attr), buttonCommand=partial(cmds.select, offset_ctrl), columnWidth4=(180, 50, 120, 50), adjustableColumn=3, parent='calibrate_facial_joints_attributes_cl')


    def clear_facial_calibration_attributes_layout(self):
        if cmds.columnLayout('calibrate_facial_joints_attributes_cl', query=True, exists=True):
            cmds.deleteUI('calibrate_facial_joints_attributes_cl')
            cmds.columnLayout('calibrate_facial_joints_attributes_cl', columnOffset=('both', 10), rowSpacing=10, parent='calibrate_facial_joints_sl')
