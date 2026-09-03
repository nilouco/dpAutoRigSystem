#import libraries
from maya import cmds
from ..library.validate.checkout import reset_pose
from functools import partial
from importlib import reload


class ValueEditorUI(object):
    def __init__(self, ar):
        self.ar = ar
        if self.ar.dev:
            reload(reset_pose)
        self.reset_pose = reset_pose.ResetPose(self.ar)
    
    
    def create_ui(self, *args):
        """ Create an UI to edit the attributes default values.
        """
        self.ar.ui_manager.close_ui('dpDefaultValueOptionWindow')
        # window
        width  = 430
        height = 300
        cmds.window('dpDefaultValueOptionWindow', title=self.ar.data.lang['i270_defaultValues']+" "+self.ar.data.lang['i274_editor'], widthHeight=(width, height), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        # create UI layout and elements:
        cmds.columnLayout('value_editor_main_cl', adjustableColumn=True, columnOffset=("both", 10), parent='dpDefaultValueOptionWindow')
        cmds.separator(style='none', height=5, parent='value_editor_main_cl')
        cmds.rowColumnLayout('value_editor_header_rcl', numberOfColumns=3, columnWidth=[(1, 150), (2, 10), (3, 180)], columnAlign=[(1, 'center'), (2, 'right'), (3, 'center')], columnAttach=[(1, 'both', 5), (2, 'both', 2), (3, 'both', 5)], adjustableColumn=2, parent='value_editor_main_cl')
        cmds.button('value_editor_edit_selected_ctrl_btn', label=self.ar.data.lang['i011_editSelected'], command=self.populate_selected_controllers, parent='value_editor_header_rcl')
        cmds.separator(style='none', height=30, parent='value_editor_header_rcl')
        cmds.button('value_editor_selected_all_ctrl_btn', label=self.ar.data.lang['i291_selectAllControls'], command=partial(self.ar.ctrls.select_all_controllers, True), parent='value_editor_header_rcl')
        cmds.columnLayout('value_editor_first_cl',  adjustableColumn=True, columnOffset=("both", 10), parent='value_editor_main_cl')
        cmds.rowLayout('value_editor_first_rl', numberOfColumns=4, columnWidth4=(150, 100, 50, 50), height=32, columnAlign=[(1, 'left'), (2, 'left'), (3, 'left'), (4, 'left')], columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2)], parent='value_editor_first_cl')
        cmds.text("value_editor_controller_txt", label=self.ar.data.lang['i111_controller'], font='boldLabelFont', align="center", parent='value_editor_first_rl')
        cmds.text("value_editor_attribute_txt", label=self.ar.data.lang['i275_attribute'], font='boldLabelFont', parent='value_editor_first_rl')
        cmds.text("value_editor_default_txt", label=self.ar.data.lang['m042_default'], font='boldLabelFont', parent='value_editor_first_rl')
        cmds.text("value_editor_current_txt", label=self.ar.data.lang['i276_current'], font='boldLabelFont', parent='value_editor_first_rl')
        cmds.separator(style='in', height=10, parent='value_editor_main_cl')
        cmds.scrollLayout('value_editor_default_sl', width=350, height=200, parent='value_editor_main_cl')
        cmds.columnLayout('value_editor_default_cl', adjustableColumn=True, columnOffset=("both", 10), parent='value_editor_default_sl')
        self.populate_selected_controllers()
        # call window
        cmds.showWindow('dpDefaultValueOptionWindow')


    def populate_selected_controllers(self, *args):
        """ Refresh the default value editor UI to fill it with the selected dpAR controllers.
        """
        if cmds.columnLayout('value_editor_default_cl', query=True, exists=True):
            cmds.deleteUI('value_editor_default_cl')
        cmds.columnLayout('value_editor_default_cl', adjustableColumn=True, columnOffset=("both", 10), parent='value_editor_default_sl')
        controllers = self.ar.ctrls.get_selected_controllers()
        if controllers:
            controllers.sort()
            for c, ctrl in enumerate(controllers):
                attributes = self.reset_pose.getSetupAttrList(ctrl, self.ar.ctrls.ignore_default_value_attrs)
                if attributes:
                    for a, attr in enumerate(attributes):
                        cmds.rowLayout(numberOfColumns=4, columnWidth4=(150, 100, 50, 50), columnAlign=[(1, 'left'), (2, 'left'), (3, 'left'), (4, 'left')], columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2)], parent='value_editor_default_cl')
                        if a == 0:
                            cmds.button(label=ctrl, command=partial(self.ar.ctrls.select_controller, ctrl, True))
                        else:
                            cmds.text(label="")
                        cmds.text(label=attr)
                        # default value
                        cmds.floatField(value=cmds.addAttr(ctrl+"."+attr, query=True, defaultValue=True), precision=3, changeCommand=partial(self.ar.ctrls.set_default_value, ctrl, attr))
                        # current value
                        cmds.floatField(value=cmds.getAttr(ctrl+"."+attr), precision=3, changeCommand=partial(self.ar.ctrls.set_current_value, ctrl, attr))
                    cmds.separator(style='in', height=10, parent='value_editor_default_cl')
