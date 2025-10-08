# importing libraries:
from maya import cmds
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "ChannelIO"
TITLE = "r064_channelIO"
DESCRIPTION = "r065_channelIODesc"
ICON = "/Icons/dp_channelIO.png"

DP_CHANNELIO_VERSION = 1.00


class ChannelIO(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_CHANNELIO_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_channelIO"
        self.startName = "dpChannel"
    

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
                    itemList = None
                    if objList:
                        itemList = objList
                    else:
                        itemList = cmds.ls(selection=False, type="transform")
                    if itemList:
                        if self.firstMode: #export
                            self.exportDicToJsonFile(self.getChannelDataDic(itemList))
                        else: #import
                            attrDic = self.importLatestJsonFile(self.getExportedList())
                            if attrDic:
                                self.importChannelData(attrDic)
                            else:
                                self.maybeDoneIO(self.dpUIinst.lang['r007_notExportedData'])
                    else:
                        self.maybeDoneIO("Ctrls_Grp")
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


    def getChannelDataDic(self, itemList, *args):
        """ Processes the given item list to collect and mount the tranform attributes data.
            Returns the dictionary to export.
        """
        dic = {}
        self.utils.setProgress(max=len(itemList), addOne=False, addNumber=False)
        for item in itemList:
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            if cmds.objExists(item):
                dic[item] = {}
                for attr in self.dpUIinst.transformAttrList:
                    dic[item][attr] = {
                                        "locked" : cmds.getAttr(item+"."+attr, lock=True),
                                        "keyable" : cmds.getAttr(item+"."+attr, keyable=True),
                                        "channelBox" : cmds.getAttr(item+"."+attr, channelBox=True)
                                        }
        return dic


    def importChannelData(self, attrDic, *args):
        """ Import tranform attributes states from exported dictionary.
            Just set them as locked, hidden, non keyable or not.
        """
        self.utils.setProgress(max=len(attrDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in attrDic.keys():
            notFoundNodesList = []
            self.utils.setProgress(self.dpUIinst.lang[self.title])
            # check attributes
            if not cmds.objExists(item):
                item = item[item.rfind("|")+1:] #short name (after last "|")
            if cmds.objExists(item):
                for attr in self.dpUIinst.transformAttrList:
                    try:
                        cmds.setAttr(item+"."+attr, keyable=attrDic[item][attr]['keyable'])
                        if not attrDic[item][attr]['keyable']:
                            cmds.setAttr(item+"."+attr, channelBox=attrDic[item][attr]['channelBox'])
                        cmds.setAttr(item+"."+attr, lock=attrDic[item][attr]['locked'])
                        if not item in wellImportedList:
                            wellImportedList.append(item)
                    except Exception as e:
                        self.notWorkedWellIO(item+" - "+str(e))
            else:
                notFoundNodesList.append(item)
        if wellImportedList:
            self.wellDoneIO(self.latestDataFile)
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
