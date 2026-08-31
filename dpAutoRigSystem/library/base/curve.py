# importing libraries:
from maya import cmds
from maya import mel
from . import base
from importlib import reload


class BaseCurve(base.BaseLibrary):
    def __init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI):
        """ Initialize the curve module base class.
        """
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        self.cv_name = None
        self.cv_action = None
        self.cv_degree = None
        self.cv_size = None
        self.cv_direction = None
        self.cv_rot = None
        self.cv_points = None
        self.cv_knots = None
        self.cv_periodic = None
        self.cv_suffix = "Ctrl"
    
    
    def get_controller_ui_values(self, cv_name=''):
        """ Check and get all UI values to define variables.
            Return them in a list:
            [cv_name, cv_size, cv_degree, cv_direction, cv_action]
        """
        # here we will use all info from UI elements in order to call the correct action to do:
        custom_name = cmds.textFieldGrp("ctr_name_tfg", query=True, text=True)
        self.cv_name = cv_name
        if custom_name:
            self.cv_name = custom_name
        # action
        self.cv_action = cmds.radioButtonGrp("ctr_action_rgb", query=True, select=True)
        # degree
        degree_rgb_value = cmds.radioButtonGrp("ctr_degree_rgb", query=True, select=True)
        self.cv_degree = 1 #linear
        if degree_rgb_value == 2:
            self.cv_degree = 3 #cubic
        # size
        self.cv_size = cmds.floatSliderGrp("ctr_size_fsg", query=True, value=True)
        # direction
        self.cv_direction = cmds.optionMenuGrp("ctr_direction_omg", query=True, value=True)
        return [self.cv_name, self.cv_size, self.cv_degree, self.cv_direction, self.cv_action]
    
    
    def add_controller_info(self, item, class_name=True, size=True, degree=True, direction=True, rot=True, guide=False):
        """ Add some information in the curve transform node of the control.
        """
        cmds.addAttr(item, longName="dpControl", attributeType='bool')
        cmds.setAttr(item+".dpControl", 1)
        if guide:
            cmds.addAttr(item, longName="dpGuide", attributeType='bool')
            cmds.setAttr(item+".dpGuide", 1)
        cmds.addAttr(item, longName="version", dataType='string')
        cmds.setAttr(item+".version", self.ar.data.version, type="string")
        if self.cv_id:
            cmds.addAttr(item, longName="controlID", dataType='string')
            cmds.setAttr(item+".controlID", self.cv_id, type="string")
        if class_name:
            cmds.addAttr(item, longName="className", dataType='string')
            cmds.setAttr(item+".className", self.name, type="string")
        if size:
            cmds.addAttr(item, longName="size", attributeType='float')
            cmds.setAttr(item+".size", self.cv_size)
        if degree:
            cmds.addAttr(item, longName="degree", attributeType='short')
            cmds.setAttr(item+".degree", self.cv_degree)
        if direction:
            cmds.addAttr(item, longName="direction", dataType='string')
            cmds.setAttr(item+".direction", self.cv_direction, type="string")
        if rot:
            cmds.addAttr(item, longName="cvRotX", attributeType='double')
            cmds.addAttr(item, longName="cvRotY", attributeType='double')
            cmds.addAttr(item, longName="cvRotZ", attributeType='double')
            cmds.setAttr(item+".cvRotX", self.cv_rot[0])
            cmds.setAttr(item+".cvRotY", self.cv_rot[1])
            cmds.setAttr(item+".cvRotZ", self.cv_rot[2])
        if not guide:
            cmds.addAttr(item, longName="parentTag", attributeType='message')
    
    
    def create_curve(self, cv_name, cv_degree, cv_points, cv_knots, cv_periodic, guide):
        """ Create and return a simple curve using given parameters.
        """
        cv_curve = cmds.curve(name=cv_name, point=cv_points, degree=cv_degree, knot=cv_knots, periodic=cv_periodic)
        self.add_controller_info(cv_curve, guide=guide)
        self.ar.ctrls.rename_shape([cv_curve])
        self.ar.ctrls.display_rotate_order_attr([cv_curve])
        self.ar.custom_attr.add_attr(0, [cv_curve]) #dpID
        return cv_curve
    
    
    def combine_curves(self, curves):
        """ Combine all guiven curve to just one main curve and return it.
        """
        cmds.makeIdentity(curves[0], translate=True, rotate=True, scale=True, apply=True)
        for item in curves[1:]:
            cmds.makeIdentity(item, translate=True, rotate=True, scale=True, apply=True)
            self.ar.ctrls.transfer_shape(True, False, item, [curves[0]])
        cmds.setAttr(curves[0]+".className", self.name, type="string")
        return curves[0]

        
    
    def set_controller_direction(self, item, cv_direction):
        """ Rotate the node given to have the correct direction orientation.
        """
        if cv_direction == "-X":
            cmds.setAttr(item+".rotateX", 90)
            cmds.setAttr(item+".rotateY", -90)
        elif cv_direction == "+X":
            cmds.setAttr(item+".rotateX", -90)
            cmds.setAttr(item+".rotateY", -90)
        elif cv_direction == "-Y":
            cmds.setAttr(item+".rotateZ", 180)
        elif cv_direction == "-Z":
            cmds.setAttr(item+".rotateX", -90)
        elif cv_direction == "+Z":
            cmds.setAttr(item+".rotateX", 90)
        else:
            pass #default +Y, just pass
        cmds.makeIdentity(item, rotate=True, apply=True)
        # rotate and freezeTransformation from given cv_rot vector:
        cmds.rotate(self.cv_rot[0], self.cv_rot[1], self.cv_rot[2], self.cv_curve)
        cmds.makeIdentity(self.cv_curve, rotate=True, apply=True)
    
    
    def run_controller_action(self, destinations):
        """ Actions to do when creating a controller, user choice:
                1 = New control
                2 = Add shape
                3 = Replace shapes
        """
        if self.cv_action == 1: #new control
            pass
        else:
            if destinations:
                if self.cv_action == 2: #add shape
                    self.ar.ctrls.transfer_shape(True, False, self.cv_curve, destinations, True)
                elif self.cv_action == 3: #replace shapes
                    self.ar.ctrls.transfer_shape(True, True, self.cv_curve, destinations, True)
            else:
                cmds.delete(self.cv_curve)
                mel.eval("warning \""+self.ar.data.lang['e011_notSelShape']+"\";")
    
    
    def cv_create(self, use_ui, cv_id, cv_name='Controller_Ctrl', cv_size=1.0, cv_degree=1, cv_direction='+Y', cv_rot=(0, 0, 0), cv_action=1, guide=False, combine=False):
        """ Check if we need to get parameters from UI.
            Create a respective curve shape.
            Return the transform curve or a list of selected destination items.
        """
        # getting current selection:
        destinations = cmds.ls(selection=True, type="transform")
        # check if the given name is good or add a sequencial number on it:
        self.cv_name = self.ar.utils.validateName(cv_name, self.cv_suffix)
        self.cv_id = cv_id
        self.cv_size = cv_size
        self.cv_degree = cv_degree
        self.cv_direction = cv_direction
        self.cv_rot = cv_rot
        self.cv_action = cv_action
        # getting UI info:
        if use_ui and self.ar.data.ui_state:
            self.get_controller_ui_values(self.cv_name)
        
        # combine or create curve using the parameters:
        if combine:
            self.cv_curve = self.create_combined_curves(self.cv_id, self.cv_name, self.cv_size, self.cv_degree)
        else:
            # getting curve info to be created based on choose degree:
            if self.cv_degree == 1: #linear
                self.get_linear_points()
            else: #cubic
                self.get_cubic_points()
            self.cv_curve = self.create_curve(self.cv_name, self.cv_degree, self.cv_points, self.cv_knots, self.cv_periodic, guide)
        # set control direction for the control curve:
        self.set_controller_direction(self.cv_curve, self.cv_direction)
        
        # working about action to do, like new control, add shape or replace shapes:
        self.run_controller_action(destinations)
        # select the result node and return it
        if self.cv_action == 1: #new control
            cmds.select(self.cv_curve)
            return self.cv_curve
        elif destinations:
            cmds.select(destinations)
            return destinations
