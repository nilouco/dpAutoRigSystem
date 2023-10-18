# importing libraries:
from maya import cmds
from .. import dpBaseValidatorClass
from ...Modules.Library import dpUtils

# global variables to this module:
CLASS_NAME = "ProxyCreator"
TITLE = "m230_proxyCreator"
DESCRIPTION = "m231_proxyCreatorDesc"
ICON = "/Icons/dp_proxyCreator.png"

PROXIED = "dpProxied"
NO_PROXY = "dpDoNotProxyIt"

DP_PROXYCREATOR_VERSION = 1.0


class ProxyCreator(dpBaseValidatorClass.ValidatorStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseValidatorClass.ValidatorStartClass.__init__(self, *args, **kwargs)
    

    def runValidator(self, verifyMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If verifyMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.verifyMode = verifyMode
        self.cleanUpToStart()
        
        # ---
        # --- validator code --- beginning
        self.skinClusterList = []
        proxyGrp = None
        if objList:
            proxyGrp = objList[0]
        else:
            proxyGrp = dpUtils.getNodeByMessage("proxyGrp")
            if not proxyGrp:
                if cmds.objExists("Proxy_Grp"):
                    proxyGrp = "Proxy_Grp"
        if proxyGrp:
            if not cmds.objExists(proxyGrp+"."+PROXIED):
                meshList = cmds.listRelatives(proxyGrp, children=True, allDescendents=True, type="mesh")
                if not meshList:
                    renderGrp = dpUtils.getNodeByMessage("renderGrp")
                    if not renderGrp:
                        if cmds.objExists("Render_Grp"):
                            renderGrp = "Render_Grp"
                    if renderGrp:
                        meshList = cmds.listRelatives(renderGrp, children=True, allDescendents=True, type="mesh")
                if meshList:
                    # find meshes to generate proxy
                    toProxyList = []
                    for mesh in meshList:
                        meshTransform = cmds.listRelatives(mesh, parent=True, type="transform")
                        if meshTransform:
                            if not meshTransform[0] in toProxyList:
                                if not cmds.objExists(meshTransform[0]+"."+NO_PROXY):
                                    if not cmds.objExists(meshTransform[0]+"."+PROXIED):
                                        if cmds.getAttr(meshTransform[0]+".visibility"):
                                            toProxyList.append(meshTransform[0])
                    if toProxyList:
                        progressAmount = 0
                        maxProcess = len(toProxyList)
                        if self.verbose:
                            # Update progress window
                            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                        self.checkedObjList.append(proxyGrp)
                        self.foundIssueList.append(True)
                        if self.verifyMode:
                            self.resultOkList.append(False)
                        else: #fix
#                            try:
                                for sourceTransform in toProxyList:
                                    # Update progress window
                                    progressAmount += 1
                                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)+' '+sourceTransform))
                                    self.createProxy(sourceTransform, proxyGrp)
                                self.proxyIntegration(proxyGrp)
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+proxyGrp)
#                            except:
#                                self.resultOkList.append(False)
#                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+proxyGrp)
                    else:
                        self.foundIssueList.append(False)
                        self.resultOkList.append(True)
                else:
                    self.notFoundNodes(proxyGrp)
            else:
                self.notFoundNodes(proxyGrp)
        else:
            self.notFoundNodes(proxyGrp)
        # --- validator code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        return self.dataLogDic


    def createProxy(self, source, grp, *args):
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
                gotVertexList = []
                for jnt in weightedInfluenceList:
                    skinnedFaceList = []
                    nodeFaceList = []
                    faceList = cmds.ls(source+".f[*]", flatten=True)
                    for i, idx in enumerate(faceList):
                        if not i in gotVertexList:
                            percList = cmds.skinPercent(skinClusterNode, source+".f["+str(i)+"]", ignoreBelow=0.1, transform=None, query=True)
                            if percList:
                                if jnt in percList:
                                    skinnedFaceList.append(i)
                                    gotVertexList.append(i)
                    if skinnedFaceList:
                        faceList = [w.replace(source+".f[", "") for w in faceList]
                        faceList = [int(w.replace("]", "")) for w in faceList]
                        if faceList:
                            for v in reversed(skinnedFaceList):
                                faceList.pop(v)
                        if faceList:
                            for n in faceList:
                                nodeFaceList.append(source+".f["+str(n)+"]")
                        if nodeFaceList:
                            dup = cmds.duplicate(source, name=source+"_"+jnt+"_Pxy")[0]
                            for dupItem in cmds.listRelatives(dup, children=True, allDescendents=True):
                                if "Orig" in dupItem:
                                    cmds.delete(dupItem)
                            faceDupList = [w.replace(source, dup) for w in nodeFaceList]
                            cmds.delete(faceDupList)
                            self.dpUIinst.ctrls.setLockHide([dup], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], l=False)
                            cmds.xform(dup, pivots=cmds.xform(jnt, worldSpace=True, rotatePivot=True, query=True))
                            cmds.parent(dup, jnt)
                            cmds.makeIdentity(dup, apply=True, translate=True, rotate=True, scale=True)
                            cmds.connectAttr(jnt+".worldMatrix", dup+".offsetParentMatrix", force=True)
                            cmds.parent(dup, grp)
                            dpUtils.setAttrValues([dup], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], [0, 0, 0, 0, 0, 0, 1, 1, 1])
                            self.dpUIinst.ctrls.setLockHide([dup], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
                            drawOverrideList = cmds.listConnections(dup+".drawOverride", source=True, destination=False, plugs=True)
                            if drawOverrideList:
                                # remove from display layer
                                cmds.disconnectAttr(drawOverrideList[0], dup+".drawOverride")
                            cmds.setAttr(dup+".overrideEnabled", 1)
                            cmds.setAttr(dup+".overrideDisplayType", 2) #reference
            cmds.addAttr(source, longName=PROXIED, attributeType="bool", defaultValue=1)
        sourceParent = cmds.listRelatives(source, parent=True, type="transform")
        if sourceParent:
            if sourceParent[0] == grp:
                cmds.delete(source)


    def proxyIntegration(self, grp, *args):
        """ Add attributes, connect to deformer envelopes if possible to disable them and 
        """
        if not cmds.objExists(grp+"."+PROXIED):
            cmds.addAttr(grp, longName=PROXIED, attributeType="bool", defaultValue=1)
        
        #
        # WIP
        #
        #
        optionCtrl = dpUtils.getNodeByMessage("optionCtrl")
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
                deformerList.extend(cmds.ls(type=deform))
            if deformerList:
                for deformNode in deformerList:
                    try:
                        cmds.connectAttr(optionCtrl+".proxyRevOutput", deformNode+".envelope") #don't force it please
                    except:
                        pass #maybe it already has a connection from another node


        self.dpUIinst.ctrls.colorShape([grp], [1, 0.5, 0.5], outliner=True) #red

        #
        # TODO
        #
        # 
        # hide tweaks
        # hide facial ctrls
        # hide mesh/Render_grp
        # 
        # 