# importing libraries:
from maya import cmds
from maya import mel
from ..base import base
from importlib import reload

# global variables to this module:    
CLASS_NAME = "CorrectionManager"
TITLE = "m068_correctionManager"
DESCRIPTION = "m069_correctionManagerDesc"
WIKI = "06-‐-Tools#-correction-manager"

ANGLE = "Angle"
DISTANCE = "Distance"



class CorrectionManager(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        self.angle_name = ANGLE
        self.distance_name = DISTANCE
        self.net_suffix = "Net"
        self.cm_data_grp = "CorrectionManager_Data_Grp"
        self.nets = []
        self.net = None

    
    def build_tool(self, *args):
        # call main UI function
        if self.ar.data.ui_state:
            self.ar.correction_manager_ui.create_ui(self)


    def rename_linked_nodes(self, old_name, name):
        """ List all connected nodes by message into the network and rename them using given parameters.
        """
        message_attrs = []
        attributes = cmds.listAttr(self.net)
        for attr in attributes:
            if cmds.getAttr(self.net+"."+attr, type=True) == "message":
                message_attrs.append(attr)
        if message_attrs:
            for message_attr in message_attrs:
                connections = cmds.listConnections(self.net+"."+message_attr)
                if connections:
                    children = cmds.listRelatives(connections[0], children=True, allDescendents=True)
                    cmds.rename(connections[0], connections[0].replace(old_name, name))
                    self.ar.custom_attr.updateID([connections[0].replace(old_name, name)])
                    if children:
                        for child in children:
                            try:
                                cmds.rename(child, child.replace(old_name, name))
                                self.ar.custom_attr.updateID([child.replace(old_name, name)])
                            except:
                                pass


    def get_distance(self):
        """ Returns the distance value read from the distance between node.
        """
        if cmds.getAttr(self.net+".type") == self.distance_name:
            dist_bet = cmds.listConnections(self.net+".distanceBet")[0]
            if dist_bet:
                return cmds.getAttr(dist_bet+".distance")


    def change_name(self, name=None, *args):
        """ Edit name of the current network node selected.
            If there isn't any given name, it will try to get from the UI.
            Returns the name result.
        """
        old_name = cmds.getAttr(self.net+".name")
        if not name:
            if self.ar.data.ui_state:
                name = cmds.textFieldGrp("correction_name_tfg", query=True, text=True)
        if name:
            name = self.ar.utils.resolveName(name, self.net_suffix)[0]
            self.rename_linked_nodes(old_name, name)
            cmds.setAttr(self.net+".name", name, type="string")
            self.net = cmds.rename(self.net, self.net.replace(old_name, name))
            if self.ar.data.ui_state:
                self.ar.correction_manager_ui.populate_net_ui()
                #self.ar.correction_manager_ui.update_edit_net_layout() #Bug: if we call this method here it will crash Maya! Error report: 322305477
                if cmds.textFieldGrp("correction_name_tfg", query=True, exists=True):
                    cmds.textFieldGrp("correction_name_tfg", label=self.ar.data.lang['m006_name'], edit=True, text=name)
        return name


    def change_axis(self, axis=None, *args):
        """ Update the setup to read the correct axis to extract angle or decompose distance vector.
        """
        cmds.setAttr(self.net+".axis", self.ar.data.axes.index(axis.upper()))
        
        
    def change_axis_order(self, axisOrder=None, *args):
        """ Update the setup to set the correct axis order to extract angle.
        """
        if cmds.getAttr(self.net+".type") == self.angle_name:
            cmds.setAttr(self.net+".axisOrder", self.ar.data.axis_orders.index(axisOrder.upper()))


    def change_input_values(self, min_value=None, max_value=None, *args):
        """ Update the setup to set the choose input min and max values.
            That means we can read the angle or distance in this given range.
        """
        cmds.setAttr(self.net+".inputStart", min_value)
        cmds.setAttr(self.net+".inputEnd", max_value)


    def change_output_values(self, min_value=None, max_value=None, *args):
        """ Update the setup to set the choose output min and max values.
            That means we can output the final value in this given range.
        """
        cmds.setAttr(self.net+".outputStart", min_value)
        cmds.setAttr(self.net+".outputEnd", max_value)


    def change_decompose(self, value=None, *args):
        """ Update the decompose boolean attribute using the value comming from the UI checkBox.
        """
        cmds.setAttr(self.net+".decompose", value)
        if self.ar.data.ui_state:
            cmds.optionMenu('correction_axis_om', edit=True, enable=value)


    def change_interpolation(self, interp=None, *args):
        """ Just set the interpolation method of the remapValue to this given argument.
        """
        if interp == "Linear":
            cmds.setAttr(self.net+".interpolation", 0)
        elif interp == "Smooth":
            cmds.setAttr(self.net+".interpolation", 1)
        else: #Spline
            cmds.setAttr(self.net+".interpolation", 2)


    def delete_setup(self, *args):
        """ Just delete these nodes to clear this current system setup:
            - Rivets if exists
            - Rivet_Grp if exists and empty
            - Correction Data Group
            - Network Data Node
            - Correction Manager Data Group if empty
        """
        net_attributes = cmds.listAttr(self.net)
        if net_attributes:
            for net_attr in net_attributes:
                if "Rivet" in net_attr:
                    try:
                        cmds.delete(self.ar.utils.getNodeByMessage(net_attr, self.net))
                    except:
                        pass
        if cmds.objExists("Rivet_Grp"):
            if not cmds.listRelatives("Rivet_Grp", allDescendents=True, children=True):
                cmds.delete("Rivet_Grp")
        try:
            cmds.delete(self.ar.utils.getNodeByMessage("correction_data_grp", self.net))
        except:
            pass
        cmds.delete(self.net)
        if cmds.objExists(self.cm_data_grp):
            if not cmds.listRelatives(self.cm_data_grp, allDescendents=True, children=True):
                try:
                    cmds.delete(self.cm_data_grp)
                except:
                    pass
        if self.ar.data.ui_state:
            self.ar.correction_manager_ui.populate_net_ui()
            self.ar.correction_manager_ui.update_edit_net_layout()


    def create_corrective_locator(self, name, to_attach, to_rivet=False):
        """ Creates a space locator, zeroOut it to receive a parentConstraint.
            Return the locator to use it as a reader node to the system.
        """
        if cmds.objExists(to_attach):
            loc = cmds.spaceLocator(name=name+"_Loc")[0]
            cmds.addAttr(loc, longName="inputNode", attributeType="message")
            cmds.connectAttr(to_attach+".message", loc+".inputNode", force=True)
            grp = self.ar.utils.zeroOut([loc])[0]
            if to_rivet:
                rivet_node = self.rivet.dpCreateRivet(to_attach, "AnyUVSet", [grp], True, False, False, False, False, False, False, useOffset=False)[-1]
                cmds.addAttr(self.net, longName=to_attach+"_Rivet", attributeType="message")
                cmds.connectAttr(rivet_node+".message", self.net+"."+to_attach+"_Rivet", force=True)
            else:
                cmds.parentConstraint(to_attach, grp, maintainOffset=False, name=grp+"_PaC")
                cmds.scaleConstraint(to_attach, grp, maintainOffset=True, name=grp+"_ScC")
            cmds.parent(grp, self.ar.utils.getNodeByMessage("correctionDataGrp", self.net))
            return loc
        else:
            mel.eval('warning \"'+to_attach+' '+self.ar.data.lang['i061_notExists']+'\";')


    def create_correction_manager_setup(self, nodes=None, name=None, correct_type=None, to_rivet=False, from_ui=False, *args):
        """ Create nodes to calculate the correction we want to mapper fix.
            Returns the created network node.
        """
        # loading Maya matrix node
        loaded_quaternion_plugin = self.ar.utils.checkLoadedPlugin("quatNodes", self.ar.data.lang['e014_cantLoadQuatNode'])
        loaded_matrix_plugin = self.ar.utils.checkLoadedPlugin("matrixNodes", self.ar.data.lang['e002_matrixPluginNotFound'])
        if loaded_quaternion_plugin and loaded_matrix_plugin:
            if not nodes:
                nodes = cmds.ls(selection=True, flatten=True)
            if nodes:
                if len(nodes) == 2:
                    self.to_ids = []
                    orig_node = nodes[0]
                    action_node = nodes[1]
                    cmds.undoInfo(openChunk=True)
                    
                    # main group
                    if not cmds.objExists(self.cm_data_grp):
                        self.cm_data_grp = cmds.group(empty=True, name=self.cm_data_grp)
                        cmds.addAttr(self.cm_data_grp, longName="dpCorrectionManagerDataGrp", attributeType="bool")
                        cmds.setAttr(self.cm_data_grp+".dpCorrectionManagerDataGrp", 1)
                        self.ar.ctrls.setLockHide([self.cm_data_grp], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
                        scalable_grp = self.ar.utils.getNodeByMessage("scalable_grp")
                        if scalable_grp:
                            cmds.parent(self.cm_data_grp, scalable_grp)
                        cmds.setAttr(self.cm_data_grp+".visibility", 0)

                    # naming
                    if not name:
                        name = cmds.textField('correction_create_tf', query=True, text=True)
                        if not name:
                            name = "Correction"
                    correction_name, name = self.ar.utils.resolveName(name, self.net_suffix)
                    
                    # type
                    if not correct_type:
                        if self.ar.data.ui_state:
                            correct_type = cmds.radioButton(cmds.radioCollection('correction_type_rc', query=True, select=True), query=True, annotation=True) #typeSelectedRadioButton
                        if not correct_type:
                            correct_type = self.angle_name

                    # rivet
                    if from_ui:
                        to_rivet = cmds.checkBox('correction_rivet_cb', query=True, value=True)
                    if to_rivet:
                        self.rivet = self.ar.config.get_instance("Rivet", [self.ar.data.tools_folder])
                        self.rivet.ui = False

                    # create the container of the system data using a network node
                    self.net = cmds.createNode("network", name=name)
                    cmds.addAttr(self.net, longName="dpNetwork", attributeType="bool")
                    cmds.addAttr(self.net, longName="dpCorrectionManager", attributeType="bool")
                    cmds.addAttr(self.net, longName="name", dataType="string")
                    cmds.addAttr(self.net, longName="type", dataType="string")
                    cmds.addAttr(self.net, longName="inputValue", attributeType="float")
                    cmds.addAttr(self.net, longName="interpolation", attributeType='enum', enumName="Linear:Smooth:Spline")
                    cmds.addAttr(self.net, longName="decompose", attributeType="bool", defaultValue=0)
                    cmds.addAttr(self.net, longName="axis", attributeType='enum', enumName="X:Y:Z")
                    cmds.addAttr(self.net, longName="axisOrder", attributeType='enum', enumName="XYZ:YZX:ZXY:XZY:YXZ:ZYX")
                    cmds.addAttr(self.net, longName="inputStart", attributeType="float", defaultValue=0)
                    cmds.addAttr(self.net, longName="inputEnd", attributeType="float", defaultValue=90)
                    cmds.addAttr(self.net, longName="outputStart", attributeType="float", defaultValue=0)
                    cmds.addAttr(self.net, longName="outputEnd", attributeType="float", defaultValue=1)
                    # add serialization attributes
                    message_attrs = ["correctionDataGrp", "originalLoc", "actionLoc", "correctiveMD", "extractAngleMM", "extractAngleDM", "extractAngleQtE", "extractAngleMD", "angleAxisChc", "smallerThanOneCnd", "overZeroCnd", "interpolationPMA", "inputRmV", "outputSR"]
                    if correct_type == self.distance_name:
                        message_attrs = ["correctionDataGrp", "originalLoc", "actionLoc", "correctiveMD", "outputRmV", "distanceBet", "distanceAllCnd", "distanceAxisExtractPMA", "distanceAxisXCnd", "distanceAxisYZCnd", "interpolationPMA", "distanceScaleMD"]
                    for message_attr in message_attrs:
                        cmds.addAttr(self.net, longName=message_attr, attributeType="message")
                    cmds.addAttr(self.net, longName="inputRigScale", attributeType="float", defaultValue=1)
                    option_ctrl = self.ar.utils.getNodeByMessage("optionCtrl")
                    if option_ctrl:
                        cmds.connectAttr(option_ctrl+".rigScaleOutput", self.net+".inputRigScale", force=True)
                    cmds.addAttr(self.net, longName="corrective", attributeType="float", minValue=0, defaultValue=1, maxValue=1)
                    cmds.addAttr(self.net, longName="outputValue", attributeType="float")
                    cmds.setAttr(self.net+".dpNetwork", 1)
                    cmds.setAttr(self.net+".dpCorrectionManager", 1)
                    cmds.setAttr(self.net+".name", correction_name, type="string")
                    cmds.setAttr(self.net+".type", correct_type, type="string")
                    # setup group
                    correction_data_grp = cmds.group(empty=True, name=correction_name+"_Grp")
                    cmds.parent(correction_data_grp, self.cm_data_grp)
                    cmds.connectAttr(correction_data_grp+".message", self.net+".correctionDataGrp", force=True)
                    original_loc = self.create_corrective_locator(correction_name+"_Original", orig_node, to_rivet)
                    action_loc = self.create_corrective_locator(correction_name+"_Action", action_node, to_rivet)
                    cmds.connectAttr(original_loc+".message", self.net+".originalLoc", force=True)
                    cmds.connectAttr(action_loc+".message", self.net+".actionLoc", force=True)

                    # create corrective, interpolation and rigScale nodes:
                    corrective_md = cmds.createNode("multiplyDivide", name=correction_name+"_Corrective_MD")
                    interpolation_pma = cmds.createNode("plusMinusAverage", name=correction_name+"_Interpolation_PMA")
                    self.to_ids.extend([self.net, corrective_md, interpolation_pma])
                    cmds.connectAttr(corrective_md+".message", self.net+".correctiveMD", force=True)
                    cmds.connectAttr(interpolation_pma+".message", self.net+".interpolationPMA", force=True)
                    cmds.connectAttr(self.net+".corrective", corrective_md+".input2X", force=True)
                    cmds.connectAttr(self.net+".interpolation", interpolation_pma+".input1D[0]", force=True)
                    cmds.setAttr(interpolation_pma+".input1D[1]", 1)
                    
                    # if rotate extration option:
                    if correct_type == self.angle_name:                        
                        # write a new self.ar.utils function to generate these matrix nodes here:
                        extract_angle_mm = cmds.createNode("multMatrix", name=correction_name+"_ExtractAngle_MM")
                        extract_angle_dm = cmds.createNode("decomposeMatrix", name=correction_name+"_ExtractAngle_DM")
                        extract_angle_qte = cmds.createNode("quatToEuler", name=correction_name+"_ExtractAngle_QtE")
                        extract_angle_md = cmds.createNode("multiplyDivide", name=correction_name+"_ExtractAngle_MD")
                        # workaround to generate UnitConversion nodes before connect to Choice node (passing by a temporary MultiplyDivide)
                        angle_unit_convertion_md = cmds.createNode("multiplyDivide", name=correction_name+"_ExtractAngle_UnitConversion_MD")
                        angle_axis_chc = cmds.createNode("choice", name=correction_name+"_ExtractAngle_Axis_Chc")
                        smaller_than_one_cnd = cmds.createNode("condition", name=correction_name+"_ExtractAngle_SmallerThanOne_Cnd")
                        over_zero_cnd = cmds.createNode("condition", name=correction_name+"_ExtractAngle_OverZero_Cnd")
                        input_rmv = cmds.createNode("remapValue", name=correction_name+"_Input_RmV")
                        output_sr = cmds.createNode("setRange", name=correction_name+"_Output_SR")
                        self.to_ids.extend([extract_angle_mm, extract_angle_dm, extract_angle_qte, extract_angle_md, angle_unit_convertion_md, angle_axis_chc, smaller_than_one_cnd, over_zero_cnd, input_rmv, output_sr])
                        cmds.setAttr(extract_angle_md+".operation", 2)
                        cmds.setAttr(smaller_than_one_cnd+".operation", 5) #less or equal
                        cmds.setAttr(smaller_than_one_cnd+".secondTerm", 1)
                        cmds.setAttr(over_zero_cnd+".secondTerm", 0)
                        cmds.setAttr(over_zero_cnd+".colorIfFalseR", 0)
                        cmds.setAttr(over_zero_cnd+".operation", 3) #greater or equal
                        cmds.connectAttr(action_loc+".worldMatrix[0]", extract_angle_mm+".matrixIn[0]", force=True)
                        cmds.connectAttr(original_loc+".worldInverseMatrix[0]", extract_angle_mm+".matrixIn[1]", force=True)
                        cmds.connectAttr(extract_angle_mm+".matrixSum", extract_angle_dm+".inputMatrix", force=True)
                        # set general values and connections:
                        cmds.setAttr(output_sr+".oldMaxX", 1)
                        cmds.connectAttr(self.net+".inputStart", input_rmv+".inputMin", force=True)
                        cmds.connectAttr(self.net+".inputEnd", input_rmv+".inputMax", force=True)
                        cmds.connectAttr(self.net+".inputEnd", input_rmv+".outputMax", force=True)
                        cmds.connectAttr(self.net+".outputStart", output_sr+".minX", force=True)
                        cmds.connectAttr(self.net+".outputEnd", output_sr+".maxX", force=True)
                        cmds.connectAttr(interpolation_pma+".output1D", input_rmv+".value[0].value_Interp", force=True)
                        # setup the rotation affection
                        cmds.connectAttr(extract_angle_dm+".outputQuatX", extract_angle_qte+".inputQuatX", force=True)
                        cmds.connectAttr(extract_angle_dm+".outputQuatY", extract_angle_qte+".inputQuatY", force=True)
                        cmds.connectAttr(extract_angle_dm+".outputQuatZ", extract_angle_qte+".inputQuatZ", force=True)
                        cmds.connectAttr(extract_angle_dm+".outputQuatW", extract_angle_qte+".inputQuatW", force=True)
                        # axis setup
                        cmds.connectAttr(extract_angle_qte+".outputRotateX", angle_unit_convertion_md+".input1X", force=True)
                        cmds.connectAttr(extract_angle_qte+".outputRotateY", angle_unit_convertion_md+".input1Y", force=True)
                        cmds.connectAttr(extract_angle_qte+".outputRotateZ", angle_unit_convertion_md+".input1Z", force=True)
                        cmds.connectAttr(cmds.listConnections(angle_unit_convertion_md+".input1X", source=True, destination=False, plugs=True)[0], angle_axis_chc+".input[0]", force=True)
                        cmds.connectAttr(cmds.listConnections(angle_unit_convertion_md+".input1Y", source=True, destination=False, plugs=True)[0], angle_axis_chc+".input[1]", force=True)
                        cmds.connectAttr(cmds.listConnections(angle_unit_convertion_md+".input1Z", source=True, destination=False, plugs=True)[0], angle_axis_chc+".input[2]", force=True)
                        cmds.delete(angle_unit_convertion_md)
                        cmds.connectAttr(self.net+".axis", angle_axis_chc+".selector", force=True)
                        cmds.connectAttr(angle_axis_chc+".output", input_rmv+".inputValue", force=True)
                        cmds.connectAttr(input_rmv+".outValue", extract_angle_md+".input1X", force=True)
                        cmds.connectAttr(angle_axis_chc+".output", self.net+".inputValue", force=True)
                        cmds.setAttr(self.net+".inputValue", lock=True)
                        # axis order setup
                        cmds.connectAttr(self.net+".inputEnd", extract_angle_md+".input2X", force=True) #it'll be updated when changing angle
                        cmds.connectAttr(extract_angle_md+".outputX", smaller_than_one_cnd+".firstTerm", force=True)
                        cmds.connectAttr(extract_angle_md+".outputX", smaller_than_one_cnd+".colorIfTrueR", force=True)
                        cmds.connectAttr(smaller_than_one_cnd+".outColorR", over_zero_cnd+".firstTerm", force=True)
                        cmds.connectAttr(smaller_than_one_cnd+".outColorR", over_zero_cnd+".colorIfTrueR", force=True)
                        cmds.connectAttr(self.net+".axisOrder", extract_angle_dm+".inputRotateOrder", force=True)
                        cmds.connectAttr(self.net+".axisOrder", extract_angle_qte+".inputRotateOrder", force=True)
                        # corrective setup:
                        cmds.connectAttr(over_zero_cnd+".outColorR", corrective_md+".input1X", force=True)
                        cmds.connectAttr(corrective_md+".outputX", output_sr+".valueX", force=True)
                        # TODO create a way to avoid manual connection here, maybe using the UI new tab?
                        cmds.connectAttr(output_sr+".outValueX", self.net+".outputValue", force=True)
                        cmds.setAttr(self.net+".outputValue", lock=True)
                        # serialize angle nodes
                        cmds.connectAttr(extract_angle_mm+".message", self.net+".extractAngleMM", force=True)
                        cmds.connectAttr(extract_angle_dm+".message", self.net+".extractAngleDM", force=True)
                        cmds.connectAttr(extract_angle_qte+".message", self.net+".extractAngleQtE", force=True)
                        cmds.connectAttr(extract_angle_md+".message", self.net+".extractAngleMD", force=True)
                        cmds.connectAttr(angle_axis_chc+".message", self.net+".angleAxisChc", force=True)
                        cmds.connectAttr(smaller_than_one_cnd+".message", self.net+".smallerThanOneCnd", force=True)
                        cmds.connectAttr(over_zero_cnd+".message", self.net+".overZeroCnd", force=True)
                        cmds.connectAttr(input_rmv+".message", self.net+".inputRmV", force=True)
                        cmds.connectAttr(output_sr+".message", self.net+".outputSR", force=True)
                        
                    else: #Distance
                        distance_scale_md = cmds.createNode("multiplyDivide", name=correction_name+"_DistanceRigScale_MD")
                        output_rmv = cmds.createNode("remapValue", name=correction_name+"_Output_RmV")
                        dist_bet = cmds.createNode("distanceBetween", name=correction_name+"_Distance_DB")
                        distance_axis_extract_pma = cmds.createNode("plusMinusAverage", name=correction_name+"_DistanceAxisExtract_PMA")
                        distance_all_cnd = cmds.createNode("condition", name=correction_name+"_ExtractDistance_Cnd")
                        distance_axis_x_cnd = cmds.createNode("condition", name=correction_name+"_ExtractDistance_AxisX_Cnd")
                        distance_axis_yz_cnd = cmds.createNode("condition", name=correction_name+"_ExtractDistance_AxisYZ_Cnd")
                        self.to_ids.extend([distance_scale_md, output_rmv, dist_bet, distance_axis_extract_pma, distance_all_cnd, distance_axis_x_cnd, distance_axis_yz_cnd])
                        # connect locators source position values to extract distance from them
                        cmds.connectAttr(original_loc+".worldPosition.worldPositionX", dist_bet+".point1X")
                        cmds.connectAttr(original_loc+".worldPosition.worldPositionY", dist_bet+".point1Y")
                        cmds.connectAttr(original_loc+".worldPosition.worldPositionZ", dist_bet+".point1Z")
                        cmds.connectAttr(action_loc+".worldPosition.worldPositionX", dist_bet+".point2X")
                        cmds.connectAttr(action_loc+".worldPosition.worldPositionY", dist_bet+".point2Y")
                        cmds.connectAttr(action_loc+".worldPosition.worldPositionZ", dist_bet+".point2Z")
                        # setup distance input and output connections
                        cmds.connectAttr(output_rmv+".outValue", corrective_md+".input1X", force=True)
                        cmds.connectAttr(distance_scale_md+".message", self.net+".distanceScaleMD", force=True)
                        cmds.connectAttr(self.net+".inputRigScale", distance_scale_md+".input2X", force=True)
                        cmds.connectAttr(self.net+".inputRigScale", distance_scale_md+".input2Y", force=True)
                        cmds.connectAttr(self.net+".inputStart", distance_scale_md+".input1X", force=True)
                        cmds.connectAttr(distance_scale_md+".outputX", output_rmv+".inputMin", force=True)
                        cmds.connectAttr(self.net+".inputEnd", distance_scale_md+".input1Y", force=True)
                        cmds.connectAttr(distance_scale_md+".outputY", output_rmv+".inputMax", force=True)
                        cmds.connectAttr(self.net+".outputStart", output_rmv+".outputMin", force=True)
                        cmds.connectAttr(self.net+".outputEnd", output_rmv+".outputMax", force=True)
                        cmds.connectAttr(interpolation_pma+".output1D", output_rmv+".value[0].value_Interp", force=True)
                        # set default distance input values
                        cmds.setAttr(self.net+".inputStart", 10)
                        cmds.setAttr(self.net+".inputEnd", 0)
                        # TODO create a way to avoid manual connection here, maybe using the UI new tab?
                        cmds.connectAttr(corrective_md+".outputX", self.net+".outputValue", force=True)
                        cmds.setAttr(self.net+".outputValue", lock=True)
                        # extract axis by decomposing distance vector:
                        cmds.setAttr(distance_axis_extract_pma+".operation", 2) #Substract
                        cmds.setAttr(distance_axis_yz_cnd+".secondTerm", 1) #Y
                        cmds.connectAttr(original_loc+".worldPosition.worldPositionX", distance_axis_extract_pma+".input3D[0].input3Dx", force=True)
                        cmds.connectAttr(original_loc+".worldPosition.worldPositionY", distance_axis_extract_pma+".input3D[0].input3Dy", force=True)
                        cmds.connectAttr(original_loc+".worldPosition.worldPositionZ", distance_axis_extract_pma+".input3D[0].input3Dz", force=True)
                        cmds.connectAttr(action_loc+".worldPosition.worldPositionX", distance_axis_extract_pma+".input3D[1].input3Dx", force=True)
                        cmds.connectAttr(action_loc+".worldPosition.worldPositionY", distance_axis_extract_pma+".input3D[1].input3Dy", force=True)
                        cmds.connectAttr(action_loc+".worldPosition.worldPositionZ", distance_axis_extract_pma+".input3D[1].input3Dz", force=True)
                        cmds.connectAttr(self.net+".decompose", distance_all_cnd+".firstTerm", force=True)
                        cmds.connectAttr(self.net+".axis", distance_axis_x_cnd+".firstTerm", force=True)
                        cmds.connectAttr(self.net+".axis", distance_axis_yz_cnd+".firstTerm", force=True)
                        cmds.connectAttr(dist_bet+".distance", distance_all_cnd+".colorIfTrueR", force=True)
                        cmds.connectAttr(distance_axis_x_cnd+".outColorR", distance_all_cnd+".colorIfFalseR", force=True)
                        cmds.connectAttr(distance_axis_extract_pma+".output3Dx", distance_axis_x_cnd+".colorIfTrueR", force=True)
                        cmds.connectAttr(distance_axis_yz_cnd+".outColorR", distance_axis_x_cnd+".colorIfFalseR", force=True)
                        cmds.connectAttr(distance_axis_extract_pma+".output3Dy", distance_axis_yz_cnd+".colorIfTrueR", force=True)
                        cmds.connectAttr(distance_axis_extract_pma+".output3Dz", distance_axis_yz_cnd+".colorIfFalseR", force=True)
                        cmds.connectAttr(distance_all_cnd+".outColorR", output_rmv+".inputValue", force=True)
                        cmds.connectAttr(distance_all_cnd+".outColorR", self.net+".inputValue", force=True)
                        cmds.setAttr(self.net+".inputValue", lock=True)
                        # serialize distance nodes
                        cmds.connectAttr(dist_bet+".message", self.net+".distanceBet", force=True)
                        cmds.connectAttr(output_rmv+".message", self.net+".outputRmV", force=True)
                        cmds.connectAttr(distance_axis_extract_pma+".message", self.net+".distanceAxisExtractPMA", force=True)
                        cmds.connectAttr(distance_all_cnd+".message", self.net+".distanceAllCnd", force=True)
                        cmds.connectAttr(distance_axis_x_cnd+".message", self.net+".distanceAxisXCnd", force=True)
                        cmds.connectAttr(distance_axis_yz_cnd+".message", self.net+".distanceAxisYZCnd", force=True)
                    
                    self.ar.custom_attr.addAttr(0, self.to_ids) #dpID
                    self.ar.custom_attr.addAttr(0, [self.cm_data_grp], descendents=True) #dpID
                    # update UI                    
                    if self.ar.data.ui_state:
                        self.ar.correction_manager_ui.populate_net_ui()
                        self.ar.correction_manager_ui.update_edit_net_layout()
                    cmds.undoInfo(closeChunk=True)
                else:
                    mel.eval('warning \"'+self.ar.data.lang['m065_selOrigAction']+'\";')
            else:
                mel.eval('warning \"'+self.ar.data.lang['m066_selectTwo']+'\";')
        return self.net
