# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
from ..base import base
from importlib import reload

# global variables to this module:    
CLASS_NAME = "Zipper"
TITLE = "m061_zipper"
DESCRIPTION = "m062_zipperDesc"
WIKI = "06-‐-Tools#-zipper"

ZIPPER_ATTR = "dpZipper"
ZIPPER_ID = "dpZipperID"



class Zipper(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        self.zipper_name = self.ar.data.lang['m061_zipper']
        self.first_name = self.ar.data.lang['c114_first']
        self.second_name = self.ar.data.lang['c115_second']
        self.good_to_dpar = True
        self.orig_model = None
        self.first_curve = None
        self.second_curve = None
        self.middle_curve = None
        self.first_blend_curve = None
        self.second_blend_curve = None
        self.curve_axis = 0
        self.curve_direction = "X"
        

    def build_tool(self, *args):
        self.dpZipperUI()
        self.load_data()
    
    
    def dpZipperUI(self, *args):
        """ Zipper UI layout and elements.
        """
        self.ar.utils.close_ui('dpZipperWindow')
        width  = 380
        height = 300
        cmds.window('dpZipperWindow', title=self.zipper_name+" "+str(self.ar.data.version), widthHeight=(width, height), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpZipperWindow')
        # create UI layout and elements:
        cmds.columnLayout('zipper_main_cl', adjustableColumn=True, columnOffset=("left", 10))
        cmds.text('zipper_select_poly_txt', label=self.ar.data.lang['i191_selectPoly'], align="left", height=30, font='boldLabelFont', parent='zipper_main_cl')
        # original model layout:
        cmds.rowColumnLayout('zipper_model_rcl', numberOfColumns=2, columnWidth=[(1, 160), (2, 210)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 10), (2, 'both', 10)], parent='zipper_main_cl')
        cmds.button('zipper_model_bt', label=self.ar.data.lang['i187_load']+" "+self.ar.data.lang['m152_originalModel']+" >>", command=self.load_orig_model, backgroundColor=(1.0, 0.9, 0.4), parent='zipper_model_rcl')
        cmds.textField('zipper_model_tf', editable=False, parent='zipper_model_rcl')
        cmds.separator(style='in', height=15, width=100, parent='zipper_main_cl')
        # polygon edges to curves layout:
        cmds.text('zipper_select_edges_txt', label=self.ar.data.lang['i188_selectEdges'], align="left", height=30, font='boldLabelFont', parent='zipper_main_cl')
        cmds.rowColumnLayout('zipper_buttons_rcl', numberOfColumns=2, columnWidth=[(1, 160), (2, 210)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 10), (2, 'both', 10)], rowSpacing=(1, 3), parent='zipper_main_cl')
        cmds.button('zipper_first_bt', label=self.ar.data.lang['i187_load']+" "+self.ar.data.lang['c114_first']+" "+self.ar.data.lang['i189_curve']+" >>", command=partial(self.create_curve_from_edge, "c114_first"), backgroundColor=(1.0, 0.9, 0.4), parent='zipper_buttons_rcl')
        cmds.textField('zipper_first_tf', editable=False, parent='zipper_buttons_rcl')
        cmds.button('zipper_second_bt', label=self.ar.data.lang['i187_load']+" "+self.ar.data.lang['c115_second']+" "+self.ar.data.lang['i189_curve']+" >>", command=partial(self.create_curve_from_edge, "c115_second"), backgroundColor=(1.0, 0.9, 0.4), parent='zipper_buttons_rcl')
        cmds.textField('zipper_second_tf', editable=False, parent='zipper_buttons_rcl')
        cmds.separator(style='in', height=15, width=100, parent='zipper_main_cl')
        # options layout:
        cmds.text('zipper_options_txt', label=self.ar.data.lang["i002_options"]+":", height=30, font='boldLabelFont', align='left', parent='zipper_main_cl')
        cmds.columnLayout('zipper_options_cl', adjustableColumn=True, columnOffset=("left", 10), rowSpacing=3, parent='zipper_main_cl')
        cmds.radioButtonGrp('zipper_curve_direction_rb', label=self.ar.data.lang['i189_curve']+' '+self.ar.data.lang['i106_direction'], labelArray3=['X', 'Y', 'Z'], columnAlign=[(1, 'left'), (2, 'left')], columnWidth=[(1, 100), (2, 50), (3, 50), (4, 50)], adjustableColumn=4, numberOfRadioButtons=3, select=1, changeCommand=self.get_curve_direction, vertical=False, parent='zipper_options_cl')
        cmds.checkBox('zipper_good_to_dpar_cb', label=self.ar.data.lang['i190_integrateDPAR'], value=1, align='left', parent='zipper_options_cl')
        cmds.separator(style='none', height=15, width=100, parent='zipper_main_cl')
        cmds.columnLayout('zipper_create_cl', columnOffset=("left", 10), parent='zipper_main_cl')
        cmds.button('zipper_create_bt', label=self.ar.data.lang["i158_create"]+" "+self.zipper_name, annotation=self.ar.data.lang["i158_create"]+" "+self.zipper_name, command=self.create_zipper, width=350, backgroundColor=(0.3, 1, 0.7), parent='zipper_create_cl')
    
    
    def get_good_to_dpar(self):
        """ Check if we'll integrate with dpAutoRigSystem.
        """
        self.good_to_dpar = cmds.checkBox('zipper_good_to_dpar_cb', query=True, value=True)
        return self.good_to_dpar
    
    
    def load_orig_model(self, *args):
        """ Load selected object as original model.
        """
        selected_nodes = cmds.ls(selection=True)
        if selected_nodes:
            if cmds.objectType(cmds.listRelatives(selected_nodes[0], children=True)[0]) == "mesh":
                cmds.textField('zipper_model_tf', edit=True, text=selected_nodes[0])
                cmds.button('zipper_model_bt', edit=True, label=self.ar.data.lang['m152_originalModel'], backgroundColor=(0.3, 0.8, 1.0))
                self.orig_model = selected_nodes[0]
        else:
            mel.eval('warning \"'+self.ar.data.lang['i191_selectPoly']+'\";')
    
    
    def create_curve_from_edge(self, zipper_id, *args):
        """ Create curve from selected polygon edges.
        """
        self.get_curve_direction()
        # declaring names:
        this_name = self.first_name
        if zipper_id == "c115_second":
            this_name = self.second_name
        curve_name = self.zipper_name+"_"+this_name+"_Crv"
        pec_name = self.zipper_name+"_"+this_name+"_PEC"
        # get selected edges:
        edges = cmds.ls(selection=True, flatten=True)
        if not edges == None and not edges == [] and not edges == "":
            # delete old curve:
            self.delete_old_curve(zipper_id)
            # create curve:
            base_curves = cmds.polyToCurve(name=curve_name, form=2, degree=3, conformToSmoothMeshPreview=0)
            self.ar.custom_attr.add_attr(0, base_curves, descendents=True) #dpID
            base_curve = base_curves[0]
            # rename polyEdgeToCurve node:
            cmds.rename(cmds.listConnections(base_curve+".create")[0], pec_name)
            # add attributes:
            cmds.addAttr(base_curve, longName=ZIPPER_ATTR, attributeType='bool')
            cmds.addAttr(base_curve, longName=ZIPPER_ID, dataType='string')
            cmds.setAttr(base_curve+"."+ZIPPER_ATTR, 1)
            cmds.setAttr(base_curve+"."+ZIPPER_ID, zipper_id, type="string")
            # load curve data:
            self.load_data(base_curve)
        else:
            mel.eval('warning \"'+self.ar.data.lang['i188_selectEdges']+'\";')
    
    
    def delete_old_curve(self, zipper_id):
        """ Check if exist the same old curve to delete it.
        """
        transforms = cmds.ls(selection=False, type="transform")
        if transforms:
            for node in transforms:
                if cmds.objExists(node+"."+ZIPPER_ATTR):
                    if cmds.getAttr(node+"."+ZIPPER_ATTR) == 1:
                        if cmds.getAttr(node+"."+ZIPPER_ID) == zipper_id:
                            cmds.delete(node)
    
    
    def load_data(self, curve_name=None):
        """ Load curve info from given curve name or try to find any zipper curve existing in the scene.
            Updates de UI after finding curves.
        """
        if curve_name:
            zipper_id = cmds.getAttr(curve_name+"."+ZIPPER_ID)
            self.update_ui(curve_name, zipper_id)
        else:
            cmds.textField('zipper_first_tf', edit=True, text="")
            cmds.textField('zipper_second_tf', edit=True, text="")
            transforms = cmds.ls(selection=False, type="transform")
            if transforms:
                for node in transforms:
                    if cmds.objExists(node+"."+ZIPPER_ATTR):
                        if cmds.getAttr(node+"."+ZIPPER_ATTR) == 1:
                            zipper_id = cmds.getAttr(node+"."+ZIPPER_ID)
                            self.update_ui(node, zipper_id)
    
    
    def update_ui(self, curve_name, zipper_id):
        """ Updates zipper UI with the given curve name and refresh the button, text field and curve variable.
        """        
        if zipper_id == "c114_first":
            cmds.textField('zipper_first_tf', edit=True, text=curve_name)
            cmds.button('zipper_first_bt', edit=True, label=self.first_name+" "+self.ar.data.lang['i189_curve'], backgroundColor=(0.3, 0.8, 1.0))
            self.first_curve = curve_name
        elif zipper_id == "c115_second":
            cmds.textField('zipper_second_tf', edit=True, text=curve_name)
            cmds.button('zipper_second_bt', edit=True, label=self.second_name+" "+self.ar.data.lang['i189_curve'], backgroundColor=(0.3, 0.8, 1.0))
            self.second_curve = curve_name
    
    
    def get_curve_direction(self, *args):
        """ Read radioButtonGrp selected item from UI.
            Set curve_axis variable to be used in the curve reverse setup if needed to set up curve direction.
            Update curve_direction variable value to be "X", "Y" or "Z".
        """
        selected_item = cmds.radioButtonGrp('zipper_curve_direction_rb', query=True, select=True)
        self.curve_axis = selected_item-1
        if selected_item == 1:
            self.curve_direction = "X"
        elif selected_item == 2:
            self.curve_direction = "Y"
        elif selected_item == 3:
            self.curve_direction = "Z"
    
    
    def set_curve_direction(self, curve_name):
        """ Check and set the curve direction.
            Reverse curve direction if the first CV position is greather than last CV position by current axis.
        """
        cmds.setAttr(curve_name+"."+ZIPPER_ATTR, 0)
        curve_length = len(cmds.ls(curve_name+".cv[*]", flatten=True))
        min_pos = cmds.xform(curve_name+".cv[0]", query=True, worldSpace=True, translation=True)[self.curve_axis]
        max_pos = cmds.xform(curve_name+".cv["+str(curve_length-1)+"]", query=True, worldSpace=True, translation=True)[self.curve_axis]
        if min_pos > max_pos:
            cmds.reverseCurve(curve_name, constructionHistory=True, replaceOriginal=True)
            self.to_ids.append(cmds.rename(cmds.listConnections(curve_name+".create")[0], self.ar.utils.extractSuffix(curve_name)+"_"+self.curve_direction+"_RevC"))
    
    
    def generate_middle_curve(self, origCurve):
        """ Create a middle curve using an avgCurves node.
        """
        self.middle_curve = cmds.duplicate(origCurve, name=self.zipper_name+"_"+self.ar.data.lang['c029_middle']+"_Crv")[0]
        average_curve_node = cmds.createNode('avgCurves', name=self.zipper_name+"_"+self.ar.data.lang['c029_middle']+"_AvgC")
        self.to_ids.append(average_curve_node)
        cmds.setAttr(average_curve_node+".automaticWeight", 0)
        cmds.connectAttr(self.first_curve+".worldSpace", average_curve_node+".inputCurve1", force=True)
        cmds.connectAttr(self.second_curve+".worldSpace", average_curve_node+".inputCurve2", force=True)
        cmds.connectAttr(average_curve_node+".outputCurve", self.middle_curve+".create", force=True)
    
    
    def create_curve_blend_setup(self):
        """ Create the main curve setup using blendShapes.
            Zipper_Ctrl has attributes to control automatic or manual blend.
            This method calculate the setRange values and clamp them to target weights of the curve blendShapes.
        """
        # declaring names:
        active_attr = "zipper"+self.ar.data.lang['c118_active'].capitalize()
        crescent_attr = self.ar.data.lang['c116_crescent']
        decrescent_attr = self.ar.data.lang['c117_decrescent']
        auto_attr = self.ar.data.lang['c119_auto']
        auto_intensity_attr = self.ar.data.lang['c119_auto']+self.ar.data.lang['c049_intensity'].capitalize()
        auto_calibrate_min_attr = self.ar.data.lang['c119_auto']+self.ar.data.lang['c111_calibrate']+"Min"
        auto_calibrate_max_attr = self.ar.data.lang['c119_auto']+self.ar.data.lang['c111_calibrate']+"Max"
        initial_distance_attr = "initialDistance"
        distance_attr = "distance"
        rig_scale_attr = "rigScale"
        
        # create zipper control and attributes:
        radius = cmds.xform(self.first_curve+".cv["+str(len(cmds.ls(self.first_curve+".cv[*]", flatten=True))-1)+"]", query=True, worldSpace=True, translation=True)[self.curve_axis]*0.3
        self.zipper_ctrl = self.ar.ctrls.cvControl('id_074_Zipper', self.zipper_name+"_Ctrl", r=radius, d=0)
        self.ar.ctrls.colorShape([self.zipper_ctrl], "cyan")
        cmds.addAttr(self.zipper_ctrl, longName=active_attr, attributeType='float', minValue=0, defaultValue=1, maxValue=1, keyable=True)
        cmds.addAttr(self.zipper_ctrl, longName=crescent_attr, attributeType='float', minValue=0, defaultValue=0, maxValue=1, keyable=True)
        cmds.addAttr(self.zipper_ctrl, longName=decrescent_attr, attributeType='float', minValue=0, defaultValue=0, maxValue=1, keyable=True)
        cmds.addAttr(self.zipper_ctrl, longName=auto_attr, attributeType='float', minValue=0, defaultValue=0, maxValue=1, keyable=True)
        cmds.addAttr(self.zipper_ctrl, longName=auto_intensity_attr, attributeType='float', defaultValue=1, keyable=True)
        cmds.addAttr(self.zipper_ctrl, longName=auto_calibrate_min_attr, attributeType='float', defaultValue=0)
        cmds.addAttr(self.zipper_ctrl, longName=auto_calibrate_max_attr, attributeType='float', defaultValue=1)
        cmds.addAttr(self.zipper_ctrl, longName=initial_distance_attr, attributeType='float', defaultValue=0)
        cmds.addAttr(self.zipper_ctrl, longName=distance_attr, attributeType='float', defaultValue=0)
        cmds.addAttr(self.zipper_ctrl, longName=rig_scale_attr, attributeType='float', defaultValue=1)
        self.ar.ctrls.setStringAttrFromList(self.zipper_ctrl, [auto_calibrate_min_attr, auto_calibrate_max_attr])
        
        self.ctrl_grp = cmds.group(self.zipper_ctrl, name=self.zipper_name+"_Control_Grp")
        self.to_ids.append(self.ctrl_grp)
        
        # create blend curves and connect create input from first and second curves:
        self.first_blend_curve = cmds.duplicate(self.first_curve, name=self.ar.utils.extractSuffix(self.first_curve)+"_Blend_Crv")[0]
        self.second_blend_curve = cmds.duplicate(self.second_curve, name=self.ar.utils.extractSuffix(self.second_curve)+"_Blend_Crv")[0]
        cmds.connectAttr(self.first_curve+".worldSpace", self.first_blend_curve+".create", force=True)
        cmds.connectAttr(self.second_curve+".worldSpace", self.second_blend_curve+".create", force=True)
        
        # create curve blendShapes
        self.first_bs = cmds.blendShape(self.middle_curve, self.first_blend_curve, topologyCheck=False, name=self.ar.utils.extractSuffix(self.first_curve)+"_BS")[0]
        self.second_bs = cmds.blendShape(self.middle_curve, self.second_blend_curve, topologyCheck=False, name=self.ar.utils.extractSuffix(self.second_curve)+"_BS")[0]
        cmds.connectAttr(self.zipper_ctrl+"."+active_attr, self.first_bs+"."+self.middle_curve, force=True)
        cmds.connectAttr(self.zipper_ctrl+"."+active_attr, self.second_bs+"."+self.middle_curve, force=True)
        
        # distance dimension to calculate automatic setup:
        dist_dim_shape = cmds.distanceDimension(startPoint=(10, 100, 1000), endPoint=(11, 101, 101)) #magic numbers to avoid get existing locator at origin
        self.dist_dim_transform = cmds.listRelatives(dist_dim_shape, parent=True, type="transform")[0]
        self.dist_dim_transform = cmds.rename(self.dist_dim_transform, self.zipper_name+"_"+auto_attr.capitalize()+"_DD")
        dist_dim_shape = self.dist_dim_transform+"Shape"
        cmds.connectAttr(dist_dim_shape+"."+distance_attr, self.zipper_ctrl+"."+distance_attr, force=True)
        cmds.setAttr(self.zipper_ctrl+"."+distance_attr, lock=True)
        self.first_loc = cmds.listConnections(dist_dim_shape+".startPoint", source=True, destination=False)[0]
        self.first_loc = cmds.rename(self.first_loc, self.zipper_name+"_"+auto_attr.capitalize()+"_"+self.first_name+"_Loc")
        self.second_loc = cmds.listConnections(dist_dim_shape+".endPoint", source=True, destination=False)[0]
        self.second_loc = cmds.rename(self.second_loc, self.zipper_name+"_"+auto_attr.capitalize()+"_"+self.second_name+"_Loc")
        # attach locators to original curves:
        first_mop = self.ar.utils.attachToMotionPath(self.first_loc, self.first_curve, self.zipper_name+"_"+auto_attr.capitalize()+"_"+self.first_name+"_MoP", 0.5)
        second_mop = self.ar.utils.attachToMotionPath(self.second_loc, self.second_curve, self.zipper_name+"_"+auto_attr.capitalize()+"_"+self.second_name+"_MoP", 0.5)
        
        # automatic intensity and calibration:
        auto_on_off_md = cmds.createNode("multiplyDivide", name=self.zipper_name+"_"+auto_attr.capitalize()+"_OnOff_MD")
        auto_max_calibrate_md = cmds.createNode("multiplyDivide", name=self.zipper_name+"_"+auto_attr.capitalize()+"_MD")
        rig_scale_md = cmds.createNode("multiplyDivide", name=self.zipper_name+"_RigScale_MD")
        rig_scale_auto_md = cmds.createNode("multiplyDivide", name=self.zipper_name+"_RigScale_Auto_MD")
        hyperbole_scale_md = cmds.createNode("multiplyDivide", name=self.zipper_name+"_HyperboleScale_MD")
        auto_main_sr = cmds.createNode("setRange", name=self.zipper_name+"_"+auto_attr.capitalize()+"_SR")
        cmds.connectAttr(self.zipper_ctrl+"."+auto_attr, auto_on_off_md+".input1X", force=True)
        cmds.connectAttr(auto_main_sr+".outValueX", auto_on_off_md+".input2X", force=True)
        cmds.connectAttr(self.zipper_ctrl+"."+auto_intensity_attr, auto_max_calibrate_md+".input1X", force=True)
        cmds.connectAttr(self.zipper_ctrl+"."+auto_calibrate_max_attr, auto_max_calibrate_md+".input2X", force=True)
        
        # auto distance:
        initial_distance = cmds.getAttr(dist_dim_shape+"."+distance_attr)
        cmds.setAttr(self.zipper_ctrl+"."+initial_distance_attr, initial_distance, lock=True)
        cmds.setAttr(self.zipper_ctrl+"."+auto_calibrate_min_attr, (-10)*initial_distance)
        cmds.setAttr(self.zipper_ctrl+"."+auto_calibrate_max_attr, (20)*initial_distance) #magic numbers, need to be calibrated
        cmds.setAttr(auto_main_sr+".minX", 1)
        cmds.setAttr(hyperbole_scale_md+".input1X", 1)
        cmds.setAttr(hyperbole_scale_md+".operation", 2) #divide
        cmds.connectAttr(self.zipper_ctrl+"."+auto_calibrate_min_attr, auto_main_sr+".oldMinX", force=True)
        cmds.connectAttr(auto_max_calibrate_md+".outputX", auto_main_sr+".oldMaxX", force=True)
        # rig scale setup to work with automatic distance:
        cmds.connectAttr(self.zipper_ctrl+"."+initial_distance_attr, rig_scale_md+".input1X", force=True)
        cmds.connectAttr(self.zipper_ctrl+"."+rig_scale_attr, rig_scale_md+".input2X", force=True)
        cmds.connectAttr(rig_scale_md+".outputX", hyperbole_scale_md+".input2X", force=True)
        cmds.connectAttr(self.zipper_ctrl+"."+distance_attr, rig_scale_auto_md+".input1X", force=True)
        cmds.connectAttr(hyperbole_scale_md+".outputX", rig_scale_auto_md+".input2X", force=True)
        cmds.connectAttr(rig_scale_auto_md+".outputX", auto_main_sr+".valueX", force=True)
        
        # calculate iter counter from middle curve length:
        self.curve_length = len(cmds.ls(self.middle_curve+".cv[*]", flatten=True))
        half_curve_length = self.curve_length * 0.5
        # calculate distance position based 1.0 from our control attribute:
        dist_pos = 1.0 / self.curve_length
        for c, curve in enumerate([self.first_curve, self.second_curve]):
            base_name = self.ar.utils.extractSuffix(curve)
            for i in range(0, self.curve_length+1):
                left_a_pos = (i * dist_pos)
                left_b_pos = (left_a_pos + half_curve_length)
                right_b_pos = 1 - (i * half_curve_length)
                right_a_pos = (right_b_pos - half_curve_length)
                if i > 0:
                    left_a_pos = left_a_pos - (half_curve_length*0.5)
                    right_a_pos = right_a_pos - (half_curve_length*0.5)
                if left_a_pos < 0:
                    left_a_pos = 0
                if right_a_pos < 0:
                    right_a_pos = 0
                # create setRange nodes:
                crescent_sr = cmds.createNode("setRange", name=base_name+"_"+crescent_attr+"_"+str(i)+"_SR")
                decrescent_sr = cmds.createNode("setRange", name=base_name+"_"+decrescent_attr+"_"+str(i)+"_SR")
                # set values for serRange nodes:
                cmds.setAttr(crescent_sr+".oldMinX", left_a_pos)
                cmds.setAttr(crescent_sr+".oldMaxX", left_b_pos)
                cmds.setAttr(crescent_sr+".maxX", 1)
                cmds.setAttr(decrescent_sr+".oldMinX", right_a_pos)
                cmds.setAttr(decrescent_sr+".oldMaxX", right_b_pos)
                cmds.setAttr(decrescent_sr+".maxX", 1)
                # connect attributes from control to setRange:
                cmds.connectAttr(self.zipper_ctrl+"."+crescent_attr, crescent_sr+".valueX", force=True)
                cmds.connectAttr(self.zipper_ctrl+"."+decrescent_attr, decrescent_sr+".valueX", force=True)
                # add values for two sides and auto too:
                zipper_pma = cmds.createNode("plusMinusAverage", name=base_name+"_"+str(i)+"_PMA")
                cmds.connectAttr(crescent_sr+".outValueX", zipper_pma+".input1D[0]", force=True)
                cmds.connectAttr(decrescent_sr+".outValueX", zipper_pma+".input1D[1]", force=True)
                # add auto setRange value:
                auto_a_pos = left_a_pos
                auto_b_pos = left_b_pos
                if i > half_curve_length:
                    auto_a_pos = right_a_pos
                    auto_b_pos = right_b_pos
                auto_sr = cmds.createNode("setRange", name=base_name+"_"+auto_attr.capitalize()+"_"+str(i)+"_SR")
                cmds.setAttr(auto_sr+".oldMinX", auto_a_pos)
                cmds.setAttr(auto_sr+".oldMaxX", auto_b_pos)
                cmds.setAttr(auto_sr+".maxX", 1)
                # turn on or off this channel by zipperCtrl attribute:
                cmds.connectAttr(auto_on_off_md+".outputX", auto_sr+".valueX", force=True)
                cmds.connectAttr(auto_sr+".outValueX", zipper_pma+".input1D[2]", force=True)
                # clamp max value to 1 in order to connect it to the blend setup
                zipper_clp = cmds.createNode("clamp", name=base_name+"_"+str(i)+"_Clp")
                cmds.setAttr(zipper_clp+".maxR", 1)
                cmds.connectAttr(zipper_pma+".output1D", zipper_clp+".inputR", force=True)
                # output clamp value to blendShape node target weights:
                if c == 0:
                    cmds.connectAttr(zipper_clp+".outputR", self.first_bs+".inputTarget[0].inputTargetGroup[0].targetWeights["+str(i)+"]")
                    cmds.connectAttr(zipper_clp+".outputR", self.second_bs+".inputTarget[0].inputTargetGroup[0].targetWeights["+str(i)+"]")
                self.to_ids.extend([crescent_sr, decrescent_sr, zipper_pma, auto_sr, zipper_clp])
        self.to_ids.extend([self.first_bs, self.second_bs, first_mop, second_mop, auto_on_off_md, auto_max_calibrate_md, rig_scale_md, rig_scale_auto_md, hyperbole_scale_md, auto_main_sr])
    

    def parent_zipper_ctrl(self, rig_scale_attr="rigScale"):
        """ Try to parent the zipper controller to head sub controller or to controls visibility group.
        """
        # check if there's a dpAR Option_Ctrl:
        if self.good_to_dpar:
            option_ctrl = self.ar.utils.getNodeByMessage("optionCtrl")
            if option_ctrl:
                opt_ctrl_rig_scale_node = cmds.listConnections(option_ctrl+"."+rig_scale_attr, source=False, destination=True)[0]
                cmds.connectAttr(opt_ctrl_rig_scale_node+".outputX", self.zipper_ctrl+"."+rig_scale_attr, force=True)
                cmds.setAttr(self.zipper_ctrl+"."+rig_scale_attr, lock=True)
            head_sub_ctrl = self.ar.ctrls.getControlNodeById("id_093_HeadSub")
            if head_sub_ctrl:
                cmds.parent(self.ctrl_grp, head_sub_ctrl)
            else:
                ctrls_vis_grp = self.ar.utils.getNodeByMessage("ctrlsVisibilityGrp")
                if ctrls_vis_grp:
                    cmds.parent(self.ctrl_grp, ctrls_vis_grp)


    def create_deform_mesh(self):
        """ Generate a final deformable mesh from original loaded mesh.
            Parent old original model to Support_Grp and rename it to _Geo.
            Rename the new final dformable mesh as _Def_Mesh and put it inside Render_Grp.
        """
        # store old mesh name:
        old_mesh_name = self.orig_model
        # generate deform_mesh from orig_model:
        self.deform_mesh = cmds.polyDuplicateAndConnect(self.orig_model)
        # rename geometries:
        self.orig_model = cmds.rename(self.orig_model, self.ar.utils.extractSuffix(self.orig_model)+"_Orig_Geo")
        self.deform_mesh = cmds.rename(self.deform_mesh, self.ar.utils.extractSuffix(old_mesh_name)+"_Def_Mesh")
        self.to_ids.extend([self.orig_model, self.deform_mesh])
        cmds.setAttr(self.orig_model+".visibility", 0)
        # parent if need:
        support_grp = self.ar.utils.getNodeByMessage("supportGrp")
        if support_grp:
            cmds.parent(self.orig_model, support_grp)
            self.ar.ctrls.colorShape([support_grp], [0.51, 1, 0.667], outliner=True) #green
        render_grp = self.ar.utils.getNodeByMessage("renderGrp")
        if render_grp:
            # avoid reparent deform_mesh if already inside RenderGrp:
            parents, all_parents = [], []
            parents.append(self.deform_mesh)
            while parents:
                parents = cmds.listRelatives(parents[0], allParents=True, type="transform")
                if parents:
                    all_parents.append(parents[0])
            if not render_grp in all_parents:
                cmds.parent(self.deform_mesh, render_grp)
    
    
    def create_wire_deform(self):
        """ Create two wire deformer for first and second curves.
        """
        first_wire_def = cmds.wire(self.deform_mesh, groupWithBase=False, crossingEffect=0, localInfluence=1, dropoffDistance=(0, 1), name=self.ar.utils.extractSuffix(self.deform_mesh)+"_First_Wire")[0]
        second_wire_def = cmds.wire(self.deform_mesh, groupWithBase=False, crossingEffect=0, localInfluence=1, dropoffDistance=(1, 1), name=self.ar.utils.extractSuffix(self.deform_mesh)+"_Second_Wire")[0]
        cmds.connectAttr(self.first_curve+".worldSpace[0]", first_wire_def+".baseWire[0]", force=True)
        cmds.connectAttr(self.second_curve+".worldSpace[0]", second_wire_def+".baseWire[1]", force=True)
        cmds.connectAttr(self.first_blend_curve+".worldSpace[0]", first_wire_def+".deformedWire[0]", force=True)
        cmds.connectAttr(self.second_blend_curve+".worldSpace[0]", second_wire_def+".deformedWire[1]", force=True)
        self.to_ids.extend([first_wire_def, second_wire_def])
    
    
    def set_controller_position(self, curve_name):
        """ Change the controller position to be more rigger and animator friendly.
        """
        base_pos = cmds.xform(curve_name+".cv["+str(self.curve_length-1)+"]", query=True, worldSpace=True, translation=True)
        for a, axis in enumerate(self.ar.data.axes):
            factor = 1
            if axis == self.curve_direction:
                factor = 2.5
            cmds.setAttr(self.ctrl_grp+".translate"+axis, base_pos[a]*factor)


    def zipper_data_grp(self):
        """ Store nodes to Static Group in Data Group.
        """
        zipper_curves_grp = cmds.group(self.first_curve, self.second_curve, self.middle_curve, self.first_blend_curve, self.second_blend_curve, name=self.zipper_name+"_Curves_Grp")
        zipper_distance_grp = cmds.group(self.first_loc, self.second_loc, self.dist_dim_transform, name=self.zipper_name+"_Distance_Grp")
        zipper_grp = cmds.group(zipper_curves_grp, zipper_distance_grp, name=self.zipper_name+"_Data_Grp")
        self.to_ids.append(zipper_grp)
        if self.good_to_dpar:
            static_grp = self.ar.utils.getNodeByMessage("staticGrp")
            if static_grp:
                cmds.parent(zipper_grp, static_grp)
    
    
    def create_zipper(self, *args):
        """ Main method to buid the all zipper setup.
            Uses the pre-defined and loaded curves.
        """
        run_dialog = cmds.confirmDialog(title="Zipper", message=self.ar.data.lang["i192_notUndoable"], button=[self.ar.data.lang["i174_continue"],self.ar.data.lang["i132_cancel"]], defaultButton=self.ar.data.lang["i174_continue"], cancelButton=self.ar.data.lang["i132_cancel"], dismissString=self.ar.data.lang["i132_cancel"])
        if run_dialog == self.ar.data.lang["i174_continue"]:
            self.get_good_to_dpar()
            if self.first_curve and self.second_curve:
                if self.orig_model:
                    self.to_ids = []
                    self.old_add_double_linear_items = cmds.ls(selection=False, type="addDoubleLinear")
                    self.get_curve_direction()
                    self.set_curve_direction(self.first_curve)
                    self.set_curve_direction(self.second_curve)
                    self.generate_middle_curve(self.first_curve)
                    self.create_curve_blend_setup()
                    self.create_deform_mesh()
                    self.create_wire_deform()
                    self.set_controller_position(self.first_curve)
                    self.parent_zipper_ctrl()
                    self.zipper_data_grp()
                    self.ar.utils.close_ui("dpZipperWindow")
                    self.ar.utils.nodeRenamingTreatment(list(set(cmds.ls(selection=False, type="addDoubleLinear"))-set(self.old_add_double_linear_items)), "addDoubleLinear", "_ADL")
                    self.ar.custom_attr.add_attr(0, self.to_ids, descendents=True) #dpID
                    cmds.select(self.zipper_ctrl)
                    print(self.ar.data.lang['m174_createdZipper'])
                else:
                    mel.eval('warning \"'+self.ar.data.lang['i191_selectPoly']+'\";')
            else:
                mel.eval('warning \"'+self.ar.data.lang['i188_selectEdges']+'\";')
