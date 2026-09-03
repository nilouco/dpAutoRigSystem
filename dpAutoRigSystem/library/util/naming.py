# importing libraries:
from maya import cmds
from maya import OpenMaya
import re
import unicodedata



class Naming(object):
    def __init__(self, ar):
        self.ar = ar


    def find_last_number(self, name="dpGuideNet", attr="guideNumber", pad=3):
        """ Returns a padding string of the number of network node in the scene or zero.
        """
        nodes = self.ar.utils.get_network_by_attr(name)
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
            nodes = self.ar.utils.get_network_by_attr("dpGuideNet")
        else:
            nodes = cmds.ls(selection=False, transforms=True)
        if nodes:
            for node in nodes:
                if cmds.objExists(node+"."+type_name):
                    if cmds.getAttr(node+"."+type_name) == class_name:
                        numbers.append(class_name)
        # try check if there is a masterGrp and get its counter:
        all_grp = self.ar.utils.get_all_grp()
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


    def get_attr_name_lower(self, side, name):
        """ Return the composed name for attributes starting with lower case.
        """
        attr_name_lower = name
        if side:
            attr_name_lower = side[0]+name
        attr_name_lower = attr_name_lower[0].lower()+attr_name_lower[1:]
        return attr_name_lower


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


    def get_duplicated_names(self):
        """ Returns a list of duplicated names.
            Returns False if there are only unique names.
        """
        return [n for n in cmds.ls(selection=False, shortNames=True) if "|" in n] or False


    def get_mdagpath_by_name(self, item):
        """ Returns the OpenMaya MDagPath of the given item name.
        """
        selection = OpenMaya.MSelectionList()
        selection.add(item)
        dagpath = OpenMaya.MDagPath()
        selection.getDagPath(0, dagpath)
        return dagpath


    def get_translated_names(self, name, from_lang="english"):
        custom_name = ""
        splitted_names = name.split("_")
        for n, splitted_name in enumerate(splitted_names):
            # splits capital letters and numbers:
            capitals = re.findall(r'\d+|[A-Z][a-z]*', splitted_name)
            if capitals:
                for capitalized_name in capitals:
                    capitalize = False
                    lang_names = self.ar.utils.get_keys_by_value(self.ar.data.lang_preset_data[from_lang], capitalized_name)
                    if not lang_names:
                        lang_names = self.ar.utils.get_keys_by_value(self.ar.data.lang_preset_data[from_lang], capitalized_name.lower())
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
