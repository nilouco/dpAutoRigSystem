from maya import cmds
from maya import mel
from ..base import base
from importlib import reload

# global variables to this module:    
CLASS_NAME = "UpdateGuides"
TITLE = "m186_updateGuides"
DESCRIPTION = "m187_updateGuidesDesc"
WIKI = "06-‐-Tools#-update-guides"



class UpdateGuides(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)


    def build_tool(self, *args):
        # Dictionary that will hold data for update, whatever don't need update will not be saved
        self.update_data = {}
        # Receive the guides list from hook function
        self.guides_directory = self.ar.utils.get_hook()
        # List that will hold all new guides instances
        self.new_guides_instances = []
        # Dictionary where the keys are the guides that will be used and don't need update
        # and values are its current parent, this is used to search for possible new parent
        self.guides_to_reparent_data = {}

        # If there are guides on the dictionary go on.
        if len(self.guides_directory) > 0:
            # Get all info nedeed and store in update_data dictionary
            self.get_guides_to_update_data()
            if self.ar.data.ui_state:
                # Open the UI
                self.ar.update_guides_ui.create_ui(self)
            else:
                # Update existing outdated guides.
                self.do_update()
        else:
            mel.eval('print \"dpAR: '+self.ar.data.lang['e000_guideNotFound']+'\\n\";')
    

    def filter_not_nurbs_curve_and_transform(self, items):
        """ Remove objects different from transform and nurbsCurve from list.
            Returns cleaned list.
        """
        results = []
        for item in items:
            item_type = cmds.objectType(item)
            if item_type == 'nurbsCurve' or item_type == 'transform':
                results.append(item)
        return results
    

    def filter_annotation(self, items):
        """ Remove _Ant(Anotations) items from list of transforms.
            Return cleaned list.
        """
        results = []
        for item in items:
            if not '_Ant' in item:
                results.append(item)
        return results


    def get_attr_value(self, guide, attr, locked=False):
        if locked:
            try:
                return cmds.getAttr(guide+'.'+attr, lock=True)
            except:
                return False
        else:
            try:
                return cmds.getAttr(guide+'.'+attr, silent=True)
            except:
                return ''
    

    def get_new_guide_instance(self, new_name):
        new_guide_names = list(map(lambda module_instance : module_instance.guide_base, self.new_guides_instances))
        current_guide_instance_index = new_guide_names.index(new_name)
        return self.new_guides_instances[current_guide_instance_index]
    

    def translate_limb_style_value(self, enum_value):
        if enum_value == 1:
            return self.ar.data.lang['m026_biped']
        elif enum_value == 2:
            return self.ar.data.lang['m037_quadruped']
        elif enum_value == 3:
            return self.ar.data.lang['m043_quadSpring']
        elif enum_value == 4:
            return self.ar.data.lang['m155_quadrupedExtra']
        else:
            return self.ar.data.lang['m042_default']


    def translate_spine_style_value(self, enum_value):
        if enum_value == 1:
            return self.ar.data.lang['m026_biped']
        else:
            return self.ar.data.lang['m042_default']
    

    def translate_limb_type_value(self, enum_value):
        if enum_value == 1:
            return self.ar.data.lang['m030_leg']
        else:
            return self.ar.data.lang['m028_arm']


    def set_attr_value(self, guide, attr, value):
        try:
            cmds.setAttr(guide+'.'+attr, value)
        except:
            mel.eval('print \"dpAR: '+self.ar.data.lang['m195_couldNotBeSet']+' '+guide+'.'+attr+'\\n\";')


    def set_attr_string_value(self, guide, attr, value):
        try:
            cmds.setAttr(guide+'.'+attr, value, type='string')
        except:
            mel.eval('print \"dpAR: '+self.ar.data.lang['m195_couldNotBeSet']+' '+guide+'.'+attr+'\\n\";')
    

    def set_eyelid_guide_attr(self, guide, value):
        current_instance = self.get_new_guide_instance(guide)
        cmds.setAttr(guide+".eyelid", value)
        cmds.setAttr(current_instance.name_guide+"_UpperEyelidLoc.visibility", value)
        cmds.setAttr(current_instance.name_guide+"_LowerEyelidLoc.visibility", value)
        cmds.setAttr(current_instance.name_guide+"_JEyelid.visibility", value)
        cmds.setAttr(current_instance.name_guide+"_JUpperEyelid.visibility", value)
        cmds.setAttr(current_instance.name_guide+"_JLowerEyelid.visibility", value)


    def set_iris_guide_attr(self, guide, value):
        current_instance = self.get_new_guide_instance(guide)
        cmds.setAttr(guide+".iris", value)
        cmds.setAttr(current_instance.name_guide+"_IrisLoc.visibility", value)


    def set_pupil_guide_attr(self, guide, value):
        current_instance = self.get_new_guide_instance(guide)
        cmds.setAttr(guide+".pupil", value)
        cmds.setAttr(current_instance.name_guide+"_PupilLoc.visibility", value)


    def set_nostril_guide_attr(self, guide, value):
        current_instance = self.get_new_guide_instance(guide)
        cmds.setAttr(guide+".nostril", value)
        cmds.setAttr(current_instance.cvLNostrilLoc+".visibility", value)
        cmds.setAttr(current_instance.cvRNostrilLoc+".visibility", value)
    

    def check_set_new_guide_to_attr(self, guide, attr, value):
        if value in self.update_data:
            self.set_attr_string_value(guide, attr, self.update_data[value]['new_guide'])
        else:
            self.set_attr_string_value(guide, attr, value)
            

    def set_guide_attributes(self, guide, attr, value, lock=False):
        """ Verify if we have specific attribute cases to work with each kind of module guides.
            Ignore known attributes.
        """
        ignores = ['version', 'controlID', 'className', 'direction', 'pinGuideConstraint', 'moduleNamespace', 'customName', 'moduleInstanceInfo', 'hookNode', 'guideObjectInfo', 'dpARVersion', 'dpID']
        if attr not in ignores:
            if attr == 'nJoints':
                current_instance = self.get_new_guide_instance(guide)
                current_instance.change_joint_number(value)
            elif attr == 'style':
                current_instance = self.get_new_guide_instance(guide)
                if current_instance.name == 'Limb':
                    expected_value = self.translate_limb_style_value(value)
                else:
                    expected_value = self.translate_spine_style_value(value)
                current_instance.changeStyle(expected_value)
            elif attr == 'type':
                current_instance = self.get_new_guide_instance(guide)
                expected_value = self.translate_limb_type_value(value)
                current_instance.change_type(expected_value)
            elif attr == 'mirrorAxis':
                current_instance = self.get_new_guide_instance(guide)
                current_instance.change_mirror(value)
            elif attr == 'mirrorName':
                current_instance = self.get_new_guide_instance(guide)
                current_instance.change_mirror_name(value)
            elif attr == 'displayAnnotation':
                current_instance = self.get_new_guide_instance(guide)
                current_instance.display_annotation(value)
            elif attr == 'rigType':
                current_instance = self.get_new_guide_instance(guide)
                current_instance.rigType = value
                self.set_attr_string_value(guide, attr, value)
            elif attr == 'lockedList' and value != '':
                self.set_attr_string_value(guide, attr, value)
            # EYE ATTRIBUTES
            elif attr == 'eyelid':
                self.set_eyelid_guide_attr(guide, value)
            elif attr == 'iris':
                self.set_iris_guide_attr(guide, value)
            elif attr == 'pupil':
                self.set_pupil_guide_attr(guide, value)
            elif attr == 'aimDirection':
                current_instance = self.get_new_guide_instance(guide)
                current_instance.change_aim_direction(self.ar.data.direcions[value])
            # self.noseName ATTRIBUTES
            elif attr == 'nostril':
                self.set_nostril_guide_attr(guide, value)
            # self.suspensionName ATTRIBUTES AND self.wheelName ATTRIBUTES
            elif attr == 'fatherB' or attr == 'geo':
                self.check_set_new_guide_to_attr(guide, attr, value)
            else:
                self.set_attr_value(guide, attr, value)
            if lock:
                cmds.setAttr(f'{guide}.{attr}', lock=True)
            if self.ar.data.ui_state:
                cmds.refresh()
    

    def get_key_user_attr(self, items):
        """ Return a list of attributes, keyable and userDefined
        """
        results = []
        keyable = cmds.listAttr(items, keyable=True)
        if keyable:
            results.extend(keyable)
        user_attr = cmds.listAttr(items, userDefined=True)
        if user_attr:
            results.extend(user_attr)
        # Guaranty no duplicated attr
        results = list(set(results))
        return results
    

    def get_guide_parent(self, base_guide):
        try:
            return cmds.listRelatives(base_guide, parent=True)[0]
        except:
            return None


    def get_children(self, base_guide):
        children = cmds.listRelatives(base_guide, allDescendents=True, children=True, type='transform')
        children = self.filter_not_nurbs_curve_and_transform(children)
        children = self.filter_annotation(children)
        return children
    

    def split_tranform_attr_values(self, guide, attributes):
        non_transform_data = {}
        transform_data = {}
        for attribute in attributes:
            attr_value = self.get_attr_value(guide, attribute)
            if attribute in self.ar.data.transform_attrs[:-1]: #without visibility
                attr_value_locked = self.get_attr_value(guide, attribute, True)
                transform_data[attribute] = (attr_value, attr_value_locked)
            else:
                non_transform_data[attribute] = attr_value
        return non_transform_data, transform_data


    def get_guides_to_update_data(self):
        """ Scan a dictionary for old guides and gather data needed to update them.
        """
        guides_to_rig = self.ar.utils.get_guides_to_rig()
        instance_modules_strings = list(map(str, guides_to_rig))
        for base_guide in self.guides_directory:
            guide_version = cmds.getAttr(base_guide+'.dpARVersion', silent=True)
            if guide_version != self.ar.data.version:
                # Create the database holder where the key is the base_guide
                self.update_data[base_guide] = {}
                self.update_data[base_guide]["name"] = self.guides_directory[base_guide]["name"]
                guide_attrs = self.get_key_user_attr(base_guide)
                # Create de attributes dictionary for each base_guide
                self.update_data[base_guide]['attributes'], self.update_data[base_guide]['transformAttributes'] = self.split_tranform_attr_values(base_guide, guide_attrs)
                self.update_data[base_guide]['instance'] = guides_to_rig[instance_modules_strings.index(self.update_data[base_guide]['attributes']['moduleInstanceInfo'])]
                self.update_data[base_guide]['children'] = {}
                self.update_data[base_guide]['parent'] = self.get_guide_parent(base_guide)
                children = self.get_children(base_guide)
                for child in children:
                    self.update_data[base_guide]['children'][child] = {'attributes': {}}
                    self.update_data[base_guide]['children'][child] = {'transformAttributes': {}}
                    guide_attrs = self.get_key_user_attr(child)
                    self.update_data[base_guide]['children'][child]['attributes'], self.update_data[base_guide]['children'][child]['transformAttributes'] = self.split_tranform_attr_values(child, guide_attrs)
            else:
                self.guides_to_reparent_data[base_guide] = self.get_guide_parent(base_guide)


    def create_new_guides(self):
        for guide in self.update_data:
            current_new_guide = self.ar.config.get_instance(self.update_data[guide]['name'], [self.ar.data.standard_folder])
            current_new_guide.build_raw_guide()
            # rename as it's predecessor
            name_guide = self.update_data[guide]['attributes']['customName']
            current_new_guide.set_guide_custom_name(name_guide)
            self.update_data[guide]['new_guide'] = current_new_guide.guide_base
            self.new_guides_instances.append(current_new_guide)
            if self.ar.data.ui_state:
                cmds.refresh()


    def rename_old_guides(self):
        for guide in self.update_data:
            current_custom_name = self.update_data[guide]['attributes']['customName']
            if current_custom_name == '' or current_custom_name == None:
                self.update_data[guide]['instance'].set_guide_custom_name(self.update_data[guide]['instance'].guide_base.split(':')[0]+'_OLD')
            else:
                self.update_data[guide]['instance'].set_guide_custom_name(current_custom_name+'_OLD')


    def retrieve_new_parent(self, current_parent):
        current_parent_base = current_parent.split(':')[0]+":Guide_Base"
        if current_parent_base in self.update_data.keys():
            new_parent_base = self.update_data[current_parent_base]['new_guide']
            new_parent_final = new_parent_base.split(':')[0]+':'+current_parent.split(':')[1]
            return new_parent_final
        else:
            return current_parent


    def parent_new_guides(self):
        for guide in self.update_data:
            has_parent = self.update_data[guide]['parent']
            if has_parent != None:
                new_parent_final = self.retrieve_new_parent(has_parent)
                try:
                    cmds.parent(self.update_data[guide]['new_guide'], new_parent_final)
                except:
                    mel.eval('print \"dpAR: '+self.ar.data.lang['m196_parentNotFound']+' '+self.update_data[guide]['new_guide']+'\\n\";')
            if self.ar.data.ui_state:
                cmds.refresh()


    def parent_retain_guides(self):
        if len(self.guides_to_reparent_data) > 0:
            for retain_guide in self.guides_to_reparent_data:
                has_parent = self.guides_to_reparent_data[retain_guide]
                if has_parent != None:
                    new_parent_final = self.retrieve_new_parent(has_parent)
                    try:
                        cmds.parent(retain_guide, new_parent_final)
                    except:
                        mel.eval('print \"dpAR: '+self.ar.data.lang['m197_notPossibleParent']+' '+retain_guide+'\\n\";')
    

    def copy_attr_from_guides(self, new_guide, old_guide_attr_data):
        new_guide_attrs = self.get_key_user_attr(new_guide)
        # For each attribute in the new guide check if exists equivalent in the old one, and check if the value is different, in that case
        # set the new guide attr value to the old one.
        for attr in new_guide_attrs:
            if attr in old_guide_attr_data:
                current_value = self.get_attr_value(new_guide, attr)
                if isinstance(old_guide_attr_data[attr], tuple):
                    if current_value != old_guide_attr_data[attr][0] or old_guide_attr_data[attr][1]:
                        self.set_guide_attributes(new_guide, attr, old_guide_attr_data[attr][0], old_guide_attr_data[attr][1])
                else:
                    if current_value != old_guide_attr_data[attr]:
                        self.set_guide_attributes(new_guide, attr, old_guide_attr_data[attr])


    def set_new_guide_attr(self, attributesSet):
        for guide in self.update_data:
            self.copy_attr_from_guides(self.update_data[guide]['new_guide'], self.update_data[guide][attributesSet])
    

    def filter_children_from_another_base(self, children, base_guide):
        filtered_items = []
        filter_string = base_guide.split(':')[0]
        for children in children:
            if filter_string in children:
                filtered_items.append(children)
        return filtered_items
    

    def set_children_guides(self):
        """ Set all attributes from children with same BaseGuide to avoid double set.
        """
        for guide in self.update_data:
            new_guide_children = self.get_children(self.update_data[guide]['new_guide'])
            new_guide_children = self.filter_children_from_another_base(new_guide_children, self.update_data[guide]['new_guide'])
            old_guide_children = self.update_data[guide]['children'].keys()
            old_guide_children = self.filter_children_from_another_base(old_guide_children, guide)
            new_guide_children_only = list(map(lambda name : name.split(':')[1], new_guide_children))
            old_guide_children_only = list(map(lambda name : name.split(':')[1], old_guide_children))
            for i, new_child in enumerate(new_guide_children):
                if new_guide_children_only[i] in old_guide_children_only:
                    name_guide = self.update_data[guide]['children'][guide.split(':')[0]+':'+new_guide_children_only[i]]
                    self.copy_attr_from_guides(new_child, name_guide['attributes'])
                    self.copy_attr_from_guides(new_child, name_guide['transformAttributes'])
    

    def get_new_attr(self):
        """ List new attributes from created guides for possible input.
            Returns new data dictionary if it exists.
        """
        new_data = {}
        for guide in self.update_data:
            old_guide_set = set(self.update_data[guide]['attributes']) | set(self.update_data[guide]['transformAttributes'])
            new_guide_set = set(self.get_key_user_attr(self.update_data[guide]['new_guide']))
            new_attributes_set = new_guide_set - old_guide_set
            if len(new_attributes_set) > 0:
                for attr in new_attributes_set:
                    if guide in new_data:
                        new_data[guide].append(attr)
                    else:
                        new_data[guide] = [attr]
        if len(new_data.keys()) == 0:
            return False
        else:
            return new_data
    

    def do_delete(self, *args):
        self.ar.utils.close_ui('update_summary_win')
        for guide in self.update_data:
            if cmds.listRelatives(guide, parent=True):
                cmds.parent(guide, world=True)
        try:
            cmds.delete(*self.update_data.keys())
        except:
            mel.eval('print \"dpAR: '+self.ar.data.lang['e000_guideNotFound']+'\\n\";')
        for guide in self.update_data:
             if self.update_data[guide]['instance'].guide_namespace in cmds.namespaceInfo(listOnlyNamespaces=True):
                cmds.namespace(moveNamespace=(self.update_data[guide]['instance'].guide_namespace, ':'), force=True)
                cmds.namespace(removeNamespace=self.update_data[guide]['instance'].guide_namespace, force=True)
        self.ar.ui_manager.refresh_ui()


    def patch_foot_rff(self):
        """ Patching RfF new Foot pivot.
        """
        reverse_foot_e = "Guide_RfE"
        reverse_foot_f = "Guide_RfF"
        reverse_foot_e_items = cmds.ls("*:"+reverse_foot_e)
        reverse_foot_f_items = cmds.ls("*:"+reverse_foot_f)
        if reverse_foot_f_items:
            need_patch = False
            if reverse_foot_e_items:
                for rf_e in reverse_foot_e_items:
                    guide_version = cmds.getAttr(rf_e+".version")
                    if int(guide_version.split(".")[0]) == 4:
                        if float(guide_version.split(".")[1]+"."+guide_version.split(".")[2]) < 4.25:
                            need_patch = True
                            break
            if need_patch:
                for f in reverse_foot_f_items:
                    e = f.replace(reverse_foot_f, reverse_foot_e)
                    for attr in ["tx", "ty", "tz"]:
                        cmds.setAttr(f+"."+attr, cmds.getAttr(e+"."+attr))
                    toes = cmds.listRelatives(e, children=True, type="transform")
                    if toes:
                        cmds.matchTransform(e, f, position=True, rotation=True)
                        cmds.parent(toes, f)
                    for attr in ["tx", "ty", "tz"]:
                        cmds.setAttr(e+"."+attr, 0)


    def do_update(self, *args):
        """ Main method to update the guides in the scene.
        """
        self.ar.utils.close_ui('updateGuidesWindow')
        # Starts progress bar feedback
        self.ar.utils.setProgress(self.ar.data.lang['m198_renameOldGuides'], self.ar.data.lang['m186_updateGuides'], 7, add_one=False)
        # Rename guides to discard as *_OLD
        self.rename_old_guides()
        self.ar.utils.setProgress(self.ar.data.lang['m199_creatingNewGuides'])
        # Create the new base guides to replace the old ones
        self.create_new_guides()
        self.ar.utils.setProgress(self.ar.data.lang['m200_setAttrs'])
        # Set all attributes except transforms, it's needed for parenting
        self.set_new_guide_attr('attributes')
        self.ar.utils.setProgress(self.ar.data.lang['m201_parentGuides'])
        # Parent all new guides;
        self.parent_new_guides()
        self.ar.utils.setProgress(self.ar.data.lang['m202_setTranforms'])
        # Set new base guides transform attrbutes
        self.set_new_guide_attr('transformAttributes')
        self.ar.utils.setProgress(self.ar.data.lang['m203_setChildGuides'])
        # Set all children attributes
        self.set_children_guides()
        self.ar.utils.setProgress(self.ar.data.lang['m201_parentGuides'])
        # After all new guides parented and set, reparent old ones that will be used.
        self.parent_retain_guides()
        self.patch_foot_rff()
        cmds.select(clear=True)
        # Ends progress bar feedback
        self.ar.utils.setProgress(endIt=True)
        if self.ar.data.ui_state:
            # Calls for summary window
            self.ar.update_guides_ui.summary_ui()
        else:
            self.do_delete()
