# importing libraries:
from maya import cmds
from .. import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "ParentIO"
TITLE = "r019_parentIO"
DESCRIPTION = "r020_parentIODesc"
ICON = "/Icons/dp_parentIO.png"

DP_PARENTIO_VERSION = 1.0


class ParentIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_PARENTIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_parentIO"
        self.startName = "dpParent"
    

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
                if self.firstMode: #export
                    transformList = None
                    if objList:
                        transformList = objList
                    else:
                        transformList = cmds.ls(selection=False, long=True, type="transform")
                    if transformList:
                        progressAmount = 0
                        maxProcess = len(transformList)
                        if self.verbose:
                            # Update progress window
                            progressAmount += 1
                            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                        # define list to export
                        transformList = self.filterTransformList(transformList)
                        transformList = self.reorderList(transformList)
                        parentDic = {"Parent" : transformList}
                        try:
                            # export json file
                            self.pipeliner.makeDirIfNotExists(self.ioPath)
                            jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.pipeData['currentFileName']+".json"
                            self.pipeliner.saveJsonFile(parentDic, jsonName)
                            self.wellDoneIO(jsonName)
                        except Exception as e:
                            self.notWorkedWellIO(jsonName+": "+str(e))
                    else:
                        self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes'])
                else: #import
                    try:
                        exportedList = self.getExportedList()
                        if exportedList:
                            exportedList.sort()
                            parentDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                            if parentDic:
                                currentTransformList = cmds.ls(selection=False, long=True, type="transform")
                                currentTransformList = self.filterTransformList(currentTransformList)
                                currentTransformList = self.reorderList(currentTransformList)
                                if not currentTransformList == parentDic["Parent"]:
                                    progressAmount = 0
                                    maxProcess = len(parentDic["Parent"])
                                    # define lists to check result
                                    wellImportedList = []
                                    parentIssueList = []
                                    notFoundNodesList = []
                                    # check parenting shaders
                                    for item in parentDic["Parent"]:
                                        progressAmount += 1
                                        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)+" "+item[item.rfind("|"):]))
                                        if not cmds.objExists(item):
                                            parentIssueList.append(item)
                                            shortItem = item[item.rfind("|")+1:]
                                            if cmds.objExists(shortItem):
                                                if len(cmds.ls(shortItem)) == 1:
                                                    # get father name
                                                    longFatherNode = item[:item.rfind("|")]
                                                    shortFatherNode = longFatherNode[longFatherNode.rfind("|")+1:]
                                                    currentFatherList = cmds.listRelatives(shortItem, parent=True)
                                                    if currentFatherList:
                                                        if currentFatherList[0] == shortFatherNode:
                                                            # already child of the father node
                                                            wellImportedList.append(shortItem)
                                                    elif cmds.objExists(longFatherNode):
                                                        # simple parent to existing old father node in the ancient hierarchy
                                                        cmds.parent(shortItem, longFatherNode)
                                                        wellImportedList.append(shortItem)
                                                    elif cmds.objExists(shortFatherNode):
                                                        if len(cmds.ls(shortFatherNode)) == 1:
                                                            # found unique father node in another hierarchy to parent
                                                            cmds.parent(shortItem, shortFatherNode)
                                                            wellImportedList.append(shortItem)
                                                        else:
                                                            self.notWorkedWellIO(self.dpUIinst.lang['i075_moreOne']+" "+self.dpUIinst.lang['i076_sameName']+" "+shortFatherNode)
                                                    #else: #root here
                                                else:
                                                    self.notWorkedWellIO(self.dpUIinst.lang['i075_moreOne']+" "+self.dpUIinst.lang['i076_sameName']+" "+shortItem)
                                            else:
                                                notFoundNodesList.append(shortItem)
                                    if parentIssueList:
                                        if wellImportedList:
                                            self.wellDoneIO(exportedList[-1]+": "+', '.join(parentIssueList))
                                        else:
                                            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
                                    else:
                                        self.wellDoneIO(exportedList[-1])
                                else:
                                    self.wellDoneIO(exportedList[-1])
                            else:
                                self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                        else:
                            self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData'])
                    except Exception as e:
                        self.notWorkedWellIO(self.dpUIinst.lang['r007_notExportedData']+": "+str(e))
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


    def filterTransformList(self, itemList, filterCamera=True, filterConstraint=True, *args):
        """ Remove camera and/or constraints from the given list and return it.
        """
        cameraList = ["|persp", "|top", "|side", "|front"]
        constraintList = ["parentConstraint", "pointConstraint", "orientConstraint", "scaleConstraint", "aimConstraint"]
        toRemoveList = []
        for item in itemList:
            if filterCamera:
                for cameraName in cameraList:
                    if item.endswith(cameraName):
                        toRemoveList.append(item)
            if filterConstraint:
                itemType = cmds.objectType(item)
                if itemType in constraintList:
                    toRemoveList.append(item)
        if toRemoveList:
            for toRemoveNode in toRemoveList:
                itemList.remove(toRemoveNode)
        return itemList


    def reorderList(self, itemList, *args):
        """ Returns a list with high to low counting of '|' in the item list given. That means a descending order.
        """
        return sorted(itemList, key = lambda x: x.count("|"), reverse=True)
