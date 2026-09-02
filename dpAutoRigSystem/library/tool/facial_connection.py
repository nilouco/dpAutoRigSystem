# importing libraries:
from maya import cmds
from maya import mel
from ..base import base
from importlib import reload

# global variables to this module:
CLASS_NAME = "FacialConnection"
TITLE = "m085_facialConnection"
DESCRIPTION = "m086_facialConnectionDesc"
WIKI = "06-‐-Tools#-facial-connection"

MIDDLE = "Middle"
SIDED = "Sided"
FACIALPRESET = "joints"



class FacialConnection(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        self.joint_targets = []
        self.rmv_number = 0
        self.recept_bs_suffix = "Recept_BS"
        self.bs_suffix = "BS"
        self.default_targets = ["Base", "Recept", "Tweaks",]
        self.facial_targets = ["L_BrowUp", "L_BrowDown", "L_BrowSad", "L_BrowFrown", "L_EyelidsClose",  "L_EyelidsOpen",
                                "L_LipsSide", "L_MouthSmile", "L_MouthSad", "L_MouthWide", "L_MouthNarrow", "L_Sneer", "L_Grimace", "L_Puff",
                                "Pucker", "LipsUp", "LipsDown", "LipsFront", "LipsBack", "UpperLipFront", "UpperLipBack", "LowerLipFront", "LowerLipBack", "SoftSmile", "BigSmile", "AAA", "OOO", "UUU", "FFF", "MMM"]
        self.combination_targets = ["L_MouthComb_SmileWide", "L_MouthComb_SmileNarrow", "L_MouthComb_SadWide", "L_MouthComb_SadNarrow", "L_BrowComb_UpSad", "L_BrowComb_UpFrown", "L_BrowComb_DownSad", "L_BrowComb_DownFrown"]
        

    def build_tool(self, *args):
        # call main function:
        if self.ar.data.ui_state:
            self.ar.facial_connection_ui.create_ui(self)
    

    def load_tweaks_variables(self):
        # part names:
        tweaks_name = self.ar.data.lang['m081_tweaks']
        middle_name = self.ar.data.lang['c029_middle']
        elbow_name = self.ar.data.lang['c041_eyebrow']
        corner_name = self.ar.data.lang['c043_corner']
        upper_name = self.ar.data.lang['c044_upper']
        lower_name = self.ar.data.lang['c045_lower']
        lip_name = self.ar.data.lang['c039_lip']
        squint_name = self.ar.data.lang['c054_squint']
        cheek_name = self.ar.data.lang['c055_cheek']
        # eyebrows names:
        eyebrow_middle_name = tweaks_name+"_"+middle_name+"_"+elbow_name
        eyebrow_name_1 = tweaks_name+"_"+elbow_name+"_01"
        eyebrow_name_2 = tweaks_name+"_"+elbow_name+"_02"
        eyebrow_name_3 = tweaks_name+"_"+elbow_name+"_03"
        eyebrow_name_4 = tweaks_name+"_"+elbow_name+"_04"
        # squints names:
        squint_name_1 = tweaks_name+"_"+squint_name+"_01"
        squint_name_2 = tweaks_name+"_"+squint_name+"_02"
        squint_name_3 = tweaks_name+"_"+squint_name+"_03"
        # cheeks names:
        cheek_name_1 = tweaks_name+"_"+cheek_name+"_01"
        cheek_name_2 = tweaks_name+"_"+cheek_name+"_02"
        # lip names:
        upper_lip_middle_name = tweaks_name+"_"+upper_name+"_"+lip_name+"_00"
        upper_lip_name_1 = tweaks_name+"_"+upper_name+"_"+lip_name+"_01"
        upper_lip_name_2 = tweaks_name+"_"+upper_name+"_"+lip_name+"_02"
        lower_lip_middle_name = tweaks_name+"_"+lower_name+"_"+lip_name+"_00"
        lower_lip_name_1 = tweaks_name+"_"+lower_name+"_"+lip_name+"_01"
        lower_lip_name_2 = tweaks_name+"_"+lower_name+"_"+lip_name+"_02"
        lip_corner_name = tweaks_name+"_"+corner_name+"_"+lip_name
        # list:
        self.tweaks_names = [eyebrow_middle_name, eyebrow_name_1, eyebrow_name_2, eyebrow_name_3, eyebrow_name_4, \
                                squint_name_1, squint_name_2, squint_name_3,\
                                cheek_name_1, cheek_name_2, \
                                upper_lip_middle_name, upper_lip_name_1, upper_lip_name_2, lower_lip_middle_name, lower_lip_name_1, lower_lip_name_2, lip_corner_name]
        self.tweaks_string_names = ["eyebrowMiddleName", "eyebrowName1", "eyebrowName2", "eyebrowName3", "eyebrowName4", \
                                "squintName1", "squintName2", "squintName3", \
                                "cheekName1", "cheekName2", \
                                "upperLipMiddleName", "upperLipName1", "upperLipName2", "lowerLipMiddleName", "lowerLipName1", "lowerLipName2", "lipCornerName"]
    
    
    def get_tweaks_data(self):
        """ Load FacialJoints json file.
            Read its content.
            Rebuild a dictionary value string variables to current mounted language names.
            Return the preset_content
        """
        # load json file:
        founds, datas = self.ar.config.get_json_file_content(self.ar.data.facial_preset_folder)
        if founds and datas:
            for found in founds:
                if found == FACIALPRESET:
                    preset_content = datas[found]
                    break
        if preset_content:
            # rebuild dictionary using object variables:
            for stored_attr in list(preset_content):
                for side_name in list(preset_content[stored_attr]):
                    for to_node_name in list(preset_content[stored_attr][side_name]):
                        for i, item in enumerate(self.tweaks_string_names):
                            if to_node_name == item:
                                preset_content[stored_attr][side_name][self.tweaks_names[i]] = preset_content[stored_attr][side_name].pop(to_node_name)
                    if side_name == "MIDDLE":
                        preset_content[stored_attr][MIDDLE] = preset_content[stored_attr].pop(side_name)
                    elif side_name == "SIDED":
                        preset_content[stored_attr][SIDED] = preset_content[stored_attr].pop(side_name)
        return preset_content


    def create_targets_from_ui(self, *args):
        """ Get UI values and call the create_targets function.
        """
        if self.ar.data.ui_state:
            bs = cmds.checkBox('facial_connect_bs_cb', query=True, value=True)
            comb = cmds.checkBox('facial_connect_comb_cb', query=True, value=True)
            tweak = cmds.checkBox('facial_connect_tweak_only_cb', query=True, value=True)
            # call run function
            self.create_targets(from_mesh=None, base_name="Head", create_bs_node=bs, combination_targets=comb,  tweak_tgt_only=tweak)
        

    def create_targets(self, from_mesh=None, base_name="Head", create_bs_node=None, combination_targets=None, tweak_tgt_only=None):
        """ Creates the default blendShape targets used in the system by default.
        """
        if not from_mesh:
            from_mesh_items = cmds.ls(selection=True, type="transform")
            if from_mesh_items:
                for n, node in enumerate(from_mesh_items):
                    if cmds.listRelatives(from_mesh_items[n], children=True, type="mesh"): #fromMeshChildrenList
                        from_mesh = from_mesh_items[n]
                        break
        if from_mesh:
            geos, results = [], []
            for geo_base in from_mesh_items:
                prefix = base_name
                if self.ar.data.ui_state:
                    bt_continue = self.ar.data.lang['i174_continue']
                    bt_cancel = self.ar.data.lang['i132_cancel']
                    result = cmds.promptDialog(
                                                title=self.ar.data.lang['m006_name'],
                                                message=self.ar.data.lang['i144_prefix']+":",
                                                button=[bt_continue, bt_cancel],
                                                defaultButton=bt_continue,
                                                cancelButton=bt_cancel,
                                                dismissString=bt_cancel)
                    if result == bt_continue:
                        prefix = cmds.promptDialog(query=True, text=True)
                if prefix == "": # if no name provided in the promptDialog, use the geo_base name
                    prefix = geo_base
                    if "|" in geo_base:
                        prefix = geo_base[geo_base.rfind("|")+1:]
                if not prefix.endswith("_"):
                    prefix = prefix+"_"
                prefix = prefix.capitalize()
                suffix = "_Tgt"
                # get default list of targets to be created:
                targets = list(self.default_targets)
                # if the tweak_tgt_only is not checked, add facial targets to the list
                if not tweak_tgt_only:
                    targets.extend(self.facial_targets)
                    # if the combination_targets is checked, add combination targets to the list
                    if combination_targets:
                        targets.extend(self.combination_targets)
                if len(targets) > 3:
                    # create facial target group if there's more than 3 targets to be created (Base, Recept, Tweaks)
                    facial_target_grp = cmds.group(empty=True, name=prefix+"Facial_Tgt_Grp")
                target_grps = cmds.group(empty=True, name=prefix+"Tgt_Grp")
                # turn off deformers envelope to avoid incorrect base mesh duplication
                self.change_all_envelope(False)
                facial_targets = []
                created_targets = []
                for t, tgt in enumerate(targets):
                    # duplicate, rename and assign initial shader to target
                    new_geo = self.prepare_new_target(geo_base, prefix, tgt, suffix)
                    created_targets.append(new_geo)
                    if t == 0: # base target
                        cmds.setAttr(new_geo+".visibility", 0)
                        geos.append(new_geo)
                        cmds.parent(new_geo, target_grps)
                    elif t == 1: # recept target
                        geos.append(new_geo)
                        cmds.parent(new_geo, target_grps)
                    elif t == 2: # tweak target
                        geos.append(new_geo)
                        cmds.parent(new_geo, target_grps)
                    else: # facial targets
                        cmds.parent(new_geo, facial_target_grp)
                        facial_targets.append(new_geo)
                if facial_targets:
                    cmds.parent(facial_target_grp, target_grps)
                self.change_all_envelope(True)
                # if create_bs_node is checked, it will create the blendShape node connecting combination if needed
                if create_bs_node:
                    self.create_blendshape_node(geo_base, prefix, created_targets, comb_tgt=combination_targets)
            if self.ar.data.ui_state and results:
                self.ar.logger.infoWin('m085_facialConnection', 'm048_createdTgt', '\n'.join(results), 'center', 200, 350)
        else:
            mel.eval("warning \""+self.ar.data.lang["i042_notSelection"]+"\";")
        self.ar.utils.close_ui('dpFacialConnectionWindow')
    

    def prepare_new_target(self, from_mesh, prefix, tgt, suffix):
        """ Duplicate the given mesh, rename and assign initial shading to the target.
        """
        dup = cmds.duplicate(from_mesh)[0]
        new_tgt = cmds.rename(dup, prefix+tgt+suffix)
        self.ar.custom_attr.add_attr(0, [new_tgt], descendents=True) #dpID
        cmds.select(new_tgt)
        cmds.hyperShade(new_tgt, assign="initialShadingGroup")
        connection = cmds.listConnections(new_tgt+".drawOverride", destination=False, source=True, plugs=True)
        if connection:
            cmds.disconnectAttr(connection[0], new_tgt+".drawOverride")
        return new_tgt


    def get_facial_ctrl_data(self, controllers):
        """ Return the facial control data with facialList attributes.
        """
        result_data = {}
        if not controllers:
            controllers = self.ar.ctrls.get_controllers()
        if controllers:
            for ctrl in controllers:
                if cmds.objExists(ctrl+".facialList"):
                    result_data[ctrl] = self.ar.ctrls.get_items_from_string_attr(ctrl, "facialList")
        return result_data
    

    def get_bs_node_data(self, bs_items):
        """ Return the blendShape nodes data with their target.
        """        
        bs_data = {}
        if bs_items:
            for bs_node in bs_items:
                targets = cmds.listAttr(bs_node+".w", multi=True)
                if targets:
                    bs_data[bs_node] = targets
        return bs_data


    def connect_to_blendshape(self, controllers=None, bs_items=None, *args):
        """ Find all dpControl and list their facial attributes to connect into existing alias in all blendShape nodes.
        """
        results = []
        # get facialList attr from found dpAR controls
        facial_ctrl_data = self.get_facial_ctrl_data(controllers)
        # get target list from existing blendShape nodes
        if not bs_items:
            bs_items = cmds.ls(selection=False, type="blendShape")
        bs_data = self.get_bs_node_data(bs_items)
        # connect them
        if bs_data:
            if facial_ctrl_data and bs_data:
                for facial_ctrl in list(facial_ctrl_data.keys()):
                    for bs_node in list(bs_data.keys()):
                        for facial_attr in facial_ctrl_data[facial_ctrl]:
                            for target_attr in bs_data[bs_node]:
                                connect_it = False
                                if target_attr.endswith(facial_attr+"_Tgt"):
                                    connect_it = True
                                elif target_attr.endswith(facial_attr):
                                    connect_it = True
                                elif facial_attr == target_attr:
                                    connect_it = True
                                # not including here the (facial_attr in target_attr) statement to try avoid connect into combination alias
                                if connect_it:
                                    cmds.connectAttr(facial_ctrl+"."+facial_attr, bs_node+"."+target_attr, force=True)
                                    print(self.ar.data.lang['m143_connected'], facial_ctrl+"."+facial_attr, "->", bs_node+"."+target_attr)
                                    results.append(facial_ctrl+"."+facial_attr+" -> "+bs_node+"."+target_attr)
            for bs_node in list(bs_data.keys()):
                # check and connect combination targets if any
                combinations_data = self.find_comb_tgt_relatonship(bs_node)
                comb_results = self.connect_comb_targets(bs_node, combinations_data)
                if comb_results:
                    for result in comb_results:
                        results.append(result)
        if not self.ar.data.rebuilding:
            if self.ar.data.ui_state and results:
                self.ar.logger.infoWin('m085_facialConnection', 'm143_connected', '\n'.join(results), 'center', 200, 350)
        self.ar.utils.close_ui('dpFacialConnectionWindow')
    

    def connect_to_joints(self, controllers=None, *args):
        """ Connect the facial controllers attributes to the stored facial tweakers data.
        """
        self.to_ids, results = [], []
        # redefining Tweaks variables to get the tweaks name list
        self.load_tweaks_variables()
        # get joint target list
        self.joint_targets = self.get_joint_nodes(self.tweaks_names)
        if self.joint_targets:
            facial_ctrl_data = self.get_facial_ctrl_data(controllers)
            if facial_ctrl_data:
                # declaring gaming dictionary:
                tweaks_data = self.get_tweaks_data()
                if tweaks_data:
                    for facial_ctrl in list(facial_ctrl_data.keys()):
                        for facial_attr in facial_ctrl_data[facial_ctrl]:
                            # check attribute prefix like "L_" or "R_"
                            side_prefix = None
                            side_attr = facial_attr
                            if facial_attr[1] == "_":
                                side_prefix = facial_attr[0]
                                side_attr = facial_attr[2:]
                            # work with Middle, L_Middle, R_Middle or Sided data
                            for middle_or_sided in list(tweaks_data[side_attr].keys()):
                                node_datas = []
                                if middle_or_sided == MIDDLE:
                                    node_datas.append(tweaks_data[side_attr][middle_or_sided])
                                elif middle_or_sided == SIDED:
                                    data = {}
                                    for s in ["L", "R"]:
                                        if side_prefix == None or side_prefix == s:
                                            for n in list(tweaks_data[side_attr][middle_or_sided].keys()):
                                                # add prefix to the destination joint target node
                                                data[s+"_"+n] = tweaks_data[side_attr][middle_or_sided][n]
                                    node_datas.append(data)
                                else:
                                    for s in ["L", "R"]:
                                        if middle_or_sided == s+"_"+MIDDLE:
                                            if side_prefix == "L":
                                                # simple connection
                                                node_datas.append(tweaks_data[side_attr][middle_or_sided])
                                if node_datas:
                                    for node_data in node_datas:
                                        for to_node in list(node_data.keys()):
                                            for joint_target in self.joint_targets:
                                                if cmds.objExists(joint_target):
                                                    if joint_target.startswith(to_node):
                                                        # caculate factor for scaled item:
                                                        size_factor = self.get_size_factor(joint_target)
                                                        if not size_factor:
                                                            size_factor = 1
                                                        for to_attr in list(node_data[to_node].keys()):
                                                            # read stored values in order to call function to make the setup
                                                            output_min = node_data[to_node][to_attr][0]
                                                            output_max = node_data[to_node][to_attr][1]
                                                            self.create_remap_node(facial_ctrl, facial_attr, joint_target, to_attr, self.rmv_number, size_factor, output_min, output_max)
                                                            self.rmv_number = self.rmv_number+1
                                                        print(self.ar.data.lang['m143_connected'], facial_ctrl+"."+facial_attr, "->", joint_target)
                                                        results.append(facial_ctrl+"."+facial_attr+" -> "+joint_target)
                    self.ar.custom_attr.add_attr(0, self.to_ids) #dpID
                    if self.ar.data.ui_state and results:
                        self.ar.logger.infoWin('m085_facialConnection', 'm143_connected', '\n'.join(results), 'center', 200, 350)
        self.ar.utils.close_ui('dpFacialConnectionWindow')

    
    def get_joint_nodes(self, items):
        """ Load the respective items to build the joint target list (offset group node) and returns it.
        """
        self.offset_suffix = "_Ctrl_Offset_Grp"
        left_prefix = self.ar.data.lang["p002_left"]+"_"
        right_prefix = self.ar.data.lang["p003_right"]+"_"
        for item in items:
            center_name = item+self.offset_suffix
            left_name   = left_prefix+item+self.offset_suffix
            right_name  = right_prefix+item+self.offset_suffix
            if cmds.objExists(center_name):
                self.joint_targets.append(center_name)
            if cmds.objExists(left_name):
                self.joint_targets.append(left_name)
            if cmds.objExists(right_name):
                self.joint_targets.append(right_name)
        return self.joint_targets
    
    
    def get_size_factor(self, to_node):
        """ Get the child control size value and return it.
        """
        children = cmds.listRelatives(to_node, children=True, type="transform")
        if children:
            for child in children:
                if cmds.objExists(child+".dpControl"):
                    if cmds.getAttr(child+".dpControl") == 1:
                        if cmds.objExists(child+".size"):
                            return cmds.getAttr(child+".size") #sizeValue


    def create_remap_node(self, from_node, from_attr, joint_target, to_attr, number, size_factor, output_min=0, output_max=1, input_min=0, input_max=1):
        """ Creates the nodes to remap values and connect it to final output (joint_target) item.
        """
        from_node_name = self.ar.utils.extract_suffix(from_node)
        remap = cmds.createNode("remapValue", name=from_node_name+"_"+from_attr+"_"+str(number).zfill(2)+"_"+to_attr.upper()+"_RmV")
        self.to_ids.append(remap)
        out_max_attr = joint_target.split(self.offset_suffix)[0]+"_"+str(number).zfill(2)+"_"+to_attr.upper()
        if not cmds.objExists(from_node+"."+out_max_attr):
            cmds.addAttr(from_node, longName=out_max_attr, attributeType="float", defaultValue=output_max, keyable=False)
        if "t" in to_attr:
            if not cmds.objExists(from_node+".size_factor"):
                cmds.addAttr(from_node, longName="size_factor", attributeType="float", defaultValue=size_factor, keyable=False)
            md = cmds.createNode("multiplyDivide", name=from_node_name+"_"+from_attr+"_"+str(number).zfill(2)+"_"+to_attr.upper()+"_SizeFactor_MD")
            self.to_ids.append(md)
            cmds.connectAttr(from_node+"."+out_max_attr, md+".input1X", force=True)
            cmds.connectAttr(from_node+".size_factor", md+".input2X", force=True)
            cmds.connectAttr(md+".outputX", remap+".outputMax", force=True)
        else:
            cmds.connectAttr(from_node+"."+out_max_attr, remap+".outputMax", force=True)
        cmds.setAttr(remap+".inputMin", input_min)
        cmds.setAttr(remap+".inputMax", input_max)
        cmds.setAttr(remap+".outputMin", output_min)
        cmds.connectAttr(from_node+"."+from_attr, remap+".inputValue", force=True)
        # check if there's an input connection and create a plusMinusAverage if we don't have one to connect in:
        connections = cmds.listConnections(joint_target+"."+to_attr, destination=False, source=True, plugs=False)
        if connections:
            if cmds.objectType(connections[0]) == "plusMinusAverage":
                inputs = cmds.listConnections(connections[0]+".input1D", destination=False, source=True, plugs=False)
                cmds.connectAttr(remap+".outValue", connections[0]+".input1D["+str(len(inputs))+"]", force=True)
            else:
                if cmds.objectType(connections[0]) == "unitConversion":
                    connected_attr = cmds.listConnections(connections[0]+".input", destination=False, source=True, plugs=True)[0]
                else:
                    connected_attr = cmds.listConnections(joint_target+"."+to_attr, destination=False, source=True, plugs=True)[0]
                pma = cmds.createNode("plusMinusAverage", name=joint_target+"_"+to_attr.upper()+"_PMA")
                self.to_ids.append(pma)
                cmds.connectAttr(connected_attr, pma+".input1D[0]", force=True)
                cmds.connectAttr(remap+".outValue", pma+".input1D[1]", force=True)
                cmds.connectAttr(pma+".output1D", joint_target+"."+to_attr, force=True)
                if cmds.objectType(connections[0]) == "unitConversion":
                    cmds.delete(connections[0])
        else:
            cmds.connectAttr(remap+".outValue", joint_target+"."+to_attr, force=True)


    def node_has_envelope(self, node):
        """ Check if the given node has an envelope attribute. Avoid tweak nodes.
        """
        if cmds.nodeType(node) != "tweak":
            return cmds.attributeQuery('envelope', node=node, exists=True)


    def change_all_envelope(self, value=False):
        """ Turn on/off envelope attribute in the scene, to avoind miss deformation in base mesh duplication.
        """
        checked_items = []
        all_enveloped_nodes = list(filter(self.node_has_envelope, cmds.ls())) #all
        all_valid_envelope_nodes = list(filter(self.ar.utils.envelope_is_valid, all_enveloped_nodes))
        checked_items.extend(all_valid_envelope_nodes)
        if checked_items:
            if value == True:
                for node in checked_items:
                    cmds.setAttr(f"{node}.envelope", 1)
            if value == False:
                for node in checked_items:
                    cmds.setAttr(f"{node}.envelope", 0)
            

    def create_blendshape_node(self, from_mesh, prefix, targets, comb_tgt=False):
        """ Create a blendShape node connecting all created target meshes.
        """
        recept_target = targets[1]
        tweak_target = targets[2]
        targets_for_recept = targets[2:]
        # create Recept blendshape node with facial targets
        bs_recept = cmds.blendShape(targets_for_recept, recept_target, frontOfChain=True, name=prefix+self.recept_bs_suffix)[0]
        # create blendShape node from recept to main mesh
        bs_main = cmds.blendShape(recept_target, from_mesh, frontOfChain=True, name=prefix+self.bs_suffix)[0]
        # store prefix to define names further
        cmds.addAttr(bs_recept, longName="dpPrefix", dataType="string")
        cmds.addAttr(bs_main, longName="dpPrefix", dataType="string")
        cmds.setAttr(bs_recept+".dpPrefix", prefix, type="string")
        cmds.setAttr(bs_main+".dpPrefix", prefix, type="string")
        # turning on the targets to make it easier to work
        cmds.setAttr(f"{bs_main}.{recept_target}", 1)
        cmds.setAttr(f"{bs_recept}.{tweak_target}", 1)
        if comb_tgt:
            # check and connect combination targets if any
            combinations_data = self.find_comb_tgt_relatonship(bs_recept)
            self.connect_comb_targets(bs_recept, combinations_data)


    def find_comb_tgt_relatonship(self, bs_node):
        """ Find combination targets in the given blendShape node and their respective driver targets.
        """
        prefix = None
        comb_target_relationship_data = {}
        if bs_node:
            targets = cmds.listAttr(bs_node+".w", multi=True) or []
            if "dpPrefix" in cmds.listAttr(bs_node):
                prefix = cmds.getAttr(bs_node+".dpPrefix")
        if prefix: #only pass if the blendShape node was created by this current tool version
            base_targets = []
            combo_targets = []
            # separate in lists between base or combination target to further classification
            for target in targets:
                target_check = self.decompose_tgt_name(target, prefix)
                if target_check[0] == True:
                    combo_targets.append(target)
                else:
                    base_targets.append(target)
            for comb_name in combo_targets:
                comb_tgt_raw = self.decompose_tgt_name(comb_name, prefix)[-1]
                comb_lower = comb_tgt_raw.lower()
                # splitting using "comb_" to get before_comb name e.g: l_mouth and combination part e.g. smilewide
                before_comb, comb_part = comb_lower.split("comb_")
                drivers = []
                for base_name in base_targets:
                    base_name_attr = self.decompose_tgt_name(base_name, prefix)[-1]
                    base_lower = base_name_attr.lower()
                    # when the base target match the combination part prefix, it will replace same prefix for blank
                    # it will be remained only the suffix to compare e.g smile
                    base_suffix = base_lower.replace(before_comb, "")
                    if base_suffix and base_suffix in comb_part: # if it finds the suffix in the combination part, it's a driver
                        drivers.append(base_name)
                    if len(drivers) >= 2: # its necessary more than two drivers per combination target
                        comb_target_relationship_data[comb_name] = drivers
            return comb_target_relationship_data
    

    def get_blendshape_tgt_index(self, bs_node, target_name, *args):
        """ Get the blendShape target index from its name.
        """         
        alias = cmds.aliasAttr(bs_node, q=True) or []
        for i in range(0, len(alias), 2):
            if alias[i] == target_name:
                return int(alias[i+1].split("[")[-1][:-1])
        return None
    

    def connect_comb_targets(self, bs_node, combinations_data, *args):
        """ Connect combination targets in the given blendShape node using the combinations_data information.
        """
        results = []
        if combinations_data:
            for comb_tgt, drivers in combinations_data.items():
                comb_index = self.get_blendshape_tgt_index(bs_node, comb_tgt)
                driver_indexes = []
                for driver_tgt in drivers:
                    driver_index = self.get_blendshape_tgt_index(bs_node, driver_tgt)
                    driver_indexes.append(driver_index) 
                input_weights = cmds.combinationShape(query=True, blendShape=bs_node, combinationTargetIndex=comb_index, exist=True)    
                # check if combination target is already connected
                if not input_weights:
                    # add combination only if the target is not locked
                    if not cmds.getAttr(bs_node+"."+comb_tgt, lock=True):
                        cmds.combinationShape(blendShape=bs_node, combineMethod=0, combinationTargetIndex=comb_index, driverTargetIndex=driver_indexes)
                        print(self.ar.data.lang['m143_connected'], drivers[0]+" + "+drivers[1], "->", comb_tgt)
                        results.append(str(drivers[0]+" + "+drivers[1]+" -> "+comb_tgt))
        return results


    def decompose_tgt_name(self, tgt_name, prefix, *args):
        """ Decomposes a target name into its side and if it is a combination target, also [-1] will return the raw tgt name.
            e.g. Head_L_MouthSmile -> False, L, L_MouthSmile
        """
        comb = None
        side = None
        if tgt_name:
            if prefix:
                tgt_name = tgt_name.replace(prefix, "")
            splitted_name = tgt_name.split("_")[:-1]
            if len(splitted_name) > 2: # combination target
                side = splitted_name[0]    
                comb_region = splitted_name[1]
                raw_tgt = splitted_name[2]
                tgt = f"{side}_{comb_region}_{raw_tgt}"
                comb = True   
            elif len(splitted_name) == 1: # symetrical target
                comb = False
                side = False
                tgt = splitted_name[0]
            elif len(splitted_name) == 2: # sided target
                comb = False
                side = splitted_name[0]    
                raw_tgt = splitted_name[1]
                tgt = f"{side}_{raw_tgt}"
        return comb, side, tgt
    

    def recreate_targets(self, *args):
        """ Rebuild the blendShape targets from an old mesh to a new one.
        """
        selections = cmds.ls(selection=True, type="transform")
        if selections and len(selections) == 2:
            if self.ar.utils.check_geometry(selections[0]) and self.ar.utils.check_geometry(selections[1]):
                old_mesh = selections[0]
                new_mesh = selections[1]
                bs_node = cmds.ls(cmds.listHistory(old_mesh), type="blendShape")
                if bs_node:
                    targets = cmds.listAttr(bs_node[0]+".w", multi=True)
                    if targets:
                        self.ar.utils.set_progress(self.ar.data.lang['c110_start'], self.ar.data.lang["m265_recreateTargets"], max=len(targets), add_one=False, add_number=False)
                        reconnect_items = []
                        cmds.select([new_mesh, old_mesh])
                        mel.eval("CreateWrap;")
                        target_grps = cmds.group(name="New_Tgt_Grp", empty=True)
                        # clear selection
                        cmds.select(clear=True)
                        new_targets = []
                        for item in targets:
                            self.ar.utils.set_progress('Target: '+item)
                            if not item == old_mesh:
                                has_connection = cmds.listConnections(bs_node[0]+"."+item, source=True, destination=False, plugs=True)
                                if has_connection:
                                    cmds.disconnectAttr(has_connection[0], bs_node[0]+"."+item)
                                    reconnect_items.append(has_connection[0])
                                else:
                                    reconnect_items.append(None)
                                # set blendShape slider as 1
                                cmds.setAttr(bs_node[0]+"."+item, 1)
                                # renaming old target
                                cmds.rename(item, item+"_Old")
                                tgt = cmds.duplicate(new_mesh, name=item)[0]
                                cmds.parent(tgt, target_grps)
                                new_targets.append(tgt)
                                # back to zero
                                cmds.setAttr(bs_node[0]+"."+item, 0)
                                if has_connection:
                                    cmds.connectAttr(has_connection[0], bs_node[0]+"."+item)
                                # clear undo
                                mel.eval("flushUndo;")
                        cmds.delete(new_mesh, constructionHistory=True)
                        cmds.rename(bs_node[0], bs_node[0]+"_Old")
                        cmds.blendShape(new_targets, new_mesh, topologyCheck=False, name=bs_node[0])
                        for p, plug in enumerate(reconnect_items):
                            if plug:
                                cmds.connectAttr(plug, bs_node[0]+"."+new_targets[p], force=True)
                        if cmds.objExists(old_mesh+"Base"):
                            cmds.delete(old_mesh+"Base")
                        self.ar.utils.set_progress(end_it=True)
                        cmds.select(clear=True)
