# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "ShaderIO"
TITLE = "r008_shaderIO"
DESCRIPTION = "r009_shaderIODesc"
ICON = "/Icons/dp_shaderIO.png"

DP_SHADERIO_VERSION = 1.02


class ShaderIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_SHADERIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_shaderIO"
        self.startName = "dpShader"
        self.mayaDefaultShader = "openPBRSurface"
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If firstMode parameter is False, it'll run in import mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()
        
        # ---
        # --- rebuilder code --- beginning
        if not cmds.file(query=True, reference=True):
            if self.pipeliner.checkAssetContext():
                self.ioPath = self.getIOPath(self.ioDir)
                if self.ioPath:
                    self.customAttrList = ["aiKdInd", "azimuthalWidthG", "azimuthalShiftG", "intensityG", "longitudinalWidthTRT", "longitudinalShiftTRT", "intensityTRT", 
                                            "longitudinalWidthR", "longitudinalShiftR", "intensityR", "longitudinalWidthTT", "intensityTT", "longitudinalShiftTT", "azimuthalWidthTT",
                                            "longitudinalWidthTT", "angle", "spreadX", "spreadY", "fresnelRefractiveIndex", "specularShift", "scatter", "scatterPower", 
                                            "tubeDirection", "highlightSize", "roughness", "refractions", "refractiveIndex", "refractionLimit", "reflectionLimit", "reflectivity",
                                            "specularRollOff", "eccentricity", "diffuse", "cosinePower", "base", "diffuseRoughness", "metalness", "specular", "specularRoughness",
                                            "specularIOR", "specularAnisotropy", "specularRotation", "transmission", "transmissionDepth", "transmissionScatterAnisotropy", 
                                            "transmissionDispersion", "transmissionExtraRoughness", "subsurface", "subsurfaceScale", "subsurfaceAnisotropy", "coat", "coatRoughness", 
                                            "coatIOR", "coatAnisotropy", "coatRotation", "coatAffectColor", "coatAffectRoughness", "sheen", "sheenRoughness", "emission", "thinFilmThickness",
                                            "thinFilmIOR", "thinWalled",
                                            "baseWeight", "baseDiffuseRoughness", "baseMetalness", "specularWeight", "specularRoughnessAnisotropy", "transmissionWeight",
                                            "transmissionDispersionScale", "transmissionDispersionAbbeNumber", "subsurfaceWeight", "subsurfaceScatterAnisotropy", "fuzzWeight",
                                            "fuzzRoughness", "coatWeight", "coatRoughnessAnisotropy", "coatDarkening", "thinFilmWeight", "emissionLuminance", "geometryThinWalled"]
                    self.vectorColorList = ["outColor", "outTransparency", "outGlowColor", "outMatteOpacity", "colorTT", "colorTRT", "tipColorD", "rootColorD", "whiteness", "reflectedColor",
                                            "specularColor", "transmissionColor", "transmissionScatter", "subsurfaceColor", "coatColor", "sheenColor", "emissionColor",
                                            "ambientColor", "incandescence", "baseColor", "fuzzColor"]
                    self.changedTypeList = ["subsurfaceRadius", "subsurfaceRadiusScale"]
                    if self.firstMode: #export
                        shaderList = None
                        if objList:
                            shaderList = objList
                        else:
                            shaderList = self.getUsedMaterialList()
                        if shaderList:
                            self.exportDicToJsonFile(self.getShaderDataDic(shaderList))
                        else:
                            self.maybeDoneIO("Shading")
                    else: #import
                        shaderDic = self.importLatestJsonFile(self.getExportedList())
                        if shaderDic:
                            try:
                                self.importShader(shaderDic)
                            except Exception as e:
                                self.notWorkedWellIO(self.dpUIinst.lang['r032_notImportedData']+": "+str(e))
                        else:
                            self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])
                else:
                    self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic


    def getShaderDataDic(self, shaderList, *args):
        """ Return shader data dictionary to export.
        """
        shaderDic = {}
        self.utils.setProgress(max=len(shaderList), addOne=False, addNumber=False)
        for shader in shaderList:
            self.utils.setProgress(self.dpUIinst.lang[self.title]+": "+shader)
            fileNode = None
            texture = None
            color = None
            cmds.hyperShade(objects=shader)
            assignedList = cmds.ls(selection=True)
            if assignedList:
                # color
                colorAttr = "color"
                if not colorAttr in cmds.listAttr(shader): #support standardShader
                    colorAttr = "baseColor"
                if colorAttr in cmds.listAttr(shader):
                    shaderConnectionList = cmds.listConnections(shader+"."+colorAttr, destination=False, source=True)
                    if shaderConnectionList:
                        fileNode = shaderConnectionList[0]
                        texture = cmds.getAttr(fileNode+".fileTextureName")
                    else:
                        color = cmds.getAttr(shader+"."+colorAttr)[0]
                # transparency
                transparencyAttr = "transparency"
                if not transparencyAttr in cmds.listAttr(shader): #support standardShader
                    transparencyAttr = "opacity"
                    if not transparencyAttr in cmds.listAttr(shader): #support openPBRShader
                        transparencyAttr = "geometryOpacity"
                        transparency = cmds.getAttr(shader+"."+transparencyAttr)
                    else:
                        transparency = cmds.getAttr(shader+"."+transparencyAttr)[0]
                else:
                    transparency = cmds.getAttr(shader+"."+transparencyAttr)[0]
                # data dictionary to export
                shaderDic[shader] = {"assigned"        : assignedList,
                                    "color"            : color,
                                    "colorAttr"        : colorAttr,
                                    "fileNode"         : fileNode,
                                    "material"         : cmds.objectType(shader),
                                    "texture"          : texture,
                                    "transparency"     : transparency,
                                    "transparencyAttr" : transparencyAttr
                                    }
                # custom shader attributes
                for attr in self.customAttrList:
                    if attr in cmds.listAttr(shader):
                        shaderDic[shader][attr] = cmds.getAttr(shader+"."+attr)
                # custom vector color attributes
                for attr in self.vectorColorList:
                    if attr in cmds.listAttr(shader):
                        shaderDic[shader][attr] = cmds.getAttr(shader+"."+attr)[0]
                # changed type shader attributes
                for attr in self.changedTypeList:
                    if attr in cmds.listAttr(shader):
                        shaderDic[shader][attr] = cmds.getAttr(shader+"."+attr)
            cmds.select(clear=True)
        return shaderDic


    def importShader(self, shaderDic, *args):
        """ Import the shaders from given shader dictionary.
        """
        mayaVersion = cmds.about(version=True)
        notFoundMeshList = []
        # rebuild shaders
        for item in shaderDic.keys():
            if not cmds.objExists(item):
                shader = cmds.shadingNode(shaderDic[item]['material'], asShader=True, name=item)
                if shaderDic[item]['fileNode']:
                    fileNode = cmds.shadingNode("file", asTexture=True, isColorManaged=True, name=shaderDic[item]['fileNode'])
                    cmds.connectAttr(fileNode+".outColor", shader+"."+shaderDic[item]['colorAttr'], force=True)
                    cmds.setAttr(fileNode+".fileTextureName", shaderDic[item]['texture'], type="string")
                else:
                    colorList = shaderDic[item]['color']
                    cmds.setAttr(shader+"."+shaderDic[item]['colorAttr'], colorList[0], colorList[1], colorList[2], type="double3")
                transparencyList = shaderDic[item]['transparency']
                if shaderDic[item]['transparencyAttr'] == "geometryOpacity": #support OpenPBRShader
                    cmds.setAttr(shader+"."+shaderDic[item]['transparencyAttr'], transparencyList)
                else:
                    cmds.setAttr(shader+"."+shaderDic[item]['transparencyAttr'], transparencyList[0], transparencyList[1], transparencyList[2], type="double3")
                for attr in self.customAttrList:
                    if attr in cmds.listAttr(shader) and shaderDic[item][attr]:
                        cmds.setAttr(shader+"."+attr, shaderDic[item][attr])
                for attr in self.vectorColorList:
                    if attr in cmds.listAttr(shader) and shaderDic[item][attr]:
                        cmds.setAttr(shader+"."+attr, shaderDic[item][attr][0], shaderDic[item][attr][1], shaderDic[item][attr][2], type="double3")
                for attr in self.changedTypeList: #exception to conform Maya2024 standardSurface and Maya2026 openPBRshader - float or vector attribute types
                    if attr in cmds.listAttr(shader) and shaderDic[item][attr]:
                        try:
                            cmds.setAttr(shader+"."+attr, shaderDic[item][attr])
                        except:
                            cmds.setAttr(shader+"."+attr, shaderDic[item][attr][0][0], shaderDic[item][attr][0][1], shaderDic[item][attr][0][2], type="double3")
            # apply shader to meshes
            for mesh in shaderDic[item]['assigned']:
                if cmds.objExists(mesh):
                    if mayaVersion >= "2024":
                        cmds.hyperShade(assign=item, geometries=mesh)
                    else:
                        cmds.select(mesh)
                        cmds.hyperShade(assign=item)
                else:
                    notFoundMeshList.append(mesh)
        cmds.select(clear=True)
        if notFoundMeshList:
            self.notWorkedWellIO(self.dpUIinst.lang['r011_notFoundMesh']+", ".join(notFoundMeshList))
        else:
            self.wellDoneIO(self.latestDataFile)
