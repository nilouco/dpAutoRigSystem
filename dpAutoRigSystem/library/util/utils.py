# importing libraries:
from maya import cmds
from maya import mel
from maya import OpenMaya
import os
import re
import cProfile
import json
import time
import stat
import unicodedata



class Utils(object):
    def __init__(self, ar):
        """ Initialize the module class loading variables.
        """
        # define variables
        self.ar = ar
        self.ignore_transform_io_attr = "dpNotTransformIO"
        self.load_variables()


    def load_variables(self):
        """ Just define dictionary member variables.
        """
        self.maya_base_nodes = ['time1', 'sequenceManager1', 'hardwareRenderingGlobals', 'renderPartition', 'renderGlobalsList1', 'defaultLightList1', 'defaultShaderList1', 'postProcessList1',
                                'defaultRenderUtilityList1', 'defaultRenderingList1', 'lightList1', 'defaultTextureList1', 'lambert1', 'standardSurface1', 'particleCloud1', 'initialShadingGroup', 'initialParticleSE', 
                                'initialMaterialInfo', 'shaderGlow1', 'dof1', 'defaultRenderGlobals', 'defaultRenderQuality', 'defaultResolution', 'defaultLightSet', 'defaultObjectSet', 'defaultViewColorManager', 
                                'defaultColorMgtGlobals', 'hardwareRenderGlobals', 'characterPartition', 'defaultHardwareRenderGlobals', 'ikSystem', 'hyperGraphInfo', 'hyperGraphLayout', 'globalCacheControl', 
                                'strokeGlobals', 'dynController1', 'lightLinker1', 'persp', 'perspShape', 'top', 'topShape', 'front', 'frontShape', 'side', 'sideShape', 'shapeEditorManager', 'poseInterpolatorManager', 
                                'layerManager', 'defaultLayer', 'renderLayerManager', 'defaultRenderLayer', 'ikSCsolver', 'ikRPsolver', 'ikSplineSolver', 'hikSolver', 'MayaNodeEditorSavedTabsInfo']
        self.utility_types = ["blendColors", "blendWeighted", "choice", "chooser", "clamp", "condition", "multiplyDivide", "plusMinusAverage", "remapValue", "reverse"]
        self.type_attr_data = {
                                "blendColors"      : ["blender", "color1R", "color1G", "color1B", "color2R", "color2G", "color2B"],
                                "blendWeighted"    : ["current"],
                                "choice"           : ["selector"],
                                "clamp"            : ["minR", "minG", "minB", "maxR", "maxG", "maxB", "inputR", "inputG", "inputB"],
                                "condition"        : ["operation", "firstTerm", "secondTerm", "colorIfTrueR", "colorIfTrueG", "colorIfTrueB", "colorIfFalseR", "colorIfFalseG", "colorIfFalseB"],
                                "multiplyDivide"   : ["operation", "input1X", "input1Y", "input1Z", "input2X", "input2Y", "input2Z"],
                                "plusMinusAverage" : ["operation"],
                                "remapValue"       : ["inputValue", "inputMin", "inputMax", "outputMin", "outputMax"],
                                "reverse"          : ["inputX", "inputY", "inputZ"]
                            }
        self.type_out_attr_data = {
                                "blendColors"      : ["outputR", "outputG", "outputB"],
                                "blendWeighted"    : ["output"],
                                "choice"           : ["output"],
                                "clamp"            : ["outputR", "outputG", "outputB"],
                                "condition"        : ["outColorR", "outColorG", "outColorB"],
                                "multiplyDivide"   : ["outputX", "outputY", "outputZ"],
                                "plusMinusAverage" : ["output1D", "output2Dx", "output2Dy", "output3Dx", "output3Dy", "output3Dz"],
                                "remapValue"       : ["outColorR", "outColorG", "outColorB", "outValue"],
                                "reverse"          : ["outputX", "outputY", "outputZ"]
                            }
        self.type_multi_attr_data = {
                                    "blendWeighted"    : {"input"   : [],
                                                        "weight" : []},
                                    "choice"           : {"input" : []},
                                    "chooser"          : {"inLevel"      : [],
                                                        "displayLevel" : []},
                                    "plusMinusAverage" : {"input1D" : [],
                                                        "input2D" : ["input2Dx", "input2Dy"],
                                                        "input3D" : ["input3Dx", "input3Dy", "input3Dz"]
                                                            },
                                    "remapValue"       : {"value" : ["value_Position", "value_FloatValue", "value_Interp"],
                                                        "color" : ["color_Position", "color_Color", "color_ColorR", "color_ColorG", "color_ColorB", "color_Position"]
                                                            }
                                }
        self.type_out_multi_attr_data = {"chooser" : {"output" : []}}


    def remove_user_defined_attr(self, node, keep_origined_from=False):
        """ Just remove all user defined attributes for the given node.
        """
        user_def_attrs = cmds.listAttr(node, userDefined=True)
        if user_def_attrs:
            for user_def_attr in user_def_attrs:
                del_it = True
                if keep_origined_from:
                    if "originedFrom" in user_def_attr or "guide_source" in user_def_attr:
                        del_it = False
                if del_it:
                    try:
                        cmds.setAttr(node+"."+user_def_attr, lock=False)
                        cmds.deleteAttr(node+"."+user_def_attr)
                    except:
                        pass


    def create_zero_out(self, transforms=[], offset=False, not_transform_io=True):
        """ Create a group over the transform, parent the transform in it and set zero all transformations of the transform node.
            If don't have a transforms given, try to get the current selection.
            If want to create with offset, it'll be an offset group between zero_grp and transform.
            Return a list of names of the create_zero_out groups.
        """
        zeros = []
        if not transforms:
            transforms = cmds.ls(selection=True)
        if transforms:
            for transform in transforms:
                suffix = "_Zero_0_Grp"
                transform_name = transform
                if transform_name.endswith("_Grp"):
                    transform_name = self.ar.naming.extract_suffix(transform_name)
                    if "_Zero_" in transform_name:
                        need_add_number = True
                        while need_add_number:
                            node_number = str(int(transform_name[transform_name.rfind("_")+1:])+1)
                            transform_name = (transform_name[:transform_name.rfind("_")+1])+node_number
                            suffix = "_Grp"
                            if not cmds.objExists(transform_name+suffix):
                                need_add_number = False
                zero_grp = cmds.duplicate(transform, name=transform_name+suffix)[0]
                self.remove_user_defined_attr(zero_grp)
                children = cmds.listRelatives(zero_grp, allDescendents=True, children=True, fullPath=True)
                if children:
                    cmds.delete(children)
                if offset:
                    offset_grp = cmds.duplicate(zero_grp, name=transform+'_Offset_Grp')[0]
                    self.ar.custom_attr.add_attr(0, [offset_grp]) #dpID
                    cmds.parent(transform, offset_grp, absolute=True)
                    cmds.parent(offset_grp, zero_grp, absolute=True)
                else:
                    cmds.parent(transform, zero_grp, absolute=True)
                if not_transform_io:
                    self.add_attr_to_items([zero_grp], self.ignore_transform_io_attr)
                    if offset:
                        self.add_attr_to_items([offset_grp], self.ignore_transform_io_attr)
                self.ar.custom_attr.add_attr(0, [zero_grp]) #dpID
                zeros.append(zero_grp)
        return zeros


    def add_attr_to_items(self, items, attr_name, attr_type="bool", keyable_attr=True, default_value_attr=True):
        """ Useful method to add the same attribute and values to a list of given items.
        """
        if items and attr_name:
            for node in items:
                if not attr_name in cmds.listAttr(node):
                    cmds.addAttr(node, longName=attr_name, attributeType=attr_type, keyable=keyable_attr, defaultValue=default_value_attr)


    def set_origined_from_attr(self, item="", attr=""):
        """ Add attribute as string and set is as attr_name got.
        """
        if item != "" and attr != "":
            if not cmds.objExists(item+".originedFrom"):
                cmds.addAttr(item, longName="originedFrom", dataType='string')
            cmds.setAttr(item+".originedFrom", attr, type='string')


    def get_origined_from_data(self):
        """ List all transforms in the scene, verify if there is an originedFrom string attribute and store it value in a dictionary.
            Return a dictionary with originedFrom string as keys and transform nodes as values of these keys.
        """
        origined_from_data = {}
        transforms = cmds.ls(selection=False, type="transform")
        if transforms:
            for transform in transforms:
                if cmds.objExists(transform+".originedFrom"):
                    temp_origined_from = cmds.getAttr(transform+".originedFrom")
                    if temp_origined_from:
                        if not ";" in temp_origined_from:
                            origined_from_data[temp_origined_from] = transform
                        else:
                            temp_origined_from_items = temp_origined_from.split(";")
                            for item in temp_origined_from_items:
                                origined_from_data[item] = transform
        return origined_from_data


    def add_hook(self, item="", hook_type="staticHook", add_not_transform_io=True):
        """ Add attribute as boolean and set it as True = 1.
        """
        if item != "":
            if cmds.objExists(item):
                if not hook_type in cmds.listAttr(item):
                    cmds.addAttr(item, longName=hook_type, attributeType='bool')
                    cmds.setAttr(item+"."+hook_type, 1)
                if add_not_transform_io:
                    self.add_attr_to_items([item], self.ignore_transform_io_attr)


    def get_hook(self):
        """ Mount a dictionary with guide modules hierarchies.
            Return a dictionary with the father and children lists inside of each guide like:
            {guide{'guide_module_namespace':"...", 'name':"...", 'guide_custom_name':"...", 'guide_mirror_axis':"...", 'guide_mirror_name':"...", 'fatherGuide':"...", 'father':"...", 'father_module':"...", 'father_custom_name':"...", 'father_mirror_axis':"...", 'father_mirror_name':"...", 'father_guide_loc':"...", 'children':[...]}}
        """
        hook = {}
        transforms = cmds.ls(type='transform')
        for item in transforms:
            if "guideBase" in cmds.listAttr(item) and cmds.getAttr(item+".guideBase") == 1:
                # module info:
                guide_module_namespace = item[:item.find(":")]
                name = item[:item.find("__")]
                guide_instance = item[item.rfind("__")+2:item.find(":")]
                guide_custom_name = cmds.getAttr(item+".customName")
                guide_mirror_axis = cmds.getAttr(item+".mirrorAxis")
                current_mirror_name = cmds.getAttr(item+".mirrorName")
                guide_mirror_name = [current_mirror_name[0]+"_" , current_mirror_name[len(current_mirror_name)-1:]+"_"]
                # get children:
                guide_children = []
                children = cmds.listRelatives(item, allDescendents=True, type='transform')
                if children:
                    for child in children:
                        if cmds.objExists(child+".guideBase"):
                            if cmds.getAttr(child+".guideBase") == 1:
                                guide_children.append(child)                
                # get father:
                guide_parents = []
                father_nodes = []
                parent_node = ""
                parents = cmds.listRelatives(item, parent=True, type='transform')
                if parents:
                    next_loop = True
                    while next_loop:
                        if cmds.objExists(parents[0]+".guideBase") and cmds.getAttr(parents[0]+".guideBase") == 1:
                            guide_parents.append(parents[0])
                            next_loop = False
                        else:
                            if not father_nodes:
                                father_nodes.append(parents[0])
                            parents = cmds.listRelatives(parents[0], parent=True, type='transform')
                            if parents:
                                next_loop = True
                            else:
                                next_loop = False
                    if guide_parents:
                        # father info:
                        guide_parent      = guide_parents[0]
                        father_module     = guide_parent[:guide_parent.find("__")]
                        father_instance   = guide_parent[guide_parent.rfind("__")+2:guide_parent.find(":")]
                        father_custom_name = cmds.getAttr(guide_parent+".customName")
                        father_mirror_axis = cmds.getAttr(guide_parent+".mirrorAxis")
                        current_father_mirror_name  = cmds.getAttr(guide_parent+".mirrorName")
                        father_mirror_name = [current_father_mirror_name[0]+"_" , current_father_mirror_name[len(current_father_mirror_name)-1:]+"_"]
                        if father_nodes:
                            father_guide_loc = father_nodes[0][father_nodes[0].find("Guide_")+6:]
                        else:
                            guide_parent_children = cmds.listRelatives(guide_parent, children=True, type='transform')
                            if guide_parent_children:
                                for guide_parent_child in guide_parent_children:
                                    if cmds.objExists(guide_parent_child+'.nJoint'):
                                        if cmds.getAttr(guide_parent_child+'.nJoint') == 1:
                                            if guide_parent[:guide_parent.rfind(":")] in guide_parent_child:
                                                father_nodes = [guide_parent_child]
                                                father_guide_loc = guide_parent_child[guide_parent_child.find("Guide_")+6:]
                    
                    # parent_node info:
                    parent_node = cmds.listRelatives(item, parent=True, type='transform')[0]
                
                # mounting dictionary:
                if guide_parents and guide_children:
                    hook[item]={"guideModuleNamespace":guide_module_namespace, "name":name, "guideInstance":guide_instance, "guideCustomName":guide_custom_name, "guideMirrorAxis":guide_mirror_axis, "guideMirrorName":guide_mirror_name, "fatherGuide":guide_parent, "fatherNode":father_nodes[0], "fatherModule":father_module, "fatherInstance":father_instance, "fatherCustomName":father_custom_name, "fatherMirrorAxis":father_mirror_axis, "fatherMirrorName":father_mirror_name, "fatherGuideLoc":father_guide_loc, "parentNode":parent_node, "children":guide_children}
                elif guide_parents:
                    hook[item]={"guideModuleNamespace":guide_module_namespace, "name":name, "guideInstance":guide_instance, "guideCustomName":guide_custom_name, "guideMirrorAxis":guide_mirror_axis, "guideMirrorName":guide_mirror_name, "fatherGuide":guide_parent, "fatherNode":father_nodes[0], "fatherModule":father_module, "fatherInstance":father_instance, "fatherCustomName":father_custom_name, "fatherMirrorAxis":father_mirror_axis, "fatherMirrorName":father_mirror_name, "fatherGuideLoc":father_guide_loc, "parentNode":parent_node, "children":[]}
                elif guide_children:
                    hook[item]={"guideModuleNamespace":guide_module_namespace, "name":name, "guideInstance":guide_instance, "guideCustomName":guide_custom_name, "guideMirrorAxis":guide_mirror_axis, "guideMirrorName":guide_mirror_name, "fatherGuide":"", "fatherNode":"", "fatherModule":"", "fatherInstance":"", "fatherCustomName":"", "fatherMirrorAxis":"", "fatherMirrorName":"", "fatherGuideLoc":"", "parentNode":parent_node, "children":guide_children}
                else:
                    hook[item]={"guideModuleNamespace":guide_module_namespace, "name":name, "guideInstance":guide_instance, "guideCustomName":guide_custom_name, "guideMirrorAxis":guide_mirror_axis, "guideMirrorName":guide_mirror_name, "fatherGuide":"", "fatherNode":"", "fatherModule":"", "fatherInstance":"", "fatherCustomName":"", "fatherMirrorAxis":"", "fatherMirrorName":"", "fatherGuideLoc":"", "parentNode":parent_node, "children":[]}
        return hook


    def clear_node_grp(self, item='dpAR_GuideMirror_Grp', attr='guideBaseMirror', unparent=False):
        """ Check if there is any node with the attribute attr in the item and then unparent its children and delete it.
        """
        if cmds.objExists(item):
            if cmds.listRelatives(item, children=True, allDescendents=True, type="transform"):
                children = [child for child in cmds.listRelatives(item, children=True, allDescendents=True, type="transform") if attr in cmds.listAttr(child) and cmds.getAttr(child+"."+attr) == 1]
                if unparent and children:
                    fathers = cmds.listRelatives(item, parent=True)
                    for child in children:
                        if item.split(":")[0] in cmds.listRelatives(child, parent=True)[0]:
                            if fathers:
                                cmds.parent(child, fathers[0])
                            else:
                                cmds.parent(child, world=True)
            cmds.lockNode(item, lock=False)
            cmds.delete(item)


    def clear_guide_mirror_grp(self):
        if cmds.objExists(self.ar.data.guide_mirror_grp):
            cmds.delete(self.ar.data.guide_mirror_grp)
            

    def get_guide_children(self, item):
        """ This function verify if there are guide children of the passed item.
            It will return the guide_children if it exists.
        """
        guide_children = []
        if cmds.objExists(item):
            children = cmds.listRelatives(item, allDescendents=True, type='transform')
            if children:
                for child in children:
                    if cmds.objExists(child+".guideBase") and cmds.getAttr(child+".guideBase") == 1:
                        guide_children.append(child)
        return guide_children


    def get_mirrored_guide_father(self, item):
        """ This function verify if there is a mirrored guide as a father of the passed item.
            Returns the mirrored guide father name if true.
        """
        parents = cmds.listRelatives(item, parent=True, type='transform')
        if parents:
            next_loop = True
            while next_loop:
                if cmds.objExists(parents[0]+".guideBase") and cmds.getAttr(parents[0]+".guideBase") == 1 and cmds.getAttr(parents[0]+".mirrorEnable") == 1 and cmds.getAttr(parents[0]+".mirrorAxis") != "off":
                    next_loop = False
                    return parents[0]
                else:
                    parents = cmds.listRelatives(parents[0], parent=True, type='transform')
                    if parents:
                        next_loop = True
                    else:
                        next_loop = False


    def get_parents(self, item):
        """ Get all parents.
            Return a list with all parents if they exists.
        """
        # get father:
        all_parents = []
        parents = cmds.listRelatives(item, parent=True, type='transform')
        if parents:
            next_loop = True
            while next_loop:
                all_parents.append(parents[0])
                parents = cmds.listRelatives(parents[0], parent=True, type='transform')
                if not parents:
                    next_loop = False
        return all_parents


    def get_guides_to_rig(self):
        """ Get all valid loaded modules to be rigged (They are valid instances with namespaces in the scene, then they are not deleted).
            Currently named as rawGuide instances.
            Return a list of modules to be rigged.
        """
        guides_to_rig = []
        head_modules = []
        for guide_module in self.ar.data.guide_instances:
            if guide_module.check_guide_integrity():
                guide_namespace = guide_module.guide_namespace
                if guide_namespace in cmds.namespaceInfo(listOnlyNamespaces=True):
                    number_name = guide_module.number_name
                    if not cmds.objExists(number_name+'_Static_Grp'):
                        if not "dpHead" in str(guide_module):
                            guides_to_rig.append(guide_module)
                        else:
                            # store Head guides to rig it later
                            head_modules.append(guide_module)
        if head_modules:
            # hack to rig Head modules at the end in order to call FacialConnection properly for joint target Singles tweakers.
            guides_to_rig.extend(head_modules)
        return guides_to_rig


    def create_zero_out_joints(self, joints=None, display_bone=False):
        """ Duplicate the joints, parent as create_zero_out.
            Returns the father joints (zeroOuted).
        """
        results = []
        suffix = "_Jzt"
        if joints:
            for jnt in joints:
                if cmds.objExists(jnt):
                    jxt_name = jnt.replace("_Jnt", "").replace("_"+suffix, "")
                    if not suffix in jxt_name:
                        jxt_name += suffix
                    dup = cmds.duplicate(jnt, name=jxt_name)[0]
                    self.delete_children(dup)
                    self.clear_dpar_attr([dup])
                    self.clear_joint_label([dup])
                    cmds.parent(jnt, dup)
                    if not display_bone:
                        cmds.setAttr(dup+".drawStyle", 2) #none
                    self.ar.custom_attr.add_attr(0, [dup]) #dpID
                    results.append(dup)
        return results


    def clear_dpar_attr(self, items):
        """ Delete all dpAR (dpAutoRigSystem) attributes in this joint
        """
        dpar_attrs = ['dpAR_joint']
        if items:
            for item in items:
                for dpar_attr in dpar_attrs:
                    if cmds.objExists(item+"."+dpar_attr):
                        cmds.deleteAttr(item+"."+dpar_attr)


    def delete_children(self, item):
        """ Delete all child of the item node passed as argument.
        """
        if cmds.objExists(item):
            children = cmds.listRelatives(item, children=True, fullPath=True)
            if children:
                for child in children:
                    cmds.delete(child)


    def create_articulation_joint(self, father, brother, jcr_number=0, jcr_pos=None, jcr_rot=None, dist=1, jar_radius=1.5, do_scale=True, orient_ctrl=None):
        """ Create a simple joint to help skinning with a half rotation value.
            Receives the number of corrective joints to be created. Zero by default.
            Place these corrective joints with the given vector list.
            Returns the created joint list.
        """
        joints = []
        if father and brother:
            if cmds.objExists(father) and cmds.objExists(brother):
                jax_name = brother[:brother.rfind("_")]+"_Jax"
                jar_name = brother[:brother.rfind("_")]+"_Jar"
                cmds.select(clear=True)
                jax = cmds.joint(name=jax_name, radius=0.5*jar_radius)
                jar = cmds.joint(name=jar_name, radius=jar_radius)
                cmds.addAttr(jar, longName='dpAR_joint', attributeType='float', keyable=False)
                cmds.matchTransform(jax, brother, position=True, rotation=True)
                cmds.parent(jax, father)
                cmds.makeIdentity(jax, apply=True)
                cmds.setAttr(jax+".segmentScaleCompensate", 0)
                cmds.setAttr(jar+".segmentScaleCompensate", 1)
                joints.append(jar)
                for i in range(0, jcr_number):
                    cmds.select(jar)
                    jcr = cmds.joint(name=brother[:brother.rfind("_")+1]+str(i)+"_Jcr")
                    cmds.setAttr(jcr+".segmentScaleCompensate", 0)
                    cmds.addAttr(jcr, longName='dpAR_joint', attributeType='float', keyable=False)
                    if jcr_pos:
                        cmds.setAttr(jcr+".translateX", jcr_pos[i][0]*dist)
                        cmds.setAttr(jcr+".translateY", jcr_pos[i][1]*dist)
                        cmds.setAttr(jcr+".translateZ", jcr_pos[i][2]*dist)
                    if jcr_rot:
                        cmds.setAttr(jcr+".rotateX", jcr_rot[i][0])
                        cmds.setAttr(jcr+".rotateY", jcr_rot[i][1])
                        cmds.setAttr(jcr+".rotateZ", jcr_rot[i][2])
                    joints.append(jcr)
                cmds.pointConstraint(brother, jax, maintainOffset=True, name=jar_name+"_PoC")[0]
                if orient_ctrl:
                    orc = cmds.orientConstraint(father, orient_ctrl, jax, maintainOffset=True, name=jar_name+"_OrC")[0]
                else:
                    orc = cmds.orientConstraint(father, brother, jax, maintainOffset=True, name=jar_name+"_OrC")[0]
                cmds.setAttr(orc+".interpType", 2) #shortest
                if do_scale:
                    cmds.scaleConstraint(father, brother, jax, maintainOffset=True, name=jar_name+"_ScC")
                return joints


    def get_all_grp(self, master_attr=None):
        """ Return the All_Grp if it exists in the scene.
        """
        if not master_attr:
            master_attr = self.ar.data.master_attr
        transform_nodes = [n for n in cmds.ls(selection=False, type="transform") if master_attr in cmds.listAttr(n)]
        if transform_nodes:
            for item in transform_nodes:
                if not cmds.referenceQuery(item, isNodeReferenced=True):
                    if self.validate_master_grp(item):
                        return item


    def validate_master_grp(self, item):
        """ Check if the current item is a valid masterGrp (All_Grp) verifying it's message attribute connections.
        """
        master_grp_attrs = ["supportGrp", "ctrlsGrp", "ctrlsVisibilityGrp", "dataGrp", "renderGrp", "proxyGrp", "fxGrp", "staticGrp", "scalableGrp", "blendShapesGrp", "wipGrp"]
        old_attrs = ["modelsGrp", None, None, None, None, None, None, None, None, None, None]
        for m, master_attr in enumerate(master_grp_attrs):
            if not master_attr in cmds.listAttr(item):
                if not old_attrs[m]:
                    cmds.setAttr(item+"."+self.ar.data.master_attr, 0)
                    return False
                elif not old_attrs[m] in cmds.listAttr(item):
                    cmds.setAttr(item+"."+self.ar.data.master_attr, 0)
                    return False
        return cmds.getAttr(item+"."+self.ar.data.master_attr)
    

    def get_node_by_message(self, attr_name, node=None):
        """ Get connected node in the given attribute searching as message.
            If there isn't a given node, try to use All_Grp.
            Return the found node name or False if it wasn't found.
        """
        result = False
        if not node:
            node = self.get_all_grp()
        if node:
            if cmds.objExists(node+"."+attr_name):
                found_items = cmds.listConnections(node+"."+attr_name, source=True, destination=False)
                if found_items:
                    result = found_items[0]
        return result


    def attach_to_motionpath(self, item, curve_name, mop_name, u_value):
        """ Simple function to attach a node in a motion path curve.
            Sets the u position based to given u_value.
            Returns the created motion path node.
        """
        mop = cmds.pathAnimation(item, curve=curve_name, fractionMode=True, name=mop_name)
        cmds.delete(cmds.listConnections(mop+".u", source=True, destination=False)[0])
        cmds.setAttr(mop+".u", u_value)
        return mop
        

    #Profiler decorator
    def profiler(func):
        DPAR_PROFILE_MODE = False
        def runProfile(*args, **kwargs):
            if DPAR_PROFILE_MODE:
                pProf = cProfile.Profile()
                try:
                    pProf.enable()
                    pResult = func(*args, **kwargs)
                    pProf.disable()
                    return pResult
                finally:
                    pProf.print_stats()
            else:
                pResult = func(*args, **kwargs)
                return pResult
        return runProfile

    '''
    Open Maya Utils Functions
    '''

    def joint_chain_length(self, joints):
        """ Returns a sum of the joint lengths given.
        """
        i = 0
        chainlength = 0
        if joints:
            while ( i < len(joints) - 1 ):
                if cmds.objExists(joints[i]):
                    if cmds.objExists(joints[i+1]):
                        a = cmds.xform(joints[i], query=True, pivots=True, worldSpace=True)
                        b = cmds.xform(joints[i+1], query=True, pivots=True, worldSpace=True)
                        x = b[0] - a[0]
                        y = b[1] - a[1]
                        z = b[2] - a[2]
                        v = [x,y,z]
                        chainlength += self.ar.math.magnitude(v)
                i += 1
        return chainlength


    def unlock_attr(self, items):
        for item in items:
            if cmds.objExists(item):
                for attr in self.ar.data.transform_attrs:
                    cmds.setAttr(item+"."+attr, lock=False)


    def export_log_dic_to_json(self, data, name=None, path=None, sub_folder=None):
        """ Save to path the given dictionary as a json file.
        """
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        if not path:
            path = cmds.file(query=True, sceneName=True)
        if path:
            dp_folder = path[:path.rfind("/")]
            if sub_folder:
                dp_folder = dp_folder+"/"+sub_folder
            if not os.path.exists(dp_folder):
                os.makedirs(dp_folder)
            if not name:
                name = path[path.rfind("/")+1:path.rfind(".")]
            path_file = dp_folder+"/dpLog_"+name+"_"+current_time+".json"
        else:
            return False
        print("Log file", path_file)
        out_file = open(path_file, "w")
        json.dump(data, out_file, indent=4)
        out_file.close()
        return path_file


    def check_saved_scene(self):
        """ Check if the current scene is saved to return True.
            Otherwise return False.
        """
        scene_path = cmds.file(query=True, sceneName=True)
        modified_scene = cmds.file(query=True, modified=True)
        if not scene_path or modified_scene:
            return False
        return True


    def clear_joint_label(self, joints):
        """ Just remove the current joint label if it exists.
        """
        for jnt in joints:
            if cmds.objExists(jnt):
                cmds.setAttr(jnt+".side", 3) #None
                cmds.setAttr(jnt+".type", 0) #None
                cmds.setAttr(jnt+".otherType", "", type="string")


    def create_joint_blend(self, joints_a, joints_b, joints_c, attr_name, start_attr, world_ref, store_name=True):
        """ Create an Ik Fk Blend setup for joint chain.
            Return the created reverse node.
        """
        attr_comp_name = start_attr[0].lower()+start_attr[1:]+attr_name
        for n in range(len(joints_a)):
            pac = cmds.parentConstraint(joints_a[n], joints_b[n], joints_c[n], maintainOffset=True, name=joints_c[n]+"_"+attr_name+"_PaC")[0]
            cmds.setAttr(pac+".interpType", 2) #shortest
            if n == 0:
                rev = cmds.createNode('reverse', name=joints_c[n]+"_"+attr_name+"_Rev")
                self.ar.custom_attr.add_attr(0, [rev]) #dpID
                cmds.addAttr(world_ref, longName=attr_comp_name, attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                cmds.addAttr(world_ref, longName=attr_comp_name+"RevOutputX", attributeType="float", keyable=False)
                if store_name:
                    cmds.addAttr(world_ref, longName="ikFkBlendAttrName", dataType="string")
                    cmds.setAttr(world_ref+".ikFkBlendAttrName", attr_comp_name, type="string")
                cmds.connectAttr(world_ref+"."+attr_comp_name, rev+".inputX", force=True)
                cmds.connectAttr(rev+".outputX", world_ref+"."+attr_comp_name+"RevOutputX", force=True)
            # connecting ikFkBlend using the reverse node:
            cmds.connectAttr(world_ref+"."+attr_comp_name, pac+"."+joints_b[n]+"W1", force=True)
            cmds.connectAttr(world_ref+"."+attr_comp_name+"RevOutputX", pac+"."+joints_a[n]+"W0", force=True)
        return rev


    def set_attr_values(self, items, attributes, values, is_string=None):
        """ Just set the attribute values for the given lists.
        """
        for item in items:
            for attr, value in zip(attributes, values):
                if is_string:
                    cmds.setAttr(item+"."+attr, value, type='string')
                else:
                    cmds.setAttr(item+"."+attr, value)


    def get_network_by_attr(self, net_attr):
        """ Returns a list of network nodes with the boolean given net attribute active.
        """
        nets = []
        all_nets = cmds.ls(selection=False, type="network")
        if all_nets:
            for item in all_nets:
                if cmds.objExists(item+".dpNetwork"):
                    if cmds.getAttr(item+".dpNetwork") == 1:
                        if cmds.objExists(item+"."+net_attr):
                            if cmds.getAttr(item+"."+net_attr) == 1:
                                nets.append(item)
        return nets


    def filter_transforms(self, items=None, filter_camera=True, filter_constraint=True, filter_follicle=True, filter_joint=True, filter_locator=True, filter_handle=True, filter_linear_deform=True, filter_effector=True, filter_basenode=True, filter_basename=True, filter_lattice=True, verbose=True, title="Rigging"):
        """ Remove camera, constraints, follicles, etc from the given list and return it.
        """
        if items:
            cameras = ["|persp", "|top", "|side", "|front"]
            constraints = ["parentConstraint", "pointConstraint", "orientConstraint", "scaleConstraint", "aimConstraint", "poleVectorConstraint"]
            to_remove_items = []
            for item in items:
                if verbose:
                    self.set_progress(title)
                item_type = cmds.objectType(item)
                if filter_camera:
                    for camera_name in cameras:
                        if item.endswith(camera_name):
                            to_remove_items.append(item)
                if filter_constraint:
                    if item_type in constraints:
                        to_remove_items.append(item)
                if filter_follicle:
                    if cmds.listRelatives(item, children=True, type="follicle"):
                        to_remove_items.append(item)
                if filter_joint:
                    if cmds.listRelatives(item, children=True, type="joint") or item_type == "joint":
                        to_remove_items.append(item)
                if filter_locator:
                    if cmds.listRelatives(item, children=True, type="locator"):
                        to_remove_items.append(item)
                if filter_handle:
                    if cmds.listRelatives(item, children=True, type="ikHandle") or item_type == "ikHandle":
                        to_remove_items.append(item)
                    if cmds.listRelatives(item, children=True, type="clusterHandle") or item_type == "clusterHandle":
                        to_remove_items.append(item)
                if filter_linear_deform:
                    for def_name in ["deformBend", "deformTwist", "deformSquash", "deformFlare", "deformSine", "deformWave"]:
                        if cmds.listRelatives(item, children=True, type=def_name) or item_type == def_name:
                            to_remove_items.append(item)
                if filter_effector:
                    if cmds.listRelatives(item, children=True, type="ikEffector") or item_type == "ikEffector":
                        to_remove_items.append(item)
                if filter_basenode:
                    if item in self.maya_base_nodes:
                        to_remove_items.append(item)
                if filter_basename:
                    if self.get_suffix_numbers(item)[1].endswith("Base"):
                        to_remove_items.append(item)
                if filter_lattice:
                    for def_name in ["lattice", "baseLattice"]:
                        if cmds.listRelatives(item, children=True, type=def_name) or item_type == def_name:
                            to_remove_items.append(item)
            if to_remove_items:
                items = list(set(items) - set(to_remove_items))
        return items


    def delete_orig_shape(self, item, delete_intermediate=True, *args):
        """ Delete Orig shape if it exists.
        """
        #TODO maybe use this command instead?
        #cmds.deformableShape(item, originalGeometry=True)
        if item:
            for child in cmds.listRelatives(item, children=True, allDescendents=True, fullPath=True):
                #if "Orig" in child:
                if child.endswith("Orig"):
                    cmds.delete(child)
                elif cmds.getAttr(child+".intermediateObject") == 1:
                    if delete_intermediate:
                        cmds.delete(child)
                else:
                    self.remove_user_defined_attr(child)


    def reapply_deformers(self, item, defs):
        """ Reapply the given deformer list to the destination given item except the tweak node.
        """
        if cmds.objExists(item):
            for deformer_node in defs:
                if cmds.objExists(deformer_node):
                    if not cmds.objectType(deformer_node) == "tweak":
                        cmds.deformer(deformer_node, edit=True, geometry=item)


    def get_transform_data(self, item, t=True, r=True, s=True, user_world_space=True):
        """ Return the queried transformation data for the given node.
        """
        result_data = {}
        if item:
            if cmds.objExists(item):
                if t:
                    result_data["translation"] = cmds.xform(item, query=True, translation=t, worldSpace=user_world_space)
                if r:
                    result_data["rotation"] = cmds.xform(item, query=True, rotation=r, worldSpace=user_world_space)
                if s:
                    result_data["scale"] = cmds.xform(item, query=True, scale=s, worldSpace=user_world_space)
        return result_data


    def delete_file(self, file_path):
        """ Force delete the given file.
        """
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except PermissionError as exc:
                # use a brute force to delete without permission:
                os.chmod(file_path, stat.S_IWUSR)
                os.remove(file_path)


    def add_joint_end_attr(self, items):
        """ Create a jointEnd boolean attribute to the given list.
        """
        if items:
            for item in items:
                if not self.ar.data.joint_end_attr in cmds.listAttr(item):
                    cmds.addAttr(item, longName=self.ar.data.joint_end_attr, attributeType="bool", defaultValue=1)
        

    def create_locator_in_item_position(self, item):
        """ Create a locator in the input item position.
            Return the created locator name.
        """
        if item:
            temp_pos = cmds.spaceLocator(name=item+"_LocTemp")[0]
            cmds.matchTransform(temp_pos, item, position=True, rotation=True)
            return temp_pos


    def parent_guide_children_to(self, item, dest):
        """ Parent all children guides to the given destination node.
        """
        guide_children = self.get_guide_children(item)
        if guide_children:
            cmds.parent(guide_children, dest)


    def remove_from_sets(self, item):
        """ Remove the given node from existing sets.
        """
        if cmds.objExists(item):
            sets = cmds.listSets(object=item, extendToShape=True)
            render_sets = cmds.listSets(object=item, extendToShape=True, type=1) #rendering sets
            sets = list(set(sets)-set(render_sets))
            if sets:
                for set_nodes in sets:
                    cmds.sets(item, remove=set_nodes)
                    cmds.sets(item+".vtx[*]", remove=set_nodes)
                    cmds.sets(item+".f[*]", remove=set_nodes)
                    cmds.sets(item+".e[*]", remove=set_nodes)


    def replace_item_suffix(self, item, source_data, suffixes=None):
        """ Return found replaced item suffix in the given dictionary.
        """
        if not suffixes:
            suffixes = ["_JointLoc1", "_Head", "Neck0", "Main", "_cvTopLoc1", "_Foot", "_CenterLoc", "_JointLocA", "_JointLocB"]
        for end_name in suffixes:
            if item.replace("_Base", end_name) in source_data.keys():
                return item.replace("_Base", end_name)


    def check_geometry(self, item):
        """ Check if the given item is a geometry.
            Return True if it's geometry or False if it isn't.
        """
        if item:
            if cmds.objExists(item):
                children = cmds.listRelatives(item, children=True)
                if children:
                    self.item_type = cmds.objectType(children[0])
                    if self.item_type == "mesh" or self.item_type == "nurbsSurface":
                        return True
                    else:
                        mel.eval("warning \""+item+" is not a geometry.\";")
                else:
                    mel.eval("warning \"Select the transform node instead of "+item+" shape, please.\";")
            else:
                mel.eval("warning \""+item+" does not exists, maybe it was deleted, sorry.\";")
        else:
            mel.eval("warning \"Not found "+item+"\";")


    def get_keys_by_value(self, data, value):
        return [k for k, v in data.items() if v == value]


    def set_template(self, items, value=1):
        for item in items:
            cmds.setAttr(f"{item}.template", value)


    def envelope_is_valid(self, node):
        """ Check if the given node envelope attribute is not connected, nodeState is normal and not user defined.
        """
        not_connected =  not cmds.listConnections(node+".envelope", source=True, destination=False)
        node_state_normal = cmds.getAttr(node+".nodeState") == 0
        not_user_defined = not "envelope" in (cmds.listAttr(node, userDefined=True) or [])
        return not_connected and node_state_normal and not_user_defined
