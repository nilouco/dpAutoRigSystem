# importing libraries:
from maya import cmds
from maya import mel
import os
import getpass
import datetime

DPCONTROL = "dpControl"
SNAPSHOT_SUFFIX = "_Snapshot_Crv"
HEADDEFINFLUENCE = "dpHeadDeformerInfluence"
JAWDEFINFLUENCE = "dpJawDeformerInfluence"



class Controllers(object):
    def __init__(self, ar):
        """ Initialize the module class defining variables to use creating preset controls.
        """
        # defining variables:
        self.ar = ar
        self.load_variables()


    def load_variables(self):
        """ Just load class variables here.
        """
        self.attr_value_data = {}
        self.ignore_default_value_attrs = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ", "visibility", "rotateOrder", "scaleCompensate"]
        self.shape_types = ['nurbsCurve', 'nurbsSurface', 'mesh', 'subdiv']
        self.long_attr_data = {'tx': 'translateX',
                                'ty': 'translateY',
                                'tz': 'translateZ',
                                'rx': 'rotateX',
                                'ry': 'rotateY',
                                'rz': 'rotateZ',
                                'sx': 'scaleZ',
                                'sy': 'scaleY',
                                'sz': 'scaleZ',
                                'v': 'visibility'}
        self.declare_colors()


    def get_dpar_temp_grp(self, temp_grp=None):
        """ Create the dpAR temp group if it doesn't exists.
        """
        if not temp_grp:
            temp_grp = self.ar.data.temp_grp
        if not cmds.objExists(temp_grp):
            hidden = not self.ar.data.display_temp_grp #invert to apply
            cmds.group(name=temp_grp, empty=True)
            cmds.setAttr(temp_grp+".visibility", 0)
            cmds.setAttr(temp_grp+".template", 1)
            cmds.setAttr(temp_grp+".hiddenInOutliner", hidden)
            self.set_lock_hide([temp_grp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])
        return temp_grp


    def declare_colors(self):
        """ Just declare color lists and dictionary to use as override color data.
        self.colors = [  [0.627, 0.627, 0.627],
                            [0, 0, 0],
                            [0.247, 0.247, 0.247],
                            [0.498, 0.498, 0.498],
                            [0.608, 0, 0.157],
                            [0, 0.016, 0.373],
                            [0, 0, 1],
                            [0, 0.275, 0.094],
                            [0.145, 0, 0.263],
                            [0.780, 0, 0.78],
                            [0.537, 0.278, 0.2],
                            [0.243, 0.133, 0.122],
                            [0.600, 0.145, 0],
                            [1, 0, 0],
                            [0, 1, 0],
                            [0, 0.255, 0.6],
                            [1, 1, 1],
                            [1, 1, 0],
                            [0.388, 0.863, 1],
                            [0.263, 1, 0.635],
                            [1, 0.686, 0.686],
                            [0.890, 0.675, 0.475],
                            [1, 1, 0.384],
                            [0, 0.6, 0.325],
                            [0.627, 0.412, 0.188],
                            [0.620, 0.627, 0.188],
                            [0.408, 0.627, 0.188],
                            [0.188, 0.627, 0.365],
                            [0.188, 0.627, 0.627],
                            [0.188, 0.404, 0.627],
                            [0.435, 0.188, 0.627],
                            [0.627, 0.188, 0.412] ]
        """
        self.colors = self.get_colors()
        self.colors_data = {
                            "none": 0,
                            "yellow": 17,
                            "red": 13,
                            "blue": 6,
                            "cyan": 18,
                            "green": 7,
                            "darkRed": 4,
                            "darkBlue": 15,
                            "white": 16,
                            "black": 1,
                            "gray": 3,
                            "bonina": [0.38, 0, 0.15]
                        }
    

    def get_colors(self):
        """ Return a list of Maya's colors.
        """
        #Manually add the "none" color
        colors = [[0.627, 0.627, 0.627]]
        #WARNING --> color index in maya start to 1
        colors += [cmds.colorIndex(iColor, q=True) for iColor in range(1,32)]
        return colors


    def get_guides_by_attr(self, item, attr="guideColorIndex"):
        """ Return the guide children list if it is a guide node.
        """
        guides = []
        if attr in cmds.listAttr(item):
            guides.append(item)
            if "__" in item and ":" in item and item.endswith("Guide_Base"):
                space_name = item.split(":")[0]
                children = cmds.listRelatives(item, children=True, allDescendents=True, noIntermediate=True, type=self.shape_types)
                if children:
                    for child in children:
                        if child.startswith(space_name):
                            guides.append(child)
        return guides


    # CONTROLS functions:
    def color_shape(self, items, color, rgb=False, outliner=False, instance=None, *args):
        """ Create a color override for all shapes from the items.
        """
        # define colorIndex value
        color_index = color
        if rgb:
            if color in list(self.colors_data):
                color = self.colors_data[color]
        elif color in list(self.colors_data):
            color_index = self.colors_data[color]
        if not items:
            items = cmds.ls(selection=True)
        # find shapes and apply the color override:
        if items:
            for item in items:
                if outliner:
                    self.set_color_override(item, color, color_index, rgb, outliner)
                else:
                    item_type = cmds.objectType(item)
                    # verify if the object is the shape type:
                    if item_type in self.shape_types:
                        self.set_color_override(item, color, color_index, rgb, instance=instance)
                    # verify if the object is a transform type:
                    elif item_type == "transform":
                        # try get guide shape list
                        items = self.get_guides_by_attr(item)
                        if items:
                            if rgb:
                                cmds.setAttr(item+".guideColorIndex", -1)
                                cmds.setAttr(item+".guideColorR", color[0])
                                cmds.setAttr(item+".guideColorG", color[1])
                                cmds.setAttr(item+".guideColorB", color[2])
                            else:
                                cmds.setAttr(item+".guideColorIndex", color_index)
                                cmds.setAttr(item+".guideColorR", self.colors[color_index][0])
                                cmds.setAttr(item+".guideColorG", self.colors[color_index][1])
                                cmds.setAttr(item+".guideColorB", self.colors[color_index][2])
                        else:
                            # find all shapes children of the transform object:
                            items = cmds.listRelatives(item, shapes=True, children=True, fullPath=True)
                        if items:
                            for shape in items:
                                self.set_color_override(shape, color, color_index, rgb, instance=instance)


    def set_color_override(self, item, color, color_index, rgb, outliner=False, instance=None):
        """ Set the color for the given node and color data.
        """
        if outliner:
            cmds.setAttr(item+".useOutlinerColor", 1)
            cmds.setAttr(item+".outlinerColor.outlinerColorR", color[0])
            cmds.setAttr(item+".outlinerColor.outlinerColorG", color[1])
            cmds.setAttr(item+".outlinerColor.outlinerColorB", color[2])
            mel.eval('source AEdagNodeCommon;')
            mel.eval("AEdagNodeCommonRefreshOutliners();")
        else:
            # set override as enable:
            cmds.setAttr(item+".overrideEnabled", 1)
            # set color override:
            if rgb:
                cmds.setAttr(item+".overrideRGBColors", 1)
                cmds.setAttr(item+".overrideColorR", color[0])
                cmds.setAttr(item+".overrideColorG", color[1])
                cmds.setAttr(item+".overrideColorB", color[2])
                if instance:
                    if self.ar.data.ui_state:
                        cmds.button(f"{instance.number_name}_plus_color_bt", edit=True, backgroundColor=[color[0], color[1], color[2]])
                        if not instance.guide_base in cmds.ls(selection=True):
                            cmds.button(f"{instance.number_name}_select_bt", edit=True, backgroundColor=[color[0], color[1], color[2]])
            else:
                cmds.setAttr(item+".overrideRGBColors", 0)
                cmds.setAttr(item+".overrideColor", color_index)
                if instance:
                    if self.ar.data.ui_state:
                        cmds.button(f"{instance.number_name}_plus_color_bt", edit=True, backgroundColor=[self.colors[color_index][0], self.colors[color_index][1], self.colors[color_index][2]])
                        if not instance.guide_base in cmds.ls(selection=True):
                            cmds.button(f"{instance.number_name}_select_bt", edit=True, backgroundColor=[self.colors[color_index][0], self.colors[color_index][1], self.colors[color_index][2]])


    def remove_color(self, items, *args):
        """ Just remove color of given list or selected nodes.
        """
        if not items:
            items = cmds.ls(selection=True)
        if items:
            for item in items:
                guides = self.get_guides_by_attr(item)
                if guides:
                    for guide in guides:
                        if not guide in items:
                            items.append(guide)
            for item in items:
                is_guide = False
                if "Guide" in item:
                    self.color_shape([item], "blue")
                    is_guide = True
                if "Guide_Base" in item:
                    self.color_shape([item], "yellow")
                    is_guide = True
                if "Guide_Base_RadiusCtrl" in item:
                    self.color_shape([item], "cyan")
                    is_guide = True
                if not is_guide or not cmds.objectType(item) in self.shape_types:
                    remove_items = [item]
                    remove_items.extend(cmds.listRelatives(item, children=True, shapes=True) or [])
                    for node in remove_items:
                        cmds.setAttr(node+".overrideEnabled", 0)
                        cmds.setAttr(node+".overrideRGBColors", 0)
                        cmds.setAttr(node+".useOutlinerColor", 0)
                if "guideColorIndex" in cmds.listAttr(item):
                    cmds.setAttr(item+".guideColorIndex", 0)
                    cmds.setAttr(item+".guideColorR", self.colors[0][0])
                    cmds.setAttr(item+".guideColorG", self.colors[0][1])
                    cmds.setAttr(item+".guideColorB", self.colors[0][2])


    def get_current_rgb_color(self, item, outliner=False, *args):
        """ Return the current guide RGB color or outliner override color.
        """
        if outliner:
            return [cmds.getAttr(item+".outlinerColor.outlinerColor"+attr) for attr in ['R', 'G', 'B']]
        else:
            return [cmds.getAttr(item+".overrideColor"+attr) for attr in ['R', 'G', 'B']]
        

    def get_guide_rgb_colors(self, instance, *args):
        """ Return the guide RGB color list.
        """
        current_rgb_items = []
        for attr in ['R', 'G', 'B']:
            if "guideColor"+attr in cmds.listAttr(instance.guide_base):
                current_rgb_items.append(cmds.getAttr(instance.guide_base+".guideColor"+attr))
            else:
                break
        return current_rgb_items


    def set_color_rgb_by_ui(self, items=None, slider=None, instance=None, *args):
        """ Read from UI the rgb color to set override of given list or selected nodes.
        """
        if not items:
            items = cmds.ls(selection=True)
        if items:
            if slider and cmds.colorSliderGrp(slider, query=True, exists=True):
                self.color_shape(items, cmds.colorSliderGrp(slider, query=True, rgbValue=True), rgb=True, instance=instance)


    def set_color_outliner_by_ui(self, items=None, slider=None, *args):
        """ Read from UI the rgb color to set override of given list or selected nodes.
        """
        if not items:
            items = cmds.ls(selection=True)
        if items:
            if slider and cmds.colorSliderGrp(slider, query=True, exists=True):
                self.color_shape(items, cmds.colorSliderGrp(slider, query=True, rgbValue=True), outliner=True)


    def rename_shape(self, transforms):
        """Find shapes, rename them to #Shapes and return the results.
        """
        results = []
        for transform in transforms:
            # list all children shapes:
            children_shapes = cmds.listRelatives(transform, shapes=True, children=True, fullPath=True)
            if children_shapes:
                for i, child in enumerate(children_shapes):
                    shape_name = transform+str(i)+"Shape"
                    shape = cmds.rename(child, shape_name)
                    results.append(shape)
                cmds.select(clear=True)
            else:
                print("There are not children shape to rename inside of:", transform)
        return results


    def direct_connect(self, from_item, to_item, attributes=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], f=True):
        """Connect attributes from list directely between two objects given.
        """
        if cmds.objExists(from_item) and cmds.objExists(to_item):
            for attr in attributes:
                try:
                    # connect attributes:
                    cmds.connectAttr(from_item+"."+attr, to_item+"."+attr, force=f)
                except:
                    print("Error: Cannot connect", to_item, ".", attr, "directely.")


    def set_lock_hide(self, items, attributes, l=True, k=False, cb=False):
        """Set lock or hide to attributes for object in lists.
        """
        if items and attributes:
            for item in items:
                for attr in attributes:
                    try:
                        # set lock and hide of given attributes:
                        cmds.setAttr(item+"."+attr, lock=l, keyable=k, channelBox=cb)
                    except:
                        print("Error: Cannot set", item, ".", attr, "as lock=", l, "and keyable=", k, "and channelBox=", cb)


    def set_non_keyable(self, items, attributes):
        """Set as nonKeyable to attributes for the given object list.
        """
        if items and attributes:
            for item in items:
                for attr in attributes:
                    if attr in cmds.listAttr(item):
                        try:
                            # set lock and hide of given attributes:
                            cmds.setAttr(item+"."+attr, keyable=False, channelBox=True)
                        except:
                            print("Error: Cannot set", item, ".", attr, "as nonKeayble, sorry.")


    def set_not_renderable(self, items):
        """Receive a list of objects, find its shapes if necessary and set all as not renderable.
        """
        # declare a list of attributes for render:
        render_attrs = ["castsShadows", "receiveShadows", "motionBlur", "primaryVisibility", "smoothShading", "visibleInReflections", "visibleInRefractions", "doubleSided", "miTransparencyCast", "miTransparencyReceive", "miReflectionReceive", "miRefractionReceive", "miFinalGatherCast", "miFinalGatherReceive"]
        # find all children shapes:
        if items:
            for item in items:
                item_type = cmds.objectType(item)
                # verify if the object is the shape type:
                if item_type in self.shape_types:
                    # set attributes as not renderable:
                    for attr in render_attrs:
                        try:
                            cmds.setAttr(item+"."+attr, 0)
                        except:
                            #print("Error: Cannot set not renderable ", attr, "as zero for", item)
                            pass
                # verify if the object is a transform type:
                elif item_type == "transform":
                    # find all shapes children of the transform object:
                    shapes = cmds.listRelatives(item, shapes=True, children=True)
                    if shapes:
                        for shape in shapes:
                            # set attributes as not renderable:
                            for attr in render_attrs:
                                try:
                                    cmds.setAttr(shape+"."+attr, 0)
                                except:
                                    #print("Error: Cannot set not renderable ", attr, "as zero for", shape)
                                    pass


    def create_simple_ribbon(self, name='ribbon', total_joints=6, joint_label_number=0, joint_label_name="SimpleRibbon"):
        """ Creates a Ribbon system.
            Receives the total number of joints to create.
            Returns the ribbon nurbs plane, the joints groups and joints created.
        """
        # create a ribbon_nurbs_plane:
        ribbon_nurbs_plane = cmds.nurbsPlane(name=name+"Ribbon_NP", constructionHistory=False, object=True, polygon=0, axis=(0, 1, 0), width=1, lengthRatio=8, patchesV=total_joints)[0]
        # get the ribbon_nurbs_plane shape:
        ribbon_nurbs_plane_shape = cmds.listRelatives(ribbon_nurbs_plane, shapes=True, children=True)[0]
        # make this ribbon_nurbs_plane as template, invisible and not renderable:
        cmds.setAttr(ribbon_nurbs_plane+".template", 1)
        cmds.setAttr(ribbon_nurbs_plane+".visibility", 0)
        self.set_not_renderable([ribbon_nurbs_plane_shape])
        # make this ribbon_nurbs_plane as not skinable from dpAR_UI:
        self.ar.utils.add_attr_to_items([ribbon_nurbs_plane], self.ar.skin.ignore_skinning_attr)
        # create groups to be used as a root of the ribbon system:
        ribbon_grp = cmds.group(ribbon_nurbs_plane, n=name+"_Rbn_RibbonJoint_Grp")
        # create joints:
        joints, joint_grps = [], []
        for j in range(total_joints+1):
            # create pointOnSurfaceInfo:
            infor_node = cmds.createNode('pointOnSurfaceInfo', name=name+str(j+1)+"_POSI")
            self.ar.custom_attr.add_attr(0, [infor_node]) #dpID
            # setting parameters worldSpace, U and V:
            cmds.connectAttr(ribbon_nurbs_plane_shape+".worldSpace[0]", infor_node+".inputSurface")
            cmds.setAttr(infor_node+".parameterV", ((1/float(total_joints))*j) )
            cmds.setAttr(infor_node+".parameterU", 0.5)
            # create and parent groups to calculate:
            pos_grp = cmds.group(n=name+"Pos"+str(j+1)+"_Grp", empty=True)
            up_grp  = cmds.group(n=name+"Up"+str(j+1)+"_Grp", empty=True)
            aim_grp = cmds.group(n=name+"Aim"+str(j+1)+"_Grp", empty=True)
            cmds.parent(up_grp, aim_grp, pos_grp, relative=True)
            # connect groups translations:
            cmds.connectAttr(infor_node+".position", pos_grp+".translate", force=True)
            cmds.connectAttr(infor_node+".tangentU", up_grp+".translate", force=True)
            cmds.connectAttr(infor_node+".tangentV", aim_grp+".translate", force=True)
            # create joint:
            cmds.select(clear=True)
            joint = cmds.joint(name=name+"_%02d_Jnt"%(j+1))
            joints.append(joint)
            cmds.addAttr(joint, longName='dpAR_joint', attributeType='float', keyable=False)
            # parent the joint to the groups:
            cmds.parent(joint, pos_grp, relative=True)
            joint_grp = cmds.group(joint, name=name+"Joint"+str(j+1)+"_Grp")
            joint_grps.append(joint_grp)
            # create aimConstraint from aim_grp to joint_grp:
            cmds.aimConstraint(aim_grp, joint_grp, offset=(0, 0, 0), weight=1, aimVector=(0, 1, 0), upVector=(0, 0, 1), worldUpType="object", worldUpObject=up_grp, n=name+"Ribbon"+str(j)+"_AiC" )
            # parent this ribbonPos to the ribbon_grp:
            cmds.parent(pos_grp, ribbon_grp, absolute=True)
            # joint labelling:
            self.ar.naming.set_joint_label(joint, joint_label_number, 18, joint_label_name+"_%02d"%(j+1))
            self.ar.utils.add_attr_to_items([pos_grp, up_grp, aim_grp, joint_grp], self.ar.utils.ignore_transform_io_attr)
        self.ar.utils.add_attr_to_items([ribbon_grp, ribbon_nurbs_plane], self.ar.utils.ignore_transform_io_attr)
        return [ribbon_nurbs_plane, ribbon_nurbs_plane_shape, joint_grps, joints]


    def get_controller_node_by_id(self, ctrl_type):
        """ Find and return node list with ctrl_type in its attribute.
        """
        controllers = []
        transforms = cmds.ls(selection=False, type="transform")
        for item in transforms:
            if "controlID" in cmds.listAttr(item):
                if cmds.getAttr(item+".controlID") == ctrl_type:
                    controllers.append(item)
        return controllers


    def get_controller_module_by_id(self, ctrl_type):
        """ Check the control type reading the loaded dictionary from preset json file.
            Return the respective control module name by id.
        """
        ctrl_module = self.ar.data.curve_preset[ctrl_type]['type']
        return ctrl_module


    def get_controller_degree_by_id(self, ctrl_type):
        """ Check the control type reading the loaded dictionary from preset json file.
            Return the respective control module name by id.
        """
        ctrl_module = self.ar.data.curve_preset[ctrl_type]['degree']
        return ctrl_module


    def create_controller(self, ctrl_type, ctrl_name, r=1, d=1, dir='+Y', rot=(0, 0, 0), corrective=False, head_def=0, guide_source=None, parent_tag=None):
        """ Create and return a curve to be used as a control.
            Check if the ctrl_type starts with 'id_###_Abc' and get the control type from json file.
            Otherwise, check if ctrl_type is a valid control curve object in order to create it.
        """
        # get control module:
        if ctrl_type.startswith("id_"):
            ctrl_module = self.get_controller_module_by_id(ctrl_type)
            # get degree:
            if d == 0:
                d = self.get_controller_degree_by_id(ctrl_type)
        else:
            ctrl_module = ctrl_type
            if d == 0:
                d = 1
        # get control instance:
        ctrl_instance = self.ar.config.get_instance(ctrl_module, [self.ar.data.curve_simple_folder, self.ar.data.curve_combined_folder])
        if ctrl_instance:
            # create curve
            curve = ctrl_instance.cv_main(False, ctrl_type, ctrl_name, r, d, dir, rot, 1)
            if corrective:
                self.add_corrective_attrs(curve)
                self.ar.job.start_corrective_edit_mode([curve])
            if not head_def == 0:
                self.add_def_influence_attrs(curve, head_def)
            if guide_source:
                cmds.addAttr(curve, longName="guide_source", dataType="string")
                cmds.setAttr(curve+".guide_source", guide_source, type="string")
            if parent_tag:
                cmds.connectAttr(parent_tag+".message", curve+".parentTag", force=True)
            return curve


    def add_def_influence_attrs(self, curve, def_influence_type):
        """ Add specific attribute to be deformed by FFD
            If def_influence_type is equal 1, it will be deformed by the headDeformer
            If def_influence_type is equal 2, it will be deformed by the jawDeformer
            If def_influence_type is equal 3, it will be deformed by headDeformer and jawDeformer
        """
        if curve:
            if def_influence_type == 1 or def_influence_type == 3:
                cmds.addAttr(curve, longName=HEADDEFINFLUENCE, attributeType="bool", defaultValue=1)
            if def_influence_type == 2 or def_influence_type == 3:
                cmds.addAttr(curve, longName=JAWDEFINFLUENCE, attributeType="bool", defaultValue=1)


    def create_curve_locator(self, ctrl_name, r=1, d=1, guide=False, rot=(0, 0, 0), color="blue", cvType="Locator", pin=True):
        """ Create and return a create_curve_locator curve to be usually used in the guideSystem.
        """
        curve_instance = self.ar.config.get_instance(cvType, [self.ar.data.curve_simple_folder, self.ar.data.curve_combined_folder])
        curve = curve_instance.cv_main(False, cvType, ctrl_name, r, d, '+Y', rot, 1, guide)
        if guide:
            self.add_guide_attrs(curve, color, pin)
        return curve


    #@utils.profiler
    def create_joint_locator(self, ctrl_name, r=0.3, d=1, rot=(0, 0, 0), guide=True, pin=True):
        """ Create and return a cvJointLocator curve to be usually used in the guideSystem.
        """
        # create locator curve:
        cv_loc = self.create_curve_locator(ctrl_name+"_CvLoc", r, d)
        # create arrow curves:
        cv_arrow_1 = cmds.curve(n=ctrl_name+"_CvArrow1", d=3, p=[(-0.1*r, 0.9*r, 0.2*r), (-0.1*r, 0.9*r, 0.23*r), (-0.1*r, 0.9*r, 0.27*r), (-0.1*r, 0.9*r, 0.29*r), (-0.1*r, 0.9*r, 0.3*r), (-0.372*r, 0.9*r, 0.24*r), (-0.45*r, 0.9*r, -0.13*r), (-0.18*r, 0.9*r, -0.345*r), (-0.17*r, 0.9*r, -0.31*r), (-0.26*r, 0.9*r, -0.41*r), (-0.21*r, 0.9*r, -0.41*r), (-0.05*r, 0.9*r, -0.4*r), (0, 0.9*r, -0.4*r), (-0.029*r, 0.9*r, -0.33*r), (-0.048*r, 0.9*r, -0.22*r), (-0.055*r, 0.9*r, -0.16*r), (-0.15*r, 0.9*r, -0.272*r), (-0.12*r, 0.9*r, -0.27*r), (-0.35*r, 0.9*r, -0.1*r), (-0.29*r, 0.9*r, 0.15*r), (-0.16*r, 0.9*r, 0.21*r), (-0.1*r, 0.9*r, 0.2*r)] )
        cv_arrow_2 = cmds.curve(n=ctrl_name+"_CvArrow2", d=3, p=[(0.1*r, 0.9*r, -0.2*r), (0.1*r, 0.9*r, -0.23*r), (0.1*r, 0.9*r, -0.27*r), (0.1*r, 0.9*r, -0.29*r), (0.1*r, 0.9*r, -0.3*r), (0.372*r, 0.9*r, -0.24*r), (0.45*r, 0.9*r, 0.13*r), (0.18*r, 0.9*r, 0.345*r), (0.17*r, 0.9*r, 0.31*r), (0.26*r, 0.9*r, 0.41*r), (0.21*r, 0.9*r, 0.41*r), (0.05*r, 0.9*r, 0.4*r), (0, 0.9*r, 0.4*r), (0.029*r, 0.9*r, 0.33*r), (0.048*r, 0.9*r, 0.22*r), (0.055*r, 0.9*r, 0.16*r), (0.15*r, 0.9*r, 0.272*r), (0.12*r, 0.9*r, 0.27*r), (0.35*r, 0.9*r, 0.1*r), (0.29*r, 0.9*r, -0.15*r), (0.16*r, 0.9*r, -0.21*r), (0.1*r, 0.9*r, -0.2*r)] )
        cv_arrow_3 = cmds.curve(n=ctrl_name+"_CvArrow3", d=3, p=[(-0.1*r, -0.9*r, 0.2*r), (-0.1*r, -0.9*r, 0.23*r), (-0.1*r, -0.9*r, 0.27*r), (-0.1*r, -0.9*r, 0.29*r), (-0.1*r, -0.9*r, 0.3*r), (-0.372*r, -0.9*r, 0.24*r), (-0.45*r, -0.9*r, -0.13*r), (-0.18*r, -0.9*r, -0.345*r), (-0.17*r, -0.9*r, -0.31*r), (-0.26*r, -0.9*r, -0.41*r), (-0.21*r, -0.9*r, -0.41*r), (-0.05*r, -0.9*r, -0.4*r), (0, -0.9*r, -0.4*r), (-0.029*r, -0.9*r, -0.33*r), (-0.048*r, -0.9*r, -0.22*r), (-0.055*r, -0.9*r, -0.16*r), (-0.15*r, -0.9*r, -0.272*r), (-0.12*r, -0.9*r, -0.27*r), (-0.35*r, -0.9*r, -0.1*r), (-0.29*r, -0.9*r, 0.15*r), (-0.16*r, -0.9*r, 0.21*r), (-0.1*r, -0.9*r, 0.2*r)] )
        cv_arrow_4 = cmds.curve(n=ctrl_name+"_CvArrow4", d=3, p=[(0.1*r, -0.9*r, -0.2*r), (0.1*r, -0.9*r, -0.23*r), (0.1*r, -0.9*r, -0.27*r), (0.1*r, -0.9*r, -0.29*r), (0.1*r, -0.9*r, -0.3*r), (0.372*r, -0.9*r, -0.24*r), (0.45*r, -0.9*r, 0.13*r), (0.18*r, -0.9*r, 0.345*r), (0.17*r, -0.9*r, 0.31*r), (0.26*r, -0.9*r, 0.41*r), (0.21*r, -0.9*r, 0.41*r), (0.05*r, -0.9*r, 0.4*r), (0, -0.9*r, 0.4*r), (0.029*r, -0.9*r, 0.33*r), (0.048*r, -0.9*r, 0.22*r), (0.055*r, -0.9*r, 0.16*r), (0.15*r, -0.9*r, 0.272*r), (0.12*r, -0.9*r, 0.27*r), (0.35*r, -0.9*r, 0.1*r), (0.29*r, -0.9*r, -0.15*r), (0.16*r, -0.9*r, -0.21*r), (0.1*r, -0.9*r, -0.2*r)] )
        cv_arrow_5 = cmds.curve(n=ctrl_name+"_CvArrow5", d=1, p=[(0, 0, 1.2*r), (0.09*r, 0, 1*r), (-0.09*r, 0, 1*r), (0, 0, 1.2*r)] )
        cv_arrow_6 = cmds.curve(n=ctrl_name+"_CvArrow6", d=1, p=[(0, 0, 1.2*r), (0, 0.09*r, 1*r), (0, -0.09*r, 1*r), (0, 0, 1.2*r)] )
        # rename curveShape:
        curves = [cv_loc, cv_arrow_1, cv_arrow_2, cv_arrow_3, cv_arrow_4, cv_arrow_5, cv_arrow_6]
        self.rename_shape(curves)
        # create ball curve:
        cv_template_ball = self.create_controller("Ball", ctrl_name+"_CvBall", r=0.7*r, d=3)
        # parent shapes to transform:
        ctrl_loc = cmds.group(name=ctrl_name, empty=True)
        children_ball = cmds.listRelatives(cv_template_ball, shapes=True, children=True)
        for child_ball in children_ball:
            cmds.setAttr(child_ball+".template", 1)
        self.transfer_shape(True, False, cv_template_ball, [ctrl_loc])
        for transform in curves:
            self.transfer_shape(True, False, transform, [ctrl_loc])
        # set rotation direction:
        cmds.setAttr(ctrl_loc+".rotateX", rot[0])
        cmds.setAttr(ctrl_loc+".rotateY", rot[1])
        cmds.setAttr(ctrl_loc+".rotateZ", rot[2])
        cmds.makeIdentity(ctrl_loc, rotate=True, apply=True)
        if guide:
            self.add_guide_attrs(ctrl_loc, pin=pin)
        cmds.select(clear=True)
        return ctrl_loc


    def create_character_ctrl(self, ctrl_type, ctrl_name, r=1, d=1, dir="+Y", rot=(0, 0, 0)):
        """ Create and return a curve to be used as a control.
        """
        # get radius by checking linear unit
        #r = self.dpCheckLinearUnit(r)
        curve = self.create_controller(ctrl_type, ctrl_name, r, d, dir, rot)
        # edit a minime curve:
        cmds.addAttr(curve, longName="rigScale", attributeType='float', defaultValue=1, keyable=True, minValue=0.001)
        cmds.addAttr(curve, longName="rigScaleMultiplier", attributeType='float', defaultValue=1, keyable=False)
        
        # create Option_Ctrl Text:
        try:
            option_ctrl_txt = cmds.group(name="Option_Ctrl_Txt", empty=True)
            cv_text = cmds.textCurves(name="Option_Ctrl_Txt_TEMP_Grp", text="OPTIONS", constructionHistory=False)[0]
            for attr in self.ar.data.axes:
                cmds.setAttr(cv_text+".scale"+attr, 0.3*r)
            text_shapes = cmds.listRelatives(cv_text, allDescendents=True, type='nurbsCurve')
            if text_shapes:
                for s, shape in enumerate(text_shapes):
                    # store CV world position
                    curve_cvs = cmds.getAttr(shape+'.cp', multiIndices=True)
                    vertex_world_pos = []
                    for i in curve_cvs :
                        cv_point_pos = cmds.xform(shape+'.cp['+str(i)+']', query=True, translation=True, worldSpace=True) 
                        vertex_world_pos.append(cv_point_pos)
                    # parent the shape :
                    cmds.parent(shape, option_ctrl_txt, r=True, s=True)
                    # restore the shape world position
                    for i in curve_cvs:
                        cmds.xform(shape+'.cp['+str(i)+']', a=True, worldSpace=True, t=vertex_world_pos[i])
                    cmds.rename(shape, option_ctrl_txt+str(s)+"Shape")
            cmds.delete(cv_text)
            cmds.parent(option_ctrl_txt, curve)
            cmds.setAttr(option_ctrl_txt+".template", 1)
            cmds.setAttr(option_ctrl_txt+".tx", -0.61*r)
            cmds.setAttr(option_ctrl_txt+".ty", 1.1*r)
            self.ar.custom_attr.add_attr(0, [option_ctrl_txt]) #dpID
        except:
            # it will pass if we don't able to find the font to create the text
            pass
        return curve


    def find_history(self, items, history_name):
        """Search and return the especific history of the listed objects.
        """
        if items:
            found_histories = []
            for item in items:
                # find history_name in the object's history:
                for hist in cmds.listHistory(item):
                    if cmds.objectType(hist) == history_name:
                        found_histories.append(hist)
            return found_histories


    def create_guide_base_loc(self, ctrl_name, r=1):
        """Create a control to be used as a Base Guide control.
            Returns the main control (circle) and the radius control in a list.
        """
        # get radius by checking linear unit
        #r = self.dpCheckLinearUnit(r)
        # create a simple circle curve:
        circle = cmds.circle(n=ctrl_name, ch=True, o=True, nr=(0, 0, 1), d=3, s=8, radius=r)[0]
        radius_ctrl = cmds.circle(n=ctrl_name+"_RadiusCtrl", ch=True, o=True, nr=(0, 1, 0), d=3, s=8, radius=(r/4.0))[0]
        # rename curveShape:
        self.rename_shape([circle, radius_ctrl])
        # configure system of limits and radius:
        cmds.setAttr(radius_ctrl+".translateX", r)
        cmds.parent(radius_ctrl, circle, relative=True)
        cmds.transformLimits(radius_ctrl, tx=(0.01, 1), etx=(True, False))
        self.set_lock_hide([radius_ctrl], ['ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        # find makeNurbCircle history of the circles:
        histories = self.find_history([circle, radius_ctrl], 'makeNurbCircle')
        circle_history     = histories[0]
        radius_ctrl_history = histories[1]
        # rename and make a connection for circle:
        circle_history = cmds.rename(circle_history, circle+"_makeNurbCircle")
        cmds.connectAttr(radius_ctrl+".tx", circle_history+".radius", force=True)
        radius_ctrl_history = cmds.rename(radius_ctrl_history, radius_ctrl+"_makeNurbCircle")
        # create a mutiplyDivide in order to automatisation the radius of the radius_ctrl:
        radius_ctrl_md = cmds.createNode('multiplyDivide', name=radius_ctrl+'_MD')
        cmds.connectAttr(radius_ctrl+'.translateX', radius_ctrl_md+'.input1X', force=True)
        cmds.setAttr(radius_ctrl_md+'.input2X', 0.15)
        cmds.connectAttr(radius_ctrl_md+".outputX", radius_ctrl_history+".radius", force=True)
        # colorize curveShapes:
        self.color_shape([circle], 'yellow')
        self.color_shape([radius_ctrl], 'cyan')
        cmds.setAttr(circle+"0Shape.lineWidth", 2)
        cmds.select(clear=True)
        # pinGuide:
        self.ar.job.create_pin_guide(circle)
        return [circle, radius_ctrl]


    def copy_attr(self, source_item=False, attributes=False, verbose=False, *args):
        """ Get and store in a dictionary the attributes from source_item.
            Returns the dictionary with attribute values.
        """
        # getting source_item:
        if not source_item:
            selection = cmds.ls(selection=True, long=True)
            if selection:
                source_item = selection[0]
            else:
                print(self.ar.data.lang["e015_selectToCopyAttr"])
        if cmds.objExists(source_item):
            if not attributes:
                # getting channelBox selected attributes:
                current_attrs = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)
                if not current_attrs:
                    # list all attributes if nothing is selected:
                    current_attrs = cmds.listAttr(source_item, visible=True, keyable=True)
                attributes = current_attrs
            if attributes:
                # store attribute values in a data:
                self.attr_value_data = {}
                for attr in attributes:
                    if attr in self.long_attr_data.keys():
                        attr = self.long_attr_data[attr]
                    if attr in cmds.listAttr(source_item):
                        value = cmds.getAttr(source_item+'.'+attr)
                        self.attr_value_data[attr] = value
                if verbose:
                    print(self.ar.data.lang["i125_copiedAttr"])
        return self.attr_value_data


    def paste_attr(self, destinations=False, verbose=False, *args):
        """ Get to destination list and set the dictionary values on them.
        """
        # getting destinations:
        if not destinations:
            destinations = cmds.ls(selection=True, long=True)
        if destinations and self.attr_value_data:
            # set data values to destinations:
            for dest_item in destinations:
                for attr in self.attr_value_data:
                    try:
                        cmds.setAttr(dest_item+'.'+attr, self.attr_value_data[attr])
                    except:
                        try:
                            cmds.setAttr(dest_item+'.'+attr, self.attr_value_data[attr], type='string')
                        except:
                            pass
                            if verbose:
                                print(self.ar.data.lang["e016_notPastedAttr"], attr)
            if verbose:
                print(self.ar.data.lang["i126_pastedAttr"])


    def copy_and_paste_attr(self, verbose=False, *args):
        """ Call copy and past functions.
        """
        # copy attributes and store them in the dictionary:
        self.copy_attr()
        # get destinations:
        current_selected_items = cmds.ls(selection=True, long=True)
        if current_selected_items:
            if len(current_selected_items) > 1:
                destinations = current_selected_items[1:]
                # calling function to paste attributes to destinations:
                self.paste_attr(destinations, verbose)


    def transfer_attr(self, source_item, destinations, attributes, *args):
        """ Transfer attributes from source_item to destinations.
        """
        if source_item and destinations and attributes:
            self.copy_attr(source_item, attributes)
            self.paste_attr(destinations)


    def transfer_shape(self, delete_source=False, clear_dest_shapes=True, source_item=None, destinations=None, keep_color=True, force=False, *args):
        """ Transfer control shape from source_item to destination list
        """
        if not source_item:
            selection = cmds.ls(selection=True, type="transform")
            if selection and len(selection) > 1:
                # get first selected item
                source_item = selection[0]
                # get other selected items
                destinations = selection[1:]
        if source_item:
            source_shapes = cmds.listRelatives(source_item, shapes=True, type="nurbsCurve", fullPath=True)
            if source_shapes:
                if destinations:
                    for dest_transform in destinations:
                        need_keep_vis = False
                        source_vis = None
                        defs = False
                        dup_source_item = cmds.duplicate(source_item)[0]
                        self.ar.utils.delete_orig_shape(dup_source_item)
                        if keep_color:
                            self.set_source_color_override(dup_source_item, [dest_transform])
                        dest_shapes = cmds.listRelatives(dest_transform, shapes=True, type="nurbsCurve", fullPath=True)
                        if dest_shapes:
                            for dest_shape in dest_shapes:
                                # keep visibility connections if exists:
                                vis_connection = cmds.listConnections(dest_shape+".visibility", destination=False, source=True, plugs=True)
                                if vis_connection:
                                    need_keep_vis = True
                                    source_vis = vis_connection[0]
                                    break
                            for dest_shape in dest_shapes:
                                # keep deformers if exists
                                try:
                                    defs = cmds.findDeformers(dest_shape)
                                    break
                                except:
                                    pass
                            if clear_dest_shapes:
                                cmds.delete(dest_shapes)
                        # hack: unparent destination children in order to get a good shape hierarchy order as index 0:
                        dest_children = cmds.listRelatives(dest_transform, shapes=False, type="transform", fullPath=True)
                        if dest_children:
                            self.destChildrenGrp = cmds.group(dest_children, name="dpTemp_DestChildren_Grp")
                            cmds.parent(self.destChildrenGrp, world=True)
                        if defs:
                            self.ar.utils.reapply_deformers(dup_source_item, defs)
                        dup_source_shapes = cmds.listRelatives(dup_source_item, shapes=True, type="nurbsCurve", fullPath=True)
                        for d, dup_source_shape in enumerate(dup_source_shapes):
                            if need_keep_vis:
                                if "Global" in dest_transform or "Master" in dest_transform or "Root" in dest_transform: #directionDisplay attribute exception
                                    if not d == 0:
                                        cmds.connectAttr(source_vis, dup_source_shape+".visibility", force=True)
                                else:
                                    cmds.connectAttr(source_vis, dup_source_shape+".visibility", force=True)
                            if not force:
                                cmds.parent(dup_source_shape, dest_transform, relative=True, shape=True)
                            elif cmds.objExists(dup_source_shape):
                                # make sure we use the current shape of a froze transform, usefull to mirror control shapes
                                forced_shape = cmds.parent(dup_source_shape, dest_transform, absolute=True, shape=True)[0]
                                forced_transform = cmds.listRelatives(forced_shape, parent=True, type="transform", fullPath=True)
                                history = cmds.listHistory(forced_shape)
                                # workaround to avoid undesirable warning about tweak nodes
                                cmds.delete(forced_shape, constructionHistory=True)
                                for x in history:
                                    if "tweak" in x:
                                        if cmds.objExists(x):
                                            cmds.delete(x)
                                cmds.makeIdentity(forced_transform, apply=True, translate=True, rotate=True, scale=True)
                                cmds.parent(forced_shape, dest_transform, relative=True, shape=True)
                                cmds.delete(forced_transform)
                                if defs and history:
                                    self.ar.utils.reapply_deformers(dest_transform+"|"+forced_shape, defs)
                        if cmds.objExists(dup_source_item):
                            cmds.delete(dup_source_item)
                        self.rename_shape([dest_transform])
                        # restore children transforms to correct parent hierarchy:
                        if dest_children:
                            cmds.parent((cmds.listRelatives(self.destChildrenGrp, shapes=False, type="transform", fullPath=True)), dest_transform)
                            cmds.delete(self.destChildrenGrp)
                    if delete_source:
                        # update cvControls attributes:
                        self.transfer_attr(source_item, destinations, ["className", "size", "degree", "cvRotX", "cvRotY", "cvRotZ"])
                        cmds.delete(source_item)
                    self.ar.custom_attr.add_attr(0, destinations, shapes=True) #dpID


    def transfer_plug(self, from_plug, to_plug, value=True, connections=True):
        """ Set and transfer attributes connections.
        """
        if value:
            cmds.setAttr(to_plug, cmds.getAttr(from_plug))
        if connections:
            inputs = cmds.listConnections(from_plug, source=True, destination=False, plugs=True)
            if inputs:
                if len(inputs) > 1:
                    raise RuntimeError(self.ar.data.lang['e023_unableTransferPlug'])
                cmds.connectAttr(inputs[0], to_plug, force=True)
            destinations = cmds.listConnections(from_plug, source=False, destination=True, plugs=True) or []
            for dest in destinations:
                locked = cmds.getAttr(dest, lock=True)
                if locked:
                    cmds.setAttr(dest, lock=False)
                cmds.connectAttr(to_plug, dest, force=True)
                if locked:
                    cmds.setAttr(dest, lock=True)


    def set_source_color_override(self, source_item, destinations):
        """ Check if there's a colorOverride for destination shapes
            and try to set it to source shapes.
        """
        colors = []
        for item in destinations:
            children_shapes = cmds.listRelatives(item, shapes=True, type="nurbsCurve", fullPath=True)
            if children_shapes:
                for childShape in children_shapes:
                    if cmds.getAttr(childShape+".overrideEnabled") == 1:
                        if cmds.getAttr(childShape+".overrideRGBColors") == 1:
                            colors.append(cmds.getAttr(childShape+".overrideColorR"))
                            colors.append(cmds.getAttr(childShape+".overrideColorG"))
                            colors.append(cmds.getAttr(childShape+".overrideColorB"))
                            self.color_shape([source_item], colors, True)
                        else:
                            colors.append(cmds.getAttr(childShape+".overrideColor"))
                            self.color_shape([source_item], colors[0])
                        break


    def reset_curve(self, change_degree=False, transforms=False, *args):
        """ Read the current curve degree of selected curve controls and change it to another one.
            1 to 3
            or
            3 to 1.
        """
        if not transforms:
            transforms = cmds.ls(selection=True, type="transform")
        if transforms:
            for item in transforms:
                if DPCONTROL in cmds.listAttr(item) and cmds.getAttr(item+"."+DPCONTROL) == 1:
                    # getting current control values from stored attributes:
                    current_type = cmds.getAttr(item+".className")
                    current_size = cmds.getAttr(item+".size")
                    current_degree = cmds.getAttr(item+".degree")
                    current_dir = cmds.getAttr(item+".direction")
                    current_rot_x = cmds.getAttr(item+".cvRotX")
                    current_rot_y = cmds.getAttr(item+".cvRotY")
                    current_rot_z = cmds.getAttr(item+".cvRotZ")
                    if change_degree:
                        # changing current curve degree:
                        if current_degree == 1: #linear
                            current_degree = 3 #cubic
                        else: #cubic
                            current_degree = 1 #linear
                        cmds.setAttr(item+".degree", current_degree)
                    curve = self.create_controller(current_type, "Temp_Ctrl", current_size, current_degree, current_dir, (current_rot_x, current_rot_y, current_rot_z), 1)
                    self.transfer_shape(delete_source=True, clear_dest_shapes=True, source_item=curve, destinations=[item], keep_color=True)
            cmds.select(transforms)


    def confirm_ask_user(self, title_text, message_text, *args):
        """ Just a confirmDialog that return user choise as True or False.
        """
        # ask user to continue
        result_question = cmds.confirmDialog(
                                        title=title_text,
                                        message=message_text, 
                                        button=[self.ar.data.lang['i071_yes'], self.ar.data.lang['i072_no']], 
                                        defaultButton=self.ar.data.lang['i071_yes'], 
                                        cancelButton=self.ar.data.lang['i072_no'], 
                                        dismissString=self.ar.data.lang['i072_no'])
        if result_question == self.ar.data.lang['i071_yes']:
            return True
        return False


    def create_curve_preset(self):
        """ Creates a json file as a Control Preset and returns it.
        """
        result_string = None
        controllers, ctrl_ids = [], []
        transforms = cmds.ls(selection=False, type='transform')
        for item in transforms:
            if DPCONTROL in cmds.listAttr(item):
                if cmds.getAttr(item+"."+DPCONTROL) == 1:
                    controllers.append(item)
        if controllers:
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
                confirm_same_name = True
                if result_name in self.ar.data.curve_preset_data:
                    confirm_same_name = self.confirm_ask_user(self.ar.data.lang['i129_createPreset'], self.ar.data.lang['i135_existingName'])
                if confirm_same_name:
                    author = getpass.getuser()
                    date = str(datetime.datetime.now().date())
                    result_string = '{"_preset":"'+result_name+'","_author":"'+author+'","_date":"'+date+'","_updated":"'+date+'"'
                    # add default keys to dict:
                    ctrl_ids.append("_preset")
                    ctrl_ids.append("_author")
                    ctrl_ids.append("_date")
                    ctrl_ids.append("_updated")
                    # get all existing controls info
                    for ctrl_node in controllers:
                        ctrl_id = cmds.getAttr(ctrl_node+".controlID")
                        if ctrl_id.startswith("id_"):
                            if not ctrl_id in ctrl_ids:
                                ctrl_ids.append(ctrl_id)
                                ctrl_type = cmds.getAttr(ctrl_node+".className")
                                ctrl_degree = cmds.getAttr(ctrl_node+".degree")
                                result_string += ',"'+ctrl_id+'":{"type":"'+ctrl_type+'","degree":'+str(ctrl_degree)+'}'
                    # check if we got all controlIDs:
                    for j, p_id in enumerate(self.ar.data.curve_preset):
                        if not p_id in ctrl_ids:
                            # get missing controlIDs from current preset:
                            result_string += ',"'+p_id+'":{"type":"'+self.ar.data.curve_preset[p_id]["type"]+'","degree":'+str(self.ar.data.curve_preset[p_id]["degree"])+'}'
                    result_string += "}"
        return result_string


    def dpCheckLinearUnit(self, origRadius, defaultUnit="centimeter", boundingBox=True, *args):
        """ Verify if the Maya linear unit is in Centimeter.
            Return the radius to the new unit size.
            TODO: delete this unused method?
            WIP!
            Changing to shapeSize cluster setup
        """
        magicNumber = 0.085
        newRadius = origRadius
    #    newRadius = 1
    #    linearUnit = cmds.currentUnit(query=True, linear=True, fullName=True)
    #    # centimeter
    #    if linearUnit == defaultUnit:
    #        newRadius = origRadius
    #    elif linearUnit == "meter":
    #        newRadius = origRadius*0.01
    #    elif linearUnit == "millimeter":
    #        newRadius = origRadius*10
    #    elif linearUnit == "inch":
    #        newRadius = origRadius*0.393701
    #    elif linearUnit == "foot":
    #        newRadius = origRadius*0.032808
    #    elif linearUnit == "yard":
    #        newRadius = origRadius*0.010936
        # adapt radius to geometry meshes size
        if boundingBox:
            meshes = cmds.ls(selection=False, noIntermediate=True, long=True, type="mesh")
            if meshes:
                tempList = []
                for item in meshes:
                    if not "_DeformerCube_Geo" in item:
                        fatherNode = item[:item[1:].find("|")+1]
                        if fatherNode:
                            if not fatherNode in tempList:
                                tempList.append(fatherNode)
                if tempList:
                    bbList = list(cmds.getAttr(tempList[0]+".boundingBox.boundingBoxMax")[0])
                    bbList[1] *= 0.75 #less importance to height
                    bbAverage = self.ar.math.average_value(bbList)
                    resultValue = magicNumber*bbAverage*origRadius
                    if resultValue:
                        return resultValue
                    return origRadius
        return newRadius
        

    #@utils.profiler
    def shape_size_setup(self, transform_node):
        """ Find shapes, create a cluster deformer to all and set the pivot to transform pivot.
        """
        cluster_handle = None
        children_shapes = cmds.listRelatives(transform_node, shapes=True, children=True)
        if children_shapes:
            this_namespace = children_shapes[0].split(":")[0]
            cmds.namespace(set=this_namespace, force=True)
            cluster_name = transform_node.split(":")[1]+"_ShapeSizeCH"
            cluster_handle = cmds.cluster(children_shapes, name=cluster_name)[1]
            cmds.setAttr(cluster_handle+".visibility", 0)
            cmds.xform(cluster_handle, scalePivot=(0, 0, 0), worldSpace=True)
            cmds.namespace(set=":")
        else:
            print("There are not children shape to create shapeSize setup of:", transform_node)
        if cluster_handle:
            self.connect_shape_size(cluster_handle)


    def connect_shape_size(self, cluster_handle):
        """ Connect shapeSize attribute from guide main control to shapeSizeClusterHandle scale XYZ.
        """
        main = cluster_handle[:cluster_handle.rfind("Guide_")+6]+"Base" #hack to get main name by string TODO: change to find by instance
        cmds.connectAttr(main+".shapeSize", cluster_handle+".scaleX", force=True)
        cmds.connectAttr(main+".shapeSize", cluster_handle+".scaleY", force=True)
        cmds.connectAttr(main+".shapeSize", cluster_handle+".scaleZ", force=True)
        # re-declaring Temporary Group and parenting shapeSizeClusterHandle:
        cmds.parent(cluster_handle, self.ar.data.temp_grp)


    def add_guide_attrs(self, ctrl_name, color="blue", pin=True):
        """ Add and set attributes to this control curve be used as a guide.
        """
        # create an attribute to be used as guide by module:
        cmds.addAttr(ctrl_name, longName="nJoint", attributeType='long')
        cmds.setAttr(ctrl_name+".nJoint", 1)
        # colorize curveShapes:
        self.color_shape([ctrl_name], color)
        # shapeSize setup:
        self.shape_size_setup(ctrl_name)
        # pinGuide:
        if pin:
            self.ar.job.create_pin_guide(ctrl_name)


    def import_calibration(self, *args):
        """ Import calibration from a referenced file.
            Transfer calibration for same nodes by name using calibrationList attribute.
        """
        import_calib_namespace = "dpImportCalibration"
        source_ref_nodes = []
        # get user file to import calibration from
        import_calib_path = cmds.fileDialog2(fileMode=1, caption=self.ar.data.lang['i196_import']+" "+self.ar.data.lang['i193_calibration'])
        if not import_calib_path:
            return
        self.ar.ui_manager.set_progress(self.ar.data.lang['i214_refFile'], import_calib_namespace, add_one=False)
        import_calib_path = next(iter(import_calib_path), None)
        # create a file reference:
        refFile = cmds.file(import_calib_path, reference=True, namespace=import_calib_namespace)
        ref_node = cmds.file(import_calib_path, referenceNode=True, query=True)
        ref_nodes = cmds.referenceQuery(ref_node, nodes=True)
        if ref_nodes:
            for item in ref_nodes:
                self.ar.ui_manager.set_progress(max=len(ref_nodes), add_one=False, add_number=False)
                self.ar.ui_manager.set_progress(self.ar.data.lang['i215_setAttr'], add_one=True)
                if "calibrationList" in cmds.listAttr(item):
                    source_ref_nodes.append(item)
        if source_ref_nodes:
            for source_ref_node in source_ref_nodes:
                destination_node = source_ref_node[source_ref_node.rfind(":")+1:]
                if cmds.objExists(destination_node):
                    self.transfer_calibration(source_ref_node, [destination_node], verbose=False)
        # remove referenced file:
        cmds.file(import_calib_path, removeReference=True)
        self.ar.ui_manager.set_progress(end_it=True)
        print("dpImportCalibrationPath: "+import_calib_path)


    def mirror_calibration(self, node_name=False, from_prefix=False, to_prefix=False, *args):
        """ Mirror calibration by naming using prefixes to find nodes.
            Ask to mirror calibration of all controls if nothing is selected.
        """
        if not from_prefix:
            from_prefix = cmds.textField("ctr_mirror_calibration_from_prefix_tf", query=True, text=True)
            to_prefix = cmds.textField("ctr_mirror_calibration_to_prefix_tf", query=True, text=True)
        if from_prefix and to_prefix:
            if not node_name:
                current_selection = cmds.ls(selection=True, type="transform")
                if current_selection:
                    for selected_node in current_selection:
                        if selected_node.startswith(from_prefix):
                            self.mirror_calibration(selected_node, from_prefix, to_prefix)
                else:
                    # ask to run for all nodes:
                    if self.confirm_ask_user(self.ar.data.lang['m010_mirror']+" "+self.ar.data.lang['i193_calibration'], self.ar.data.lang['i042_notSelection']+"\n"+self.ar.data.lang['i197_mirrorAll']):
                        all_nodes = cmds.ls(from_prefix+"*", selection=False, type="transform")
                        if all_nodes:
                            for node in all_nodes:
                                self.mirror_calibration(node, from_prefix, to_prefix)
            else:
                attributes = self.get_items_from_string_attr(node_name)
                if attributes:
                    destination_node = to_prefix+node_name[len(from_prefix):]
                    if cmds.objExists(destination_node):
                        not_mirror_attrs = self.get_items_from_string_attr(node_name, "notMirrorList")
                        if not_mirror_attrs:
                            attributes = list(set(attributes) - set(not_mirror_attrs))
                        self.transfer_attr(node_name, [destination_node], attributes)
        else:
            print(self.ar.data.lang['i198_mirrorPrefix'])


    def transfer_calibration(self, source_item=False, destinations=False, attributes=False, verbose=True, *args):
        """ Transfer calibration attributes.
        """
        if not source_item:
            # check current selection:
            current_selection = cmds.ls(selection=True, type="transform")
            if current_selection:
                if len(current_selection) > 1:
                    source_item = current_selection[0]
                    destinations = current_selection[1:]
        if source_item:
            if not attributes:
                attributes = self.get_items_from_string_attr(source_item)
            if attributes:
                self.transfer_attr(source_item, destinations, attributes)
            if verbose:
                print(self.ar.data.lang['i195_transferedCalib'], source_item, destinations, attributes)
        else:
            print(self.ar.data.lang['i042_notSelection'])


    def set_string_attr_from_items(self, node_name, attributes, attr_name="calibrationList"):
        """ Set the given attribute that contains a list of the given list.
            Add a string attribute if it doesn't exists.
            Useful for calibrationList attribute.
        """
        if cmds.objExists(node_name):
            if attributes:
                calib_attr = ';'.join(attributes)
                if not attr_name in cmds.listAttr(node_name):
                    cmds.addAttr(node_name, longName=attr_name, dataType="string")
                cmds.setAttr(node_name+"."+attr_name, calib_attr, type="string")


    def get_items_from_string_attr(self, node_name, attr_name="calibrationList"):
        """ Return the list from a string if it exists in the given node_name.
            Useful to ready calibrationList attributes by default.
        """
        if attr_name in cmds.listAttr(node_name):
            return list(cmds.getAttr(node_name+"."+attr_name).split(";"))


    def get_controllers(self, attr=None):
        """ List all dpControl transforms that has active .dpControl attribute.
            If have a given attr, it'll filter if there are nodes with this attribute.
            Returns a list of them.
        """
        nodes = []
        all_items = cmds.ls(selection=False, type="transform")
        if all_items:
            if attr:
                for item in all_items:
                    if attr in cmds.listAttr(item):
                        nodes.append(item)
            else:
                for item in all_items:
                    if DPCONTROL in cmds.listAttr(item) and cmds.getAttr(item+"."+DPCONTROL):
                        nodes.append(item)
        return nodes


    def export_shape(self, nodes=None, path=None, io=False, snapshot_grp="dpSnapshot_Grp", keep_snapshot=False, override_existing=True, ui=True, verbose=False, dir="dpControlShape", *args):
        """ Export control shapes from a given list or all found dpControl transforms in the scene.
            It will save a Maya ASCII file with the control shapes snapshots.
            If there is no given path, it will ask user where to save the file.
            If io is True, it will use the current location and create the dpControlShapeIO directory inside dpData folder by default.
            If keep_snapshot is True, it will parent a backup snapshot_grp group to Wip_Grp and hide it.
            If override_existing is True, it will delete the old node before create the new snapshot.
        """
        current_path = cmds.file(query=True, sceneName=True)
        if not current_path:
            if path and "dpData" in path:
                current_path = path.split("dpData")[0]
            else:
                mel.eval('warning \"'+self.ar.data.lang['i201_saveScene']+'\";')
                return
        if not nodes:
            nodes = self.get_controllers()
        if nodes:
            if not path:
                if io:
                    folder = current_path[:current_path.rfind("/")+1]+self.ar.dpData+"/"+dir
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    path = folder+"/"+dir+"_"+current_path[current_path.rfind("/")+1:]
                else:
                    paths = cmds.fileDialog2(fileMode=0, caption="Export Shapes")
                    if paths:
                        path = paths[0] 
            if path:
                if ui:
                    self.ar.ui_manager.set_progress(self.ar.data.lang['m094_doing']+': '+self.ar.data.lang['c110_start'], self.ar.data.lang['i164_export'], len(nodes), add_one=False, add_number=False)
                # make sure we save the file as mayaAscii
                if not path.endswith(".ma"):
                    path = path.replace(".*", ".ma")
                cmds.undoInfo(openChunk=True)
                if not cmds.objExists(snapshot_grp):
                    cmds.group(name=snapshot_grp, empty=True)
                for item in nodes:
                    if ui or verbose:
                        self.ar.ui_manager.set_progress(self.ar.data.lang['m094_doing']+': Shape')
                    snapshot_name = item+SNAPSHOT_SUFFIX
                    if cmds.objExists(snapshot_name):
                        if override_existing:
                            cmds.delete(snapshot_name)
                    dup = cmds.duplicate(item, name=snapshot_name)[0]
                    cmds.setAttr(dup+".dpControl", 0)
                    dup_children = cmds.listRelatives(dup, allDescendents=True, children=True, fullPath=True)
                    if dup_children:
                        to_delete_items = []
                        for child in dup_children:
                            if not cmds.objectType(child) == "nurbsCurve":
                                to_delete_items.append(child)
                        if to_delete_items:
                            cmds.delete(to_delete_items)
                    cmds.parent(dup, snapshot_grp)
                # export shapes
                if cmds.listRelatives(snapshot_grp, allDescendents=True, children=True, type="nurbsCurve"):
                    cmds.select(snapshot_grp)
                    cmds.file(rename=path)
                    cmds.file(exportSelected=True, type='mayaAscii', prompt=False, force=True)
                    cmds.file(rename=current_path)
                    # DEV helper keep_snapshot
                    wip_grp = self.ar.utils.get_node_by_message("wipGrp")
                    if not cmds.objExists(wip_grp):
                        keep_snapshot = False
                    if keep_snapshot:
                        try:
                            cmds.parent(snapshot_grp, wip_grp)
                            cmds.setAttr(snapshot_grp+".visibility", 0)
                            if cmds.objExists("Backup_"+snapshot_grp):
                                cmds.delete("Backup_"+snapshot_grp)
                            cmds.rename(snapshot_grp, "Backup_"+snapshot_grp)
                        except:
                            pass
                    else:
                        cmds.delete(snapshot_grp)
                    print('Exported shapes to: {0}'.format(path))
                cmds.undoInfo(closeChunk=True)
        else:
            mel.eval('warning \"'+self.ar.data.lang['i202_noControls']+'\";')
        if ui:
            # Close progress window
            self.ar.ui_manager.set_progress(end_it=True)


    def import_shape(self, nodes=None, path=None, io=False, ui=True, verbose=False, dir="dpControlShape", *args):
        """ Import control shapes from an external loaded Maya file.
            If not get an user defined parameter for a node list, it will import all shapes.
            If the io parameter is True, it will use the default path as current location inside dpControlShapeIO directory.
        """
        importShapeNamespace = "dpImportShape"
        if not nodes:
            nodes = self.get_controllers()
        if nodes:
            if io:
                current_path = cmds.file(query=True, sceneName=True)
                if not current_path:
                    if path and "dpData" in path:
                        current_path = path.split("dpData")[0]
                    else:
                        print(self.ar.data.lang['i201_saveScene'])
                        return
                folder = current_path[:current_path.rfind("/")+1]+self.ar.dpData+"/"+dir
                ctrl_shape = "/"+dir+"_"+current_path[current_path.rfind("/")+1:]
                path = folder+ctrl_shape
                if not os.path.exists(path):
                    print (self.ar.data.lang['i202_noControls'])
                    return
            elif not path:
                paths = cmds.fileDialog2(fileMode=1, caption="Import Shapes")
                if paths:
                    path = paths[0]
            if path:
                if not os.path.exists(path):
                    print(self.ar.data.lang['e004_objNotExist']+path)
                else:
                    # create a file reference:
                    cmds.file(path, reference=True, namespace=importShapeNamespace)
                    ref_node = cmds.file(path, referenceNode=True, query=True)
                    ref_nodes = cmds.referenceQuery(ref_node, nodes=True)
                    if ref_nodes:
                        if ui:
                            self.ar.ui_manager.set_progress(self.ar.data.lang['m094_doing']+': '+self.ar.data.lang['c110_start'], self.ar.data.lang['i196_import'], len(ref_nodes), add_one=False, add_number=False)
                        for source_ref_node in ref_nodes:
                            if ui or verbose:
                                self.ar.ui_manager.set_progress(self.ar.data.lang['m094_doing']+': Shape')
                            if cmds.objectType(source_ref_node) == "transform":
                                destination_node = source_ref_node[source_ref_node.rfind(":")+1:-len(SNAPSHOT_SUFFIX)] #removed namespace before ":"" and the suffix _Snapshot_Crv (-13)
                                if cmds.objExists(destination_node):
                                    self.transfer_shape(delete_source=False, clear_dest_shapes=True, source_item=source_ref_node, destinations=[destination_node], keep_color=False)
                    # remove referenced file:
                    cmds.file(path, removeReference=True)
                    print("Imported shapes: {0}".format(path))
        else:
            print(self.ar.data.lang['i202_noControls'])
        if ui:
            # Close progress window
            self.ar.ui_manager.set_progress(end_it=True)


    def create_corrective_joint_ctrl(self, jcr_name, corrective_net, type='id_092_Correctives', radius=1, degree=3):
        """ Create a corrective joint controller.
            Connect setup nodes and add calibration attributes to it.
            Returns the corrective controller and its highest zero out group.
        """
        to_ids = []
        calib_attrs = ["T", "R", "S"]
        to_calibration_items = []
        jcr_ctrl = self.create_controller(type, jcr_name.replace("_Jcr", "_Ctrl"), r=radius, d=degree, corrective=True)
        jcr_grp_0 = self.ar.utils.create_zero_out([jcr_ctrl])[0]
        jcr_grp_1 = self.ar.utils.create_zero_out([jcr_grp_0])[0]
        cmds.matchTransform(jcr_grp_1, jcr_name, position=True, rotation=True)
        cmds.parentConstraint(cmds.listRelatives(jcr_name, parent=True)[0], jcr_grp_1, maintainOffset=True, name=jcr_grp_1+"_PaC")
        cmds.parentConstraint(jcr_ctrl, jcr_name, maintainOffset=True, name=jcr_ctrl+"_PaC")
        cmds.scaleConstraint(jcr_ctrl, jcr_name, maintainOffset=True, name=jcr_ctrl+"_ScC")
        cmds.addAttr(jcr_ctrl, longName="correctiveNetwork", attributeType="message")
        cmds.addAttr(jcr_ctrl, longName="inputValue", attributeType="float", defaultValue=0)
        cmds.connectAttr(corrective_net+".message", jcr_ctrl+".correctiveNetwork", force=True)
        cmds.connectAttr(corrective_net+".outputValue", jcr_ctrl+".inputValue", force=True)
        for attr in calib_attrs:
            for axis in self.ar.data.axes:
                rmv = cmds.createNode("remapValue", name=jcr_name.replace("_Jcr", "_"+attr+axis+"_RmV"))
                intensity_md = cmds.createNode("multiplyDivide", name=jcr_name.replace("_Jcr", "_"+attr+axis+"_Intensity_MD"))
                to_ids.extend([rmv, intensity_md])
                cmds.connectAttr(corrective_net+".outputStart", rmv+".inputMin", force=True)
                cmds.connectAttr(corrective_net+".outputEnd", rmv+".inputMax", force=True)
                cmds.connectAttr(corrective_net+".outputValue", rmv+".inputValue", force=True)
                cmds.connectAttr(jcr_ctrl+".intensity", intensity_md+".input1X", force=True)
                cmds.connectAttr(rmv+".outValue", intensity_md+".input2X", force=True)
                # add calibrate attributes:
                if attr == "S":
                    scale_clp = cmds.createNode("clamp", name=jcr_name.replace("_Jcr", "_"+attr+axis+"_ScaleIntensity_Clp"))
                    to_ids.append(scale_clp)
                    cmds.addAttr(jcr_ctrl, longName="calibrate"+attr+axis, attributeType="float", defaultValue=1)
                    cmds.setAttr(rmv+".outputMin", 1)
                    cmds.setAttr(scale_clp+".minR", 1)
                    cmds.setAttr(scale_clp+".maxR", 1000)
                    cmds.connectAttr(intensity_md+".outputX", scale_clp+".inputR", force=True)
                    cmds.connectAttr(scale_clp+".outputR", jcr_grp_0+"."+attr.lower()+axis.lower(), force=True)
                else:
                    invert_md = cmds.createNode("multiplyDivide", name=jcr_name.replace("_Jcr", "_"+attr+axis+"_Invert_MD"))
                    invert_cnd = cmds.createNode("condition", name=jcr_name.replace("_Jcr", "_"+attr+axis+"_Invert_Cnd"))
                    to_ids.extend([invert_md, invert_cnd])
                    cmds.setAttr(invert_cnd+".secondTerm", 1)
                    cmds.setAttr(invert_cnd+".colorIfTrueR", -1)
                    cmds.addAttr(jcr_ctrl, longName="calibrate"+attr+axis, attributeType="float", defaultValue=0)
                    cmds.addAttr(jcr_ctrl, longName="invert"+attr+axis, attributeType="bool", defaultValue=0)
                    cmds.connectAttr(intensity_md+".outputX", invert_md+".input1X", force=True)
                    cmds.connectAttr(invert_cnd+".outColorR", invert_md+".input2X", force=True)
                    cmds.connectAttr(jcr_ctrl+".invert"+attr+axis, invert_cnd+".firstTerm", force=True)
                    cmds.connectAttr(invert_md+".outputX", jcr_grp_0+"."+attr.lower()+axis.lower(), force=True)
                cmds.connectAttr(jcr_ctrl+".calibrate"+attr+axis, rmv+".outputMax", force=True)
                to_calibration_items.append("calibrate"+attr+axis)
        self.ar.custom_attr.add_attr(0, to_ids) #dpID
        self.set_string_attr_from_items(jcr_ctrl, to_calibration_items)
        return jcr_ctrl, jcr_grp_1


    def add_corrective_attrs(self, ctrl_name):
        """ Add and set attributes to this control curve be used as a corrective controller.
        """
        cmds.addAttr(ctrl_name, longName="intensity", attributeType="float", minValue=0, defaultValue=1, maxValue=1, keyable=True)
        # create an attribute to be used as editMode by module:
        cmds.addAttr(ctrl_name, longName="editMode", attributeType="bool", keyable=False)
        cmds.setAttr(ctrl_name+".editMode", channelBox=True)


    def display_rotate_order_attr(self, controllers):
        """ Set display a non keyable rotateOrder attribute in the channelBox.
        """
        if controllers:
            for ctrl in controllers:
                if "rotateOrder" in cmds.listAttr(ctrl):
                    cmds.setAttr(ctrl+".rotateOrder", keyable=False, channelBox=True)


    def set_sub_ctrl_display(self, ctrl, sub_ctrl, def_value):
        """ Set the shapes visibility of sub control.
        """
        if not "subControlDisplay" in cmds.listAttr(ctrl):
            cmds.addAttr(ctrl, longName="subControlDisplay", attributeType="short", minValue=0, maxValue=1, defaultValue=def_value)
            cmds.setAttr(ctrl+".subControlDisplay", channelBox=True)
        sub_shapes = cmds.listRelatives(sub_ctrl, children=True, type="shape")
        if sub_shapes:
            for sub_shape in sub_shapes:
                cmds.connectAttr(ctrl+".subControlDisplay", sub_shape+".visibility", force=True)
        if self.ar.data.display_sub_shape:
            cmds.setAttr(ctrl+".subControlDisplay", 1)


    def mirror_shape(self, node_name=False, from_prefix=False, to_prefix=False, axis=False, *args):
        """ Mirror control shape by naming using prefixes to find nodes.
            Ask to mirror control shape of all controls if nothing is selected.
        """
        if not from_prefix:
            from_prefix = cmds.textField("ctr_mirror_shape_from_prefix_tf", query=True, text=True)
            to_prefix = cmds.textField("ctr_mirror_shape_to_prefix_tf", query=True, text=True)
            axis = cmds.optionMenu("ctr_mirror_shape_axis_om", query=True, value=True)
        if from_prefix and to_prefix:
            if not node_name:
                current_selection = cmds.ls(selection=True, type="transform")
                if current_selection:
                    for selected_node in current_selection:
                        if selected_node.startswith(from_prefix):
                            self.mirror_shape(selected_node, from_prefix, to_prefix, axis)
                else:
                    # ask to run for all nodes:
                    if self.confirm_ask_user(self.ar.data.lang['m010_mirror']+" "+self.ar.data.lang['m067_shape'], self.ar.data.lang['i042_notSelection']+"\n"+self.ar.data.lang['i265_mirrorShapeAll']):
                        all_nodes = cmds.ls(from_prefix+"*", selection=False, type="transform")
                        allControlList = self.get_controllers()
                        if all_nodes and allControlList:
                            self.ar.ui_manager.set_progress(self.ar.data.lang['m067_shape'], self.ar.data.lang['m010_mirror'], len(all_nodes), add_one=False, add_number=False)
                            for node in all_nodes:
                                if node in allControlList:
                                    self.ar.ui_manager.set_progress(self.ar.data.lang['m067_shape']+": "+node)
                                    self.mirror_shape(node, from_prefix, to_prefix, axis)
                                    cmds.refresh()
                        self.ar.ui_manager.set_progress(end_it=True)
            else:
                if DPCONTROL in cmds.listAttr(node_name) and cmds.getAttr(node_name+"."+DPCONTROL) == 1:
                    destination_node = to_prefix+node_name[len(from_prefix):]
                    if cmds.objExists(destination_node):
                        # do mirror algorithm
                        dup_source = cmds.duplicate(node_name, name=node_name+"_Duplicated_TEMP")[0]
                        self.ar.utils.delete_orig_shape(dup_source)
                        dup_grp = cmds.group(dup_source, name=dup_source+"_Grp")
                        mirror_shape_grp = cmds.group(empty=True, name=dup_source+"_MirrorShape_Grp")
                        cmds.parent(dup_grp, mirror_shape_grp)
                        cmds.setAttr(mirror_shape_grp+".scale"+axis, -1)
                        self.transfer_shape(delete_source=True, clear_dest_shapes=True, source_item=dup_source, destinations=[destination_node], keep_color=True, force=True)
                        cmds.delete(mirror_shape_grp)
        else:
            print(self.ar.data.lang['i198_mirrorPrefix'])


    def setup_default_values(self, reset_mode=True, controllers=None, *args):
        """ Set or Reset control attributes to their default values.
            Ask user to run for all nodes if there aren't any selected nodes.
            Settings argument calls the window to setup each default value for selected nodes.
        """
        if not controllers:
            items = self.get_selected_controllers()
            if not items:
                # ask to run for all nodes:
                if self.confirm_ask_user(self.ar.data.lang['i270_defaultValues'], self.ar.data.lang['i042_notSelection']+"\n"+self.ar.data.lang['i273_runAllNodes']):
                    items = self.get_controllers()
        else:
            items = self.get_controllers()
        if items:
            if reset_mode:
                self.ar.value_editor_ui.reset_pose.verbose = False
                self.ar.value_editor_ui.reset_pose.run_action(False, items)
                self.ar.value_editor_ui.reset_pose.verbose = True
                self.ar.ui_manager.set_progress(end_it=True)
            else: #set default values
                for item in items:
                    attributes = self.ar.value_editor_ui.reset_pose.getSetupAttrList(item, self.ignore_default_value_attrs)
                    if attributes:
                        for attr in attributes:
                            # hack to avoid Maya limitation to edit boolean attributes
                            if not cmds.attributeQuery(attr, node=item, attributeType=True) == "bool":
                                cmds.addAttr(item+"."+attr, edit=True, defaultValue=cmds.getAttr(item+"."+attr))


    def get_selected_controllers(self):
        """ Return the intersection of all controllers in the scene and the selected items.
        """
        return list(set(self.get_controllers()) & set(cmds.ls(selection=True, type="transform")))


    def select_controller(self, ctrl, refresh_ui=False, *args):
        """ Select the given controller.
            Populate the defaultValueEditor if True.
        """
        if cmds.objExists(ctrl):
            cmds.select(ctrl)
        if refresh_ui:
            self.ar.value_editor_ui.populate_selected_controllers()


    def select_all_controllers(self, refresh_ui=False, *args):
        """ Select all dpAR controllers in the scene.
            Populate the defaultValueEditor if True.
        """
        controllers = self.get_controllers()
        if controllers:
            cmds.select(controllers)
        if refresh_ui:
            self.ar.value_editor_ui.populate_selected_controllers()


    def set_default_value(self, ctrl, attr, value, *args):
        """ Edit the default value of the given controller.
        """
        cmds.addAttr(ctrl+"."+attr, edit=True, defaultValue=value)


    def set_current_value(self, ctrl, attr, value, *args):
        """ Edit the current value of the given controller.
        """
        cmds.setAttr(ctrl+"."+attr, value)


    def reset_mirror_shape(self, *args):
        """ Call reset all controls before run mirror_shape script.
        """
        self.setup_default_values(reset_mode=True, controllers=self.get_controllers())
        self.mirror_shape()

        
    def set_controller_scale_compensate(self, value, controllers=None):
        """ Set the controllers scaleCompensate value.
        """
        if not controllers:
            controllers = [c for c in self.get_controllers() if "scaleCompensate" in cmds.listAttr(c)]
        if controllers:
            for ctrl in controllers:
                cmds.setAttr(ctrl+".scaleCompensate", value)
                

    def create_ground_direction_shape(self, ctrl, radius, translate, value, *args):
        """ Create and add groundDirection shape control.
        """
        ground_direction_ctrl = self.create_controller("id_102_GroundDirection", "ground_direction_ctrl", r=self.dpCheckLinearUnit(radius), dir="+X", rot=(0, -90, 0))
        cmds.setAttr(ground_direction_ctrl+'.tz', self.dpCheckLinearUnit(translate))
        cmds.makeIdentity(ground_direction_ctrl, apply=True)
        self.transfer_shape(delete_source=True, clear_dest_shapes=False, source_item=ground_direction_ctrl, destinations=[ctrl], keep_color=True, force=False)
        # Add ground direction visibility attribute and connect
        cmds.addAttr(ctrl, longName="directionDisplay", attributeType="long", defaultValue=value, minValue=0, maxValue=1, keyable=False)
        cmds.setAttr(ctrl+".directionDisplay", channelBox=True)
        direction_shapes = cmds.listRelatives(ctrl, shapes=True)
        cmds.connectAttr(ctrl+".directionDisplay", direction_shapes[-1]+".visibility")
        if self.ar.data.display_sub_shape:
            cmds.setAttr(ctrl+".directionDisplay", 1)


    def get_ctrl_radius(self, item):
        """ Calculate and return the final radius to be used as a size of controls.
        """
        radius = float(cmds.getAttr(item+".translateX"))
        parents = self.ar.utils.get_parents(item)
        if (parents):
            for parent in parents:
                radius *= cmds.getAttr(parent+'.scaleX')
                if "worldSize" in cmds.listAttr(parent):
                    radius *= cmds.getAttr(parent+".worldSize")
        return radius
