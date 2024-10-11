# importing libraries:
from maya import cmds
from .. import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "ConnectionIO"
TITLE = "r045_connectionIO"
DESCRIPTION = "r046_connectionIODesc"
ICON = "/Icons/dp_connectionIO.png"

DP_CONNECTIONIO_VERSION = 1.0


class ConnectionIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_CONNECTIONIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_connectionIO"
        self.startName = "dpConnection"
        self.defaultAttrList = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ", "visibility"]
    

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
                        toExportDataDic = self.getConnectionDataDic(ctrlList)
                        try:
                            # export json file
                            self.pipeliner.makeDirIfNotExists(self.ioPath)
                            jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.pipeData['currentFileName']+".json"
                            self.pipeliner.saveJsonFile(toExportDataDic, jsonName)
                            self.wellDoneIO(jsonName)
                        except Exception as e:
                            self.notWorkedWellIO(jsonName+": "+str(e))
                    else: #import
#                        try:
                            exportedList = self.getExportedList()
                            if exportedList:
                                exportedList.sort()
                                connectDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                                if connectDic:
                                    self.importConnectionData(connectDic)
                                else:
                                    self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                            else:
                                self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
#                        except Exception as e:
#                            self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData']+": "+str(e))
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


    def getConnectionDataDic(self, ctrlList, *args):
        """ Processes the given controller list to collect the info about their connections to rebuild.
            Returns a dictionary to export.
        """
        if ctrlList:
            dic = {}
            progressAmount = 0
            maxProcess = len(ctrlList)
            for ctrl in ctrlList:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                if cmds.objExists(ctrl):
                    attrList = self.defaultAttrList
                    userDefList = cmds.listAttr(ctrl, userDefined=True)
                    if userDefList:
                        attrList.extend(userDefList)
                    connectedAttrList = []
                    for attr in attrList:
                        if cmds.objExists(ctrl+"."+attr):
                            if cmds.listConnections(ctrl+"."+attr):
                                connectedAttrList.append(attr)
                    if connectedAttrList:
                        dic[ctrl] = {}
                        for attr in connectedAttrList:
                            dic[ctrl][attr] = {
                                                "in"  : self.getConnectionInfoList(ctrl+"."+attr, sourceConnection=True, destinationConnection=False),
                                                "out" : self.getConnectionInfoList(ctrl+"."+attr, sourceConnection=False, destinationConnection=True)
                                                }
            return dic


    def getConnectionInfoList(self, item, sourceConnection, destinationConnection, *args):
        """ Return a list of plugged nodes and their attributes of the given item.
        """
        resultList = []
        if cmds.listConnections(item, plugs=True, source=sourceConnection, destination=destinationConnection):
            infoList = cmds.listConnections(item, plugs=True, source=sourceConnection, destination=destinationConnection)
            if infoList:
                for info in infoList:
                    if cmds.objectType(info[:info.find(".")]) == "unitConversion":
                        if sourceConnection:
                            resultList.append({info : self.getConnectionInfoList(info[:info.find(".")]+".input", sourceConnection, destinationConnection)})
                        else:
                            resultList.append({info : self.getConnectionInfoList(info[:info.find(".")]+".output", sourceConnection, destinationConnection)})
                    else:
                        resultList.append({info : []})
        return resultList


    def importConnectionData(self, connectDic, *args):
        """
        """

        progressAmount = 0
        maxProcess = len(connectDic.keys())
        # define lists to check result
        wellImportedList = []
        for item in connectDic.keys():
            notFoundNodesList = []
            if self.verbose:
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)+" "+item[item.rfind("|"):]))
            # check connections

            # WIP

            for attr in connectDic[item].keys():
                if cmds.objExists(item+"."+attr):
                    for i, io in enumerate(["in", "out"]): # input and output
                        if connectDic[item][attr][io]: # have connection
                            for j, ioDic in enumerate(connectDic[item][attr][io]):
                                plug = list(ioDic.keys())[0]
                                subPlug = ioDic[plug]
                                if subPlug: # has unitConversion node
                                    subPlug = list(ioDic[plug][0].keys())[0]
                                    print("subPlug = ", subPlug)
                                    if cmds.objExists(subPlug):
                                        print("exists unitConversion node")


                                if not cmds.objExists(plug):
                                    if cmds.objectType(plug.split(".")[0]) == "unitConversion":
                                        plug = list(list(connectDic[item][attr][io][0].keys())[0].keys())[0]
        #                                print("plug ======", plug)


                                #else:
                                #    if not cmds.listConnections(item+"."+attr, plugs=True, source=True, destination=False) == [plug]:
                                #        isLocked = cmds.getAttr(item+"."+attr, lock=True)
                                #        cmds.setAttr(item+"."+attr, lock=False)
                                #        cmds.connectAttr(plug, item+"."+attr, force=True)
                                #        if isLocked:
                                #            cmds.setAttr(item+"."+attr, lock=True)
                                #        if not item in wellImportedList:
                                #            wellImportedList.append(item)
                            

                        # output
                        if connectDic[item][attr]['out']:
                            for outPlugDic in connectDic[item][attr]['out']:
                                #print("yes out", attr)
                                pass
#for i, idx in enumerate( list(connectDic[item][attr]['in'][0].keys())[0].keys()):
#   plug = list(list(connectDic[item][attr]['in'][0].keys())[0].keys())[i]
                else:
                    #print("nnooooooo exists =", item, attr)
                    pass



            if cmds.objExists(item):
                wellImportedList.append(item)
            else:
                notFoundNodesList.append(item)
        if wellImportedList:
            self.wellDoneIO(', '.join(wellImportedList))
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))