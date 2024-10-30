# importing libraries:
from maya import cmds
from .. import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "ConstraintIO"
TITLE = "r050_constraintIO"
DESCRIPTION = "r051_constraintIODesc"
ICON = "/Icons/dp_constraintIO.png"

DP_CONSTRAINTIO_VERSION = 1.0


class ConstraintIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_CONSTRAINTIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
        self.setActionType("r000_rebuilder")
        self.ioDir = "s_constraintIO"
        self.startName = "dpConstraint"



        self.constraintTypeList = ["parentConstraint", "pointConstraint", "orientConstraint", "scaleConstraint", "aimConstraint", "pointOnPolyConstraint", "geometryConstraint", "normalConstraint"]
    

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
                constraintList = None
                if objList:
                    constraintList = objList
                else:
                    constraintList = cmds.ls(selection=False, type=self.constraintTypeList)
                if constraintList:
                    if self.firstMode: #export
                        toExportDataDic = self.getConstraintDataDic(constraintList)
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
                                constDic = self.pipeliner.getJsonContent(self.ioPath+"/"+exportedList[-1])
                                if constDic:
                                    self.importConstraintData(constDic)
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


    def getConstraintDataDic(self, constraintList, *args):
        """ Processes the given constraint list to collect and mount the info data.
            Returns the dictionary to export.
        """
        if constraintList:
            dic = {}
            attrList = ["interpType", "constraintOffsetPolarity", "aimVectorX", "aimVectorY", "aimVectorZ", "upVectorX", "upVectorY", "upVectorZ", "worldUpType", "worldUpVectorX", "worldUpVectorY", "worldUpVectorZ"]
            #typeAttrDic = {
            #                "parentConstraint" : ["interpType"],
            #                "orientConstraint" : ["interpType"],
            #                "pointConstraint"  : ["constraintOffsetPolarity"],
            #                "normalConstraint" : ["aimVectorX", "aimVectorY", "aimVectorZ", "upVectorX", "upVectorY", "upVectorZ", "worldUpType", "worldUpVectorX", "worldUpVectorY", "worldUpVectorZ"],
            #                "aimConstraint"    : ["aimVectorX", "aimVectorY", "aimVectorZ", "upVectorX", "upVectorY", "upVectorZ", "worldUpType", "worldUpVectorX", "worldUpVectorY", "worldUpVectorZ"]
            #            }
            progressAmount = 0
            maxProcess = len(constraintList)
            for const in constraintList:
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                # getting attributes if they exists
                dic[const] = {"attributes" : {},
                              "type"       : cmds.objectType(const)}
                for attr in attrList:
                    if cmds.objExists(const+"."+attr):
                        dic[const]["attributes"][attr] = cmds.getAttr(const+"."+attr)
                dic[const]["worldUpMatrix"] = []
                if cmds.objExists(const+".worldUpMatrix"):
                    dic[const]["worldUpMatrix"] = cmds.listConnections(const+".worldUpMatrix", source=True, destination=False)
                dic[const]["constraintParentInverseMatrix"] = cmds.listConnections(const+".constraintParentInverseMatrix", source=True, destination=False)
                dic[const]["target"] = {}
                if cmds.objExists(const+".target"):
                    targetAttr = None
                    if cmds.objExists(const+".target[0].targetParentMatrix"):
                        targetAttr = "targetParentMatrix"
                    elif cmds.objExists(const+".target[0].targetGeometry"):
                        targetAttr = "targetGeometry"
                    elif cmds.objExists(const+".target[0].targetMesh"):
                        targetAttr = "targetMesh"
                    if targetAttr:
                        targetList = cmds.getAttr(const+".target", multiIndices=True)
                        for t in targetList:
                            dic[const]["target"][targetAttr] = {t : [cmds.listConnections(const+".target["+str(t)+"]."+targetAttr, source=True, destination=False)[0], cmds.getAttr(const+".target["+str(t)+"].targetWeight")]}
            return dic


    def importConstraintData(self, constDic, *args):
        """ Import constraints from exported dictionary.
            Create missing constraints and set them values if they don't exists.
        """
        progressAmount = 0
        maxProcess = len(constDic.keys())
        # define lists to check result
        wellImportedList = []
        for item in constDic.keys():
            notFoundNodesList = []
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)+" "+item[item.rfind("|"):]))
            # check attributes
            if not cmds.objExists(item):
                constType = constDic[item]["type"]

            # WIP
            
#[, "pointConstraint", "orientConstraint", "scaleConstraint", "aimConstraint", "pointOnPolyConstraint", "geometryConstraint", "normalConstraint"]

                #if constType == "parentConstraint":
                #    cmds.parentConstraint(constDic[item])



                    #cmds.createNode(, , maintainOffset=True, name=item)
            if cmds.objExists(item):
                for attr in constDic[item]["attributes"].keys():
                    if not cmds.objExists(item+"."+attr):
                        try:
                            # add and set attribute value
                            if constDic[item]["attributes"][attr]['type'] == "string":
                                cmds.addAttr(item, longName=attr, dataType="string")
                                cmds.setAttr(item+"."+attr, constDic[item]["attributes"][attr]['value'], type="string")
                            elif constDic[item]["attributes"][attr]['type'] == "enum":
                                cmds.addAttr(item, longName=attr, attributeType="enum", enumName=constDic[item]["attributes"][attr]['enumName'])
                            else:
                                if constDic[item]["attributes"][attr]['minExists']:
                                    if constDic[item]["attributes"][attr]['maxExists']:
                                        cmds.addAttr(item, longName=attr, attributeType=constDic[item]["attributes"][attr]['type'], minValue=constDic[item]["attributes"][attr]['minimum'], maxValue=constDic[item]["attributes"][attr]['maximum'], defaultValue=constDic[item]["attributes"][attr]['default'])
                                    else:
                                        cmds.addAttr(item, longName=attr, attributeType=constDic[item]["attributes"][attr]['type'], minValue=constDic[item]["attributes"][attr]['minimum'], defaultValue=constDic[item]["attributes"][attr]['default'])
                                elif constDic[item]["attributes"][attr]['maxExists']:
                                    cmds.addAttr(item, longName=attr, attributeType=constDic[item]["attributes"][attr]['type'], maxValue=constDic[item]["attributes"][attr]['maximum'], defaultValue=constDic[item]["attributes"][attr]['default'])
                                else:
                                    cmds.addAttr(item, longName=attr, attributeType=constDic[item]["attributes"][attr]['type'], defaultValue=constDic[item]["attributes"][attr]['default'])
                            if constDic[item]["attributes"][attr]['type'] in self.defaultValueTypeList:
                                cmds.setAttr(item+"."+attr, constDic[item]["attributes"][attr]['value'])
                                cmds.setAttr(item+"."+attr, keyable=constDic[item]["attributes"][attr]['keyable'])
                                if not constDic[item]["attributes"][attr]['keyable']:
                                    cmds.setAttr(item+"."+attr, channelBox=constDic[item]["attributes"][attr]['channelBox'])
                                cmds.setAttr(item+"."+attr, lock=constDic[item]["attributes"][attr]['locked'])
                            if not item in wellImportedList:
                                wellImportedList.append(item)
                        except Exception as e:
                            self.notWorkedWellIO(item+" - "+str(e))
                    else:
                        wellImportedList.append(item)
                # reorder attr
                self.dpUIinst.reorderAttributes([item], constDic[item]["order"], False)
            else:
                notFoundNodesList.append(item)
        if wellImportedList:
            self.wellDoneIO(', '.join(wellImportedList))
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
