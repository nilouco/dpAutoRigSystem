# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:    
CLASS_NAME = "Suspension"
TITLE = "m153_suspension"
DESCRIPTION = "m154_suspensionDesc"
WIKI = "03-‐-Guides#-suspension"



class Suspension(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    
    
    
    def create_guide(self, *args):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.add_node_to_guide_net([self.cvALoc, self.cvBLoc], 
                                   ["JointLocA", "JointLocB"])


    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="flip", attributeType='bool')
        cmds.addAttr(self.guide_base, longName="fatherB", dataType='string')


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.cvALoc = self.ar.ctrls.cvJointLoc(ctrlName=self.name_guide+"_JointLocA", r=0.3, d=1, guide=True)
        self.cvBLoc = self.ar.ctrls.cvJointLoc(ctrlName=self.name_guide+"_JointLocB", r=0.3, d=1, guide=True)
        # joints
        self.jAGuide = cmds.joint(name=self.name_guide+"_jAGuide", radius=0.001)
        self.jBGuide = cmds.joint(name=self.name_guide+"_jBGuide", radius=0.001)
        # setup
        self.ar.utils.set_template([self.jAGuide, self.jBGuide])
        cmds.setAttr(self.cvBLoc+".tz", 3)
        cmds.setAttr(self.cvBLoc+".rotateX", 180)
        # parenting
        cmds.parent(self.jAGuide, self.cvALoc, self.guide_base, relative=True)
        cmds.parent(self.cvBLoc, self.cvALoc)
        # edit
        cmds.parentConstraint(self.cvALoc, self.jAGuide, maintainOffset=False, name=self.jAGuide+"_PaC")
        cmds.parentConstraint(self.cvBLoc, self.jBGuide, maintainOffset=False, name=self.jBGuide+"_PaC")
        cmds.scaleConstraint(self.cvALoc, self.jAGuide, maintainOffset=False, name=self.jAGuide+"_ScC")
        cmds.scaleConstraint(self.cvBLoc, self.jBGuide, maintainOffset=False, name=self.jBGuide+"_ScC")
        cmds.transformLimits(self.cvBLoc, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.setLockHide([self.cvBLoc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        
    
    def loadFatherB(self, *args):
        """ Loads the selected node to fatherBTextField in selectedModuleLayout.
        """
        selList = cmds.ls(selection=True)
        if selList:
            if cmds.objExists(selList[0]):
                cmds.textField('edit_guide_fatherb_tf', edit=True, text=selList[0])
                cmds.setAttr(self.guide_base+".fatherB", selList[0], type='string')
    
    
    def changeFatherB(self, *args):
        """ Update main fatherB attribute from UI textField.
        """
        newFatherBValue = cmds.textField('edit_guide_fatherb_tf', query=True, text=True)
        cmds.setAttr(self.guide_base+".fatherB", newFatherBValue, type='string')
    
    
    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            # declare lists to store names and attributes:
            self.suspensionBCtrlGrpList, self.fatherBList, self.ctrlHookGrpList = [], [], []
            # run for all sides
            for s, side in enumerate(self.sides):
                # declare guide:
                self.base = side+self.number_name+'_Guide_Base'
                self.cvALoc = side+self.number_name+"_Guide_JointLocA"
                self.cvBLoc = side+self.number_name+"_Guide_JointLocB"
                self.radiusGuide = side+self.number_name+"_Guide_Base_RadiusCtrl"
                self.locatorsGrp = cmds.group(name=side+self.number_name+"_Loc_Grp", empty=True)
                # calculate distance between guide and end:
                self.dist = self.ar.utils.distanceBet(self.cvALoc, self.cvBLoc)[0] * 0.2
                self.jointList, self.mainCtrlList, self.ctrlZeroList, self.controllers, self.aimLocList, self.upLocList = [], [], [], [], [], []
                for p, letter in enumerate(["A", "B"]):
                    # create joints:
                    cmds.select(clear=True)
                    jnt = cmds.joint(name=side+self.number_name+"_"+letter+"_1_Jnt", scaleCompensate=False)
                    endJoint = cmds.joint(name=side+self.number_name+"_"+letter+"_"+self.ar.data.joint_end_attr, scaleCompensate=False, radius=0.5)
                    self.ar.utils.addJointEndAttr([endJoint])
                    cmds.addAttr(jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    cmds.setAttr(endJoint+".translateZ", self.dist)
                    # joint labelling:
                    self.ar.utils.setJointLabel(jnt, s+self.joint_label_add, 18, self.number_name+"_"+letter)
                    self.jointList.append(jnt)
                    
                    # create a control:
                    mainCtrl = self.ar.ctrls.cvControl("id_055_SuspensionMain", side+self.number_name+"_"+self.ar.data.lang["c058_main"]+"_"+letter+"_Ctrl", r=self.radius, d=self.curve_degree, guideSource=self.name_guide+"_JointLoc"+letter)
                    ctrl = self.ar.ctrls.cvControl("id_056_SuspensionAB", side+self.number_name+"_"+letter+"_Ctrl", r=self.radius*0.5, d=self.curve_degree, guideSource=self.name_guide+"_JointLoc"+letter, parentTag=mainCtrl)
                    upLocCtrl = self.ar.ctrls.cvControl("id_057_SuspensionUpLoc", side+self.number_name+"_"+letter+"_UpLoc_Ctrl", r=self.radius*0.1, d=self.curve_degree, guideSource=self.name_guide+"_JointLoc"+letter, parentTag=ctrl)
                    self.ar.ctrls.setLockHide([ctrl], ['tx', 'ty', 'tz', 'v'])
                    self.ar.ctrls.setLockHide([upLocCtrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])
                    # position and orientation of joint and control:
                    cmds.parent(ctrl, upLocCtrl, mainCtrl)
                    cmds.parentConstraint(ctrl, jnt, maintainOffset=False, name=jnt+"_PaC")
                    cmds.scaleConstraint(ctrl, jnt, maintainOffset=False, name=jnt+"_ScC")
                    self.controllers.append(ctrl)
                    # zeroOut controls:
                    zeroOutCtrlGrp = self.ar.utils.zeroOut([mainCtrl, ctrl, upLocCtrl])
                    self.mainCtrlList.append(zeroOutCtrlGrp[0])
                    self.ctrlZeroList.append(zeroOutCtrlGrp[1])
                    cmds.setAttr(zeroOutCtrlGrp[2]+".translateX", self.dist)
                    # origined from data:
                    if p == 0:
                        self.ar.utils.originedFrom(objName=mainCtrl, attrString=self.base+";"+self.cvALoc+";"+self.radiusGuide)
                        cmds.delete(cmds.parentConstraint(self.cvALoc, zeroOutCtrlGrp[0], maintainOffset=False))
                    else:
                        self.ar.utils.originedFrom(objName=mainCtrl, attrString=self.cvBLoc)
                        cmds.delete(cmds.parentConstraint(self.cvBLoc, zeroOutCtrlGrp[0], maintainOffset=False))
                        # integrating data:
                        self.suspensionBCtrlGrpList.append(zeroOutCtrlGrp[0])
                    # hide visibility attribute:
                    cmds.setAttr(mainCtrl+'.visibility', keyable=False)
                    # fixing flip mirror:
                    if s == 1:
                        if cmds.getAttr(self.guide_base+".flip") == 1:
                            cmds.setAttr(zeroOutCtrlGrp[0]+".scaleX", -1)
                            cmds.setAttr(zeroOutCtrlGrp[0]+".scaleY", -1)
                            cmds.setAttr(zeroOutCtrlGrp[0]+".scaleZ", -1)
                    cmds.addAttr(ctrl, longName='scaleCompensate', attributeType="short", minValue=0, maxValue=1, defaultValue=1, keyable=False)
                    cmds.setAttr(ctrl+".scaleCompensate", channelBox=True)
                    cmds.connectAttr(ctrl+".scaleCompensate", jnt+".segmentScaleCompensate", force=True)
                    
                    # working with aim setup:
                    cmds.addAttr(ctrl, longName=self.ar.data.lang['c118_active'], attributeType="short", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                    aimLoc = cmds.spaceLocator(name=side+self.number_name+"_"+letter+"_Aim_Loc")[0]
                    upLoc = cmds.spaceLocator(name=side+self.number_name+"_"+letter+"_Up_Loc")[0]
                    locGrp = cmds.group(aimLoc, upLoc, name=side+self.number_name+"_"+letter+"_Loc_Grp")
                    cmds.parent(locGrp, self.locatorsGrp, relative=True)
                    cmds.delete(cmds.parentConstraint(ctrl, locGrp, maintainOffset=False))
                    cmds.parentConstraint(upLocCtrl, upLoc, maintainOffset=False, name=upLoc+"_PaC")
                    cmds.parentConstraint(mainCtrl, locGrp, maintainOffset=True, name=locGrp+"_PaC")
                    cmds.setAttr(locGrp+".visibility", 0)
                    self.aimLocList.append(aimLoc)
                    self.upLocList.append(upLoc)

                # aim constraints:
                # B to A:
                aAimConst = cmds.aimConstraint(self.aimLocList[1], self.ctrlZeroList[0], aimVector=(0, 0, 1), upVector=(1, 0, 0), worldUpType="object", worldUpObject=self.upLocList[0], maintainOffset=True, name=self.ctrlZeroList[0]+"_AiC")[0]
                cmds.connectAttr(self.controllers[0]+"."+self.ar.data.lang['c118_active'], aAimConst+"."+self.aimLocList[1]+"W0", force=True)
                # A to B:
                bAimConst = cmds.aimConstraint(self.aimLocList[0], self.ctrlZeroList[1], aimVector=(0, 0, 1), upVector=(1, 0, 0), worldUpType="object", worldUpObject=self.upLocList[1], maintainOffset=True, name=self.ctrlZeroList[1]+"_AiC")[0]
                cmds.connectAttr(self.controllers[1]+"."+self.ar.data.lang['c118_active'], bAimConst+"."+self.aimLocList[0]+"W0", force=True)
                
                # integrating data:
                self.loadedFatherB = cmds.getAttr(self.guide_base+".fatherB")
                if self.loadedFatherB:
                    self.fatherBList.append(self.loadedFatherB)
                else:
                    self.fatherBList.append(None)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.create_hook_setup(side, self.mainCtrlList, self.jointList, [self.locatorsGrp])
                self.ctrlHookGrpList.append(self.ctrl_hook_grp)
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.number_name+'_'+self.mirror_grp)
                self.ar.custom_attr.addAttr(0, [self.static_hook_grp], descendents=True) #dpID
            # finalize this rig:
            self.serialize_guide()
            self.composing_info()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and module_instance namespace:
        self.delete_guide()
        self.rename_unit_conversion()
    
    
    def composing_info(self):
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.composed = {
                            "suspensionBCtrlGrpList" : self.suspensionBCtrlGrpList,
                            "fatherBList"        : self.fatherBList,
                            "ctrlHookGrpList"    : self.ctrlHookGrpList,
                        }
