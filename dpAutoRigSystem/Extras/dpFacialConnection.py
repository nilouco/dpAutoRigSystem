# importing libraries:
from maya import cmds
from maya import mel
import os
import json
from ..Modules.Library import dpControls

# global variables to this module:
CLASS_NAME = "FacialConnection"
TITLE = "m085_facialConnection"
DESCRIPTION = "m086_facialConnectionDesc"
ICON = "/Icons/dp_facialConnection.png"

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
    
    
    def dpFacialConnectionUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        # creating targetMirrorUI Window:
        self.utils.closeUI('dpFacialConnectionWindow')
        facialCtrl_winWidth  = 220
        facialCtrl_winHeight = 160
        dpFacialControlWin = cmds.window('dpFacialConnectionWindow', title=self.dpUIinst.lang["m085_facialConnection"]+" "+str(DP_FACIALCONNECTION_VERSION), widthHeight=(facialCtrl_winWidth, facialCtrl_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        facialCtrlLayout = cmds.columnLayout('facialCtrlLayout', columnOffset=("both", 10), rowSpacing=10)
        cmds.separator(height=5, style="in", horizontal=True, parent=facialCtrlLayout)
        cmds.button(label=self.dpUIinst.lang["m140_createTargets"], annotation=self.dpUIinst.lang['m141_createTargetsDesc'], width=220, command=self.dpCreateTargets, align="center", parent=facialCtrlLayout)
        cmds.separator(height=5, style="single", horizontal=True, parent=facialCtrlLayout)
        cmds.text(label=self.dpUIinst.lang['m142_connectFacialAttr'], parent=facialCtrlLayout)
        cmds.button(label=self.dpUIinst.lang['m170_blendShapes']+" - "+self.dpUIinst.lang['i185_animation'], annotation="Create selected facial controls.", width=220, command=self.dpConnectToBlendShape, parent=facialCtrlLayout)
        cmds.button(label=self.dpUIinst.lang['i181_facialJoint']+" - "+self.dpUIinst.lang['i186_gaming'], annotation="Create default facial controls package.", width=220, command=self.dpConnectToJoints, parent=facialCtrlLayout)
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


    def dpConnectToBlendShape(self, ctrlList=None, bsList=None, *args):
        """ Find all dpControl and list their facial attributes to connect into existing alias in all blendShape nodes.
        """
        facialCtrlDic, bsDic = {}, {}
        # get facialList attr from dpAR controls found
        if not ctrlList:
            ctrlList = self.ctrls.getControlList()
        if ctrlList:
            for ctrl in ctrlList:
                if cmds.objExists(ctrl+".facialList"):
                    facialCtrlDic[ctrl] = self.ctrls.getListFromStringAttr(ctrl, "facialList")
        # get target list from existing blendShape nodes
        if not bsList:
            bsList = cmds.ls(selection=False, type="blendShape")
        if bsList:
            for bsNode in bsList:
                targetList = cmds.listAttr(bsNode+".w", multi=True)
                if targetList:
                    bsDic[bsNode] = targetList
        # connect them
        if facialCtrlDic and bsDic:
            for facialCtrl in list(facialCtrlDic.keys()):
                for bsNode in list(bsDic.keys()):
                    for facialAttr in facialCtrlDic[facialCtrl]:
                        for targetAttr in bsDic[bsNode]:
                            connectIt = False
                            if targetAttr.endswith(facialAttr+"_Tgt"):
                                connectIt = True
                            elif targetAttr.endswith(facialAttr):
                                connectIt = True
                            elif facialAttr == targetAttr:
                                connectIt = True
                            # not including here the (facialAttr in targetAttr) statement to try avoid connect into combination alias
                            if connectIt:
                                cmds.connectAttr(facialCtrl+"."+facialAttr, bsNode+"."+targetAttr, force=True)
                                print(self.dpUIinst.lang['m143_connected'], facialCtrl+"."+facialAttr, "->", bsNode+"."+targetAttr)


    def dpConnectToJoints(self, *args):
        """
        """
        print("here we are full of love with facial joints my friend...")
        # TODO






    
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
                self.ctrls.setStringAttrFromList(fCtrl, calibrationList)
            # parenting the hierarchy:
            if not cmds.objExists(self.headFacialCtrlsGrp):
                cmds.group(name=self.headFacialCtrlsGrp, empty=True)
            cmds.parent(fCtrlGrp, self.headFacialCtrlsGrp)
        
        cmds.select(self.headFacialCtrlsGrp)
        return fCtrl, fCtrlGrp
    
    
    
    
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