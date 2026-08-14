from maya import cmds
from maya import mel
from ..base import base
from importlib import reload

# global variables to this module:    
CLASS_NAME = "UpdateGuides"
TITLE = "m186_updateGuides"
DESCRIPTION = "m187_updateGuidesDesc"
WIKI = "06-‐-Tools#-update-guides"



class UpdateGuides(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)


    def build_tool(self, *args):
        # Dictionary that will hold data for update, whatever don't need update will not be saved
        self.updateData = {}
        # Receive the guides list from hook function
        self.guidesDictionary = self.ar.utils.get_hook()
        # List that will hold all new guides instances
        self.newGuidesInstanceList = []
        # Dictionary where the keys are the guides that will be used and don't need update
        # and values are its current parent, this is used to search for possible new parent
        self.guidesToReParentDict = {}

        # If there are guides on the dictionary go on.
        if len(self.guidesDictionary) > 0:
            # Get all info nedeed and store in updateData dictionary
            self.getGuidesToUpdateData()
            if self.ar.data.ui_state:
                # Open the UI
                self.updateGuidesUI()
            else:
                # Update existing outdated guides.
                self.doUpdate()
        else:
            mel.eval('print \"dpAR: '+self.ar.data.lang['e000_guideNotFound']+'\\n\";')


    def summaryUI(self):
        """ Update Guides Summary UI for log info.
        """
        self.ar.utils.close_ui('updateSummary')
        newData = self.listNewAttr()
        cmds.window('updateSummary', title="Update Summary")
        updateSummaryCL = cmds.columnLayout('updateSummaryCL', adjustableColumn=1, rowSpacing=10, columnOffset=("both", 10), parent='updateSummary')
        cmds.text(label=str(len(self.updateData))+' '+self.ar.data.lang['m189_guidesUpdatedSuccess'], align='center', height=30, parent=updateSummaryCL)
        if newData:
            cmds.text(label=self.ar.data.lang['m190_newAttrFound'], align='center', parent=updateSummaryCL)
            updateSummarySL = cmds.scrollLayout('updateSummarySL', width=330, height=400, parent=updateSummaryCL)
            updateSummaryRC = cmds.rowColumnLayout('updateSummaryRC', numberOfColumns=2, adjustableColumn=2, columnSpacing=[(1, 0), (2, 20)], parent=updateSummarySL)
            cmds.text(label=self.ar.data.lang['i205_guide'], align='center', font='boldLabelFont', height=30, parent=updateSummaryRC)
            cmds.text(label=self.ar.data.lang['m191_newAttr'], align='center', font='boldLabelFont', height=30, parent=updateSummaryRC)
            for guide in newData:
                for newAttr in newData[guide]:
                    cmds.text(label=guide, align='left', parent=updateSummaryRC)
                    cmds.text(label=newAttr, align='center', parent=updateSummaryRC)
        cmds.separator(style='none', height=10, parent=updateSummaryCL)
        cmds.text(label=self.ar.data.lang['m192_askOldGuides'], align='center', parent=updateSummaryCL)
        cmds.separator(style='none', height=10, parent=updateSummaryCL)
        cmds.button(label=self.ar.data.lang['m193_deleteOldGuides'], command=self.doDelete, backgroundColor=(1.0, 0.6, 0.4), parent=updateSummaryCL)
        cmds.separator(style='none', height=10, parent=updateSummaryCL)
        cmds.showWindow('updateSummary')


    def updateGuidesUI(self):
        """ Main Update Guides UI.
        """
        self.ar.utils.close_ui('updateGuidesWindow')
        self.ar.utils.close_ui('updateSummary')
        if self.ar.data.ui_state:
            cmds.window('updateGuidesWindow', title="Guides Info")
            updateGuidesCL = cmds.columnLayout('updateGuidesCL', adjustableColumn=1, rowSpacing=10, columnOffset=("both", 10), parent='updateGuidesWindow')
            cmds.text(label='DPAR '+self.ar.data.lang['m194_currentVersion']+' '+str(self.ar.data.version), height=30, align="center", parent=updateGuidesCL)
            if len(self.updateData) > 0:
                updateGuidesSL = cmds.scrollLayout('updateGuidesSL', width=330, height=400, parent=updateGuidesCL)
                updateGuidesBaseRCL = cmds.rowColumnLayout('updateGuidesBaseRCL', numberOfColumns=3, columnSpacing=[(1, 0), (2, 20), (3, 20)], adjustableColumn=2, parent=updateGuidesSL)
                cmds.text(label=self.ar.data.lang['i205_guide'], align='center', font='boldLabelFont', height=30, parent=updateGuidesBaseRCL)
                cmds.text(label=self.ar.data.lang['m006_name'], align='center', font='boldLabelFont', parent=updateGuidesBaseRCL)
                cmds.text(label=self.ar.data.lang['m205_version'], align='center', font='boldLabelFont', parent=updateGuidesBaseRCL)
                for guide in self.updateData:
                    cmds.text(label=guide, align='left', parent=updateGuidesBaseRCL)
                    cmds.text(label=str(self.updateData[guide]['attributes']['customName']), align='center', parent=updateGuidesBaseRCL)
                    cmds.text(label=self.updateData[guide]['attributes']['dpARVersion'], align='left', parent=updateGuidesBaseRCL)
                cmds.separator(style='none', height=10, parent=updateGuidesBaseRCL)
                cmds.button(label=self.ar.data.lang['m186_updateGuides'], command=self.doUpdate, backgroundColor=(0.6, 1.0, 0.7), parent=updateGuidesCL)
            else:
                cmds.text(label=self.ar.data.lang['m188_noGuidesToUpdate'], align='left', parent=updateGuidesCL)
            cmds.separator(style='none', height=10, parent=updateGuidesCL)
            cmds.window('updateGuidesWindow', edit=True, height=1)
            cmds.select(clear=True)
            cmds.showWindow('updateGuidesWindow')
    

    def filterNotNurbsCurveAndTransform(self, mayaObjList):
        """ Remove objects different from transform and nurbsCurve from list.
            Returns cleaned list.
        """
        results = []
        for obj in mayaObjList:
            objType = cmds.objectType(obj)
            if objType == 'nurbsCurve' or objType == 'transform':
                results.append(obj)
        return results
    

    def filterAnotation(self, dpArTransformsList):
        """ Remove _Ant(Anotations) items from list of transforms.
            Return cleaned list.
        """
        results = []
        for obj in dpArTransformsList:
            if not '_Ant' in obj:
                results.append(obj)
        return results


    def getAttrValue(self, guide, attr, locked=False):
        if locked:
            try:
                return cmds.getAttr(guide+'.'+attr, lock=True)
            except:
                return False
        else:
            try:
                return cmds.getAttr(guide+'.'+attr, silent=True)
            except:
                return ''
    

    def getNewGuideInstance(self, newGuideName):
        newGuidesNamesList = list(map(lambda module_instance : module_instance.guide_base, self.newGuidesInstanceList))
        currentGuideInstanceIdx = newGuidesNamesList.index(newGuideName)
        return self.newGuidesInstanceList[currentGuideInstanceIdx]
    

    def translateLimbStyleValue(self, enumValue):
        if enumValue == 1:
            return self.ar.data.lang['m026_biped']
        elif enumValue == 2:
            return self.ar.data.lang['m037_quadruped']
        elif enumValue == 3:
            return self.ar.data.lang['m043_quadSpring']
        elif enumValue == 4:
            return self.ar.data.lang['m155_quadrupedExtra']
        else:
            return self.ar.data.lang['m042_default']


    def translateSpineStyleValue(self, enumValue):
        if enumValue == 1:
            return self.ar.data.lang['m026_biped']
        else:
            return self.ar.data.lang['m042_default']
    

    def translateLimbTypeValue(self, enumValue):
        if enumValue == 1:
            return self.ar.data.lang['m030_leg']
        else:
            return self.ar.data.lang['m028_arm']


    def setAttrValue(self, guide, attr, value):
        try:
            cmds.setAttr(guide+'.'+attr, value)
        except:
            mel.eval('print \"dpAR: '+self.ar.data.lang['m195_couldNotBeSet']+' '+guide+'.'+attr+'\\n\";')


    def setAttrStrValue(self, guide, attr, value):
        try:
            cmds.setAttr(guide+'.'+attr, value, type='string')
        except:
            mel.eval('print \"dpAR: '+self.ar.data.lang['m195_couldNotBeSet']+' '+guide+'.'+attr+'\\n\";')
    

    def setEyelidGuideAttribute(self, guide, value):
        currentInstance = self.getNewGuideInstance(guide)
        cvUpperEyelidLoc = currentInstance.name_guide+"_UpperEyelidLoc"
        cvLowerEyelidLoc = currentInstance.name_guide+"_LowerEyelidLoc"
        jEyelid = currentInstance.name_guide+"_JEyelid"
        jUpperEyelid = currentInstance.name_guide+"_JUpperEyelid"
        jLowerEyelid = currentInstance.name_guide+"_JLowerEyelid"
        cmds.setAttr(guide+".eyelid", value)
        cmds.setAttr(cvUpperEyelidLoc+".visibility", value)
        cmds.setAttr(cvLowerEyelidLoc+".visibility", value)
        cmds.setAttr(jEyelid+".visibility", value)
        cmds.setAttr(jUpperEyelid+".visibility", value)
        cmds.setAttr(jLowerEyelid+".visibility", value)


    def setIrisGuideAttribute(self, guide, value):
        currentInstance = self.getNewGuideInstance(guide)
        cvIrisLoc = currentInstance.name_guide+"_IrisLoc"
        cmds.setAttr(guide+".iris", value)
        cmds.setAttr(cvIrisLoc+".visibility", value)


    def setPupilGuideAttribute(self, guide, value):
        currentInstance = self.getNewGuideInstance(guide)
        cvPupilLoc = currentInstance.name_guide+"_PupilLoc"
        cmds.setAttr(guide+".pupil", value)
        cmds.setAttr(cvPupilLoc+".visibility", value)


    def setNostrilGuideAttribute(self, guide, value):
        currentInstance = self.getNewGuideInstance(guide)
        cmds.setAttr(guide+".nostril", value)
        cmds.setAttr(currentInstance.cvLNostrilLoc+".visibility", value)
        cmds.setAttr(currentInstance.cvRNostrilLoc+".visibility", value)
    

    def checkSetNewGuideToAttr(self, guide, attr, value):
        if value in self.updateData:
            self.setAttrStrValue(guide, attr, self.updateData[value]['newGuide'])
        else:
            self.setAttrStrValue(guide, attr, value)
            

    def setGuideAttributes(self, guide, attr, value, lock=False):
        """ Verify if we have specific attribute cases to work with each kind of module guides.
            Ignore known attributes.
        """
        ignores = ['version', 'controlID', 'className', 'direction', 'pinGuideConstraint', 'moduleNamespace', 'customName', 'moduleInstanceInfo', 'hookNode', 'guideObjectInfo', 'dpARVersion', 'dpID']
        if attr not in ignores:
            if attr == 'nJoints':
                currentInstance = self.getNewGuideInstance(guide)
                currentInstance.changeJointNumber(value)
            elif attr == 'style':
                currentInstance = self.getNewGuideInstance(guide)
                if currentInstance.name == 'Limb':
                    expectedValue = self.translateLimbStyleValue(value)
                else:
                    expectedValue = self.translateSpineStyleValue(value)
                currentInstance.changeStyle(expectedValue)
            elif attr == 'type':
                currentInstance = self.getNewGuideInstance(guide)
                expectedValue = self.translateLimbTypeValue(value)
                currentInstance.changeType(expectedValue)
            elif attr == 'mirrorAxis':
                currentInstance = self.getNewGuideInstance(guide)
                currentInstance.changeMirror(value)
            elif attr == 'mirrorName':
                currentInstance = self.getNewGuideInstance(guide)
                currentInstance.changeMirrorName(value)
            elif attr == 'displayAnnotation':
                currentInstance = self.getNewGuideInstance(guide)
                currentInstance.displayAnnotation(value)
            elif attr == 'rigType':
                currentInstance = self.getNewGuideInstance(guide)
                currentInstance.rigType = value
                self.setAttrStrValue(guide, attr, value)
            elif attr == 'lockedList' and value != '':
                self.setAttrStrValue(guide, attr, value)
            # EYE ATTRIBUTES
            elif attr == 'eyelid':
                self.setEyelidGuideAttribute(guide, value)
            elif attr == 'iris':
                self.setIrisGuideAttribute(guide, value)
            elif attr == 'pupil':
                self.setPupilGuideAttribute(guide, value)
            elif attr == 'aimDirection':
                currentInstance = self.getNewGuideInstance(guide)
                aimMenuItemList = ['+X', '-X', '+Y', '-Y', '+Z', '-Z']
                currentInstance.changeAimDirection(aimMenuItemList[value])
            # self.noseName ATTRIBUTES
            elif attr == 'nostril':
                self.setNostrilGuideAttribute(guide, value)
            # self.suspensionName ATTRIBUTES AND self.wheelName ATTRIBUTES
            elif attr == 'fatherB' or attr == 'geo':
                self.checkSetNewGuideToAttr(guide, attr, value)
            else:
                self.setAttrValue(guide, attr, value)
            if lock:
                cmds.setAttr(f'{guide}.{attr}', lock=True)
            if self.ar.data.ui_state:
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
        children = cmds.listRelatives(baseGuide, allDescendents=True, children=True, type='transform')
        children = self.filterNotNurbsCurveAndTransform(children)
        children = self.filterAnotation(children)
        return children
    

    def splitTransformAttrValues(self, guide, attributes):
        nonTransformDic = {}
        transformDic = {}
        for attribute in attributes:
            attributeValue = self.getAttrValue(guide, attribute)
            if attribute in self.ar.data.transform_attrs[:-1]: #without visibility
                attributeValueLocked = self.getAttrValue(guide, attribute, True)
                transformDic[attribute] = (attributeValue, attributeValueLocked)
            else:
                nonTransformDic[attribute] = attributeValue
        return nonTransformDic, transformDic


    def getGuidesToUpdateData(self):
        """ Scan a dictionary for old guides and gather data needed to update them.
        """
        guides_to_rig = self.ar.utils.get_guides_to_rig()
        instancedModulesStrList = list(map(str, guides_to_rig))
        for baseGuide in self.guidesDictionary:
            guideVersion = cmds.getAttr(baseGuide+'.dpARVersion', silent=True)
            if guideVersion != self.ar.data.version:
                # Create the database holder where the key is the baseGuide
                self.updateData[baseGuide] = {}
                self.updateData[baseGuide]["name"] = self.guidesDictionary[baseGuide]["name"]
                guideAttrList = self.listKeyUserAttr(baseGuide)
                # Create de attributes dictionary for each baseGuide
                self.updateData[baseGuide]['attributes'], self.updateData[baseGuide]['transformAttributes'] = self.splitTransformAttrValues(baseGuide, guideAttrList)
                self.updateData[baseGuide]['instance'] = guides_to_rig[instancedModulesStrList.index(self.updateData[baseGuide]['attributes']['moduleInstanceInfo'])]
                self.updateData[baseGuide]['children'] = {}
                self.updateData[baseGuide]['parent'] = self.getGuideParent(baseGuide)
                children = self.listChildren(baseGuide)
                for child in children:
                    self.updateData[baseGuide]['children'][child] = {'attributes': {}}
                    self.updateData[baseGuide]['children'][child] = {'transformAttributes': {}}
                    guideAttrList = self.listKeyUserAttr(child)
                    self.updateData[baseGuide]['children'][child]['attributes'], self.updateData[baseGuide]['children'][child]['transformAttributes'] = self.splitTransformAttrValues(child, guideAttrList)
            else:
                self.guidesToReParentDict[baseGuide] = self.getGuideParent(baseGuide)


    def createNewGuides(self):
        for guide in self.updateData:
            currentNewGuide = self.ar.config.get_instance(self.updateData[guide]['name'], [self.ar.data.standard_folder])
            currentNewGuide.build_raw_guide()
            # rename as it's predecessor
            name_guide = self.updateData[guide]['attributes']['customName']
            currentNewGuide.set_guide_custom_name(name_guide)
            self.updateData[guide]['newGuide'] = currentNewGuide.guide_base
            self.newGuidesInstanceList.append(currentNewGuide)
            if self.ar.data.ui_state:
                cmds.refresh()


    def renameOldGuides(self):
        for guide in self.updateData:
            currentCustomName = self.updateData[guide]['attributes']['customName']
            if currentCustomName == '' or currentCustomName == None:
                self.updateData[guide]['instance'].set_guide_custom_name(self.updateData[guide]['instance'].guide_base.split(':')[0]+'_OLD')
            else:
                self.updateData[guide]['instance'].set_guide_custom_name(currentCustomName+'_OLD')


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
                    mel.eval('print \"dpAR: '+self.ar.data.lang['m196_parentNotFound']+' '+self.updateData[guide]['newGuide']+'\\n\";')
            if self.ar.data.ui_state:
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
                        mel.eval('print \"dpAR: '+self.ar.data.lang['m197_notPossibleParent']+' '+retainGuide+'\\n\";')
    

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
    

    def filterChildrenFromAnotherBase(self, children, baseGuide):
        filtered_items = []
        filterStr = baseGuide.split(':')[0]
        for children in children:
            if filterStr in children:
                filtered_items.append(children)
        return filtered_items
    

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
                    name_guide = self.updateData[guide]['children'][guide.split(':')[0]+':'+newGuideChildrenOnlyList[i]]
                    self.copyAttrFromGuides(newChild, name_guide['attributes'])
                    self.copyAttrFromGuides(newChild, name_guide['transformAttributes'])
    

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
        self.ar.utils.close_ui('updateSummary')
        for guide in self.updateData:
            if cmds.listRelatives(guide, parent=True):
                cmds.parent(guide, world=True)
        try:
            cmds.delete(*self.updateData.keys())
        except:
            mel.eval('print \"dpAR: '+self.ar.data.lang['e000_guideNotFound']+'\\n\";')
        for guide in self.updateData:
             if self.updateData[guide]['instance'].guide_namespace in cmds.namespaceInfo(listOnlyNamespaces=True):
                cmds.namespace(moveNamespace=(self.updateData[guide]['instance'].guide_namespace, ':'), force=True)
                cmds.namespace(removeNamespace=self.updateData[guide]['instance'].guide_namespace, force=True)
        self.ar.ui_manager.refresh_ui()


    def patchFootRfF(self, *args):
        """ Patching RfF new Foot pivot.
        """
        reverseFootE = "Guide_RfE"
        reverseFootF = "Guide_RfF"
        reverseFootEList = cmds.ls("*:"+reverseFootE)
        reverseFootFList = cmds.ls("*:"+reverseFootF)
        if reverseFootFList:
            needPatch = False
            if reverseFootEList:
                for rfE in reverseFootEList:
                    guideVersion = cmds.getAttr(rfE+".version")
                    if int(guideVersion.split(".")[0]) == 4:
                        if float(guideVersion.split(".")[1]+"."+guideVersion.split(".")[2]) < 4.25:
                            needPatch = True
                            break
            if needPatch:
                for f in reverseFootFList:
                    e = f.replace(reverseFootF, reverseFootE)
                    for attr in ["tx", "ty", "tz"]:
                        cmds.setAttr(f+"."+attr, cmds.getAttr(e+"."+attr))
                    toeList = cmds.listRelatives(e, children=True, type="transform")
                    if toeList:
                        cmds.matchTransform(e, f, position=True, rotation=True)
                        cmds.parent(toeList, f)
                    for attr in ["tx", "ty", "tz"]:
                        cmds.setAttr(e+"."+attr, 0)


    def doUpdate(self, *args):
        """ Main method to update the guides in the scene.
        """
        self.ar.utils.close_ui('updateGuidesWindow')
        # Starts progress bar feedback
        self.ar.utils.setProgress(self.ar.data.lang['m198_renameOldGuides'], self.ar.data.lang['m186_updateGuides'], 7, add_one=False)
        # Rename guides to discard as *_OLD
        self.renameOldGuides()
        self.ar.utils.setProgress(self.ar.data.lang['m199_creatingNewGuides'])
        # Create the new base guides to replace the old ones
        self.createNewGuides()
        self.ar.utils.setProgress(self.ar.data.lang['m200_setAttrs'])
        # Set all attributes except transforms, it's needed for parenting
        self.setNewGuideAttr('attributes')
        self.ar.utils.setProgress(self.ar.data.lang['m201_parentGuides'])
        # Parent all new guides;
        self.parentNewGuides()
        self.ar.utils.setProgress(self.ar.data.lang['m202_setTranforms'])
        # Set new base guides transform attrbutes
        self.setNewGuideAttr('transformAttributes')
        self.ar.utils.setProgress(self.ar.data.lang['m203_setChildGuides'])
        # Set all children attributes
        self.setChildrenGuides()
        self.ar.utils.setProgress(self.ar.data.lang['m201_parentGuides'])
        # After all new guides parented and set, reparent old ones that will be used.
        self.parentRetainGuides()
        self.patchFootRfF()
        cmds.select(clear=True)
        # Ends progress bar feedback
        self.ar.utils.setProgress(endIt=True)
        if self.ar.data.ui_state:
            # Calls for summary window
            self.summaryUI()
        else:
            self.doDelete()

