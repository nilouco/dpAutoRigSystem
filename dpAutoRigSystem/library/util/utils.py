# importing libraries:
from maya import cmds
from maya import mel
from maya import OpenMaya
from importlib import reload
import os
import re
import cProfile
import webbrowser
import math
import json
import time
import getpass
import datetime
import stat
import unicodedata



class Utils(object):
    def __init__(self, ar):
        """ Initialize the module class loading variables.
        """
        # define variables
        self.ar = ar
        self.order = "_order"
        self.ignore_transform_io_attr = "dpNotTransformIO"
        self.progress = False
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
        

    # UTILS functions:
    def find_env(self, key, path):
        """ Find and return the environ directory of this system.
        """
        env = os.environ[key]
        split_envs = []
        if os.name == "posix":
            split_envs = env.split(":")
        else:
            split_envs = env.split(";")
        env_path = ""
        if split_envs:
            split_envs = [x for x in split_envs if x != "" and x != ' ' and x != None]
            for env in split_envs:
                env = os.path.abspath(env) # Fix crash when there's relative path in os.environ
                if env in self.ar.data.dp_auto_rig_path:
                    try:
                        env_path = self.ar.data.dp_auto_rig_path.split(env)[1][+1:].split(path)[0][:-1].replace('/','.')
                    except:
                        pass
                    if len(env) < 4:
                        env_path = self.ar.data.dp_auto_rig_path.split(env)[1][0:].split(path)[0][:-1].replace('/','.')
                        return env_path+"."+path
                    break
        # if we are here, we must return a default path:
        split_envs = env.rpartition(path)
        if os.name == "posix":
            if env_path != "":
                env_path = env_path+".dpAutoRigSystem"
            else:
                env_path = "dpAutoRigSystem"
        else:
            if ":" in env_path:
                env_path = split_envs[0][split_envs[0].rfind(":")-1:]
        if env_path == "" or env_path == " " or env_path == None:
            return path
        return env_path


    def find_files_by_folder(self, path, folder, ext="py"):
        """ Find all files in the directory with the extension.
            Return a list of all module names (without the given extension).
        """
        file_dir = path + "/" + folder.replace(".", "/")
        all_files = os.listdir(file_dir)
        # select only files with extension:
        files = []
        for file in all_files:
            if file.endswith(f".{ext}") and str(file) != "__init__.py":
                files.append(str(file)[:file.rfind(".")])
        return files


    def find_modules_by_folder(self, path, folder, ext="py"):
        """ Find all modules in the directory.
            If find an _order*.txt file it will order the list for priority proporses.
            Return a list of all module names (without the given extension).
        """
        folder = folder.replace(".", "/")
        modules = self.find_files_by_folder(path, folder, ext)
        for text in self.find_files_by_folder(path, folder, "txt"):
            if text.startswith(self.order):
                desired_order_items = []
                dups = modules.copy()
                modules = []
                with open(path+"/"+folder+"/"+text+".txt", encoding='utf8') as filename:
                    for line in filename.readlines():
                        desired_order_items.append(line.strip())
                if desired_order_items:
                    for item in desired_order_items:
                        if item in dups:
                            modules.append(item)
                            dups.remove(item)
                if dups:
                    modules.extend(dups)
        return modules


    def find_module_names_by_folder(self, path, folder):
        """ Find all modules names for this directory.
            Return a list with the valid modules and valid modules names.
        """
        valid_modules = self.find_modules_by_folder(path, folder)
        valid_module_names = []
        guide_folder = self.find_env("PYTHONPATH", "dpAutoRigSystem")+"."+self.ar.data.standard_folder
        for m in valid_modules:
            mod = __import__(guide_folder+"."+m, {}, {}, [m])
            if self.ar.dev:
                reload(mod)
            valid_module_names.append(mod.CLASS_NAME)
        return(valid_modules, valid_module_names)


    def find_last_number(self, name="dpGuideNet", attr="guideNumber", pad=3):
        """ Returns a padding string of the number of network node in the scene or zero.
        """
        nodes = self.get_network_by_attr(name)
        if not nodes:
            return str(0).zfill(pad)
        else:
            numbers = []
            for node in nodes:
                if attr in cmds.listAttr(node):
                    numbers.append(int(cmds.getAttr(node+"."+attr)))
            if not numbers:
                return str(0).zfill(pad)
            else:
                return str(max(numbers)+1).zfill(pad)


    def find_module_last_number(self, class_name, type_name, guide_net=False):
        """ Find the last used number of this type of module or guideNet.
            Return its highest number.
        """
        # work with rigged modules in the scene:
        nodes, numbers = [], []
        guide_type_count = 0
        if guide_net:
            nodes = self.get_network_by_attr("dpGuideNet")
        else:
            nodes = cmds.ls(selection=False, transforms=True)
        if nodes:
            for node in nodes:
                if cmds.objExists(node+"."+type_name):
                    if cmds.getAttr(node+"."+type_name) == class_name:
                        numbers.append(class_name)
        # try check if there is a masterGrp and get its counter:
        all_grp = self.get_all_grp()
        if all_grp:
            guide_type_count = cmds.getAttr(all_grp+'.dp'+class_name+'Count') #v5
        if guide_type_count > len(numbers):
            return guide_type_count
        else:
            return len(numbers)
    
        
    def normalize_text(self, inputted_text="", prefixMax=4):
        """ Analisys the inputted_text to conform it in order to use in Application (Maya).
            Return the normalized text.
        """
        normal_text = ""
        inputted_text = ''.join(c for c in unicodedata.normalize('NFD', inputted_text) if unicodedata.category(c) != 'Mn') #strip accents
        if inputted_text:
            # analisys if it starts with number or has a whitespace or special character:
            if re.match("[0-9]", inputted_text[0]): #starts with number
                return normal_text
            else:
                #if re.search("\s", inputted_text[:len(inputted_text)-1]): #has space
                inputted_text = inputted_text.replace(" ", "_")
                while re.search(r"\W", inputted_text): #special character
                    span = re.search(r"\W", inputted_text).span()[0]
                    inputted_text = inputted_text[:span]+"_"+inputted_text[span+1:]
                if not len(inputted_text) < prefixMax:
                    inputted_text = inputted_text[:prefixMax]
                normal_text = inputted_text
        return normal_text


    def get_suffix_numbers(self, name):
        """ Returns a list of [index, base_name, suffixTrailingNumber]
        """
        idx = name.rfind(next(filter(lambda x: not x.isdigit(), name[::-1])))
        if idx:
            return [idx, name[:idx+1], name[idx+1:]]
        else:
            return [None, None, None]


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
                    transform_name = self.extract_suffix(transform_name)
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


    def create_dist_between(self, a, b, name="temp_DistBet", keep=False):
        """ Creates a distance between node for 2 objects a and b.
            Keeps them in the scene or delete.
            Returns the distance value only in case of not keeping dist_bet node or
            a list of distance value, distanceNode, two nulls used to calculate and the created constraint.
        """
        if cmds.objExists(a) and cmds.objExists(b):
            # create nulls:
            null_a = cmds.createNode('transform', name=a+"_DistBetNull_Grp")
            null_b = cmds.createNode('transform', name=b+"_DistBetNull_Grp")
            null_c = cmds.createNode('transform', name=b+"_DistBetNull_OrigRef_Grp")
            cmds.pointConstraint(a, null_a, maintainOffset=False, name=null_a+"_PoC")
            cmds.pointConstraint(b, null_b, maintainOffset=False, name=null_b+"_PoC")
            cmds.delete(cmds.pointConstraint(b, null_c, maintainOffset=False))
            poc = cmds.pointConstraint(b, null_c, null_b, maintainOffset=False, name=null_b+"_PoC")[0]
            # create distanceBetween node:
            dist_bet = cmds.createNode("distanceBetween", n=name)
            # connect aPos to the distance between point1:
            cmds.connectAttr(null_a+".tx", dist_bet+".point1X")
            cmds.connectAttr(null_a+".ty", dist_bet+".point1Y")
            cmds.connectAttr(null_a+".tz", dist_bet+".point1Z")
            # connect bPos to the distance between point2:
            cmds.connectAttr(null_b+".tx", dist_bet+".point2X")
            cmds.connectAttr(null_b+".ty", dist_bet+".point2Y")
            cmds.connectAttr(null_b+".tz", dist_bet+".point2Z")
            dist = cmds.getAttr(dist_bet+".distance")
            if keep:
                self.add_attr_to_items([null_a, null_b, null_c], self.ignore_transform_io_attr)
                self.ar.custom_attr.add_attr(0, [dist_bet]) #dpID
                return [dist, dist_bet, null_a, null_b, null_c, poc]
            else:
                cmds.delete(dist_bet, null_a, null_b, null_c, poc)
                return [dist, None, None, None, None, None]


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


    def get_ctrl_radius(self, item):
        """ Calculate and return the final radius to be used as a size of controls.
        """
        radius = float(cmds.getAttr(item+".translateX"))
        parents = self.get_parents(item)
        if (parents):
            for parent in parents:
                radius *= cmds.getAttr(parent+'.scaleX')
                if "worldSize" in cmds.listAttr(parent):
                    radius *= cmds.getAttr(parent+".worldSize")
        return radius


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


    def set_joint_label(self, joint_name, side_number, type_number, label):
        """ Set joint labelling in order to help Maya calculate the skinning mirror correctly.
            side:
                0 = Center
                1 = Left
                2 = Right
            type:
                18 = Other
        """
        cmds.setAttr(joint_name+".side", side_number)
        cmds.setAttr(joint_name+".type", type_number)
        if type_number == 18: #other
            cmds.setAttr(joint_name+".otherType", label, type="string")


    def extract_suffix(self, item):
        """ Remove suffix from a node name and return the base name.
        """
        end_suffixes = ["_Mesh", "_Msh", "_Geo", "_Ges", "_Tgt", "_Ctrl", "_Grp", "_Crv"]
        for end_suffix in end_suffixes:
            if item.endswith(end_suffix):
                base_name = item[:item.rfind(end_suffix)]
                return base_name
            if item.endswith(end_suffix.lower()):
                base_name = item[:item.rfind(end_suffix.lower())]
                return base_name
            if item.endswith(end_suffix.upper()):
                base_name = item[:item.rfind(end_suffix.upper())]
                return base_name
        return item


    def filter_name(self, name, items, separator):
        """ Filter list with the name or a list of name as a string separated by the separator (usually a space).
            Returns the filtered list.
        """
        filtered_items = []
        multi_filters = [name]
        if separator in name:
            multi_filters = list(name.split(separator))
        for filter in multi_filters:
            if filter:
                for item in items:
                    if str(filter) in item:
                        if not item in filtered_items:
                            filtered_items.append(item)
        return filtered_items
        
        
    def visit_website(self, url, *args):
        """ Start browser with the given website URL address.
        """
        #webSiteString = "start "+URL
        #os.popen(webSiteString)
        webbrowser.open(url, new=2)
        
        
    def check_loaded_plugin(self, plugin_name, message="Not loaded plugin"):
        """ Check if plugin is loaded and try to load it.
            Returns True if ok (loaded)
            Returns False if not found or not loaded.
        """
        loaded_plugin = True
        if not (cmds.pluginInfo(plugin_name, query=True, loaded=True)):
            loaded_plugin = False
            try:
                cmds.loadPlugin(plugin_name+".mll")
                loaded_plugin = True
            except:
                pass
        if not loaded_plugin:
            print(message, plugin_name)
        return loaded_plugin
        
        
    def create_twist_bone_matrix(self, node_a, node_b, twist_bone_name, twist_bone_md=None, axis='Z', inverse=True, *args):
        """ Create matrix nodes and quaternion to extract rotate.
            node_a = father transform node
            node_b = child transform node
            Returns the final multiplyDivide node created or given.
            Reference:
            https://bindpose.com/maya-matrix-nodes-part-2-node-based-matrix-twist-calculator/
        """
        twist_bone_mm = cmds.createNode("multMatrix", name=twist_bone_name+"_ExtractAngle_MM")
        twist_bone_dm = cmds.createNode("decomposeMatrix", name=twist_bone_name+"_ExtractAngle_DM")
        twist_bone_qte = cmds.createNode("quatToEuler", name=twist_bone_name+"_ExtractAngle_QtE")
        cmds.connectAttr(node_b+".worldMatrix[0]", twist_bone_mm+".matrixIn[0]", force=True)
        if inverse:
            cmds.connectAttr(node_a+".worldInverseMatrix[0]", twist_bone_mm+".matrixIn[1]", force=True)
        else:
            cmds.connectAttr(node_a+".worldMatrix[0]", twist_bone_mm+".matrixIn[1]", force=True)
        cmds.connectAttr(twist_bone_mm+".matrixSum", twist_bone_dm+".inputMatrix", force=True)
        cmds.connectAttr(twist_bone_dm+".outputQuat.outputQuat"+axis, twist_bone_qte+".inputQuat.inputQuat"+axis, force=True)
        cmds.connectAttr(twist_bone_dm+".outputQuat.outputQuatW", twist_bone_qte+".inputQuat.inputQuatW", force=True)
        if twist_bone_md:
            cmds.connectAttr(twist_bone_qte+".outputRotate.outputRotate"+axis, twist_bone_md+".input2"+axis, force=True)
        else:
            twist_bone_md = cmds.createNode("multiplyDivide", name=twist_bone_name+"_MD")
            cmds.connectAttr(twist_bone_qte+".outputRotate.outputRotate"+axis, twist_bone_md+".input2"+axis, force=True)
        self.ar.custom_attr.add_attr(0, [twist_bone_mm, twist_bone_dm, twist_bone_qte, twist_bone_md]) #dpID
        return twist_bone_md
        

    def validate_name(self, item, suffix=None):
        """ Check the default name in order to validate it and preserves the suffix naming.
            Returns the correct node name.
        """
        if cmds.objExists(item):
            need_restore_suffix = False
            if suffix:
                if item.endswith("_"+suffix):
                    need_restore_suffix = True
                    item = item[:item.rfind("_")]
            # find numering:
            i = 1
            if not need_restore_suffix:
                while cmds.objExists(item+str(i)):
                    i += 1
            else:
                while cmds.objExists(item+str(i)+"_"+suffix):
                    i += 1
            # add number:
            item = item+str(i)
            if need_restore_suffix:
                # restore suffix
                item = item+"_"+suffix
        return item


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

    def extract_world_scale_from_matrix(self, obj):
        world_matrix = cmds.getAttr(obj + ".worldMatrix")
        m_mat = OpenMaya.MMatrix()
        OpenMaya.MScriptUtil.createMatrixFromList(world_matrix, m_mat)
        m_transform = OpenMaya.MTransformationMatrix(m_mat)
        scale_util = OpenMaya.MScriptUtil()
        scale_util.createFromDouble(0.0, 0.0, 0.0)
        ptr = scale_util.asDoublePtr()
        m_transform.getScale(ptr, OpenMaya.MSpace.kWorld)
        x_scale = OpenMaya.MScriptUtil.getDoubleArrayItem(ptr, 0)
        y_scale = OpenMaya.MScriptUtil.getDoubleArrayItem(ptr, 1)
        z_scale = OpenMaya.MScriptUtil.getDoubleArrayItem(ptr, 2)
        return [x_scale, y_scale, z_scale]


    def resolve_name(self, name, suffix):
        """ Resolve repeated name adding number in the middle of the string.
            Returns the resolved base_name and name (including the suffix).
        """
        name = name[0].upper()+name[1:].replace(" ", "_")
        base_name = name
        name = name+"_00_"+suffix
        if cmds.objExists(name):
            i = 1
            while cmds.objExists(name):
                name = base_name+"_"+str(i).zfill(2)+"_"+suffix
                i = i+1
            base_name = base_name+"_"+str(i-1).zfill(2)
        else:
            base_name = base_name+"_00"
        return base_name, name


    def magnitude(self, v):
        """ Returns the square root of the sum of power 2 from a given vector.
        """
        return math.sqrt(pow(v[0], 2)+pow(v[1], 2)+pow(v[2], 2))


    def average_value(self, values):
        """ Return the average value for the given value list.
        """
        return sum(values)/len(values)


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
                        chainlength += self.magnitude(v)
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


    def create_validator_preset(self):
        """ Creates a json file as a Validator Preset and returns it.
        """
        result = None
        validators = self.ar.config.get_validator_instances()
        if validators:
            result_dialog = cmds.promptDialog(
                                                title=self.ar.data.lang['i129_createPreset'],
                                                message=self.ar.data.lang['i130_presetName'],
                                                button=[self.ar.data.lang['i131_ok'], self.ar.data.lang['i132_cancel']],
                                                defaultButton=self.ar.data.lang['i131_ok'],
                                                cancelButton=self.ar.data.lang['i132_cancel'],
                                                dismissString=self.ar.data.lang['i132_cancel'])
            if result_dialog == self.ar.data.lang['i131_ok']:
                result_name = cmds.promptDialog(query=True, text=True)
                result_name = result_name[0].upper()+result_name[1:]
                author = getpass.getuser()
                date = str(datetime.datetime.now().date())
                result = '{"_preset":"'+result_name+'","_author":"'+author+'","_date":"'+date+'","_updated":"'+date+'"'
                # add validators and its current active values
                for validator in validators:
                    result += ',"'+validator.name+'" : '+str(validator.active).lower()
                result += "}"
        return result


    #
    # TODO: passe it to Manager class
    #
    def close_ui(self, win_name, *args):
        """ Closes the given window name if it exists.
        """
        if cmds.window(win_name, query=True, exists=True):
            cmds.deleteUI(win_name, window=True)


    def generate_id(self, name):
        """ Return an ID generated by the sum of the "dp" string, plus the given name, plus dot, plus the current time.
        """
        now = str(round(time.time()*10000000000000))
        word = ("dp"+str(name)).encode('utf-8').hex()
        return word+"."+now


    def get_decomposed_ids(self, id):
        """ Returns a list with prefix, name and date from decomposed given dpID.
        """
        word, now = id.split(".")
        info = bytes.fromhex(word).decode('utf-8')
        prefix = info[0:2]
        name = info[2:]
        date = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(int(now)/10000000000000))
        return [prefix, name, date]


    def decompose_id(self, item):
        """ Return a list with the name and date decomposed from dpID attribute of the given node.
        """
        if cmds.attributeQuery(self.ar.data.dp_id, node=item, exists=True):
            id = cmds.getAttr(item+"."+self.ar.data.dp_id)
            return self.get_decomposed_ids(id)
        return [None, None, None]
    

    def validate_id(self, item):
        """ Return True if the decomposed name in the dpID is equal to the given node name.
        """
        if cmds.attributeQuery(self.ar.data.dp_id, node=item, exists=True):
            decomposed_id_items = self.decompose_id(item)
            if "dp" == decomposed_id_items[0]:
                if item == decomposed_id_items[1]:
                    return True


    def check_saved_scene(self):
        """ Check if the current scene is saved to return True.
            Otherwise return False.
        """
        scene_path = cmds.file(query=True, sceneName=True)
        modified_scene = cmds.file(query=True, modified=True)
        if not scene_path or modified_scene:
            return False
        return True


    def mount_wh(self, start, end):
        """ Mount and return path.
        """
        return "{}{}{}".format(start, "/", end)


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


    def get_attr_name_lower(self, side, name):
        """ Return the composed name for attributes starting with lower case.
        """
        attr_name_lower = name
        if side:
            attr_name_lower = side[0]+name
        attr_name_lower = attr_name_lower[0].lower()+attr_name_lower[1:]
        return attr_name_lower


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


    def node_renaming_treatment(self, items=None, node_type="unitConversion", suffix="_UC"):
        """ Rename unitConversion nodes to something like this:
            [IN]capitals+#+attr+_+[OUT]capitals+#+attr+"_UC"
            or the given node_type and suffix.
        """
        if not items:
            items = cmds.ls(selection=False, type=node_type)
        if items:
            self.ar.custom_attr.add_attr(0, items) #dpID
            for item in items:
                if not item.endswith(suffix):
                    if cmds.attributeQuery("input", node=item, exists=True):
                        new_name = self.get_capitals_name(cmds.listConnections(item+".input", plugs=True, source=True, destination=False)[0])
                    elif cmds.attributeQuery("input1", node=item, exists=True):
                        new_name = self.get_capitals_name(cmds.listConnections(item+".input1", plugs=True, source=True, destination=False)[0])
                    new_name += "_"
                    if cmds.listConnections(item+".output", plugs=True, source=False, destination=True):
                        new_name += self.get_capitals_name(cmds.listConnections(item+".output", plugs=True, source=False, destination=True)[0])
                    new_name += suffix
                    cmds.rename(item, new_name)


    def get_capitals_name(self, plug):
        """ Returns a string of all capital letters from a given name.
            Example:
                    Head_Head_Ctrl.rotateX = HHCrotateX
                    L_Arm_Wrist_Ctrl.translateZ = LAWCtranslateZ
        """
        return str("".join([n for n in plug.split(".")[0] if n.isupper() or n.isnumeric()])+plug.split(".")[1].replace("[", "").replace("]", ""))


    def set_progress(self, message="Rigging...", header="dpAutoRigSystem", max=100, amount=0, add_one=True, add_number=True, end_it=False, is_interruptable=False, *args):
        """ Centralize the progressWindow calling in one method.
            Try to use the cmds.progressWindow as a more automate process.
            
            Arguments:
                message = status
                header = tittle
                max = maxValue
                amount = progress
                add_one = increment amount plus 1
                add_number = add amount to the end of the message string
                end_it = end progress
                is_interruptable = if we can interrupt the process or not. False by default.

            Example:
                self.ar.utils.set_progress(messageName, titleName, 20, add_one=False)
                self.ar.utils.set_progress(doingName+': '+backWheelName)

            Returns the progress: 
                True if the progressWindow is running
                False if the progressWindow was ended or cancelled
        """
        if end_it:
            cmds.progressWindow(endProgress=True)
            self.progress = False
        else:
            if self.progress: #edit
                if add_one:
                    self.current_amount += 1
                else:
                    self.current_amount = amount
                if message == "Rigging...":
                    if max > 0:
                        cmds.progressWindow(edit=True, maxValue=max, progress=0)
                else:
                    if add_number:
                        message = message+" # "+str(self.current_amount)
                    cmds.progressWindow(edit=True, progress=self.current_amount, status=message)
            else: #create
                self.current_amount = amount
                cmds.progressWindow(title=header, progress=self.current_amount, status=message, maxValue=max, isInterruptable=is_interruptable)
                self.progress = True
        return self.progress


    def get_short_name(self, name, v_bar=True):
        """ Returns the short name of the given node.
            Example:
            |All_Grp|Render_Grp|Body_Mesh -> BodyMesh
            |pCube1 -> pCube1
        """
        short_name = None
        if name:
            short_name = name
            if "|" in name:
                if name.count("|") > 1:
                    if v_bar:
                        short_name = name[name.rfind("|"):]
                    else:
                        short_name = name[name.rfind("|")+1:]
                elif not v_bar:   
                    short_name = name[1:]
        return short_name


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


    def get_duplicated_names(self):
        """ Returns a list of duplicated names.
            Returns False if there are only unique names.
        """
        return [n for n in cmds.ls(selection=False, shortNames=True) if "|" in n] or False


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
    
    
    def get_mdagpath_by_name(self, item):
        """ Returns the OpenMaya MDagPath of the given item name.
        """
        selection = OpenMaya.MSelectionList()
        selection.add(item)
        dagpath = OpenMaya.MDagPath()
        selection.getDagPath(0, dagpath)
        return dagpath


    def get_keys_by_value(self, data, value):
        return [k for k, v in data.items() if v == value]


    def get_translated_names(self, name, from_lang="english"):
        custom_name = ""
        splitted_names = name.split("_")
        for n, splitted_name in enumerate(splitted_names):
            # splits capital letters and numbers:
            capitals = re.findall(r'\d+|[A-Z][a-z]*', splitted_name)
            if capitals:
                for capitalized_name in capitals:
                    capitalize = False
                    lang_names = self.get_keys_by_value(self.ar.data.lang_preset_data[from_lang], capitalized_name)
                    if not lang_names:
                        lang_names = self.get_keys_by_value(self.ar.data.lang_preset_data[from_lang], capitalized_name.lower())
                        capitalize = True
                    if lang_names:
                        if capitalize:
                            custom_name += self.ar.data.lang[lang_names[0]].capitalize()
                        else:
                            custom_name += self.ar.data.lang[lang_names[0]]
                    else:
                        custom_name += capitalized_name
            else:
                custom_name += splitted_name    
            if n < len(splitted_names)-1:
                custom_name += "_"
        if custom_name:
            return custom_name
        return name


    def to_snake_case(self, text):
        # Inserts an underscore before any capital letter followed by a lowercase letter
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        # Inserts an underscore before any capital letter if preceded by a lowercase letter or number
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        return s2.lower()


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




    #######
    #
    # TODO: UNUSED vector math functions
    #
    #
    def normalizeVector(self, v):
        """ Returns the normalized given vector.
        """
        vmag = self.magnitude(v)
        return [v[i]/vmag for i in range(len(v))]
    #
    #
    def distanceVectors(self, u, v):
        """ Returns the distance between 2 given points.
        """
        return math.sqrt((v[0]-u[0])**2+(v[1]-u[1])**2+(v[2]-u[2])**2)
    #
    #
    def addVectors(self, u, v):
        """ Returns the addition of 2 given vectors.
        """
        return [u[i]+v[i] for i in range(len(u))]
    #
    #
    def subVectors(self, u, v):
        """ Returns the substration of 2 given vectors.
        """
        return [u[i]-v[i] for i in range(len(u))]
    #
    #
    def multVectors(self, u, v):
        return [u[i]*v[i] for i in range(len(u))]
    #
    #
    def multiScalarVector(self, u, scalar):
        return [u[i]*scalar for i in range(len(u))]
    #
    #
    #######
