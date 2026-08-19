# importing libraries:
from maya import cmds
from functools import partial



class GuideUI(object):
    def __init__(self, ar):
        self.ar = ar
        
    
    def basic_module_layout(self, standard, *args):
        """ Create a Basic Module layout.
        """

        # declaring facial variables
        self.jointsType = "jointsType"

        cmds.rowLayout(f"{standard.number_name}_rl", numberOfColumns=3, width=190, columnWidth3=(30, 120, 20), adjustableColumn=2, columnAlign=[(1, 'left'), (2, 'left'), (3, 'left')], columnAttach=[(1, 'both', 2), (2, 'both', 4), (3, 'both', 0)], parent=f"{standard.number_name}_top_cl")
        cmds.button(f"{standard.number_name}_select_bt", label=" ", annotation=self.ar.data.lang['m004_select'], command=partial(self.update_edit_selected_module_ui, standard, True), backgroundColor=(0.5, 0.5, 0.5), dragCallback=partial(self.select_button_callback, standard), parent=f"{standard.number_name}_rl")
        cmds.textField(f"{standard.number_name}_custom_name_tf", annotation=self.ar.data.lang['i101_customName'], text=cmds.getAttr(standard.guide_base+".customName"), changeCommand=standard.set_guide_custom_name, parent=f"{standard.number_name}_rl")
        cmds.iconTextButton(image=self.ar.data.icon['plus_info'], height=30, width=17, style='iconOnly', command=partial(self.plus_info_ui, standard), parent=f"{standard.number_name}_rl")
        self.update_edit_selected_module_ui(standard)


    def clear_selected_module_layout(self):
        """ Clear the selected module layout, because the module was rigged, deleted or unselected maybe.
        """
        if cmds.columnLayout("rig_selected_module_cl", query=True, exists=True):
            cmds.deleteUI("rig_selected_module_cl")
    
    
    def update_edit_selected_module_ui(self, standard, select=True, *args):
        """ Select the moduleGuide, clear the selectedModuleLayout and re-create the mirrorLayout and custom attribute layouts.
        """
        if self.ar.data.ui_state:
            if standard.check_guide_integrity():
                # select the module to be recreate the edit selected module layout
                if select:
                    cmds.select(standard.guide_base)
                self.clear_selected_module_layout()
                self.create_edit_selected_layout(standard)
                # work on guides features
                self.segment_layout(standard)
                self.delete_duplicate_button(standard)
                self.flip_layout(standard)
                self.mirror_layout(standard)
                self.rig_it_button(standard)
                self.degree_layout(standard)
                self.reorient_layout(standard)
                self.style_layout(standard)
                self.type_layout(standard)
                self.deformed_by_layout(standard)
                self.eye_aim_direction_layout(standard)
                self.indirectskin_layout(standard)
                self.eyelid_layout(standard)
                self.geometry_layout(standard)
                self.start_frame_layout(standard)
                self.steering_layout(standard)
                self.fatherb_layout(standard)
                self.head_items_layout(standard)
                self.align_world_layout(standard)
                self.articulation_layout(standard)
                self.nostril_layout(standard)
                self.corrective_layout(standard)
                self.dynamic_layout(standard)
                self.main_ctrl_layout(standard)
                self.bend_layout(standard)
                self.deformer_layout(standard)
                self.facial_layout(standard)
                if cmds.window(self.ar.data.plus_info_win_name, query=True, exists=True):
                    self.plus_info_ui(standard)


    def create_edit_selected_layout(self, standard):
        # edit label of frame layout:
        guide_name = cmds.getAttr(standard.guide_base+".customName")
        if not guide_name:
            guide_name = standard.number_name
        cmds.frameLayout("rig_edit_selected_module_fl", edit=True, collapse=self.ar.data.collapse_edit_sel_mod, label=self.ar.data.lang['i011_editSelected']+" "+self.ar.data.lang['i143_module']+" :  "+self.ar.data.lang[standard.title]+" - "+guide_name)
        cmds.columnLayout("rig_selected_module_cl", adjustableColumn=True, parent="rig_edit_selected_module_fl")
        # re-create segment layout:
        cmds.rowLayout('edit_seg_del_dup_rl', numberOfColumns=4, columnWidth4=(100, 140, 50, 75), columnAlign=[(1, 'right'), (2, 'left'), (3, 'left'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
        # reCreate mirror layout:
        cmds.rowLayout('edit_guide_mirror_rl', numberOfColumns=5, columnWidth5=(45, 55, 50, 80, 70), columnAlign=[(2, 'right'), (4, 'right')], adjustableColumn=5, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'both', 10)], parent="rig_selected_module_cl" )


    def segment_layout(self, standard):
        if 'nJoints' in cmds.listAttr(standard.guide_base):
            cmds.text('edit_segments_txt', label=self.ar.data.lang['m003_segments'], parent='edit_seg_del_dup_rl')
            if cmds.getAttr(standard.guide_base+".nJoints") > 0:
                cmds.intField('edit_guide_n_joints_if', value=cmds.getAttr(standard.guide_base+".nJoints"), minValue=1, changeCommand=partial(standard.changeJointNumber, 0), parent='edit_seg_del_dup_rl')
            else:
                cmds.intField('edit_guide_n_joints_if', value=cmds.getAttr(standard.guide_base+".nJoints"), minValue=0, editable=False, parent='edit_seg_del_dup_rl')
        else:
            cmds.text(" ", parent='edit_seg_del_dup_rl')
            cmds.text(" ", parent='edit_seg_del_dup_rl')


    def delete_duplicate_button(self, standard):
        cmds.button('edit_delete_bt', label=self.ar.data.lang['m005_delete'], command=standard.delete_guide, backgroundColor=(1.0, 0.7, 0.7), parent='edit_seg_del_dup_rl')
        cmds.button('edit_duplicate_bt', label=self.ar.data.lang['m070_duplicate'], command=standard.duplicate_guide, backgroundColor=(0.7, 0.6, 0.8), annotation=self.ar.data.lang['i068_CtrlD'], parent='edit_seg_del_dup_rl')


    def flip_layout(self, standard):
        # create a flip layout:
        if 'flip' in cmds.listAttr(standard.guide_base):
            cmds.checkBox('edit_guide_flip', label="Flip", value=cmds.getAttr(standard.guide_base+".flip"), changeCommand=partial(standard.set_guide_attr, 'flip'), parent='edit_guide_mirror_rl')
            if standard.check_father_mirror():
                if standard.father_flip_exists:
                    cmds.checkBox(self.flipCB, edit=True, enable=False)
        else:
            cmds.text("", parent='edit_guide_mirror_rl')


    def mirror_layout(self, standard):
        cmds.text('edit_guide_mirror_txt', label=self.ar.data.lang['m010_mirror'], parent='edit_guide_mirror_rl')
        cmds.optionMenu("edit_mirror_om", label='', changeCommand=standard.changeMirror, parent='edit_guide_mirror_rl')
        for item in self.ar.data.mirror_menus:
            cmds.menuItem(f"{item}_mi", label=item, parent='edit_mirror_om')
        # verify if there are a list of mirrorNames to menuOption:
        current_mirror_names = cmds.getAttr(standard.guide_base+".mirrorNameList")
        if current_mirror_names:
            mirror_names = str(current_mirror_names).split(';')
        else:
            L = self.ar.data.lang['p002_left']
            R = self.ar.data.lang['p003_right']
            T = self.ar.data.lang['p004_top']
            B = self.ar.data.lang['p005_bottom']
            F = self.ar.data.lang['p006_front']
            K = self.ar.data.lang['p007_back']
            mirror_names = [L+' --> '+R, R+' --> '+L, T+' --> '+B, B+' --> '+T, F+' --> '+K, K+' --> '+F]
        # create items for mirrorName menu:
        cmds.optionMenu("edit_mirror_name_om", label='', changeCommand=standard.changeMirrorName, parent='edit_guide_mirror_rl')
        menu_name_item_text = ""
        for item in mirror_names:
            if item != "":
                cmds.menuItem(f"{item}_mi", label=item, parent='edit_mirror_name_om')
                menu_name_item_text += item + ";"
        cmds.setAttr(standard.guide_base+".mirrorNameList", menu_name_item_text, type='string')
        # verify if it is the first time to creation this instance or re-loading an existing guide:
        first_time = cmds.getAttr(standard.guide_base+".mirrorAxis")
        if first_time == "" or first_time == None:
            # set initial values to guide base:
            cmds.setAttr(standard.guide_base+".mirrorAxis", self.ar.data.mirror_menus[0], type='string')
            cmds.setAttr(standard.guide_base+".mirrorName", mirror_names[0], type='string')
        else:
            cmds.optionMenu('edit_mirror_om', edit=True, value=first_time) #initial mirror
            cmds.optionMenu('edit_mirror_name_om', edit=True, value=cmds.getAttr(standard.guide_base+".mirrorName")) #initial mirror name


    def rig_it_button(self, standard):
        cmds.button('edit_rig_it_bt', label="Rig", command=standard.rig_me, backgroundColor=(1.0, 1.0, 0.7), parent='edit_guide_mirror_rl')


    def degree_layout(self, standard):
        cmds.rowLayout('edit_guide_degree_rl', numberOfColumns=4, columnWidth4=(100, 100, 50, 20), columnAlign=[(1, 'right'), (3, 'left')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'left', 10), (4, 'both', 2)], parent="rig_selected_module_cl" )
        cmds.text('edit_guide_degree_txt', label=self.ar.data.lang['i119_curveDegree'], parent='edit_guide_degree_rl')
        cmds.optionMenu('edit_guide_curve_degree_om', label='', changeCommand=partial(self.change_curve_degree, standard), parent='edit_guide_degree_rl')
        for item in ['0 - Preset', '1 - Linear', '3 - Cubic']: #degreeMenuItemList
            cmds.menuItem(f"{item}_mi", label=item, parent='edit_guide_curve_degree_om')
        current_degree = cmds.getAttr(standard.guide_base+".degree")
        # set layout with the current value:
        if current_degree == 0:
            cmds.optionMenu('edit_guide_curve_degree_om', edit=True, value='0 - Preset')
        elif current_degree == 1:
            cmds.optionMenu('edit_guide_curve_degree_om', edit=True, value='1 - Linear')
        else:
            cmds.optionMenu('edit_guide_curve_degree_om', edit=True, value='3 - Cubic')


    def reorient_layout(self, standard):
        if 'reorient' in cmds.listAttr(standard.guide_base):
            cmds.button('edit_reorient_bt', label=self.ar.data.lang["m022_reOrient"], annotation=self.ar.data.lang["m023_reOrientDesc"], command=standard.reOrientGuideButton, backgroundColor=(0.5, 0.7, 0.8), parent="edit_guide_degree_rl")


    def style_layout(self, standard):
        if 'style' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_style_rl', numberOfColumns=4, columnWidth4=(100, 50, 50, 70), columnAlign=[(1, 'right'), (2, 'left'), (3, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (3, 'both', 10)], parent="rig_selected_module_cl")
            cmds.text('edit_guide_style_txt', label=self.ar.data.lang['m041_style'], visible=True, parent='edit_guide_style_rl')
            cmds.optionMenu('edit_guide_style_om', label='', changeCommand=standard.changeStyle, parent='edit_guide_style_rl')
            for item in [self.ar.data.lang['m042_default'], self.ar.data.lang['m026_biped'], self.ar.data.lang['m037_quadruped']]: #styleMenuItemList
                cmds.menuItem(f"{item}_mi", label=item, parent='edit_guide_style_om')
            # read from guide attribute the current value to style:
            current_style = cmds.getAttr(standard.guide_base+".style")
            cmds.optionMenu('edit_guide_style_om', edit=True, select=int(current_style+1))


    def type_layout(self, standard):
        if 'type' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_type_rl', numberOfColumns=4, columnWidth4=(100, 50, 77, 70), columnAlign=[(1, 'right'), (2, 'left'), (3, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (3, 'both', 10)], parent="rig_selected_module_cl")
            cmds.text('edit_guide_type_txt', label=self.ar.data.lang['m021_type'], parent='edit_guide_type_rl')
            cmds.optionMenu('edit_guide_type_om', label='', changeCommand=standard.changeType, parent='edit_guide_type_rl')
            for item in [self.ar.data.lang['m028_arm'], self.ar.data.lang['m030_leg']]: #typeMenuItemList
                cmds.menuItem(f"{item}_mi", label=item, parent='edit_guide_type_om')
            # read from guide attribute the current value to type:
            current_type = cmds.getAttr(standard.guide_base+".type")
            cmds.optionMenu('edit_guide_type_om', edit=True, select=int(current_type+1))


    def deformed_by_layout(self, standard):
        if 'deformedBy' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_deformed_by_rl', numberOfColumns=3, columnWidth3=(100, 170, 30), columnAlign=[(1, 'right'), (3, 'right')], adjustableColumn=3, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2)], parent="rig_selected_module_cl" )
            cmds.text('edit_guide_deformed_by_txt', label=self.ar.data.lang['i313_deformedBy'], parent='edit_guide_deformed_by_rl')
            cmds.optionMenu('edit_guide_deformed_by_om', label='', changeCommand=standard.change_deformed_by, parent='edit_guide_deformed_by_rl')
            for item in ['0 - None', '1 - Head Deformer', '2 - Jaw Deformer', '3 - Head and Jaw Deformers']: #deformedByMenuItemList
                cmds.menuItem(f"{item}_mi", label=item, parent='edit_guide_deformed_by_om')
            current_deformed_by_value = cmds.getAttr(standard.guide_base+".deformedBy")
            # set layout with the current value:
            if current_deformed_by_value == 1:
                cmds.optionMenu('edit_guide_deformed_by_om', edit=True, value='1 - Head Deformer')
            elif current_deformed_by_value == 2:
                cmds.optionMenu('edit_guide_deformed_by_om', edit=True, value='2 - Jaw Deformer')
            elif current_deformed_by_value == 3:
                cmds.optionMenu('edit_guide_deformed_by_om', edit=True, value='3 - Head and Jaw Deformers')
            else:
                cmds.optionMenu('edit_guide_deformed_by_om', edit=True, value='0 - None')


    def eye_aim_direction_layout(self, standard):
        if 'aimDirection' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_eye_aim_direction_rl', numberOfColumns=4, columnWidth4=(100, 50, 180, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text('edit_guide_eye_aim_direction_txt', label=self.ar.data.lang['i082_aimDirection'], parent='edit_guide_eye_aim_direction_rl')
            cmds.optionMenu('edit_guide_eye_aim_direction_om', label='', changeCommand=standard.changeAimDirection, parent='edit_guide_eye_aim_direction_rl')
            for item in standard.aimMenuItemList:
                cmds.menuItem(f"{item}_mi", label=item, parent='edit_guide_eye_aim_direction_om')
            cmds.optionMenu('edit_guide_eye_aim_direction_om', edit=True, value=standard.aimMenuItemList[cmds.getAttr(standard.guide_base+".aimDirection")])


    def indirectskin_layout(self, standard):
        if 'indirectSkin' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_indirectskin_rl', numberOfColumns=4, columnWidth4=(100, 150, 10, 40), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text(" ", parent='edit_guide_indirectskin_rl')
            cmds.checkBox('edit_guide_indirectskin_cb', label="Indirect Skinning", value=cmds.getAttr(standard.guide_base+".indirectSkin"), changeCommand=standard.changeIndirectSkin, parent='edit_guide_indirectskin_rl')
            cmds.text(" ", parent='edit_guide_indirectskin_rl')
            cmds.checkBox('edit_guide_indirectskin_holder_cb', label=self.ar.data.lang['c046_holder'], value=cmds.getAttr(standard.guide_base+".holder"), enable=False, changeCommand=partial(standard.set_guide_attr, 'holder'), parent='edit_guide_indirectskin_rl')
            cmds.rowLayout('edit_guide_indirectskin_sdk_locator_rl', numberOfColumns=4, columnWidth4=(100, 150, 10, 40), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text(" ", parent='edit_guide_indirectskin_sdk_locator_rl')
            cmds.text(" ", parent='edit_guide_indirectskin_sdk_locator_rl')
            cmds.text(" ", parent='edit_guide_indirectskin_sdk_locator_rl')
            cmds.checkBox('edit_guide_indirectskin_sdk_locator_cb', label="SDK Locator", value=cmds.getAttr(standard.guide_base+".sdkLocator"), enable=False, changeCommand=partial(standard.set_guide_attr, 'sdkLocator'), parent='edit_guide_indirectskin_sdk_locator_rl')
            standard.changeIndirectSkin(cmds.getAttr(standard.guide_base+".indirectSkin"))


    def eyelid_layout(self, standard):
        if 'eyelid' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_eyelid_rl', numberOfColumns=6, columnWidth6=(30, 75, 75, 80, 40, 60), columnAlign=[(1, 'right'), (2, 'left'), (6, 'right')], adjustableColumn=6, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'both', 2), (6, 'both', 2)], parent="rig_selected_module_cl")
            cmds.text(" ", parent='edit_guide_eyelid_rl')
            cmds.checkBox('edit_guide_eyelid_cb', label=self.ar.data.lang['i079_eyelid'], value=cmds.getAttr(standard.guide_base+".eyelid"), changeCommand=standard.changeEyelid, parent='edit_guide_eyelid_rl')
            cmds.checkBox('edit_guide_eyelid_pivot_cb', label=self.ar.data.lang['i283_pivot'], value=cmds.getAttr(standard.guide_base+".lidPivot"), changeCommand=standard.changeLidPivot, parent='edit_guide_eyelid_rl')
            cmds.checkBox('edit_guide_eyelid_specular_cb', label=self.ar.data.lang['i184_specular'], value=cmds.getAttr(standard.guide_base+".specular"), changeCommand=standard.changeSpecular, parent='edit_guide_eyelid_rl')
            cmds.checkBox('edit_guide_eyelid_iris_cb', label=self.ar.data.lang['i080_iris'], value=cmds.getAttr(standard.guide_base+".iris"), changeCommand=standard.changeIris, parent='edit_guide_eyelid_rl')
            cmds.checkBox('edit_guide_eyelid_pupil_cb', label=self.ar.data.lang['i081_pupil'], value=cmds.getAttr(standard.guide_base+".pupil"), changeCommand=standard.changePupil, parent='edit_guide_eyelid_rl')


    def geometry_layout(self, standard):
        if 'geo' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_geo_rl', numberOfColumns=3, columnWidth3=(100, 100, 70), columnAlign=[(1, 'right'), (3, 'right')], adjustableColumn=3, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2)], parent="rig_selected_module_cl" )
            cmds.button('edit_guide_geo_bt', label=self.ar.data.lang["m146_geo"]+" >", command=partial(self.load_geo, standard), parent='edit_guide_geo_rl')
            cmds.textField('edit_guide_geo_tf', text=cmds.getAttr(standard.guide_base+".geo"), enable=True, changeCommand=standard.changeGeo, parent='edit_guide_geo_rl')


    def start_frame_layout(self, standard):
        if 'startFrame' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_start_frame_rl', numberOfColumns=4, columnWidth4=(100, 60, 70, 40), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text('edit_guide_start_frame_txt', label=self.ar.data.lang["i169_startFrame"], parent='edit_guide_start_frame_rl')
            cmds.intField('edit_guide_start_frame_if', value=cmds.getAttr(standard.guide_base+".startFrame"), changeCommand=standard.set_start_frame, parent='edit_guide_start_frame_rl')


    def steering_layout(self, standard):
        if 'steering' in cmds.listAttr(standard.guide_base):
            if not 'startFrame' in cmds.listAttr(standard.guide_base):
                cmds.rowLayout('edit_guide_start_frame_rl', numberOfColumns=4, columnWidth4=(100, 60, 70, 40), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.checkBox('edit_guide_steering_cb', label=self.ar.data.lang['m158_steering'], value=cmds.getAttr(standard.guide_base+".steering"), changeCommand=standard.set_wheel_steering, parent='edit_guide_start_frame_rl')
            cmds.checkBox('edit_guide_show_ctrls_cb', label=self.ar.data.lang['i170_showControls'], value=cmds.getAttr(standard.guide_base+".showControls"), changeCommand=standard.changeShowControls, parent='edit_guide_start_frame_rl')


    def fatherb_layout(self, standard):
        if 'fatherB' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_fatherb_rl', numberOfColumns=3, columnWidth3=(100, 100, 70), columnAlign=[(1, 'right'), (3, 'right')], adjustableColumn=3, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2)], parent="rig_selected_module_cl" )
            cmds.button('edit_guide_fatherb_bt', label=self.ar.data.lang["m160_fatherB"]+" >", command=standard.loadFatherB, parent='edit_guide_fatherb_rl')
            cmds.textField('edit_guide_fatherb_tf', text=cmds.getAttr(standard.guide_base+".fatherB"), enable=True, changeCommand=standard.changeFatherB, parent='edit_guide_fatherb_rl')


    def head_items_layout(self, standard):
        if 'jaw' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_head_items_rl', numberOfColumns=5, columnWidth5=(30, 75, 75, 75, 75), columnAlign=[(1, 'right'), (2, 'left'), (3, 'left'), (4, 'left'), (5, 'right')], adjustableColumn=5, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'both', 2)], parent="rig_selected_module_cl")
            cmds.text(" ", parent='edit_guide_head_items_rl')
            cmds.checkBox('edit_guide_head_jaw_cb', label=self.ar.data.lang['c025_jaw'], value=cmds.getAttr(standard.guide_base+".jaw"), changeCommand=standard.changeJaw, parent='edit_guide_head_items_rl')
            cmds.checkBox('edit_guide_head_chin_cb', label=self.ar.data.lang['c026_chin'], value=cmds.getAttr(standard.guide_base+".chin"), changeCommand=standard.changeChin, enable=cmds.checkBox('edit_guide_head_jaw_cb', query=True, value=True), parent='edit_guide_head_items_rl')
            cmds.checkBox('edit_guide_head_lips_cb', label=self.ar.data.lang['c062_lips'], value=cmds.getAttr(standard.guide_base+".lips"), changeCommand=standard.changeLips, enable=cmds.checkBox('edit_guide_head_jaw_cb', query=True, value=True), parent='edit_guide_head_items_rl')
            cmds.checkBox('edit_guide_head_upperhead_cb', label=self.ar.data.lang['c044_upper']+" "+self.ar.data.lang['c024_head'], value=cmds.getAttr(standard.guide_base+".upperHead"), changeCommand=standard.changeUpperHead, parent='edit_guide_head_items_rl')


    def articulation_layout(self, standard):      
        if 'articulation' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_articulation_rl', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text('edit_guide_articulation_rl', label=self.ar.data.lang['m173_articulation'], parent='edit_guide_articulation_rl')
            cmds.checkBox('edit_guide_articulation_cb', label="", value=cmds.getAttr(standard.guide_base+".articulation"), changeCommand=standard.changeArticulation, parent='edit_guide_articulation_rl')


    def nostril_layout(self, standard):
        if 'nostril' in cmds.listAttr(standard.guide_base):
            cmds.text(" ", parent='edit_guide_articulation_rl')
            self.nostrilCB = cmds.checkBox(label=self.ar.data.lang['m079_nostril'], value=cmds.getAttr(standard.guide_base+".nostril"), changeCommand=standard.changeNostril, parent='edit_guide_articulation_rl')


    def corrective_layout(self, standard):
        if 'corrective' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_corrective_rl', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text('edit_guide_corrective_txt', label=self.ar.data.lang['c124_corrective'].capitalize(), parent='edit_guide_corrective_rl')
            cmds.checkBox('edit_guide_corrective_cb', label="", value=cmds.getAttr(standard.guide_base+".corrective"), changeCommand=partial(standard.set_guide_attr, 'corrective'), parent='edit_guide_corrective_rl')
            if 'articulation' in cmds.listAttr(standard.guide_base):
                cmds.text('edit_guide_corrective_txt', edit=True, enable=cmds.getAttr(standard.guide_base+".articulation"))
                cmds.checkBox('edit_guide_corrective_cb', edit=True, enable=cmds.getAttr(standard.guide_base+".articulation"))


    def dynamic_layout(self, standard):
        if 'dynamic' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_dynamic_rl', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text('edit_guide_dynamic_txt', label=self.ar.data.lang['m097_dynamic'], parent='edit_guide_dynamic_rl')
            cmds.checkBox('edit_guide_dynamic_cb', label="", value=cmds.getAttr(standard.guide_base+".dynamic"), changeCommand=partial(standard.set_guide_attr, 'dynamic'), parent='edit_guide_dynamic_rl')


    def main_ctrl_layout(self, standard):
        if 'nJoints' in cmds.listAttr(standard.guide_base):
            if 'mainControls' in cmds.listAttr(standard.guide_base):
                if cmds.getAttr(standard.guide_base+".nJoints") > 0:
                    cmds.rowLayout('edit_guide_main_ctrl_rl', numberOfColumns=2, columnWidth2=(100, 100), columnAlign=[(1, 'right'), (2, 'left')], adjustableColumn=2, columnAttach=[(1, 'right', 2), (2, 'left', 2)], parent="rig_selected_module_cl" )
                    if cmds.getAttr(standard.guide_base+".nJoints") > 1:
                        cmds.checkBox('edit_guide_main_ctrl_cb', label=self.ar.data.lang['m227_mainCtrls'], value=cmds.getAttr(standard.guide_base+".mainControls"), enable=True, changeCommand=standard.set_main_ctrls, parent='edit_guide_main_ctrl_rl')
                        cmds.intField('edit_guide_main_ctrl_if', value=cmds.getAttr(standard.guide_base+".nMain"), minValue=1, changeCommand=partial(standard.change_main_ctrls_number, 0), editable=cmds.getAttr(standard.guide_base+".mainControls"), parent='edit_guide_main_ctrl_rl')
                    else:
                        cmds.checkBox('edit_guide_main_ctrl_cb', label=self.ar.data.lang['m227_mainCtrls'], value=False, enable=True, changeCommand=standard.set_main_ctrls, parent='edit_guide_main_ctrl_rl')
                        cmds.intField('edit_guide_main_ctrl_if', value=cmds.getAttr(standard.guide_base+".nMain"), minValue=1, changeCommand=partial(standard.change_main_ctrls_number, 0), editable=False, parent='edit_guide_main_ctrl_rl')
                        cmds.setAttr(standard.guide_base+".mainControls", 0)


    def deformer_layout(self, standard):
        if 'deformer' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_deformer_rl', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text('edit_guide_deformer_txt', label=self.ar.data.lang['c097_deformer'].capitalize(), enable=cmds.getAttr(standard.guide_base+".upperHead"), parent='edit_guide_deformer_rl')
            cmds.checkBox('edit_guide_deformer_cb', label="", value=cmds.getAttr(standard.guide_base+".deformer"), changeCommand=standard.changeDeformer, enable=cmds.getAttr(standard.guide_base+".upperHead"), parent='edit_guide_deformer_rl')


    def facial_layout(self, standard):
        if 'facial' in cmds.listAttr(standard.guide_base):
            facial_enable_value = True
            if not cmds.getAttr(standard.guide_base+".jaw") or not cmds.getAttr(standard.guide_base+".chin") or not cmds.getAttr(standard.guide_base+".lips") or not cmds.getAttr(standard.guide_base+".upperHead"):
                facial_enable_value=False
            cmds.rowLayout('edit_guide_facial_rl', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text('edit_guide_facial_txt', label=self.ar.data.lang['c059_facial'].capitalize(), enable=facial_enable_value, parent='edit_guide_facial_rl')
            facial_value = cmds.getAttr(standard.guide_base+".facial")
            cmds.checkBox('edit_guide_facial_cb', label="", value=facial_value, changeCommand=standard.changeFacial, enable=facial_enable_value, parent='edit_guide_facial_rl') #facial
            collapsed = False
            if not facial_value:
                collapsed = True
            # facial frame layout
            cmds.frameLayout("edit_guide_facial_fl", label=self.ar.data.lang['m139_facialCtrlsAttr'], collapsable=True, collapse=collapsed, enable=facial_value, parent="rig_selected_module_cl")
            cmds.rowColumnLayout('edit_guide_facial_rcl', numberOfColumns=2, columnWidth=[(1, 70), (2, 300)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 20)], parent='edit_guide_facial_fl')
            # facial element checkboxes
            cmds.checkBox('edit_guide_facial_brow_cb', label=self.ar.data.lang["c060_brow"], value=cmds.getAttr(standard.guide_base+".facialBrow"), changeCommand=partial(standard.changeFacialElement, "facialBrow"), parent='edit_guide_facial_rcl')
            cmds.text('edit_guide_facial_brow_txt', label=', '.join(self.ar.data.facial_brow_targets), parent='edit_guide_facial_rcl')
            cmds.checkBox('edit_guide_facial_eyelid_cb', label=self.ar.data.lang["c042_eyelid"], value=cmds.getAttr(standard.guide_base+".facialEyelid"), changeCommand=partial(standard.changeFacialElement, "facialEyelid"), parent='edit_guide_facial_rcl')
            cmds.text('edit_guide_facial_eyelid_txt', label=', '.join(self.ar.data.facial_eyelid_targets[2:]), parent='edit_guide_facial_rcl')
            cmds.checkBox('edit_guide_facial_mouth_cb', label=self.ar.data.lang["c061_mouth"], value=cmds.getAttr(standard.guide_base+".facialMouth"), changeCommand=partial(standard.changeFacialElement, "facialMouth"), parent='edit_guide_facial_rcl')
            cmds.text('edit_guide_facial_mouth_txt', label=', '.join(self.ar.data.facial_mouth_targets), parent='edit_guide_facial_rcl')
            cmds.checkBox('edit_guide_facial_lips_cb', label=self.ar.data.lang["c062_lips"], value=cmds.getAttr(standard.guide_base+".facialLips"), changeCommand=partial(standard.changeFacialElement, "facialLips"), parent='edit_guide_facial_rcl')
            cmds.text('edit_guide_facial_lips_txt', label=', '.join(self.ar.data.facial_lips_targets), parent='edit_guide_facial_rcl')
            cmds.checkBox('edit_guide_facial_sneer_cb', label=self.ar.data.lang["c063_sneer"], value=cmds.getAttr(standard.guide_base+".facialSneer"), changeCommand=partial(standard.changeFacialElement, "facialSneer"), parent='edit_guide_facial_rcl')
            cmds.text('edit_guide_facial_sneer_txt', label=', '.join([item for item in self.ar.data.facial_sneer_targets if item is not None]), parent='edit_guide_facial_rcl')
            cmds.checkBox('edit_guide_facial_grimace_cb', label=self.ar.data.lang["c064_grimace"], value=cmds.getAttr(standard.guide_base+".facialGrimace"), changeCommand=partial(standard.changeFacialElement, "facialGrimace"), parent='edit_guide_facial_rcl')
            cmds.text('edit_guide_facial_grimace_txt', label=', '.join([item for item in self.ar.data.facial_grimace_targets if item is not None]), parent='edit_guide_facial_rcl')
            cmds.checkBox('edit_guide_facial_face_cb', label=self.ar.data.lang["c065_face"], value=cmds.getAttr(standard.guide_base+".facialFace"), changeCommand=partial(standard.changeFacialElement, "facialFace"), parent='edit_guide_facial_rcl')
            cmds.text('edit_guide_facial_face_txt', label=', '.join(self.ar.data.facial_face_targets), parent='edit_guide_facial_rcl')
            cmds.separator(style='none', height=5, parent='edit_guide_facial_rcl')
            cmds.columnLayout('edit_guide_facial_type_cl', parent="edit_guide_facial_fl")
            current_type = cmds.getAttr(standard.guide_base+".connectUserType")
            cmds.radioCollection('edit_guide_facial_type_rc', parent='edit_guide_facial_type_cl')
            cmds.radioButton('edit_guide_facial_type_bs_rb', label=self.ar.data.lang['m170_blendShapes']+" - "+self.ar.data.lang['i185_animation']+": #_Recept_BS", annotation=standard.bsType, onCommand=standard.dpChangeType)
            cmds.radioButton('edit_guide_facial_type_jnt_rb', label=self.ar.data.lang['i181_facialJoint']+" - "+self.ar.data.lang['i186_gaming'], annotation=self.jointsType, onCommand=standard.dpChangeType)
            cmds.radioCollection('edit_guide_facial_type_rc', edit=True, select='edit_guide_facial_type_bs_rb')
            if current_type:
                cmds.radioCollection('edit_guide_facial_type_rc', edit=True, select='edit_guide_facial_type_jnt_rb')


    def bend_layout(self, standard):
        if 'hasBend' in cmds.listAttr(standard.guide_base):
            cmds.rowColumnLayout('edit_guide_bend_rcl', numberOfColumns=2, columnWidth=[(1, 260), (2, 80)], columnSpacing=[(1, 2), (2, 10)], parent="rig_selected_module_cl")
            cmds.rowLayout('edit_guide_bend_rl', numberOfColumns=4, columnWidth4=(100, 20, 50, 20), columnAlign=[(1, 'right'), (2, 'left'), (3, 'left'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (4, 'both', 10)], parent='edit_guide_bend_rcl')
            cmds.text('edit_guide_bend_txt', label=self.ar.data.lang['m044_addBend'], visible=True, parent='edit_guide_bend_rl')
            cmds.checkBox('edit_guide_bend_cb', value=standard.getHasBend(), label=' ', changeCommand=standard.changeBend, parent='edit_guide_bend_rl')
            cmds.optionMenu('edit_guide_bend_num_om', label='Ribbon Joints', changeCommand=standard.changeNumBend, enable=standard.getHasBend(), parent='edit_guide_bend_rl')
            bend_num_menus = [3, 5, 7]
            for item in bend_num_menus:
                cmds.menuItem(f"{item}_mi", label=item, parent='edit_guide_bend_num_om')
            for i, item in enumerate(bend_num_menus):
                if item == cmds.getAttr(standard.guide_base+".numBendJoints"):
                    cmds.optionMenu('edit_guide_bend_num_om', edit=True, select=i+1)
                    break
            # additional ribbon joint:
            cmds.checkBox("edit_guide_additional_cb", label=self.ar.data.lang['m180_additional'], value=cmds.getAttr(standard.guide_base+".additional"), changeCommand=partial(standard.set_guide_attr, 'additional'), parent='edit_guide_bend_rcl')
        
                

    
    def align_world_layout(self, standard):
        if 'alignWorld' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_align_world_rl', numberOfColumns=4, columnWidth4=(100, 20, 50, 20), columnAlign=[(1, 'right'), (2, 'left'), (3, 'left'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (4, 'both', 10)], parent="rig_selected_module_cl")
            cmds.text('edit_guide_align_world_txt', label=self.ar.data.lang['m080_alignWorld'], visible=True, parent='edit_guide_align_world_rl')
            cmds.checkBox('edit_guide_align_world_cb', value=cmds.getAttr(standard.guide_base+'.alignWorld'), label=' ', changeCommand=partial(standard.set_guide_attr, 'alignWorld'), parent='edit_guide_align_world_rl')
    
    
    def change_corrective(self, standard, value, *args):
        cmds.text('edit_guide_corrective_txt', edit=True, enable=value)
        cmds.checkBox('edit_guide_corrective_cb', edit=True, enable=value)
        if not value:
            cmds.checkBox('edit_guide_corrective_cb', edit=True, value=value)
            cmds.setAttr(standard.guide_base+".corrective", value)
    

    def change_curve_degree(self, standard, item, *args):
        """ This function receives the degree menu name item string and set it as a int in the guide base (main).
        """
        if standard.check_guide_integrity():
            if item == '3 - Cubic':
                cmds.setAttr(standard.guide_base+".degree", 3)
            else:
                cmds.setAttr(standard.guide_base+".degree", 1)
    

    def change_indirectskin_ui(self, value):
        if value == 0:
            cmds.checkBox('edit_guide_indirectskin_holder_cb', edit=True, value=False, enable=False)
            cmds.checkBox('edit_guide_indirectskin_sdk_locator_cb', edit=True,  value=False, enable=False)
        else:
            cmds.checkBox('edit_guide_indirectskin_holder_cb', edit=True, enable=True)
            cmds.checkBox('edit_guide_indirectskin_sdk_locator_cb', edit=True, enable=True)


    


    def plus_info_ui(self, instance=None, *args):
        """ Open plus info attributes to each module
        """
        # declaring variables:
        win_width  = 250
        win_height = 180
        width_size = (0.8*win_width)
        # creating Plus Info Window:
        self.ar.utils.close_ui(self.ar.data.color_override_win_name)
        if cmds.window(self.ar.data.plus_info_win_name, query=True, exists=True):
            cmds.deleteUI('plus_fl')
        else:
            cmds.window(self.ar.data.plus_info_win_name, title='dpAutoRig - '+self.ar.data.lang['i205_guide']+" "+self.ar.data.lang['i013_info'], iconName='dpPlus', widthHeight=(win_width, win_height), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
        cmds.formLayout('plus_fl', numberOfDivisions=100, parent=self.ar.data.plus_info_win_name)
        cmds.scrollLayout('plus_sl', parent='plus_fl')
        cmds.formLayout('plus_fl', edit=True, attachForm=(('plus_sl', 'bottom', 10), ('plus_sl', 'top', 10), ('plus_sl', 'left', 10), ('plus_sl', 'right', 10)))
        # get selected module guides
        guide_instances = self.ar.job.selected_instances.copy()
        if not guide_instances:
            guide_instances = [instance]
        if instance:
            if not instance in guide_instances:
                guide_instances.insert(0, instance)
        for standard in guide_instances:
            guide_name = standard.guide_namespace.split("__")[-1]
            custom_name = cmds.getAttr(standard.guide_base+".customName")
            if not custom_name:
                custom_name = ""
            # creating text layout:
            cmds.separator(style='none', height=10, parent='plus_sl')
            cmds.rowColumnLayout(f"{standard.number_name}_plus_header_rcl", numberOfColumns=2, adjustableColumn=2, columnWidth=[(1, 55), (2, 150)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 10)], parent='plus_sl')
            cmds.text(f"{standard.number_name}_plus_header_guide_txt", label=guide_name, align='left', parent=f"{standard.number_name}_plus_header_rcl")
            cmds.text(f"{standard.number_name}_plus_header_custom_txt", label=custom_name, align='left', font='boldLabelFont', parent=f"{standard.number_name}_plus_header_rcl")
            cmds.separator(style='none', height=10, parent='plus_sl')
            cmds.checkBox(f"{standard.number_name}_plus_annotation_cb", label=self.ar.data.lang['m014_annotation'], annotation=self.ar.data.lang['m014_annotation'], value=cmds.getAttr(standard.guide_base+'.displayAnnotation'), onCommand=partial(standard.displayAnnotation, 1), offCommand=partial(standard.displayAnnotation, 0), parent='plus_sl')
            cmds.separator(style='none', height=5, parent='plus_sl')
            cmds.floatSliderGrp(f"{standard.number_name}_plus_radius_size_fsg", label=self.ar.data.lang['c067_radius'].capitalize(), field=True, width=width_size, minValue=0.001, maxValue=10.0, fieldMinValue=0.001, fieldMaxValue=100.0, precision=2, value=cmds.getAttr(standard.radius_ctrl+".translateX"), changeCommand=standard.change_radius_size, dragCommand=standard.change_radius_size, columnWidth=[(1, 55), (2, 60), (3, 30)], parent='plus_sl')
            cmds.separator(style='none', height=5, parent='plus_sl')
            cmds.floatSliderGrp(f"{standard.number_name}_plus_shape_size_fsg", label=self.ar.data.lang['m067_shape']+" "+self.ar.data.lang['i115_size'], width=width_size, field=True, minValue=0.001, maxValue=10.0, fieldMinValue=0.001, fieldMaxValue=100.0, precision=2, value=cmds.getAttr(standard.guide_base+'.shapeSize'), changeCommand=partial(standard.set_guide_attr, 'shapeSize'), dragCommand=partial(standard.set_guide_attr, 'shapeSize'), columnWidth=[(1, 55), (2, 60), (3, 30)], parent='plus_sl')
            cmds.separator(style='none', height=10, parent='plus_sl')
            cmds.button(f"{standard.number_name}_plus_color_bt", label=self.ar.data.lang['m013_color'], annotation=self.ar.data.lang['m013_color'], width=width_size, align="center", command=partial(self.ar.ctrls.colorizeUI, standard), backgroundColor=self.ar.ctrls.getGuideRGBColorList(standard), parent='plus_sl')
            cmds.separator(style='none', height=5, parent='plus_sl')
            cmds.separator(style='in', height=10, width=width_size, parent='plus_sl')
        # call Info Window:
        cmds.showWindow(self.ar.data.plus_info_win_name)


    def delete_module_layout(self):
        if self.ar.data.ui_state:
            if cmds.frameLayout("rig_edit_selected_module_fl", query=True, exists=True):
                cmds.frameLayout("rig_edit_selected_module_fl", edit=True, label=self.ar.data.lang['i011_editSelected']+" "+self.ar.data.lang['i143_module'])
            if cmds.columnLayout("rig_selected_module_cl", query=True, exists=True):
                cmds.deleteUI("rig_selected_module_cl")


    def enable_main_ctrls(self, standard, value, *args):
        """ Just enable or disable the main controllers int field UI.
        """
        if self.ar.data.ui_state:
            cmds.intField('edit_guide_main_ctrl_if', edit=True, editable=value)
            cmds.checkBox('edit_guide_main_ctrl_cb', edit=True, editable=True)


    def load_geo(self, standard, *args):
        """ Loads the selected node to geoTextField in selectedModuleLayout.
        """
        is_geo = False
        selected_items = cmds.ls(selection=True)
        if selected_items:
            if cmds.objExists(selected_items[0]):
                for item in cmds.listRelatives(selected_items[0], children=True, allDescendents=True) or []:
                    item_type = cmds.objectType(item)
                    if item_type == "mesh" or item_type == "nurbsSurface":
                        is_geo = True
        if is_geo:
            cmds.textField('edit_guide_geo_tf', edit=True, text=selected_items[0])
            cmds.setAttr(standard.guide_base+".geo", selected_items[0], type='string')


    def update_select_button(self, selected_guides):
            selected_instances = []
            for m, instance in enumerate(self.ar.data.guide_instances):
                if cmds.objExists(instance.guide_base):
                    if cmds.button(f"{instance.number_name}_select_bt", query=True, exists=True):
                        current_colors = self.ar.ctrls.getGuideRGBColorList(instance)
                        if current_colors:
                            cmds.button(f"{instance.number_name}_select_bt", edit=True, label=" ", backgroundColor=current_colors)
                        if selected_guides:
                            for selected_guide in selected_guides:
                                if str(instance) == cmds.getAttr(selected_guide+"."+self.ar.data.module_instance_info_attr):
                                    cmds.button(f"{instance.number_name}_select_bt", edit=True, label="S", backgroundColor=(1.0, 1.0, 1.0))
                                    selected_instances.append(instance)
            return selected_instances
    
    
    def select_button_callback(self, standard, dragControl, x, y, modifiers):
        """ Add mouse middle click functions.
        """
        selection = cmds.ls(selection=True)
        if modifiers == 0: #middle mouse drag
            selection = [standard.guide_base]
        elif modifiers == 1: #middle mouse drag + shift
            if not standard.guide_base in selection:
                selection.append(standard.guide_base)
        elif modifiers == 2: #middle drag + control
            if standard.guide_base in selection:
                selection.remove(standard.guide_base)
        cmds.select(selection)
        cmds.button(f"{standard.number_name}_select_bt", edit=True, label="S", backgroundColor=(1.0, 1.0, 1.0))
