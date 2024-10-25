# importing libraries:
from maya import cmds
from .. import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "CalibrationIO"
TITLE = "r041_calibrationIO"
DESCRIPTION = "r042_calibrationIODesc"
ICON = "/Icons/dp_calibrationIO.png"

DP_CALIBRATIONIO_VERSION = 1.0


class CalibrationIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_CALIBRATIONIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_calibrationIO"
        self.startName = "dpCalibration"
    

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
                ctrlList = None
                if objList:
                    ctrlList = objList
                else:
                    ctrlList = self.dpUIinst.ctrls.getControlList()
                if ctrlList:
                    if self.firstMode: #export
                        toExportDataDic = self.getCalibrationDataDic(ctrlList)
                        try:
                            # export json file
                            self.pipeliner.makeDirIfNotExists(self.ioPath)
                            jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.pipeData['currentFileName']+".json"
                            self.pipeliner.saveJsonFile(toExportDataDic, jsonName)
                            self.wellDoneIO(jsonName)
                        except Exception as e:
                            self.notWorkedWellIO(jsonName+": "+str(e))
                    else: #import
                        try:
                            exportedList = self.getExportedList()
                            if exportedList:
                                exportedList.sort()
                                calibrationDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                                if calibrationDic:
                                    self.importCalibrationData(calibrationDic)
                                else:
                                    self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                            else:
                                self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                        except Exception as e:
                            self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData']+": "+str(e))
                else:
                    self.notWorkedWellIO("Ctrls_Grp")
            else:
                self.notWorkedWellIO(self.dpUIinst.lang['r010_notFoundPath'])
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r027_noAssetContext'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        self.refreshView()
        return self.dataLogDic


    def getCalibrationDataDic(self, ctrlList, *args):
        """ Processes the given controller list to collect and mount the calibration data.
            Returns the dictionary to export.
        """
        if ctrlList:
            dic = {}
            progressAmount = 0
            maxProcess = len(ctrlList)
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
            for ctrl in ctrlList:
                calibrationList = self.dpUIinst.ctrls.getListFromStringAttr(ctrl)
                if calibrationList:
                    dic[ctrl] = {}
                    for attr in calibrationList:
                        dic[ctrl][attr] = cmds.getAttr(ctrl+"."+attr)
            return dic

    def importCalibrationData(self, calibrationDic, *args):
        """ Import the calibration setup from the given calibration data dictionary.
        """
        progressAmount = 0
        maxProcess = len(calibrationDic.keys())
        # define lists to check result
        wellImportedList = []
        for item in calibrationDic.keys():
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)+" "+item[item.rfind("|"):]))
            notFoundNodesList = []
            # check transformations
            if not cmds.objExists(item):
                item = item[item.rfind("|")+1:] #short name (after last "|")
            if cmds.objExists(item):
                for attr in calibrationDic[item].keys():
                    if not cmds.listConnections(item+"."+attr, destination=False, source=True):
                        # unlock attribute
                        wasLocked = cmds.getAttr(item+"."+attr, lock=True)
                        cmds.setAttr(item+"."+attr, lock=False)
                        try:
                            # set calibration value
                            cmds.setAttr(item+"."+attr, calibrationDic[item][attr])
                            # lock attribute again if it was locked
                            cmds.setAttr(item+"."+attr, lock=wasLocked)
                            if not item in wellImportedList:
                                wellImportedList.append(item)
                        except Exception as e:
                            self.notWorkedWellIO(item+" - "+str(e))
            else:
                notFoundNodesList.append(item)
        if wellImportedList:
            self.wellDoneIO(', '.join(wellImportedList))
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))