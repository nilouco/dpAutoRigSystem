# importing libraries:
from maya import cmds
from .. import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "ShaderIO"
TITLE = "r008_shaderIO"
DESCRIPTION = "r009_shaderIODesc"
ICON = "/Icons/dp_shaderIO.png"

DP_SHADERIO_VERSION = 1.0


class ShaderIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_SHADERIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.ioDir = "s_shaderIO"
        self.startName = "dpShader"
    

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
        # ensure file has a name to define dpData path
        if not cmds.file(query=True, sceneName=True):
            self.notWorkedWellIO(self.dpUIinst.lang['i201_saveScene'])
        else:
            self.ioPath = self.getIOPath(self.ioDir)
            if self.ioPath:
                if self.firstMode: #export
                    shaderList = None
                    if objList:
                        shaderList = objList
                    else:
                        shaderList = self.getShaderToExportList()
                    if shaderList:
                        shaderDic = {}
                        progressAmount = 0
                        maxProcess = len(shaderList)
                        for shader in shaderList:
                            if self.verbose:
                                # Update progress window
                                progressAmount += 1
                                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                            fileNode = None
                            texture = None
                            color = None
                            cmds.hyperShade(objects=shader)
                            assignedList = cmds.ls(selection=True)
                            if assignedList:
                                colorAttr = "color"
                                transparencyAttr = "transparency"
                                if not cmds.objExists(shader+"."+colorAttr): #support standardShader
                                    colorAttr = "baseColor"
                                    transparencyAttr = "opacity"
                                if cmds.objExists(shader+"."+colorAttr):
                                    shaderConnectionList = cmds.listConnections(shader+"."+colorAttr, destination=False, source=True)
                                    if shaderConnectionList:
                                        fileNode = shaderConnectionList[0]
                                        texture = cmds.getAttr(fileNode+".fileTextureName")
                                    else:
                                        color = cmds.getAttr(shader+"."+colorAttr)[0]
                                transparency = cmds.getAttr(shader+"."+transparencyAttr)[0]
                                # data dictionary to export
                                shaderDic[shader] = {"assigned"         : assignedList,
                                                     "color"            : color,
                                                     "colorAttr"        : colorAttr,
                                                     "fileNode"         : fileNode,
                                                     "material"         : cmds.objectType(shader),
                                                     "texture"          : texture,
                                                     "transparency"     : transparency,
                                                     "transparencyAttr" : transparencyAttr
                                                     }
                            cmds.select(clear=True)
                        try:
                            # export json file
                            self.pipeliner.makeDirIfNotExists(self.ioPath)
                            jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.getCurrentFileName()+".json"
                            self.pipeliner.saveJsonFile(shaderDic, jsonName)
                            self.wellDoneIO(jsonName)
                        except:
                            self.notWorkedWellIO(jsonName)
                    else:
                        self.notWorkedWellIO("Render_Grp")
                else: #import
                    try:
                        exportedList = self.getExportedList()
                        if exportedList:
                            exportedList.sort()
                            shaderDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                            if shaderDic:
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
                                        cmds.setAttr(shader+"."+shaderDic[item]['transparencyAttr'], transparencyList[0], transparencyList[1], transparencyList[2], type="double3")
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
                                    self.notWorkedWellIO(self.dpUIinst.lang['r011_notFoundMesh'])
                                else:
                                    self.wellDoneIO(exportedList[-1])
                            else:
                                self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                    except:
                        self.notWorkedWellIO(exportedList[-1])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        return self.dataLogDic


    def getShaderToExportList(self, *args):
        """ Returns a list of shaders to export as json dictionary.
        """
        materialList = ["anisotropic", "blinn", "hairTubeShader", "lambert", "phong", "phongE", "aiStandardSurface", "standardSurface"]
        ignoreMaterialList = ["lambert1"]
        shaderList = []
        for material in materialList:
            matList = cmds.ls(selection=False, type=material)
            if matList:
                shaderList.extend(matList)
        if shaderList:
            shaderList = list(set(shaderList))
            shaderList.sort()
            for ignoreMaterial in ignoreMaterialList:
                if ignoreMaterial in shaderList:
                    shaderList.remove(ignoreMaterial)
        return shaderList
