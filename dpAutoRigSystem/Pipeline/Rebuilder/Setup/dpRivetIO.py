# importing libraries:
from maya import cmds
import json
from ....Modules.Base import dpBaseAction
from ....Tools import dpRivet

# global variables to this module:
CLASS_NAME = "RivetIO"
TITLE = "r039_rivetIO"
DESCRIPTION = "r040_rivetIODesc"
ICON = "/Icons/dp_rivetIO.png"

DP_RIVETIO_VERSION = 1.00


class RivetIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_RIVETIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.dpRivet = dpRivet.Rivet(self.dpUIinst, ui=False)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_rivetIO"
        self.startName = "dpRivet"
    

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
                    if self.firstMode: #export
                        netList = None
                        if objList:
                            netList = objList
                        else:
                            netList = self.utils.getNetworkNodeByAttr("dpRivetNet")
                        if netList:
                            self.exportDicToJsonFile(self.getRivetDataDic(netList))
                        else:
                            self.maybeDoneIO(self.dpUIinst.lang['v014_notFoundNodes'])
                            cmds.select(clear=True)
                    else: #import
                        rivetDic = self.importLatestJsonFile(self.getExportedList())
                        if rivetDic:
                            self.importRivet(rivetDic)
                        else:
                            self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])
                        cmds.select(clear=True)
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


    def getRivetDataDic(self, netList, *args):
        """ Processes the given rivet network list and mount the right info pack to rebuild the module.
            Returns the dictionary to export.
        """
        dic = {}
        self.utils.setProgress(max=len(netList), addOne=False, addNumber=False)
        i = 0
        for n, net in enumerate(netList):
            if self.verbose:
                self.utils.setProgress(self.dpUIinst.lang[self.title])
            # mount a dic
            if cmds.objExists(net+".rivetData"):
                data = json.loads(cmds.getAttr(net+".rivetData"))
                addIt = True
                if n > 0:
                    for x in range(0, i):
                        if data["itemNode"] in dic[x]["itemList"]:
                            addIt = False
                            break
                if addIt:
                    dic[i] = data
                    i += 1
        return dic


    def importRivet(self, rivetDic, *args):
        """ Import rivet data creating new instances with exported attribute values.
        """
        wellImported = True
        self.utils.setProgress(max=len(rivetDic.keys()), addOne=False, addNumber=False)
        for net in rivetDic.keys():
            try:
                netDic = rivetDic[net]
                self.utils.setProgress(self.dpUIinst.lang[self.title]+': '+netDic['geoToAttach'])
                # recreate rivet:
                self.dpRivet.deformerToUse = netDic['deformerToUse']
                rivetList = self.dpRivet.dpCreateRivet(netDic['geoToAttach'], netDic['uvSetName'], netDic['itemList'], netDic['attachTranslate'], netDic['attachRotate'], netDic['addFatherGrp'], netDic['addInvert'], netDic['invT'], netDic['invR'], netDic['faceToRivet'], netDic['rivetGrpName'], netDic['askComponent'], netDic['useOffset'], netDic['reuseFaceToRivet'])
                if not rivetList:
                    wellImported = False
                    self.notWorkedWellIO(net+": "+self.dpUIinst.lang['r032_notImportedData'])
            except Exception as e:
                wellImported = False
                self.notWorkedWellIO(net+": "+str(e))
                break
        if wellImported:
            self.wellDoneIO(self.latestDataFile)
