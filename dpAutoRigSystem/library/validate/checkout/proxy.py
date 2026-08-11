# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "Proxy"
TITLE = "m230_proxy"
DESCRIPTION = "m231_proxyDesc"
WIKI = "07-‐-Validator#-proxy-creator"

PROXIED = "dpProxied"
NO_PROXY = "dpDoNotProxyIt"



class Proxy(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.repeatedNameList = []
    

    def runAction(self, first_mode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If first_mode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start()

        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            self.skinClusterList = []
            proxyGrp = None
            if objList:
                proxyGrp = objList[0]
            else:
                proxyGrp = self.ar.utils.getNodeByMessage("proxyGrp")
                if not proxyGrp:
                    if cmds.objExists("Proxy_Grp"):
                        proxyGrp = "Proxy_Grp"
            if proxyGrp:
                if not PROXIED in cmds.listAttr(proxyGrp):
                    meshList = cmds.listRelatives(proxyGrp, children=True, allDescendents=True, type="mesh")
                    if not meshList:
                        renderGrp = self.ar.utils.getNodeByMessage("renderGrp")
                        if not renderGrp:
                            if cmds.objExists("Render_Grp"):
                                renderGrp = "Render_Grp"
                        if renderGrp:
                            meshList = cmds.listRelatives(renderGrp, children=True, allDescendents=True, fullPath=True, type="mesh")
                    if meshList:
                        # find meshes to generate proxy
                        toProxyList = []
                        for mesh in meshList:
                            if len(cmds.ls(mesh)) == 1:
                                meshTransform = cmds.listRelatives(mesh, parent=True, fullPath=True, type="transform")
                                if meshTransform:
                                    if not meshTransform[0] in toProxyList:
                                        if not NO_PROXY in cmds.listAttr(meshTransform):
                                            if not PROXIED in cmds.listAttr(meshTransform):
                                                toProxyList.append(meshTransform[0])
                        if toProxyList:
                            self.ar.utils.setProgress(max=len(toProxyList), add_one=False, add_number=False)
                            self.checked_items.append(proxyGrp)
                            self.found_issues.append(True)
                            if self.first_mode:
                                self.good_results.append(False)
                            else: #fix
                                try:
                                    for sourceTransform in toProxyList:
                                        sourceShortName = self.ar.utils.getShortName(sourceTransform)
                                        self.ar.utils.setProgress(self.ar.data.lang[self.title]+": "+sourceShortName)
                                        self.createProxy(sourceTransform, sourceShortName, proxyGrp)
                                    self.proxyIntegration(proxyGrp)
                                    self.good_results.append(True)
                                    self.messages.append(self.ar.data.lang['v004_fixed']+": "+proxyGrp)
                                except:
                                    self.good_results.append(False)
                                    self.messages.append(self.ar.data.lang['v005_cantFix']+": "+proxyGrp)
                        else:
                            self.found_issues.append(False)
                            self.good_results.append(True)
                    else:
                        self.not_found_node(proxyGrp)
                else:
                    self.not_found_node(proxyGrp)
            else:
                self.not_found_node(proxyGrp)
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---
        
        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data


    def createProxy(self, source, shortName, grp, *args):
        """ Creates a proxy setup from the given source transform and put it into the given grp group.
        """
        try:
            inputDeformerList = cmds.findDeformers(source)
        except:
            return
        skinClusterNode = None
        if inputDeformerList:
            for deformerNode in inputDeformerList:
                if cmds.objectType(deformerNode) == "skinCluster":
                    skinClusterNode = deformerNode
                    break
        if skinClusterNode:
            self.skinClusterList.append(skinClusterNode)
            weightedInfluenceList = cmds.skinCluster(skinClusterNode, query=True, weightedInfluence=True)
            if weightedInfluenceList:
                # get data and store it into a dic
                indexJointDic = {}
                sourceFaceList = cmds.ls(source+".f[*]", flatten=True, long=True)
                for i, idx in enumerate(sourceFaceList):
                    percList = cmds.skinPercent(skinClusterNode, source+".f["+str(i)+"]", ignoreBelow=0.1, transform=None, query=True)
                    if percList:
                        indexJointDic[i] = percList[0]
                        if not len(percList) == 1:
                            jointValueList = []
                            for item in percList:
                                jointValueList.append(cmds.skinPercent(skinClusterNode, source+".f["+str(i)+"]", ignoreBelow=0.1, transform=item, query=True))
                            indexJointDic[i] = percList[jointValueList.index(max(jointValueList))]
                for jnt in weightedInfluenceList:
                    nodeFaceList = []
                    skinnedFaceList = []
                    # data analisis
                    for j in list(indexJointDic.keys()):
                        if indexJointDic[j] == jnt:
                            skinnedFaceList.append(j)
                    if skinnedFaceList:
                        # filter lists
                        faceList = [w.replace(source+".f[", "") for w in sourceFaceList]
                        faceList = [int(w.replace("]", "")) for w in faceList]
                        if faceList:
                            for v in reversed(skinnedFaceList):
                                faceList.pop(v)
                        if faceList:
                            for n in faceList:
                                nodeFaceList.append(source+".f["+str(n)+"]")
                        # create proxy geometry
                        dup = cmds.duplicate(source, name=shortName+"_"+str(self.repeatedNameList.count(shortName)).zfill(2)+"_"+jnt+"_Pxy")[0]
                        self.repeatedNameList.append(shortName)
                        self.ar.utils.removeUserDefinedAttr(dup)
                        self.ar.utils.deleteOrigShape(dup)
                        self.ar.utils.removeFromSets(dup)
                        if nodeFaceList:
                            faceDupList = [w.replace(source, dup) for w in nodeFaceList]
                            cmds.delete(faceDupList)
                        self.ar.ctrls.setLockHide([dup], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], l=False)
                        cmds.xform(dup, pivots=cmds.xform(jnt, worldSpace=True, rotatePivot=True, query=True))
                        cmds.parent(dup, jnt)
                        cmds.scriptEditorInfo(suppressWarnings=True)
                        cmds.makeIdentity(dup, apply=True, translate=True, rotate=True, scale=True)
                        cmds.scriptEditorInfo(suppressWarnings=False)
                        self.checkReverseNormal(dup, jnt)
                        cmds.connectAttr(jnt+".worldMatrix", dup+".offsetParentMatrix", force=True)
                        cmds.parent(dup, grp)
                        self.ar.utils.setAttrValues([dup], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], [0, 0, 0, 0, 0, 0, 1, 1, 1])
                        self.ar.ctrls.setLockHide([dup], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
                        drawOverrideList = cmds.listConnections(dup+".drawOverride", source=True, destination=False, plugs=True)
                        if drawOverrideList:
                            # remove from display layer
                            cmds.disconnectAttr(drawOverrideList[0], dup+".drawOverride")
                        cmds.setAttr(dup+".overrideEnabled", 1)
                        cmds.setAttr(dup+".overrideDisplayType", 2) #reference
                        self.reconnectVisibility(source, dup)
            cmds.addAttr(source, longName=PROXIED, attributeType="bool", defaultValue=1)
        sourceParent = cmds.listRelatives(source, parent=True, fullPath=True, type="transform")
        if sourceParent:
            if sourceParent[0] == grp:
                cmds.delete(source)


    def proxyIntegration(self, grp, *args):
        """ Add attributes, connect to deformer nodeState if possible to disable them in order to get performance.
        """
        if not PROXIED in cmds.listAttr(grp):
            cmds.addAttr(grp, longName=PROXIED, attributeType="bool", defaultValue=1)
        optionCtrl = self.ar.utils.getNodeByMessage("optionCtrl")
        if optionCtrl:
            # prepare optionCtrl to deformers connections
            cmds.setAttr(optionCtrl+".proxy", channelBox=True)
            cmds.addAttr(optionCtrl, longName="proxyRevOutput", attributeType="bool")
            proxyRev = cmds.createNode("reverse", name="Proxy_Rev")
            cmds.connectAttr(optionCtrl+".proxy", proxyRev+".inputX", force=True)
            cmds.connectAttr(proxyRev+".outputX", optionCtrl+".proxyRevOutput", force=True)
            deformerList = self.skinClusterList
            defList = ["blendShape", "wrap", "ffd", "wire", "shrinkWrap", "sculpt", "morph"]
            for deform in defList:
                deformerList.extend(cmds.ls(type=deform) or [])
            if deformerList:
                for deformNode in deformerList:
                    try:
                        cmds.connectAttr(optionCtrl+".proxy", deformNode+".nodeState") #don't force it please
                    except:
                        pass #maybe it already has a connection from another node
            # hide controllers and meshes
            self.connectProxyVis(optionCtrl, "mesh")
            self.connectProxyVis(optionCtrl, "tweaks")
            self.connectProxyVis(optionCtrl, "Tweaks") #fixed camelCase for earlier rig versions v4.03.32
            self.connectProxyVis(optionCtrl, suffixName="Facial_Ctrls_Grp")
            self.connectProxyVis(optionCtrl, suffixName="Deformer_Ctrl_Grp")
        self.ar.ctrls.colorShape([grp], [1, 0.5, 0.5], outliner=True) #red


    def connectProxyVis(self, ctrl, attr=None, suffixName=None, *args):
        """ Create a reverseNode to plug it to the inverse visibility proxy option to the matching nodes.
        """
        if attr or suffixName:
            if attr:
                if attr in cmds.listAttr(ctrl):
                    connectList = cmds.listConnections(ctrl+"."+attr, source=False, destination=True, plugs=True) #list before connect on it
                    visMD = cmds.createNode("multiplyDivide", name="Proxy_"+(attr[0].upper()+attr[1:])+"_Vis_MD")
                    cmds.connectAttr(ctrl+".proxyRevOutput", visMD+".input1X", force=True)
                    cmds.connectAttr(ctrl+"."+attr, visMD+".input2X", force=True)
                    if connectList:
                        for plugDest in connectList:
                            cmds.connectAttr(visMD+".outputX", plugDest, force=True)
            else:
                allNodesList = cmds.ls("*"+suffixName, selection=False)
                if allNodesList:
                    for item in allNodesList:
                        cmds.connectAttr(ctrl+".proxyRevOutput", item+".visibility", force=True)


    def reconnectVisibility(self, sourceMesh, proxyMesh, *args):
        """ Check if there's sourceMesh visibility connection then connect the new proxyMesh visibility too, if so.
        """
        visList = cmds.listConnections(sourceMesh+".visibility", source=True, destination=False, plugs=True)
        if visList:
            cmds.connectAttr(visList[0], proxyMesh+".visibility", force=True)


    def checkReverseNormal(self, dup, jnt, *args):
        """ Verify if there're negative scale joint attributes and reverse the normal mesh if true.
        """
        for axis in ['sx', 'sy', 'sz']:
            if cmds.getAttr(jnt+'.'+axis) < 0:
                cmds.polyNormal(dup, normalMode=0, userNormalMode=0, constructionHistory=False)
                break
