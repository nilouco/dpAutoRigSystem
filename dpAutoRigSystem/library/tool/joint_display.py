# importing libraries:
from maya import cmds
from ..base import base
from importlib import reload

# global variables to this module:
CLASS_NAME = "JointDisplay"
TITLE = "m233_jointDisplay"
DESCRIPTION = "m234_jointDisplayDesc"
WIKI = "06-‐-Tools#-joint-display"



class JointDisplay(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        # joints lists 
        self.joints = []
        self.bone_label_items = []
        self.joint_label_items = []
        self.multichild_label_items = []
        self.none_label_items = []
        self.selection_ui_items = []
        self.selected_board = 0
        self.dest_board_index = 0
        

    def build_tool(self, *args):
        if self.ar.data.ui_state:
            self.ar.joint_display_ui.create_ui(self)


    def update_joints(self):
        """ Get all joints in the scene and update the joints variable.
        """
        self.joints = cmds.ls(selection=False, type='joint')
        if self.ar.data.ui_state:
            written_value = cmds.textFieldGrp('joint_display_filter_tfg', query=True, text=True)
            if not written_value == "" and not written_value == " ":
                self.joints = self.ar.naming.filter_name(written_value, cmds.ls(selection=False, type='joint'), " ")


    def update_labels(self, *args):
        """ Populate each list with label joint type.
        """
        if self.joints:
            for jnt in self.joints:
                if cmds.getAttr(jnt +'.drawStyle') == 0:
                    self.bone_label_items.append(jnt)
                    self.selected_board = 0
                elif cmds.getAttr(jnt +'.drawStyle') == 1:
                    self.multichild_label_items.append(jnt)                    
                    self.selected_board = 1
                elif cmds.getAttr(jnt +'.drawStyle') == 2:
                    self.none_label_items.append(jnt)
                    self.selected_board = 2
                elif cmds.getAttr(jnt +'.drawStyle') == 3:
                    self.joint_label_items.append(jnt)
                    self.selected_board = 3


    def clear_items(self):
        """ Clear all Lists
        """
        self.joints.clear()
        self.bone_label_items.clear()
        self.multichild_label_items.clear()
        self.none_label_items.clear()
        self.joint_label_items.clear()


    def move_to_right(self, *args):
        """ Button to move the selected joints to the right board
        """
        # Get active selection of button list
        if self.selection_ui_items:
            current_draw_style = cmds.getAttr(self.selection_ui_items[0]+'.drawStyle')
            if current_draw_style < 3:
                for jnt in self.selection_ui_items:
                    cmds.setAttr(jnt +'.drawStyle', current_draw_style + 1)
                self.dest_board_index = current_draw_style + 1
            else:
                current_draw_style = 0
                for jnt in self.selection_ui_items: 
                    cmds.setAttr(jnt +'.drawStyle', current_draw_style)
                self.dest_board_index = 0
            if self.ar.data.ui_state:
                self.ar.joint_display_ui.refresh_ui()
                self.ar.joint_display_ui.keep_selection()
    
    
    def move_to_left(self, *args):
        """ Button to move the selected joints to the left board 
        """
        # Get active selection of button list
        if self.selection_ui_items:
            current_draw_style = cmds.getAttr(self.selection_ui_items[0]+'.drawStyle')
            if current_draw_style > 0 < 3:
                for jnt in self.selection_ui_items:
                    cmds.setAttr(jnt +'.drawStyle', current_draw_style - 1)
                self.dest_board_index = current_draw_style - 1
            else: 
                current_draw_style = 3
                for jnt in self.selection_ui_items:
                    cmds.setAttr(jnt +'.drawStyle', current_draw_style)
                self.dest_board_index = 3
            if self.ar.data.ui_state:
                self.ar.joint_display_ui.refresh_ui()
                self.ar.joint_display_ui.keep_selection()


    def change_all_joints(self, *args):
        """ Change all joints to the selected drawStyle.
        """
        selected_label = cmds.optionMenu('joint_display_change_om', query=True, value=True)
        if selected_label == 'Bone':
            self.set_draw_style(0)
        elif selected_label == 'Multi-Child as box':
            self.set_draw_style(1)
        elif selected_label == 'None':
            self.set_draw_style(2)
        elif selected_label == 'Joint':
            self.set_draw_style(3)


    def set_draw_style(self, draw_style_index, *args):
        """ Set all joints to the selected drawStyle.
        """        
        self.joints
        if self.joints:
            for jnt in self.joints:
                cmds.setAttr(f"{jnt}.drawStyle", draw_style_index)
                self.selection_ui_items.append(jnt)
        self.dest_board_index = draw_style_index
        if self.ar.data.ui_state:
            self.ar.joint_display_ui.refresh_ui()
                

    def change_radius(self, value, *args):
        """ Set the selected joints radius as given value.
        """
        if self.ar.data.ui_state:
            self.ar.joint_display_ui.refresh_ui()
        if self.selection_ui_items:
            for jnt in self.selection_ui_items:
                cmds.setAttr(jnt+".radius", value)
