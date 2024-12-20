# importing libraries:
from maya import cmds
from maya import OpenMaya as om
import os
import sys
import re
import cProfile
import urllib.request
import webbrowser
import math
import json
import time
import getpass
import datetime
import stat
from io import TextIOWrapper
from importlib import reload

DP_UTILS_VERSION = 3.1


class Utils(object):
    def __init__(self, dpUIinst, *args):
        """ Initialize the module class loading variables.
        """
        # define variables
        self.dpUIinst = dpUIinst
        self.dpOrderList = "dpOrderList"
        self.ignoreTransformIOAttr = "dpNotTransformIO"
        self.progress = False
        self.dpID = self.dpUIinst.dpID
        self.defineDics()


    def defineDics(self, *args):
        """ Just define dictionary member variables.
        """
        self.baseNodeList = ['time1', 'sequenceManager1', 'hardwareRenderingGlobals', 'renderPartition', 'renderGlobalsList1', 'defaultLightList1', 'defaultShaderList1', 'postProcessList1',
                            'defaultRenderUtilityList1', 'defaultRenderingList1', 'lightList1', 'defaultTextureList1', 'lambert1', 'standardSurface1', 'particleCloud1', 'initialShadingGroup', 'initialParticleSE', 
                            'initialMaterialInfo', 'shaderGlow1', 'dof1', 'defaultRenderGlobals', 'defaultRenderQuality', 'defaultResolution', 'defaultLightSet', 'defaultObjectSet', 'defaultViewColorManager', 
                            'defaultColorMgtGlobals', 'hardwareRenderGlobals', 'characterPartition', 'defaultHardwareRenderGlobals', 'ikSystem', 'hyperGraphInfo', 'hyperGraphLayout', 'globalCacheControl', 
                            'strokeGlobals', 'dynController1', 'lightLinker1', 'persp', 'perspShape', 'top', 'topShape', 'front', 'frontShape', 'side', 'sideShape', 'shapeEditorManager', 'poseInterpolatorManager', 
                            'layerManager', 'defaultLayer', 'renderLayerManager', 'defaultRenderLayer', 'ikSCsolver', 'ikRPsolver', 'ikSplineSolver', 'hikSolver', 'MayaNodeEditorSavedTabsInfo']
        self.utilityTypeList = ["blendColors", "blendWeighted", "choice", "chooser", "clamp", "condition", "multiplyDivide", "plusMinusAverage", "remapValue", "reverse"]
        self.typeAttrDic = {
                            "blendColors"      : ["blender", "color1R", "color1G", "color1B", "color2R", "color2G", "color2B"],
                            "blendWeighted"    : ["current"],
                            "choice"           : ["selector"],
                            "clamp"            : ["minR", "minG", "minB", "maxR", "maxG", "maxB", "inputR", "inputG", "inputB"],
                            "condition"        : ["operation", "firstTerm", "secondTerm", "colorIfTrueR", "colorIfTrueG", "colorIfTrueB", "colorIfFalseR", "colorIfFalseG", "colorIfFalseB"],
                            "multiplyDivide"   : ["operation", "input1X", "input1Y", "input1Z", "input2X", "input2Y", "input2Z"],
                            "plusMinusAverage" : ["operation"],
                            "remapValue"       : ["inputValue", "inputMin", "inputMax", "outputMin", "outputMax"],
                            "reverse"          : ["inputX", "inputY", "inputZ"]
                        }
        self.typeOutAttrDic = {
                            "blendColors"      : ["outputR", "outputG", "outputB"],
                            "blendWeighted"    : ["output"],
                            "choice"           : ["output"],
                            "clamp"            : ["outputR", "outputG", "outputB"],
                            "condition"        : ["outColorR", "outColorG", "outColorB"],
                            "multiplyDivide"   : ["outputX", "outputY", "outputZ"],
                            "plusMinusAverage" : ["output1D", "output2Dx", "output2Dy", "output3Dx", "output3Dy", "output3Dz"],
                            "remapValue"       : ["outColorR", "outColorG", "outColorB", "outValue"],
                            "reverse"          : ["outputX", "outputY", "outputZ"]
                        }
        self.typeMultiAttrDic = {
                            "blendWeighted"    : {"input"   : [],
                                                   "weight" : []},
                            "choice"           : {"input" : []},
                            "chooser"          : {"inLevel"      : [],
                                                  "displayLevel" : []},
                            "plusMinusAverage" : {"input1D" : [],
                                                  "input2D" : ["input2Dx", "input2Dy"],
                                                  "input3D" : ["input3Dx", "input3Dy", "input3Dz"]
                                                    },
                            "remapValue"       : {"value" : ["value_Position", "value_FloatValue", "value_Interp"],
                                                  "color" : ["color_Position", "color_Color", "color_ColorR", "color_ColorG", "color_ColorB", "color_Position"]
                                                    }
                        }
        self.typeOutMultiAttrDic = {"chooser" : {"output" : []}}
        

    # UTILS functions:
    def findEnv(self, key, path):
        """ Find and return the environ directory of this system.
        """
        envStr = os.environ[key]
        
        dpARPath = self.findPath("dpAutoRig.py")

        splitEnvList = []
        if os.name == "posix":
            splitEnvList = envStr.split(":")
        else:
            splitEnvList = envStr.split(";")
        envPath = ""

        if splitEnvList:
            splitEnvList = [x for x in splitEnvList if x != "" and x != ' ' and x != None]
            for env in splitEnvList:
                env = os.path.abspath(env) # Fix crash when there's relative path in os.environ
                if env in dpARPath:
                    try:
                        envPath = dpARPath.split(env)[1][+1:].split(path)[0][:-1].replace('/','.')
                    except:
                        pass
                    if len(env) < 4:
                        envPath = dpARPath.split(env)[1][0:].split(path)[0][:-1].replace('/','.')
                        return envPath+"."+path
                    break
        # if we are here, we must return a default path:
        splitEnvList = envStr.rpartition(path)
        if os.name == "posix":
            if envPath != "":
                envPath = envPath+".dpAutoRigSystem"
            else:
                envPath = "dpAutoRigSystem"
        else:
            if ":" in envPath:
                envPath = splitEnvList[0][splitEnvList[0].rfind(":")-1:]
        if envPath == "" or envPath == " " or envPath == None:
            return path
        return envPath


    def findPath(self, filename):
        """ Find and return the absolute path of the fileName.
        """
        stringPath   = str(os.path.join(os.path.dirname(sys._getframe(1).f_code.co_filename), filename))
        correctPath  = stringPath.replace("\\", "/")
        if os.name == "posix":
            absolutePath = stringPath[0:stringPath.rfind("/")]
        else:
            absolutePath = correctPath[correctPath.find("/")-2:correctPath.rfind("/")]
        return absolutePath


    def findAllFiles(self, path, dir, ext=".py"):
        """ Find all files in the directory with the extension.
            Return a list of all module names (without '.py' extension).
        """
        fileDir = path + "/" + dir
        allFilesList = os.listdir(fileDir)
        # select only files with extension:
        pyFilesList = []
        for file in allFilesList:
            if file.endswith(ext) and str(file) != "__init__.py":
                pyFilesList.append(str(file)[:file.rfind(".")])
        return pyFilesList


    def findAllModules(self, path, dir):
        """ Find all modules in the directory.
            If find a dpOrderList.txt file it will order the list for priority proporses.
            Return a list of all module names (without '.py' extension).
        """
        baseClassList = ["dpBaseStandard", "dpBaseLayout", "dpBaseCurve", "dpBaseAction", "dpValidatorTemplate", "dpPublisher", "dpPipeliner", "dpPackager"]
        allPyFilesList = self.findAllFiles(path, dir, ".py")
        moduleList = []
        for file in allPyFilesList:
            # ensure base class are skipped
            if not file in baseClassList:
                moduleList.append(file)
        # check order list
        if moduleList:
            textList = self.findAllFiles(path, dir, ".txt")
            if textList:
                for text in textList:
                    if self.dpOrderList in text:
                        desiredOrderList = []
                        dupList = moduleList
                        moduleList = []
                        with open(path+"/"+dir+"/"+text+".txt", encoding='utf8') as filename:
                            for line in filename.readlines():
                                desiredOrderList.append(line.strip())
                        if desiredOrderList:
                            for item in desiredOrderList:
                                if item in dupList:
                                    moduleList.append(item)
                                    dupList.remove(item)
                        if dupList:
                            moduleList.extend(dupList)
        return moduleList


    def findAllModuleNames(self, path, dir):
        """ Find all modules names for this directory.
            Return a list with the valid modules and valid modules names.
        """
        validModules = self.findAllModules(path, dir)
        validModuleNames = []
        #guideFolder = (path+"/"+dir).partition("/Modules/")[2]
        guideFolder = self.findEnv("PYTHONPATH", "dpAutoRigSystem")+".Modules.Standard"
        for m in validModules:
            mod = __import__(guideFolder+"."+m, {}, {}, [m])
            if self.dpUIinst.dev:
                reload(mod)
            validModuleNames.append(mod.CLASS_NAME)
        return(validModules, validModuleNames)


    def findLastNumber(self, name="dpGuideNet", attr="guideNumber", *args):
        """ Returns a padding 3 string of the number of network node in the scene or zero.
        """
        nodeList = self.getNetworkNodeByAttr(name)
        if not nodeList:
            return "000"
        else:
            numberList = []
            for node in nodeList:
                if cmds.objExists(node+"."+attr):
                    numberList.append(int(cmds.getAttr(node+"."+attr)))
            if not numberList:
                return "000"
            else:
                return str(max(numberList)+1).zfill(3)


    def findModuleLastNumber(self, className, typeName):
        """ Find the last used number of this type of module.
            Return its highest number.
        """
        # work with rigged modules in the scene:
        numberList = []
        guideTypeCount = 0
        # list all transforms and find the existing value in them names:
        transformList = cmds.ls(selection=False, transforms=True)
        for transform in transformList:
            if cmds.objExists(transform+"."+typeName):
                if cmds.getAttr(transform+"."+typeName) == className:
                    numberList.append(className)
            # try check if there is a masterGrp and get its counter:
            if cmds.objExists(transform+".masterGrp") and cmds.getAttr(transform+".masterGrp") == 1:
                guideTypeCount = cmds.getAttr(transform+'.dp'+className+'Count')
        if(guideTypeCount > len(numberList)):
            return guideTypeCount
        else:
            return len(numberList)
        
        
    def normalizeText(self, enteredText="", prefixMax=4):
        """ Analisys the enteredText to conform it in order to use in Application (Maya).
            Return the normalized text.
        """
        normalText = ""
        # analisys if it starts with number or has a whitespace or special character:
        if re.match("[0-9]", enteredText) or re.search("\s", enteredText[:len(enteredText)-1]) or re.search("\W", enteredText):
            return normalText
        # just add a underscore at the end for one character entered:
        #elif len(enteredText) == 1 and enteredText != " " and enteredText != "_":
        #    normalText = enteredText+"_"
        # edit this to have only a maximum of 'prefixMax' digits:
        else:
            if len(enteredText) < prefixMax:
                prefixMax = len(enteredText)
            for m in range(0, prefixMax):
                if enteredText[m] != " " and enteredText[m] != "_":
                    normalText = enteredText[:m+1]
        return normalText


    def useDefaultRenderLayer(self):
        """ Analisys if must use the Default Render Layer (masterLayer) checking the option in the UI.
            Set to use it if need.
        """
        # analisys to use the defaultRenderLayer:
        useDefaultRL = cmds.checkBox('defaultRenderLayerCB', query=True, value=True)
        if useDefaultRL:
            cmds.editRenderLayerGlobals(currentRenderLayer='defaultRenderLayer')


    def removeUserDefinedAttr(self, node, keepOriginedFrom=False):
        """ Just remove all user defined attributes for the given node.
        """
        userDefAttrList = cmds.listAttr(node, userDefined=True)
        if userDefAttrList:
            for userDefAttr in userDefAttrList:
                delIt = True
                if "originedFrom" in userDefAttr:
                    if keepOriginedFrom:
                        delIt = False
                if delIt:
                    try:
                        cmds.setAttr(node+"."+userDefAttr, lock=False)
                        cmds.deleteAttr(node+"."+userDefAttr)
                    except:
                        pass


    def zeroOut(self, transformList=[], offset=False, notTransformIO=True):
        """ Create a group over the transform, parent the transform in it and set zero all transformations of the transform node.
            If don't have a transformList given, try to get the current selection.
            If want to create with offset, it'll be an offset group between zeroGrp and transform.
            Return a list of names of the zeroOut groups.
        """
        zeroList = []
        if not transformList:
            transformList = cmds.ls(selection=True)
        if transformList:
            for transform in transformList:
                suffix = "_Zero_0_Grp"
                transformName = transform
                if transformName.endswith("_Grp"):
                    transformName = self.extractSuffix(transformName)
                    if "_Zero_" in transformName:
                        needAddNumber = True
                        while needAddNumber:
                            nodeNumber = str(int(transformName[transformName.rfind("_")+1:])+1)
                            transformName = (transformName[:transformName.rfind("_")+1])+nodeNumber
                            suffix = "_Grp"
                            if not cmds.objExists(transformName+suffix):
                                needAddNumber = False
                zeroGrp = cmds.duplicate(transform, name=transformName+suffix)[0]
                self.removeUserDefinedAttr(zeroGrp)
                allChildrenList = cmds.listRelatives(zeroGrp, allDescendents=True, children=True, fullPath=True)
                if allChildrenList:
                    cmds.delete(allChildrenList)
                if offset:
                    offsetGrp = cmds.duplicate(zeroGrp, name=transform+'_Offset_Grp')[0]
                    self.dpUIinst.customAttr.addAttr(0, [offsetGrp]) #dpID
                    cmds.parent(transform, offsetGrp, absolute=True)
                    cmds.parent(offsetGrp, zeroGrp, absolute=True)
                else:
                    cmds.parent(transform, zeroGrp, absolute=True)
                if notTransformIO:
                    self.addCustomAttr([zeroGrp], self.ignoreTransformIOAttr)
                    if offset:
                        self.addCustomAttr([offsetGrp], self.ignoreTransformIOAttr)
                self.dpUIinst.customAttr.addAttr(0, [zeroGrp]) #dpID
                zeroList.append(zeroGrp)
        return zeroList


    def addCustomAttr(self, nodeList, attrName, attrType="bool", keyableAttr=True, defaultValueAttr=True, *args):
        """ Useful method to add the same attribute and values to a list of given nodes.
        """
        if nodeList and attrName:
            for node in nodeList:
                if not cmds.objExists(node+"."+attrName):
                    cmds.addAttr(node, longName=attrName, attributeType=attrType, keyable=keyableAttr, defaultValue=defaultValueAttr)


    def originedFrom(self, objName="", attrString=""):
        """ Add attribute as string and set is as attrName got.
        """
        if objName != "" and attrString != "":
            if not cmds.objExists(objName+".originedFrom"):
                cmds.addAttr(objName, longName="originedFrom", dataType='string')
            cmds.setAttr(objName+".originedFrom", attrString, type='string')


    def getOriginedFromDic(self):
        """ List all transforms in the scene, verify if there is an originedFrom string attribute and store it value in a dictionary.
            Return a dictionary with originedFrom string as keys and transform nodes as values of these keys.
        """
        originedFromDic = {}
        allTransformList = cmds.ls(selection=False, type="transform")
        if allTransformList:
            for transform in allTransformList:
                if cmds.objExists(transform+".originedFrom"):
                    tempOriginedFrom = cmds.getAttr(transform+".originedFrom")
                    if tempOriginedFrom:
                        if not ";" in tempOriginedFrom:
                            originedFromDic[tempOriginedFrom] = transform
                        else:
                            tempOriginedFromList = tempOriginedFrom.split(";")
                            for orignedFromString in tempOriginedFromList:
                                originedFromDic[orignedFromString] = transform
        return originedFromDic


    def addHook(self, objName="", hookType="staticHook", addNotTransformIO=True):
        """ Add attribute as boolean and set it as True = 1.
        """
        if objName != "":
            if cmds.objExists(objName):
                if not cmds.objExists(objName+"."+hookType):
                    cmds.addAttr(objName, longName=hookType, attributeType='bool')
                    cmds.setAttr(objName+"."+hookType, 1)
                if addNotTransformIO:
                    self.addCustomAttr([objName], self.ignoreTransformIOAttr)


    def hook(self):
        """ Mount a dictionary with guide modules hierarchies.
            Return a dictionary with the father and children lists inside of each guide like:
            {guide{'guideModuleNamespace':"...", 'guideModuleName':"...", 'guideCustomName':"...", 'guideMirrorAxis':"...", 'guideMirrorName':"...", 'fatherGuide':"...", 'fatherNode':"...", 'fatherModule':"...", 'fatherCustomName':"...", 'fatherMirrorAxis':"...", 'fatherMirrorName':"...", 'fatherGuideLoc':"...", 'childrenList':[...]}}
        """
        hookDic = {}
        allList = cmds.ls(type='transform')
        for item in allList:
            if cmds.objExists(item+".guideBase") and cmds.getAttr(item+".guideBase") == 1:
                # module info:
                guideModuleNamespace = item[:item.find(":")]
                guideModuleName      = item[:item.find("__")]
                guideInstance        = item[item.rfind("__")+2:item.find(":")]
                guideCustomName      = cmds.getAttr(item+".customName")
                guideMirrorAxis      = cmds.getAttr(item+".mirrorAxis")
                tempAMirrorName      = cmds.getAttr(item+".mirrorName")
                guideMirrorName      = [tempAMirrorName[0]+"_" , tempAMirrorName[len(tempAMirrorName)-1:]+"_"]
                
                # get children:
                guideChildrenList = []
                childrenList = cmds.listRelatives(item, allDescendents=True, type='transform')
                if childrenList:
                    for child in childrenList:
                        if cmds.objExists(child+".guideBase"):
                            if cmds.getAttr(child+".guideBase") == 1:
                                guideChildrenList.append(child)
                        if cmds.objExists(child+".hookNode"):
                            hookNode = cmds.getAttr(child+".hookNode")
                
                # get father:
                guideParentList = []
                fatherNodeList = []
                parentNode = ""
                parentList = cmds.listRelatives(item, parent=True, type='transform')
                if parentList:
                    nextLoop = True
                    while nextLoop:
                        if cmds.objExists(parentList[0]+".guideBase") and cmds.getAttr(parentList[0]+".guideBase") == 1:
                            guideParentList.append(parentList[0])
                            nextLoop = False
                        else:
                            if not fatherNodeList:
                                fatherNodeList.append(parentList[0])
                            parentList = cmds.listRelatives(parentList[0], parent=True, type='transform')
                            if parentList:
                                nextLoop = True
                            else:
                                nextLoop = False
                    if guideParentList:
                        # father info:
                        guideParent      = guideParentList[0]
                        fatherModule     = guideParent[:guideParent.find("__")]
                        fatherInstance   = guideParent[guideParent.rfind("__")+2:guideParent.find(":")]
                        fatherCustomName = cmds.getAttr(guideParent+".customName")
                        fatherMirrorAxis = cmds.getAttr(guideParent+".mirrorAxis")
                        tempBMirrorName  = cmds.getAttr(guideParent+".mirrorName")
                        fatherMirrorName = [tempBMirrorName[0]+"_" , tempBMirrorName[len(tempBMirrorName)-1:]+"_"]
                        if fatherNodeList:
                            fatherGuideLoc = fatherNodeList[0][fatherNodeList[0].find("Guide_")+6:]
                        else:
                            guideParentChildrenList = cmds.listRelatives(guideParent, children=True, type='transform')
                            if guideParentChildrenList:
                                for guideParentChild in guideParentChildrenList:
                                    if cmds.objExists(guideParentChild+'.nJoint'):
                                        if cmds.getAttr(guideParentChild+'.nJoint') == 1:
                                            if guideParent[:guideParent.rfind(":")] in guideParentChild:
                                                fatherNodeList = [guideParentChild]
                                                fatherGuideLoc = guideParentChild[guideParentChild.find("Guide_")+6:]
                    
                    # parentNode info:
                    parentNode = cmds.listRelatives(item, parent=True, type='transform')[0]
                
                # mounting dictionary:
                if guideParentList and guideChildrenList:
                    hookDic[item]={"guideModuleNamespace":guideModuleNamespace, "guideModuleName":guideModuleName, "guideInstance":guideInstance, "guideCustomName":guideCustomName, "guideMirrorAxis":guideMirrorAxis, "guideMirrorName":guideMirrorName, "fatherGuide":guideParent, "fatherNode":fatherNodeList[0], "fatherModule":fatherModule, "fatherInstance":fatherInstance, "fatherCustomName":fatherCustomName, "fatherMirrorAxis":fatherMirrorAxis, "fatherMirrorName":fatherMirrorName, "fatherGuideLoc":fatherGuideLoc, "parentNode":parentNode, "childrenList":guideChildrenList}
                elif guideParentList:
                    hookDic[item]={"guideModuleNamespace":guideModuleNamespace, "guideModuleName":guideModuleName, "guideInstance":guideInstance, "guideCustomName":guideCustomName, "guideMirrorAxis":guideMirrorAxis, "guideMirrorName":guideMirrorName, "fatherGuide":guideParent, "fatherNode":fatherNodeList[0], "fatherModule":fatherModule, "fatherInstance":fatherInstance, "fatherCustomName":fatherCustomName, "fatherMirrorAxis":fatherMirrorAxis, "fatherMirrorName":fatherMirrorName, "fatherGuideLoc":fatherGuideLoc, "parentNode":parentNode, "childrenList":[]}
                elif guideChildrenList:
                    hookDic[item]={"guideModuleNamespace":guideModuleNamespace, "guideModuleName":guideModuleName, "guideInstance":guideInstance, "guideCustomName":guideCustomName, "guideMirrorAxis":guideMirrorAxis, "guideMirrorName":guideMirrorName, "fatherGuide":"", "fatherNode":"", "fatherModule":"", "fatherInstance":"", "fatherCustomName":"", "fatherMirrorAxis":"", "fatherMirrorName":"", "fatherGuideLoc":"", "parentNode":parentNode, "childrenList":guideChildrenList}
                else:
                    hookDic[item]={"guideModuleNamespace":guideModuleNamespace, "guideModuleName":guideModuleName, "guideInstance":guideInstance, "guideCustomName":guideCustomName, "guideMirrorAxis":guideMirrorAxis, "guideMirrorName":guideMirrorName, "fatherGuide":"", "fatherNode":"", "fatherModule":"", "fatherInstance":"", "fatherCustomName":"", "fatherMirrorAxis":"", "fatherMirrorName":"", "fatherGuideLoc":"", "parentNode":parentNode, "childrenList":[]}
        return hookDic


    def distanceBet(self, a, b, name="temp_DistBet", keep=False):
        """ Creates a distance between node for 2 objects a and b.
            Keeps them in the scene or delete.
            Returns the distance value only in case of not keeping distBet node or
            a list of distance value, distanceNode, two nulls used to calculate and the created constraint.
        """
        if cmds.objExists(a) and cmds.objExists(b):
            # create nulls:
            nullA = cmds.group(empty=True, name=a+"_DistBetNull_Grp")
            nullB = cmds.group(empty=True, name=b+"_DistBetNull_Grp")
            nullC = cmds.group(empty=True, name=b+"_DistBetNull_OrigRef_Grp")
            cmds.pointConstraint(a, nullA, maintainOffset=False, name=nullA+"_PaC")
            cmds.pointConstraint(b, nullB, maintainOffset=False, name=nullB+"_PaC")
            cmds.delete(cmds.pointConstraint(b, nullC, maintainOffset=False))
            pointConst = cmds.pointConstraint(b, nullC, nullB, maintainOffset=False, name=nullB+"_PaC")[0]
            # create distanceBetween node:
            distBet = cmds.createNode("distanceBetween", n=name)
            # connect aPos to the distance between point1:
            cmds.connectAttr(nullA+".tx", distBet+".point1X")
            cmds.connectAttr(nullA+".ty", distBet+".point1Y")
            cmds.connectAttr(nullA+".tz", distBet+".point1Z")
            # connect bPos to the distance between point2:
            cmds.connectAttr(nullB+".tx", distBet+".point2X")
            cmds.connectAttr(nullB+".ty", distBet+".point2Y")
            cmds.connectAttr(nullB+".tz", distBet+".point2Z")
            dist = cmds.getAttr(distBet+".distance")
            if keep:
                self.addCustomAttr([nullA, nullB, nullC], self.ignoreTransformIOAttr)
                self.dpUIinst.customAttr.addAttr(0, [distBet]) #dpID
                return [dist, distBet, nullA, nullB, nullC, pointConst]
            else:
                cmds.delete(distBet, nullA, nullB, nullC, pointConst)
                return [dist, None, None, None, None, None]


    def middlePoint(self, a, b, createLocator=False):
        """ UNUSED...
            Find the point location in the middle of two items.
            Return the middle point position as a vector and a locator in that postition if wanted.
        """
        if cmds.objExists(a) and cmds.objExists(b):
            # get xform datas:
            aPos = cmds.xform(a, query=True, worldSpace=True, rotatePivot=True)
            bPos = cmds.xform(b, query=True, worldSpace=True, rotatePivot=True)
            # calculating the result position:
            resultPosX = ( aPos[0] + bPos[0] )/2
            resultPosY = ( aPos[1] + bPos[1] )/2
            resultPosZ = ( aPos[2] + bPos[2] )/2
            resultPos = [resultPosX, resultPosY, resultPosZ]
            if createLocator:
                middleLoc = cmds.spaceLocator(name=a+"_"+b+"_Middle_Loc", position=resultPos)[0]
                cmds.xform(middleLoc, centerPivots=True)
                return [resultPos, middleLoc]
            return[resultPos]


    def clearNodeGrp(self, nodeGrpName='dpAR_GuideMirror_Grp', attrFind='guideBaseMirror', unparent=False):
        """ Check if there is any node with the attribute attrFind in the nodeGrpName and then unparent its children and delete it.
        """
        if cmds.objExists(nodeGrpName):
            if cmds.listRelatives(nodeGrpName, children=True, allDescendents=True, type="transform"):
                foundChildrenList = [child for child in cmds.listRelatives(nodeGrpName, children=True, allDescendents=True, type="transform") if attrFind in cmds.listAttr(child) and cmds.getAttr(child+"."+attrFind) == 1]
                if foundChildrenList:
                    if unparent:
                        fatherList = cmds.listRelatives(nodeGrpName, parent=True)
                        for child in foundChildrenList:
                            if nodeGrpName.split(":")[0] in cmds.listRelatives(child, parent=True)[0]:
                                if fatherList:
                                    cmds.parent(child, fatherList[0])
                                else:
                                    cmds.parent(child, world=True)
            cmds.delete(nodeGrpName)


    def getGuideChildrenList(self, nodeName):
        """ This function verify if there are guide children of the passed nodeName.
            It will return the guideChildrenList if it exists.
        """
        guideChildrenList = []
        if cmds.objExists(nodeName):
            childrenList = cmds.listRelatives(nodeName, allDescendents=True, type='transform')
            if childrenList:
                for child in childrenList:
                    if cmds.objExists(child+".guideBase") and cmds.getAttr(child+".guideBase") == 1:
                        guideChildrenList.append(child)
        return guideChildrenList


    def mirroredGuideFather(self, nodeName):
        """ This function verify if there is a mirrored guide as a father of the passed nodeName.
            Returns the mirrored guide father name if true.
        """
        parentList = cmds.listRelatives(nodeName, parent=True, type='transform')
        if parentList:
            nextLoop = True
            while nextLoop:
                if cmds.objExists(parentList[0]+".guideBase") and cmds.getAttr(parentList[0]+".guideBase") == 1 and cmds.getAttr(parentList[0]+".mirrorEnable") == 1 and cmds.getAttr(parentList[0]+".mirrorAxis") != "off":
                    return parentList[0]
                    nextLoop = False
                else:
                    parentList = cmds.listRelatives(parentList[0], parent=True, type='transform')
                    if parentList:
                        nextLoop = True
                    else:
                        nextLoop = False


    def getParentsList(self, nodeName):
        """ Get all parents.
            Return a list with all parents if they exists.
        """
        # get father:
        allParentsList = []
        parentList = cmds.listRelatives(nodeName, parent=True, type='transform')
        if parentList:
            nextLoop = True
            while nextLoop:
                allParentsList.append(parentList[0])
                parentList = cmds.listRelatives(parentList[0], parent=True, type='transform')
                if not parentList:
                    nextLoop = False
        return allParentsList


    def getModulesToBeRigged(self, instanceList):
        """ Get all valid loaded modules to be rigged (They are valid instances with namespaces in the scene, then they are not deleted).
            Currently named as rawGuide instances.
            Return a list of modules to be rigged.
        """
        modulesToBeRiggedList = []
        headModuleList = []
        allNamespaceList = cmds.namespaceInfo(listNamespace=True)
        for guideModule in instanceList:
            # verify integrity of the guideModule:
            if guideModule.verifyGuideModuleIntegrity():
                guideNamespaceName = guideModule.guideNamespace
                if guideNamespaceName in allNamespaceList:
                    userGuideName = guideModule.userGuideName
                    if not cmds.objExists(userGuideName+'_Static_Grp'):
                        if not "dpHead" in str(guideModule):
                            modulesToBeRiggedList.append(guideModule)
                        else:
                            # store Head guides to rig it later
                            headModuleList.append(guideModule)
        if headModuleList:
            # hack to rig Head modules at the end in order to call FacialConnection properly for joint target Singles tweakers.
            modulesToBeRiggedList.extend(headModuleList)
        return modulesToBeRiggedList


    def getCtrlRadius(self, nodeName):
        """ Calculate and return the final radius to be used as a size of controls.
        """
        radius = float(cmds.getAttr(nodeName+".translateX"))
        parentList = self.getParentsList(nodeName)
        if (parentList):
            for parent in parentList:
                radius *= cmds.getAttr(parent+'.scaleX')
                if "worldSize" in cmds.listAttr(parent):
                    radius *= cmds.getAttr(parent+".worldSize")
        return radius


    def zeroOutJoints(self, jntList=None, displayBone=False):
        """ Duplicate the joints, parent as zeroOut.
            Returns the father joints (zeroOuted).
        """
        resultList = []
        zeroOutJntSuffix = "_Jzt"
        if jntList:
            for jnt in jntList:
                if cmds.objExists(jnt):
                    jxtName = jnt.replace("_Jnt", "").replace("_"+zeroOutJntSuffix, "")
                    if not zeroOutJntSuffix in jxtName:
                        jxtName += zeroOutJntSuffix
                    dup = cmds.duplicate(jnt, name=jxtName)[0]
                    self.deleteChildren(dup)
                    self.clearDpArAttr([dup])
                    self.deleteJointLabel(dup)
                    cmds.parent(jnt, dup)
                    if not displayBone:
                        cmds.setAttr(dup+".drawStyle", 2) #none
                    self.dpUIinst.customAttr.addAttr(0, [dup]) #dpID
                    resultList.append(dup)
        return resultList


    def clearDpArAttr(self, itemList):
        """ Delete all dpAR (dpAutoRigSystem) attributes in this joint
        """
        dpArAttrList = ['dpAR_joint']
        if itemList:
            for item in itemList:
                for dpArAttr in dpArAttrList:
                    if cmds.objExists(item+"."+dpArAttr):
                        cmds.deleteAttr(item+"."+dpArAttr)


    def deleteChildren(self, item):
        """ Delete all child of the item node passed as argument.
        """
        if(cmds.objExists(item)):
            childrenList = cmds.listRelatives(item, children=True, fullPath=True)
            if(childrenList):
                for child in childrenList:
                    cmds.delete(child)


    def setJointLabel(self, jointName, sideNumber, typeNumber, labelString):
        """ Set joint labelling in order to help Maya calculate the skinning mirror correctly.
            side:
                0 = Center
                1 = Left
                2 = Right
            type:
                18 = Other
        """
        cmds.setAttr(jointName+".side", sideNumber)
        cmds.setAttr(jointName+".type", typeNumber)
        if typeNumber == 18: #other
            cmds.setAttr(jointName+".otherType", labelString, type="string")


    def deleteJointLabel(self, jointName):
        """ Set joint labelling to
            side = None
            type = Other
            other type = ""
        """
        cmds.setAttr(jointName+".side", 3)#None
        cmds.setAttr(jointName+".type", 18)#Other
        cmds.setAttr(jointName+".otherType", "", type="string")


    def extractSuffix(self, nodeName):
        """ Remove suffix from a node name and return the base name.
        """
        endSuffixList = ["_Mesh", "_Msh", "_Geo", "_Ges", "_Tgt", "_Ctrl", "_Grp", "_Crv"]
        for endSuffix in endSuffixList:
            if nodeName.endswith(endSuffix):
                baseName = nodeName[:nodeName.rfind(endSuffix)]
                return baseName
            if nodeName.endswith(endSuffix.lower()):
                baseName = nodeName[:nodeName.rfind(endSuffix.lower())]
                return baseName
            if nodeName.endswith(endSuffix.upper()):
                baseName = nodeName[:nodeName.rfind(endSuffix.upper())]
                return baseName
        return nodeName


    def filterName(self, name, itemList, separator):
        """ Filter list with the name or a list of name as a string separated by the separator (usually a space).
            Returns the filtered list.
        """
        filteredList = []
        multiFilterList = [name]
        if separator in name:
            multiFilterList = list(name.split(separator))
        for filterName in multiFilterList:
            if filterName:
                for item in itemList:
                    if str(filterName) in item:
                        if not item in filteredList:
                            filteredList.append(item)
        return filteredList
        
        
    def checkRawURLForUpdate(self, DPAR_VERSION, rawURL, *args):
        """ Check for update using raw url.
            Compares the remote version from GitHub to the current version.
            
            Returns a list with CheckedNumber and RemoteVersion or None.
            
            CheckedNumber:
                    0 - the current version is up to date
                    1 - there's a new version
                    2 - remote file not found using given raw url
                    3 - internet connection fail (probably)
                    4 - error
                    
            if we have an update to do:
                return [CheckedNumber, RemoteVersion, RemoteLog]
            if not or ok:
                return [CheckedNumber, None]
        """
        try:
            gotRemoteFile = False
            # getting dpAutoRig.py file from GitHub website using the Raw URL:
            remoteSource = urllib.request.urlopen(rawURL)
            remoteContents = TextIOWrapper(remoteSource, encoding='utf-8')
            # find the line with the version and compare them:
            for line in remoteContents:
                if "DPAR_VERSION_PY3 = " in line:
                    gotRemoteFile = True
                    remoteVersion = line[20:-2] #these magic numbers filter only the version XX.YY.ZZ
                    if remoteVersion == self.dpUIinst.dpARVersion:
                        # 0 - the current version is up to date
                        return [0, None, None]
                    else:
                        # 1 - there's a new version
                        for extraLine in remoteContents:
                            if "DPAR_UPDATELOG = " in extraLine:
                                remoteLog = extraLine[18:-2] #these magic numbers filter only the log string sentence
                                return [1, remoteVersion, remoteLog]
                        return [1, remoteVersion, None]
            if not gotRemoteFile:
                # 2 - remote file not found using given raw url
                return [2, None, None]
        except:
            # 3 - internet connection fail (probably)
            return [3, None, None]
        # 4 - error
        return [4, None, None]


    def visitWebSite(self, website, *args):
        """ Start browser with the given website address.
        """
        #webSiteString = "start "+website
        #os.popen(webSiteString)
        webbrowser.open(website, new=2)
        
        
    def checkLoadedPlugin(self, pluginName, message="Not loaded plugin", *args):
        """ Check if plugin is loaded and try to load it.
            Returns True if ok (loaded)
            Returns False if not found or not loaded.
        """
        loadedPlugin = True
        if not (cmds.pluginInfo(pluginName, query=True, loaded=True)):
            loadedPlugin = False
            try:
                cmds.loadPlugin(pluginName+".mll")
                loadedPlugin = True
            except:
                pass
        if not loadedPlugin:
            print(message, pluginName)
        return loadedPlugin
        
        
    def twistBoneMatrix(self, nodeA, nodeB, twistBoneName, twistBoneMD=None, axis='Z', inverse=True, *args):
        """ Create matrix nodes and quaternion to extract rotate.
            nodeA = father transform node
            nodeB = child transform node
            Returns the final multiplyDivide node created or given.
            Reference:
            https://bindpose.com/maya-matrix-nodes-part-2-node-based-matrix-twist-calculator/
        """
        twistBoneMM = cmds.createNode("multMatrix", name=twistBoneName+"_ExtractAngle_MM")
        twistBoneDM = cmds.createNode("decomposeMatrix", name=twistBoneName+"_ExtractAngle_DM")
        twistBoneQtE = cmds.createNode("quatToEuler", name=twistBoneName+"_ExtractAngle_QtE")
        cmds.connectAttr(nodeB+".worldMatrix[0]", twistBoneMM+".matrixIn[0]", force=True)
        if inverse:
            cmds.connectAttr(nodeA+".worldInverseMatrix[0]", twistBoneMM+".matrixIn[1]", force=True)
        else:
            cmds.connectAttr(nodeA+".worldMatrix[0]", twistBoneMM+".matrixIn[1]", force=True)
        cmds.connectAttr(twistBoneMM+".matrixSum", twistBoneDM+".inputMatrix", force=True)
        cmds.connectAttr(twistBoneDM+".outputQuat.outputQuat"+axis, twistBoneQtE+".inputQuat.inputQuat"+axis, force=True)
        cmds.connectAttr(twistBoneDM+".outputQuat.outputQuatW", twistBoneQtE+".inputQuat.inputQuatW", force=True)
        if twistBoneMD:
            cmds.connectAttr(twistBoneQtE+".outputRotate.outputRotate"+axis, twistBoneMD+".input2"+axis, force=True)
        else:
            twistBoneMD = cmds.createNode("multiplyDivide", name=twistBoneName+"_MD")
            cmds.connectAttr(twistBoneQtE+".outputRotate.outputRotate"+axis, twistBoneMD+".input2"+axis, force=True)
        self.dpUIinst.customAttr.addAttr(0, [twistBoneMM, twistBoneDM, twistBoneQtE, twistBoneMD]) #dpID
        return twistBoneMD
        

    def validateName(self, nodeName, suffix=None, *args):
        """ Check the default name in order to validate it and preserves the suffix naming.
            Returns the correct node name.
        """
        if cmds.objExists(nodeName):
            needRestoreSuffix = False
            if suffix:
                if nodeName.endswith("_"+suffix):
                    needRestoreSuffix = True
                    nodeName = nodeName[:nodeName.rfind("_")]
            # find numering:
            i = 1
            if not needRestoreSuffix:
                while cmds.objExists(nodeName+str(i)):
                    i += 1
            else:
                while cmds.objExists(nodeName+str(i)+"_"+suffix):
                    i += 1
            # add number:
            nodeName = nodeName+str(i)
            if needRestoreSuffix:
                # restore suffix
                nodeName = nodeName+"_"+suffix
        return nodeName


    def articulationJoint(self, fatherNode, brotherNode, jcrNumber=0, jcrPosList=None, jcrRotList=None, dist=1, jarRadius=1.5, doScale=True, *args):
        """ Create a simple joint to help skinning with a half rotation value.
            Receives the number of corrective joints to be created. Zero by default.
            Place these corrective joints with the given vector list.
            Returns the created joint list.
        """
        jointList = []
        if fatherNode and brotherNode:
            if cmds.objExists(fatherNode) and cmds.objExists(brotherNode):
                jaxName = brotherNode[:brotherNode.rfind("_")]+"_Jax"
                jarName = brotherNode[:brotherNode.rfind("_")]+"_Jar"
                cmds.select(clear=True)
                jax = cmds.joint(name=jaxName, radius=0.5*jarRadius)
                jar = cmds.joint(name=jarName, radius=jarRadius)
                cmds.addAttr(jar, longName='dpAR_joint', attributeType='float', keyable=False)
                cmds.delete(cmds.parentConstraint(brotherNode, jax, maintainOffset=0))
                cmds.parent(jax, fatherNode)
                cmds.makeIdentity(jax, apply=True)
                cmds.setAttr(jax+".segmentScaleCompensate", 0)
                cmds.setAttr(jar+".segmentScaleCompensate", 1)
                jointList.append(jar)
                for i in range(0, jcrNumber):
                    cmds.select(jar)
                    jcr = cmds.joint(name=brotherNode[:brotherNode.rfind("_")+1]+str(i)+"_Jcr")
                    cmds.setAttr(jcr+".segmentScaleCompensate", 0)
                    cmds.addAttr(jcr, longName='dpAR_joint', attributeType='float', keyable=False)
                    if jcrPosList:
                        cmds.setAttr(jcr+".translateX", jcrPosList[i][0]*dist)
                        cmds.setAttr(jcr+".translateY", jcrPosList[i][1]*dist)
                        cmds.setAttr(jcr+".translateZ", jcrPosList[i][2]*dist)
                    if jcrRotList:
                        cmds.setAttr(jcr+".rotateX", jcrRotList[i][0])
                        cmds.setAttr(jcr+".rotateY", jcrRotList[i][1])
                        cmds.setAttr(jcr+".rotateZ", jcrRotList[i][2])
                    jointList.append(jcr)
                cmds.pointConstraint(brotherNode, jax, maintainOffset=True, name=jarName+"_PoC")[0]
                oc = cmds.orientConstraint(fatherNode, brotherNode, jax, maintainOffset=True, name=jarName+"_OrC")[0]
                cmds.setAttr(oc+".interpType", 2) #shortest
                if doScale:
                    cmds.scaleConstraint(fatherNode, brotherNode, jax, maintainOffset=True, name=jarName+"_ScC")
                return jointList


    def getNodeByMessage(self, attrName, node=None, *args):
        """ Get connected node in the given attribute searching as message.
            If there isn't a given node, try to use All_Grp.
            Return the found node name or False if it wasn't found.
        """
        result = False
        if not node:
            # try to find All_Grp
            allTransformList = cmds.ls(selection=False, type="transform")
            if allTransformList:
                for transform in allTransformList:
                    if cmds.objExists(transform+".masterGrp"):
                        if cmds.getAttr(transform+".masterGrp") == 1:
                            node = transform #All_Grp found
                            break
        if node:
            if cmds.objExists(node+"."+attrName):
                foundNodeList = cmds.listConnections(node+"."+attrName, source=True, destination=False)
                if foundNodeList:
                    result = foundNodeList[0]
        return result


    def attachToMotionPath(self, nodeName, curveName, mopName, uValue):
        """ Simple function to attach a node in a motion path curve.
            Sets the u position based to given uValue.
            Returns the created motion path node.
        """
        moPath = cmds.pathAnimation(nodeName, curve=curveName, fractionMode=True, name=mopName)
        cmds.delete(cmds.listConnections(moPath+".u", source=True, destination=False)[0])
        cmds.setAttr(moPath+".u", uValue)
        return moPath
        

    #Profiler decorator
    def profiler(func):
        DPAR_PROFILE_MODE = False
        def runProfile(*args, **kwargs):
            if DPAR_PROFILE_MODE:
                pProf = cProfile.Profile()
                try:
                    pProf.enable()
                    pResult = func(*args, **kwargs)
                    pProf.disable()
                    return pResult
                finally:
                    pProf.print_stats()
            else:
                pResult = func(*args, **kwargs)
                return pResult
        return runProfile

    '''
    Open Maya Utils Functions
    '''

    def extract_world_scale_from_matrix(self, obj):
        world_matrix = cmds.getAttr(obj + ".worldMatrix")
        mMat = om.MMatrix()
        om.MScriptUtil.createMatrixFromList(world_matrix, mMat)
        mTransform = om.MTransformationMatrix(mMat)
        scale_util = om.MScriptUtil()
        scale_util.createFromDouble(0.0, 0.0, 0.0)
        ptr = scale_util.asDoublePtr()
        mTransform.getScale(ptr, om.MSpace.kWorld)

        x_scale = om.MScriptUtil.getDoubleArrayItem(ptr, 0)
        y_scale = om.MScriptUtil.getDoubleArrayItem(ptr, 1)
        z_scale = om.MScriptUtil.getDoubleArrayItem(ptr, 2)

        return [x_scale, y_scale, z_scale]


    def resolveName(self, name, suffix, *args):
        """ Resolve repeated name adding number in the middle of the string.
            Returns the resolved baseName and name (including the suffix).
        """
        name = name[0].upper()+name[1:].replace(" ", "_")
        baseName = name
        name = name+"_00_"+suffix
        if cmds.objExists(name):
            i = 1
            while cmds.objExists(name):
                name = baseName+"_"+str(i).zfill(2)+"_"+suffix
                i = i+1
            baseName = baseName+"_"+str(i-1).zfill(2)
        else:
            baseName = baseName+"_00"
        return baseName, name


    def magnitude(self, v, *args):
        """ Returns the square root of the sum of power 2 from a given vector.
        """
        return math.sqrt(pow(v[0], 2)+pow(v[1], 2)+pow(v[2], 2))


    def normalizeVector(self, v):
        """ Returns the normalized given vector.
        """
        vMag = self.magnitude(v)
        return [v[i]/vMag for i in range(len(v))]


    def distanceVectors(self, u, v):
        """ Returns the distance between 2 given points.
        """
        return math.sqrt((v[0]-u[0])**2+(v[1]-u[1])**2+(v[2]-u[2])**2)


    def addVectors(self, u, v):
        """ Returns the addition of 2 given vectors.
        """
        return [u[i]+v[i] for i in range(len(u))]


    def subVectors(self, u, v):
        """ Returns the substration of 2 given vectors.
        """
        return [u[i]-v[i] for i in range(len(u))]


    def multVectors(self, u, v):
        return [u[i]*v[i] for i in range(len(u))]


    def multiScalarVector(self, u, scalar):
        return [u[i]*scalar for i in range(len(u))]


    def averageValue(self, valueList, *args):
        """ Return the average value for the given value list.
        """
        return sum(valueList)/len(valueList)


    def jointChainLength(self, jointList):
        """ Returns a sum of the joint lengths given.
        """
        i = 0
        chainlength = 0
        if jointList:
            while ( i < len(jointList) - 1 ):
                if cmds.objExists(jointList[i]):
                    if cmds.objExists(jointList[i+1]):
                        a = cmds.xform(jointList[i], query=True, pivots=True, worldSpace=True)
                        b = cmds.xform(jointList[i+1], query=True, pivots=True, worldSpace=True)
                        x = b[0] - a[0]
                        y = b[1] - a[1]
                        z = b[2] - a[2]
                        v = [x,y,z]
                        chainlength += self.magnitude(v)
                i += 1
        return chainlength


    def unlockAttr(self, nodeList):
        attrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']
        for node in nodeList:
            if cmds.objExists(node):
                for attr in attrList:
                    cmds.setAttr(node+"."+attr, lock=False)


    def exportLogDicToJson(self, dic, name=None, path=None, subFolder=None):
        """ Save to path the given dictionary as a json file.
        """
        currentTime = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        if not path:
            path = cmds.file(query=True, sceneName=True)
        if path:
            dpFolder = path[:path.rfind("/")]
            if subFolder:
                dpFolder = dpFolder+"/"+subFolder
            if not os.path.exists(dpFolder):
                os.makedirs(dpFolder)
            if not name:
                name = path[path.rfind("/")+1:path.rfind(".")]
            pathFile = dpFolder+"/dpLog_"+name+"_"+currentTime+".json"
        else:
            return False
        print("\nLog file", pathFile)
        outFile = open(pathFile, "w")
        json.dump(dic, outFile, indent=4)
        outFile.close()
        return pathFile


    def dpCreateValidatorPreset(self, *args):
        """ Creates a json file as a Validator Preset and returns it.
        """
        resultString = None
        validatorsList = self.dpUIinst.checkInInstanceList + self.dpUIinst.checkOutInstanceList + self.dpUIinst.checkAddOnsInstanceList
        if validatorsList:
            resultDialog = cmds.promptDialog(
                                                title=self.dpUIinst.lang['i129_createPreset'],
                                                message=self.dpUIinst.lang['i130_presetName'],
                                                button=[self.dpUIinst.lang['i131_ok'], self.dpUIinst.lang['i132_cancel']],
                                                defaultButton=self.dpUIinst.lang['i131_ok'],
                                                cancelButton=self.dpUIinst.lang['i132_cancel'],
                                                dismissString=self.dpUIinst.lang['i132_cancel'])
            if resultDialog == self.dpUIinst.lang['i131_ok']:
                resultName = cmds.promptDialog(query=True, text=True)
                resultName = resultName[0].upper()+resultName[1:]
                author = getpass.getuser()
                date = str(datetime.datetime.now().date())
                resultString = '{"_preset":"'+resultName+'","_author":"'+author+'","_date":"'+date+'","_updated":"'+date+'"'
                # add validators and its current active values
                for validator in validatorsList:
                    resultString += ',"'+validator.guideModuleName+'" : '+str(validator.active).lower()
                resultString += "}"
        return resultString


    def closeUI(self, winName):
        """ Closes the given window name if it exists.
        """
        if cmds.window(winName, query=True, exists=True):
            cmds.deleteUI(winName, window=True)


    def generateID(self, name):
        """ Return an ID generated by the sum of the "dp" string, plus the given name, plus dot, plus the current time.
        """
        now = str(round(time.time()*10000000000000))
        word = ("dp"+str(name)).encode('utf-8').hex()
        return word+"."+now


    def getDecomposedIDList(self, id, *args):
        """ Returns a list with prefix, name and date from decomposed given dpID.
        """
        word, now = id.split(".")
        info = bytes.fromhex(word).decode('utf-8')
        prefix = info[0:2]
        name = info[2:]
        date = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(int(now)/10000000000000))
        return [prefix, name, date]


    def decomposeID(self, item, *args):
        """ Return a list with the name and date decomposed from dpID attribute of the given node.
        """
        if cmds.attributeQuery(self.dpID, node=item, exists=True):
            id = cmds.getAttr(item+"."+self.dpID)
            return self.getDecomposedIDList(id)
        return [None, None, None]
    

    def validateID(self, item, *args):
        """ Return True if the decomposed name in the dpID is equal to the given node name.
        """
        if cmds.attributeQuery(self.dpID, node=item, exists=True):
            decomposedIDList = self.decomposeID(item)
            if "dp" == decomposedIDList[0]:
                if item == decomposedIDList[1]:
                    return True


    def checkSavedScene(self):
        """ Check if the current scene is saved to return True.
            Otherwise return False.
        """
        scenePath = cmds.file(query=True, sceneName=True)
        modifiedScene = cmds.file(query=True, modified=True)
        if not scenePath or modifiedScene:
            return False
        return True


    def mountWH(self, start, end):
        """ Mount and return path.
        """
        return "{}{}{}".format(start, "/", end)


    def clearJointLabel(self, jointList):
        """ Just remove the current joint label if it exists.
        """
        if jointList:
            for jnt in jointList:
                if cmds.objExists(jnt):
                    cmds.setAttr(jnt+".otherType", "", type="string")
                    cmds.setAttr(jnt+".type", 0)


    def createJointBlend(self, jointListA, jointListB, jointListC, attrName, attrStartName, worldRef, storeName=True):
        """ Create an Ik Fk Blend setup for joint chain.
            Return the created reverse node.
        """
        attrCompName = attrStartName[0].lower()+attrStartName[1:]+attrName
        for n in range(len(jointListA)):
            parentConst = cmds.parentConstraint(jointListA[n], jointListB[n], jointListC[n], maintainOffset=True, name=jointListC[n]+"_"+attrName+"_PaC")[0]
            cmds.setAttr(parentConst+".interpType", 2) #shortest
            if n == 0:
                revNode = cmds.createNode('reverse', name=jointListC[n]+"_"+attrName+"_Rev")
                self.dpUIinst.customAttr.addAttr(0, [revNode]) #dpID
                cmds.addAttr(worldRef, longName=attrCompName, attributeType='float', minValue=0, maxValue=1, defaultValue=0, keyable=True)
                cmds.addAttr(worldRef, longName=attrCompName+"RevOutputX", attributeType="float", keyable=False)
                if storeName:
                    cmds.addAttr(worldRef, longName="ikFkBlendAttrName", dataType="string")
                    cmds.setAttr(worldRef+".ikFkBlendAttrName", attrCompName, type="string")
                cmds.connectAttr(worldRef+"."+attrCompName, revNode+".inputX", force=True)
                cmds.connectAttr(revNode+".outputX", worldRef+"."+attrCompName+"RevOutputX", force=True)
            # connecting ikFkBlend using the reverse node:
            cmds.connectAttr(worldRef+"."+attrCompName, parentConst+"."+jointListB[n]+"W1", force=True)
            cmds.connectAttr(worldRef+"."+attrCompName+"RevOutputX", parentConst+"."+jointListA[n]+"W0", force=True)
        return revNode


    def getAttrNameLower(self, side, name):
        """ Return the composed name for attributes starting with lower case.
        """
        attrNameLower = name
        if side:
            attrNameLower = side[0]+name
        attrNameLower = attrNameLower[0].lower()+attrNameLower[1:]
        return attrNameLower


    def setAttrValues(self, itemList, attrList, valueList):
        """ Just set the attribute values for the given lists.
        """
        if itemList and attrList and valueList:
            for item in itemList:
                for attr, value in zip(attrList, valueList):
                    cmds.setAttr(item+"."+attr, value)


    def reapplyDeformers(self, item, defList):
        """ Reapply the given deformer list to the destination given item except the tweak node.
        """
        if item and defList:
            if cmds.objExists(item):
                for deformerNode in defList:
                    if cmds.objExists(deformerNode):
                        if not cmds.objectType(deformerNode) == "tweak":
                            cmds.deformer(deformerNode, edit=True, geometry=item)


    def getNetworkNodeByAttr(self, netAttr, *args):
        """ Returns a list of network nodes with the boolean given net attribute active.
        """
        netList = []
        allNetList = cmds.ls(selection=False, type="network")
        if allNetList:
            for item in allNetList:
                if cmds.objExists(item+".dpNetwork"):
                    if cmds.getAttr(item+".dpNetwork") == 1:
                        if cmds.objExists(item+"."+netAttr):
                            if cmds.getAttr(item+"."+netAttr) == 1:
                                netList.append(item)
        return netList


    def filterTransformList(self, itemList, filterCamera=True, filterConstraint=True, filterFollicle=True, filterJoint=True, filterLocator=True, filterHandle=True, filterLinearDeform=True, filterEffector=True, filterBaseNode=True, verbose=True, title="Rigging", *args):
        """ Remove camera, constraints, follicles, etc from the given list and return it.
        """
        cameraList = ["|persp", "|top", "|side", "|front"]
        constraintList = ["parentConstraint", "pointConstraint", "orientConstraint", "scaleConstraint", "aimConstraint", "poleVectorConstraint"]
        toRemoveList = []
        for item in itemList:
            if verbose:
                self.setProgress(title)
            itemType = cmds.objectType(item)
            if filterCamera:
                for cameraName in cameraList:
                    if item.endswith(cameraName):
                        toRemoveList.append(item)
            if filterConstraint:
                if itemType in constraintList:
                    toRemoveList.append(item)
            if filterFollicle:
                if cmds.listRelatives(item, children=True, type="follicle"):
                    toRemoveList.append(item)
            if filterJoint:
                if cmds.listRelatives(item, children=True, type="joint") or itemType == "joint":
                    toRemoveList.append(item)
            if filterLocator:
                if cmds.listRelatives(item, children=True, type="locator"):
                    toRemoveList.append(item)
            if filterHandle:
                if cmds.listRelatives(item, children=True, type="ikHandle") or itemType == "ikHandle":
                    toRemoveList.append(item)
                if cmds.listRelatives(item, children=True, type="clusterHandle") or itemType == "clusterHandle":
                    toRemoveList.append(item)
            if filterLinearDeform:
                for defName in ["deformBend", "deformTwist", "deformSquash", "deformFlare", "deformSine", "deformWave"]:
                    if cmds.listRelatives(item, children=True, type=defName):
                        toRemoveList.append(item)
            if filterEffector:
                if cmds.listRelatives(item, children=True, type="ikEffector") or itemType == "ikEffector":
                    toRemoveList.append(item)
            if filterBaseNode:
                if item in self.baseNodeList:
                    toRemoveList.append(item)
        if toRemoveList:
            toRemoveList = list(set(toRemoveList))
            for toRemoveNode in toRemoveList:
                itemList.remove(toRemoveNode)
        return itemList


    def deleteOrigShape(self, item, deleteIntermediate=True, *args):
        """ Delete Orig shape if it exists.
        """
        #TODO maybe use this command instead?
        #cmds.deformableShape(item, originalGeometry=True)
        if item:
            for child in cmds.listRelatives(item, children=True, allDescendents=True, fullPath=True):
                #if "Orig" in child:
                if child.endswith("Orig"):
                    cmds.delete(child)
                elif cmds.getAttr(child+".intermediateObject") == 1:
                    if deleteIntermediate:
                        cmds.delete(child)
                else:
                    self.removeUserDefinedAttr(child)


    def reapplyDeformers(self, item, defList, *args):
        """ Reapply the given deformer list to the destination given item except the tweak node.
        """
        if cmds.objExists(item):
            for deformerNode in defList:
                if cmds.objExists(deformerNode):
                    if not cmds.objectType(deformerNode) == "tweak":
                        cmds.deformer(deformerNode, edit=True, geometry=item)


    def getTransformData(self, item, t=True, r=True, s=True, useWorldSpace=True, *args):
        """ Return the queried transformation data for the given node.
        """
        resultDic = {}
        if item:
            if cmds.objExists(item):
                if t:
                    resultDic["translation"] = cmds.xform(item, query=True, translation=t, worldSpace=useWorldSpace)
                if r:
                    resultDic["rotation"] = cmds.xform(item, query=True, rotation=r, worldSpace=useWorldSpace)
                if s:
                    resultDic["scale"] = cmds.xform(item, query=True, scale=s, worldSpace=useWorldSpace)
        return resultDic


    def nodeRenamingTreatment(self, itemList=None, nodeType="unitConversion", suffix="_UC", *args):
        """ Rename unitConversion nodes to something like this:
            [IN]capitals+#+attr+_+[OUT]capitals+#+attr+"_UC"
            or the given nodeType and suffix.
        """
        if not itemList:
            itemList = cmds.ls(selection=False, type=nodeType)
        if itemList:
            self.dpUIinst.customAttr.addAttr(0, itemList) #dpID
            for item in itemList:
                if not item.endswith(suffix):
                    if cmds.attributeQuery("input", node=item, exists=True):
                        newName = self.getCapitalsName(cmds.listConnections(item+".input", plugs=True, source=True, destination=False)[0])
                    elif cmds.attributeQuery("input1", node=item, exists=True):
                        newName = self.getCapitalsName(cmds.listConnections(item+".input1", plugs=True, source=True, destination=False)[0])
                    newName += "_"
                    newName += self.getCapitalsName(cmds.listConnections(item+".output", plugs=True, source=False, destination=True)[0])
                    newName += suffix
                    cmds.rename(item, newName)


    def getCapitalsName(self, plug, *args):
        """ Returns a string of all capital letters from a given name.
            Example:
                    Head_Head_Ctrl.rotateX = HHCrotateX
                    L_Arm_Wrist_Ctrl.translateZ = LAWCtranslateZ
        """
        return str("".join([n for n in plug.split(".")[0] if n.isupper() or n.isnumeric()])+plug.split(".")[1].replace("[", "").replace("]", ""))


    def setProgress(self, message="Rigging...", header="dpAutoRigSystem", max=100, amount=0, addOne=True, addNumber=True, endIt=False, isInterruptable=False, *args):
        """ Centralize the progressWindow calling in one method.
            Try to use the cmds.progressWindow as a more automate process.
            
            Arguments:
                message = status
                header = tittle
                max = maxValue
                amount = progress
                addOne = increment amount plus 1
                addNumber = add amount to the end of the message string
                endIt = endProgress
                isInterruptable = if we can interrupt the process or not. False by default.

            Example:
                self.utils.setProgress(messageName, titleName, 20, addOne=False)
                self.dpUIinst.utils.setProgress(doingName+': '+backWheelName)

            Returns the progress: 
                True if the progressWindow is running
                False if the progressWindow was ended or cancelled
        """
        if endIt:
            cmds.progressWindow(endProgress=True)
            self.progress = False
        else:
            if self.progress: #edit
                if addOne:
                    self.currentAmount += 1
                else:
                    self.currentAmount = amount
                if message == "Rigging...":
                    if max > 0:
                        cmds.progressWindow(edit=True, maxValue=max, progress=0)
                else:
                    if addNumber:
                        message = message+" # "+str(self.currentAmount)
                    cmds.progressWindow(edit=True, progress=self.currentAmount, status=message)
            else: #create
                self.currentAmount = amount
                cmds.progressWindow(title=header, progress=self.currentAmount, status=message, maxValue=max, isInterruptable=isInterruptable)
                self.progress = True
        return self.progress


    def getShortName(self, name, *args):
        """ Returns the short name of the given node.
            Example:
            |All_Grp|Render_Grp|Body_Mesh -> BodyMesh
            |pCube1 -> pCube1
        """
        shortName = None
        if name:
            shortName = name
            if "|" in name:
                if name.count("|") > 1:
                    shortName = name[name.rfind("|"):]
                else:
                    shortName = name[1:]
        return shortName


    def deleteFile(self, filePath, *args):
        """ Force delete given file.
        """
        if os.path.exists(filePath):
            try:
                os.remove(filePath)
            except PermissionError as exc:
                # use a brute force to delete without permission:
                os.chmod(filePath, stat.S_IWUSR)
                os.remove(filePath)
