# importing libraries:
from maya import cmds
from maya import mel
import os
import json
from ..Modules.Library import dpControls

# global variables to this module:
CLASS_NAME = "FacialConnection"
TITLE = "m085_facialCtrl"
DESCRIPTION = "m086_facialCtrlDesc"
ICON = "/Icons/dp_facialCtrl.png"

HEAD_BSNAME = "Head_Recept_BS"
BODY_BSNAME = "Body_Recept_BS"
BROW_TGTLIST = ["BrowFrown", "BrowSad", "BrowDown", "BrowUp"]
EYELID_TGTLIST = [None, None, "EyelidsClose", "EyelidsOpen"]
MOUTH_TGTLIST = ["MouthNarrow", "MouthWide", "MouthSad", "MouthSmile"]
LIPS_TGTLIST = ["R_LipsSide", "L_LipsSide", "LipsDown", "LipsUp", "LipsBack", "LipsFront"]
SNEER_TGTLIST = ["R_Sneer", "L_Sneer", None, None, "UpperLipBack", "UpperLipFront"]
GRIMACE_TGTLIST = ["R_Grimace", "L_Grimace", None, None, "LowerLipBack", "LowerLipFront"]
FACE_TGTLIST = ["L_Puff", "R_Puff", "Pucker", "SoftSmile", "BigSmile", "AAA", "OOO", "UUU", "FFF", "MMM"]
TYPE_BS = "typeBS"
TYPE_JOINTS = "typeJoints"
MIDDLE = "Middle"
SIDED = "Sided"
PRESETS = "Presets"
FACIALPRESET = "FacialJoints"
HEADDEFINFLUENCE = "dpHeadDeformerInfluence"
JAWDEFINFLUENCE = "dpJawDeformerInfluence"

DP_FACIALCONNECTION_VERSION = 1.0


class FacialConnection(object):
    def __init__(self, dpUIinst, ui=True, *args, **kwargs):
        # defining variables:
        self.dpUIinst = dpUIinst
        self.utils = dpUIinst.utils
        self.ctrls = dpControls.ControlClass(self.dpUIinst)
        self.ui = ui
        self.headFacialCtrlsGrp = self.dpUIinst.lang["c024_head"]+"_"+self.dpUIinst.lang["c059_facial"]+"_Ctrls_Grp"
        self.headCtrl = self.dpGetHeadCtrl('id_093_HeadSub')
        self.upperHeadCtrl = self.dpGetHeadCtrl('id_081_HeadUpperHead')
        self.upperJawCtrl = self.dpGetHeadCtrl('id_069_HeadUpperJaw')
        self.chinCtrl = self.dpGetHeadCtrl('id_025_HeadChin')
        self.jntTargetList = []
        self.RmVNumber = 0
        self.targetList = [ "Base", "Recept", "Tweaks", 
                            "L_BrowUp", "L_BrowDown", "L_BrowSad", "L_BrowFrown", "L_EyelidsClose",  "L_EyelidsOpen",
                            "L_LipsSide", "L_MouthSmile", "L_MouthSad", "L_MouthWide", "L_MouthNarrow", "L_Sneer", "L_Grimace", "L_Puff",
                            "Pucker", "LipsUp", "LipsDown", "LipsFront", "LipsBack", "UpperLipFront", "UpperLipBack", "LowerLipFront", "LowerLipBack", "SoftSmile", "BigSmile", "AAA", "OOO", "UUU", "FFF", "MMM"
                            ]
        # redefining Tweaks variables:
        self.dpInitTweaksVariables()
        # call main function:
        if self.ui:
            self.dpFacialConnectionUI(self)

            TEMP = None
            if TEMP:
                # load fields:
                self.userType = TYPE_BS
                self.bsNode = None
                if cmds.objExists(BODY_BSNAME):
                    self.dpLoadBSTgtList(BODY_BSNAME)
                elif cmds.objExists(HEAD_BSNAME):
                    self.dpLoadBSTgtList(HEAD_BSNAME)
                self.dpLoadJointNode(self.tweaksNameList)

        # declaring gaming dictionary:
        self.tweaksDic = self.dpInitTweaksDic()
    
    
    def dpInitTweaksVariables(self, *args):
        # part names:
        mainName = self.dpUIinst.lang['c058_main']
        tweaksName = self.dpUIinst.lang['m081_tweaks']
        middleName = self.dpUIinst.lang['c029_middle']
        eyebrowName = self.dpUIinst.lang['c041_eyebrow']
        cornerName = self.dpUIinst.lang['c043_corner']
        upperName = self.dpUIinst.lang['c044_upper']
        lowerName = self.dpUIinst.lang['c045_lower']
        lipName = self.dpUIinst.lang['c039_lip']
        squintName = self.dpUIinst.lang['c054_squint']
        cheekName = self.dpUIinst.lang['c055_cheek']
        self.calibrateName = self.dpUIinst.lang["c111_calibrate"].lower()
        # eyebrows names:
        self.eyebrowMiddleName = tweaksName+"_"+middleName+"_"+eyebrowName
        self.eyebrowName1 = tweaksName+"_"+eyebrowName+"_01"
        self.eyebrowName2 = tweaksName+"_"+eyebrowName+"_02"
        self.eyebrowName3 = tweaksName+"_"+eyebrowName+"_03"
        # squints names:
        self.squintName1 = tweaksName+"_"+squintName+"_01"
        self.squintName2 = tweaksName+"_"+squintName+"_02"
        self.squintName3 = tweaksName+"_"+squintName+"_03"
        # cheeks names:
        self.cheekName1 = tweaksName+"_"+cheekName+"_01"
        # lip names:
        self.upperLipMiddleName = tweaksName+"_"+upperName+"_"+lipName+"_00"
        self.upperLipName1 = tweaksName+"_"+upperName+"_"+lipName+"_01"
        self.upperLipName2 = tweaksName+"_"+upperName+"_"+lipName+"_02"
        self.lowerLipMiddleName = tweaksName+"_"+lowerName+"_"+lipName+"_00"
        self.lowerLipName1 = tweaksName+"_"+lowerName+"_"+lipName+"_01"
        self.lowerLipName2 = tweaksName+"_"+lowerName+"_"+lipName+"_02"
        self.lipCornerName = tweaksName+"_"+cornerName+"_"+lipName
        # list:
        self.tweaksNameList = [self.eyebrowMiddleName, self.eyebrowName1, self.eyebrowName2, self.eyebrowName3, \
                                self.squintName1, self.squintName2, self.squintName3, \
                                self.cheekName1, \
                                self.upperLipMiddleName, self.upperLipName1, self.upperLipName2, self.lowerLipMiddleName, self.lowerLipName1, self.lowerLipName2, self.lipCornerName]
        self.tweaksNameStrList = ["eyebrowMiddleName", "eyebrowName1", "eyebrowName2", "eyebrowName3", \
                                "squintName1", "squintName2", "squintName3", \
                                "cheekName1", \
                                "upperLipMiddleName", "upperLipName1", "upperLipName2", "lowerLipMiddleName", "lowerLipName1", "lowerLipName2", "lipCornerName"]
    
    
    def dpInitTweaksDic(self, *args):
        """ Load FacialJoints json file.
            Read its content.
            Rebuild a dictionary changing string variables to current mounted language names.
            Return the presetContent
        """
        # load json file:
        presetContent = None
        file = FACIALPRESET+".json"
        # find current path:
        path = os.path.dirname(__file__)
        # hack in order to avoid "\\" from os.sep, then we need to use the replace string method:
        jsonPath = os.path.join(path, PRESETS, "").replace("\\", "/")
        fileDictionary = open(jsonPath + file, "r", encoding='utf-8')
        # read the json file content and store it in a dictionary:
        presetContent = json.loads(fileDictionary.read())
        # close the json file:
        fileDictionary.close()
        if presetContent:
            # rebuild dictionary using object variables:
            for storedAttr in list(presetContent):
                for sideName in list(presetContent[storedAttr]):
                    for toNodeName in list(presetContent[storedAttr][sideName]):
                        for i, item in enumerate(self.tweaksNameStrList):
                            if toNodeName == item:
                                presetContent[storedAttr][sideName][self.tweaksNameList[i]] = presetContent[storedAttr][sideName].pop(toNodeName)
                    if sideName == "MIDDLE":
                        presetContent[storedAttr][MIDDLE] = presetContent[storedAttr].pop(sideName)
                    elif sideName == "SIDED":
                        presetContent[storedAttr][SIDED] = presetContent[storedAttr].pop(sideName)
        return presetContent
    
    
    def dpGetHeadCtrl(self, id, *args):
        """ Find and return the headCtrl if it exists in the scene.
        """
        headCtrlList = self.ctrls.getControlNodeById(id)
        if headCtrlList:
            if cmds.objExists(headCtrlList[0]):
                return headCtrlList[0]
    
    
    def dpCloseFacialConnectionWin(self, *args):
        """ Close facial connection window if it exists.
        """
        if cmds.window('dpFacialConnectionWindow', query=True, exists=True):
            cmds.deleteUI('dpFacialConnectionWindow', window=True)
    
    
    def dpFacialConnectionUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        # creating targetMirrorUI Window:
        self.dpCloseFacialConnectionWin()
        
        facialCtrl_winWidth  = 180
        facialCtrl_winHeight = 100
        dpFacialControlWin = cmds.window('dpFacialConnectionWindow', title=self.dpUIinst.lang["m085_facialCtrl"]+" "+str(DP_FACIALCONNECTION_VERSION), widthHeight=(facialCtrl_winWidth, facialCtrl_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)

        # creating layout:
        facialCtrlLayout = cmds.columnLayout('facialCtrlLayout', columnOffset=("left", 10))
        cmds.button(label=self.dpUIinst.lang["m143_createSelected"], annotation="Create selected facial controls.", width=290, backgroundColor=(0.6, 0.6, 1.0), command=self.dpCreateTargets, parent=facialCtrlLayout)
        cmds.separator(height=20, style="in", horizontal=True, parent=facialCtrlLayout)
        cmds.button(label=self.dpUIinst.lang["m143_createSelected"], annotation="Create selected facial controls.", width=290, backgroundColor=(0.6, 1.0, 0.6), command=self.dpSelectedCtrls, parent=facialCtrlLayout)
        cmds.button(label=self.dpUIinst.lang["m144_createDefaltPackage"], annotation="Create default facial controls package.", width=290, backgroundColor=(1.0, 1.0, 0.6), command=self.dpCreateDefaultPackage, parent=facialCtrlLayout)
        
        # call facialControlUI Window:
        cmds.showWindow(dpFacialControlWin)
    

    def dpCreateTargets(self, fromMesh=None, baseName="Head", *args):
        """ Creates the default blendShape targets used in the system by default.
        """
        if not fromMesh:
            fromMeshList = cmds.ls(selection=True, type="transform")
            if fromMeshList:
                for n, node in enumerate(fromMeshList):
                    fromMeshChildrenList = cmds.listRelatives(fromMeshList[n], children=True, type="mesh")
                    if fromMeshChildrenList:
                        fromMesh = fromMeshList[n]
                        break
        if fromMesh:
            geoList = []
            prefix = baseName
            if self.ui:
                btContinue = self.dpUIinst.lang['i174_continue']
                btCancel = self.dpUIinst.lang['i132_cancel']
                result = cmds.promptDialog(
                        title=self.dpUIinst.lang['m006_name'],
                        message=self.dpUIinst.lang['i144_prefix']+":",
                        button=[btContinue, btCancel],
                        defaultButton=btContinue,
                        cancelButton=btCancel,
                        dismissString=btCancel)
                if result == btContinue:
                    prefix = cmds.promptDialog(query=True, text=True)
            if not prefix.endswith("_"):
                prefix = prefix+"_"
            prefix = prefix.capitalize()
            suffix = "_Tgt"
            facialGrp = cmds.group(empty=True, name=prefix+"Facial_Tgt_Grp")
            # create target meshes
            for t, tgt in enumerate(self.targetList):
                dup = cmds.duplicate(fromMesh)[0]
                geo = cmds.rename(dup, prefix+tgt+suffix)
                if t == 0:
                    cmds.setAttr(geo+".visibility", 0)
                    geoList.append(geo)
                elif t == 1:
                    geoList.append(geo)
                elif t == 2:
                    geoList.append(geo)
                else:
                    cmds.parent(geo, facialGrp)
            geoGrp = cmds.group(empty=True, name=prefix+"Tgt_Grp")
            cmds.parent(geoList, geoGrp)
            cmds.parent(facialGrp, geoGrp)
            cmds.hyperShade(assign="initialShadingGroup")
        else:
            mel.eval("warning \""+self.dpUIinst.lang["i042_notSelection"]+"\";")


    
    def dpChangeConnectCB(self, *args):
        """ Set values enable or disable when the user change the connect check box for Facial BlendShapes.
        """
        # get
        cbValue = cmds.checkBox(self.connectCB, query=True, value=True)
        # set
        cmds.button(self.loadBSButton, edit=True, enable=cbValue)
        cmds.textField(self.bsNodeTextField, edit=True, text="", enable=cbValue)
        cmds.text(self.bsTgtListTxt, edit=True, enable=cbValue)
        cmds.textScrollList(self.bsTargetScrollList, edit=True, removeAll=True, enable=cbValue)
    
    
    def dpChangeConnectFJ(self, *args):
        """ Set values enable or disable when the user change the connect check box for Facial Joints.
        """
        # get
        cbValue = cmds.checkBox(self.connectFJ, query=True, value=True)
        # set
        cmds.text(self.jntTgtListTxt, edit=True, enable=cbValue)
        cmds.textScrollList(self.jntTargetScrollList, edit=True, removeAll=True, enable=cbValue)
        if cbValue:
            # reload all joint target:
            self.dpLoadJointNode(self.tweaksNameList)
    
    
    def dpGetUserType(self, *args):
        """ Read UI in order to return a list of user choose.
            Returns [bool, bool] for use or not blendShapes or facial joints.
        """
        connectBS = cmds.checkBox(self.connectCB, query=True, value=True)
        connectJnt = cmds.checkBox(self.connectFJ, query=True, value=True)
        return [connectBS, connectJnt]
    
    
    def dpChangeType(self, *args):
        """ Get and return the user selected type of controls.
            Change interface to be more clear.
        """
        typeSelectedRadioButton = cmds.radioCollection(self.typeCollection, query=True, select=True)
        self.userType = cmds.radioButton(typeSelectedRadioButton, query=True, annotation=True)
        if self.userType == TYPE_BS:
            cmds.frameLayout(self.bsLayout, edit=True, enable=True, collapse=False)
            cmds.frameLayout(self.jointsLayout, edit=True, enable=False, collapse=True)
            cmds.checkBox(self.eyelidCB, edit=True, enable=True)
        elif self.userType == TYPE_JOINTS:
            cmds.frameLayout(self.bsLayout, edit=True, enable=False, collapse=True)
            cmds.frameLayout(self.jointsLayout, edit=True, enable=True, collapse=False)
            cmds.checkBox(self.eyelidCB, edit=True, enable=False)

    
    def dpCreateDefaultPackage(self, *args):
        """ Function to create a package of facial controls we use as default.
        """
        connectBS, connectJnt = self.dpGetUserType()
        # creating controls:
        lBrowCtrl, lBrowCtrlGrp = self.dpCreateFacialCtrl(self.dpUIinst.lang["p002_left"], self.dpUIinst.lang["c060_brow"], "id_046_FacialBrow", BROW_TGTLIST, (0, 0, 0), False, False, True, True, True, True, False, connectBS, connectJnt, "red", True, False)
        rBrowCtrl, rBrowCtrlGrp = self.dpCreateFacialCtrl(self.dpUIinst.lang["p003_right"], self.dpUIinst.lang["c060_brow"], "id_046_FacialBrow", BROW_TGTLIST, (0, 0, 0), False, False, True, True, True, True, False, connectBS, connectJnt, "blue", True, False)
        if self.userType == TYPE_BS:
            lEyelidCtrl, lEyelidCtrlGrp = self.dpCreateFacialCtrl(self.dpUIinst.lang["p002_left"], self.dpUIinst.lang["c042_eyelid"], "id_047_FacialEyelid", EYELID_TGTLIST, (0, 0, 90), True, False, True, False, True, True, False, connectBS, connectJnt, "red", True, False)
            rEyelidCtrl, rEyelidCtrlGrp = self.dpCreateFacialCtrl(self.dpUIinst.lang["p003_right"], self.dpUIinst.lang["c042_eyelid"], "id_047_FacialEyelid", EYELID_TGTLIST, (0, 0, 90), True, False, True, False, True, True, False, connectBS, connectJnt, "blue", True, False)
        lMouthCtrl, lMouthCtrlGrp = self.dpCreateFacialCtrl(self.dpUIinst.lang["p002_left"], self.dpUIinst.lang["c061_mouth"], "id_048_FacialMouth", MOUTH_TGTLIST, (0, 0, -90), False, False, True, False, False, True, False, connectBS, connectJnt, "red", True, True)
        rMouthCtrl, rMouthCtrlGrp = self.dpCreateFacialCtrl(self.dpUIinst.lang["p003_right"], self.dpUIinst.lang["c061_mouth"], "id_048_FacialMouth", MOUTH_TGTLIST, (0, 0, -90), False, False, True, False, False, True, False, connectBS, connectJnt, "blue", True, True)
        lipsCtrl, lipsCtrlGrp = self.dpCreateFacialCtrl(None, self.dpUIinst.lang["c062_lips"], "id_049_FacialLips", LIPS_TGTLIST, (0, 0, 0), False, False, False, True, True, True, False, connectBS, connectJnt, "yellow", True, True)
        sneerCtrl, sneerCtrlGrp = self.dpCreateFacialCtrl(None, self.dpUIinst.lang["c063_sneer"], "id_050_FacialSneer", SNEER_TGTLIST, (0, 0, 0), False, False, False, True, True, True, False, connectBS, connectJnt, "cyan", True, True)
        grimaceCtrl, grimaceCtrlGrp = self.dpCreateFacialCtrl(None, self.dpUIinst.lang["c064_grimace"], "id_051_FacialGrimace", GRIMACE_TGTLIST, (0, 0, 0), False, False, False, True, True, True, False, connectBS, connectJnt, "cyan", True, True)
        faceCtrl, faceCtrlGrp = self.dpCreateFacialCtrl(None, self.dpUIinst.lang["c065_face"], "id_052_FacialFace", FACE_TGTLIST, (0, 0, 0), True, True, True, True, True, True, True, connectBS, connectJnt, "cyan", False, False)
        
        # integrating to dpAutoRigSystem:
        if self.headCtrl:
            self.upperHeadFacialCtrlsGrp = cmds.group(name=self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c024_head']+"_"+self.dpUIinst.lang["c059_facial"]+"_Ctrls_Grp", empty=True)
            self.upperJawFacialCtrlsGrp = cmds.group(name=self.dpUIinst.lang['c044_upper']+self.dpUIinst.lang['c025_jaw']+"_"+self.dpUIinst.lang["c059_facial"]+"_Ctrls_Grp", empty=True)
            self.chinFacialCtrlsGrp = cmds.group(name=self.dpUIinst.lang['c026_chin']+"_"+self.dpUIinst.lang["c059_facial"]+"_Ctrls_Grp", empty=True)
            cmds.parent(self.upperHeadFacialCtrlsGrp, self.headFacialCtrlsGrp)
            cmds.parent(self.upperJawFacialCtrlsGrp, self.headFacialCtrlsGrp)
            cmds.parent(self.chinFacialCtrlsGrp, self.headFacialCtrlsGrp)
        else:
            self.upperHeadFacialCtrlsGrp = None
            self.upperJawFacialCtrlsGrp = None
            self.chinFacialCtrlsGrp = None

        # placing control groups:
        if lBrowCtrlGrp:
            cmds.setAttr(lBrowCtrlGrp+".translateX", 4)
            cmds.setAttr(lBrowCtrlGrp+".translateY", 12)
            cmds.setAttr(lBrowCtrlGrp+".translateZ", 13)
            if self.upperHeadFacialCtrlsGrp:
                cmds.parent(lBrowCtrlGrp, self.upperHeadFacialCtrlsGrp)
        if rBrowCtrlGrp:
            cmds.setAttr(rBrowCtrlGrp+".rotateY", 180)
            cmds.setAttr(rBrowCtrlGrp+".translateX", -4)
            cmds.setAttr(rBrowCtrlGrp+".translateY", 12)
            cmds.setAttr(rBrowCtrlGrp+".translateZ", 13)
            if self.upperHeadFacialCtrlsGrp:
                cmds.parent(rBrowCtrlGrp, self.upperHeadFacialCtrlsGrp)
        if lMouthCtrlGrp:
            cmds.setAttr(lMouthCtrlGrp+".translateX", 3)
            cmds.setAttr(lMouthCtrlGrp+".translateY", 1.5)
            cmds.setAttr(lMouthCtrlGrp+".translateZ", 13)
            if self.upperJawFacialCtrlsGrp:
                cmds.parent(lMouthCtrlGrp, self.upperJawFacialCtrlsGrp)
        if rMouthCtrlGrp:
            cmds.setAttr(rMouthCtrlGrp+".rotateY", 180)
            cmds.setAttr(rMouthCtrlGrp+".translateX", -3)
            cmds.setAttr(rMouthCtrlGrp+".translateY", 1.5)
            cmds.setAttr(rMouthCtrlGrp+".translateZ", 13)
            if self.upperJawFacialCtrlsGrp:
                cmds.parent(rMouthCtrlGrp, self.upperJawFacialCtrlsGrp)
        if lipsCtrlGrp:
            cmds.setAttr(lipsCtrlGrp+".translateY", 1.5)
            cmds.setAttr(lipsCtrlGrp+".translateZ", 13)
            if self.upperJawFacialCtrlsGrp:
                cmds.parent(lipsCtrlGrp, self.upperJawFacialCtrlsGrp)
        if sneerCtrlGrp:
            cmds.setAttr(sneerCtrlGrp+".translateY", 2.5)
            cmds.setAttr(sneerCtrlGrp+".translateZ", 13)
            if self.upperJawFacialCtrlsGrp:
                cmds.parent(sneerCtrlGrp, self.upperJawFacialCtrlsGrp)
        if grimaceCtrlGrp:
            cmds.setAttr(grimaceCtrlGrp+".rotateX", 180)
            cmds.setAttr(grimaceCtrlGrp+".scaleZ", -1)
            cmds.setAttr(grimaceCtrlGrp+".translateY", 0.5)
            cmds.setAttr(grimaceCtrlGrp+".translateZ", 13)
            if self.chinFacialCtrlsGrp:
                cmds.parent(grimaceCtrlGrp, self.chinFacialCtrlsGrp)
        if faceCtrlGrp:
            cmds.setAttr(faceCtrlGrp+".translateX", 10)
            cmds.setAttr(faceCtrlGrp+".translateY", 2)
        
        if self.userType == TYPE_BS:
            if lEyelidCtrlGrp:
                cmds.setAttr(lEyelidCtrlGrp+".translateX", 2)
                cmds.setAttr(lEyelidCtrlGrp+".translateY", 10)
                cmds.setAttr(lEyelidCtrlGrp+".translateZ", 13)
                if self.upperHeadFacialCtrlsGrp:
                    cmds.parent(lEyelidCtrlGrp, self.upperHeadFacialCtrlsGrp)
            if rEyelidCtrlGrp:
                cmds.setAttr(rEyelidCtrlGrp+".translateX", -2)
                cmds.setAttr(rEyelidCtrlGrp+".translateY", 10)
                cmds.setAttr(rEyelidCtrlGrp+".translateZ", 13)
                if self.upperHeadFacialCtrlsGrp:
                    cmds.parent(rEyelidCtrlGrp, self.upperHeadFacialCtrlsGrp)
        
        # integrating to dpAutoRigSystem:
        if self.headCtrl:
            cmds.parent(self.headFacialCtrlsGrp, self.headCtrl, absolute=True)
            cmds.setAttr(self.headFacialCtrlsGrp+".tx", 0)
            cmds.setAttr(self.headFacialCtrlsGrp+".ty", 0)
            cmds.setAttr(self.headFacialCtrlsGrp+".tz", 0)
            cmds.parent(self.upperHeadFacialCtrlsGrp, self.upperHeadCtrl)
            cmds.parent(self.upperJawFacialCtrlsGrp, self.upperJawCtrl)
            cmds.parent(self.chinFacialCtrlsGrp, self.chinCtrl)
            cmds.select(self.upperHeadFacialCtrlsGrp, self.upperJawFacialCtrlsGrp, self.chinFacialCtrlsGrp, self.headFacialCtrlsGrp)
    
        # closes window:
        self.dpCloseFacialConnectionWin()
        
    
    def dpSelectedCtrls(self, *args):
        """ Function to create selected facial controls checkboxes.
        """
        connectBS, connectJnt = self.dpGetUserType()
        
        if cmds.checkBox(self.browCB, query=True, value=True):
            lBrowCtrl, lBrowCtrlGrp = self.dpCreateFacialCtrl(self.dpUIinst.lang["p002_left"], self.dpUIinst.lang["c060_brow"], "id_046_FacialBrow", BROW_TGTLIST, (0, 0, 0), False, False, True, True, True, True, False, connectBS, connectJnt, "red", True, False)
            rBrowCtrl, rBrowCtrlGrp = self.dpCreateFacialCtrl(self.dpUIinst.lang["p003_right"], self.dpUIinst.lang["c060_brow"], "id_046_FacialBrow", BROW_TGTLIST, (0, 0, 0), False, False, True, True, True, True, False, connectBS, connectJnt, "blue", True, False)
            if rBrowCtrlGrp:
                cmds.setAttr(rBrowCtrlGrp+".rotateY", 180)
        if cmds.checkBox(self.eyelidCB, query=True, enable=True):
            if cmds.checkBox(self.eyelidCB, query=True, value=True):
                lEyelidCtrl, lEyelidCtrlGrp = self.dpCreateFacialCtrl(self.dpUIinst.lang["p002_left"], self.dpUIinst.lang["c042_eyelid"], "id_047_FacialEyelid", EYELID_TGTLIST, (0, 0, 90), True, False, True, False, True, True, False, connectBS, connectJnt, "red", True, False)
                rEyelidCtrl, rEyelidCtrlGrp = self.dpCreateFacialCtrl(self.dpUIinst.lang["p003_right"], self.dpUIinst.lang["c042_eyelid"], "id_047_FacialEyelid", EYELID_TGTLIST, (0, 0, 90), True, False, True, False, True, True, False, connectBS, connectJnt, "blue", True, False)
        if cmds.checkBox(self.mouthCB, query=True, value=True):
            lMouthCtrl, lMouthCtrlGrp = self.dpCreateFacialCtrl(self.dpUIinst.lang["p002_left"], self.dpUIinst.lang["c061_mouth"], "id_048_FacialMouth", MOUTH_TGTLIST, (0, 0, -90), False, False, True, False, False, True, False, connectBS, connectJnt, "red", True, True)
            rMouthCtrl, rMouthCtrlGrp = self.dpCreateFacialCtrl(self.dpUIinst.lang["p003_right"], self.dpUIinst.lang["c061_mouth"], "id_048_FacialMouth", MOUTH_TGTLIST, (0, 0, -90), False, False, True, False, False, True, False, connectBS, connectJnt, "blue", True, True)
            if rMouthCtrlGrp:
                cmds.setAttr(rMouthCtrlGrp+".rotateY", 180)
        if cmds.checkBox(self.lipsCB, query=True, value=True):
            lipsCtrl, lipsCtrlGrp = self.dpCreateFacialCtrl(None, self.dpUIinst.lang["c062_lips"], "id_049_FacialLips", LIPS_TGTLIST, (0, 0, 0), False, False, False, True, True, True, False, connectBS, connectJnt, "yellow", True, True)
        if cmds.checkBox(self.sneerCB, query=True, value=True):
            sneerCtrl, sneerCtrlGrp = self.dpCreateFacialCtrl(None, self.dpUIinst.lang["c063_sneer"], "id_050_FacialSneer", SNEER_TGTLIST, (0, 0, 0), False, False, True, True, True, True, False, connectBS, connectJnt, "cyan", True, True, True, True)
        if cmds.checkBox(self.grimaceCB, query=True, value=True):
            grimaceCtrl, grimaceCtrlGrp = self.dpCreateFacialCtrl(None, self.dpUIinst.lang["c064_grimace"], "id_051_FacialGrimace", GRIMACE_TGTLIST, (0, 0, 0), False, False, True, True, True, True, False, connectBS, connectJnt, "cyan", True, True, True, True)
            if grimaceCtrlGrp:
                cmds.setAttr(grimaceCtrlGrp+".rotateX", 180)
        if cmds.checkBox(self.faceCB, query=True, value=True):
            faceCtrl, faceCtrlGrp = self.dpCreateFacialCtrl(None, self.dpUIinst.lang["c065_face"], "id_052_FacialFace", FACE_TGTLIST, (0, 0, 0), True, True, True, True, True, False, True, connectBS, connectJnt, "cyan", False, False)
        
    
    def dpCreateFacialCtrl(self, side, ctrlName, cvCtrl, attrList, rotVector=(0, 0, 0), lockX=False, lockY=False, lockZ=False, limitX=True, limitY=True, limitZ=True, directConnection=False, connectBS=True, connectJnt=False, color='yellow', headDefInfluence=False, jawDefInfluence=False, addTranslateY=False, limitMinY=False, *args):
        """ Important function to receive called parameters and create the specific asked control.
            Convention:
                transfList = ["tx", "tx", "ty", "ty", "tz", "tz]
                axisDirectionList = [-1, 1, -1, 1, -1, 1] # neg, pos, neg, pos, neg, pos
            Returns the created Facial control and its zeroOut group.
        """
        # force limits when working on facial joints:
        if connectJnt:
            limitX = True
            limitY = True
            limitZ = True
        
        # declaring variables:
        fCtrl = None
        fCtrlGrp = None
        
        calibrationList = []
        transfList = ["tx", "tx", "ty", "ty", "tz", "tz"]
        # naming:
        if not side == None:
            ctrlName = side+"_"+ctrlName
        fCtrlName = ctrlName+"_Ctrl"
        # skip if already there is this ctrl object:
        if cmds.objExists(fCtrlName):
            return None, None
        else:
            if self.userType == TYPE_BS:
                if connectBS and self.bsNode:
                    # validating blendShape node:
                    if cmds.objectType(self.bsNode) == "blendShape":
                        aliasList = cmds.aliasAttr(self.bsNode, query=True)
            # create control calling dpControls function:
            fCtrl = self.ctrls.cvControl(cvCtrl, fCtrlName, d=0, rot=rotVector)
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
                            cmds.connectAttr(invMD+".outputX", fCtrl+"."+attr, force=True)
                            cmds.setAttr(fCtrl+"."+attr, lock=True)
                        
                        if self.userType == TYPE_BS:
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
                        else: # setup to using facial joints:
                            if connectJnt:
                                sidedNodeList = None
                                try:
                                    sidedNodeList = self.tweaksDic[attr]
                                except:
                                    pass
                                if sidedNodeList:
                                    # sideNode is like MIDDLE or SIDED:
                                    for sidedNode in sidedNodeList:
                                        toNodeList = None
                                        try:
                                            toNodeList = self.tweaksDic[attr][sidedNode]
                                        except:
                                            pass
                                        if toNodeList:
                                            # toNodeBase is igual to facial control offset group target:
                                            for toNodeBaseName in toNodeList:
                                                toNode = None
                                                toNodeSided = toNodeBaseName
                                                addedSide = False
                                                toNodeTargedList = []
                                                for jntTarget in self.jntTargetList:
                                                    toNodeSided = toNodeBaseName
                                                    if sidedNode == SIDED:
                                                        if not addedSide:
                                                            if not side == None:
                                                                # check prefix:
                                                                if jntTarget[1] == "_":
                                                                    if side == jntTarget[0]:
                                                                        toNodeSided = side+"_"+toNodeBaseName
                                                                        if jntTarget.startswith(toNodeSided):    
                                                                            toNode = jntTarget
                                                                            addedSide = True
                                                            elif toNodeSided in jntTarget:
                                                                if attr[1] == "_":
                                                                    if attr[0] == jntTarget[0]:
                                                                        toNode = jntTarget
                                                                        addedSide = True
                                                                else:
                                                                    toNodeTargedList.append(jntTarget)
                                                                    toNode = jntTarget
                                                    elif jntTarget.startswith(toNodeSided):
                                                        if cmds.objExists(jntTarget):
                                                            toNode = jntTarget
                                                if toNode:
                                                    if not toNodeTargedList:
                                                        toNodeTargedList.append(toNode)
                                                    for toNode in toNodeTargedList:
                                                        if cmds.objExists(toNode):
                                                            # caculate factor for scaled item:
                                                            sizeFactor = self.dpGetSizeFactor(toNode)
                                                            if not sizeFactor:
                                                                sizeFactor = 1
                                                            toAttrList = self.tweaksDic[attr][sidedNode][toNodeBaseName]
                                                            for toAttr in toAttrList:
                                                                # read stored values in order to call function to make the setup:
                                                                oMin = self.tweaksDic[attr][sidedNode][toNodeBaseName][toAttr][0]
                                                                oMax = self.tweaksDic[attr][sidedNode][toNodeBaseName][toAttr][1]
                                                                self.dpCreateRemapNode(fCtrl, attr, toNodeBaseName, toNode, toAttr, self.RmVNumber, sizeFactor, oMin, oMax)
                                                                self.RmVNumber = self.RmVNumber+1
            if calibrationList:
                self.ctrls.setCalibrationAttr(fCtrl, calibrationList)
            # parenting the hierarchy:
            if not cmds.objExists(self.headFacialCtrlsGrp):
                cmds.group(name=self.headFacialCtrlsGrp, empty=True)
            cmds.parent(fCtrlGrp, self.headFacialCtrlsGrp)
        
        cmds.select(self.headFacialCtrlsGrp)
        return fCtrl, fCtrlGrp
    
    
    def dpLockLimitAttr(self, fCtrl, ctrlName, lockList, limitList, limitMinY, *args):
        """ Lock or limit attributes for XYZ.
        """
        axisList = ["X", "Y", "Z"]
        for i, axis in enumerate(axisList):
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
    
    
    def dpLoadBSNode(self, *args):
        """ Load selected object as blendShapeNode
        """
        selectedList = cmds.ls(selection=True)
        if selectedList:
            if cmds.objectType(selectedList[0]) == "blendShape":
                cmds.textField(self.bsNodeTextField, edit=True, text=selectedList[0])
                self.dpLoadBSTgtList(selectedList[0])
                self.bsNode = selectedList[0]
            elif cmds.objectType(selectedList[0]) == "transform":
                meshList = cmds.listRelatives(selectedList[0], children=True, shapes=True, noIntermediate=True, type="mesh")
                if meshList:
                    bsNodeList = cmds.listConnections(meshList[0], type="blendShape")
                    if bsNodeList:
                        self.dpLoadBSTgtList(bsNodeList[0])
                        self.bsNode = bsNodeList[0]
                    else:
                        mel.eval("warning \""+self.dpUIinst.lang["e018_selectBlendShape"]+"\";")
                else:
                    mel.eval("warning \""+self.dpUIinst.lang["e018_selectBlendShape"]+"\";")
            else:
                mel.eval("warning \""+self.dpUIinst.lang["e018_selectBlendShape"]+"\";")
        else:
            mel.eval("warning \""+self.dpUIinst.lang["e018_selectBlendShape"]+"\";")
    
    
    def dpLoadBSTgtList(self, bsNodeName, *args):
        """ Add target list found in the blendShape node to target textScroll list
        """
        if cmds.objExists(bsNodeName):
            if cmds.objectType(bsNodeName) == "blendShape":
                tgtList = cmds.blendShape(bsNodeName, query=True, target=True)
                if tgtList:
                    cmds.textScrollList(self.bsTargetScrollList, edit=True, removeAll=True)
                    cmds.textScrollList(self.bsTargetScrollList, edit=True, append=tgtList)
                    cmds.textField(self.bsNodeTextField, edit=True, text=bsNodeName)
                    self.bsNode = bsNodeName
    
    
    def dpLoadJointNode(self, itemList, *args):
        """ Load the respective items to build the joint target list (offset group node).
        """
        leftPrefix = self.dpUIinst.lang["p002_left"]+"_"
        rightPrefix = self.dpUIinst.lang["p003_right"]+"_"
        offsetSuffix = "_Ctrl_Offset_Grp"
        for item in itemList:
            centerName = item+offsetSuffix
            leftName   = leftPrefix+item+offsetSuffix
            rightName  = rightPrefix+item+offsetSuffix
            if cmds.objExists(centerName):
                self.dpLoadJointTgtList(centerName)
            if cmds.objExists(leftName):
                self.dpLoadJointTgtList(leftName)
            if cmds.objExists(rightName):
                self.dpLoadJointTgtList(rightName)
    
    
    def dpLoadJointTgtList(self, item, *args):
        # get current list
        currentList = cmds.textScrollList(self.jntTargetScrollList, query=True, allItems=True)
        if currentList:
            # clear current list
            cmds.textScrollList(self.jntTargetScrollList, edit=True, removeAll=True)
            # avoid repeated items
            if not item in currentList:
                currentList.append(item)
            # refresh textScrollList
            cmds.textScrollList(self.jntTargetScrollList, edit=True, append=currentList)
        else:
            # add selected items in the empyt target scroll list
            cmds.textScrollList(self.jntTargetScrollList, edit=True, append=item)
        self.jntTargetList = cmds.textScrollList(self.jntTargetScrollList, query=True, allItems=True)
    
    
    def dpCreateRemapNode(self, fromNode, fromAttr, toNodeBaseName, toNode, toAttr, number, sizeFactor, oMin=0, oMax=1, iMin=0, iMax=1, *args):
        """ Creates the nodes to remap values and connect it to final output (toNode) item.
        """
        fromNodeName = self.utils.extractSuffix(fromNode)
        remap = cmds.createNode("remapValue", name=fromNodeName+"_"+fromAttr+"_"+str(number).zfill(2)+"_"+toAttr.upper()+"_RmV")
        outMaxAttr = toNodeBaseName+"_"+str(number).zfill(2)+"_"+toAttr.upper()
        if "t" in toAttr:
            if not cmds.objExists(fromNode+".sizeFactor"):
                cmds.addAttr(fromNode, longName="sizeFactor", attributeType="float", defaultValue=sizeFactor, keyable=False)
            cmds.addAttr(fromNode, longName=outMaxAttr, attributeType="float", defaultValue=oMax, keyable=False)
            md = cmds.createNode("multiplyDivide", name=fromNodeName+"_"+fromAttr+"_"+str(number).zfill(2)+"_"+toAttr.upper()+"_SizeFactor_MD")
            cmds.connectAttr(fromNode+"."+outMaxAttr, md+".input1X", force=True)
            cmds.connectAttr(fromNode+".sizeFactor", md+".input2X", force=True)
            cmds.connectAttr(md+".outputX", remap+".outputMax", force=True)
        else:
            cmds.addAttr(fromNode, longName=outMaxAttr, attributeType="float", defaultValue=oMax, keyable=False)
            cmds.connectAttr(fromNode+"."+outMaxAttr, remap+".outputMax", force=True)
        cmds.setAttr(remap+".inputMin", iMin)
        cmds.setAttr(remap+".inputMax", iMax)
        cmds.setAttr(remap+".outputMin", oMin)
        cmds.connectAttr(fromNode+"."+fromAttr, remap+".inputValue", force=True)
        # check if there's an input connection and create a plusMinusAverage if we don't have one to connect in:
        connectedList = cmds.listConnections(toNode+"."+toAttr, destination=False, source=True, plugs=False)
        if connectedList:
            if cmds.objectType(connectedList[0]) == "plusMinusAverage":
                inputList = cmds.listConnections(connectedList[0]+".input1D", destination=False, source=True, plugs=False)
                cmds.connectAttr(remap+".outValue", connectedList[0]+".input1D["+str(len(inputList))+"]", force=True)
            else:
                if cmds.objectType(connectedList[0]) == "unitConversion":
                    connectedAttr = cmds.listConnections(connectedList[0]+".input", destination=False, source=True, plugs=True)[0]
                else:
                    connectedAttr = cmds.listConnections(toNode+"."+toAttr, destination=False, source=True, plugs=True)[0]
                pma = cmds.createNode("plusMinusAverage", name=toNode+"_"+toAttr.upper()+"_PMA")
                cmds.connectAttr(connectedAttr, pma+".input1D[0]", force=True)
                cmds.connectAttr(remap+".outValue", pma+".input1D[1]", force=True)
                cmds.connectAttr(pma+".output1D", toNode+"."+toAttr, force=True)
                if cmds.objectType(connectedList[0]) == "unitConversion":
                    cmds.delete(connectedList[0])
        else:
            cmds.connectAttr(remap+".outValue", toNode+"."+toAttr, force=True)
    

    def dpGetSizeFactor(self, toNode, *args):
        """ Get the child control size value and return it.
        """
        childrenList = cmds.listRelatives(toNode, children=True, type="transform")
        if childrenList:
            for child in childrenList:
                if cmds.objExists(child+".dpControl"):
                    if cmds.getAttr(child+".dpControl") == 1:
                        if cmds.objExists(child+".size"):
                            sizeValue = cmds.getAttr(child+".size")
                            return sizeValue