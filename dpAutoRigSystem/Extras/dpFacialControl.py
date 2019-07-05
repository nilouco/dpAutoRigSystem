# importing libraries:
import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import dpAutoRigSystem.Modules.Library.dpControls as ctrls

# global variables to this module:
CLASS_NAME = "FacialControl"
TITLE = "m085_facialCtrl"
DESCRIPTION = "m086_facialCtrlDesc"
ICON = "/Icons/dp_facialCtrl.png"


BSNAME = "Head_Recept_BS"
FACIAL_CTRLS_GRP = "Facial_Ctrls_Grp"
BROW_TGTLIST = ["BrowFrown", "BrowSad", "BrowDown", "BrowUp"]
EYELID_TGTLIST = [None, None, "EyelidsClose", "EyelidsOpen"]
MOUTH_TGTLIST = ["MouthNarrow", "MouthWide", "MouthSad", "MouthSmile"]
LIPS_TGTLIST = ["Pucker", "LipsOpen", "LipsDown", "LipsUp"]
SNEER_TGTLIST = ["R_Sneer", "L_Sneer", None, None]
GRIMACE_TGTLIST = ["R_Grimace", "L_Grimace", None, None]
FACE_TGTLIST = ["L_Puff", "R_Puff", "AAA", "OOO", "UUU", "FFF", "MMM"]


DPFC_VERSION = "1.0"

class FacialControl():
    def __init__(self, *args, **kwargs):
        # call main function
        self.dpFacialControlUI(self)
        self.bsNode = None
        self.dpLoadTgtList(BSNAME)
    
    
    def dpFacialControlUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        # creating targetMirrorUI Window:
        if cmds.window('dpFacialControlWindow', query=True, exists=True):
            cmds.deleteUI('dpFacialControlWindow', window=True)
        facialCtrl_winWidth  = 380
        facialCtrl_winHeight = 450
        dpFacialControlWin = cmds.window('dpFacialControlWindow', title="Facial Control 1.0", widthHeight=(facialCtrl_winWidth, facialCtrl_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)

        # creating layout:
        facialCtrlLayout = cmds.columnLayout('facialCtrlLayout', columnOffset=("left", 10))
        cmds.text(label="Facial controls and attributes to create:", height=30, parent=facialCtrlLayout)
        
        doubleCBLayout = cmds.rowColumnLayout('doubleCBLayout', numberOfColumns=2, columnWidth=[(1, 70), (2, 300)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 20)], parent=facialCtrlLayout)
        
        self.browCB = cmds.checkBox('browCB', label="Brow", value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(BROW_TGTLIST), parent=doubleCBLayout)
        
        self.eyelidCB = cmds.checkBox('eyelidCB', label="Eyelid", value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(EYELID_TGTLIST[2:]), parent=doubleCBLayout)
        
        self.mouthCB = cmds.checkBox('mouthCB', label="Mouth", value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(MOUTH_TGTLIST), parent=doubleCBLayout)
        
        self.lipsCB = cmds.checkBox('lipsCB', label="Lips", value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(LIPS_TGTLIST), parent=doubleCBLayout)
        
        self.sneerCB = cmds.checkBox('sneerCB', label="Sneer", value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(SNEER_TGTLIST[:2]), parent=doubleCBLayout)
        
        self.grimaceCB = cmds.checkBox('grimaceCB', label="Grimace", value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(GRIMACE_TGTLIST[:2]), parent=doubleCBLayout)
        
        self.faceCB = cmds.checkBox('faceCB', label="Face", value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(FACE_TGTLIST), parent=doubleCBLayout)
        
        cmds.separator(height=20, style="in", horizontal=True, parent=facialCtrlLayout)
        self.connectCB = cmds.checkBox("connectCB", label="Try connect facial control attributes to BlendShape node", value=1, height=30, changeCommand=self.dpChangeConnectCB, parent=facialCtrlLayout)
        doubleLayout = cmds.rowColumnLayout('doubleLayout', numberOfColumns=2, columnWidth=[(1, 120), (2, 180)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 20)], parent=facialCtrlLayout)
        self.loadBSButton = cmds.button("loadBSButton", label="Load BlendShape >", annotation="Load the BlendShape Node here in order to connect controls attributes.", backgroundColor=(0.6, 0.6, 1.0), width=120, command=self.dpLoadBSNode, parent=doubleLayout)
        self.bsNodeTextField = cmds.textField('bsNodeTextField', width=160, text='', editable=False, parent=doubleLayout)
        
        tgtListFoundLayout = cmds.columnLayout('tgtListFoundLayout', columnOffset=('left', 10), width=310, rowSpacing=4, parent=facialCtrlLayout)
        self.tgtListTxt = cmds.text("tgtListTxt", label="BlendShape target list found:", height=30, parent=tgtListFoundLayout)
        self.targetScrollList = cmds.textScrollList('targetScrollList', width=290, height=100, enable=True, parent=tgtListFoundLayout)
        cmds.text(label='', parent=tgtListFoundLayout)
        
        cmds.button(label="Create selected", annotation="Create selected facial controls.", width=290, backgroundColor=(0.6, 1.0, 0.6), command=self.dpSelectedCtrls, parent=tgtListFoundLayout)
        cmds.button(label="Create default package", annotation="Create default facial controls package.", width=290, backgroundColor=(1.0, 1.0, 0.6), command=self.dpSelectedCtrls, parent=tgtListFoundLayout)
        
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
        self.bsNode = BSNAME
        lBrowCtrl, lBrowCtrlGrp = self.dpCreateFacialCtrl("L", "Brow", "cvBrow", BROW_TGTLIST, False, False, True, True, False, True, "red")
        rBrowCtrl, rBrowCtrlGrp = self.dpCreateFacialCtrl("R", "Brow", "cvBrow", BROW_TGTLIST, False, False, True, True, False, True, "blue")
        if rBrowCtrlGrp:
            cmds.setAttr(rBrowCtrlGrp+".rotateY", 180)
        lEyelidCtrl, lEyelidCtrlGrp = self.dpCreateFacialCtrl("L", "Eyelid", "cvEyelid", EYELID_TGTLIST, True, False, False, True, False, True, "red")
        rEyelidCtrl, rEyelidCtrlGrp = self.dpCreateFacialCtrl("R", "Eyelid", "cvEyelid", EYELID_TGTLIST, True, False, False, True, False, True, "blue")
        lMouthCtrl, lMouthCtrlGrp = self.dpCreateFacialCtrl("L", "Mouth", "cvMouth", MOUTH_TGTLIST, False, False, False, False, False, True, "red")
        rMouthCtrl, rMouthCtrlGrp = self.dpCreateFacialCtrl("R", "Mouth", "cvMouth", MOUTH_TGTLIST, False, False, False, False, False, True, "blue")
        if rMouthCtrlGrp:
            cmds.setAttr(rMouthCtrlGrp+".rotateY", 180)
        lipsCtrl, lipsCtrlGrp = self.dpCreateFacialCtrl(None, "Lips", "cvLips", LIPS_TGTLIST, False, False, True, True, False, True, "yellow")
        sneerCtrl, sneerCtrlGrp = self.dpCreateFacialCtrl(None, "Sneer", "cvSneer", SNEER_TGTLIST, False, True, True, True, False, True, "cyan")
        grimaceCtrl, grimaceCtrlGrp = self.dpCreateFacialCtrl(None, "Grimace", "cvGrimace", GRIMACE_TGTLIST, False, True, True, True, False, True, "cyan")
        faceCtrl, faceCtrlGrp = self.dpCreateFacialCtrl(None, "Face", "cvFace", FACE_TGTLIST, True, True, True, True, True, True, "cyan")
    
    
    def dpSelectedCtrls(self, *args):
        """ Function to create selected facial controls checkboxes.
        """
        connectBS = cmds.checkBox(self.connectCB, query=True, value=True)
        if cmds.checkBox(self.browCB, query=True, value=True):
            lBrowCtrl, lBrowCtrlGrp = self.dpCreateFacialCtrl("L", "Brow", "cvBrow", BROW_TGTLIST, False, False, True, True, False, connectBS, "red")
            rBrowCtrl, rBrowCtrlGrp = self.dpCreateFacialCtrl("R", "Brow", "cvBrow", BROW_TGTLIST, False, False, True, True, False, connectBS, "blue")
            if rBrowCtrlGrp:
                cmds.setAttr(rBrowCtrlGrp+".rotateY", 180)
        if cmds.checkBox(self.eyelidCB, query=True, value=True):
            lEyelidCtrl, lEyelidCtrlGrp = self.dpCreateFacialCtrl("L", "Eyelid", "cvEyelid", EYELID_TGTLIST, True, False, False, True, False, connectBS, "red")
            rEyelidCtrl, rEyelidCtrlGrp = self.dpCreateFacialCtrl("R", "Eyelid", "cvEyelid", EYELID_TGTLIST, True, False, False, True, False, connectBS, "blue")
        if cmds.checkBox(self.mouthCB, query=True, value=True):
            lMouthCtrl, lMouthCtrlGrp = self.dpCreateFacialCtrl("L", "Mouth", "cvMouth", MOUTH_TGTLIST, False, False, False, False, False, connectBS, "red")
            rMouthCtrl, rMouthCtrlGrp = self.dpCreateFacialCtrl("R", "Mouth", "cvMouth", MOUTH_TGTLIST, False, False, False, False, False, connectBS, "blue")
            if rMouthCtrlGrp:
                cmds.setAttr(rMouthCtrlGrp+".rotateY", 180)
        if cmds.checkBox(self.lipsCB, query=True, value=True):
            lipsCtrl, lipsCtrlGrp = self.dpCreateFacialCtrl(None, "Lips", "cvLips", LIPS_TGTLIST, False, False, True, True, False, connectBS, "yellow")
        if cmds.checkBox(self.sneerCB, query=True, value=True):
            sneerCtrl, sneerCtrlGrp = self.dpCreateFacialCtrl(None, "Sneer", "cvSneer", SNEER_TGTLIST, False, True, True, True, False, connectBS, "cyan")
        if cmds.checkBox(self.grimaceCB, query=True, value=True):
            grimaceCtrl, grimaceCtrlGrp = self.dpCreateFacialCtrl(None, "Grimace", "cvGrimace", GRIMACE_TGTLIST, False, True, True, True, False, connectBS, "cyan")
        if cmds.checkBox(self.faceCB, query=True, value=True):
            faceCtrl, faceCtrlGrp = self.dpCreateFacialCtrl(None, "Face", "cvFace", FACE_TGTLIST, True, True, True, True, True, connectBS, "cyan")
        
    
    def dpCreateFacialCtrl(self, side, ctrlName, cvCtrl, attrList, lockX=False, lockY=False, limitX=True, limitY=True, directConnection=False, connectBS=True, color='yellow', *args):
        """ Important function to receive called parameters and create the specific asked control.
            Convention:
                transfList = ["tx", "tx", "ty", "ty"]
                axisDirectionList = [-1, 1, -1, 1] # neg, pos, neg, pos
            Returns the created Facial control and its zeroOut group.
        """
        # declaring variables:
        fCtrl = None
        fCtrlGrp = None
        facialCtrlsGrp = FACIAL_CTRLS_GRP
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
            if cvCtrl == "cvBrow":
                fCtrl = ctrls.cvBrow(fCtrlName)
            elif cvCtrl == "cvEyelid":
                fCtrl = ctrls.cvEyelid(fCtrlName)
            elif cvCtrl == "cvMouth":
                fCtrl = ctrls.cvMouth(fCtrlName, rotateShape=-1)
            elif cvCtrl == "cvLips":
                fCtrl = ctrls.cvLips(fCtrlName)
            elif cvCtrl == "cvSneer":
                fCtrl = ctrls.cvSneer(fCtrlName)
            elif cvCtrl == "cvGrimace":
                fCtrl = ctrls.cvGrimace(fCtrlName)
            elif cvCtrl == "cvFace":
                fCtrl = ctrls.cvFace(fCtrlName)
            else:
                fCtrl = cmds.circle(name=fCtrlName, constructionHistory=False, object=True, normal=(0, 0, 1), degree=3, sections=8, radius=1)[0]
            # ctrl zeroOut grp and color:
            fCtrlGrp = cmds.group(fCtrl, name=fCtrlName+"_Grp")
            ctrls.colorShape([fCtrl], color)
            # lock or limit XY axis:
            if lockX:
                cmds.setAttr(fCtrl+".tx", lock=True, keyable=False)
            elif limitX:
                cmds.transformLimits(fCtrl, translationX=(-1, 1), enableTranslationX=(1, 1))
            if lockY:
                cmds.setAttr(fCtrl+".ty", lock=True, keyable=False)
            elif limitY:
                cmds.transformLimits(fCtrl, translationY=(-1, 1), enableTranslationY=(1, 1))
            ctrls.setLockHide([fCtrl], ['tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
            # add calibrate attributes:
            if not lockX:
                cmds.addAttr(fCtrl, longName="calibrateTX", attributeType="float", defaultValue=1)
            if not lockY:
                cmds.addAttr(fCtrl, longName="calibrateTY", attributeType="float", defaultValue=1)
            # start work with custom attributes
            if attrList:
                for a, attr in enumerate(attrList):
                    if not attr == None:
                        if directConnection:
                            cmds.addAttr(fCtrl, longName=attr, attributeType="float", defaultValue=0, minValue=0, maxValue=1)
                            cmds.setAttr(fCtrl+"."+attr, keyable=True)
                        else:
                            cmds.addAttr(fCtrl, longName=attr, attributeType="float", defaultValue=0)
                            clp = cmds.createNode("clamp", name=ctrlName+"_"+attr+"_Clp")
                            invMD = cmds.createNode("multiplyDivide", name=ctrlName+"_"+attr+"_Invert_MD")
                            calibrateMD = cmds.createNode("multiplyDivide", name=ctrlName+"_"+attr+"_Calibrate_MD")
                            if a == 0 or a == 2: #negative
                                cmds.setAttr(clp+".minR", -1000)
                                cmds.setAttr(invMD+".input2X", -1)
                            else: #positive
                                cmds.setAttr(clp+".maxR", 1000)
                            # connect nodes:
                            cmds.connectAttr(fCtrl+"."+transfList[a], clp+".input.inputR", force=True)
                            cmds.connectAttr(clp+".outputR", invMD+".input1X", force=True)
                            cmds.connectAttr(invMD+".outputX", calibrateMD+".input1X", force=True)
                            cmds.connectAttr(calibrateMD+".outputX", fCtrl+"."+attr, force=True)
                            if a == 0 or a == 1:
                                cmds.connectAttr(fCtrl+".calibrateTX", calibrateMD+".input2X", force=True)
                            else:
                                cmds.connectAttr(fCtrl+".calibrateTY", calibrateMD+".input2X", force=True)
                        
                        # try to connect attributes into blendShape node:
                        if connectBS and self.bsNode:
                            for i, alias in enumerate(aliasList):
                                if not side == None:
                                    attr = side+"_"+attr
                                if attr in alias:
                                    try:
                                        cmds.connectAttr(fCtrl+"."+attr, self.bsNode+"."+alias, force=True)
                                    except:
                                        pass
                                    
            # parenting the hierarchy:
            if not cmds.objExists(facialCtrlsGrp):
                cmds.group(name=facialCtrlsGrp, empty=True)
            cmds.parent(fCtrlGrp, facialCtrlsGrp)
        
        cmds.select(facialCtrlsGrp)
        return fCtrl, fCtrlGrp
    
    
    
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
                        mel.eval("warning \"Select a BlendShape node, a mesh or a connected transform in order to load, please.\";")
                else:
                    mel.eval("warning \"Select a BlendShape node, a mesh or a connected transform in order to load, please.\";")
            else:
                mel.eval("warning \"Select a BlendShape node, a mesh or a connected transform in order to load, please.\";")
        else:
            mel.eval("warning \"Select a BlendShape node, a mesh or a connected transform in order to load, please.\";")
    
    
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