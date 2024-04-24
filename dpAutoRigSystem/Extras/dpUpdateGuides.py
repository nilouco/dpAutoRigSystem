from maya import cmds
from maya import mel

# global variables to this module:    
CLASS_NAME = "UpdateGuides"
TITLE = "m186_updateGuides"
DESCRIPTION = "m187_updateGuidesDesc"
ICON = "/Icons/dp_updateGuides.png"

DP_UPDATEGUIDES_VERSION = 1.7


class UpdateGuides(object):

    def __init__(self, dpUIinst, ui=True, *args, **kwargs):
        # defining variables
        self.dpUIinst = dpUIinst
        self.ui = ui
        self.utils = dpUIinst.utils
        # Dictionary that will hold data for update, whatever don't need update will not be saved
        self.updateData = {}
        self.currentDpArVersion = dpUIinst.dpARVersion
        # Receive the guides list from hook function
        self.guidesDictionary = self.utils.hook()
        # List that will hold all new guides instances
        self.newGuidesInstanceList = []
        # Dictionary where the keys are the guides that will be used and don't need update
        # and values are its current parent, this is used to search for possible new parent
        self.guidesToReParentDict = {}
        self.TRANSFORM_LIST = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']
        # If there are guides on the dictionary go on.
        if len(self.guidesDictionary) > 0:
            # Get all info nedeed and store in updateData dictionary
            self.getGuidesToUpdateData()
        else:
            mel.eval('print \"dpAR: '+self.dpUIinst.lang['e000_guideNotFound']+'\\n\";')
        if self.ui:
            # Open the UI
            self.updateGuidesUI()
        elif len(self.guidesDictionary) > 0:
            # In case of ui = False, update existing outdated guides.
            self.doUpdate()


    def summaryUI(self):
        """ Update Guides Summary UI for log info.
        """
        self.closeExistWin('updateSummary')
        newData = self.listNewAttr()
        cmds.window('updateSummary', title="Update Summary")
        updateSummaryCL = cmds.columnLayout('updateSummaryCL', adjustableColumn=1, rowSpacing=10, columnOffset=("both", 10), parent='updateSummary')
        cmds.text(label=str(len(self.updateData))+' '+self.dpUIinst.lang['m189_guidesUpdatedSuccess'], align='center', height=30, parent=updateSummaryCL)
        if newData:
            cmds.text(label=self.dpUIinst.lang['m190_newAttrFound'], align='center', parent=updateSummaryCL)
            updateSummarySL = cmds.scrollLayout('updateSummarySL', width=330, height=400, parent=updateSummaryCL)
            updateSummaryRC = cmds.rowColumnLayout('updateSummaryRC', numberOfColumns=2, adjustableColumn=2, columnSpacing=[(1, 0), (2, 20)], parent=updateSummarySL)
            cmds.text(label=self.dpUIinst.lang['i205_guide'], align='center', font='boldLabelFont', height=30, parent=updateSummaryRC)
            cmds.text(label=self.dpUIinst.lang['m191_newAttr'], align='center', font='boldLabelFont', height=30, parent=updateSummaryRC)
            for guide in newData:
                for newAttr in newData[guide]:
                    cmds.text(label=guide, align='left', parent=updateSummaryRC)
                    cmds.text(label=newAttr, align='center', parent=updateSummaryRC)
        cmds.separator(style='none', height=10, parent=updateSummaryCL)
        cmds.text(label=self.dpUIinst.lang['m192_askOldGuides'], align='center', parent=updateSummaryCL)
        cmds.separator(style='none', height=10, parent=updateSummaryCL)
        cmds.button(label=self.dpUIinst.lang['m193_deleteOldGuides'], command=self.doDelete, backgroundColor=(1.0, 0.6, 0.4), parent=updateSummaryCL)
        cmds.separator(style='none', height=10, parent=updateSummaryCL)
        cmds.showWindow('updateSummary')


    def closeExistWin(self, winName, *args):
        """ Close existing window.
        """
        if cmds.window(winName, query=True, exists=True):
            cmds.deleteUI(winName, window=True)


    def updateGuidesUI(self):
        """ Main Update Guides UI.
        """
        self.closeExistWin('updateGuidesWindow')
        cmds.window('updateGuidesWindow', title="Guides Info")
        updateGuidesCL = cmds.columnLayout('updateGuidesCL', adjustableColumn=1, rowSpacing=10, columnOffset=("both", 10), parent='updateGuidesWindow')
        cmds.text(label='DPAR '+self.dpUIinst.lang['m194_currentVersion']+' '+str(self.currentDpArVersion), height=30, align="center", parent=updateGuidesCL)
        if len(self.updateData) > 0:
            updateGuidesSL = cmds.scrollLayout('updateGuidesSL', width=330, height=400, parent=updateGuidesCL)
            updateGuidesBaseRCL = cmds.rowColumnLayout('updateGuidesBaseRCL', numberOfColumns=3, columnSpacing=[(1, 0), (2, 20), (3, 20)], adjustableColumn=2, parent=updateGuidesSL)
            cmds.text(label=self.dpUIinst.lang['i205_guide'], align='center', font='boldLabelFont', height=30, parent=updateGuidesBaseRCL)
            cmds.text(label=self.dpUIinst.lang['m006_name'], align='center', font='boldLabelFont', parent=updateGuidesBaseRCL)
            cmds.text(label=self.dpUIinst.lang['m205_version'], align='center', font='boldLabelFont', parent=updateGuidesBaseRCL)
            for guide in self.updateData:
                cmds.text(label=guide, align='left', parent=updateGuidesBaseRCL)
                cmds.text(label=str(self.updateData[guide]['attributes']['customName']), align='center', parent=updateGuidesBaseRCL)
                cmds.text(label=self.updateData[guide]['attributes']['dpARVersion'], align='left', parent=updateGuidesBaseRCL)
            cmds.separator(style='none', height=10, parent=updateGuidesBaseRCL)
            cmds.button(label=self.dpUIinst.lang['m186_updateGuides'], command=self.doUpdate, backgroundColor=(0.6, 1.0, 0.7), parent=updateGuidesCL)
        else:
            cmds.text(label=self.dpUIinst.lang['m188_noGuidesToUpdate'], align='left', parent=updateGuidesCL)
        cmds.separator(style='none', height=10, parent=updateGuidesCL)
        cmds.window('updateGuidesWindow', edit=True, height=1)
        cmds.select(clear=True)
        cmds.showWindow('updateGuidesWindow')


    def setProgressBar(self, progressAmount, status):
        if self.ui:
            cmds.progressWindow(edit=True, progress=progressAmount, status=status, isInterruptable=False)
    

    def filterNotNurbsCurveAndTransform(self, mayaObjList):
        """ Remove objects different from transform and nurbsCurve from list.
            Returns cleaned list.
        """
        resultList = []
        for obj in mayaObjList:
            objType = cmds.objectType(obj)
            if objType == 'nurbsCurve' or objType == 'transform':
                resultList.append(obj)
        return resultList
    

    def filterAnotation(self, dpArTransformsList):
        """ Remove _Ant(Anotations) items from list of transforms.
            Return cleaned list.
        """
        resultList = []
        for obj in dpArTransformsList:
            if not '_Ant' in obj:
                resultList.append(obj)
        return resultList


    def getAttrValue(self, dpGuide, attr, locked=False):
        if locked:
            try:
                return cmds.getAttr(dpGuide+'.'+attr, lock=True)
            except:
                return False
        else:
            try:
                return cmds.getAttr(dpGuide+'.'+attr, silent=True)
            except:
                return ''
    

    def getNewGuideInstance(self, newGuideName):
        newGuidesNamesList = list(map(lambda moduleInstance : moduleInstance.moduleGrp, self.newGuidesInstanceList))
        currentGuideInstanceIdx = newGuidesNamesList.index(newGuideName)
        return self.newGuidesInstanceList[currentGuideInstanceIdx]
    

    def translateLimbStyleValue(self, enumValue):
        if enumValue == 1:
            return self.dpUIinst.lang['m026_biped']
        elif enumValue == 2:
            return self.dpUIinst.lang['m037_quadruped']
        elif enumValue == 3:
            return self.dpUIinst.lang['m043_quadSpring']
        elif enumValue == 4:
            return self.dpUIinst.lang['m155_quadrupedExtra']
        else:
            return self.dpUIinst.lang['m042_default']


    def translateSpineStyleValue(self, enumValue):
        if enumValue == 1:
            return self.dpUIinst.lang['m026_biped']
        else:
            return self.dpUIinst.lang['m042_default']
    

    def translateLimbTypeValue(self, enumValue):
        if enumValue == 1:
            return self.dpUIinst.lang['m030_leg']
        else:
            return self.dpUIinst.lang['m028_arm']


    def setAttrValue(self, dpGuide, attr, value):
        try:
            cmds.setAttr(dpGuide+'.'+attr, value)
        except:
            mel.eval('print \"dpAR: '+self.dpUIinst.lang['m195_couldNotBeSet']+' '+dpGuide+'.'+attr+'\\n\";')


    def setAttrStrValue(self, dpGuide, attr, value):
        try:
            cmds.setAttr(dpGuide+'.'+attr, value, type='string')
        except:
            mel.eval('print \"dpAR: '+self.dpUIinst.lang['m195_couldNotBeSet']+' '+dpGuide+'.'+attr+'\\n\";')
    

    def setEyelidGuideAttribute(self, dpGuide, value):
        currentInstance = self.getNewGuideInstance(dpGuide)
        cvUpperEyelidLoc = currentInstance.guideName+"_UpperEyelidLoc"
        cvLowerEyelidLoc = currentInstance.guideName+"_LowerEyelidLoc"
        jEyelid = currentInstance.guideName+"_JEyelid"
        jUpperEyelid = currentInstance.guideName+"_JUpperEyelid"
        jLowerEyelid = currentInstance.guideName+"_JLowerEyelid"
        cmds.setAttr(dpGuide+".eyelid", value)
        cmds.setAttr(cvUpperEyelidLoc+".visibility", value)
        cmds.setAttr(cvLowerEyelidLoc+".visibility", value)
        cmds.setAttr(jEyelid+".visibility", value)
        cmds.setAttr(jUpperEyelid+".visibility", value)
        cmds.setAttr(jLowerEyelid+".visibility", value)


    def setIrisGuideAttribute(self, dpGuide, value):
        currentInstance = self.getNewGuideInstance(dpGuide)
        cvIrisLoc = currentInstance.guideName+"_IrisLoc"
        cmds.setAttr(dpGuide+".iris", value)
        cmds.setAttr(cvIrisLoc+".visibility", value)


    def setPupilGuideAttribute(self, dpGuide, value):
        currentInstance = self.getNewGuideInstance(dpGuide)
        cvPupilLoc = currentInstance.guideName+"_PupilLoc"
        cmds.setAttr(dpGuide+".pupil", value)
        cmds.setAttr(cvPupilLoc+".visibility", value)


    def setNostrilGuideAttribute(self, dpGuide, value):
        currentInstance = self.getNewGuideInstance(dpGuide)
        cmds.setAttr(dpGuide+".nostril", value)
        cmds.setAttr(currentInstance.cvLNostrilLoc+".visibility", value)
        cmds.setAttr(currentInstance.cvRNostrilLoc+".visibility", value)
    

    def checkSetNewGuideToAttr(self, dpGuide, attr, value):
        if value in self.updateData:
            self.setAttrStrValue(dpGuide, attr, self.updateData[value]['newGuide'])
        else:
            self.setAttrStrValue(dpGuide, attr, value)
            

    def setGuideAttributes(self, dpGuide, attr, value, lock=False):
        """ Verify if we have specific attribute cases to work with each kind of module guides.
            Ignore known attributes.
        """
        ignoreList = ['version', 'controlID', 'className', 'direction', 'pinGuideConstraint', 'moduleNamespace', 'customName', 'moduleInstanceInfo', 'hookNode', 'guideObjectInfo', 'dpARVersion', 'dpID']
        if attr not in ignoreList:
            if attr == 'nJoints':
                currentInstance = self.getNewGuideInstance(dpGuide)
                currentInstance.changeJointNumber(value)
            elif attr == 'style':
                currentInstance = self.getNewGuideInstance(dpGuide)
                if currentInstance.guideModuleName == 'Limb':
                    expectedValue = self.translateLimbStyleValue(value)
                else:
                    expectedValue = self.translateSpineStyleValue(value)
                currentInstance.changeStyle(expectedValue)
            elif attr == 'type':
                currentInstance = self.getNewGuideInstance(dpGuide)
                expectedValue = self.translateLimbTypeValue(value)
                currentInstance.changeType(expectedValue)
            elif attr == 'mirrorAxis':
                currentInstance = self.getNewGuideInstance(dpGuide)
                currentInstance.changeMirror(value)
            elif attr == 'mirrorName':
                currentInstance = self.getNewGuideInstance(dpGuide)
                currentInstance.changeMirrorName(value)
            elif attr == 'rigType':
                currentInstance = self.getNewGuideInstance(dpGuide)
                currentInstance.rigType = value
                self.setAttrStrValue(dpGuide, attr, value)
            elif attr == 'lockedList' and value != '':
                self.setAttrStrValue(dpGuide, attr, value)
            # EYE ATTRIBUTES
            elif attr == 'eyelid':
                self.setEyelidGuideAttribute(dpGuide, value)
            elif attr == 'iris':
                self.setIrisGuideAttribute(dpGuide, value)
            elif attr == 'pupil':
                self.setPupilGuideAttribute(dpGuide, value)
            elif attr == 'aimDirection':
                currentInstance = self.getNewGuideInstance(dpGuide)
                aimMenuItemList = ['+X', '-X', '+Y', '-Y', '+Z', '-Z']
                currentInstance.changeAimDirection(aimMenuItemList[value])
            # NOSE ATTRIBUTES
            elif attr == 'nostril':
                self.setNostrilGuideAttribute(dpGuide, value)
            # SUSPENSION ATTRIBUTES AND WHEEL ATTRIBUTES
            elif attr == 'fatherB' or attr == 'geo':
                self.checkSetNewGuideToAttr(dpGuide, attr, value)
            else:
                self.setAttrValue(dpGuide, attr, value)
            if lock:
                cmds.setAttr(f'{dpGuide}.{attr}', lock=True)
            if self.ui:
                cmds.refresh()
    

    def listKeyUserAttr(self, objWithAttr):
        """ Return a list of attributes, keyable and userDefined
        """
        returnList = []
        keyable = cmds.listAttr(objWithAttr, keyable=True)
        if keyable:
            returnList.extend(keyable)
        userAttr = cmds.listAttr(objWithAttr, userDefined=True)
        if userAttr:
            returnList.extend(userAttr)
        # Guaranty no duplicated attr
        returnList = list(set(returnList))
        return returnList
    

    def getGuideParent(self, baseGuide):
        try:
            return cmds.listRelatives(baseGuide, parent=True)[0]
        except:
            return None


    def listChildren(self, baseGuide):
        childrenList = cmds.listRelatives(baseGuide, allDescendents=True, children=True, type='transform')
        childrenList = self.filterNotNurbsCurveAndTransform(childrenList)
        childrenList = self.filterAnotation(childrenList)
        return childrenList
    

    def splitTransformAttrValues(self, guide, attrList):
        nonTransformDic = {}
        transformDic = {}
        for attribute in attrList:
            attributeValue = self.getAttrValue(guide, attribute)
            if attribute in self.TRANSFORM_LIST:
                attributeValueLocked = self.getAttrValue(guide, attribute, True)
                transformDic[attribute] = (attributeValue, attributeValueLocked)
            else:
                nonTransformDic[attribute] = attributeValue
        return nonTransformDic, transformDic


    def getGuidesToUpdateData(self):
        """ Scan a dictionary for old guides and gather data needed to update them.
        """
        self.dpUIinst.populateCreatedGuideModules()
        instancedModulesStrList = list(map(str, self.dpUIinst.modulesToBeRiggedList))

        for baseGuide in self.guidesDictionary:
            guideVersion = cmds.getAttr(baseGuide+'.dpARVersion', silent=True)
            if guideVersion != self.currentDpArVersion:
                # Create the database holder where the key is the baseGuide
                self.updateData[baseGuide] = {}
                guideAttrList = self.listKeyUserAttr(baseGuide)
                # Create de attributes dictionary for each baseGuide
                self.updateData[baseGuide]['attributes'], self.updateData[baseGuide]['transformAttributes'] = self.splitTransformAttrValues(baseGuide, guideAttrList)

                self.updateData[baseGuide]['idx'] = instancedModulesStrList.index(self.updateData[baseGuide]['attributes']['moduleInstanceInfo'])
                
                self.updateData[baseGuide]['children'] = {}
                self.updateData[baseGuide]['parent'] = self.getGuideParent(baseGuide)
                childrenList = self.listChildren(baseGuide)
                for child in childrenList:
                    self.updateData[baseGuide]['children'][child] = {'attributes': {}}
                    self.updateData[baseGuide]['children'][child] = {'transformAttributes': {}}
                    guideAttrList = self.listKeyUserAttr(child)
                    self.updateData[baseGuide]['children'][child]['attributes'], self.updateData[baseGuide]['children'][child]['transformAttributes'] = self.splitTransformAttrValues(child, guideAttrList)
            else:
                self.guidesToReParentDict[baseGuide] = self.getGuideParent(baseGuide)


    def createNewGuides(self):
        beforeNewGuidesMTBRList = self.dpUIinst.modulesToBeRiggedList
        for guide in self.updateData:
            guideType = beforeNewGuidesMTBRList[self.updateData[guide]['idx']].guideModuleName
            # create the new guide
            currentNewGuide = self.dpUIinst.initGuide("dp"+guideType, "Modules")
            # rename as it's predecessor
            guideName = self.updateData[guide]['attributes']['customName']
            currentNewGuide.editUserName(guideName)
            self.updateData[guide]['newGuide'] = currentNewGuide.moduleGrp
            self.updateData[guide]['guideModuleName'] = guideType
            self.newGuidesInstanceList.append(currentNewGuide)
            if self.ui:
                cmds.refresh()


    def renameOldGuides(self):
        for guide in self.updateData:
            currentCustomName = self.updateData[guide]['attributes']['customName']
            if currentCustomName == '' or currentCustomName == None:
                self.dpUIinst.modulesToBeRiggedList[self.updateData[guide]['idx']].editUserName(self.dpUIinst.modulesToBeRiggedList[self.updateData[guide]['idx']].moduleGrp.split(':')[0]+'_OLD')
            else:
                self.dpUIinst.modulesToBeRiggedList[self.updateData[guide]['idx']].editUserName(currentCustomName+'_OLD')


    def retrieveNewParent(self, currentParent):
        currentParentBase = currentParent.split(':')[0]+":Guide_Base"
        if currentParentBase in self.updateData.keys():
            newParentBase = self.updateData[currentParentBase]['newGuide']
            newParentFinal = newParentBase.split(':')[0]+':'+currentParent.split(':')[1]
            return newParentFinal
        else:
            return currentParent


    def parentNewGuides(self):
        for guide in self.updateData:
            hasParent = self.updateData[guide]['parent']
            if hasParent != None:
                newParentFinal = self.retrieveNewParent(hasParent)
                try:
                    cmds.parent(self.updateData[guide]['newGuide'], newParentFinal)
                except:
                    mel.eval('print \"dpAR: '+self.dpUIinst.lang['m196_parentNotFound']+' '+self.updateData[guide]['newGuide']+'\\n\";')
            if self.ui:
                cmds.refresh()


    def parentRetainGuides(self):
        if len(self.guidesToReParentDict) > 0:
            for retainGuide in self.guidesToReParentDict:
                hasParent = self.guidesToReParentDict[retainGuide]
                if hasParent != None:
                    newParentFinal = self.retrieveNewParent(hasParent)
                    try:
                        cmds.parent(retainGuide, newParentFinal)
                    except:
                        mel.eval('print \"dpAR: '+self.dpUIinst.lang['m197_notPossibleParent']+' '+retainGuide+'\\n\";')
    

    def sendTransformsToListEnd(self, elementList):
        toMoveList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
        for element in toMoveList:
            elementList.append(elementList.pop(elementList.index(element)))


    def copyAttrFromGuides(self, newGuide, oldGuideAttrDic):
        newGuideAttrList = self.listKeyUserAttr(newGuide)
        # For each attribute in the new guide check if exists equivalent in the old one, and check if the value is different, in that case
        # set the new guide attr value to the old one.
        for attr in newGuideAttrList:
            if attr in oldGuideAttrDic:
                currentValue = self.getAttrValue(newGuide, attr)
                if isinstance(oldGuideAttrDic[attr], tuple):
                    if currentValue != oldGuideAttrDic[attr][0] or oldGuideAttrDic[attr][1]:
                        self.setGuideAttributes(newGuide, attr, oldGuideAttrDic[attr][0], oldGuideAttrDic[attr][1])
                else:
                    if currentValue != oldGuideAttrDic[attr]:
                        self.setGuideAttributes(newGuide, attr, oldGuideAttrDic[attr])


    def setNewGuideAttr(self, attributesSet):
        for guide in self.updateData:
            self.copyAttrFromGuides(self.updateData[guide]['newGuide'], self.updateData[guide][attributesSet])
    

    def filterChildrenFromAnotherBase(self, childrenList, baseGuide):
        filteredList = []
        filterStr = baseGuide.split(':')[0]
        for children in childrenList:
            if filterStr in children:
                filteredList.append(children)
        return filteredList
    

    def setChildrenGuides(self):
        """ Set all attributes from children with same BaseGuide to avoid double set.
        """
        for guide in self.updateData:
            newGuideChildrenList = self.listChildren(self.updateData[guide]['newGuide'])
            newGuideChildrenList = self.filterChildrenFromAnotherBase(newGuideChildrenList, self.updateData[guide]['newGuide'])
            oldGuideChildrenList = self.updateData[guide]['children'].keys()
            oldGuideChildrenList = self.filterChildrenFromAnotherBase(oldGuideChildrenList, guide)
            newGuideChildrenOnlyList = list(map(lambda name : name.split(':')[1], newGuideChildrenList))
            oldGuideChildrenOnlyList = list(map(lambda name : name.split(':')[1], oldGuideChildrenList))
            for i, newChild in enumerate(newGuideChildrenList):
                if newGuideChildrenOnlyList[i] in oldGuideChildrenOnlyList:
                    guideName = self.updateData[guide]['children'][guide.split(':')[0]+':'+newGuideChildrenOnlyList[i]]
                    self.copyAttrFromGuides(newChild, guideName['attributes'])
                    self.copyAttrFromGuides(newChild, guideName['transformAttributes'])
    

    def listNewAttr(self):
        """ List new attributes from created guides for possible input.
            Returns new data dictionary if it exists.
        """
        newDataDic = {}
        for guide in self.updateData:
            oldGuideSet = set(self.updateData[guide]['attributes']) | set(self.updateData[guide]['transformAttributes'])
            newGuideSet = set(self.listKeyUserAttr(self.updateData[guide]['newGuide']))
            newAttributesSet = newGuideSet - oldGuideSet
            if len(newAttributesSet) > 0:
                for attr in newAttributesSet:
                    if guide in newDataDic:
                        newDataDic[guide].append(attr)
                    else:
                        newDataDic[guide] = [attr]
        if len(newDataDic.keys()) == 0:
            return False
        else:
            return newDataDic
    

    def doDelete(self, *args):
        self.closeExistWin('updateSummary')
        for guide in self.updateData:
            try:
                cmds.parent(guide, world=True)
            except Exception as e:
                print(e)
        try:
            cmds.delete(*self.updateData.keys())
        except:
            mel.eval('print \"dpAR: '+self.dpUIinst.lang['e000_guideNotFound']+'\\n\";')
        allNamespaceList = cmds.namespaceInfo(listOnlyNamespaces=True)
        for guide in self.updateData:
             if self.dpUIinst.modulesToBeRiggedList[self.updateData[guide]['idx']].guideNamespace in allNamespaceList:
                    cmds.namespace(moveNamespace=(self.dpUIinst.modulesToBeRiggedList[self.updateData[guide]['idx']].guideNamespace, ':'), force=True)
                    cmds.namespace(removeNamespace=self.dpUIinst.modulesToBeRiggedList[self.updateData[guide]['idx']].guideNamespace, force=True)
        self.dpUIinst.reloadMainUI()


    def doUpdate(self, *args):
        """ Main method to update the guides in the scene.
        """
        self.closeExistWin('updateGuidesWindow')
        if self.ui:
            # Starts progress bar feedback
            cmds.progressWindow(title='Updating Guides', progress=0, maxValue=7, status=self.dpUIinst.lang['m198_renameOldGuides'])
        # Rename guides to discard as *_OLD
        self.renameOldGuides()
        self.setProgressBar(1, self.dpUIinst.lang['m199_creatingNewGuides'])
        # Create the new base guides to replace the old ones
        self.createNewGuides()
        self.setProgressBar(2, self.dpUIinst.lang['m200_setAttrs'])
        # Set all attributes except transforms, it's needed for parenting
        self.setNewGuideAttr('attributes')
        self.setProgressBar(3, self.dpUIinst.lang['m201_parentGuides'])
        # Parent all new guides;
        self.parentNewGuides()
        self.setProgressBar(4, self.dpUIinst.lang['m202_setTranforms'])
        # Set new base guides transform attrbutes
        self.setNewGuideAttr('transformAttributes')
        self.setProgressBar(5, self.dpUIinst.lang['m203_setChildGuides'])
        # Set all children attributes
        self.setChildrenGuides()
        self.setProgressBar(6, self.dpUIinst.lang['m201_parentGuides'])
        # After all new guides parented and set, reparent old ones that will be used.
        self.parentRetainGuides()
        cmds.select(clear=True)
        if self.ui:
            self.setProgressBar(7, self.dpUIinst.lang['m204_finish'])
            # Ends progress bar feedback
            cmds.progressWindow(endProgress=True)
            # Calls for summary window
            self.summaryUI()
        else:
            self.doDelete()
