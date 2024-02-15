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
        # ensure file has a name to define dpData path
        if not cmds.file(query=True, sceneName=True):
            self.notWorkedWellIO(self.dpUIinst.lang['i201_saveScene'])
        else:
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
                        transformList = self.removeCameras(transformList)
                        transformList = self.reorderedList(transformList)
                        parentDic = {"Parent" : transformList}
                        try:
                            # export json file
                            self.pipeliner.makeDirIfNotExists(self.ioPath)
                            jsonName = self.ioPath+"/"+self.startName+"_"+self.pipeliner.getCurrentFileName()+".json"
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
                                currentTransformList = self.removeCameras(currentTransformList)
                                currentTransformList = self.reorderedList(currentTransformList)

                                if not currentTransformList == parentDic["Parent"]:
                                    progressAmount = 0
                                    maxProcess = len(parentDic["Parent"])

                                    wellImportedList = []
                                    parentIssueList = []
                                    # check parenting shaders
                                    for item in parentDic["Parent"]:
                                        if self.verbose:
                                            # Update progress window
                                            progressAmount += 1
                                            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                                                        
                                        
                                        if not cmds.objExists(item):
                                            parentIssueList.append(item)

                                            # WIP

                                            shortItem = item[item.rfind("|")+1:]
                                            print("shortItem = ", shortItem)
                                            if cmds.objExists(shortItem):
                                                itemSelList = cmds.ls(shortItem)
                                                if itemSelList:
                                                    if len(itemSelList) == 1:
                                                        shortFatherNode = item[:item.rfind("|")]
                                                        print("shortFatherNode1 =", shortFatherNode)
                                                        shortFatherNode = shortFatherNode[shortFatherNode.rfind("|")+1:]
                                                        print("shortFatherNode2 =", shortFatherNode)
                                                        if cmds.objExists(shortFatherNode):
                                                            fatherSelList = cmds.ls(shortFatherNode)
                                                            if fatherSelList:
                                                                if len(fatherSelList) == 1:
                                                                    cmds.parent(shortItem, shortFatherNode)
                                                                    wellImportedList.append(shortItem)

                                            # TODO: node/father in root, don't exists father anymore, 

                                    if parentIssueList:
                                        print("parentIssueList =", parentIssueList)

                                        if wellImportedList:
                                            self.wellDoneIO(exportedList[-1]+": "+', '.join(parentIssueList))
                                        else:
                                            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(parentIssueList))
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
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        self.refreshView()
        return self.dataLogDic


    def removeCameras(self, camList, *args):
        """ Remove default cameras from given list and return it.
        """
        ignoreList = ["|persp", "|top", "|side", "|front"]
        for ignoreNode in ignoreList:
            if ignoreNode in camList:
                camList.remove(ignoreNode)
        return camList
    

    def reorderedList(self, itemList, *args):
        """ Returns a list with high to low counting of '|' in the item list given. That means a descending order.
        """
        return sorted(itemList, key = lambda x: x.count("|"), reverse=True)





    # TODO
    #
    # get uniqueName
    # parent unique node to unique father
    # check again after reparenting to see if we got orphan transforms
    #
    #