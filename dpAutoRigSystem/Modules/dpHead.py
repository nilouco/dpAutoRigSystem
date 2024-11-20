# importing libraries:
from maya import cmds
from . import dpBaseClass
from . import dpLayoutClass
from ..Extras import dpFacialConnection
from ..Extras import dpHeadDeformer

# global variables to this module:    
CLASS_NAME = "Head"
TITLE = "m017_head"
DESCRIPTION = "m018_headDesc"
ICON = "/Icons/dp_head.png"

DP_HEAD_VERSION = 3.0


class Head(dpBaseClass.StartClass, dpLayoutClass.LayoutClass):
    def __init__(self,  *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.facialAttrList = ["facialBrow", "facialEyelid", "facialMouth", "facialLips", "facialSneer", "facialGrimace", "facialFace"]
        dpBaseClass.StartClass.__init__(self, *args, **kwargs)
        # declare variables
        self.correctiveCtrlGrpList = []
        self.aInnerCtrls = []
        self.redeclareVariables(self.guideName)
        self.facialFactor = 0.15
        self.dpFacialConnect = dpFacialConnection.FacialConnection(self.dpUIinst, ui=False)
        self.dpHeadDeformer = dpHeadDeformer.HeadDeformer(self.dpUIinst, ui=False)

    
    def createModuleLayout(self, *args):
        dpBaseClass.StartClass.createModuleLayout(self)
        dpLayoutClass.LayoutClass.basicModuleLayout(self)
    
    
    def createGuide(self, *args):
        dpBaseClass.StartClass.createGuide(self)
        # Custom GUIDE:
        cmds.addAttr(self.moduleGrp, longName="nJoints", attributeType='long')
        cmds.setAttr(self.moduleGrp+".nJoints", 1)
        cmds.addAttr(self.moduleGrp, longName="flip", attributeType='bool')
        cmds.addAttr(self.moduleGrp, longName="articulation", attributeType='bool')
        cmds.addAttr(self.moduleGrp, longName="corrective", attributeType='bool')
        cmds.addAttr(self.moduleGrp, longName="deformer", attributeType='bool')
        cmds.addAttr(self.moduleGrp, longName="facial", attributeType='bool')
        for attr in self.facialAttrList:
            cmds.addAttr(self.moduleGrp, longName=attr, attributeType='bool')
            cmds.setAttr(self.moduleGrp+"."+attr, 1)
        cmds.addAttr(self.moduleGrp, longName="connectUserType", attributeType='long', defaultValue=0) #bs

        # create cvJointLoc and cvLocators:
        self.cvNeckLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_Neck0", r=0.5, d=1, rot=(-90, 90, 0), guide=True)
        self.cvHeadLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_Head", r=0.4, d=1, guide=True)
        self.cvJawLoc  = self.ctrls.cvLocator(ctrlName=self.guideName+"_Jaw", r=0.3, d=1, guide=True)
        self.cvChinLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_Chin", r=0.3, d=1, guide=True)
        self.cvChewLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_Chew", r=0.3, d=1, guide=True)
        self.cvLCornerLipLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_LCornerLip", r=0.1, d=1, guide=True)
        self.cvRCornerLipLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_RCornerLip", r=0.1, d=1, guide=True)
        self.cvUpperJawLoc  = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_UpperJaw", r=0.2, d=1, rot=(0, 0, 90), guide=True)
        self.cvUpperHeadLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_UpperHead", r=0.2, d=1, rot=(0, 0, 90), guide=True)
        self.cvUpperLipLoc  = self.ctrls.cvLocator(ctrlName=self.guideName+"_UpperLip", r=0.15, d=1, guide=True)
        self.cvLowerLipLoc  = self.ctrls.cvLocator(ctrlName=self.guideName+"_LowerLip", r=0.15, d=1, guide=True)
        self.cvBrowLoc    = self.ctrls.cvLocator(ctrlName=self.guideName+"_Brow", r=0.2, d=1, guide=True, color="cyan", cvType=self.ctrls.getControlModuleById("id_046_FacialBrow"))
        self.cvEyelidLoc  = self.ctrls.cvLocator(ctrlName=self.guideName+"_Eyelid", r=0.2, d=1, guide=True, rot=(0, 0, 90), color="cyan", cvType=self.ctrls.getControlModuleById("id_047_FacialEyelid"))
        self.cvMouthLoc   = self.ctrls.cvLocator(ctrlName=self.guideName+"_Mouth", r=0.2, d=1, guide=True, rot=(0, 0, -90), color="cyan", cvType=self.ctrls.getControlModuleById("id_048_FacialMouth"))
        self.cvLipsLoc    = self.ctrls.cvLocator(ctrlName=self.guideName+"_Lips", r=0.1, d=1, guide=True, color="cyan", cvType=self.ctrls.getControlModuleById("id_049_FacialLips"))
        self.cvSneerLoc   = self.ctrls.cvLocator(ctrlName=self.guideName+"_Sneer", r=0.2, d=1, guide=True, color="cyan", cvType=self.ctrls.getControlModuleById("id_050_FacialSneer"))
        self.cvGrimaceLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_Grimace", r=0.2, d=1, guide=True, rot=(0, 0, 180), color="cyan", cvType=self.ctrls.getControlModuleById("id_051_FacialGrimace"))
        self.cvFaceLoc    = self.ctrls.cvLocator(ctrlName=self.guideName+"_Face", r=0.2, d=1, guide=True, color="cyan", cvType=self.ctrls.getControlModuleById("id_052_FacialFace"))
        self.cvDeformerCenterLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_DeformerCenter", r=0.6, d=1, guide=True, color="cyan")
        self.cvDeformerRadiusLoc = self.ctrls.cvLocator(ctrlName=self.guideName+"_DeformerRadius", r=0.3, d=1, guide=True, color="cyan", cvType=self.ctrls.getControlModuleById("id_100_HeadDeformerRadius"))

        # create jointGuides:
        self.jGuideNeck0 = cmds.joint(name=self.guideName+"_JGuideNeck0", radius=0.001)
        self.jGuideHead = cmds.joint(name=self.guideName+"_JGuideHead", radius=0.001)
        self.jGuideUpperJaw = cmds.joint(name=self.guideName+"_jGuideUpperJaw", radius=0.001)
        self.jGuideUpperLip = cmds.joint(name=self.guideName+"_jGuideUpperLip", radius=0.001)
        cmds.select(self.jGuideUpperJaw)
        self.jGuideUpperHead = cmds.joint(name=self.guideName+"_jGuideUpperHead", radius=0.001)
        cmds.select(self.jGuideHead)
        self.jGuideJaw  = cmds.joint(name=self.guideName+"_JGuideJaw", radius=0.001)
        self.jGuideChin = cmds.joint(name=self.guideName+"_JGuideChin", radius=0.001)
        self.jGuideChew = cmds.joint(name=self.guideName+"_JGuideChew", radius=0.001)
        cmds.select(self.jGuideChin)
        self.jGuideLowerLip = cmds.joint(name=self.guideName+"_jGuideLowerLip", radius=0.001)
        cmds.select(self.jGuideJaw)
        self.jGuideLLip = cmds.joint(name=self.guideName+"_jGuideLLip", radius=0.001)
        # set jointGuides as templates:
        jGuideList = [self.jGuideNeck0, self.jGuideHead, self.jGuideUpperJaw, self.jGuideUpperHead, self.jGuideJaw, self.jGuideChin, self.jGuideChew, self.jGuideUpperLip, self.jGuideLowerLip]
        for jGuide in jGuideList:
            cmds.setAttr(jGuide+".template", 1)
        cmds.parent(self.jGuideNeck0, self.moduleGrp, relative=True)
        # create cvEnd:
        cmds.select(self.jGuideChew)
        self.cvEndJoint = self.ctrls.cvLocator(ctrlName=self.guideName+"_JointEnd", r=0.1, d=1, guide=True)
        cmds.parent(self.cvEndJoint, self.cvChewLoc)
        cmds.setAttr(self.cvEndJoint+".tz", self.ctrls.dpCheckLinearUnit(0.6))
        self.jGuideEnd = cmds.joint(name=self.guideName+"_JGuideEnd", radius=0.001)
        cmds.setAttr(self.jGuideEnd+".template", 1)
        cmds.parent(self.jGuideEnd, self.jGuideChew)
        # connect cvLocs in jointGuides:
        self.ctrls.directConnect(self.cvNeckLoc, self.jGuideNeck0, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvHeadLoc, self.jGuideHead, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvUpperJawLoc, self.jGuideUpperJaw, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvUpperHeadLoc, self.jGuideUpperHead, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvJawLoc, self.jGuideJaw, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvChinLoc, self.jGuideChin, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvChewLoc, self.jGuideChew, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvUpperLipLoc, self.jGuideUpperLip, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvLowerLipLoc, self.jGuideLowerLip, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvEndJoint, self.jGuideEnd, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        self.ctrls.directConnect(self.cvLCornerLipLoc, self.jGuideLLip, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        # limit, lock and hide cvEnd:
        cmds.transformLimits(self.cvEndJoint, tz=(0.01, 1), etz=(True, False))
        self.ctrls.setLockHide([self.cvEndJoint], ['tx', 'ty', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'ro'])
        # transform cvLocs in order to put as a good head guide:
        cmds.setAttr(self.moduleGrp+".rotateX", -90)
        cmds.setAttr(self.moduleGrp+".rotateY", 90)
        cmds.setAttr(self.cvNeckLoc+".rotateZ", 90)
        cmds.makeIdentity(self.cvNeckLoc, rotate=True, apply=False)
        cmds.setAttr(self.cvHeadLoc+".translateY", 2)
        cmds.setAttr(self.cvUpperJawLoc+".translateY", 3.5)
        cmds.setAttr(self.cvUpperJawLoc+".translateZ", 0.25)
        cmds.setAttr(self.cvUpperHeadLoc+".translateY", 4.2)
        cmds.setAttr(self.cvUpperHeadLoc+".translateZ", 0.5)
        cmds.setAttr(self.cvJawLoc+".translateY", 2.7)
        cmds.setAttr(self.cvJawLoc+".translateZ", 0.7)
        cmds.setAttr(self.cvChinLoc+".translateY", 2.5)
        cmds.setAttr(self.cvChinLoc+".translateZ", 1.0)
        cmds.setAttr(self.cvChewLoc+".translateY", 2.3)
        cmds.setAttr(self.cvChewLoc+".translateZ", 1.3)
        # deformers
        cmds.setAttr(self.cvDeformerCenterLoc+".translateY", 4.0)
        cmds.setAttr(self.cvDeformerCenterLoc+".translateZ", 0.5)
        cmds.setAttr(self.cvDeformerRadiusLoc+".translateX", 3.0)
        cmds.setAttr(self.cvDeformerRadiusLoc+".translateY", 7.0)
        cmds.setAttr(self.cvDeformerRadiusLoc+".translateZ", 3.5)
        cmds.transformLimits(self.cvDeformerRadiusLoc, enableTranslationX=(1, 0), translationX=(0.001, 1), enableTranslationY=(1, 0), translationY=(0.001, 1), enableTranslationZ=(1, 0), translationZ=(0.001, 1))
        # lip cvLocs:
        cmds.setAttr(self.cvUpperLipLoc+".translateY", 2.9)
        cmds.setAttr(self.cvUpperLipLoc+".translateZ", 3.5)
        cmds.setAttr(self.cvLowerLipLoc+".translateY", 2.3)
        cmds.setAttr(self.cvLowerLipLoc+".translateZ", 3.5)
        cmds.setAttr(self.cvLCornerLipLoc+".translateX", 0.6)
        cmds.setAttr(self.cvLCornerLipLoc+".translateY", 2.6)
        cmds.setAttr(self.cvLCornerLipLoc+".translateZ", 3.4)
        # mirror right Lip:
        self.lipTMD = cmds.createNode("multiplyDivide", name=self.guideName+"_LipTMD")
        self.lipRMD = cmds.createNode("multiplyDivide", name=self.guideName+"_LipRMD")
        cmds.connectAttr(self.cvLCornerLipLoc+".translateX", self.lipTMD+".input1X", force=True)
        cmds.connectAttr(self.cvLCornerLipLoc+".translateY", self.lipTMD+".input1Y", force=True)
        cmds.connectAttr(self.cvLCornerLipLoc+".translateZ", self.lipTMD+".input1Z", force=True)
        cmds.connectAttr(self.cvLCornerLipLoc+".rotateX", self.lipRMD+".input1X", force=True)
        cmds.connectAttr(self.cvLCornerLipLoc+".rotateY", self.lipRMD+".input1Y", force=True)
        cmds.connectAttr(self.cvLCornerLipLoc+".rotateZ", self.lipRMD+".input1Z", force=True)
        cmds.connectAttr(self.lipTMD+".outputX", self.cvRCornerLipLoc+".translateX", force=True)
        cmds.connectAttr(self.lipTMD+".outputY", self.cvRCornerLipLoc+".translateY", force=True)
        cmds.connectAttr(self.lipTMD+".outputZ", self.cvRCornerLipLoc+".translateZ", force=True)
        cmds.connectAttr(self.lipRMD+".outputX", self.cvRCornerLipLoc+".rotateX", force=True)
        cmds.connectAttr(self.lipRMD+".outputY", self.cvRCornerLipLoc+".rotateY", force=True)
        cmds.connectAttr(self.lipRMD+".outputZ", self.cvRCornerLipLoc+".rotateZ", force=True)
        cmds.setAttr(self.lipTMD+".input2X", -1)
        cmds.setAttr(self.lipRMD+".input2Y", -1)
        cmds.setAttr(self.lipRMD+".input2Z", -1)
        cmds.setAttr(self.cvRCornerLipLoc+".template", 1)
        # facial cvLocs
        cmds.setAttr(self.cvBrowLoc+".translateX", 0.9)
        cmds.setAttr(self.cvBrowLoc+".translateY", 4.7)
        cmds.setAttr(self.cvBrowLoc+".translateZ", 3.5)
        cmds.setAttr(self.cvEyelidLoc+".translateX", 0.3)
        cmds.setAttr(self.cvEyelidLoc+".translateY", 4.15)
        cmds.setAttr(self.cvEyelidLoc+".translateZ", 3.5)
        cmds.setAttr(self.cvMouthLoc+".translateX", 1)
        cmds.setAttr(self.cvMouthLoc+".translateY", 2.6)
        cmds.setAttr(self.cvMouthLoc+".translateZ", 3.4)
        cmds.setAttr(self.cvLipsLoc+".translateY", 2.6)
        cmds.setAttr(self.cvLipsLoc+".translateZ", 3.9)
        cmds.setAttr(self.cvSneerLoc+".translateY", 3.15)
        cmds.setAttr(self.cvSneerLoc+".translateZ", 3.9)
        cmds.setAttr(self.cvGrimaceLoc+".translateY", 2)
        cmds.setAttr(self.cvGrimaceLoc+".translateZ", 3.9)
        cmds.setAttr(self.cvFaceLoc+".translateX", 2.4)
        cmds.setAttr(self.cvFaceLoc+".translateY", 1.5)
        cmds.setAttr(self.cvFaceLoc+".translateZ", 0.7)
        for facialLoc in [self.cvBrowLoc, self.cvEyelidLoc, self.cvMouthLoc, self.cvLipsLoc, self.cvSneerLoc, self.cvGrimaceLoc, self.cvFaceLoc, self.cvDeformerCenterLoc]:
            cmds.setAttr(facialLoc+".visibility", 0)
        # make parenting between cvLocs:
        cmds.parent(self.cvNeckLoc, self.moduleGrp)
        cmds.parent(self.cvHeadLoc, self.cvNeckLoc)
        cmds.parent(self.cvUpperJawLoc, self.cvJawLoc, self.cvHeadLoc)
        cmds.parent(self.cvChinLoc, self.cvJawLoc)
        cmds.parent(self.cvChewLoc, self.cvLowerLipLoc, self.cvChinLoc)
        cmds.parent(self.cvLCornerLipLoc, self.cvJawLoc)
        cmds.parent(self.cvRCornerLipLoc, self.cvJawLoc)
        cmds.parent(self.cvUpperLipLoc, self.cvUpperHeadLoc, self.cvLipsLoc, self.cvUpperJawLoc)
        cmds.parent(self.cvBrowLoc, self.cvEyelidLoc, self.cvUpperHeadLoc)
        cmds.parent(self.cvMouthLoc, self.cvLCornerLipLoc)
        cmds.parent(self.cvSneerLoc, self.cvUpperLipLoc)
        cmds.parent(self.cvGrimaceLoc, self.cvLowerLipLoc)
        cmds.parent(self.cvFaceLoc, self.cvHeadLoc)
        cmds.parent(self.cvDeformerCenterLoc, self.cvUpperHeadLoc)
        cmds.parent(self.cvDeformerRadiusLoc, self.cvDeformerCenterLoc)
        # deformer cube setup
        defCubeList = cmds.polyCube(name=self.guideName+"_DeformerCube_Geo", constructionHistory=True)
        self.deformerCube = defCubeList[0]
        defPolyCube = cmds.rename(defCubeList[1], self.guideName+"_DeformerCube_PCu")
        cmds.setAttr(self.deformerCube+".translateY", 4.0)
        cmds.setAttr(self.deformerCube+".translateZ", 0.5)
        cmds.parent(self.deformerCube, self.cvDeformerCenterLoc)
        self.defRadiusMD = cmds.createNode("multiplyDivide", name=self.guideName+"_DeformerCube_MD")
        for axis, attr in zip(["X", "Y", "Z"], ["width", "height", "depth"]):
            cmds.setAttr(self.defRadiusMD+".input2"+axis, 2)
            cmds.connectAttr(self.cvDeformerRadiusLoc+".translate"+axis, self.defRadiusMD+".input1"+axis)
            cmds.connectAttr(self.defRadiusMD+".output"+axis, defPolyCube+"."+attr)
        cmds.setAttr(self.deformerCube+".template", 1)
        self.utils.addCustomAttr([self.deformerCube], self.dpUIinst.skin.ignoreSkinningAttr)
        # include nodes into net
        self.addNodeToGuideNet([self.cvNeckLoc, self.cvHeadLoc, self.cvJawLoc, self.cvChinLoc, self.cvChewLoc, self.cvLCornerLipLoc, self.cvUpperJawLoc, self.cvUpperHeadLoc, self.cvUpperLipLoc, self.cvLowerLipLoc, self.cvDeformerCenterLoc, self.cvDeformerRadiusLoc, self.cvBrowLoc, self.cvEyelidLoc, self.cvMouthLoc, self.cvLipsLoc, self.cvSneerLoc, self.cvGrimaceLoc, self.cvFaceLoc, self.cvEndJoint],\
                                ["Neck0", "Head", "Jaw", "Chin", "Chew", "LCornerLip", "UpperJaw", "UpperHead", "UpperLip", "LowerLip", "DeformerCenter", "DeformerRadius", "Brow", "Eyelid", "Mouth", "Lips", "Sneer", "Grimace", "Face", "JointEnd"])
    

    def changeJointNumber(self, enteredNJoints, *args):
        """ Edit the number of joints in the guide.
        """
        self.utils.useDefaultRenderLayer()
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
            # verify if the nJoints is greather or less than the current
            if self.enteredNJoints > self.currentNJoints:
                for n in range(self.currentNJoints+1, self.enteredNJoints+1):
                    # create another N cvNeckLoc:
                    self.cvNeckLoc = self.ctrls.cvJointLoc(ctrlName=self.guideName+"_Neck"+str(n-1), r=0.2, d=1, rot=(-90, 90, 0), guide=True)
                    # set its nJoint value as n:
                    cmds.setAttr(self.cvNeckLoc+".nJoint", n)
                    # parent it to the lastGuide:
                    cmds.parent(self.cvNeckLoc, self.guideName+"_Neck"+str(n-2), relative=True)
                    # create a joint to use like an arrowLine:
                    self.jGuide = cmds.joint(name=self.guideName+"_JGuideNeck"+str(n-1), radius=0.001)
                    cmds.setAttr(self.jGuide+".template", 1)
                    #Prevent a intermidiate node to be added
                    cmds.parent(self.jGuide, self.guideName+"_JGuideNeck"+str(n-2), relative=True)
                    #Do not maintain offset and ensure cv will be at the same place than the joint
                    cmds.parentConstraint(self.cvNeckLoc, self.jGuide, maintainOffset=False, name=self.jGuide+"_PaC")
                    cmds.scaleConstraint(self.cvNeckLoc, self.jGuide, maintainOffset=False, name=self.jGuide+"_ScC")
                    self.addNodeToGuideNet([self.cvNeckLoc], ["Neck"+str(n-1)])
            elif self.enteredNJoints < self.currentNJoints:
                # re-define cvNeckLoc:
                self.cvNeckLoc = self.guideName+"_Neck"+str(self.enteredNJoints)
                # re-parent the children guides:
                childrenGuideBellowList = self.utils.getGuideChildrenList(self.cvNeckLoc)
                if childrenGuideBellowList:
                    for childGuide in childrenGuideBellowList:
                        cmds.parent(childGuide, self.cvNeckLoc)
                # delete difference of nJoints:
                cmds.delete(self.guideName+"_Neck"+str(self.enteredNJoints))
                cmds.delete(self.guideName+"_JGuideNeck"+str(self.enteredNJoints))
                for j in range(self.enteredNJoints, self.currentNJoints):
                    self.removeAttrFromGuideNet(["Neck"+str(j)])
            # get the length of the neck to position segments.
            dist = self.utils.distanceBet(self.guideName+"_Neck0", self.guideName+"_Head")[0]
            # translateY to input on each cvLocator
            distBt = dist/(self.enteredNJoints)
            for n in range(1, self.enteredNJoints):
                # translate the locators to the calculated position:
                cmds.setAttr(self.guideName+"_Neck"+str(n)+".translateY", distBt)
            cmds.setAttr(self.moduleGrp+".nJoints", self.enteredNJoints)
            self.currentNJoints = self.enteredNJoints
            # re-build the preview mirror:
            dpLayoutClass.LayoutClass.createPreviewMirror(self)
        cmds.select(self.moduleGrp)
    

    def changeDeformer(self, deformerValue, *args):
        """ Set the attribute value for deformer and show or hide guide locators.
        """
        #deformerValue = cmds.checkBox(self.deformerCB, query=True, value=True)
        cmds.setAttr(self.moduleGrp+".deformer", deformerValue)
        cmds.setAttr(self.cvDeformerCenterLoc+".visibility", deformerValue)


    def changeFacial(self, value, *args):
        """ Enable or disable the Facial Controls UI.
            Set the moduleGrp facial value as well.
        """
        collapsed = False
        if not value:
            collapsed = True
        try:
            cmds.frameLayout(self.facialCtrlFrameLayout, edit=True, collapse=collapsed, enable=value)
        except:
            pass #maybe it's just a call from a procedural integrated module script
        cmds.setAttr(self.moduleGrp+".facial", value)
        for item in list(self.facialLocDic.keys()):
            cmds.setAttr(self.facialLocDic[item]+".visibility", False)
            if value:
                cmds.setAttr(self.facialLocDic[item]+".visibility", cmds.getAttr(self.moduleGrp+"."+item))


    def changeFacialElement(self, uiCB, attr, *args):
        """ Activate or disactivate the facial elements by them UI checkbox value.
        """
        cbValue = cmds.checkBox(uiCB, query=True, value=True)
        cmds.setAttr(self.moduleGrp+"."+attr, cbValue)
        cmds.setAttr(self.facialLocDic[attr]+".visibility", cbValue)


    def setupJawMove(self, attrCtrl, openCloseID, positiveRotation=True, axis="Y", intAttrID="c049_intensity", invertRot=False, createOutput=False, fixValue=0.01, *args):
        """ Create the setup for move jaw group when jaw control rotates for open or close adjustements.
            Depends on axis and rotation done.
        """
        # declaring naming:
        attrBaseName = self.utils.extractSuffix(attrCtrl)
        drivenGrp = attrBaseName+"_"+self.dpUIinst.lang[openCloseID]+self.dpUIinst.lang['c034_move']+"_Grp"
        # attribute names:
        intAttrName = self.dpUIinst.lang[openCloseID].lower()+self.dpUIinst.lang[intAttrID].capitalize()+axis
        startRotName = self.dpUIinst.lang[openCloseID].lower()+self.dpUIinst.lang['c110_start'].capitalize()+"Rotation"
        unitFixAttrName = self.dpUIinst.lang[openCloseID].lower()+"UnitFix"+axis
        calibAttrName = self.dpUIinst.lang[openCloseID].lower()+self.dpUIinst.lang['c111_calibrate']+axis
        calibOutputAttrName = self.dpUIinst.lang[openCloseID].lower()+self.dpUIinst.lang['c111_calibrate']+self.dpUIinst.lang['c112_output']
        outputAttrName = self.dpUIinst.lang[openCloseID].lower()+self.dpUIinst.lang['c112_output']
        # utility node names:
        jawCalibrateMDName = attrBaseName+self.dpUIinst.lang[openCloseID]+"_"+self.dpUIinst.lang[intAttrID].capitalize()+"_"+self.dpUIinst.lang['c111_calibrate']+"_"+axis+"_MD"
        jawUnitFixMDName = attrBaseName+self.dpUIinst.lang[openCloseID]+"_UnitFix_"+axis+"_MD"
        jawIntMDName = attrBaseName+self.dpUIinst.lang[openCloseID]+"_"+self.dpUIinst.lang[intAttrID].capitalize()+"_"+axis+"_MD"
        jawStartMDName = attrBaseName+self.dpUIinst.lang[openCloseID]+"_Start_"+axis+"_MD"
        jawIntPMAName = attrBaseName+self.dpUIinst.lang[openCloseID]+"_"+self.dpUIinst.lang[intAttrID].capitalize()+"_Start_"+axis+"_PMA"
        jawIntCndName = attrBaseName+self.dpUIinst.lang[openCloseID]+"_"+self.dpUIinst.lang[intAttrID].capitalize()+"_"+axis+"_Cnd"
        jawOutputRmVName = attrBaseName+self.dpUIinst.lang[openCloseID]+"_"+self.dpUIinst.lang['c112_output']+"_RmV"
        
        # create move group and its attributes:
        if not cmds.objExists(drivenGrp):
            drivenGrp = cmds.group(attrCtrl, name=drivenGrp)
            self.utils.addCustomAttr([drivenGrp], self.utils.ignoreTransformIOAttr)
        if not cmds.objExists(self.jawCtrl+"."+startRotName):
            if positiveRotation: #open
                cmds.addAttr(self.jawCtrl, longName=startRotName, attributeType='float', defaultValue=5, minValue=0, keyable=True)
            else: #close
                cmds.addAttr(self.jawCtrl, longName=startRotName, attributeType='float', defaultValue=0, maxValue=0, keyable=True)
            cmds.setAttr(self.jawCtrl+"."+startRotName, keyable=False, channelBox=True)
        if not cmds.objExists(attrCtrl+"."+unitFixAttrName):
            if positiveRotation: #open
                cmds.addAttr(attrCtrl, longName=unitFixAttrName, attributeType='float', defaultValue=fixValue)
            else:
                cmds.addAttr(attrCtrl, longName=unitFixAttrName, attributeType='float', defaultValue=-fixValue)
            cmds.setAttr(attrCtrl+"."+unitFixAttrName, lock=True)
        if not cmds.objExists(attrCtrl+"."+calibAttrName):
            cmds.addAttr(attrCtrl, longName=calibAttrName, attributeType='float', defaultValue=1)
        if not cmds.objExists(attrCtrl+"."+intAttrName):
            cmds.addAttr(attrCtrl, longName=intAttrName, attributeType='float', defaultValue=1, keyable=True)
            cmds.setAttr(attrCtrl+"."+intAttrName, keyable=False, channelBox=True)
        
        # create utility nodes:
        jawCalibrateMD = cmds.createNode('multiplyDivide', name=jawCalibrateMDName)
        jawUnitFixMD = cmds.createNode('multiplyDivide', name=jawUnitFixMDName)
        jawIntMD = cmds.createNode('multiplyDivide', name=jawIntMDName)
        jawStartMD = cmds.createNode('multiplyDivide', name=jawStartMDName)
        jawIntPMA = cmds.createNode('plusMinusAverage', name=jawIntPMAName)
        jawIntCnd = cmds.createNode('condition', name=jawIntCndName)
        self.toIDList.extend([jawCalibrateMD, jawUnitFixMD, jawIntMD, jawStartMD, jawIntPMA, jawIntCnd])
        
        # set attributes to move jaw group when open or close:
        cmds.setAttr(jawIntPMA+".operation", 2) #substract
        cmds.setAttr(jawIntCnd+".operation", 4) #less than
        if positiveRotation: #open
            cmds.setAttr(jawIntCnd+".operation", 2) #greater than
        cmds.setAttr(jawIntCnd+".colorIfFalseR", 0)
        
        # connect utility nodes:
        cmds.connectAttr(self.jawCtrl+".rotateX", jawIntMD+".input1"+axis, force=True)
        cmds.connectAttr(self.jawCtrl+".rotateX", jawIntCnd+".firstTerm", force=True)
        cmds.connectAttr(self.jawCtrl+"."+startRotName, jawStartMD+".input2"+axis, force=True)
        cmds.connectAttr(self.jawCtrl+"."+startRotName, jawIntCnd+".secondTerm", force=True)
        cmds.connectAttr(attrCtrl+"."+intAttrName, jawCalibrateMD+".input1"+axis, force=True)
        cmds.connectAttr(attrCtrl+"."+calibAttrName, jawCalibrateMD+".input2"+axis, force=True)
        cmds.connectAttr(attrCtrl+"."+unitFixAttrName, jawUnitFixMD+".input2"+axis, force=True)
        cmds.connectAttr(jawCalibrateMD+".output"+axis, jawUnitFixMD+".input1"+axis, force=True)
        cmds.connectAttr(jawUnitFixMD+".output"+axis, jawIntMD+".input2"+axis, force=True)
        cmds.connectAttr(jawUnitFixMD+".output"+axis, jawStartMD+".input1"+axis, force=True)
        cmds.connectAttr(jawIntMD+".output"+axis, jawIntPMA+".input1D[0]", force=True)
        cmds.connectAttr(jawStartMD+".output"+axis, jawIntPMA+".input1D[1]", force=True)
        cmds.connectAttr(jawIntPMA+".output1D", jawIntCnd+".colorIfTrueR", force=True)
        cmds.connectAttr(jawIntCnd+".outColorR", drivenGrp+".translate"+axis, force=True)
        
        # invert rotation for lower lip exception:
        if invertRot:
            invetRotPMAName = attrBaseName+self.dpUIinst.lang[openCloseID]+self.dpUIinst.lang[intAttrID].capitalize()+"_"+axis+"_InvertRot_PMA"
            invetRotMDName = attrBaseName+self.dpUIinst.lang[openCloseID]+self.dpUIinst.lang[intAttrID].capitalize()+"_"+axis+"_InvertRot_MD"
            invetRotPMA = cmds.createNode('plusMinusAverage', name=invetRotPMAName)
            invetRotMD = cmds.createNode('multiplyDivide', name=invetRotMDName)
            self.toIDList.extend([invetRotPMA, invetRotMD])
            cmds.setAttr(invetRotPMA+".operation", 2) #substract
            cmds.setAttr(invetRotMD+".input2X", -1)
            cmds.setAttr(jawIntCnd+".colorIfFalseG", 0)
            cmds.connectAttr(self.jawCtrl+".rotateX", invetRotPMA+".input1D[0]", force=True)
            cmds.connectAttr(self.jawCtrl+"."+startRotName, invetRotPMA+".input1D[1]", force=True)
            cmds.connectAttr(invetRotPMA+".output1D", jawIntCnd+".colorIfTrueG", force=True)
            cmds.connectAttr(jawIntCnd+".outColorG", invetRotMD+".input1X", force=True)
            cmds.connectAttr(invetRotMD+".outputX", drivenGrp+".rotateX", force=True)
            
        # output to a blendShape target value setup:
        if createOutput:
            if not cmds.objExists(self.jawCtrl+"."+outputAttrName):
                cmds.addAttr(self.jawCtrl, longName=calibOutputAttrName, attributeType='float', defaultValue=1)
                cmds.addAttr(self.jawCtrl, longName=outputAttrName, attributeType='float', defaultValue=1)
            jawOutputRmV = cmds.createNode('remapValue', name=jawOutputRmVName)
            self.toIDList.append(jawOutputRmV)
            cmds.connectAttr(self.jawCtrl+".rotateX", jawOutputRmV+".inputValue", force=True)
            cmds.connectAttr(self.jawCtrl+"."+calibOutputAttrName, jawOutputRmV+".inputMax", force=True)
            cmds.connectAttr(jawOutputRmV+".outValue", self.jawCtrl+"."+outputAttrName, force=True)
            cmds.setAttr(self.jawCtrl+"."+outputAttrName, lock=True)

    
    def getCalibratePresetList(self, s, *args):
        """ Returns the calibration preset and invert lists for neck and head joints.
        """
        invertList = [[], [], ["invertTX", "invertRY", "invertRZ"], [], []]
        presetList = [{}, {"calibrateTX":1}, {"calibrateTX":1}, {"calibrateTZ":1}, {"calibrateTZ":-1}]
        if s == 1:
            if self.addFlip:
                invertList = [[], ["invertTX"], ["invertTX"], ["invertTZ"], ["invertTZ"]]
        return presetList, invertList


    def autoRotateCalc(self, n, *args):
        if self.nJoints < 7:
            return 0.15*(n+1)
        else:
            if n == 0:
                return (2**(1/self.nJoints))-1
            else:
                return (2**(n/self.nJoints))-(1-(1/self.nJoints))

    
    def redeclareVariables(self, middle, side="", guide="", *args):
        """ Just redeclare main locators and dictionary to use it again after reloading code.
        """
        self.base            = side+middle+guide+"_Base"
        self.cvHeadLoc       = side+middle+guide+"_Head"
        self.cvUpperJawLoc   = side+middle+guide+"_UpperJaw"
        self.cvUpperHeadLoc  = side+middle+guide+"_UpperHead"
        self.cvJawLoc        = side+middle+guide+"_Jaw"
        self.cvChinLoc       = side+middle+guide+"_Chin"
        self.cvChewLoc       = side+middle+guide+"_Chew"
        self.cvLCornerLipLoc = side+middle+guide+"_LCornerLip"
        self.cvRCornerLipLoc = side+middle+guide+"_RCornerLip"
        self.cvUpperLipLoc   = side+middle+guide+"_UpperLip"
        self.cvLowerLipLoc   = side+middle+guide+"_LowerLip"
        self.cvEndJoint      = side+middle+guide+"_JointEnd"
        self.radiusGuide     = side+middle+guide+"_Base_RadiusCtrl"
        self.cvBrowLoc       = side+middle+guide+"_Brow"
        self.cvEyelidLoc     = side+middle+guide+"_Eyelid"
        self.cvMouthLoc      = side+middle+guide+"_Mouth"
        self.cvLipsLoc       = side+middle+guide+"_Lips"
        self.cvSneerLoc      = side+middle+guide+"_Sneer"
        self.cvGrimaceLoc    = side+middle+guide+"_Grimace"
        self.cvFaceLoc       = side+middle+guide+"_Face"
        self.facialLocDic = {
                                self.facialAttrList[0] : self.cvBrowLoc,
                                self.facialAttrList[1] : self.cvEyelidLoc,
                                self.facialAttrList[2] : self.cvMouthLoc,
                                self.facialAttrList[3] : self.cvLipsLoc,
                                self.facialAttrList[4] : self.cvSneerLoc,
                                self.facialAttrList[5] : self.cvGrimaceLoc,
                                self.facialAttrList[6] : self.cvFaceLoc
                            }
        self.cvDeformerCenterLoc = side+middle+guide+"_DeformerCenter"
        self.cvDeformerRadiusLoc = side+middle+guide+"_DeformerRadius"
        self.deformerCube = side+middle+guide+"_DeformerCube_Geo"
        

    def rigModule(self, *args):
        dpBaseClass.StartClass.rigModule(self)
        # verify if the guide exists:
        if cmds.objExists(self.moduleGrp):
            # articulation joint:
            self.addArticJoint = self.getArticulation()
            self.addFlip = self.getModuleAttr("flip")
            self.addCorrective = self.getModuleAttr("corrective")
            # declare lists to store names and attributes:
            self.worldRefList, self.upperCtrlList, self.upperJawCtrlList = [], [], []
            self.aCtrls, self.aLCtrls, self.aRCtrls = [], [], []
            # run for all sides
            for s, side in enumerate(self.sideList):
                self.neckLocList, self.neckCtrlList, self.neckJointList = [], [], []
                # redeclaring variables:
                self.redeclareVariables(self.userGuideName, side, "_Guide")
                
                # generating naming:
                headJntName = side+self.userGuideName+"_01_"+self.dpUIinst.lang['c024_head']+"_Jnt"
                if self.addArticJoint:
                    headJntName = side+self.userGuideName+"_02_"+self.dpUIinst.lang['c024_head']+"_Jnt"
                upperJawJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c025_jaw']+"_Jnt"
                upperHeadJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c024_head']+"_Jnt"
                upperEndJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c024_head']+"_JEnd"
                jawJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c025_jaw']+"_Jnt"
                chinJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c026_chin']+"_Jnt"
                chewJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c048_chew']+"_Jnt"
                endJntName = side+self.userGuideName+"_JEnd"
                lCornerLipJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['p002_left']+"_"+self.dpUIinst.lang['c043_corner']+self.dpUIinst.lang['c039_lip']+"_Jnt"
                rCornerLipJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['p003_right']+"_"+self.dpUIinst.lang['c043_corner']+self.dpUIinst.lang['c039_lip']+"_Jnt"
                upperLipJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c039_lip']+"_Jnt"
                lowerLipJntName = side+self.userGuideName+"_"+self.dpUIinst.lang['c045_lower']+self.dpUIinst.lang['c039_lip']+"_Jnt"
                neckCtrlBaseName = side+self.userGuideName+"_"+self.dpUIinst.lang['c023_neck']
                headCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c024_head']+"_Ctrl"
                headSubCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c024_head']+"_Sub_Ctrl"
                upperJawCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c025_jaw']+"_Ctrl"
                upperHeadCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c024_head']+"_Ctrl"
                jawCtrlName  = side+self.userGuideName+"_"+self.dpUIinst.lang['c025_jaw']+"_Ctrl"
                chinCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c026_chin']+"_Ctrl"
                chewCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c048_chew']+"_Ctrl"
                lCornerLipCtrlName = self.dpUIinst.lang['p002_left']+"_"+self.userGuideName+"_"+self.dpUIinst.lang['c043_corner']+self.dpUIinst.lang['c039_lip']+"_Ctrl"
                rCornerLipCtrlName = self.dpUIinst.lang['p003_right']+"_"+self.userGuideName+"_"+self.dpUIinst.lang['c043_corner']+self.dpUIinst.lang['c039_lip']+"_Ctrl"
                upperLipCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c039_lip']+"_Ctrl"
                lowerLipCtrlName = side+self.userGuideName+"_"+self.dpUIinst.lang['c045_lower']+self.dpUIinst.lang['c039_lip']+"_Ctrl"
                self.calibrateName = self.dpUIinst.lang["c111_calibrate"].lower()
                
                # connect facial controllers to blendShape node or tweakers:
                self.connectUserType = self.bsType
                userType = cmds.getAttr(self.moduleGrp+".connectUserType")
                if userType == 1:
                    self.connectUserType = self.jointsType

                # get the number of joints to be created for the neck:
                self.nJoints = cmds.getAttr(self.base+".nJoints")

                # creating joints:
                cmds.select(clear=True)
                for n in range(0, self.nJoints):
                    # neck segments:
                    cvNeckLoc = side+self.userGuideName+"_Guide_Neck"+str(n)
                    self.neckLocList.append(cvNeckLoc)
                    neckJnt = cmds.joint(name=neckCtrlBaseName+"_"+str(n).zfill(2)+"_Jnt", scaleCompensate=False)
                    self.neckJointList.append(neckJnt)
                self.headJnt = cmds.joint(name=headJntName, scaleCompensate=False)
                self.upperJawJnt = cmds.joint(name=upperJawJntName, scaleCompensate=False)
                self.upperHeadJnt = cmds.joint(name=upperHeadJntName, scaleCompensate=False)
                self.upperEndJnt = cmds.joint(name=upperEndJntName, scaleCompensate=False, radius=0.5)
                cmds.setAttr(self.upperEndJnt+".translateY", 0.3*self.ctrlRadius)
                cmds.select(self.headJnt)
                self.jawJnt  = cmds.joint(name=jawJntName, scaleCompensate=False)
                self.chinJnt = cmds.joint(name=chinJntName, scaleCompensate=False)
                self.chewJnt = cmds.joint(name=chewJntName, scaleCompensate=False)
                self.endJnt  = cmds.joint(name=endJntName, scaleCompensate=False, radius=0.5)
                cmds.select(self.headJnt)
                self.lCornerLipJnt = cmds.joint(name=lCornerLipJntName, scaleCompensate=False)
                cmds.select(self.headJnt)
                self.rCornerLipJnt = cmds.joint(name=rCornerLipJntName, scaleCompensate=False)
                cmds.select(self.upperJawJnt)
                self.upperLipJnt = cmds.joint(name=upperLipJntName, scaleCompensate=False)
                cmds.select(self.chinJnt)
                self.lowerLipJnt = cmds.joint(name=lowerLipJntName, scaleCompensate=False)
                cmds.select(clear=True)
                dpARJointList = [self.headJnt, self.upperJawJnt, self.upperHeadJnt, self.jawJnt, self.chinJnt, self.chewJnt, self.lCornerLipJnt, self.rCornerLipJnt, self.upperLipJnt, self.lowerLipJnt]
                dpARJointList.extend(self.neckJointList)
                for dpARJoint in dpARJointList:
                    cmds.addAttr(dpARJoint, longName='dpAR_joint', attributeType='float', keyable=False)
                # joint labelling:
                for n in range(0, self.nJoints):
                    self.utils.setJointLabel(self.neckJointList[n], s+self.jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c023_neck']+"_"+str(n).zfill(2))
                self.utils.setJointLabel(self.headJnt, s+self.jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c024_head'])
                self.utils.setJointLabel(self.upperJawJnt, s+self.jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c025_jaw'])
                self.utils.setJointLabel(self.upperHeadJnt, s+self.jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c024_head'])
                self.utils.setJointLabel(self.jawJnt, s+self.jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c025_jaw'])
                self.utils.setJointLabel(self.chinJnt, s+self.jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c026_chin'])
                self.utils.setJointLabel(self.chewJnt, s+self.jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c048_chew'])
                self.utils.setJointLabel(self.lCornerLipJnt, 1, 18, self.userGuideName+"_"+self.dpUIinst.lang['c039_lip'])
                self.utils.setJointLabel(self.rCornerLipJnt, 2, 18, self.userGuideName+"_"+self.dpUIinst.lang['c039_lip'])
                self.utils.setJointLabel(self.upperLipJnt, s+self.jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c039_lip'])
                self.utils.setJointLabel(self.lowerLipJnt, s+self.jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c045_lower']+self.dpUIinst.lang['c039_lip'])
                # creating controls:
                for n in range(0, self.nJoints):
                    neckCtrl = self.ctrls.cvControl("id_022_HeadNeck", ctrlName=neckCtrlBaseName+"_"+str(n).zfill(2)+"_Ctrl", r=(self.ctrlRadius/((n*0.2)+1)), d=self.curveDegree, dir="-Z", guideSource=self.guideName+"_Neck"+str(n))
                    if n > 0:
                        cmds.parent(neckCtrl, self.neckCtrlList[-1])
                    self.neckCtrlList.append(neckCtrl)
                self.headCtrl = self.ctrls.cvControl("id_023_HeadHead", ctrlName=headCtrlName, r=(self.ctrlRadius * 2.5), d=self.curveDegree, guideSource=self.guideName+"_Head")
                self.headSubCtrl = self.ctrls.cvControl("id_093_HeadSub", ctrlName=headSubCtrlName, r=(self.ctrlRadius * 2.2), d=self.curveDegree, guideSource=self.guideName+"_Head")
                self.upperJawCtrl = self.ctrls.cvControl("id_069_HeadUpperJaw", ctrlName=upperJawCtrlName, r=self.ctrlRadius, d=self.curveDegree, headDef=1, guideSource=self.guideName+"_UpperJaw")
                self.upperHeadCtrl = self.ctrls.cvControl("id_081_HeadUpperHead", ctrlName=upperHeadCtrlName, r=self.ctrlRadius, d=self.curveDegree, headDef=1, guideSource=self.guideName+"_UpperHead")
                self.jawCtrl = self.ctrls.cvControl("id_024_HeadJaw", ctrlName=jawCtrlName, r=self.ctrlRadius, d=self.curveDegree, headDef=3, guideSource=self.guideName+"_Jaw")
                self.chinCtrl = self.ctrls.cvControl("id_025_HeadChin", ctrlName=chinCtrlName, r=(self.ctrlRadius * 0.2), d=self.curveDegree, headDef=3, guideSource=self.guideName+"_Chin")
                self.chewCtrl = self.ctrls.cvControl("id_026_HeadChew", ctrlName=chewCtrlName, r=(self.ctrlRadius * 0.15), d=self.curveDegree, headDef=3, guideSource=self.guideName+"_Chew")
                self.lCornerLipCtrl = self.ctrls.cvControl("id_027_HeadLipCorner", ctrlName=lCornerLipCtrlName, r=(self.ctrlRadius * 0.1), d=self.curveDegree, headDef=3, guideSource=self.guideName+"_LCornerLip")
                self.rCornerLipCtrl = self.ctrls.cvControl("id_027_HeadLipCorner", ctrlName=rCornerLipCtrlName, r=(self.ctrlRadius * 0.1), d=self.curveDegree, headDef=3, guideSource=self.guideName+"_RCornerLip")
                self.upperLipCtrl = self.ctrls.cvControl("id_072_HeadUpperLip", ctrlName=upperLipCtrlName, r=(self.ctrlRadius * 0.1), d=self.curveDegree, headDef=3, guideSource=self.guideName+"_UpperLip")
                self.lowerLipCtrl = self.ctrls.cvControl("id_073_HeadLowerLip", ctrlName=lowerLipCtrlName, r=(self.ctrlRadius * 0.1), d=self.curveDegree, headDef=3, guideSource=self.guideName+"_LowerLip")
                headDefCtrlList = [self.upperJawCtrl, self.upperHeadCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl, self.lCornerLipCtrl, self.rCornerLipCtrl, self.upperLipCtrl, self.lowerLipCtrl]
                
                # facial controls
                facialCtrlList = []
                if cmds.getAttr(self.moduleGrp+".facial"):
                    if cmds.getAttr(self.moduleGrp+".facialBrow"):
                        self.lBrowCtrl, lBrowCtrlGrp = self.dpCreateFacialCtrl(side, self.dpUIinst.lang["p002_left"], self.dpUIinst.lang["c060_brow"], "id_046_FacialBrow", self.browTgtList, (0, 0, 0), False, False, True, True, True, True, False, "red", True, False)
                        self.rBrowCtrl, rBrowCtrlGrp = self.dpCreateFacialCtrl(side, self.dpUIinst.lang["p003_right"], self.dpUIinst.lang["c060_brow"], "id_046_FacialBrow", self.browTgtList, (0, 0, 0), False, False, True, True, True, True, False, "blue", True, False)
                        facialCtrlList.extend([self.lBrowCtrl, self.rBrowCtrl])
                    if cmds.getAttr(self.moduleGrp+".facialEyelid"):
                        if self.connectUserType == self.bsType:
                            self.lEyelidCtrl, lEyelidCtrlGrp = self.dpCreateFacialCtrl(side, self.dpUIinst.lang["p002_left"], self.dpUIinst.lang["c042_eyelid"], "id_047_FacialEyelid", self.eyelidTgtList, (0, 0, 90), True, False, True, False, True, True, False, "red", True, False)
                            self.rEyelidCtrl, rEyelidCtrlGrp = self.dpCreateFacialCtrl(side, self.dpUIinst.lang["p003_right"], self.dpUIinst.lang["c042_eyelid"], "id_047_FacialEyelid", self.eyelidTgtList, (0, 0, 90), True, False, True, False, True, True, False, "blue", True, False)
                            facialCtrlList.extend([self.lEyelidCtrl, self.rEyelidCtrl])
                    if cmds.getAttr(self.moduleGrp+".facialMouth"):
                        self.lMouthCtrl, lMouthCtrlGrp = self.dpCreateFacialCtrl(side, self.dpUIinst.lang["p002_left"], self.dpUIinst.lang["c061_mouth"], "id_048_FacialMouth", self.mouthTgtList, (0, 0, -90), False, False, True, True, True, True, False, "red", True, True)
                        self.rMouthCtrl, rMouthCtrlGrp = self.dpCreateFacialCtrl(side, self.dpUIinst.lang["p003_right"], self.dpUIinst.lang["c061_mouth"], "id_048_FacialMouth", self.mouthTgtList, (0, 0, -90), False, False, True, True, True, True, False, "blue", True, True)
                        facialCtrlList.extend([self.lMouthCtrl, self.rMouthCtrl])
                    if cmds.getAttr(self.moduleGrp+".facialLips"):
                        self.lipsCtrl, lipsCtrlGrp = self.dpCreateFacialCtrl(side, None, self.dpUIinst.lang["c062_lips"], "id_049_FacialLips", self.lipsTgtList, (0, 0, 0), False, False, False, True, True, True, False, "yellow", True, True)
                        facialCtrlList.append(self.lipsCtrl)
                    if cmds.getAttr(self.moduleGrp+".facialSneer"):
                        self.sneerCtrl, sneerCtrlGrp = self.dpCreateFacialCtrl(side, None, self.dpUIinst.lang["c063_sneer"], "id_050_FacialSneer", self.sneerTgtList, (0, 0, 0), False, False, False, True, True, True, False, "cyan", True, True, True, True)
                        facialCtrlList.append(self.sneerCtrl)
                    if cmds.getAttr(self.moduleGrp+".facialGrimace"):
                        self.grimaceCtrl, grimaceCtrlGrp = self.dpCreateFacialCtrl(side, None, self.dpUIinst.lang["c064_grimace"], "id_051_FacialGrimace", self.grimaceTgtList, (0, 0, 0), False, False, False, True, True, True, False, "cyan", True, True, True, True, True)
                        facialCtrlList.append(self.grimaceCtrl)
                    if cmds.getAttr(self.moduleGrp+".facialFace"):
                        self.faceCtrl, faceCtrlGrp = self.dpCreateFacialCtrl(side, None, self.dpUIinst.lang["c065_face"], "id_052_FacialFace", self.faceTgtList, (0, 0, 0), True, True, True, True, True, True, True, "cyan", False, False)
                        facialCtrlList.append(self.faceCtrl)

                # colorize controllers
                self.upperCtrlList.append(self.upperHeadCtrl)
                self.aCtrls.append([self.upperLipCtrl, self.lowerLipCtrl])
                self.aLCtrls.append([self.lCornerLipCtrl])
                self.aRCtrls.append([self.rCornerLipCtrl])
                self.aInnerCtrls.append([self.headSubCtrl])
                self.ctrls.setSubControlDisplay(self.headCtrl, self.headSubCtrl, 1)
                self.upperJawCtrlList.append(self.upperJawCtrl)

                # optimize control CV shapes:
                tempHeadCluster = cmds.cluster(self.headCtrl, self.headSubCtrl)[1]
                cmds.setAttr(tempHeadCluster+".translateY", -0.5)
                tempJawCluster = cmds.cluster(self.jawCtrl)[1]
                cmds.setAttr(tempJawCluster+".translateY", -2)
                cmds.setAttr(tempJawCluster+".translateZ", 2.1)
                tempChinCluster = cmds.cluster(self.chinCtrl)[1]
                cmds.setAttr(tempChinCluster+".translateY", -1.4)
                cmds.setAttr(tempChinCluster+".translateZ", 3.6)
                cmds.setAttr(tempChinCluster+".rotateX", 22)
                tempChewCluster = cmds.cluster(self.chewCtrl)[1]
                cmds.setAttr(tempChewCluster+".translateY", -1.35)
                cmds.setAttr(tempChewCluster+".translateZ", 3.6)
                cmds.setAttr(tempChewCluster+".rotateX", 22)
                cmds.delete([self.headCtrl, self.headSubCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl], constructionHistory=True)
                
                #Setup Axis Order
                if self.rigType == dpBaseClass.RigType.quadruped:
                    for n in range(0, self.nJoints):
                        cmds.setAttr(self.neckCtrlList[n]+".rotateOrder", 1)
                    cmds.setAttr(self.headCtrl+".rotateOrder", 1)
                    cmds.setAttr(self.headSubCtrl+".rotateOrder", 1)
                    cmds.setAttr(self.upperJawCtrl+".rotateOrder", 1)
                    cmds.setAttr(self.upperHeadCtrl+".rotateOrder", 1)
                    cmds.setAttr(self.jawCtrl+".rotateOrder", 1)
                else:
                    for n in range(0, self.nJoints):
                        cmds.setAttr(self.neckCtrlList[n]+".rotateOrder", 3)
                    cmds.setAttr(self.headCtrl+".rotateOrder", 3)
                    cmds.setAttr(self.headSubCtrl+".rotateOrder", 3)
                    cmds.setAttr(self.upperJawCtrl+".rotateOrder", 3)
                    cmds.setAttr(self.upperHeadCtrl+".rotateOrder", 3)
                    cmds.setAttr(self.jawCtrl+".rotateOrder", 3)

                # creating the originedFrom attributes (in order to permit integrated parents in the future):
                for n in range(0, self.nJoints):
                    if n == 0:
                        self.utils.originedFrom(objName=self.neckCtrlList[0], attrString=self.base+";"+self.neckLocList[0]+";"+self.radiusGuide)
                    else:
                        self.utils.originedFrom(objName=self.neckCtrlList[n], attrString=self.neckLocList[n])
                self.utils.originedFrom(objName=self.headSubCtrl, attrString=self.cvHeadLoc)
                self.utils.originedFrom(objName=self.upperJawCtrl, attrString=self.cvUpperJawLoc)
                self.utils.originedFrom(objName=self.upperHeadCtrl, attrString=self.cvUpperHeadLoc)
                self.utils.originedFrom(objName=self.upperLipCtrl, attrString=self.cvUpperLipLoc)
                self.utils.originedFrom(objName=self.jawCtrl, attrString=self.cvJawLoc)
                self.utils.originedFrom(objName=self.chinCtrl, attrString=self.cvChinLoc)
                self.utils.originedFrom(objName=self.chewCtrl, attrString=self.cvChewLoc+";"+self.cvEndJoint)
                self.utils.originedFrom(objName=self.lCornerLipCtrl, attrString=self.cvLCornerLipLoc)
                self.utils.originedFrom(objName=self.rCornerLipCtrl, attrString=self.cvRCornerLipLoc)
                self.utils.originedFrom(objName=self.lowerLipCtrl, attrString=self.cvLowerLipLoc)
                # facial origined from
                if cmds.getAttr(self.moduleGrp+".facial"):
                    if cmds.getAttr(self.moduleGrp+".facialBrow"):
                        if cmds.getAttr(self.moduleGrp+".facialEyelid"):
                            cmds.setAttr(self.upperHeadCtrl+".originedFrom", self.cvUpperHeadLoc+";"+self.cvBrowLoc+";"+self.cvEyelidLoc, type="string")
                        else:
                            cmds.setAttr(self.upperHeadCtrl+".originedFrom", self.cvUpperHeadLoc+";"+self.cvBrowLoc, type="string")
                    elif cmds.getAttr(self.moduleGrp+".facialEyelid"):
                        cmds.setAttr(self.upperHeadCtrl+".originedFrom", self.cvUpperHeadLoc+";"+self.cvEyelidLoc, type="string")
                    if cmds.getAttr(self.moduleGrp+".facialMouth"):
                        if cmds.getAttr(self.moduleGrp+".facialLips"):
                            cmds.setAttr(self.upperJawCtrl+".originedFrom", self.cvUpperJawLoc+";"+self.cvMouthLoc+";"+self.cvLipsLoc, type="string")
                        else:
                            cmds.setAttr(self.upperJawCtrl+".originedFrom", self.cvUpperJawLoc+";"+self.cvMouthLoc, type="string")
                    elif cmds.getAttr(self.moduleGrp+".facialLips"):
                        cmds.setAttr(self.upperJawCtrl+".originedFrom", self.cvUpperJawLoc+";"+self.cvLipsLoc, type="string")
                    if cmds.getAttr(self.moduleGrp+".facialSneer"):
                        cmds.setAttr(self.upperLipCtrl+".originedFrom", self.cvUpperLipLoc+";"+self.cvSneerLoc, type="string")
                    if cmds.getAttr(self.moduleGrp+".facialGrimace"):
                        cmds.setAttr(self.lowerLipCtrl+".originedFrom", self.cvLowerLipLoc+";"+self.cvGrimaceLoc, type="string")
                    if cmds.getAttr(self.moduleGrp+".facialFace"):
                        cmds.setAttr(self.headSubCtrl+".originedFrom", self.cvHeadLoc+";"+self.cvFaceLoc, type="string")
                
                # temporary parentConstraints:
                for n in range(0, self.nJoints):
                    cmds.delete(cmds.parentConstraint(self.neckLocList[n], self.neckCtrlList[n], maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvHeadLoc, self.headCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvHeadLoc, self.headSubCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvUpperJawLoc, self.upperJawCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvUpperHeadLoc, self.upperHeadCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvJawLoc, self.jawCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvChinLoc, self.chinCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvChewLoc, self.chewCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvLCornerLipLoc, self.lCornerLipCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvRCornerLipLoc, self.rCornerLipCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvUpperLipLoc, self.upperLipCtrl, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.cvLowerLipLoc, self.lowerLipCtrl, maintainOffset=False))

                # edit the mirror shape to a good direction of controls:
                toFlipList = [self.headCtrl, self.headSubCtrl, self.upperJawCtrl, self.upperHeadCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl, self.lCornerLipCtrl, self.rCornerLipCtrl, self.upperLipCtrl, self.lowerLipCtrl]
                # fixing flip mirror:
                if s == 1:
                    if self.addFlip:
                        for toFlipNode in toFlipList:
                            cmds.setAttr(toFlipNode+".scaleX", -1)
                            cmds.setAttr(toFlipNode+".scaleY", -1)
                            cmds.setAttr(toFlipNode+".scaleZ", -1)

                # zeroOut controls:
                self.zeroCornerLipCtrlList = self.utils.zeroOut([self.lCornerLipCtrl, self.rCornerLipCtrl])
                self.lLipGrp = cmds.group(self.lCornerLipCtrl, name=self.lCornerLipCtrl+"_Grp")
                self.rLipGrp = cmds.group(self.rCornerLipCtrl, name=self.rCornerLipCtrl+"_Grp")
                if not self.addFlip:
                    cmds.setAttr(self.zeroCornerLipCtrlList[1]+".scaleX", -1)
                self.zeroNeckCtrlList = self.utils.zeroOut(self.neckCtrlList)
                self.zeroCtrlList = self.utils.zeroOut([self.headCtrl, self.upperJawCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl, self.upperLipCtrl, self.lowerLipCtrl, self.upperHeadCtrl])
                self.zeroCtrlList.extend(self.zeroCornerLipCtrlList)
                self.zeroCtrlList.extend(self.utils.zeroOut([self.headSubCtrl]))
                
                # make joints be ride by controls:
                for n in range(0, self.nJoints):
                    cmds.parentConstraint(self.neckCtrlList[n], self.neckJointList[n], maintainOffset=False, name=self.neckJointList[n]+"_PaC")
                    cmds.scaleConstraint(self.neckCtrlList[n], self.neckJointList[n], maintainOffset=False, name=self.neckJointList[n]+"_ScC")
                cmds.parentConstraint(self.headSubCtrl, self.headJnt, maintainOffset=False, name=self.headJnt+"_PaC")
                cmds.parentConstraint(self.upperJawCtrl, self.upperJawJnt, maintainOffset=False, name=self.upperJawJnt+"_PaC")
                cmds.parentConstraint(self.upperHeadCtrl, self.upperHeadJnt, maintainOffset=False, name=self.upperHeadJnt+"_PaC")
                cmds.parentConstraint(self.jawCtrl, self.jawJnt, maintainOffset=False, name=self.jawJnt+"_PaC")
                cmds.parentConstraint(self.chinCtrl, self.chinJnt, maintainOffset=False, name=self.chinJnt+"_PaC")
                cmds.parentConstraint(self.chewCtrl, self.chewJnt, maintainOffset=False, name=self.chewJnt+"_PaC")
                cmds.parentConstraint(self.lCornerLipCtrl, self.lCornerLipJnt, maintainOffset=False, name=self.lCornerLipJnt+"_PaC")
                cmds.parentConstraint(self.rCornerLipCtrl, self.rCornerLipJnt, maintainOffset=False, name=self.rCornerLipJnt+"_PaC")
                cmds.parentConstraint(self.upperLipCtrl, self.upperLipJnt, maintainOffset=False, name=self.upperLipJnt+"_PaC")
                cmds.parentConstraint(self.lowerLipCtrl, self.lowerLipJnt, maintainOffset=False, name=self.lowerLipJnt+"_PaC")
                cmds.scaleConstraint(self.headSubCtrl, self.headJnt, maintainOffset=True, name=self.headJnt+"_ScC")
                cmds.scaleConstraint(self.upperJawCtrl, self.upperJawJnt, maintainOffset=True, name=self.upperJawJnt+"_ScC")
                cmds.scaleConstraint(self.upperHeadCtrl, self.upperHeadJnt, maintainOffset=True, name=self.upperHeadJnt+"_ScC")
                cmds.scaleConstraint(self.jawCtrl, self.jawJnt, maintainOffset=True, name=self.jawJnt+"_ScC")
                cmds.scaleConstraint(self.chinCtrl, self.chinJnt, maintainOffset=True, name=self.chinJnt+"_ScC")
                cmds.scaleConstraint(self.chewCtrl, self.chewJnt, maintainOffset=True, name=self.chewJnt+"_ScC")
                cmds.scaleConstraint(self.lCornerLipCtrl, self.lCornerLipJnt, maintainOffset=True, name=self.lCornerLipJnt+"_ScC")
                cmds.scaleConstraint(self.rCornerLipCtrl, self.rCornerLipJnt, maintainOffset=True, name=self.rCornerLipJnt+"_ScC")
                cmds.scaleConstraint(self.upperLipCtrl, self.upperLipJnt, maintainOffset=True, name=self.upperLipJnt+"_ScC")
                cmds.scaleConstraint(self.lowerLipCtrl, self.lowerLipJnt, maintainOffset=True, name=self.lowerLipJnt+"_ScC")
                cmds.delete(cmds.parentConstraint(self.cvEndJoint, self.endJnt, maintainOffset=False))

                # hide unnecessary zero out bone display:
                self.utils.zeroOutJoints([self.lCornerLipJnt, self.rCornerLipJnt])

                # head follow/isolate create interations between neck and head:
                self.headOrientGrp = cmds.group(empty=True, name=self.headCtrl+"_Orient_Grp")
                self.zeroHeadGrp = self.utils.zeroOut([self.headOrientGrp])[0]
                cmds.parent(self.zeroHeadGrp, self.neckCtrlList[-1])
                self.worldRef = cmds.group(empty=True, name=side+self.userGuideName+"_WorldRef_Grp")
                self.worldRefList.append(self.worldRef)
                cmds.delete(cmds.parentConstraint(self.neckCtrlList[0], self.worldRef, maintainOffset=False))
                cmds.delete(cmds.parentConstraint(self.zeroCtrlList[0], self.zeroHeadGrp, maintainOffset=False))
                cmds.parent(self.zeroCtrlList[0], self.headOrientGrp, absolute=True)
                headRotateParentConst = cmds.parentConstraint(self.neckCtrlList[-1], self.worldRef, self.headOrientGrp, maintainOffset=True, skipTranslate=["x", "y", "z"], name=self.headOrientGrp+"_PaC")[0]
                cmds.setAttr(headRotateParentConst+".interpType", 2) #shortest

                # connect reverseNode:
                cmds.addAttr(self.headCtrl, longName=self.dpUIinst.lang['c032_follow'], attributeType='float', minValue=0, maxValue=1, keyable=True)
                cmds.connectAttr(self.headCtrl+'.'+self.dpUIinst.lang['c032_follow'], headRotateParentConst+"."+self.neckCtrlList[-1]+"W0", force=True)
                self.headRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_"+self.dpUIinst.lang['c032_follow'].capitalize()+"_Rev")
                cmds.connectAttr(self.headCtrl+'.'+self.dpUIinst.lang['c032_follow'], self.headRevNode+".inputX", force=True)
                cmds.connectAttr(self.headRevNode+'.outputX', headRotateParentConst+"."+self.worldRef+"W1", force=True)
                
                # setup neck autoRotate:
                for n in range(0, self.nJoints):
                    self.neckPivot = cmds.xform(self.neckCtrlList[n], query=True, worldSpace=True, translation=True)
                    self.neckOrientGrp = cmds.group(self.neckCtrlList[n], name=self.neckCtrlList[n]+"_Orient_Grp")
                    self.utils.addCustomAttr([self.neckOrientGrp], self.utils.ignoreTransformIOAttr)
                    cmds.xform(self.neckOrientGrp, pivots=(self.neckPivot[0], self.neckPivot[1], self.neckPivot[2]), worldSpace=True)
                    cmds.addAttr(self.neckCtrlList[n], longName=self.dpUIinst.lang['c047_autoRotate'], attributeType='float', minValue=0, maxValue=1, defaultValue=self.autoRotateCalc(n), keyable=True)
                    neckARMDName = self.dpUIinst.lang['c047_autoRotate'][0].capitalize()+self.dpUIinst.lang['c047_autoRotate'][1:]
                    neckARMD = cmds.createNode('multiplyDivide', name=self.neckCtrlList[n]+"_"+neckARMDName+"_MD")
                    self.toIDList.append(neckARMD)
                    cmds.connectAttr(self.headCtrl+".rotateX", neckARMD+".input1X", force=True)
                    cmds.connectAttr(self.headCtrl+".rotateY", neckARMD+".input1Y", force=True)
                    cmds.connectAttr(self.headCtrl+".rotateZ", neckARMD+".input1Z", force=True)
                    cmds.connectAttr(self.neckCtrlList[n]+"."+self.dpUIinst.lang['c047_autoRotate'], neckARMD+".input2X", force=True)
                    cmds.connectAttr(self.neckCtrlList[n]+"."+self.dpUIinst.lang['c047_autoRotate'], neckARMD+".input2Y", force=True)
                    cmds.connectAttr(self.neckCtrlList[n]+"."+self.dpUIinst.lang['c047_autoRotate'], neckARMD+".input2Z", force=True)
                    cmds.connectAttr(neckARMD+".outputX", self.neckOrientGrp+".rotateX", force=True)
                    if self.rigType == dpBaseClass.RigType.quadruped:
                        cmds.connectAttr(neckARMD+".outputZ", self.neckOrientGrp+".rotateY", force=True)
                        quadrupedRotYZFixMD = cmds.createNode('multiplyDivide', name=self.neckCtrlList[n]+"_"+neckARMDName+"_YZ_Fix_MD")
                        cmds.connectAttr(neckARMD+".outputY", quadrupedRotYZFixMD+".input1X", force=True)
                        cmds.setAttr(quadrupedRotYZFixMD+".input2X", -1)
                        cmds.connectAttr(quadrupedRotYZFixMD+".outputX", self.neckOrientGrp+".rotateZ", force=True)
                    else:
                        cmds.connectAttr(neckARMD+".outputY", self.neckOrientGrp+".rotateY", force=True)
                        cmds.connectAttr(neckARMD+".outputZ", self.neckOrientGrp+".rotateZ", force=True)
                
                # mount controls hierarchy:
                cmds.parent(self.zeroCtrlList[3], self.jawCtrl, absolute=True) #chinCtrl
                cmds.parent(self.zeroCtrlList[4], self.zeroCtrlList[6], self.chinCtrl, absolute=True) #chewCtrl, lowerLipCtrl
                cmds.parent(self.zeroCtrlList[5], self.zeroCtrlList[7], self.upperJawCtrl, absolute=True) #upperLipCtrl, upperHeadCtrl
                
                # jaw follow sub head or root ctrl (using worldRef)
                jawParentConst = cmds.parentConstraint(self.headSubCtrl, self.worldRef, self.zeroCtrlList[2], maintainOffset=True, name=self.zeroCtrlList[2]+"_PaC")[0]
                cmds.setAttr(jawParentConst+".interpType", 2) #Shortest, no flip cause problem with scrubing
                cmds.addAttr(self.jawCtrl, longName=self.dpUIinst.lang['c032_follow'], attributeType="float", minValue=0, maxValue=1, defaultValue=1, keyable=True)
                cmds.connectAttr(self.jawCtrl+"."+self.dpUIinst.lang['c032_follow'], jawParentConst+"."+self.headSubCtrl+"W0", force=True)
                jawFollowRev = cmds.createNode("reverse", name=self.jawCtrl+"_Rev")
                cmds.connectAttr(self.jawCtrl+"."+self.dpUIinst.lang['c032_follow'], jawFollowRev+".inputX", force=True)
                cmds.connectAttr(jawFollowRev+".outputX", jawParentConst+"."+self.worldRef+"W1", force=True)
                cmds.scaleConstraint(self.headSubCtrl, self.zeroCtrlList[2], maintainOffset=True, name=self.zeroCtrlList[2]+"_ScC")[0]
                
                # setup jaw move:
                # jaw open:
                self.setupJawMove(self.jawCtrl, "c108_open", True, "Y", "c049_intensity", createOutput=True)
                self.setupJawMove(self.jawCtrl, "c108_open", True, "Z", "c049_intensity")
                # jaw close:
                self.setupJawMove(self.jawCtrl, "c109_close", False, "Y", "c049_intensity", createOutput=True)
                self.setupJawMove(self.jawCtrl, "c109_close", False, "Z", "c049_intensity")
                # upper lid close:
                self.setupJawMove(self.upperLipCtrl, "c109_close", False, "Y", "c039_lip")
                self.setupJawMove(self.upperLipCtrl, "c109_close", False, "Z", "c039_lip")
                # lower lid close:
                self.setupJawMove(self.lowerLipCtrl, "c109_close", False, "Y", "c039_lip", invertRot=True)
                self.setupJawMove(self.lowerLipCtrl, "c109_close", False, "Z", "c039_lip")
                
                # set jaw move and lips calibrate default values:
                cmds.setAttr(self.jawCtrl+"."+self.dpUIinst.lang['c108_open'].lower()+self.dpUIinst.lang['c110_start'].capitalize()+"Rotation", 5)
                cmds.setAttr(self.jawCtrl+"."+self.dpUIinst.lang['c108_open'].lower()+self.dpUIinst.lang['c111_calibrate']+"Y", -2)
                cmds.setAttr(self.jawCtrl+"."+self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Z", 0)
                cmds.setAttr(self.jawCtrl+"."+self.dpUIinst.lang['c108_open'].lower()+self.dpUIinst.lang['c111_calibrate']+self.dpUIinst.lang['c112_output'], 30)
                cmds.setAttr(self.jawCtrl+"."+self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+self.dpUIinst.lang['c112_output'], -10)
                cmds.setAttr(self.upperLipCtrl+"."+self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Z", 2)
                cmds.setAttr(self.lowerLipCtrl+"."+self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Y", 0)
                cmds.setAttr(self.lowerLipCtrl+"."+self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Z", 2)
                
                # upper lip follows lower lip:
                cmds.addAttr(self.upperLipCtrl, longName=self.dpUIinst.lang['c032_follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                upperLipConst = cmds.parentConstraint(self.upperJawCtrl, self.lowerLipCtrl, self.zeroCtrlList[5], maintainOffset=True, name=self.zeroCtrlList[5]+"_PaC")[0]
                upperLipRev = cmds.createNode("reverse", name=self.zeroCtrlList[5]+"_Follow_Rev")
                cmds.connectAttr(self.upperLipCtrl+"."+self.dpUIinst.lang['c032_follow'], upperLipRev+".inputX", force=True)
                cmds.connectAttr(self.upperLipCtrl+"."+self.dpUIinst.lang['c032_follow'], upperLipConst+"."+self.lowerLipCtrl+"W1", force=True)
                cmds.connectAttr(upperLipRev+".outputX", upperLipConst+"."+self.upperJawCtrl+"W0", force=True)

                # left side lip:
                lLipParentConst = cmds.parentConstraint(self.jawCtrl, self.upperJawCtrl, self.lLipGrp, maintainOffset=True, name=self.lLipGrp+"_PaC")[0]
                cmds.setAttr(lLipParentConst+".interpType", 2)
                cmds.addAttr(self.lCornerLipCtrl, longName=self.dpUIinst.lang['c032_follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.5, keyable=True)
                cmds.connectAttr(self.lCornerLipCtrl+'.'+self.dpUIinst.lang['c032_follow'], lLipParentConst+"."+self.jawCtrl+"W0", force=True)
                self.lLipRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_"+self.dpUIinst.lang['p002_left']+"_"+self.dpUIinst.lang['c039_lip']+"_Rev")
                cmds.connectAttr(self.lCornerLipCtrl+'.'+self.dpUIinst.lang['c032_follow'], self.lLipRevNode+".inputX", force=True)
                cmds.connectAttr(self.lLipRevNode+'.outputX', lLipParentConst+"."+self.upperJawCtrl+"W1", force=True)
                cmds.scaleConstraint(self.upperJawCtrl, self.lLipGrp, maintainOffset=True, name=self.lLipGrp+"_ScC")[0]
                # right side lip:
                rLipParentConst = cmds.parentConstraint(self.jawCtrl, self.upperJawCtrl, self.rLipGrp, maintainOffset=True, name=self.rLipGrp+"_PaC")[0]
                cmds.setAttr(rLipParentConst+".interpType", 2)
                cmds.addAttr(self.rCornerLipCtrl, longName=self.dpUIinst.lang['c032_follow'], attributeType='float', minValue=0, maxValue=1, defaultValue=0.5, keyable=True)
                cmds.connectAttr(self.rCornerLipCtrl+'.'+self.dpUIinst.lang['c032_follow'], rLipParentConst+"."+self.jawCtrl+"W0", force=True)
                self.rLipRevNode = cmds.createNode('reverse', name=side+self.userGuideName+"_"+self.dpUIinst.lang['p003_right']+"_"+self.dpUIinst.lang['c039_lip']+"_Rev")
                cmds.connectAttr(self.rCornerLipCtrl+'.'+self.dpUIinst.lang['c032_follow'], self.rLipRevNode+".inputX", force=True)
                cmds.connectAttr(self.rLipRevNode+'.outputX', rLipParentConst+"."+self.upperJawCtrl+"W1", force=True)
                cmds.scaleConstraint(self.upperJawCtrl, self.rLipGrp, maintainOffset=True, name=self.rLipGrp+"_ScC")[0]
                self.toIDList.extend([self.headRevNode, jawFollowRev, upperLipRev, self.lLipRevNode, self.rLipRevNode])

                # articulation joint:
                if self.addArticJoint:
                    # neckBase
                    neckBaseJzt = self.utils.zeroOutJoints([self.neckJointList[0]])[0]
                    if self.addCorrective:
                        # corrective controls group
                        self.correctiveCtrlsGrp = cmds.group(name=side+self.userGuideName+"_Corrective_Grp", empty=True)
                        self.correctiveCtrlGrpList.append(self.correctiveCtrlsGrp)
                        neckHeadCalibratePresetList, invertList = self.getCalibratePresetList(s)
                        
                        # neck corrective
                        for n in range(0, self.nJoints):
                            if n == 0:
                                fatherJoint = neckBaseJzt
                            else:
                                fatherJoint = self.neckJointList[n-1]
                            correctiveNetList = [None]
                            correctiveNetList.append(self.setupCorrectiveNet(self.neckCtrlList[n], fatherJoint, self.neckJointList[n], neckCtrlBaseName+"_"+str(n)+"_YawRight", 2, 2, -80))
                            correctiveNetList.append(self.setupCorrectiveNet(self.neckCtrlList[n], fatherJoint, self.neckJointList[n], neckCtrlBaseName+"_"+str(n)+"_YawLeft", 2, 2, 80))
                            correctiveNetList.append(self.setupCorrectiveNet(self.neckCtrlList[n], fatherJoint, self.neckJointList[n], neckCtrlBaseName+"_"+str(n)+"_PitchUp", 0, 0, 80))
                            correctiveNetList.append(self.setupCorrectiveNet(self.neckCtrlList[n], fatherJoint, self.neckJointList[n], neckCtrlBaseName+"_"+str(n)+"_PitchDown", 0, 0, -80))
                            
                            articJntList = self.utils.articulationJoint(fatherJoint, self.neckJointList[n], 4, [(0.5*self.ctrlRadius, 0, 0), (-0.5*self.ctrlRadius, 0, 0), (0, 0, 0.5*self.ctrlRadius), (0, 0, -0.5*self.ctrlRadius)])
                            self.setupJcrControls(articJntList, s, self.jointLabelAdd, neckCtrlBaseName+"_"+str(n), correctiveNetList, neckHeadCalibratePresetList, invertList, [False, True, True, False, False])
                            if s == 1:
                                if self.addFlip:
                                    cmds.setAttr(articJntList[0]+".scaleX", -1)
                                    cmds.setAttr(articJntList[0]+".scaleY", -1)
                                    cmds.setAttr(articJntList[0]+".scaleZ", -1)
                            self.utils.setJointLabel(articJntList[0], s+self.jointLabelAdd, 18, self.userGuideName+"_"+self.dpUIinst.lang['c023_neck']+"_"+str(n)+"_Jar")

                        # head corrective
                        headCorrectiveNetList = [None]
                        headCorrectiveNetList.append(self.setupCorrectiveNet(self.headSubCtrl, self.neckJointList[-1], self.headJnt, side+self.userGuideName+"_"+self.dpUIinst.lang['c024_head']+"_YawRight", 2, 2, -80))
                        headCorrectiveNetList.append(self.setupCorrectiveNet(self.headSubCtrl, self.neckJointList[-1], self.headJnt, side+self.userGuideName+"_"+self.dpUIinst.lang['c024_head']+"_YawLeft", 2, 2, 80))
                        headCorrectiveNetList.append(self.setupCorrectiveNet(self.headSubCtrl, self.neckJointList[-1], self.headJnt, side+self.userGuideName+"_"+self.dpUIinst.lang['c024_head']+"_PitchUp", 0, 0, 80))
                        headCorrectiveNetList.append(self.setupCorrectiveNet(self.headSubCtrl, self.neckJointList[-1], self.headJnt, side+self.userGuideName+"_"+self.dpUIinst.lang['c024_head']+"_PitchDown", 0, 0, -80))
                        headCalibratePresetList, invertList = self.getCalibratePresetList(s)
                        articJntList = self.utils.articulationJoint(self.neckJointList[-1], self.headJnt, 4, [(0.5*self.ctrlRadius, 0, 0), (-0.5*self.ctrlRadius, 0, 0), (0, 0, 0.5*self.ctrlRadius), (0, 0, -0.5*self.ctrlRadius)])
                        self.setupJcrControls(articJntList, s, self.jointLabelAdd, side+self.userGuideName+"_"+self.dpUIinst.lang['c024_head'], headCorrectiveNetList, headCalibratePresetList, invertList, [False, True, True, False, False])
                        if s == 1:
                            if self.addFlip:
                                cmds.setAttr(articJntList[0]+".scaleX", -1)
                                cmds.setAttr(articJntList[0]+".scaleY", -1)
                                cmds.setAttr(articJntList[0]+".scaleZ", -1)
                    else:
                        articJntList = self.utils.articulationJoint(neckBaseJzt, self.neckJointList[0])
                        self.utils.setJointLabel(articJntList[0], s+self.jointLabelAdd, 18, self.userGuideName+"_00_"+self.dpUIinst.lang['c023_neck']+self.dpUIinst.lang['c106_base']+"_Jar")
                        cmds.rename(articJntList[0], side+self.userGuideName+"_00_"+self.dpUIinst.lang['c023_neck']+self.dpUIinst.lang['c106_base']+"_Jar")
                        articJntList = self.utils.articulationJoint(self.neckJointList[-1], self.headJnt)
                    
                    self.neckJointList.insert(0, neckBaseJzt)
                    cmds.parentConstraint(self.zeroNeckCtrlList[0], neckBaseJzt, maintainOffset=True, name=neckBaseJzt+"_PaC")
                    cmds.scaleConstraint(self.zeroNeckCtrlList[0], neckBaseJzt, maintainOffset=True, name=neckBaseJzt+"_ScC")
                    self.utils.setJointLabel(articJntList[0], s+self.jointLabelAdd, 18, self.userGuideName+"_01_"+self.dpUIinst.lang['c024_head']+self.dpUIinst.lang['c106_base']+"_Jar")
                    cmds.rename(articJntList[0], side+self.userGuideName+"_01_"+self.dpUIinst.lang['c024_head']+self.dpUIinst.lang['c106_base']+"_Jar")
                
                # hiding visibility attributes:
                self.ctrls.setLockHide([self.headCtrl, self.upperJawCtrl, self.upperHeadCtrl, self.jawCtrl, self.chinCtrl, self.chewCtrl, self.upperLipCtrl, self.lowerLipCtrl], ['v'], l=False)
                self.ctrls.setLockHide(self.neckCtrlList, ['v'], l=False)

                # arrange controllers hierarchy
                cmds.parent(self.zeroCtrlList[-1], self.zeroCtrlList[1], self.headCtrl, absolute=True) #headSubCtrl
                cmds.parent(self.zeroCtrlList[1], self.headSubCtrl, absolute=True) #upperJawCtrl
                # facial controls hierarchy
                if cmds.getAttr(self.moduleGrp+".facial"):
                    if cmds.getAttr(self.moduleGrp+".facialBrow"):
                        cmds.parent(lBrowCtrlGrp, rBrowCtrlGrp, self.upperHeadCtrl)
                        cmds.delete(cmds.parentConstraint(self.cvBrowLoc, lBrowCtrlGrp, maintainOffset=False))
                        cmds.delete(cmds.parentConstraint(self.cvBrowLoc, rBrowCtrlGrp, maintainOffset=False))
                        cmds.setAttr(rBrowCtrlGrp+".translateX", (-1*cmds.getAttr(rBrowCtrlGrp+".translateX")))
                        cmds.setAttr(rBrowCtrlGrp+".rotateY", 180)
                    if cmds.getAttr(self.moduleGrp+".facialEyelid"):
                        if self.connectUserType == self.bsType:
                            cmds.parent(lEyelidCtrlGrp, rEyelidCtrlGrp, self.upperHeadCtrl)
                            cmds.delete(cmds.parentConstraint(self.cvEyelidLoc, lEyelidCtrlGrp, maintainOffset=False))
                            cmds.delete(cmds.parentConstraint(self.cvEyelidLoc, rEyelidCtrlGrp, maintainOffset=False))
                            cmds.setAttr(rEyelidCtrlGrp+".translateX", (-1*cmds.getAttr(rEyelidCtrlGrp+".translateX")))
                    if cmds.getAttr(self.moduleGrp+".facialMouth"):
                        cmds.parent(lMouthCtrlGrp, rMouthCtrlGrp, self.upperJawCtrl)
                        cmds.delete(cmds.parentConstraint(self.cvMouthLoc, lMouthCtrlGrp, maintainOffset=False))
                        cmds.delete(cmds.parentConstraint(self.cvMouthLoc, rMouthCtrlGrp, maintainOffset=False))
                        cmds.setAttr(rMouthCtrlGrp+".translateX", (-1*cmds.getAttr(rMouthCtrlGrp+".translateX")))
                        cmds.setAttr(rMouthCtrlGrp+".rotateY", 180)
                    if cmds.getAttr(self.moduleGrp+".facialLips"):
                        cmds.parent(lipsCtrlGrp, self.upperJawCtrl)
                        cmds.delete(cmds.parentConstraint(self.cvLipsLoc, lipsCtrlGrp, maintainOffset=False))
                    if cmds.getAttr(self.moduleGrp+".facialSneer"):
                        cmds.parent(sneerCtrlGrp, self.upperJawCtrl)
                        cmds.delete(cmds.parentConstraint(self.cvSneerLoc, sneerCtrlGrp, maintainOffset=False))
                    if cmds.getAttr(self.moduleGrp+".facialGrimace"):
                        cmds.parent(grimaceCtrlGrp, self.chinCtrl)
                        cmds.delete(cmds.parentConstraint(self.cvGrimaceLoc, grimaceCtrlGrp, maintainOffset=False))
                        cmds.setAttr(grimaceCtrlGrp+".rotateX", 180)
                    if cmds.getAttr(self.moduleGrp+".facialFace"):
                        cmds.parent(faceCtrlGrp, self.headSubCtrl)
                        cmds.delete(cmds.parentConstraint(self.cvFaceLoc, faceCtrlGrp, maintainOffset=False))
                
                # calibration attributes:
                neckCalibrationList = [self.dpUIinst.lang['c047_autoRotate']]
                jawCalibrationList = [
                                    self.dpUIinst.lang['c108_open'].lower()+self.dpUIinst.lang['c111_calibrate']+"Y",
                                    self.dpUIinst.lang['c108_open'].lower()+self.dpUIinst.lang['c111_calibrate']+"Z",
                                    self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Y",
                                    self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Z",
                                    self.dpUIinst.lang['c108_open'].lower()+self.dpUIinst.lang['c111_calibrate']+self.dpUIinst.lang['c112_output'],
                                    self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+self.dpUIinst.lang['c112_output']
                ]
                lipCalibrationList = [
                                    self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Y",
                                    self.dpUIinst.lang['c109_close'].lower()+self.dpUIinst.lang['c111_calibrate']+"Z"
                ]
                self.ctrls.setStringAttrFromList(self.neckCtrlList[0], neckCalibrationList)
                self.ctrls.setStringAttrFromList(self.jawCtrl, jawCalibrationList)
                self.ctrls.setStringAttrFromList(self.upperLipCtrl, lipCalibrationList)
                self.ctrls.setStringAttrFromList(self.lowerLipCtrl, lipCalibrationList)
                
                # create a masterModuleGrp to be checked if this rig exists:
                self.hookSetup(side, [self.zeroNeckCtrlList[0], self.zeroCtrlList[2], self.zeroCtrlList[8], self.zeroCtrlList[9]], [self.neckJointList[0]], [self.worldRef])
                if self.addCorrective:
                    cmds.parent(self.correctiveCtrlsGrp, self.toCtrlHookGrp)
                
                # head deformer
                if cmds.getAttr(self.moduleGrp+".deformer"):
                    # collect nodes to be deformedBy this Head module:
                    deformedByList = headDefCtrlList + self.getDeformedByList(s) + facialCtrlList
                    self.dpHeadDeformer.dpHeadDeformer(side+self.userGuideName+"_"+self.dpUIinst.lang['c024_head'], [self.deformerCube], self.headSubCtrl, deformedByList)
                elif cmds.objExists(self.guideName+"_DeformerCube_MD"):
                    cmds.delete(self.guideName+"_DeformerCube_MD")

                # delete duplicated group for side (mirror):
                cmds.delete(side+self.userGuideName+'_'+self.mirrorGrp)

                self.utils.addCustomAttr([self.lLipGrp, self.rLipGrp, self.headOrientGrp, self.worldRef], self.utils.ignoreTransformIOAttr)
                if self.correctiveCtrlGrpList:
                    self.utils.addCustomAttr(self.correctiveCtrlGrpList, self.utils.ignoreTransformIOAttr)
                self.dpUIinst.customAttr.addAttr(0, [self.toStaticHookGrp], descendents=True) #dpID
                
            # connect to facial controllers to blendShapes or facial joints
            if cmds.getAttr(self.moduleGrp+".facial"):
                if self.connectUserType == self.bsType:
                    self.dpFacialConnect.dpConnectToBlendShape()
                else:
                    self.dpFacialConnect.dpConnectToJoints()

            # finalize this rig:
            self.serializeGuide()
            self.integratingInfo()
            cmds.select(clear=True)
        # delete UI (moduleLayout), GUIDE and moduleInstance namespace:
        self.deleteModule()
        self.renameUnitConversion()
        self.dpUIinst.customAttr.addAttr(0, self.toIDList) #dpID
    
    
    def dpCreateFacialCtrl(self, side, sideName, ctrlName, cvCtrl, attrList, rotVector=(0, 0, 0), lockX=False, lockY=False, lockZ=False, limitX=True, limitY=True, limitZ=True, directConnection=False, color='yellow', headDefInfluence=False, jawDefInfluence=False, addTranslateY=False, limitMinY=False, invertZ=False, *args):
        """ Important function to receive called parameters and create the specific asked control.
            Convention:
                transfList = ["tx", "tx", "ty", "ty", "tz", "tz]
                axisDirectionList = [-1, 1, -1, 1, -1, 1] # neg, pos, neg, pos, neg, pos
            Returns the created Facial control and its zeroOut group.
        """
        # declaring variables:
        fCtrl = None
        fCtrlGrp = None
        calibrationList = []
        transfList = ["tx", "tx", "ty", "ty", "tz", "tz"]
        # naming:
        ctrlName = side+self.userGuideName+"_"+ctrlName
        if sideName:
            ctrlName = sideName+"_"+ctrlName
        fCtrlName = ctrlName+"_Ctrl"
        # skip if already there is this ctrl object:
        if cmds.objExists(fCtrlName):
            return None, None
        else:
            # create control calling dpControls function:
            fCtrl = self.ctrls.cvControl(cvCtrl, fCtrlName, r=1, d=0, rot=rotVector)
            # add head or jaw influence attribute
            if headDefInfluence:
                self.ctrls.addDefInfluenceAttrs(fCtrl, 1)                
            if jawDefInfluence:
                self.ctrls.addDefInfluenceAttrs(fCtrl, 2)
            # ctrl zeroOut grp and color:
            fCtrlGrp = self.utils.zeroOut([fCtrl])[0]
            self.ctrls.colorShape([fCtrl], color)
            # lock or limit XYZ axis:
            self.dpLockLimitAttr(fCtrl, ctrlName, [lockX, lockY, lockZ], [limitX, limitY, limitZ], limitMinY)
            self.ctrls.setLockHide([fCtrl], ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v', 'ro'])
            scaleFactorValue = self.facialFactor*self.ctrlRadius
            cmds.addAttr(fCtrl, longName="scaleFactor", attributeType="float", defaultValue=scaleFactorValue, minValue=0.001)
            cmds.connectAttr(fCtrl+".scaleFactor", fCtrlGrp+".scaleX", force=True)
            cmds.connectAttr(fCtrl+".scaleFactor", fCtrlGrp+".scaleY", force=True)
            if invertZ: # grimace hack to invert front and back values from Z axis
                invZMD = cmds.createNode("multiplyDivide", name=ctrlName+"_InvZ_MD")
                self.toIDList.append(invZMD)
                cmds.setAttr(invZMD+".input2Z", -1)
                cmds.connectAttr(fCtrl+".scaleFactor", invZMD+".input1Z", force=True)
                cmds.connectAttr(invZMD+".outputZ", fCtrlGrp+".scaleZ", force=True)
            else:
                cmds.connectAttr(fCtrl+".scaleFactor", fCtrlGrp+".scaleZ", force=True)
            # start work with custom attributes
            facialAttrList = []
            if attrList:
                for a, attr in enumerate(attrList):
                    if not attr == None:
                        ctrlAttr = attr
                        if sideName:
                            ctrlAttr = sideName+"_"+attr
                        facialAttrList.append(ctrlAttr)
                        if directConnection:
                            cmds.addAttr(fCtrl, longName=attr, attributeType="float", defaultValue=0, minValue=0, maxValue=1)
                            cmds.setAttr(fCtrl+"."+attr, keyable=True)
                        else:
                            cmds.addAttr(fCtrl, longName=ctrlAttr, attributeType="float", defaultValue=0)
                            calibrateMD = cmds.createNode("multiplyDivide", name=ctrlName+"_"+attr+"_Calibrate_MD")
                            clp = cmds.createNode("clamp", name=ctrlName+"_"+attr+"_Clp")
                            invMD = cmds.createNode("multiplyDivide", name=ctrlName+"_"+attr+"_Invert_MD")
                            self.toIDList.extend([calibrateMD, clp, invMD])
                            if a == 0 or a == 2 or a == 4: #negative
                                cmds.setAttr(clp+".minR", -1000)
                                cmds.setAttr(invMD+".input2X", -1)
                            else: #positive
                                cmds.setAttr(clp+".maxR", 1000)
                            # connect nodes:
                            cmds.connectAttr(fCtrl+"."+transfList[a], calibrateMD+".input1X", force=True)
                            if a == 0 or a == 1: # -x or +x
                                cmds.connectAttr(fCtrl+"."+self.calibrateName+"TX", calibrateMD+".input2X", force=True)
                                if not self.calibrateName+"TX" in calibrationList:
                                    calibrationList.append(self.calibrateName+"TX")
                            elif a == 2 or a == 3: # -y or +y
                                cmds.connectAttr(fCtrl+"."+self.calibrateName+"TY", calibrateMD+".input2X", force=True)
                                if not self.calibrateName+"TY" in calibrationList:
                                    calibrationList.append(self.calibrateName+"TY")
                            else: # -z or +z
                                cmds.connectAttr(fCtrl+"."+self.calibrateName+"TZ", calibrateMD+".input2X", force=True)
                                if not self.calibrateName+"TZ" in calibrationList:
                                    calibrationList.append(self.calibrateName+"TZ")
                            if addTranslateY: #useful for Sneer and Grimace
                                integrateTYPMA = cmds.createNode("plusMinusAverage", name=ctrlName+"_"+attr+"_TY_PMA")
                                self.toIDList.append(integrateTYPMA)
                                cmds.connectAttr(calibrateMD+".outputX", integrateTYPMA+".input1D[0]", force=True)
                                if not "Front" in attr:
                                    cmds.connectAttr(fCtrl+".translateY", integrateTYPMA+".input1D[1]", force=True)
                                cmds.connectAttr(integrateTYPMA+".output1D", clp+".input.inputR", force=True)
                                if "R_" in attr: #hack to set operation as substract in PMA node for Right side
                                    cmds.setAttr(integrateTYPMA+".operation", 2)
                                cmds.setAttr(fCtrl+"."+self.calibrateName+"TY", lock=True)
                            else:
                                cmds.connectAttr(calibrateMD+".outputX", clp+".input.inputR", force=True)
                            cmds.connectAttr(clp+".outputR", invMD+".input1X", force=True)
                            cmds.connectAttr(invMD+".outputX", fCtrl+"."+ctrlAttr, force=True)
                            cmds.setAttr(fCtrl+"."+ctrlAttr, lock=True)
            if facialAttrList:
                self.ctrls.setStringAttrFromList(fCtrl, facialAttrList, "facialList")
            if calibrationList:
                self.ctrls.setStringAttrFromList(fCtrl, calibrationList)
        return fCtrl, fCtrlGrp
    
    
    def dpLockLimitAttr(self, fCtrl, ctrlName, lockList, limitList, limitMinY, *args):
        """ Lock or limit attributes for XYZ.
        """
        for i, axis in enumerate(self.axisList):
            if lockList[i]:
                cmds.setAttr(fCtrl+".translate"+axis, lock=True, keyable=False)
            else:
                # add calibrate attributes:
                cmds.addAttr(fCtrl, longName=self.calibrateName+"T"+axis, attributeType="float", defaultValue=1, minValue=0.001)
                if limitList[i]:
                    if i == 0: #X
                        cmds.transformLimits(fCtrl, enableTranslationX=(1, 1))
                    elif i == 1: #Y
                        cmds.transformLimits(fCtrl, enableTranslationY=(1, 1))
                    else: #Z
                        cmds.transformLimits(fCtrl, enableTranslationZ=(1, 1))
                    self.dpLimitTranslate(fCtrl, ctrlName, axis, limitMinY)

    
    def dpLimitTranslate(self, fCtrl, ctrlName, axis, limitMinY=False, *args):
        """ Create a hyperbolic setup to limit min and max value for translation of the control.
            Resuming it's just divide 1 by the calibrate value.
        """
        hyperboleTLimitMD = cmds.createNode("multiplyDivide", name=ctrlName+"_LimitT"+axis+"_MD")
        hyperboleInvMD = cmds.createNode("multiplyDivide", name=ctrlName+"_LimitT"+axis+"_Inv_MD")
        self.toIDList.extend([hyperboleTLimitMD, hyperboleInvMD])
        cmds.setAttr(hyperboleTLimitMD+".input1X", 1)
        cmds.setAttr(hyperboleTLimitMD+".operation", 2)
        cmds.setAttr(hyperboleInvMD+".input2X", -1)
        cmds.connectAttr(fCtrl+"."+self.calibrateName+"T"+axis, hyperboleTLimitMD+".input2X", force=True)
        cmds.connectAttr(hyperboleTLimitMD+".outputX", fCtrl+".maxTransLimit.maxTrans"+axis+"Limit", force=True)
        cmds.connectAttr(hyperboleTLimitMD+".outputX", hyperboleInvMD+".input1X", force=True)
        if not limitMinY:
            cmds.connectAttr(hyperboleInvMD+".outputX", fCtrl+".minTransLimit.minTrans"+axis+"Limit", force=True)
        else:
            cmds.transformLimits(fCtrl, translationY=(0, 1))
    

    def dpChangeType(self, *args):
        """ Get and return the user selected type of controls.
            Change interface to be more clear.
        """
        typeSelectedRadioButton = cmds.radioCollection(self.facialTypeRC, query=True, select=True)
        self.connectUserType = cmds.radioButton(typeSelectedRadioButton, query=True, annotation=True)
        if self.connectUserType == self.bsType:
            cmds.setAttr(self.moduleGrp+".connectUserType", 0)
        elif self.connectUserType == self.jointsType:
            cmds.setAttr(self.moduleGrp+".connectUserType", 1)
    
    
    def getDeformedByList(self, s, *args):
        """ Returns the defomedBy list for this Head module based in the integrated hook dictionary.
        """
        guideList, resultList = [], []
        for item in self.dpUIinst.hookDic.keys():
            if self.guideName in self.dpUIinst.hookDic[item]['fatherGuide']:
                if not item in guideList:
                    guideList.append(item.split(":")[0])
                    if self.dpUIinst.hookDic[item]['childrenList']:
                        for child in self.dpUIinst.hookDic[item]['childrenList']:
                            if not child in guideList:
                                guideList.append(child.split(":")[0])
        if guideList:
            allList = cmds.ls(selection=False, type="transform")
            for node in allList:
                if cmds.objExists(node+".guideSource"):
                    guideSource = cmds.getAttr(node+".guideSource")
                    if guideSource.split(":")[0] in guideList:
                        if not node in resultList:
                            if self.mirrorAxis != 'off':
                                if node.startswith(self.sideList[s]):
                                    resultList.append(node)
                            else:
                                resultList.append(node)
        return resultList


    def integratingInfo(self, *args):
        dpBaseClass.StartClass.integratingInfo(self)
        """ This method will create a dictionary with informations about integrations system between modules.
        """
        self.integratedActionsDic = {
                                    "module": {
                                                "worldRefList"         : self.worldRefList,
                                                "upperCtrlList"        : self.upperCtrlList,
                                                "ctrlList"             : self.aCtrls,
                                                "InnerCtrls"           : self.aInnerCtrls,
                                                "lCtrls"               : self.aLCtrls,
                                                "rCtrls"               : self.aRCtrls,
                                                "correctiveCtrlGrpList": self.correctiveCtrlGrpList,
                                                "upperJawCtrlList"     : self.upperJawCtrlList
                                              }
                                    }
