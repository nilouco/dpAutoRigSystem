#import libraries
from maya import cmds
from functools import partial


class JointDisplayUI(object):
    def __init__(self, ar):
        self.ar = ar
        self.boards = ['joint_display_bone_field_sl', 'joint_display_multichild_field_sl', 'joint_display_none_field_sl', 'joint_display_joint_field_sl']
        
    
    
    def create_ui(self, app):
        """ This is the main method to load the Joint Display UI.
        """
        self.app = app
        self.ar.utils.close_ui('dpJointDisplayWindow')
        width  = 660
        height = 410
        cmds.window('dpJointDisplayWindow', title=self.ar.data.lang["m233_jointDisplay"]+" "+str(self.ar.data.version), widthHeight=(width, height), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating Main layout:
        cmds.columnLayout('joint_display_cl', columnOffset=('both', 5), adjustableColumn=True)
        cmds.separator(style='none', height=10, parent='joint_display_cl')
        cmds.rowColumnLayout('joint_display_header_rcl', adjustableColumn=1, numberOfColumns=2, columnWidth=[(1, 140), (2, 320)], columnAlign=[(1, 'left'), (2, 'right')], columnAttach=[(1, 'left', 10), (2, 'right', 10)], parent='joint_display_cl')
        # filter
        cmds.textFieldGrp('joint_display_filter_tfg', label=self.ar.data.lang['i268_filterByName'], text="", textChangedCommand=self.refresh_ui, adjustableColumn=2, parent='joint_display_header_rcl')
        cmds.floatSliderGrp('joint_display_radius_fsg', label=self.ar.data.lang['c067_radius'].capitalize(), field=True, minValue=0, value=1, sliderStep=0.1, changeCommand=self.app.change_radius, adjustableColumn=3, parent='joint_display_header_rcl')
        cmds.separator(style='none', height=5, parent='joint_display_cl')
        # bone display panels
        cmds.paneLayout('joint_display_pl', configuration="vertical4", separatorThickness=5.0, width=400, parent='joint_display_cl')
        cmds.columnLayout('joint_display_bone_cl', columnOffset=('both', 1), adjustableColumn=True, parent='joint_display_pl')
        cmds.columnLayout('joint_display_multi_cl', columnOffset=('both', 1), adjustableColumn=True, parent='joint_display_pl')
        cmds.columnLayout('joint_display_none_cl', columnOffset=('both', 1), adjustableColumn=True, parent='joint_display_pl')
        cmds.columnLayout('joint_display_joint_cl', columnOffset=('both', 1), adjustableColumn=True, parent='joint_display_pl')
        cmds.text('joint_display_bone_txt', label='Bone', font="boldLabelFont", parent='joint_display_bone_cl')
        cmds.text('joint_display_multichild_txt', label='Multi-Child as box', font="boldLabelFont", parent='joint_display_multi_cl')
        cmds.text('joint_display_none_txt', label='None', font="boldLabelFont", parent='joint_display_none_cl')
        cmds.text('joint_display_joint_txt', label='Joint', font="boldLabelFont", parent='joint_display_joint_cl')
        cmds.separator(style='none', height=5, parent='joint_display_bone_cl')
        cmds.separator(style='none', height=5, parent='joint_display_multi_cl')
        cmds.separator(style='none', height=5, parent='joint_display_none_cl')
        cmds.separator(style='none', height=5, parent='joint_display_joint_cl')
        cmds.textScrollList(self.boards[0], enable=True, parent='joint_display_bone_cl', allowMultiSelection=True, selectCommand=partial(self.get_active_selection, 0), deselectAll=True, height=300)
        cmds.textScrollList(self.boards[1], enable=True, parent='joint_display_multi_cl', allowMultiSelection=True, selectCommand=partial(self.get_active_selection, 1), deselectAll=True, height=300)
        cmds.textScrollList(self.boards[2],enable=True, parent='joint_display_none_cl', allowMultiSelection=True, selectCommand=partial(self.get_active_selection, 2), deselectAll=True, height=300)
        cmds.textScrollList(self.boards[3],enable=True, parent='joint_display_joint_cl', allowMultiSelection=True, selectCommand=partial(self.get_active_selection, 3), deselectAll=True, height=300)
        # bottom layout for buttons
        cmds.separator(style='none', height=10, parent='joint_display_cl')
        cmds.rowColumnLayout('joint_display_button_rcl', childArray=True, numberOfColumns=3, columnWidth=[(1, 160), (2, 100), (3, 160)], columnOffset=[(1, "both", 5), (2, "both", 80), (3, "both", 5)], adjustableColumn=2, parent='joint_display_cl')
        # defining move buttons
        cmds.button('joint_display_move_to_right_btn', label=self.ar.data.lang['c034_move']+' >>', backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.app.move_to_right, parent='joint_display_button_rcl')
        cmds.optionMenu('joint_display_change_om',label=self.ar.data.lang['i359_changeTo']+' :', width = 200, parent='joint_display_button_rcl', changeCommand= self.app.change_all_joints)
        cmds.menuItem('joint_display_bone_mi', label='Bone', parent='joint_display_change_om')
        cmds.menuItem('joint_display_multichild_mi', label='Multi-Child as box', parent='joint_display_change_om' )
        cmds.menuItem('joint_display_none_mi', label='None', parent='joint_display_change_om' )
        cmds.menuItem('joint_display_joint_mi', label='Joint', parent='joint_display_change_om' )
        cmds.button('joint_display_move_to_left_btn', label='<< '+self.ar.data.lang['c034_move'], backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.app.move_to_left, parent='joint_display_button_rcl')
        cmds.showWindow('dpJointDisplayWindow')
        self.app.clear_items()
        self.refresh_ui()
        self.ar.job.refresh_preview_win(self.refresh_ui, 'dpJointDisplayWindow')
    

    def refresh_ui(self, *args):
        """ Refresh the code
        """
        self.app.clear_items()
        self.app.update_joints()
        self.app.update_labels()
        self.populate_boards()


    def deselect_other_boards(self, board_index):
        """ Figure out which board column is selected.
        """
        for b, board in enumerate(self.boards):
            if not b == board_index:
                cmds.textScrollList(self.boards[b], edit=True, deselectAll=True)
        

    def get_active_selection(self, board_index, *args):
        """ Get the active selection.
        """
        self.selected_board = board_index
        self.deselect_other_boards(board_index)
        self.app.selection_ui_items = cmds.textScrollList(self.boards[board_index], query=True, selectItem=True)


    def populate_boards(self):
        """ Refresh the preview of each board.
        """
        # BoneFieldcolumn board
        cmds.textScrollList(self.boards[0], edit=True, removeAll=True)
        cmds.textScrollList(self.boards[0], edit=True, append=self.app.bone_label_items)
        # BultiChildFieldcolumn board
        cmds.textScrollList(self.boards[1], edit=True, removeAll=True)
        cmds.textScrollList(self.boards[1], edit=True, append=self.app.multichild_label_items)
        # BoneFieldcolumn board
        cmds.textScrollList(self.boards[2], edit=True, removeAll=True)
        cmds.textScrollList(self.boards[2], edit=True, append=self.app.none_label_items)
        # JointFieldcolumn board
        cmds.textScrollList(self.boards[3], edit=True, removeAll=True)
        cmds.textScrollList(self.boards[3], edit=True, append=self.app.joint_label_items)


    def keep_selection(self):
        """ Maintain ative the selected joints.
        """
        selected_items = self.app.selection_ui_items
        if selected_items:
            cmds.textScrollList(self.boards[self.app.dest_board_index], edit=True, selectItem=selected_items)