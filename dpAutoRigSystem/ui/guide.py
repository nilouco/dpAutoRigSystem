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
        cmds.iconTextButton(image=self.ar.data.icon['plus_info'], height=30, width=17, style='iconOnly', command=partial(self.plusInfoWin, standard), parent=f"{standard.number_name}_rl")
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
                    self.plusInfoWin(standard)


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
                cmds.intField(f"{standard.number_name}_n_joints_if", value=cmds.getAttr(standard.guide_base+".nJoints"), minValue=1, changeCommand=partial(standard.changeJointNumber, 0), parent='edit_seg_del_dup_rl')
            else:
                cmds.intField(f"{standard.number_name}_n_joints_if", value=cmds.getAttr(standard.guide_base+".nJoints"), minValue=0, editable=False, parent='edit_seg_del_dup_rl')
        else:
            cmds.text(" ", parent='edit_seg_del_dup_rl')
            cmds.text(" ", parent='edit_seg_del_dup_rl')


    def delete_duplicate_button(self, standard):
        cmds.button('edit_delete_bt', label=self.ar.data.lang['m005_delete'], command=standard.delete_guide, backgroundColor=(1.0, 0.7, 0.7), parent='edit_seg_del_dup_rl')
        cmds.button('edit_duplicate_bt', label=self.ar.data.lang['m070_duplicate'], command=standard.duplicate_guide, backgroundColor=(0.7, 0.6, 0.8), annotation=self.ar.data.lang['i068_CtrlD'], parent='edit_seg_del_dup_rl')


    def flip_layout(self, standard):
        # create a flip layout:
        if 'flip' in cmds.listAttr(standard.guide_base):
            cmds.checkBox('edit_guide_flip', label="Flip", value=cmds.getAttr(standard.guide_base+".flip"), changeCommand=standard.changeFlip, parent='edit_guide_mirror_rl')
            if standard.check_father_mirror():
                if standard.father_flip_exists:
                    cmds.checkBox(self.flipCB, edit=True, enable=False)
        else:
            cmds.text("", parent='edit_guide_mirror_rl')


    def mirror_layout(self, standard):
        cmds.text(self.ar.data.lang['m010_mirror'], parent='edit_guide_mirror_rl')
        cmds.optionMenu("edit_mirror_om", label='', changeCommand=standard.changeMirror, parent='edit_guide_mirror_rl')
        for item in self.ar.data.mirror_menus:
            cmds.menuItem(label=item, parent='edit_mirror_om')
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
                cmds.menuItem(label=item, parent='edit_mirror_name_om')
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
        cmds.text(self.ar.data.lang['i119_curveDegree'], parent='edit_guide_degree_rl')
        cmds.optionMenu(f"{standard.number_name}_curve_degree_om", label='', changeCommand=partial(self.change_curve_degree, standard), parent='edit_guide_degree_rl')
        self.degreeMenuItemList = ['0 - Preset', '1 - Linear', '3 - Cubic']
        for item in self.degreeMenuItemList:
            cmds.menuItem(label=item, parent=f"{standard.number_name}_curve_degree_om")
        currentDegree = cmds.getAttr(standard.guide_base+".degree")
        # set layout with the current value:
        if currentDegree == 0:
            cmds.optionMenu(f"{standard.number_name}_curve_degree_om", edit=True, value='0 - Preset')
        elif currentDegree == 1:
            cmds.optionMenu(f"{standard.number_name}_curve_degree_om", edit=True, value='1 - Linear')
        else:
            cmds.optionMenu(f"{standard.number_name}_curve_degree_om", edit=True, value='3 - Cubic')


    def reorient_layout(self, standard):
        if 'reorient' in cmds.listAttr(standard.guide_base):
            cmds.button('edit_reorient_bt', label=self.ar.data.lang["m022_reOrient"], annotation=self.ar.data.lang["m023_reOrientDesc"], command=standard.reOrientGuideButton, backgroundColor=(0.5, 0.7, 0.8), parent="edit_guide_degree_rl")


    def style_layout(self, standard):
        if 'style' in cmds.listAttr(standard.guide_base):
            self.styleLayout = cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 50, 50, 70), columnAlign=[(1, 'right'), (2, 'left'), (3, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (3, 'both', 10)], parent="rig_selected_module_cl")
            cmds.text(label=self.ar.data.lang['m041_style'], visible=True, parent=self.styleLayout)
            self.styleMenu = cmds.optionMenu("styleMenu", label='', changeCommand=standard.changeStyle, parent=self.styleLayout)
            styleMenuItemList = [self.ar.data.lang['m042_default'], self.ar.data.lang['m026_biped'], self.ar.data.lang['m037_quadruped']]
            for item in styleMenuItemList:
                cmds.menuItem(label=item, parent=self.styleMenu)
            # read from guide attribute the current value to style:
            currentStyle = cmds.getAttr(standard.guide_base+".style")
            cmds.optionMenu(self.styleMenu, edit=True, select=int(currentStyle+1))


    def type_layout(self, standard):
        if 'type' in cmds.listAttr(standard.guide_base):
            self.typeLayout = cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 50, 77, 70), columnAlign=[(1, 'right'), (2, 'left'), (3, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (3, 'both', 10)], parent="rig_selected_module_cl")
            cmds.text(self.ar.data.lang['m021_type'], parent=self.typeLayout)
            self.typeMenu = cmds.optionMenu("typeMenu", label='', changeCommand=standard.changeType, parent=self.typeLayout)
            typeMenuItemList = [self.ar.data.lang['m028_arm'], self.ar.data.lang['m030_leg']]
            for item in typeMenuItemList:
                cmds.menuItem(label=item, parent=self.typeMenu)
            # read from guide attribute the current value to type:
            currentType = cmds.getAttr(standard.guide_base+".type")
            cmds.optionMenu(self.typeMenu, edit=True, select=int(currentType+1))


    def deformed_by_layout(self, standard):
        if 'deformedBy' in cmds.listAttr(standard.guide_base):
            self.deformedByLayout = cmds.rowLayout('deformedByLayout', numberOfColumns=3, columnWidth3=(100, 170, 30), columnAlign=[(1, 'right'), (3, 'right')], adjustableColumn=3, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2)], parent="rig_selected_module_cl" )
            cmds.text(self.ar.data.lang['i313_deformedBy'], parent=self.deformedByLayout)
            cmds.optionMenu(f"{standard.number_name}_deformed_by_om", label='', changeCommand=partial(self.changeDeformedBy, standard), parent=self.deformedByLayout)
            self.deformedByMenuItemList = ['0 - None', '1 - Head Deformer', '2 - Jaw Deformer', '3 - Head and Jaw Deformers']
            for item in self.deformedByMenuItemList:
                cmds.menuItem(label=item, parent=f"{standard.number_name}_deformed_by_om")
            currentDeformedByValue = cmds.getAttr(standard.guide_base+".deformedBy")
            # set layout with the current value:
            if currentDeformedByValue == 1:
                cmds.optionMenu(f"{standard.number_name}_deformed_by_om", edit=True, value='1 - Head Deformer')
            elif currentDeformedByValue == 2:
                cmds.optionMenu(f"{standard.number_name}_deformed_by_om", edit=True, value='2 - Jaw Deformer')
            elif currentDeformedByValue == 3:
                cmds.optionMenu(f"{standard.number_name}_deformed_by_om", edit=True, value='3 - Head and Jaw Deformers')
            else:
                cmds.optionMenu(f"{standard.number_name}_deformed_by_om", edit=True, value='0 - None')

                
    def eye_aim_direction_layout(self, standard):
        if 'aimDirection' in cmds.listAttr(standard.guide_base):
            self.aimDirectionLayout = cmds.rowLayout('aimDirectionLayout', numberOfColumns=4, columnWidth4=(100, 50, 180, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text(self.ar.data.lang['i082_aimDirection'], parent=self.aimDirectionLayout)
            self.aimMenu = cmds.optionMenu("aimMenu", label='', changeCommand=standard.changeAimDirection, parent=self.aimDirectionLayout)
            for item in standard.aimMenuItemList:
                cmds.menuItem(label=item, parent=self.aimMenu)
            currentAimDirection = cmds.getAttr(standard.guide_base+".aimDirection")
            # set layout with the current value:
            cmds.optionMenu(self.aimMenu, edit=True, value=standard.aimMenuItemList[currentAimDirection])


    def indirectskin_layout(self, standard):
        if 'indirectSkin' in cmds.listAttr(standard.guide_base):
            self.indirectSkinLayout = cmds.rowLayout('indirectSkinLayout', numberOfColumns=4, columnWidth4=(100, 150, 10, 40), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text(" ", parent=self.indirectSkinLayout)
            indirectSkinValue = cmds.getAttr(standard.guide_base+".indirectSkin")
            self.indirectSkinCB = cmds.checkBox(label="Indirect Skinning", value=indirectSkinValue, changeCommand=standard.changeIndirectSkin, parent=self.indirectSkinLayout)
            cmds.text(" ", parent=self.indirectSkinLayout)
            holderValue = cmds.getAttr(standard.guide_base+".holder")
            self.holderCB = cmds.checkBox(label=self.ar.data.lang['c046_holder'], value=holderValue, enable=False, changeCommand=standard.changeHolder, parent=self.indirectSkinLayout)
            self.sdkLocatorLayout = cmds.rowLayout('sdkLocatorLayout', numberOfColumns=4, columnWidth4=(100, 150, 10, 40), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text(" ", parent=self.sdkLocatorLayout)
            cmds.text(" ", parent=self.sdkLocatorLayout)
            cmds.text(" ", parent=self.sdkLocatorLayout)
            sdkLocatorValue = cmds.getAttr(standard.guide_base+".sdkLocator")
            self.sdkLocatorCB = cmds.checkBox(label="SDK Locator", value=sdkLocatorValue, enable=False, changeCommand=standard.changeSDKLocator, parent=self.sdkLocatorLayout)
            standard.changeIndirectSkin()


    def eyelid_layout(self, standard):
        if 'eyelid' in cmds.listAttr(standard.guide_base):
            self.eyelidLayout = cmds.rowLayout('eyelidLayout', numberOfColumns=6, columnWidth6=(30, 75, 75, 80, 40, 60), columnAlign=[(1, 'right'), (2, 'left'), (6, 'right')], adjustableColumn=6, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'both', 2), (6, 'both', 2)], parent="rig_selected_module_cl")
            cmds.text(" ", parent=self.eyelidLayout)
            self.eyelidCB = cmds.checkBox(label=self.ar.data.lang['i079_eyelid'], value=cmds.getAttr(standard.guide_base+".eyelid"), changeCommand=standard.changeEyelid, parent=self.eyelidLayout)
            self.lidPivotCB = cmds.checkBox(label=self.ar.data.lang['i283_pivot'], value=cmds.getAttr(standard.guide_base+".lidPivot"), changeCommand=standard.changeLidPivot, parent=self.eyelidLayout)
            self.specCB = cmds.checkBox(label=self.ar.data.lang['i184_specular'], value=cmds.getAttr(standard.guide_base+".specular"), changeCommand=standard.changeSpecular, parent=self.eyelidLayout)
            self.irisCB = cmds.checkBox(label=self.ar.data.lang['i080_iris'], value=cmds.getAttr(standard.guide_base+".iris"), changeCommand=standard.changeIris, parent=self.eyelidLayout)
            self.pupilCB = cmds.checkBox(label=self.ar.data.lang['i081_pupil'], value=cmds.getAttr(standard.guide_base+".pupil"), changeCommand=standard.changePupil, parent=self.eyelidLayout)


    def geometry_layout(self, standard):
        if 'geo' in cmds.listAttr(standard.guide_base):
            self.geoColumn = cmds.rowLayout('geoColumn', numberOfColumns=3, columnWidth3=(100, 100, 70), columnAlign=[(1, 'right'), (3, 'right')], adjustableColumn=3, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2)], parent="rig_selected_module_cl" )
            cmds.button(label=self.ar.data.lang["m146_geo"]+" >", command=partial(self.load_geo, standard), parent=self.geoColumn)
            self.geoTF = cmds.textField('geoTF', text='', enable=True, changeCommand=standard.changeGeo, parent=self.geoColumn)
            currentGeo = cmds.getAttr(standard.guide_base+".geo")
            if currentGeo:
                cmds.textField(self.geoTF, edit=True, text=currentGeo, parent=self.geoColumn)


    def start_frame_layout(self, standard):
        if 'startFrame' in cmds.listAttr(standard.guide_base):
            self.startFrameColumn = cmds.rowLayout('startFrameColumn', numberOfColumns=4, columnWidth4=(100, 60, 70, 40), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text(self.ar.data.lang["i169_startFrame"], parent=self.startFrameColumn)
            cmds.intField(f"{standard.number_name}_start_frame_if", value=cmds.getAttr(standard.guide_base+".startFrame"), changeCommand=standard.set_start_frame, parent=self.startFrameColumn)


    def steering_layout(self, standard):
        if 'steering' in cmds.listAttr(standard.guide_base):
            if 'startFrame' in cmds.listAttr(standard.guide_base):
                self.wheelLayout = self.startFrameColumn
            else:
                self.wheelLayout = cmds.rowLayout('wheelLayout', numberOfColumns=4, columnWidth4=(100, 60, 70, 40), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            steeringValue = cmds.getAttr(standard.guide_base+".steering")
            cmds.checkBox(f"{standard.number_name}_steering_cb", label=self.ar.data.lang['m158_steering'], value=steeringValue, changeCommand=standard.set_wheel_steering, parent=self.wheelLayout)
            showControlsValue = cmds.getAttr(standard.guide_base+".showControls")
            self.showControlsCB = cmds.checkBox(label=self.ar.data.lang['i170_showControls'], value=showControlsValue, changeCommand=standard.changeShowControls, parent=self.wheelLayout)


    def fatherb_layout(self, standard):
        if 'fatherB' in cmds.listAttr(standard.guide_base):
            self.fatherBColumn = cmds.rowLayout('fatherBColumn', numberOfColumns=3, columnWidth3=(100, 100, 70), columnAlign=[(1, 'right'), (3, 'right')], adjustableColumn=3, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2)], parent="rig_selected_module_cl" )
            cmds.button(label=self.ar.data.lang["m160_fatherB"]+" >", command=self.loadFatherB, parent=self.fatherBColumn)
            self.fatherBTF = cmds.textField('fatherBTF', text='', enable=True, changeCommand=standard.changeFatherB, parent=self.fatherBColumn)
            currentFatherB = cmds.getAttr(standard.guide_base+".fatherB")
            if currentFatherB:
                cmds.textField(self.fatherBTF, edit=True, text=currentFatherB, parent=self.fatherBColumn)


    def head_items_layout(self, standard):
        if 'jaw' in cmds.listAttr(standard.guide_base):
            self.headItemsLayout = cmds.rowLayout('headItemsLayout', numberOfColumns=5, columnWidth5=(30, 75, 75, 75, 75), columnAlign=[(1, 'right'), (2, 'left'), (3, 'left'), (4, 'left'), (5, 'right')], adjustableColumn=5, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'both', 2)], parent="rig_selected_module_cl")
            cmds.text(" ", parent=self.headItemsLayout)
            self.jawCB = cmds.checkBox(label=self.ar.data.lang['c025_jaw'], value=cmds.getAttr(standard.guide_base+".jaw"), changeCommand=standard.changeJaw, parent=self.headItemsLayout)
            self.chinCB = cmds.checkBox(label=self.ar.data.lang['c026_chin'], value=cmds.getAttr(standard.guide_base+".chin"), changeCommand=standard.changeChin, enable=cmds.checkBox(self.jawCB, query=True, value=True), parent=self.headItemsLayout)
            self.lipsCB = cmds.checkBox(label=self.ar.data.lang['c062_lips'], value=cmds.getAttr(standard.guide_base+".lips"), changeCommand=standard.changeLips, enable=cmds.checkBox(self.jawCB, query=True, value=True), parent=self.headItemsLayout)
            self.upperHeadCB = cmds.checkBox(label=self.ar.data.lang['c044_upper']+" "+self.ar.data.lang['c024_head'], value=cmds.getAttr(standard.guide_base+".upperHead"), changeCommand=standard.changeUpperHead, parent=self.headItemsLayout)


    def articulation_layout(self, standard):      
        if 'articulation' in cmds.listAttr(standard.guide_base):
            self.articLayout = cmds.rowLayout('articLayout', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text(self.ar.data.lang['m173_articulation'], parent=self.articLayout)
            cmds.checkBox(f"{standard.number_name}_articulation_cb", label="", value=cmds.getAttr(standard.guide_base+".articulation"), changeCommand=standard.changeArticulation, parent=self.articLayout)


    def nostril_layout(self, standard):
        if 'nostril' in cmds.listAttr(standard.guide_base):
            cmds.text(" ", parent=self.articLayout)
            nostrilValue = cmds.getAttr(standard.guide_base+".nostril")
            self.nostrilCB = cmds.checkBox(label=self.ar.data.lang['m079_nostril'], value=nostrilValue, changeCommand=standard.changeNostril, parent=self.articLayout)


    def corrective_layout(self, standard):
        if 'corrective' in cmds.listAttr(standard.guide_base):
            self.correctiveLayout = cmds.rowLayout('correctiveLayout', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text(f"{standard.number_name}_corrective_txt", label=self.ar.data.lang['c124_corrective'].capitalize(), parent=self.correctiveLayout)
            cmds.checkBox(f"{standard.number_name}_corrective_cb", label="", value=cmds.getAttr(standard.guide_base+".corrective"), changeCommand=partial(standard.set_guide_attr, 'corrective'), parent=self.correctiveLayout)
            if 'articulation' in cmds.listAttr(standard.guide_base):
                articulationValue = cmds.getAttr(standard.guide_base+".articulation")
                cmds.text(f"{standard.number_name}_corrective_txt", edit=True, enable=articulationValue)
                cmds.checkBox(f"{standard.number_name}_corrective_cb", edit=True, enable=articulationValue)


    def dynamic_layout(self, standard):
        if 'dynamic' in cmds.listAttr(standard.guide_base):
            self.dynamicLayout = cmds.rowLayout('dynamicLayout', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            cmds.text(self.ar.data.lang['m097_dynamic'], parent=self.dynamicLayout)
            cmds.checkBox(f"{standard.number_name}_dynamic_cb", label="", value=cmds.getAttr(standard.guide_base+".dynamic"), changeCommand=partial(standard.set_guide_attr, 'dynamic'), parent=self.dynamicLayout)


    def main_ctrl_layout(self, standard):
        if 'nJoints' in cmds.listAttr(standard.guide_base):
            if 'mainControls' in cmds.listAttr(standard.guide_base):
                if cmds.getAttr(standard.guide_base+".nJoints") > 0:
                    self.mainCtrlColumn = cmds.rowLayout('mainCtrlColumn', numberOfColumns=2, columnWidth2=(100, 100), columnAlign=[(1, 'right'), (2, 'left')], adjustableColumn=2, columnAttach=[(1, 'right', 2), (2, 'left', 2)], parent="rig_selected_module_cl" )
                    hasMain = cmds.getAttr(standard.guide_base+".mainControls")
                    if cmds.getAttr(standard.guide_base+".nJoints") > 1:
                        cmds.checkBox(f"{standard.number_name}_main_ctrl_cb", label=self.ar.data.lang['m227_mainCtrls'], value=hasMain, enable=True, changeCommand=standard.set_main_ctrls, parent=self.mainCtrlColumn)
                        cmds.intField(f"{standard.number_name}_main_ctrl_if", value=cmds.getAttr(standard.guide_base+".nMain"), minValue=1, changeCommand=partial(standard.change_main_ctrls_number, 0), editable=hasMain, parent=self.mainCtrlColumn)
                    else:
                        cmds.checkBox(f"{standard.number_name}_main_ctrl_cb", label=self.ar.data.lang['m227_mainCtrls'], value=False, enable=True, changeCommand=standard.set_main_ctrls, parent=self.mainCtrlColumn)
                        cmds.intField(f"{standard.number_name}_main_ctrl_if", value=cmds.getAttr(standard.guide_base+".nMain"), minValue=1, changeCommand=partial(standard.change_main_ctrls_number, 0), editable=False, parent=self.mainCtrlColumn)
                        cmds.setAttr(standard.guide_base+".mainControls", 0)


    def deformer_layout(self, standard):
        if 'deformer' in cmds.listAttr(standard.guide_base):
            deformerEnableValue = cmds.getAttr(standard.guide_base+".upperHead")
            self.deformerLayout = cmds.rowLayout('deformerLayout', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            self.deformerTxt = cmds.text(self.ar.data.lang['c097_deformer'].capitalize(), enable=deformerEnableValue, parent=self.deformerLayout)
            self.deformerCB = cmds.checkBox('deformerCB', label="", value=cmds.getAttr(standard.guide_base+".deformer"), changeCommand=standard.changeDeformer, enable=deformerEnableValue, parent=self.deformerLayout)


    def facial_layout(self, standard):
        if 'facial' in cmds.listAttr(standard.guide_base):
            facialEnableValue = True
            if not cmds.getAttr(standard.guide_base+".jaw") or not cmds.getAttr(standard.guide_base+".chin") or not cmds.getAttr(standard.guide_base+".lips") or not cmds.getAttr(standard.guide_base+".upperHead"):
                facialEnableValue=False
            self.facialLayout = cmds.rowLayout('facialLayout', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="rig_selected_module_cl" )
            self.facialTxt = cmds.text(self.ar.data.lang['c059_facial'].capitalize(), enable=facialEnableValue, parent=self.facialLayout)
            facialValue = cmds.getAttr(standard.guide_base+".facial")
            self.facialCB = cmds.checkBox('facialCB', label="", value=facialValue, changeCommand=standard.changeFacial, enable=facialEnableValue, parent=self.facialLayout)
            collapsed = False
            if not facialValue:
                collapsed = True
            # facial frame layout
            cmds.frameLayout("edit_guide_facial_fl", label=self.ar.data.lang['m139_facialCtrlsAttr'], collapsable=True, collapse=collapsed, enable=facialValue, parent="rig_selected_module_cl")
            cmds.rowColumnLayout(f"{standard.number_name}_facial_rcl", numberOfColumns=2, columnWidth=[(1, 70), (2, 300)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 20)], parent='edit_guide_facial_fl')
            # facial element checkboxes
            cmds.checkBox(f"{standard.number_name}_facial_brow_cb", label=self.ar.data.lang["c060_brow"], value=cmds.getAttr(standard.guide_base+".facialBrow"), changeCommand=partial(standard.changeFacialElement, "facialBrow"), parent=f"{standard.number_name}_facial_rcl")
            cmds.text(f"{standard.number_name}_facial_brow_txt", label=', '.join(self.ar.data.facial_brow_targets), parent=f"{standard.number_name}_facial_rcl")
            cmds.checkBox(f"{standard.number_name}_facial_eyelid_cb", label=self.ar.data.lang["c042_eyelid"], value=cmds.getAttr(standard.guide_base+".facialEyelid"), changeCommand=partial(standard.changeFacialElement, "facialEyelid"), parent=f"{standard.number_name}_facial_rcl")
            cmds.text(f"{standard.number_name}_facial_eyelid_txt", label=', '.join(self.ar.data.facial_eyelid_targets[2:]), parent=f"{standard.number_name}_facial_rcl")
            cmds.checkBox(f"{standard.number_name}_facial_mouth_cb", label=self.ar.data.lang["c061_mouth"], value=cmds.getAttr(standard.guide_base+".facialMouth"), changeCommand=partial(standard.changeFacialElement, "facialMouth"), parent=f"{standard.number_name}_facial_rcl")
            cmds.text(f"{standard.number_name}_facial_mouth_txt", label=', '.join(self.ar.data.facial_mouth_targets), parent=f"{standard.number_name}_facial_rcl")
            cmds.checkBox(f"{standard.number_name}_facial_lips_cb", label=self.ar.data.lang["c062_lips"], value=cmds.getAttr(standard.guide_base+".facialLips"), changeCommand=partial(standard.changeFacialElement, "facialLips"), parent=f"{standard.number_name}_facial_rcl")
            cmds.text(f"{standard.number_name}_facial_lips_txt", label=', '.join(self.ar.data.facial_lips_targets), parent=f"{standard.number_name}_facial_rcl")
            cmds.checkBox(f"{standard.number_name}_facial_sneer_cb", label=self.ar.data.lang["c063_sneer"], value=cmds.getAttr(standard.guide_base+".facialSneer"), changeCommand=partial(standard.changeFacialElement, "facialSneer"), parent=f"{standard.number_name}_facial_rcl")
            cmds.text(f"{standard.number_name}_facial_sneer_txt", label=', '.join([item for item in self.ar.data.facial_sneer_targets if item is not None]), parent=f"{standard.number_name}_facial_rcl")
            cmds.checkBox(f"{standard.number_name}_facial_grimace_cb", label=self.ar.data.lang["c064_grimace"], value=cmds.getAttr(standard.guide_base+".facialGrimace"), changeCommand=partial(standard.changeFacialElement, "facialGrimace"), parent=f"{standard.number_name}_facial_rcl")
            cmds.text(f"{standard.number_name}_facial_grimace_txt", label=', '.join([item for item in self.ar.data.facial_grimace_targets if item is not None]), parent=f"{standard.number_name}_facial_rcl")
            cmds.checkBox(f"{standard.number_name}_facial_face_cb", label=self.ar.data.lang["c065_face"], value=cmds.getAttr(standard.guide_base+".facialFace"), changeCommand=partial(standard.changeFacialElement, "facialFace"), parent=f"{standard.number_name}_facial_rcl")
            cmds.text(f"{standard.number_name}_facial_face_txt", label=', '.join(self.ar.data.facial_face_targets), parent=f"{standard.number_name}_facial_rcl")
            cmds.separator(style='none', height=5, parent=f"{standard.number_name}_facial_rcl")
            self.facialTypeLayout = cmds.columnLayout('facialTypeLayout', parent="edit_guide_facial_fl")
            userType = cmds.getAttr(standard.guide_base+".connectUserType")
            self.facialTypeRC = cmds.radioCollection('facialTypeRC', parent=self.facialTypeLayout)
            bs = cmds.radioButton(label=self.ar.data.lang['m170_blendShapes']+" - "+self.ar.data.lang['i185_animation']+": #_Recept_BS", annotation=standard.bsType, onCommand=standard.dpChangeType)
            jnt = cmds.radioButton(label=self.ar.data.lang['i181_facialJoint']+" - "+self.ar.data.lang['i186_gaming'], annotation=self.jointsType, onCommand=standard.dpChangeType)
            cmds.radioCollection(self.facialTypeRC, edit=True, select=bs)
            if userType:
                cmds.radioCollection(self.facialTypeRC, edit=True, select=jnt)


    def bend_layout(self, standard):
        if 'hasBend' in cmds.listAttr(standard.guide_base):
            self.bendMainLayout = cmds.rowColumnLayout("bendMainLayout", numberOfColumns=2, columnWidth=[(1, 260), (2, 80)], columnSpacing=[(1, 2), (2, 10)], parent="rig_selected_module_cl")
            self.bendLayout = cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 20, 50, 20), columnAlign=[(1, 'right'), (2, 'left'), (3, 'left'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (4, 'both', 10)], parent=self.bendMainLayout)
            cmds.text(label=self.ar.data.lang['m044_addBend'], visible=True, parent=self.bendLayout)
            self.bendCB = cmds.checkBox(value=standard.getHasBend(), label=' ', changeCommand=standard.changeBend, parent=self.bendLayout)
            cmds.optionMenu('edit_guide_bend_num_om', label='Ribbon Joints', changeCommand=standard.changeNumBend, enable=standard.getHasBend(), parent=self.bendLayout)
            bendNumMenuItemList = [3, 5, 7]
            for item in bendNumMenuItemList:
                cmds.menuItem(label=item, parent='edit_guide_bend_num_om')
            # read from guide attribute the current value to number of joints for bend:
            currentNumberBendJoints = cmds.getAttr(standard.guide_base+".numBendJoints")
            for i, item in enumerate(bendNumMenuItemList):
                if currentNumberBendJoints == item:
                    cmds.optionMenu('edit_guide_bend_num_om', edit=True, select=i+1)
                    break
            # additional ribbon joint:
            cmds.checkBox("edit_guide_additional_cb", label=self.ar.data.lang['m180_additional'], value=cmds.getAttr(standard.guide_base+".additional"), changeCommand=partial(standard.set_guide_attr, 'additional'), parent=self.bendMainLayout)
        
                

    
    def align_world_layout(self, standard):
        if 'alignWorld' in cmds.listAttr(standard.guide_base):
            cmds.rowLayout('edit_guide_align_world_rl', numberOfColumns=4, columnWidth4=(100, 20, 50, 20), columnAlign=[(1, 'right'), (2, 'left'), (3, 'left'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'left', 2), (4, 'both', 10)], parent="rig_selected_module_cl")
            cmds.text('edit_guide_align_world_txt', label=self.ar.data.lang['m080_alignWorld'], visible=True, parent='edit_guide_align_world_rl')
            cmds.checkBox('edit_guide_align_world_cb', value=cmds.getAttr(standard.guide_base+'.alignWorld'), label=' ', changeCommand=partial(standard.set_guide_attr, 'alignWorld'), parent='edit_guide_align_world_rl')
    
    
    
    def change_corrective(self, standard, value, *args):
        cmds.text(f"{standard.number_name}_corrective_txt", edit=True, enable=value)
        cmds.checkBox(f"{standard.number_name}_corrective_cb", edit=True, enable=value)
        if not value:
            cmds.checkBox(f"{standard.number_name}_corrective_cb", edit=True, value=value)
            cmds.setAttr(standard.guide_base+".corrective", value)
    

    def change_curve_degree(self, standard, item, *args):
        """ This function receives the degree menu name item string and set it as a int in the guide base (main).
        """
        # verify integrity of the guideModule:
        if standard.check_guide_integrity():
            if item == '3 - Cubic':
                cmds.setAttr(standard.guide_base+".degree", 3)
            else:
                cmds.setAttr(standard.guide_base+".degree", 1)
    

   
    


    def changeDeformedBy(self, standard, item, *args):
        """ This function receives the deformedBy menu name item and set it as a integer value in the guide base (main).
        """
        # verify integrity of the guideModule:
        if standard.check_guide_integrity():
            cmds.setAttr(standard.guide_base+".deformedBy", int(item[0]))


    def plusInfoWin(self, instance=None, *args):
        """ Open plus info attributes to each module
        """
        # declaring variables:
        plus_winWidth  = 250
        plus_winHeight = 180
        widthSize = (0.8*plus_winWidth)
        # creating Plus Info Window:
        self.ar.utils.close_ui(self.ar.data.color_override_win_name)
        if cmds.window(self.ar.data.plus_info_win_name, query=True, exists=True):
            cmds.deleteUI('plusFL')
            self.dpPlusInfo = self.ar.data.plus_info_win_name
        else:
            self.dpPlusInfo = cmds.window(self.ar.data.plus_info_win_name, title='dpAutoRig - '+self.ar.data.lang['i205_guide']+" "+self.ar.data.lang['i013_info'], iconName='dpPlus', widthHeight=(plus_winWidth, plus_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
        plusFL = cmds.formLayout('plusFL', numberOfDivisions=100, parent=self.dpPlusInfo)
        plusSL = cmds.scrollLayout('plusSL', parent=plusFL)
        cmds.formLayout(plusFL, edit=True, attachForm=((plusSL, 'bottom', 10), (plusSL, 'top', 10), (plusSL, 'left', 10), (plusSL, 'right', 10)))
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
            cmds.separator(style='none', height=10, parent=plusSL)
            headerRCL = cmds.rowColumnLayout(numberOfColumns=2, adjustableColumn=2, columnWidth=[(1, 55), (2, 150)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 10)], parent=plusSL)
            cmds.text(label=guide_name, align='left', parent=headerRCL)
            cmds.text(label=custom_name, align='left', font='boldLabelFont', parent=headerRCL)
            cmds.separator(style='none', height=10, parent=plusSL)
            standard.annotationCheckBox = cmds.checkBox(label=standard.ar.data.lang['m014_annotation'], annotation=standard.ar.data.lang['m014_annotation'], value=cmds.getAttr(standard.guide_base+'.displayAnnotation'), onCommand=partial(standard.displayAnnotation, 1), offCommand=partial(standard.displayAnnotation, 0), parent=plusSL)
            cmds.separator(style='none', height=5, parent=plusSL)
            cmds.floatSliderGrp(f"{standard.number_name}_radius_size_fsg", label=standard.ar.data.lang['c067_radius'].capitalize(), field=True, width=widthSize, minValue=0.001, maxValue=10.0, fieldMinValue=0.001, fieldMaxValue=100.0, precision=2, value=cmds.getAttr(standard.radius_ctrl+".translateX"), changeCommand=standard.change_radius_size, dragCommand=standard.change_radius_size, columnWidth=[(1, 55), (2, 60), (3, 30)], parent=plusSL)
            cmds.separator(style='none', height=5, parent=plusSL)
            cmds.floatSliderGrp(f"{standard.number_name}_shape_size_fsg", label=standard.ar.data.lang['m067_shape']+" "+standard.ar.data.lang['i115_size'], width=widthSize, field=True, minValue=0.001, maxValue=10.0, fieldMinValue=0.001, fieldMaxValue=100.0, precision=2, value=cmds.getAttr(standard.guide_base+'.shapeSize'), changeCommand=partial(standard.set_guide_attr, 'shapeSize'), dragCommand=partial(standard.set_guide_attr, 'shapeSize'), columnWidth=[(1, 55), (2, 60), (3, 30)], parent=plusSL)
            cmds.separator(style='none', height=10, parent=plusSL)
            currentRGBGuideColor = standard.ar.ctrls.getGuideRGBColorList(standard)
            standard.colorButton = cmds.button(label=standard.ar.data.lang['m013_color'], annotation=standard.ar.data.lang['m013_color'], width=widthSize, align="center", command=partial(standard.ar.ctrls.colorizeUI, standard), backgroundColor=currentRGBGuideColor, parent=plusSL)
            cmds.separator(style='none', height=5, parent=plusSL)
            cmds.separator(style='in', height=10, width=widthSize, parent=plusSL)
        # call Info Window:
        cmds.showWindow(self.dpPlusInfo)


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
            cmds.intField(f"{standard.number_name}_main_ctrl_if", edit=True, editable=value)
            cmds.checkBox(f"{standard.number_name}_main_ctrl_cb", edit=True, editable=True)


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
            cmds.textField(self.geoTF, edit=True, text=selected_items[0])
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





