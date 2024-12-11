# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction
from ....Modules.Library import dpWeights

# global variables to this module:
CLASS_NAME = "ComponentTagIO"
TITLE = "r048_componentTagIO"
DESCRIPTION = "r049_componentTagIODesc"
ICON = "/Icons/dp_componentTagIO.png"

DP_COMPONENTTAGIO_VERSION = 1.0


class ComponentTagIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_COMPONENTTAGIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_componentTagIO"
        self.startName = "dpComponentTag"
        self.defWeights = dpWeights.Weights(self.dpUIinst)
    

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
        if self.pipeliner.checkAssetContext():
            self.ioPath = self.getIOPath(self.ioDir)
            if self.ioPath:
                nodeList = None
                if objList:
                    nodeList = objList
                else:
                    nodeList = cmds.listRelatives(cmds.ls(selection=False, type=["mesh", "lattice"]), parent=True)
                if self.firstMode: #export
                    if nodeList:
                        # finding tags
                        hasTag = False
                        for node in nodeList:
                            if cmds.geometryAttrInfo(node+"."+cmds.deformableShape(node, localShapeOutAttr=True)[0], componentTagHistory=True):
                                hasTag = True
                                break
                        if hasTag:
                            # Declaring the data dictionary to export it
                            self.tagDataDic = { "tagged"     : self.defWeights.getComponentTagInfo(nodeList),
                                                "influencer" : self.defWeights.getComponentTagInfluencer(),
                                                "falloff"    : self.defWeights.getComponentTagFalloff()
                                            }
                            self.exportDicToJsonFile(self.tagDataDic)
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" componentTag")
                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+" mesh, lattice")
                else: #import
                    tagDataDic = self.importLatestJsonFile(self.getExportedList())
                    if tagDataDic:
                        self.importTag(tagDataDic, nodeList)
                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        # --- rebuilder code --- end
        # ---

        # finishing
        cmds.select(clear=True)
        self.updateButtonColors()
        self.reportLog()
        self.endProgress()
        self.refreshView()
        return self.dataLogDic


    def importTag(self, tagDataDic, nodeList, *args):
        """ Import componentTag data.
        """
        fail = False
        # import tagged (tag info into the received deformed mesh)
        if tagDataDic["tagged"]:
            if not self.defWeights.importComponentTagInfo(tagDataDic["tagged"], nodeList):
                self.notWorkedWellIO(self.latestDataFile+": tagged - "+", ".join(self.defWeights.notWorkWellInfoList))
                fail = True
        # import influencers (tag info into the deformer node)
        if tagDataDic["influencer"]:
            if not self.defWeights.importComponentTagInfluencer(tagDataDic["influencer"]):
                self.notWorkedWellIO(self.latestDataFile+": influencer - "+", ".join(self.defWeights.notWorkWellInfoList))
                fail = True
        # import falloffs
        if tagDataDic["falloff"]:
            if not self.defWeights.importComponentTagFalloff(tagDataDic["falloff"]):
                self.notWorkedWellIO(self.latestDataFile+": falloff - "+", ".join(self.defWeights.notWorkWellInfoList))
                fail = True
        if not fail:
            self.wellDoneIO(self.latestDataFile)
