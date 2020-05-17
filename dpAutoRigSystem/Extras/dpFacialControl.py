# importing libraries:
import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import dpAutoRigSystem.Modules.Library.dpControls as dpControls

# global variables to this module:
CLASS_NAME = "FacialControl"
TITLE = "m085_facialCtrl"
DESCRIPTION = "m086_facialCtrlDesc"
ICON = "/Icons/dp_facialCtrl.png"


HEAD_BSNAME = "Head_Recept_BS"
BODY_BSNAME = "Body_Recept_BS"
BROW_TGTLIST = ["BrowFrown", "BrowSad", "BrowDown", "BrowUp"]
EYELID_TGTLIST = [None, None, "EyelidsClose", "EyelidsOpen"]
MOUTH_TGTLIST = ["MouthNarrow", "MouthWide", "MouthSad", "MouthSmile"]
LIPS_TGTLIST = ["Pucker", "LipsOpen", "LipsDown", "LipsUp"]
SNEER_TGTLIST = ["R_Sneer", "L_Sneer", None, None]
GRIMACE_TGTLIST = ["R_Grimace", "L_Grimace", None, None]
FACE_TGTLIST = ["L_Puff", "R_Puff", "AAA", "OOO", "UUU", "FFF", "MMM"]


DPFC_VERSION = "1.5"


class FacialControl():
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, *args, **kwargs):
        # defining variables:
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
        self.facialCtrlsGrp = self.langDic[self.langName]["c059_facial"]+"_Ctrls_Grp"
        self.headCtrl = self.langDic[self.langName]["c024_head"]+"_"+self.langDic[self.langName]["c024_head"]+"_Ctrl"
        # call main function
        self.dpFacialControlUI(self)
        self.bsNode = None
        if cmds.objExists(BODY_BSNAME):
            self.dpLoadTgtList(BODY_BSNAME)
        elif cmds.objExists(HEAD_BSNAME):
            self.dpLoadTgtList(HEAD_BSNAME)
    
    
    def dpCloseFacialControlWin(self, *args):
        """ close facial control window if it exists.
        """
        if cmds.window('dpFacialControlWindow', query=True, exists=True):
            cmds.deleteUI('dpFacialControlWindow', window=True)
    
    
    def dpFacialControlUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        # creating targetMirrorUI Window:
        self.dpCloseFacialControlWin()
        
        facialCtrl_winWidth  = 380
        facialCtrl_winHeight = 450
        dpFacialControlWin = cmds.window('dpFacialControlWindow', title=self.langDic[self.langName]["m085_facialCtrl"]+" "+DPFC_VERSION, widthHeight=(facialCtrl_winWidth, facialCtrl_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)

        # creating layout:
        facialCtrlLayout = cmds.columnLayout('facialCtrlLayout', columnOffset=("left", 10))
        cmds.text(label=self.langDic[self.langName]["m139_facialCtrlsAttr"], height=30, parent=facialCtrlLayout)
        
        doubleCBLayout = cmds.rowColumnLayout('doubleCBLayout', numberOfColumns=2, columnWidth=[(1, 70), (2, 300)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 20)], parent=facialCtrlLayout)
        
        self.browCB = cmds.checkBox('browCB', label=self.langDic[self.langName]["c060_brow"], value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(BROW_TGTLIST), parent=doubleCBLayout)
        
        self.eyelidCB = cmds.checkBox('eyelidCB', label=self.langDic[self.langName]["c042_eyelid"], value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(EYELID_TGTLIST[2:]), parent=doubleCBLayout)
        
        self.mouthCB = cmds.checkBox('mouthCB', label=self.langDic[self.langName]["c061_mouth"], value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(MOUTH_TGTLIST), parent=doubleCBLayout)
        
        self.lipsCB = cmds.checkBox('lipsCB', label=self.langDic[self.langName]["c062_lips"], value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(LIPS_TGTLIST), parent=doubleCBLayout)
        
        self.sneerCB = cmds.checkBox('sneerCB', label=self.langDic[self.langName]["c063_sneer"], value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(SNEER_TGTLIST[:2]), parent=doubleCBLayout)
        
        self.grimaceCB = cmds.checkBox('grimaceCB', label=self.langDic[self.langName]["c064_grimace"], value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(GRIMACE_TGTLIST[:2]), parent=doubleCBLayout)
        
        self.faceCB = cmds.checkBox('faceCB', label=self.langDic[self.langName]["c065_face"], value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(FACE_TGTLIST), parent=doubleCBLayout)
        
        cmds.separator(height=20, style="in", horizontal=True, parent=facialCtrlLayout)
        self.connectCB = cmds.checkBox("connectCB", label=self.langDic[self.langName]["m140_tryConnectFacial"], value=1, height=30, changeCommand=self.dpChangeConnectCB, parent=facialCtrlLayout)
        doubleLayout = cmds.rowColumnLayout('doubleLayout', numberOfColumns=2, columnWidth=[(1, 120), (2, 180)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 20)], parent=facialCtrlLayout)
        self.loadBSButton = cmds.button("loadBSButton", label=self.langDic[self.langName]["m141_loadBlendShape"]+" >", annotation="Load the BlendShape Node here in order to connect controls attributes.", backgroundColor=(0.6, 0.6, 1.0), width=120, command=self.dpLoadBSNode, parent=doubleLayout)
        self.bsNodeTextField = cmds.textField('bsNodeTextField', width=160, text='', editable=False, parent=doubleLayout)
        
        tgtListFoundLayout = cmds.columnLayout('tgtListFoundLayout', columnOffset=('left', 10), width=310, rowSpacing=4, parent=facialCtrlLayout)
        self.tgtListTxt = cmds.text("tgtListTxt", label=self.langDic[self.langName]["m142_targetListFound"], height=30, parent=tgtListFoundLayout)
        self.targetScrollList = cmds.textScrollList('targetScrollList', width=290, height=100, enable=True, parent=tgtListFoundLayout)
        cmds.text(label='', parent=tgtListFoundLayout)
        
        cmds.button(label=self.langDic[self.langName]["m143_createSelected"], annotation="Create selected facial controls.", width=290, backgroundColor=(0.6, 1.0, 0.6), command=self.dpSelectedCtrls, parent=tgtListFoundLayout)
        cmds.button(label=self.langDic[self.langName]["m144_createDefaltPackage"], annotation="Create default facial controls package.", width=290, backgroundColor=(1.0, 1.0, 0.6), command=self.dpCreateDefaultPackage, parent=tgtListFoundLayout)
        
        # call facialControlUI Window:
        cmds.showWindow(dpFacialControlWin)
    
    
    def dpChangeConnectCB(self, *args):
        """ Set values enable or disable when the user change the connect check box.
        """
        # get
        cbValue = cmds.checkBox(self.connectCB, query=True, value=True)
        # set
        cmds.button(self.loadBSButton, edit=True, enable=cbValue)
        cmds.textField(self.bsNodeTextField, edit=True, text="", enable=cbValue)
        cmds.text(self.tgtListTxt, edit=True, enable=cbValue)
        cmds.textScrollList(self.targetScrollList, edit=True, removeAll=True, enable=cbValue)
    
    
    def dpCreateDefaultPackage(self, *args):
        """ Function to create a package of facial controls we use as default.
        """
        if cmds.objExists(BODY_BSNAME):
            self.bsNode = BODY_BSNAME
        elif cmds.objExists(HEAD_BSNAME):
            self.bsNode = HEAD_BSNAME
        # creating controls:
        lBrowCtrl, lBrowCtrlGrp = self.dpCreateFacialCtrl("L", self.langDic[self.langName]["c060_brow"], "id_046_FacialBrow", BROW_TGTLIST, (0, 0, 0), False, False, True, True, False, True, "red")
        rBrowCtrl, rBrowCtrlGrp = self.dpCreateFacialCtrl("R", self.langDic[self.langName]["c060_brow"], "id_046_FacialBrow", BROW_TGTLIST, (0, 0, 0), False, False, True, True, False, True, "blue")
        lEyelidCtrl, lEyelidCtrlGrp = self.dpCreateFacialCtrl("L", self.langDic[self.langName]["c042_eyelid"], "id_047_FacialEyelid", EYELID_TGTLIST, (0, 0, 90), True, False, False, True, False, True, "red")
        rEyelidCtrl, rEyelidCtrlGrp = self.dpCreateFacialCtrl("R", self.langDic[self.langName]["c042_eyelid"], "id_047_FacialEyelid", EYELID_TGTLIST, (0, 0, 90), True, False, False, True, False, True, "blue")
        lMouthCtrl, lMouthCtrlGrp = self.dpCreateFacialCtrl("L", self.langDic[self.langName]["c061_mouth"], "id_048_FacialMouth", MOUTH_TGTLIST, (0, 0, -90), False, False, False, False, False, True, "red")
        rMouthCtrl, rMouthCtrlGrp = self.dpCreateFacialCtrl("R", self.langDic[self.langName]["c061_mouth"], "id_048_FacialMouth", MOUTH_TGTLIST, (0, 0, -90), False, False, False, False, False, True, "blue")
        lipsCtrl, lipsCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c062_lips"], "id_049_FacialLips", LIPS_TGTLIST, (0, 0, 0), False, False, True, True, False, True, "yellow")
        sneerCtrl, sneerCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c063_sneer"], "id_050_FacialSneer", SNEER_TGTLIST, (0, 0, 0), False, False, True, True, False, True, "cyan", True)
        grimaceCtrl, grimaceCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c064_grimace"], "id_051_FacialGrimace", GRIMACE_TGTLIST, (0, 0, 0), False, False, True, True, False, True, "cyan", True)
        faceCtrl, faceCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c065_face"], "id_052_FacialFace", FACE_TGTLIST, (0, 0, 0), True, True, True, True, True, True, "cyan")
        
        # positioning control groups:
        cmds.setAttr(rBrowCtrlGrp+".rotateY", 180)
        cmds.setAttr(rMouthCtrlGrp+".rotateY", 180)
        cmds.setAttr(grimaceCtrlGrp+".rotateX", 180)
        
        cmds.setAttr(lBrowCtrlGrp+".translateX", 4)
        cmds.setAttr(rBrowCtrlGrp+".translateX", -4)
        cmds.setAttr(lEyelidCtrlGrp+".translateX", 2)
        cmds.setAttr(rEyelidCtrlGrp+".translateX", -2)
        cmds.setAttr(lMouthCtrlGrp+".translateX", 3)
        cmds.setAttr(rMouthCtrlGrp+".translateX", -3)
        cmds.setAttr(faceCtrlGrp+".translateX", 10)
        
        cmds.setAttr(lBrowCtrlGrp+".translateY", 12)
        cmds.setAttr(rBrowCtrlGrp+".translateY", 12)
        cmds.setAttr(lEyelidCtrlGrp+".translateY", 10)
        cmds.setAttr(rEyelidCtrlGrp+".translateY", 10)
        cmds.setAttr(lMouthCtrlGrp+".translateY", 1.5)
        cmds.setAttr(rMouthCtrlGrp+".translateY", 1.5)
        cmds.setAttr(lipsCtrlGrp+".translateY", 1.5)
        cmds.setAttr(sneerCtrlGrp+".translateY", 2.5)
        cmds.setAttr(grimaceCtrlGrp+".translateY", 0.5)
        cmds.setAttr(faceCtrlGrp+".translateY", 2)
        
        cmds.setAttr(lBrowCtrlGrp+".translateZ", 13)
        cmds.setAttr(rBrowCtrlGrp+".translateZ", 13)
        cmds.setAttr(lEyelidCtrlGrp+".translateZ", 13)
        cmds.setAttr(rEyelidCtrlGrp+".translateZ", 13)
        cmds.setAttr(lMouthCtrlGrp+".translateZ", 13)
        cmds.setAttr(rMouthCtrlGrp+".translateZ", 13)
        cmds.setAttr(lipsCtrlGrp+".translateZ", 13)
        cmds.setAttr(sneerCtrlGrp+".translateZ", 13)
        cmds.setAttr(grimaceCtrlGrp+".translateZ", 13)
        
        # integrating to dpAutoRigSystem:
        if cmds.objExists(self.headCtrl):
            cmds.parent(self.facialCtrlsGrp, self.headCtrl, absolute=True)
            cmds.setAttr(self.facialCtrlsGrp+".tx", 0)
            cmds.setAttr(self.facialCtrlsGrp+".ty", 0)
            cmds.setAttr(self.facialCtrlsGrp+".tz", 0)
    
        # closes window:
        self.dpCloseFacialControlWin()
        
    
    def dpSelectedCtrls(self, *args):
        """ Function to create selected facial controls checkboxes.
        """
        connectBS = cmds.checkBox(self.connectCB, query=True, value=True)
        if cmds.checkBox(self.browCB, query=True, value=True):
            lBrowCtrl, lBrowCtrlGrp = self.dpCreateFacialCtrl("L", self.langDic[self.langName]["c060_brow"], "id_046_FacialBrow", BROW_TGTLIST, (0, 0, 0), False, False, True, True, False, connectBS, "red")
            rBrowCtrl, rBrowCtrlGrp = self.dpCreateFacialCtrl("R", self.langDic[self.langName]["c060_brow"], "id_046_FacialBrow", BROW_TGTLIST, (0, 0, 0), False, False, True, True, False, connectBS, "blue")
            if rBrowCtrlGrp:
                cmds.setAttr(rBrowCtrlGrp+".rotateY", 180)
        if cmds.checkBox(self.eyelidCB, query=True, value=True):
            lEyelidCtrl, lEyelidCtrlGrp = self.dpCreateFacialCtrl("L", self.langDic[self.langName]["c042_eyelid"], "id_047_FacialEyelid", EYELID_TGTLIST, (0, 0, 90), True, False, False, True, False, connectBS, "red")
            rEyelidCtrl, rEyelidCtrlGrp = self.dpCreateFacialCtrl("R", self.langDic[self.langName]["c042_eyelid"], "id_047_FacialEyelid", EYELID_TGTLIST, (0, 0, 90), True, False, False, True, False, connectBS, "blue")
        if cmds.checkBox(self.mouthCB, query=True, value=True):
            lMouthCtrl, lMouthCtrlGrp = self.dpCreateFacialCtrl("L", self.langDic[self.langName]["c061_mouth"], "id_048_FacialMouth", MOUTH_TGTLIST, (0, 0, -90), False, False, False, False, False, connectBS, "red")
            rMouthCtrl, rMouthCtrlGrp = self.dpCreateFacialCtrl("R", self.langDic[self.langName]["c061_mouth"], "id_048_FacialMouth", MOUTH_TGTLIST, (0, 0, -90), False, False, False, False, False, connectBS, "blue")
            if rMouthCtrlGrp:
                cmds.setAttr(rMouthCtrlGrp+".rotateY", 180)
        if cmds.checkBox(self.lipsCB, query=True, value=True):
            lipsCtrl, lipsCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c062_lips"], "id_049_FacialLips", LIPS_TGTLIST, (0, 0, 0), False, False, True, True, False, connectBS, "yellow")
        if cmds.checkBox(self.sneerCB, query=True, value=True):
            sneerCtrl, sneerCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c063_sneer"], "id_050_FacialSneer", SNEER_TGTLIST, (0, 0, 0), False, False, True, True, False, connectBS, "cyan", True)
        if cmds.checkBox(self.grimaceCB, query=True, value=True):
            grimaceCtrl, grimaceCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c064_grimace"], "id_051_FacialGrimace", GRIMACE_TGTLIST, (0, 0, 0), False, False, True, True, False, connectBS, "cyan", True)
            cmds.setAttr(grimaceCtrlGrp+".rotateX", 180)
        if cmds.checkBox(self.faceCB, query=True, value=True):
            faceCtrl, faceCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c065_face"], "id_052_FacialFace", FACE_TGTLIST, (0, 0, 0), True, True, True, True, True, connectBS, "cyan")
        
    
    def dpCreateFacialCtrl(self, side, ctrlName, cvCtrl, attrList, rotVector=(0, 0, 0), lockX=False, lockY=False, limitX=True, limitY=True, directConnection=False, connectBS=True, color='yellow', addTranslateY=False, *args):
        """ Important function to receive called parameters and create the specific asked control.
            Convention:
                transfList = ["tx", "tx", "ty", "ty"]
                axisDirectionList = [-1, 1, -1, 1] # neg, pos, neg, pos
            Returns the created Facial control and its zeroOut group.
        """
        # declaring variables:
        fCtrl = None
        fCtrlGrp = None
        
        transfList = ["tx", "tx", "ty", "ty"]
        # naming:
        if not side == None:
            ctrlName = side+"_"+ctrlName
        fCtrlName = ctrlName+"_Ctrl"
        # skip if already there is this ctrl object:
        if cmds.objExists(fCtrlName):
            return None, None
        else:
            if connectBS and self.bsNode:
                # validating blendShape node:
                if cmds.objectType(self.bsNode) == "blendShape":
                    aliasList = cmds.aliasAttr(self.bsNode, query=True)
            # create control calling dpControls function:
            fCtrl = self.ctrls.cvControl(cvCtrl, fCtrlName, d=0, rot=rotVector)
            
            # ctrl zeroOut grp and color:
            fCtrlGrp = cmds.duplicate(fCtrl, name=fCtrl+'_Grp')[0]
            allChildrenList = cmds.listRelatives(fCtrlGrp, allDescendents=True, children=True, fullPath=True)
            if allChildrenList:
                cmds.delete(allChildrenList)
            cmds.parent(fCtrl, fCtrlGrp, absolute=True)
            self.ctrls.colorShape([fCtrl], color)
            # lock or limit XY axis:
            if lockX:
                cmds.setAttr(fCtrl+".tx", lock=True, keyable=False)
            else:
                # add calibrate attributes:
                cmds.addAttr(fCtrl, longName="calibrateTX", attributeType="float", defaultValue=1, minValue=0.001)
                if limitX:
                    cmds.transformLimits(fCtrl, enableTranslationX=(1, 1))
                    self.dpLimitTranslate(fCtrl, ctrlName, "X")
            if lockY:
                cmds.setAttr(fCtrl+".ty", lock=True, keyable=False)
            else:
                cmds.addAttr(fCtrl, longName="calibrateTY", attributeType="float", defaultValue=1, minValue=0.001)
                if limitY:
                    cmds.transformLimits(fCtrl, enableTranslationY=(1, 1))
                    self.dpLimitTranslate(fCtrl, ctrlName, "Y")
            self.ctrls.setLockHide([fCtrl], ['tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
            # start work with custom attributes
            if attrList:
                for a, attr in enumerate(attrList):
                    if not attr == None:
                        if directConnection:
                            cmds.addAttr(fCtrl, longName=attr, attributeType="float", defaultValue=0, minValue=0, maxValue=1)
                            cmds.setAttr(fCtrl+"."+attr, keyable=True)
                        else:
                            cmds.addAttr(fCtrl, longName=attr, attributeType="float", defaultValue=0)
                            calibrateMD = cmds.createNode("multiplyDivide", name=ctrlName+"_"+attr+"_Calibrate_MD")
                            clp = cmds.createNode("clamp", name=ctrlName+"_"+attr+"_Clp")
                            invMD = cmds.createNode("multiplyDivide", name=ctrlName+"_"+attr+"_Invert_MD")
                            if a == 0 or a == 2: #negative
                                cmds.setAttr(clp+".minR", -1000)
                                cmds.setAttr(invMD+".input2X", -1)
                            else: #positive
                                cmds.setAttr(clp+".maxR", 1000)
                            # connect nodes:
                            cmds.connectAttr(fCtrl+"."+transfList[a], calibrateMD+".input1X", force=True)
                            if a == 0 or a == 1: # -x or +x
                                cmds.connectAttr(fCtrl+".calibrateTX", calibrateMD+".input2X", force=True)
                            else: # -y or +y
                                cmds.connectAttr(fCtrl+".calibrateTY", calibrateMD+".input2X", force=True)
                            if addTranslateY: #useful for Sneer and Grimace
                                integrateTYPMA = cmds.createNode("plusMinusAverage", name=ctrlName+"_"+attr+"_TY_PMA")
                                cmds.connectAttr(calibrateMD+".outputX", integrateTYPMA+".input1D[0]", force=True)
                                cmds.connectAttr(fCtrl+".translateY", integrateTYPMA+".input1D[1]", force=True)
                                cmds.connectAttr(integrateTYPMA+".output1D", clp+".input.inputR", force=True)
                                if "R_" in attr: #hack to set operation as substract in PMA node for Right side
                                    cmds.setAttr(integrateTYPMA+".operation", 2)
                                cmds.setAttr(fCtrl+".calibrateTY", lock=True)
                            else:
                                cmds.connectAttr(calibrateMD+".outputX", clp+".input.inputR", force=True)
                            cmds.connectAttr(clp+".outputR", invMD+".input1X", force=True)
                            cmds.connectAttr(invMD+".outputX", fCtrl+"."+attr, force=True)
                            cmds.setAttr(fCtrl+"."+attr, lock=True)
                        
                        # try to connect attributes into blendShape node:
                        if connectBS and self.bsNode:
                            addedSide = False
                            storedAttr = attr
                            for i, alias in enumerate(aliasList):
                                if not side == None and not addedSide:
                                    attr = side+"_"+attr
                                    addedSide = True
                                if attr in alias:
                                    try:
                                        cmds.connectAttr(fCtrl+"."+attr, self.bsNode+"."+alias, force=True)
                                    except:
                                        try:
                                            cmds.connectAttr(fCtrl+"."+storedAttr, self.bsNode+"."+alias, force=True)
                                        except:
                                            pass
                                    
            # parenting the hierarchy:
            if not cmds.objExists(self.facialCtrlsGrp):
                cmds.group(name=self.facialCtrlsGrp, empty=True)
            cmds.parent(fCtrlGrp, self.facialCtrlsGrp)
        
        cmds.select(self.facialCtrlsGrp)
        return fCtrl, fCtrlGrp
    
    
    def dpLimitTranslate(self, fCtrl, ctrlName, axis, *args):
        """ Create a hyperbolic setup to limit min and max value for translation of the control.
            Resuming it's just divide 1 by the calibrate value.
        """
        hyperboleTLimitMD = cmds.createNode("multiplyDivide", name=ctrlName+"_LimitT"+axis+"_MD")
        hyperboleInvMD = cmds.createNode("multiplyDivide", name=ctrlName+"_LimitT"+axis+"_Inv_MD")
        cmds.setAttr(hyperboleTLimitMD+".input1X", 1)
        cmds.setAttr(hyperboleTLimitMD+".operation", 2)
        cmds.setAttr(hyperboleInvMD+".input2X", -1)
        cmds.connectAttr(fCtrl+".calibrateT"+axis, hyperboleTLimitMD+".input2X", force=True)
        cmds.connectAttr(hyperboleTLimitMD+".outputX", fCtrl+".maxTransLimit.maxTrans"+axis+"Limit", force=True)
        cmds.connectAttr(hyperboleTLimitMD+".outputX", hyperboleInvMD+".input1X", force=True)
        cmds.connectAttr(hyperboleInvMD+".outputX", fCtrl+".minTransLimit.minTrans"+axis+"Limit", force=True)
    
    
    def dpLoadBSNode(self, *args):
        """ Load selected object as blendShapeNode
        """
        selectedList = cmds.ls(selection=True)
        if selectedList:
            if cmds.objectType(selectedList[0]) == "blendShape":
                cmds.textField(self.bsNodeTextField, edit=True, text=selectedList[0])
                self.dpLoadTgtList(selectedList[0])
                self.bsNode = selectedList[0]
            elif cmds.objectType(selectedList[0]) == "transform":
                meshList = cmds.listRelatives(selectedList[0], children=True, shapes=True, noIntermediate=True, type="mesh")
                if meshList:
                    bsNodeList = cmds.listConnections(meshList[0], type="blendShape")
                    if bsNodeList:
                        self.dpLoadTgtList(bsNodeList[0])
                        self.bsNode = bsNodeList[0]
                    else:
                        mel.eval("warning \""+self.langDic[self.langName]["e018_selectBlendShape"]+"\";")
                else:
                    mel.eval("warning \""+self.langDic[self.langName]["e018_selectBlendShape"]+"\";")
            else:
                mel.eval("warning \""+self.langDic[self.langName]["e018_selectBlendShape"]+"\";")
        else:
            mel.eval("warning \""+self.langDic[self.langName]["e018_selectBlendShape"]+"\";")
    
    
    def dpLoadTgtList(self, bsNodeName, *args):
        """ Add target list found in the blendShape node to target textScroll list
        """
        if cmds.objExists(bsNodeName):
            if cmds.objectType(bsNodeName) == "blendShape":
                tgtList = cmds.blendShape(bsNodeName, query=True, target=True)
                if tgtList:
                    cmds.textScrollList(self.targetScrollList, edit=True, removeAll=True)
                    cmds.textScrollList(self.targetScrollList, edit=True, append=tgtList)
                    cmds.textField(self.bsNodeTextField, edit=True, text=bsNodeName)
                    self.bsNode = bsNodeName