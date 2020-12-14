# importing libraries:
import maya.cmds as cmds

from Library import dpUtils as utils
import dpBaseClass as Base
import dpLayoutClass as Layout

# global variables to this module:
CLASS_NAME = "Finger"
TITLE = "m007_finger"
DESCRIPTION = "m008_fingerDesc"
ICON = "/Icons/dp_finger.png"


class Finger(Base.StartClass, Layout.LayoutClass):
    def __init__(self, *args, **kwargs):
        # Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        Base.StartClass.__init__(self, *args, **kwargs)

    def createModuleLayout(self, *args):
        Base.StartClass.createModuleLayout(self)
        Layout.LayoutClass.basicModuleLayout(self)

    def createGuide(self, *args):
        Base.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="nJoints", attributeType='long')
        cmds.setAttr(self.moduleGrp+".nJoints", 1)

        cmds.setAttr(self.moduleGrp+".moduleNamespace", self.moduleGrp[:self.moduleGrp.rfind(":")], type='string')
        
        cmds.addAttr(self.moduleGrp, longName="articulation", attributeType='bool')
        cmds.setAttr(self.moduleGrp+".articulation", 1)

        self.cvJointLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLoc1", r=0.3, d=1, guide=True)
        self.jGuide1 = cmds.joint(name=self.guideName+"_JGuide1", radius=0.001)
        cmds.setAttr(self.jGuide1+".template", 1)
        cmds.parent(self.jGuide1, self.moduleGrp, relative=True)

        self.cvEndJoint = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.2, d=1, guide=True)
        cmds.parent(self.cvEndJoint, self.cvJointLoc)
        cmds.setAttr(self.cvEndJoint+".tz", 1.3)
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz'])

        cmds.parent(self.cvJointLoc, self.moduleGrp)
        cmds.parent(self.jGuideEnd, self.jGuide1)
        self.ctrls.directConnect(self.cvJointLoc, self.jGuide1, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])

        # change the number of phalanges to 3:
        self.changeJointNumber(3)

        # create a base cvLoc to start the finger joints:
        self.cvBaseJoint = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointLoc0", r=0.2, d=1, guide=True)
        cmds.setAttr(self.cvBaseJoint+".translateZ", -1)
        cmds.parent(self.cvBaseJoint, self.moduleGrp)

        # transform cvLocs in order to put as a good finger guide:
        cmds.setAttr(self.moduleGrp+".rotateX", 90)
        cmds.setAttr(self.moduleGrp+".rotateZ", 90)

    def changeJointNumber(self, enteredNJoints, *args):
        """ Edit the number of joints in the guide.
        """
        utils.useDefaultRenderLayer()
        # get the number of joints entered by user:
        if enteredNJoints == 0:
            try:
                self.enteredNJoints = cmds.intField(self.nJointsIF, query=True, value=True)
            except:
                return
        else:
            self.enteredNJoints = enteredNJoints
        # get the number of joints existing:
        self.currentNJoints = cmds.getAttr(self.moduleGrp+".nJoints")
        # start analisys the difference between values:
        if self.enteredNJoints != self.currentNJoints:
            # unparent temporarely the Ends:
            self.cvEndJoint = self.guideName+"_JointEnd"
            cmds.parent(self.cvEndJoint, world=True)
            self.jGuideEnd = (self.guideName+"_JGuideEnd")
            cmds.parent(self.jGuideEnd, world=True)
            # verify if the nJoints is greather or less than the current
            if self.enteredNJoints > self.currentNJoints:
                for n in range(self.currentNJoints+1, self.enteredNJoints+1):
                    # create another N cvJointLoc:
                    self.cvJointLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_JointLoc"+str(n), r=0.2, d=1, guide=True)
                    # set its nJoint value as n:
                    cmds.setAttr(self.cvJointLoc+".nJoint", n)
                    # parent it to the lastGuide:
                    cmds.parent(self.cvJointLoc, self.guideName+"_JointLoc"+str(n-1), relative=True)
                    cmds.setAttr(self.cvJointLoc+".translateZ", 1)
                    cmds.setAttr(self.cvJointLoc+".rotateY", -1)
                    # create a joint to use like an arrowLine:
                    self.jGuide = cmds.joint(name=self.guideName+"_JGuide"+str(n), radius=0.001)
                    cmds.setAttr(self.jGuide+".template", 1)
                    cmds.parent(self.jGuide, self.guideName+"_JGuide"+str(n-1))
                    self.ctrls.directConnect(self.cvJointLoc, self.jGuide, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
            elif self.enteredNJoints < self.currentNJoints:
                # re-define cvEndJoint:
                self.cvJointLoc = self.guideName+"_JointLoc"+str(self.enteredNJoints)
                self.cvEndJoint = self.guideName+"_JointEnd"
                self.jGuide = self.guideName+"_JGuide"+str(self.enteredNJoints)
                # re-parent the children guides:
                childrenGuideBellowList = utils.getGuideChildrenList(self.cvJointLoc)
                if childrenGuideBellowList:
                    for childGuide in childrenGuideBellowList:
                        cmds.parent(childGuide, self.cvJointLoc)
                # delete difference of nJoints:
                cmds.delete(self.guideName+"_JointLoc"+str(self.enteredNJoints+1))
                cmds.delete(self.guideName+"_JGuide"+str(self.enteredNJoints+1))
            # re-parent cvEndJoint:
            cmds.parent(self.cvEndJoint, self.cvJointLoc)
            cmds.setAttr(self.cvEndJoint+".tz", 1.3)
            cmds.parent(self.jGuideEnd, self.jGuide)
            # actualise the nJoints in the moduleGrp:
            cmds.setAttr(self.moduleGrp+".nJoints", self.enteredNJoints)
            self.currentNJoints = self.enteredNJoints
            # re-build the preview mirror:
            Layout.LayoutClass.createPreviewMirror(self)
        cmds.select(self.moduleGrp)

    def rigModule(self, *args):
        Base.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            try:
                hideJoints = cmds.checkBox('hideJointsCB', query=True, value=True)
            except:
                hideJoints = 1
            # articulation joint:
            self.addArticJoint = self.getArticulation()
            # declaring lists to send information for integration:
            self.scalableGrpList, self.ikCtrlZeroList = [], []
            # start as no having mirror:
            sideList = [""]
            # analisys the mirror module:
            self.mirrorAxis = cmds.getAttr(self.moduleGrp+".mirrorAxis")
            if self.mirrorAxis != 'off':
                # get rigs names:
                self.mirrorNames = cmds.getAttr(self.moduleGrp+".mirrorName")
                # get first and last letters to use as side initials (prefix):
                sideList = [self.mirrorNames[0]+'_', self.mirrorNames[len(self.mirrorNames)-1]+'_']
                for s, side in enumerate(sideList):
                    duplicated = cmds.duplicate(self.moduleGrp, name=side+self.userGuideName+'_Guide_Base')[0]
                    allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                    for item in allGuideList:
                        cmds.rename(item, side+self.userGuideName+"_"+item)
                    self.mirrorGrp = cmds.group(name="Guide_Base_Grp", empty=True)
                    cmds.parent(side+self.userGuideName+'_Guide_Base', self.mirrorGrp, absolute=True)
                    # re-rename grp:
                    cmds.rename(self.mirrorGrp, side+self.userGuideName+'_'+self.mirrorGrp)
                    # do a group mirror with negative scaling:
                    if s == 1:
                        for axis in self.mirrorAxis:
                            cmds.setAttr(side+self.userGuideName+'_'+self.mirrorGrp+'.scale'+axis, -1)
                # joint labelling:
                jointLabelAdd = 1
            else:  # if not mirror:
                duplicated = cmds.duplicate(self.moduleGrp, name=self.userGuideName+'_Guide_Base')[0]
                allGuideList = cmds.listRelatives(duplicated, allDescendents=True)
                for item in allGuideList:
                    cmds.rename(item, self.userGuideName+"_"+item)
                self.mirrorGrp = cmds.group(self.userGuideName+'_Guide_Base', name="Guide_Base_Grp", relative=True)
                # re-rename grp:
                cmds.rename(self.mirrorGrp, self.userGuideName+'_'+self.mirrorGrp)
                # joint labelling:
                jointLabelAdd = 0
            # store the number of this guide by module type
            dpAR_count = utils.findModuleLastNumber(CLASS_NAME, "dpAR_type")+1
            # run for all sides
            for s, side in enumerate(sideList):
                self.skinJointList = []
                self.base = side+self.userGuideName+'_Guide_Base'
                # get the number of joints to be created:
                self.nJoints = cmds.getAttr(self.base+".nJoints")
                for n in range(0, self.nJoints+1):
                    cmds.select(clear=True)
                    # declare guide:
                    self.guide = side+self.userGuideName+"_Guide_JointLoc"+str(n)
                    self.cvEndJoint = side+self.userGuideName+"_Guide_JointEnd"
                    self.radiusGuide = side+self.userGuideName+"_Guide_Base_RadiusCtrl"
                    # create a joint:
                    self.jnt = cmds.joint(name=side+self.userGuideName+"_%02d_Jnt"%(n), scaleCompensate=False)
                    self.skinJointList.append(self.jnt)
                    cmds.addAttr(self.jnt, longName='dpAR_joint', attributeType='float', keyable=False)
                    utils.setJointLabel(self.jnt, s+jointLabelAdd, 18, self.userGuideName+"_%02d"%(n))
                    # create a control:
                    if n == 1:
                        self.fingerCtrl = self.ctrls.cvControl("id_015_FingerMain", ctrlName=side+self.userGuideName+"_%02d_Ctrl"%(n), r=(self.ctrlRadius * 2.0), d=self.curveDegree, rot=(0, 0, -90))
                        cmds.setAttr(self.fingerCtrl+".rotateOrder", 1)
                        utils.originedFrom(objName=self.fingerCtrl, attrString=self.base+";"+self.guide)   
                        # edit the mirror shape to a good direction of controls:
                        if s == 1:
                            if self.mirrorAxis == 'X':
                                cmds.setAttr(self.fingerCtrl+'.rotateZ', 180)
                            elif self.mirrorAxis == 'Y':
                                cmds.setAttr(self.fingerCtrl+'.rotateY', 180)
                            elif self.mirrorAxis == 'Z':
                                cmds.setAttr(self.fingerCtrl+'.rotateZ', 180)
                            elif self.mirrorAxis == 'XY':
                                cmds.setAttr(self.fingerCtrl+'.rotateX', 180)
                            elif self.mirrorAxis == 'XYZ':
                                cmds.setAttr(self.fingerCtrl+'.rotateZ', 180)
                            cmds.makeIdentity(self.fingerCtrl, apply=True, translate=False, rotate=True, scale=False)
                    else:
                        self.fingerCtrl = self.ctrls.cvControl("id_016_FingerFk", ctrlName=side+self.userGuideName+"_%02d_Ctrl"%(n), r=self.ctrlRadius, d=self.curveDegree)
                        cmds.setAttr(self.fingerCtrl+".rotateOrder", 1)
                        if n == self.nJoints:
                            utils.originedFrom(objName=self.fingerCtrl, attrString=self.guide+";"+self.cvEndJoint+";"+self.radiusGuide)
                        else:
                            utils.originedFrom(objName=self.fingerCtrl, attrString=self.guide)
                        if n == 0:
                            if self.nJoints == 2:
                                # problably we are creating the first control to a thumb
                                cmds.scale(2, 2, 2, self.fingerCtrl, relative=True)
                                cmds.makeIdentity(self.fingerCtrl, apply=True)
                            else:
                                # problably we are creating other base controls
                                cmds.scale(2, 0.5, 1, self.fingerCtrl, relative=True)
                                cmds.makeIdentity(self.fingerCtrl, apply=True)

                    # scaleCompensate attribute:
                    #Not needed in Maya 2016 since we need to deactivate scale compensate on all finger bone
                    if (int(cmds.about(version=True)[:4]) < 2016):
                        if n > 0 or self.nJoints == 2:
                            cmds.addAttr(self.fingerCtrl, longName="scaleCompensate", attributeType='bool', keyable=True)
                            scaleCompensateCond = cmds.createNode("condition", name=side+self.userGuideName+"_%02d_ScaleCompensate_Cnd"%(n))
                            cmds.setAttr(scaleCompensateCond+".secondTerm", 1)
                            cmds.connectAttr(self.fingerCtrl+".scaleCompensate", scaleCompensateCond+".colorIfTrueR", force=True)
                            cmds.connectAttr(scaleCompensateCond+".outColorR", self.jnt+".segmentScaleCompensate", force=True)

                    # hide visibility attribute:
                    cmds.setAttr(self.fingerCtrl+'.visibility', keyable=False)
                    # put another group over the control in order to use this to connect values from mainFingerCtrl:
                    self.sdkGrp = cmds.group(self.fingerCtrl, name=side+self.userGuideName+"_%02d_SDK_Grp"%(n))
                    if n == 1:
                        # change pivot of this group to control pivot:
                        pivotPos = cmds.xform(self.fingerCtrl, query=True, worldSpace=True, rotatePivot=True)
                        cmds.setAttr(self.sdkGrp+'.rotatePivotX', pivotPos[0])
                        cmds.setAttr(self.sdkGrp+'.rotatePivotY', pivotPos[1])
                        cmds.setAttr(self.sdkGrp+'.rotatePivotZ', pivotPos[2])
                    # position and orientation of joint and control:
                    tempDel = cmds.parentConstraint(self.guide, self.jnt, maintainOffset=False)
                    cmds.delete(tempDel)
                    tempDel = cmds.parentConstraint(self.guide, self.sdkGrp, maintainOffset=False)
                    cmds.delete(tempDel)
                    # zeroOut controls:
                    self.zeroGrp = utils.zeroOut([self.sdkGrp])
                    
                    # grouping:
                    if n > 0:
                        if n == 1:
                            if not cmds.objExists(self.fingerCtrl+'.ikFkBlend'):
                                cmds.addAttr(self.fingerCtrl, longName="ikFkBlend", attributeType='float', keyable=True, minValue=0.0, maxValue=1.0, defaultValue=1.0)
                                self.ikFkRevNode = cmds.createNode("reverse", name=side+self.userGuideName+"_ikFk_Rev")
                                cmds.connectAttr(self.fingerCtrl+".ikFkBlend", self.ikFkRevNode+".inputX", force=True)
                            if not cmds.objExists(self.fingerCtrl+'.'+self.langDic[self.langName]['c021_showControls']):
                                cmds.addAttr(self.fingerCtrl, longName=self.langDic[self.langName]['c021_showControls'], attributeType='float', keyable=True, minValue=0.0, maxValue=1.0, defaultValue=1.0)
                                self.ctrlShape0 = cmds.listRelatives(side+self.userGuideName+"_00_Ctrl", children=True, type='nurbsCurve')[0]
                                cmds.connectAttr(self.fingerCtrl+"."+self.langDic[self.langName]['c021_showControls'], self.ctrlShape0+".visibility", force=True)
                                cmds.setAttr(self.fingerCtrl+'.'+self.langDic[self.langName]['c021_showControls'], keyable=False, channelBox=True)
                            for j in range(1, self.nJoints+1):
                                cmds.addAttr(self.fingerCtrl, longName=self.langDic[self.langName]['c022_phalange']+str(j), attributeType='float', keyable=True)
                        # parent joints as a simple chain (line)
                        self.fatherJnt = side+self.userGuideName+"_%02d_Jnt"%(n-1)
                        cmds.parent(self.jnt, self.fatherJnt, absolute=True)
                        # parent zeroGrp Group to the before ctrl:
                        self.fatherCtrl = side+self.userGuideName+"_%02d_Ctrl"%(n-1)
                        cmds.parent(self.zeroGrp, self.fatherCtrl, absolute=True)
                    # freeze joints rotation
                    cmds.makeIdentity(self.jnt, apply=True)
                    # create parent and scale constraints from ctrl to jnt:
                    cmds.delete(cmds.parentConstraint(self.fingerCtrl, self.jnt, maintainOffset=False, name=self.jnt+"_PaC"))
                    
                    # add articulationJoint:
                    if n > 0:
                        if self.addArticJoint:
                            artJntList = utils.articulationJoint(self.fatherJnt, self.jnt) #could call to create corrective joints. See parameters to implement it, please.
                            utils.setJointLabel(artJntList[0], s+jointLabelAdd, 18, self.userGuideName+"_%02d_Jar"%(n))
                    cmds.select(self.jnt)
                    
                    if n == self.nJoints:
                        # create end joint:
                        self.endJoint = cmds.joint(name=side+self.userGuideName+"_JEnd", radius=0.5)
                        cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJoint, maintainOffset=False))
                
                # make first phalange be leads from base finger control:
                cmds.parentConstraint(side+self.userGuideName+"_00_Ctrl", side+self.userGuideName+"_01_SDK_Zero_0_Grp", maintainOffset=True, name=side+self.userGuideName+"_01_SDK_Zero_0_Grp"+"_PaC")
                cmds.scaleConstraint(side+self.userGuideName+"_00_Ctrl", side+self.userGuideName+"_01_SDK_Zero_0_Grp", maintainOffset=True, name=side+self.userGuideName+"_01_SDK_Zero_0_Grp"+"_ScC")
                if self.nJoints != 2:
                    cmds.parentConstraint(side+self.userGuideName+"_00_Ctrl", side+self.userGuideName+"_00_Jnt", maintainOffset=True, name=side+self.userGuideName+"_PaC")
                    cmds.scaleConstraint(side+self.userGuideName+"_00_Ctrl", side+self.userGuideName+"_00_Jnt", maintainOffset=True, name=side+self.userGuideName+"_ScC")
                # connecting the attributes from control 1 to phalanges rotate:
                for n in range(1, self.nJoints+1):
                    self.fingerCtrl = side+self.userGuideName+"_01_Ctrl"
                    self.sdkGrp = side+self.userGuideName+"_%02d_SDK_Grp"%(n)
                    cmds.connectAttr(self.fingerCtrl+"."+self.langDic[self.langName]['c022_phalange']+str(n), self.sdkGrp+".rotateY", force=True)
                    if n > 1:
                        self.ctrlShape = cmds.listRelatives(side+self.userGuideName+"_%02d_Ctrl"%(n), children=True, type='nurbsCurve')[0]
                        cmds.connectAttr(self.fingerCtrl+"."+self.langDic[self.langName]['c021_showControls'], self.ctrlShape+".visibility", force=True)

                # ik and Fk setup
                if self.nJoints == 2:
                    dupIk = cmds.duplicate(self.skinJointList[0])[0]
                    dupFk = cmds.duplicate(self.skinJointList[0])[0]
                else:
                    dupIk = cmds.duplicate(self.skinJointList[1])[0]
                    dupFk = cmds.duplicate(self.skinJointList[1])[0]
                
                # hide ik and fk joints in order to be Rigger friendly while skinning
                cmds.setAttr(dupIk+".visibility", 0)
                cmds.setAttr(dupFk+".visibility", 0)
                
                # ik setup
                childrenIkList = cmds.listRelatives(dupIk, children=True, allDescendents=True, fullPath=True)
                if childrenIkList:
                    for child in childrenIkList:
                        if not cmds.objectType(child) == "joint":
                            cmds.delete(child)
                        if child.endswith("_Jar"):
                            cmds.delete(child)
                jointIkList = cmds.listRelatives(dupIk, children=True, allDescendents=True, fullPath=True)
                for jointNode in jointIkList:
                    if "_Jnt" in jointNode[jointNode.rfind("|"):]:
                        cmds.rename(jointNode, jointNode[jointNode.rfind("|")+1:].replace("_Jnt", "_Ik_Jxt"))
                    elif "_JEnd" in jointNode[jointNode.rfind("|"):]:
                        cmds.rename(jointNode, jointNode[jointNode.rfind("|")+1:].replace("_JEnd", "_Ik_JEnd"))
                ikBaseJoint = cmds.rename(dupIk, dupIk.replace("_Jnt1", "_Ik_Jxt"))
                ikJointList = cmds.listRelatives(ikBaseJoint, children=True, allDescendents=True)
                ikJointList.append(ikBaseJoint)

                # Fk setup
                childrenFkList = cmds.listRelatives(dupFk, children=True, allDescendents=True, fullPath=True)
                if childrenFkList:
                    for child in childrenFkList:
                        if not cmds.objectType(child) == "joint":
                            cmds.delete(child)
                        if child.endswith("_Jar"):
                            cmds.delete(child)
                jointFkList = cmds.listRelatives(dupFk, children=True, allDescendents=True, fullPath=True)
                for jointNode in jointFkList:
                    if "_Jnt" in jointNode[jointNode.rfind("|"):]:
                        cmds.rename(jointNode, jointNode[jointNode.rfind("|")+1:].replace("_Jnt", "_Fk_Jxt"))
                    elif "_JEnd" in jointNode[jointNode.rfind("|"):]:
                        cmds.rename(jointNode, jointNode[jointNode.rfind("|")+1:].replace("_JEnd", "_Fk_JEnd"))
                fkBaseJoint = cmds.rename(dupFk, dupFk.replace("_Jnt2", "_Fk_Jxt"))
                fkJointList = cmds.listRelatives(fkBaseJoint, children=True, allDescendents=True)
                fkJointList.append(fkBaseJoint)
                # ik fk blend connnections
                for i, ikJoint in enumerate(ikJointList):
                    if not "_JEnd" in ikJoint:
                        utils.clearDpArAttr([ikJoint])
                        fkJoint = ikJoint.replace("_Ik_Jxt", "_Fk_Jxt")
                        skinJoint = ikJoint.replace("_Ik_Jxt", "_Jnt")
                        self.fingerCtrl = side+self.userGuideName+"_01_Ctrl"
                        scaleCompensateCond = ikJoint.replace("_Ik_Jxt", "_ScaleCompensate_Cnd")
                        ikFkParentConst = cmds.parentConstraint(ikJoint, fkJoint, skinJoint, maintainOffset=True, name=skinJoint+"_PaC")[0]
                        ikFkScaleConst = cmds.scaleConstraint(ikJoint, fkJoint, skinJoint, maintainOffset=True, name=skinJoint+"_ScC")[0]
                        cmds.connectAttr(self.fingerCtrl+".ikFkBlend", ikFkParentConst+"."+fkJoint+"W1", force=True)
                        cmds.connectAttr(self.ikFkRevNode+".outputX", ikFkParentConst+"."+ikJoint+"W0", force=True)
                        cmds.connectAttr(self.fingerCtrl+".ikFkBlend", ikFkScaleConst+"."+fkJoint+"W1", force=True)
                        cmds.connectAttr(self.ikFkRevNode+".outputX", ikFkScaleConst+"."+ikJoint+"W0", force=True)
                        cmds.setAttr(ikJoint+".segmentScaleCompensate", 1)
                        #Condition for scale compensate will not exist in maya 2016 since we need to have the compensate
                        #off for almost every joint
                        if (int(cmds.about(version=True)[:4]) < 2016):
                            cmds.connectAttr(self.fingerCtrl+".ikFkBlend", scaleCompensateCond+".firstTerm", force=True)
                # fk control drives fk joints
                for i, fkJoint in enumerate(fkJointList):
                    if not "_JEnd" in fkJoint:
                        utils.clearDpArAttr([fkJoint])
                        fkCtrl = fkJoint.replace("_Fk_Jxt", "_Ctrl")
                        scaleCompensateCond = fkCtrl.replace("_Ctrl", "_ScaleCompensate_Cnd")
                        cmds.parentConstraint(fkCtrl, fkJoint, maintainOffset=True, name=fkJoint+"_PaC")
                        cmds.scaleConstraint(fkCtrl, fkJoint, maintainOffset=True, name=fkJoint+"_ScC")
                        #Not needed in Maya 2016 since we need to deactivate scale compensate on all finger bone
                        if (int(cmds.about(version=True)[:4]) < 2016):
                            cmds.connectAttr(fkCtrl+".scaleCompensate", fkJoint+".segmentScaleCompensate", force=True)
                        else:
                            cmds.setAttr(fkJoint+".segmentScaleCompensate", 0)
                        cmds.setAttr(fkCtrl+".rotateOrder", 1)

                #Force Scale compensate to prevent scale problem in Maya 2016
                for nJnt in self.skinJointList:
                    if (int(cmds.about(version=True)[:4]) >= 2016):
                        cmds.setAttr(nJnt+".segmentScaleCompensate", 0)
                
                # ik handle
                if self.nJoints >= 2:
                    if self.nJoints == 2:
                        ikHandleList = cmds.ikHandle(startJoint=side+self.userGuideName+"_00_Ik_Jxt", endEffector=side+self.userGuideName+"_%02d_Ik_Jxt"%(self.nJoints), solver="ikRPsolver", name=side+self.userGuideName+"_IKH")
                    else:
                        ikHandleList = cmds.ikHandle(startJoint=side+self.userGuideName+"_01_Ik_Jxt", endEffector=side+self.userGuideName+"_%02d_Ik_Jxt"%(self.nJoints), solver="ikRPsolver", name=side+self.userGuideName+"_IKH")
                    cmds.rename(ikHandleList[1], side+self.userGuideName+"_Eff")
                    endIkHandleList = cmds.ikHandle(startJoint=side+self.userGuideName+"_%02d_Ik_Jxt"%(self.nJoints), endEffector=side+self.userGuideName+"_Ik_JEnd", solver="ikSCsolver", name=side+self.userGuideName+"_EndIkHandle")
                    cmds.rename(endIkHandleList[1], side+self.userGuideName+"_End_Eff")
                    self.ikCtrl = self.ctrls.cvControl("id_017_FingerIk", ctrlName=side+self.userGuideName+"_Ik_Ctrl", r=(self.ctrlRadius * 0.3), d=self.curveDegree)
                    cmds.addAttr(self.ikCtrl, longName='twist', attributeType='float', keyable=True)
                    cmds.connectAttr(self.ikCtrl+".twist", ikHandleList[0]+".twist", force=True)
                    cmds.delete(cmds.parentConstraint(side+self.userGuideName+"_Ik_JEnd", self.ikCtrl))
                    cmds.setAttr(self.ikCtrl+".rotateOrder", 1)
                    self.ikCtrlZero = utils.zeroOut([self.ikCtrl])[0]
                    self.ikCtrlZeroList.append(self.ikCtrlZero)
                    cmds.connectAttr(self.ikFkRevNode+".outputX", self.ikCtrlZero+".visibility", force=True)
                    for q in range(2, self.nJoints+1):
                        cmds.connectAttr(side+self.userGuideName+"_01_Ctrl.ikFkBlend", side+self.userGuideName+"_%02d_Ctrl.visibility"%(q), force=True)
                    cmds.parentConstraint(self.ikCtrl, ikHandleList[0], name=side+self.userGuideName+"_IKH_PaC", maintainOffset=True)
                    cmds.parentConstraint(self.ikCtrl, endIkHandleList[0], name=side+self.userGuideName+"_EndIkHandle_PaC", maintainOffset=True)
                    ikHandleGrp = cmds.group(ikHandleList[0], endIkHandleList[0], name=side+self.userGuideName+"_IKH_Grp")
                    cmds.setAttr(ikHandleGrp+".visibility", 0)
                    self.ctrls.setLockHide([self.ikCtrl], ['sx', 'sy', 'sz', 'v'])

                    if self.nJoints == 2:
                        cmds.parentConstraint(side+self.userGuideName+"_00_Ctrl", side+self.userGuideName+"_00_Ik_Jxt", maintainOffset=True, name=side+self.userGuideName+"_00_Ik_Jxt_PaC")
                        cmds.scaleConstraint(side+self.userGuideName+"_00_Ctrl", side+self.userGuideName+"_00_Ik_Jxt", maintainOffset=True, name=side+self.userGuideName+"_00_Ik_Jxt_ScC")

                    # stretch
                    cmds.addAttr(self.ikCtrl, longName='stretchable', attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                    stretchNormMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_StretchNormalize_MD")
                    cmds.setAttr(stretchNormMD+".operation", 2)
                    distBetweenList = self.ctrls.distanceBet(side+self.userGuideName+"_00_Ctrl", self.ikCtrl, name=side+self.userGuideName+"_DistBet", keep=True)
                    cmds.connectAttr(self.ikFkRevNode+".outputX", distBetweenList[5]+"."+self.ikCtrl+"W0", force=True)
                    cmds.connectAttr(self.fingerCtrl+".ikFkBlend", distBetweenList[5]+"."+distBetweenList[4]+"W1", force=True)
                    cmds.connectAttr(distBetweenList[1]+".distance", stretchNormMD+".input1X", force=True)
                    cmds.setAttr(stretchNormMD+".input2X", distBetweenList[0])
                    stretchScaleMD = cmds.createNode("multiplyDivide", name=side+self.userGuideName+"_StretchScale_MD")
                    cmds.connectAttr(stretchNormMD+".outputX", stretchScaleMD+".input1X", force=True)
                    cmds.connectAttr(self.ikCtrl+".stretchable", stretchScaleMD+".input2X", force=True)
                    stretchCond = cmds.createNode("condition", name=side+self.userGuideName+"_Stretch_Cnd")
                    cmds.connectAttr(stretchScaleMD+".outputX", stretchCond+".firstTerm", force=True)
                    cmds.setAttr(stretchCond+".secondTerm", 1)
                    cmds.setAttr(stretchCond+".operation", 2)
                    cmds.connectAttr(stretchScaleMD+".outputX", stretchCond+".colorIfTrueR", force=True)
                    for i, ikJoint in enumerate(ikJointList):
                        if not "_JEnd" in ikJoint:
                            if self.nJoints == 2 and i == 0:
                                pass
                            else:
                                cmds.connectAttr(stretchCond+".outColorR", ikJoint+".scaleZ", force=True)

                    # create a masterModuleGrp to be checked if this rig exists:
                    self.toCtrlHookGrp = cmds.group(self.ikCtrlZero, side+self.userGuideName+"_00_SDK_Zero_0_Grp", side+self.userGuideName+"_01_SDK_Zero_0_Grp", name=side+self.userGuideName+"_Control_Grp")
                    if self.nJoints == 2:
                        self.toScalableHookGrp = cmds.group(self.skinJointList[0], ikBaseJoint, fkBaseJoint, ikHandleGrp, distBetweenList[2], distBetweenList[3], distBetweenList[4], name=side+self.userGuideName+"_Joint_Grp")
                    else:
                        self.toScalableHookGrp = cmds.group(self.skinJointList[0], ikHandleGrp, distBetweenList[2], distBetweenList[3], distBetweenList[4], name=side+self.userGuideName+"_Joint_Grp")
                else:
                    self.toCtrlHookGrp = cmds.group(side+self.userGuideName+"_00_SDK_Zero_0_Grp", side+self.userGuideName+"_01_SDK_Zero_0_Grp", name=side+self.userGuideName+"_Control_Grp")
                    self.toScalableHookGrp = cmds.group(side+self.userGuideName+"_00_Jnt", name=side+self.userGuideName+"_Joint_Grp")
                self.scalableGrpList.append(self.toScalableHookGrp)
                self.toStaticHookGrp = cmds.group(self.toCtrlHookGrp, self.toScalableHookGrp, name=side+self.userGuideName+"_Grp")
                # add hook attributes to be read when rigging integrated modules:
                utils.addHook(objName=self.toCtrlHookGrp, hookType='ctrlHook')
                utils.addHook(objName=self.toScalableHookGrp, hookType='scalableHook')
                utils.addHook(objName=self.toStaticHookGrp, hookType='staticHook')
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_name", dataType="string")
                cmds.addAttr(self.toStaticHookGrp, longName="dpAR_type", dataType="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_name", self.userGuideName, type="string")
                cmds.setAttr(self.toStaticHookGrp+".dpAR_type", CLASS_NAME, type="string")
                # add module type counter value
                cmds.addAttr(self.toStaticHookGrp, longName='dpAR_count', attributeType='long', keyable=False)
                cmds.setAttr(self.toStaticHookGrp+'.dpAR_count', dpAR_count)
                # create a locator in order to avoid delete static group
                loc = cmds.spaceLocator(name=side+self.userGuideName+"_DO_NOT_DELETE_PLEASE_Loc")[0]
                cmds.parent(loc, self.toStaticHookGrp, absolute=True)
                cmds.setAttr(loc+".visibility", 0)
                self.ctrls.setLockHide([loc], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
                if hideJoints:
                    cmds.setAttr(self.toScalableHookGrp+".visibility", 0)
                # delete duplicated group for side (mirror):
                cmds.delete(side+self.userGuideName+'_'+self.mirrorGrp)
            # finalize this rig:
            self.integratingInfo()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and moduleInstance namespace:
        self.deleteModule()

    def integratingInfo(self, *args):
        Base.StartClass.integratingInfo(self)
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.integratedActionsDic = {
            "module": {
                "scalableGrpList": self.scalableGrpList,
                "ikCtrlZeroList": self.ikCtrlZeroList,
            }
        }
