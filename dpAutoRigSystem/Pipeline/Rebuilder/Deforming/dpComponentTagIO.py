# importing libraries:
from maya import cmds
from ... import dpBaseActionClass
from .... Deforms import dpWeights

# global variables to this module:
CLASS_NAME = "ComponentTagIO"
TITLE = "r048_componentTagIO"
DESCRIPTION = "r049_componentTagIODesc"
ICON = "/Icons/dp_componentTagIO.png"

DP_COMPONENTTAGIO_VERSION = 1.0


class ComponentTagIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_COMPONENTTAGIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
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
                    self.exportedList = self.getExportedList()
                    if self.exportedList:
                        self.exportedList.sort()
                        self.tagDataDic = self.pipeliner.getJsonContent(self.ioPath+"/"+self.exportedList[-1])
                        if self.tagDataDic:
                            wellImported = True
                            # import tagged (tag info into the received deformed mesh)
                            if self.tagDataDic["tagged"]:
                                wellImported = self.defWeights.importComponentTagInfo(self.tagDataDic["tagged"], nodeList, wellImported)
                                if not wellImported:
                                    self.notWorkedWellIO(self.exportedList[-1]+": "+", ".join(self.defWeights.notWorkWellInfoList))
                            # import influencers (tag info into the deformer node)
                            if self.tagDataDic["influencer"]:
                                wellImported = self.defWeights.importComponentTagInfluencer(self.tagDataDic["influencer"], wellImported)
                                if not wellImported:
                                    self.notWorkedWellIO(self.exportedList[-1]+": "+", ".join(self.defWeights.notWorkWellInfoList))
                            # import falloffs
                            if self.tagDataDic["falloff"]:
                                wellImported = self.defWeights.importComponentTagFalloff(self.tagDataDic["falloff"], wellImported)
                                if not wellImported:
                                    self.notWorkedWellIO(self.exportedList[-1]+": "+", ".join(self.defWeights.notWorkWellInfoList))
                            if wellImported:
                                self.wellDoneIO(", ".join(list(self.tagDataDic["tagged"].keys())))
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
