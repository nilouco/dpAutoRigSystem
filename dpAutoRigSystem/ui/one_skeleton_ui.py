#import libraries
from maya import cmds
from functools import partial


class OneSkeletonUI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self, app):
        """ This is the main method to load the One Skeleton UI.
        """
        self.app = app
        # creating Window:
        self.ar.utils.close_ui('one_skeleton_win')
        width  = 230
        height = 230
        cmds.window('one_skeleton_win', title=self.ar.data.lang["m254_oneSkeleton"]+" "+str(self.ar.data.version), widthHeight=(width, height), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        cmds.columnLayout('one_skeleton_cl', columnOffset=("both", 10), rowSpacing=10, adjustableColumn=True, parent='one_skeleton_win')
        cmds.separator(height=5, style="in", horizontal=True, parent='one_skeleton_cl')
        cmds.rowColumnLayout('one_skeleton_naming_rcl', numberOfColumns=2, adjustableColumn=2, columnWidth=(80, 100), rowSpacing=(7, 7), parent='one_skeleton_cl')
        cmds.text('one_skeleton_prefix_txt', label=self.ar.data.lang['i144_prefix'], parent='one_skeleton_naming_rcl')
        cmds.textField('one_skeleton_prefix_tf', text=self.app.prefix, textChangedCommand=self.app.change_prefix, parent='one_skeleton_naming_rcl')
        cmds.text('one_skeleton_root_txt', label="Root", parent='one_skeleton_naming_rcl')
        cmds.textField('one_skeleton_root_tf', text=self.app.root_name, textChangedCommand=self.app.change_root, parent='one_skeleton_naming_rcl')
        cmds.text('one_skeleton_suffix_txt', label=self.ar.data.lang['m217_suffix'], parent='one_skeleton_naming_rcl')
        cmds.textField('one_skeleton_suffix_tf', text=self.app.suffix, textChangedCommand=self.app.change_suffix, parent='one_skeleton_naming_rcl')
        cmds.text('one_skeleton_header_txt', label=self.ar.data.lang['m223_preview'], parent='one_skeleton_naming_rcl')
        cmds.text('one_skeleton_preview_txt', label=f"{self.app.prefix}{self.app.root_name}{self.app.suffix}", font="boldLabelFont", parent='one_skeleton_naming_rcl')
        cmds.radioButtonGrp("one_skeleton_skeleton_rbg", label=self.ar.data.lang['i138_type'], labelArray2=["Floating Joints", self.ar.data.lang['m216_hierarchy']], vertical=True, numberOfRadioButtons=2, columnAlign2=("left", "left"), columnAttach2=("left", "left"), columnWidth2=(40, 100), changeCommand=self.app.change_parenting, parent="one_skeleton_cl")
        cmds.radioButtonGrp("one_skeleton_skeleton_rbg", edit=True, select=2) #hierarchy = 2
        cmds.checkBox("one_skeleton_use_scale_cb", label="Scale constraint", value=False, enable=False, parent="one_skeleton_cl")
        cmds.button("run_one_skeleton_bt", label=self.ar.data.lang['i158_create'], command=self.create_by_ui, parent="one_skeleton_cl")
        cmds.separator(height=5, style="in", horizontal=True, parent='one_skeleton_cl')
        # call Window:
        cmds.showWindow('one_skeleton_win')


    def create_by_ui(self, *args):
        joint_type = cmds.radioButtonGrp('one_skeleton_skeleton_rbg', query=True, select=True)-1
        use_scale = cmds.checkBox('one_skeleton_use_scale_cb', query=True, value=True)
        self.app.create_one_skeleton(hierarchy=joint_type, scale=use_scale)
        self.ar.utils.close_ui('one_skeleton_win')
