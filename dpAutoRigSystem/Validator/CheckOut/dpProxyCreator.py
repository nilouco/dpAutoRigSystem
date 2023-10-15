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
                if self.verbose:
                    # Update progress window
                    cmds.progressWindow(edit=True, maxValue=1, progress=1, status=(self.dpUIinst.lang[self.title]+': '+repr(1)))
                

                # find meshes to generate proxy
                meshList = cmds.listRelatives(proxyGrp, children=True, allDescendents=True, type="mesh")
                if not meshList:
                    renderGrp = dpUtils.getNodeByMessage("renderGrp")
                    if not renderGrp:
                        if cmds.objExists("Render_Grp"):
                            renderGrp = "Render_Grp"
                    if renderGrp:
                        meshList = cmds.listRelatives(renderGrp, children=True, allDescendents=True, type="mesh")
                if meshList:
                    toProxyList = []
                    for mesh in meshList:
                        meshTransform = cmds.listRelatives(mesh, parent=True, type="transform")
                        if meshTransform:
                            if not meshTransform[0] in toProxyList:
                                if not cmds.objExists(meshTransform[0]+"."+NO_PROXY) and not cmds.objExists(meshTransform[0]+"."+PROXIED):
                                    toProxyList.append(meshTransform[0])
                    if toProxyList:

                        print("toProxyList =", toProxyList)

                        self.checkedObjList.append(proxyGrp)
                        self.foundIssueList.append(True)
                        if self.verifyMode:
                            self.resultOkList.append(False)
                        else: #fix
                            #try:

                                #
                                # WIP
                                #
                                
                                # 
                                #
                                for sourceTransform in toProxyList:
                                    self.createProxy(sourceTransform, proxyGrp)
                                
                                self.proxyIntegration(proxyGrp)
                                
                                self.resultOkList.append(True)
                                self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+proxyGrp)
                            #except:
                            #    self.resultOkList.append(False)
                            #    self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+proxyGrp)
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
        print("WIP: createProxy = ", source, grp)
        cmds.addAttr(source, longName=PROXIED, attributeType="bool", defaultValue=1)
        #
        # WIP
        #
        




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
        # TODO
        #
        # def envelope zero (blendShapes, skinClusters, etc...)
        # hide tweaks
        # hide facial ctrls
        # hide mesh/Render_grp
        # optionCtrl attr proxy
        # outliner color