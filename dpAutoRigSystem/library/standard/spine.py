# importing libraries:
from maya import cmds
from ..base import standard

# global variables to this module:
CLASS_NAME = "Spine"
TITLE = "m011_spine"
DESCRIPTION = "m012_spineDesc"
WIKI = "03-‐-Guides#-spine"



class Spine(standard.BaseStandard):
    def __init__(self, ar):
        standard.BaseStandard.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        # declare variable
#        self.composed = {}
        self.guide_loc = None
        self.shapeSizeCH = None
        self.current_joint_number = 3
        # list of returned data:
        self.aHipsAList = []
        self.tipList = []
        self.aVolVariationAttrList = []
        self.aActVolVariationAttrList = []
        self.aMScaleVolVariationAttrList = []
        self.aIkFkBlendAttrList = []
        self.aInnerCtrls = []
        self.aOuterCtrls = []
        self.aRbnJointList = []
        self.aClusterGrp = []
        self.shapeVisAttrList = []
    

    def create_guide(self):
        self.create_guide_base()
        self.create_guide_custom_attr()
        self.create_guide_elements()
        self.change_joint_number(3)
        self.set_guide_base_initial_position()
        self.add_node_to_guide_net([self.guide_loc, self.guide_end_loc], 
                                   ["JointLoc1", "JointEnd"])


    def create_guide_custom_attr(self):
        """ Add guide_base attributes and set them.
        """
        cmds.addAttr(self.guide_base, longName="nJoints", attributeType='long', defaultValue=1)
        cmds.addAttr(self.guide_base, longName="style", attributeType='enum', enumName=self.ar.data.lang['m042_default']+':'+self.ar.data.lang['m026_biped']+":"+self.ar.data.lang['m037_quadruped'])


    def create_guide_elements(self):
        """ Creates the controller locators of the standard module guide.
        """
        # locators
        self.guide_loc = self.ar.ctrls.cvJointLoc(ctrlName=self.name_guide+"_JointLoc1", r=0.5, d=1, guide=True)
        self.guide_end_loc = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_JointEnd", r=0.1, d=1, guide=True)
        # joints
        self.line = cmds.joint(name=self.name_guide+"_JGuide1", radius=0.001)
        # setup
        cmds.setAttr(self.line+".template", 1)
        cmds.setAttr(self.guide_end_loc+".tz", 1.3)
        # parenting
        cmds.parent(self.line, self.guide_loc, self.guide_base)
        cmds.parent(self.guide_end_loc, self.guide_loc)
        # edit
        cmds.parentConstraint(self.guide_loc, self.line, maintainOffset=False, name=self.line+"_PaC")
        cmds.transformLimits(self.guide_end_loc, tz=(0.01, 1), etz=(True, False))
        self.ar.ctrls.setLockHide([self.guide_end_loc], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])


    def set_guide_base_initial_position(self):
        cmds.setAttr(self.guide_base+".rx", -90)
        cmds.setAttr(self.guide_base+".ry", -90)
        cmds.setAttr(self.radius_ctrl+".tx", 4)

        
        
    def change_joint_number(self, inputted, *args):
        """ Edit the number of joints in the guide.
        """
        joint_number = self.parse_inputted_joint_number(inputted)
        if joint_number and joint_number >= 3:
            self.ar.opt.check_use_default_render_layer()
            self.current_joint_number = cmds.getAttr(self.guide_base+".nJoints")
            if joint_number != self.current_joint_number:
                self.guide_end_loc = self.name_guide+"_JointEnd"
                if self.current_joint_number > 1:
                    # delete current point constraints:
                    for n in range(2, self.current_joint_number):
                        cmds.delete(self.name_guide+"_PaC"+str(n))
                # verify if the nJoints is greather or less than the current
                if joint_number > self.current_joint_number:
                    # add the new cvLocators:
                    for n in range(self.current_joint_number+1, joint_number+1):
                        # create another N cvLocator:
                        self.cvLocator = self.ar.ctrls.cvLocator(ctrlName=self.name_guide+"_JointLoc"+str(n), r=0.3, d=1, guide=True)
                        self.line = cmds.joint(name=self.name_guide+"_JGuide"+str(n), radius=0.001)
                        # set its nJoint value as n:
                        cmds.setAttr(self.line+".template", 1)
                        cmds.setAttr(self.cvLocator+".nJoint", n)
                        # parent its group to the first cvJointLocator:
                        self.cvLocGrp = cmds.group(self.cvLocator, name=self.cvLocator+"_Grp")
                        cmds.parent(self.cvLocGrp, self.name_guide+"_JointLoc"+str(n-1), relative=True)
                        cmds.parent(self.line, self.name_guide+"_JGuide"+str(n-1), relative=True)
                        cmds.setAttr(self.cvLocGrp+".translateZ", 2)
                        cmds.parentConstraint(self.cvLocator, self.line, maintainOffset=False, name=self.line+"_PaC")
                        if n > 2:
                            cmds.parent(self.cvLocGrp, self.name_guide+"_JointLoc1", absolute=True)
                        self.add_node_to_guide_net([self.cvLocator], ["JointLoc"+str(n)])
                elif joint_number < self.current_joint_number:
                    # re-parent cvEndJoint:
                    self.cvLocator = self.name_guide+"_JointLoc" + str(joint_number)
                    cmds.parent(self.guide_end_loc, world=True)
                    # delete difference of nJoints:
                    for n in range(joint_number, self.current_joint_number):
                        # re-parent the children guides:
                        childrenGuideBellowList = self.ar.utils.getGuideChildrenList(self.name_guide+"_JointLoc"+str(n+1)+"_Grp")
                        if childrenGuideBellowList:
                            for childGuide in childrenGuideBellowList:
                                cmds.parent(childGuide, self.cvLocator)
                        cmds.delete(self.name_guide+"_JointLoc"+str(n+1)+"_Grp")
                        self.remove_attr_from_guide_net(["JointLoc"+str(n+1)])
                    cmds.delete(self.name_guide+"_JGuide"+str(joint_number+1))
                # re-parent cvEndJoint:
                cmds.parent(self.guide_end_loc, self.cvLocator)
                cmds.setAttr(self.guide_end_loc+".tz", 1.3)
                cmds.setAttr(self.guide_end_loc+".visibility", 0)
                # re-create parentConstraints:
                if joint_number > 1:
                    for n in range(2, joint_number):
                        self.parentConst = cmds.parentConstraint(self.name_guide+"_JointLoc1", self.guide_end_loc, self.name_guide+"_JointLoc"+str(n)+"_Grp", name=self.name_guide+"_PaC"+str(n), maintainOffset=True)[0]
                        nParentValue = (n-1) / float(joint_number-1)
                        cmds.setAttr(self.parentConst+".Guide_JointLoc1W0", 1-nParentValue)
                        cmds.setAttr(self.parentConst+".Guide_JointEndW1", nParentValue)
                        self.ar.ctrls.setLockHide([self.name_guide+"_JointLoc"+ str(n)], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
                # actualise the nJoints in the main:
                cmds.setAttr(self.guide_base+".nJoints", joint_number)
                self.current_joint_number = joint_number
                # re-create the preview mirror:
                self.create_mirror_preview()
            cmds.select(self.guide_base)
        else:
            self.change_joint_number(3)


    def rig_me(self, *args):
        standard.BaseStandard.rig_me(self)
        # verify if the guide exists:
        if cmds.objExists(self.guide_base):
            style = cmds.getAttr(self.guide_base+".style")
            # naming main controls:
            hipsName  = self.ar.data.lang['c100_bottom']
            chestName = self.ar.data.lang['c099_top']
            baseName = self.ar.data.lang['c106_base']
            endName = self.ar.data.lang['c120_tip']
            if style == 1: #biped
                hipsName  = self.ar.data.lang['c027_hips']
                chestName = self.ar.data.lang['c028_chest']
            # run for all sides
            for s, side in enumerate(self.sides):
                attr_name_lower = self.ar.utils.getAttrNameLower(side, self.number_name)
                self.base = side+self.number_name+'_Guide_Base'
                self.guide_radius = side+self.number_name+"_Guide_Base_RadiusCtrl"
                # get the number of joints to be created:
                self.n_joints = cmds.getAttr(self.base+".nJoints")
                # create controls:
                self.hipsACtrl = self.ar.ctrls.cvControl("id_041_SpineHipsA", ctrlName=side+self.number_name+"_"+hipsName+"A_Ctrl", r=self.radius, d=self.curve_degree, guideSource=self.name_guide+"_JointLoc1")
                self.chestACtrl = self.ar.ctrls.cvControl("id_044_SpineChestA", ctrlName=side+self.number_name+"_"+chestName+"A_Ctrl", r=self.radius, d=self.curve_degree, guideSource=self.name_guide+"_JointLoc"+str(self.n_joints))
                # create start and end Fk controls:
                self.hipsFkCtrl = self.ar.ctrls.cvControl("id_067_SpineFk", ctrlName=side+self.number_name+"_"+hipsName+"A_Fk_Ctrl", r=self.radius, d=self.curve_degree, dir="+Z", guideSource=self.name_guide+"_JointLoc1")
                self.chestFkCtrl = self.ar.ctrls.cvControl("id_067_SpineFk", ctrlName=side+self.number_name+"_"+chestName+"A_Fk_Ctrl", r=self.radius, d=self.curve_degree, dir="+Z", guideSource=self.name_guide+"_JointLoc"+str(self.n_joints))
                # optimize controls CV shapes:
                tempHipsACluster = cmds.cluster(self.hipsACtrl)[1]
                cmds.setAttr(tempHipsACluster+".scaleY", 0.25)
                cmds.delete(self.hipsACtrl, constructionHistory=True)
                tempChestACluster = cmds.cluster(self.chestACtrl)[1]
                cmds.setAttr(tempChestACluster+".scaleY", 0.4)
                cmds.delete(self.chestACtrl, constructionHistory=True)
                hipsFkCtrlCVPos = -0.4*self.radius
                if style == 1: #biped
                    hipsFkCtrlCVPos = 0.4*self.radius
                cmds.move(0, hipsFkCtrlCVPos, 0, self.hipsFkCtrl+"0Shape.cv[0:5]", relative=True, worldSpace=True, worldSpaceDistance=True)
                
                self.hipsBCtrl = self.ar.ctrls.cvControl("id_042_SpineHipsB", side+self.number_name+"_"+hipsName+"B_Ctrl", r=self.radius, d=self.curve_degree, dir="+X", guideSource=self.name_guide+"_Base")
                self.chestBCtrl = self.ar.ctrls.cvControl("id_045_SpineChestB", side+self.number_name+"_"+chestName+"B_Ctrl", r=self.radius, d=self.curve_degree, dir="+X", guideSource=self.name_guide+"_JointLoc"+str(self.n_joints))
                cmds.addAttr(self.hipsACtrl, longName=attr_name_lower+'_'+self.ar.data.lang['c031_volumeVariation'], attributeType="float", defaultValue=1, keyable=True)
                cmds.addAttr(self.hipsACtrl, longName=attr_name_lower+'Active_'+self.ar.data.lang['c031_volumeVariation'], attributeType="float", defaultValue=1, keyable=True)
                cmds.addAttr(self.hipsACtrl, longName=attr_name_lower+'_masterScale_'+self.ar.data.lang['c031_volumeVariation'], attributeType="float", defaultValue=1, keyable=True)
                cmds.addAttr(self.hipsACtrl, longName=attr_name_lower+'Fk_ikFkBlend', attributeType="float", min=0, max=1, defaultValue=1, keyable=True)
                self.aHipsAList.append(self.hipsACtrl)
                self.aVolVariationAttrList.append(attr_name_lower+'_'+self.ar.data.lang['c031_volumeVariation'])
                self.aActVolVariationAttrList.append(attr_name_lower+'Active_'+self.ar.data.lang['c031_volumeVariation'])
                self.aMScaleVolVariationAttrList.append(attr_name_lower+'_masterScale_'+self.ar.data.lang['c031_volumeVariation'])
                self.aIkFkBlendAttrList.append(attr_name_lower+'Fk_ikFkBlend')
                
                # base and end controls:
                self.baseCtrl = self.ar.ctrls.cvControl("id_089_SpineBase", side+self.number_name+"_"+baseName+"_Ctrl", r=0.75*self.radius, d=self.curve_degree, dir="+X", guideSource=self.name_guide+"_JointLoc1")
                self.tipCtrl = self.ar.ctrls.cvControl("id_090_SpineTip", side+self.number_name+"_"+endName+"_Ctrl", r=0.75*self.radius, d=self.curve_degree, dir="+X", guideSource=self.name_guide+"_JointLoc"+str(self.n_joints))
                self.tipList.append(self.tipCtrl)
                # optimize control CV shapes:
                tempBaseCluster = cmds.cluster(self.baseCtrl)[1]
                tempTipCluster = cmds.cluster(self.tipCtrl)[1]
                if style == 0: #default
                    cmds.setAttr(tempBaseCluster+".translateY", 0.2*self.radius)
                    cmds.setAttr(tempTipCluster+".translateY", -0.2*self.radius)
                else:
                    cmds.setAttr(tempBaseCluster+".translateY", -0.2*self.radius)
                    cmds.setAttr(tempTipCluster+".translateY", 0.2*self.radius)
                cmds.delete([self.baseCtrl, self.tipCtrl], constructionHistory=True)
                # shape visibility
                cmds.addAttr(self.hipsACtrl, longName=attr_name_lower+endName+self.ar.data.lang['c126_display'], attributeType="long", minValue=0, maxValue=1, defaultValue=0, keyable=True)
                cmds.addAttr(self.hipsACtrl, longName=attr_name_lower+baseName+self.ar.data.lang['c126_display'], attributeType="long", minValue=0, maxValue=1, defaultValue=0, keyable=True)
                cmds.connectAttr(self.hipsACtrl+"."+attr_name_lower+endName+self.ar.data.lang['c126_display'], cmds.listRelatives(self.tipCtrl, children=True, type="shape")[0]+".visibility", force=True)
                cmds.connectAttr(self.hipsACtrl+"."+attr_name_lower+baseName+self.ar.data.lang['c126_display'], cmds.listRelatives(self.baseCtrl, children=True, type="shape")[0]+".visibility", force=True)
                self.shapeVisAttrList.append(attr_name_lower+endName+self.ar.data.lang['c126_display'])
                self.shapeVisAttrList.append(attr_name_lower+baseName+self.ar.data.lang['c126_display'])

                # Setup axis order
                if style == 2: #quadruped
                    cmds.setAttr(self.hipsACtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.hipsBCtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.chestACtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.chestBCtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.hipsFkCtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.chestFkCtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.baseCtrl + ".rotateOrder", 1)
                    cmds.setAttr(self.tipCtrl + ".rotateOrder", 1)
                    cmds.rotate(90, 0, 0, self.hipsACtrl, self.hipsBCtrl, self.chestACtrl, self.chestBCtrl, self.hipsFkCtrl, self.chestFkCtrl, self.baseCtrl, self.tipCtrl)
                    cmds.makeIdentity(self.hipsACtrl, self.hipsBCtrl, self.chestACtrl, self.chestBCtrl, self.hipsFkCtrl, self.chestFkCtrl, self.baseCtrl, self.tipCtrl, apply=True, rotate=True)
                else:
                    cmds.setAttr(self.hipsACtrl + ".rotateOrder", 3)
                    cmds.setAttr(self.hipsBCtrl + ".rotateOrder", 3)
                    cmds.setAttr(self.chestACtrl + ".rotateOrder", 3)
                    cmds.setAttr(self.chestBCtrl + ".rotateOrder", 3)
                    cmds.setAttr(self.hipsFkCtrl + ".rotateOrder", 3)
                    cmds.setAttr(self.chestFkCtrl + ".rotateOrder", 3)
                    cmds.setAttr(self.baseCtrl + ".rotateOrder", 3)
                    cmds.setAttr(self.tipCtrl + ".rotateOrder", 3)
                
                # Keep a list of ctrls we want to colorize a certain way
                self.aInnerCtrls.append([self.hipsBCtrl, self.chestBCtrl])
                self.aOuterCtrls.append([self.hipsACtrl, self.chestACtrl, self.hipsFkCtrl, self.chestFkCtrl])
                
                # organize hierarchy:
                cmds.parent(self.hipsBCtrl, self.hipsACtrl)
                cmds.parent(self.chestBCtrl, self.chestACtrl)
                cmds.parent(self.hipsFkCtrl, self.hipsACtrl)
                cmds.parent(self.chestFkCtrl, self.chestACtrl)
                cmds.parent(self.baseCtrl, self.hipsBCtrl, relative=True)
                cmds.parent(self.tipCtrl, self.chestBCtrl, relative=True)
                if style == 0: #default
                    cmds.rotate(-90, 0, 0, self.hipsACtrl, self.chestACtrl)
                    cmds.makeIdentity(self.hipsACtrl, self.chestACtrl, apply=True, rotate=True)
                # position of controls:
                bottomLocGuide = side+self.number_name+"_Guide_JointLoc1"
                topLocGuide = side+self.number_name+"_Guide_JointLoc"+str(self.n_joints)
                # snap controls to guideLocators:
                cmds.delete(cmds.parentConstraint(bottomLocGuide, self.hipsACtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(topLocGuide, self.chestACtrl, maintainOffset=False))
                
                # change axis orientation for biped style
                if style == 1: #biped
                    cmds.rotate(0, 0, 0, self.hipsACtrl, self.chestACtrl)
                    cmds.makeIdentity(self.hipsACtrl, self.chestACtrl, apply=True, rotate=True)
                cmds.parent(self.chestACtrl, self.hipsACtrl)
                
                # zeroOut transformations:
                self.hipsACtrlZero, self.chestAZero, self.chestBGrp, self.hipsFkCtrlZero, self.chestFkCtrlZero = self.ar.utils.zeroOut([self.hipsACtrl, self.chestACtrl, self.chestBCtrl, self.hipsFkCtrl, self.chestFkCtrl])
                self.chestBGrp = cmds.rename(self.chestBGrp, self.chestBGrp.replace("Zero", "Grp"))
                self.chestBZero = self.ar.utils.zeroOut([self.chestBGrp])[0]
                self.baseCtrlZero = self.ar.utils.zeroOut([self.baseCtrl])[0]
                self.tipCtrlZero = self.ar.utils.zeroOut([self.tipCtrl])[0]
                self.ar.ctrls.setLockHide([self.hipsACtrl, self.hipsBCtrl, self.chestACtrl, self.chestBCtrl, self.hipsFkCtrl, self.chestFkCtrl], ['v'], l=False)
                # modify the pivots of chest controls:
                upPivotPos = cmds.xform(side+self.number_name+"_Guide_JointLoc"+str(self.n_joints-1), query=True, worldSpace=True, translation=True)
                cmds.move(upPivotPos[0], upPivotPos[1], upPivotPos[2], self.chestACtrl+".scalePivot", self.chestACtrl+".rotatePivot")
                
                # add originedFrom attributes to hipsA, hipsB and chestB:
                self.ar.utils.originedFrom(objName=self.hipsACtrl, attrString=self.base+";"+self.guide_radius)
                self.ar.utils.originedFrom(objName=self.baseCtrl, attrString=bottomLocGuide)
                self.ar.utils.originedFrom(objName=self.tipCtrl, attrString=topLocGuide)

                # create base and end joints:
                cmds.select(clear=True)
                baseJnt = cmds.joint(name=side+self.number_name+"_00_"+self.ar.data.lang['c106_base']+"_Jnt", scaleCompensate=False)
                cmds.addAttr(baseJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                cmds.select(clear=True)
                tipJnt = cmds.joint(name=side+self.number_name+"_"+str(self.n_joints+1).zfill(2)+"_"+self.ar.data.lang['c120_tip']+"_Jnt", scaleCompensate=False)
                cmds.addAttr(tipJnt, longName='dpAR_joint', attributeType='float', keyable=False)
                # joint labelling:
                self.ar.utils.setJointLabel(baseJnt, s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['c106_base'])
                self.ar.utils.setJointLabel(tipJnt, s+self.joint_label_add, 18, self.number_name+"_"+self.ar.data.lang['c120_tip'])
                # Base and end controllers:
                cmds.parentConstraint(self.baseCtrl, baseJnt, maintainOffset=False, name=baseJnt+"_PaC")
                cmds.scaleConstraint(self.baseCtrl, baseJnt, maintainOffset=True, name=baseJnt+"_ScC")
                cmds.parentConstraint(self.tipCtrl, tipJnt, maintainOffset=False, name=tipJnt+"_PaC")
                cmds.scaleConstraint(self.tipCtrl, tipJnt, maintainOffset=True, name=tipJnt+"_ScC")

                # create a simple spine ribbon:
                returnedRibbonList = self.ar.ctrls.createSimpleRibbon(name=side+self.number_name, totalJoints=(self.n_joints-1), jointLabelNumber=(s+self.joint_label_add), jointLabelName=self.number_name)
                rbnNurbsPlane = returnedRibbonList[0]
                rbnNurbsPlaneShape = returnedRibbonList[1]
                rbnJointGrpList = returnedRibbonList[2]
                self.aRbnJointList = returnedRibbonList[3]
                # position of ribbon nurbs plane:
                cmds.setAttr(rbnNurbsPlane+".tz", -4)
                cmds.move(0, 0, 0, rbnNurbsPlane+".scalePivot", rbnNurbsPlane+".rotatePivot")
                cmds.rotate(90, 90, 0, rbnNurbsPlane)
                cmds.makeIdentity(rbnNurbsPlane, apply=True, translate=True, rotate=True)
                downLocPos = cmds.xform(side+self.number_name+"_Guide_JointLoc1", query=True, worldSpace=True, translation=True)
                upLocPos = cmds.xform(side+self.number_name+"_Guide_JointLoc"+str(self.n_joints), query=True, worldSpace=True, translation=True)
                cmds.move(downLocPos[0], downLocPos[1], downLocPos[2], rbnNurbsPlane)
                # create up and down clusters:
                downClusterList = cmds.cluster(rbnNurbsPlane+".cv[0:3][0:1]", name=side+self.number_name+'_Down_Cls')
                upClusterList = cmds.cluster(rbnNurbsPlane+".cv[0:3]["+str(self.n_joints)+":"+str(self.n_joints+1)+"]", name=side+self.number_name+'_Up_Cls')
                downCluster = downClusterList[1]
                upCluster = upClusterList[1]
                self.to_ids.extend([downClusterList[0], upClusterList[0]])
                # get positions of joints from ribbon nurbs plane:
                startRbnJointPos = cmds.xform(side+self.number_name+"_01_Jnt", query=True, worldSpace=True, translation=True)
                endRbnJointPos = cmds.xform(side+self.number_name+"_%02d_Jnt"%(self.n_joints), query=True, worldSpace=True, translation=True)
                # move pivots of clusters to start and end positions:
                cmds.move(startRbnJointPos[0], startRbnJointPos[1], startRbnJointPos[2], downCluster+".scalePivot", downCluster+".rotatePivot")
                cmds.move(endRbnJointPos[0], endRbnJointPos[1], endRbnJointPos[2], upCluster+".scalePivot", upCluster+".rotatePivot")
                # snap clusters to guideLocators:
                tempDel = cmds.parentConstraint(bottomLocGuide, downCluster, maintainOffset=False)
                cmds.delete(tempDel)
                tempDel = cmds.parentConstraint(topLocGuide, upCluster, maintainOffset=False)
                cmds.delete(tempDel)
                # rotate clusters to compensate guide:
                upClusterRot = cmds.xform(upCluster, query=True, worldSpace=True, rotation=True)
                downClusterRot = cmds.xform(downCluster, query=True, worldSpace=True, rotation=True)
                cmds.xform(upCluster, worldSpace=True, rotation=(upClusterRot[0]+90, upClusterRot[1], upClusterRot[2]))
                cmds.xform(downCluster, worldSpace=True, rotation=(downClusterRot[0]+90, downClusterRot[1], downClusterRot[2]))
                # scaleY of the clusters in order to avoid great extremity deforms:
                rbnHeight = self.ar.utils.distanceBet(side+self.number_name+"_Guide_JointLoc"+str(self.n_joints), side+self.number_name+"_Guide_JointLoc1", keep=False)[0]
                cmds.setAttr(upCluster+".sy", rbnHeight / 10)
                cmds.setAttr(downCluster+".sy", rbnHeight / 10)
                # parent clusters in controls (up and down):
                cmds.parentConstraint(self.hipsBCtrl, downCluster, maintainOffset=True, name=downCluster+"_PaC")
                cmds.parentConstraint(self.chestBCtrl, upCluster, maintainOffset=True, name=upCluster+"_PaC")
                # organize a group of clusters:
                spineClustersGrp = cmds.group(name=side+self.number_name+"_Clusters_Grp", empty=True)
                cmds.parent(downCluster, upCluster, spineClustersGrp, relative=True)
                # make ribbon joints groups scalable:
                middleScaleYMD = cmds.createNode("multiplyDivide", name=side+self.number_name+"_MiddleScaleY_MD")
                cmds.setAttr(middleScaleYMD+".operation", 2)
                cmds.setAttr(middleScaleYMD+".input1X", 1)
                sizeCtrlList = [self.hipsBCtrl]
                sizeGrpList = []
                for r, rbnJntGrp in enumerate(rbnJointGrpList):
                    sizeGrpList.append(cmds.group(rbnJntGrp, name=rbnJntGrp.replace("_Grp", "_Size_Grp")))
                    scaleGrp = cmds.group(sizeGrpList[-1], name=rbnJntGrp.replace("_Grp", "_Scale_Grp"))
                    cmds.scaleConstraint(spineClustersGrp, scaleGrp, maintainOffset=True, name=scaleGrp+"_ScC")
                    if ((r > 0) and (r < (len(rbnJointGrpList) - 1))):
                        self.ar.utils.addCustomAttr([scaleGrp], self.ar.utils.ignoreTransformIOAttr)
                        self.ar.ctrls.directConnect(scaleGrp, rbnJntGrp, ['sx', 'sy', 'sz'])
                        cmds.connectAttr(middleScaleYMD+".outputX", self.aRbnJointList[r]+".scaleY", force=True)
                        cmds.connectAttr(scaleGrp+".scaleY", middleScaleYMD+".input2X", force=True)
                        sizeCtrlList.append(side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(r)+"_Ctrl")
                sizeCtrlList.append(self.chestBCtrl)
                # calculate the distance to volumeVariation:
                arcLenShape = cmds.createNode('arcLengthDimension', name=side+self.number_name+"_Rbn_ArcLenShape")
                arcLenFather = cmds.listRelatives(arcLenShape, parent=True)[0]
                arcLen = cmds.rename(arcLenFather, side+self.number_name+"_Rbn_ArcLen")
                arcLenShape = cmds.listRelatives(arcLen, children=True, shapes=True)[0]
                cmds.setAttr(arcLen+'.visibility', 0)
                # connect nurbsPlaneShape to arcLength node:
                cmds.connectAttr(rbnNurbsPlaneShape+'.worldSpace[0]', arcLenShape+'.nurbsGeometry')
                cmds.setAttr(arcLenShape+'.vParamValue', 1)
                # avoid undesired squash if rotateZ the nurbsPlane:
                cmds.setAttr(arcLenShape+'.uParamValue', 0.5)
                arcLenValue = cmds.getAttr(arcLenShape+'.arcLengthInV')
                # create a multiplyDivide to output the squashStretch values:
                rbnMD = cmds.createNode('multiplyDivide', name=side+self.number_name+"_Rbn_MD")
                cmds.connectAttr(arcLenShape+'.arcLengthInV', rbnMD+'.input2X')
                cmds.setAttr(rbnMD+'.input1X', arcLenValue)
                cmds.setAttr(rbnMD+'.operation', 2)
                # create a blendColor, a condition and a multiplyDivide in order to get the correct result value of volumeVariation:
                rbnBlendColors = cmds.createNode('blendColors', name=side+self.number_name+"_Rbn_BC")
                cmds.connectAttr(self.hipsACtrl+'.'+attr_name_lower+'_'+self.ar.data.lang['c031_volumeVariation'], rbnBlendColors+'.blender')
                rbnCond = cmds.createNode('condition', name=side+self.number_name+'_Rbn_Cond')
                cmds.connectAttr(self.hipsACtrl+'.'+attr_name_lower+'Active_'+self.ar.data.lang['c031_volumeVariation'], rbnCond+'.firstTerm')
                cmds.connectAttr(rbnBlendColors+'.outputR', rbnCond+'.colorIfTrueR')
                cmds.connectAttr(rbnMD+'.outputX', rbnBlendColors+'.color1R')
                rbnVVMD = cmds.createNode('multiplyDivide', name=side+self.number_name+"_Rbn_VV_MD")
                cmds.connectAttr(self.hipsACtrl+'.'+attr_name_lower+'_masterScale_'+self.ar.data.lang['c031_volumeVariation'], rbnVVMD+'.input2X')
                cmds.connectAttr(rbnVVMD+'.outputX', rbnCond+'.colorIfFalseR')
                cmds.setAttr(rbnVVMD+'.operation', 2)
                cmds.setAttr(rbnBlendColors+'.color2R', 1)
                cmds.setAttr(rbnCond+".secondTerm", 1)
                # middle ribbon setup:
                for n in range(1, self.n_joints - 1):
                    if style == 0: #default
                        self.middleCtrl = self.ar.ctrls.cvControl("id_043_SpineMiddle", side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n)+"_Ctrl", r=self.radius, d=self.curve_degree, guideSource=self.name_guide+"_JointLoc"+str(n+1))
                        self.middleFkCtrl = self.ar.ctrls.cvControl("id_067_SpineFk", side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n)+"_Fk_Ctrl", r=self.radius, d=self.curve_degree, guideSource=self.name_guide+"_JointLoc"+str(n+1))
                        cmds.setAttr(self.middleCtrl+".rotateOrder", 4)
                        cmds.setAttr(self.middleFkCtrl+".rotateOrder", 4)
                        cmds.rotate(0, 0, 90, self.middleCtrl, self.middleFkCtrl)
                        cmds.makeIdentity(self.middleCtrl, self.middleFkCtrl, apply=True, rotate=True)
                    else: #biped or quadruped
                        self.middleCtrl = self.ar.ctrls.cvControl("id_043_SpineMiddle", side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n)+"_Ctrl", r=self.radius, d=self.curve_degree, dir="+X", guideSource=self.name_guide+"_JointLoc"+str(n+1))
                        self.middleFkCtrl = self.ar.ctrls.cvControl("id_067_SpineFk", side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n)+"_Fk_Ctrl", r=self.radius, d=self.curve_degree, dir="+X", guideSource=self.name_guide+"_JointLoc"+str(n+1))
                        cmds.setAttr(self.middleCtrl+".rotateOrder", 3)
                        cmds.setAttr(self.middleFkCtrl+".rotateOrder", 3)
                    self.aInnerCtrls[s].append(self.middleCtrl)
                    self.aOuterCtrls[s].append(self.middleFkCtrl)
                    self.ar.ctrls.setLockHide([self.middleCtrl, self.middleFkCtrl], ['sx', 'sy', 'sz'])
                    cmds.setAttr(self.middleCtrl+'.visibility', keyable=False)
                    cmds.setAttr(self.middleFkCtrl+'.visibility', keyable=False)
                    cmds.parent(self.middleCtrl, self.hipsACtrl)
                    middleLocGuide = side+self.number_name+"_Guide_JointLoc"+str(n + 1)
                    cmds.delete(cmds.parentConstraint(middleLocGuide, self.middleCtrl, maintainOffset=False))
                    cmds.delete(cmds.parentConstraint(middleLocGuide, self.middleFkCtrl, maintainOffset=False))
                    if style == 1: #biped
                        cmds.rotate(0, 0, 0, self.middleCtrl, self.middleFkCtrl)
                    elif style == 2: #quadruped
                        cmds.rotate(90, 0, 0, self.middleCtrl, self.middleFkCtrl)
                        cmds.makeIdentity(self.middleCtrl, self.middleFkCtrl, apply=True, rotate=True)
                    self.middleCtrlGrp = self.ar.utils.zeroOut([self.middleCtrl])[0]
                    self.middleCtrlGrp = cmds.rename(self.middleCtrlGrp, self.middleCtrlGrp.replace("Zero", "Grp"))
                    self.middleCtrlZero = self.ar.utils.zeroOut([self.middleCtrlGrp])[0]
                    self.middleFkCtrlZero = self.ar.utils.zeroOut([self.middleFkCtrl])[0]
                    middleClusterList = cmds.cluster(rbnNurbsPlane+".cv[0:3]["+str(n+1)+"]", name=side+self.number_name+'_Middle_Cls')
                    middleCluster = middleClusterList[1]
                    self.to_ids.append(middleClusterList[0])
                    middleLocPos = cmds.xform(side+self.number_name+"_Guide_JointLoc"+str(n), query=True, worldSpace=True, translation=True)
                    tempDel = cmds.parentConstraint(middleLocGuide, middleCluster, maintainOffset=False)
                    cmds.delete(tempDel)
                    middleClusterRot = cmds.xform(middleCluster, query=True, worldSpace=True, rotation=True)
                    cmds.xform(middleCluster, worldSpace=True, rotation=(middleClusterRot[0]+90, middleClusterRot[1], middleClusterRot[2]))
                    cmds.parentConstraint(self.middleCtrl, middleCluster, maintainOffset=True, name=middleCluster+"_PaC")
                    # parenting constraints like guide locators:
                    self.parentConst = cmds.parentConstraint(self.hipsBCtrl, self.chestBCtrl, self.middleCtrlZero, name=self.middleCtrl+"_PaC", maintainOffset=True)[0]
                    nParentValue = (n) / float(self.n_joints-1)
                    cmds.setAttr(self.parentConst+"."+self.hipsBCtrl+"W0", 1-nParentValue)
                    cmds.setAttr(self.parentConst+"."+self.chestBCtrl+"W1", nParentValue)
                    cmds.parent(middleCluster, spineClustersGrp, relative=True)
                    # add originedFrom attribute to this middle ctrl:
                    middleOrigGrp = cmds.group(empty=True, name=side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n)+"_OrigFrom_Grp")
                    self.ar.utils.originedFrom(objName=middleOrigGrp, attrString=middleLocGuide)
                    cmds.parentConstraint(self.aRbnJointList[n], middleOrigGrp, maintainOffset=False, name=middleOrigGrp+"_PaC")
                    cmds.parent(middleOrigGrp, self.hipsACtrl)
                    # apply volumeVariation to joints in the middle ribbon setup:
                    cmds.connectAttr(rbnCond+'.outColorR', self.aRbnJointList[n]+'.scaleX')
                    cmds.connectAttr(rbnCond+'.outColorR', self.aRbnJointList[n]+'.scaleZ')
                    # create intensity attribute to drive joint with more force in horizontal:
                    cmds.addAttr(self.middleCtrl, longName=self.ar.data.lang['c049_intensity'], attributeType="float", min=0, max=1, defaultValue=0, keyable=True)
                    cmds.addAttr(self.middleFkCtrl, longName=self.ar.data.lang['c049_intensity'], attributeType="float", min=0, max=1, defaultValue=0, keyable=True)
                    jointFather = cmds.listRelatives(self.aRbnJointList[n], allParents=True)[0]
                    intRevNode = cmds.createNode("reverse", name=side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n)+"_"+self.ar.data.lang['c049_intensity'].capitalize()+"_Rev")
                    middleIntBC = cmds.createNode("blendColors", name=side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n)+"_"+self.ar.data.lang['c049_intensity'].capitalize()+"_BC")
                    self.to_ids.extend([intRevNode, middleIntBC])
                    middleIntPC = cmds.parentConstraint(self.middleCtrl, jointFather, self.aRbnJointList[n], maintainOffset=True, name=self.aRbnJointList[n]+"_"+self.ar.data.lang['c049_intensity'].capitalize()+"_PaC")[0]
                    cmds.connectAttr(self.middleFkCtrl+"."+self.ar.data.lang['c049_intensity'], middleIntBC+".color1R", force=True)
                    cmds.connectAttr(self.middleCtrl+"."+self.ar.data.lang['c049_intensity'], middleIntBC+".color2R", force=True)
                    cmds.connectAttr(self.hipsACtrl+'.'+attr_name_lower+'Fk_ikFkBlend', middleIntBC+".blender", force=True)
                    cmds.connectAttr(middleIntBC+".outputR", middleIntPC+"."+self.middleCtrl+"W0", force=True)
                    cmds.connectAttr(self.middleCtrl+"."+self.ar.data.lang['c049_intensity'], intRevNode+".inputX", force=True)
                    cmds.connectAttr(intRevNode+".outputX", middleIntPC+"."+jointFather+"W1", force=True)
                    # fk middle control hierarchy:
                    if n == 1: #first middle
                        cmds.parent(self.middleFkCtrlZero, self.hipsFkCtrl)
                    else:
                        cmds.parent(self.middleFkCtrlZero, side+self.number_name+"_"+self.ar.data.lang['c029_middle']+str(n-1)+"_Fk_Ctrl")
                    # build fk setup:
                    self.middleCtrlGrpPC = cmds.parentConstraint(self.middleCtrlZero, self.middleFkCtrl, self.middleCtrlGrp, maintainOffset=True, name=self.middleCtrlGrp+"_IkFkBlend_PaC")[0]
                    if n == 1:
                        self.revNode = cmds.createNode('reverse', name=side+self.number_name+"_IkFkBlend_Rev")
                        self.to_ids.append(self.revNode)
                        cmds.connectAttr(self.hipsACtrl+'.'+attr_name_lower+'Fk_ikFkBlend', self.revNode+".inputX", force=True)
                    # connecting ikFkBlend using the reverse node:
                    cmds.connectAttr(self.hipsACtrl+'.'+attr_name_lower+'Fk_ikFkBlend', self.middleCtrlGrpPC+"."+self.middleFkCtrl+"W1", force=True)
                    cmds.connectAttr(self.revNode+'.outputX', self.middleCtrlGrpPC+"."+self.middleCtrlZero+"W0", force=True)
                    # ikFkBlend visibility:
                    cmds.connectAttr(self.revNode+'.outputX', self.middleCtrlZero+".visibility", force=True)
                
                # finishing ikFkBlend:
                chestACtrlShape = cmds.listRelatives(self.chestACtrl, children=True, type="shape")[0]
                chestBCtrlShape = cmds.listRelatives(self.chestBCtrl, children=True, type="shape")[0]
                cmds.parent(self.chestFkCtrlZero, self.middleFkCtrl)
                self.chestCtrlGrpPC = cmds.parentConstraint(self.chestBZero, self.chestFkCtrl, self.chestBGrp, maintainOffset=True, name=self.chestBGrp+"_IkFkBlend_PaC")[0]
                cmds.connectAttr(self.hipsACtrl+'.'+attr_name_lower+'Fk_ikFkBlend', self.chestCtrlGrpPC+"."+self.chestFkCtrl+"W1", force=True)
                cmds.connectAttr(self.revNode+'.outputX', self.chestCtrlGrpPC+"."+self.chestBZero+"W0", force=True)
                cmds.connectAttr(self.revNode+'.outputX', chestACtrlShape+".visibility", force=True)
                cmds.connectAttr(self.revNode+'.outputX', chestBCtrlShape+".visibility", force=True)
                cmds.connectAttr(self.hipsACtrl+'.'+attr_name_lower+'Fk_ikFkBlend', self.hipsFkCtrlZero+".visibility", force=True)
                cmds.connectAttr(self.hipsACtrl+'.'+attr_name_lower+'Fk_ikFkBlend', self.chestFkCtrlZero+".visibility", force=True)
                
                # parent tag
                self.addParentTagInfo()

                # adding size feature:
                for a, b in zip(sizeCtrlList, sizeGrpList):
                    self.connectSizeAxis(a, b)

                # update spine volume variation setup
                currentVV = cmds.getAttr(rbnMD+'.outputX')
                cmds.setAttr(rbnVVMD+'.input1X', currentVV)
                # organize groups:
                self.create_hook_setup(side, [self.hipsACtrlZero], [spineClustersGrp], [side+self.number_name+"_Rbn_RibbonJoint_Grp", arcLen, baseJnt, tipJnt])
                self.aClusterGrp.append(self.scalable_hook_grp)
                # lockHide scale of up and down controls:
                self.ar.ctrls.setLockHide([self.hipsACtrl, self.hipsBCtrl, self.chestACtrl, self.chestBCtrl, self.hipsFkCtrl, self.chestFkCtrl], ['sx', 'sy', 'sz'])
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.number_name+'_'+self.mirror_grp)
                self.ar.utils.addCustomAttr([middleOrigGrp], self.ar.utils.ignoreTransformIOAttr)
                self.to_ids.extend([middleScaleYMD, arcLen, rbnMD, rbnBlendColors, rbnCond, rbnVVMD])
                self.ar.custom_attr.addAttr(0, [self.static_hook_grp], descendents=True) #dpID
            # finalize this rig:
            self.serialize_guide()
            self.composing_info()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and module_instance namespace:
        self.delete_guide()
        self.rename_unit_conversion()
        self.ar.custom_attr.addAttr(0, self.to_ids) #dpID


    def addParentTagInfo(self, *args):
        """ Set the parentTag connections for existing controllers.
        """
        for i in range(2, len(self.aInnerCtrls[0])-1):
            cmds.connectAttr(self.aInnerCtrls[0][i+1]+".message", self.aInnerCtrls[0][i]+".parentTag", force=True) #middles
        for j in range(4, len(self.aOuterCtrls[0])-1):
            cmds.connectAttr(self.aOuterCtrls[0][j+1]+".message", self.aOuterCtrls[0][j]+".parentTag", force=True) #fks
        cmds.connectAttr(self.aInnerCtrls[0][2]+".message", self.hipsBCtrl+".parentTag", force=True)
        cmds.connectAttr(self.hipsBCtrl+".message", self.hipsACtrl+".parentTag", force=True)
        cmds.connectAttr(self.hipsBCtrl+".message", self.baseCtrl+".parentTag", force=True)
        cmds.connectAttr(self.aOuterCtrls[0][4]+".message", self.hipsFkCtrl+".parentTag", force=True)
        cmds.connectAttr(self.chestFkCtrl+".message", self.aOuterCtrls[0][-1]+".parentTag", force=True)
        cmds.connectAttr(self.chestBCtrl+".message", self.aInnerCtrls[0][-1]+".parentTag", force=True)
        cmds.connectAttr(self.tipCtrl+".message", self.chestFkCtrl+".parentTag", force=True)
        cmds.connectAttr(self.chestBCtrl+".message", self.tipCtrl+".parentTag", force=True)
        cmds.connectAttr(self.chestACtrl+".message", self.chestBCtrl+".parentTag", force=True)


    def connectSizeAxis(self, fromNode, toNode, *args):
        """ Just connect sizeXYZ to scaleXYZ of given nodes.
        """
        for axis in self.ar.data.axes:
            if not cmds.objExists(fromNode+".size"+axis):
                cmds.addAttr(fromNode, longName="size"+axis, attributeType="float", defaultValue=1, keyable=True)
            cmds.connectAttr(fromNode+".size"+axis, toNode+".scale"+axis, force=True)


    def composing_info(self):
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.composed = {
                            "hipsAList": self.aHipsAList,
                            "tipList": self.tipList,
                            "volumeVariationAttrList": self.aVolVariationAttrList,
                            "ActiveVolumeVariationAttrList": self.aActVolVariationAttrList,
                            "MasterScaleVolumeVariationAttrList": self.aMScaleVolVariationAttrList,
                            "IkFkBlendAttrList": self.aIkFkBlendAttrList,
                            "InnerCtrls": self.aInnerCtrls,
                            "OuterCtrls": self.aOuterCtrls,
                            "jointList": self.aRbnJointList,
                            "scalableGrp": self.aClusterGrp,
                            "shapeVisAttrList": self.shapeVisAttrList
                        }
