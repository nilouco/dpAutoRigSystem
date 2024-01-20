# importing libraries:
from maya import cmds
from .. import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "GuideIO"
TITLE = "r012_guideIO"
DESCRIPTION = "r013_guideIODesc"
ICON = "/Icons/dp_guideIO.png"

DP_GUIDEIO_VERSION = 1.0


class GuideIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_GUIDEIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.ioDir = "s_guideIO"
        self.startName = "dpGuide"
    

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
        # ensure file is saved
        if not cmds.file(query=True, sceneName=True):
            self.notWorkedWellIO(self.dpUIinst.lang['i201_saveScene'])
        else:
            self.ioPath = self.getIOPath(self.ioDir)
            if self.ioPath:
                if self.firstMode: #export
                    netList = None
                    if objList:
                        netList = objList
                    else:
                        netList = self.utils.getNetworkNodeByAttr("dpGuideNet")
                    if netList:
                        dataDic = {}
                        progressAmount = 0
                        maxProcess = len(netList)
                        for net in netList:
                            if self.verbose:
                                # Update progress window
                                progressAmount += 1
                                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                            # mount a dic with all data 
                            if cmds.objExists(net+".afterData"):
                                dataDic[net] = cmds.getAttr(net+".afterData")
                        if dataDic:
                            try:
                                # export json file
                                self.pipeliner.makeDirIfNotExists(self.ioPath)
                                jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.getCurrentFileName()+".json"
                                self.pipeliner.saveJsonFile(dataDic, jsonName)
                                self.wellDoneIO(jsonName)
                            except:
                                self.notWorkedWellIO(jsonName)
                        else:
                            self.notWorkedWellIO("v014_notFoundNodes")
                    else:
                        self.notWorkedWellIO("v014_notFoundNodes")
                else: #import
                    try:
                        exportedList = self.getExportedList()
                        if exportedList:
                            exportedList.sort()
                            dataDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                            if dataDic:

                                #WIP
                                #
                                #
                                #mount guides from netDataDic
                                #parentGuides
                                #change net status to raw True
                                print("IMPORTING Guides....")



                                
                                
                                for net in dataDic.keys():
                                    if not cmds.objExists(net):
                                        print(net)
                                        print(dataDic[net])

                                        guideDir = 'Modules'


                                        # create fkLine module instance:
                                        chassisInstance = self.dpUIinst.initGuide(dataDic[net]['moduleType'], guideDir)
                                        # editing chassis base guide informations:
                                        chassisInstance.editUserName("guideName_TEST")
                                        cmds.setAttr(chassisInstance.moduleGrp+".translateY", 9)
                                        cmds.setAttr(chassisInstance.radiusCtrl+".translateX", 8)

                                
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
