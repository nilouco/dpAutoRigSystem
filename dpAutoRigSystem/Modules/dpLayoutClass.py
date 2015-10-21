# importing libraries:
from functools import partial

import maya.cmds as cmds

from Library import dpUtils as utils
reload(utils)


class LayoutClass:
    def __init__(self, dpUIinst, langDic, langName, userGuideName, CLASS_NAME, TITLE, DESCRIPTION, ICON):
        """ Initialize the layout class.
        """
        # defining variables:
        self.langDic = langDic
        self.langName = langName
        self.guideModuleName = CLASS_NAME
        self.title = TITLE
        self.description = DESCRIPTION
        self.icon = ICON
        self.userGuideName = userGuideName
    
    
    def basicModuleLayout(self, *args):
        """ Create a Basic Module Layout.
        """
        # BASIC MODULE LAYOUT:
        self.basicColumn = cmds.rowLayout(numberOfColumns=5, width=190, columnWidth5=(30, 20, 80, 20, 35), adjustableColumn=3, columnAlign=[(1, 'left'), (2, 'left'), (3, 'left'), (4, 'left'), (5, 'left')], columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'both', 2)], parent=self.topColumn)
        # create basic module UI:
        self.selectButton = cmds.button(label=" ", annotation=self.langDic[self.langName]['m004_select'], command=partial(self.reCreateEditSelectedModuleLayout, True), backgroundColor=(0.5, 0.5, 0.5), parent=self.basicColumn)
        self.annotationCheckBox = cmds.checkBox(label=" ", annotation=self.langDic[self.langName]['m014_annotation'], onCommand=partial(self.displayAnnotation, 1), offCommand=partial(self.displayAnnotation, 0), value=0, parent=self.basicColumn)
        self.userName = cmds.textField('userName', annotation=self.langDic[self.langName]['m006_customName'], text=cmds.getAttr(self.moduleGrp+".customName"), changeCommand=self.editUserName, parent=self.basicColumn)
        self.colorButton = cmds.button(label=" ", annotation=self.langDic[self.langName]['m013_color'], command=self.colorizeModuleUI, backgroundColor=(0.5, 0.5, 0.5), parent=self.basicColumn)
        shapeSizeValue = cmds.getAttr(self.moduleGrp+'.shapeSize')
        self.shapeSizeFF = cmds.floatField('shapeSizeFF', annotation=self.langDic[self.langName]['m067_shapeSize'], minValue=0.001, value=shapeSizeValue, precision=2, step=0.01, changeCommand=self.changeShapeSize, parent=self.basicColumn)
        # edit values reading from guide:
        displayAnnotationValue = cmds.getAttr(self.moduleGrp+'.displayAnnotation')
        cmds.checkBox(self.annotationCheckBox, edit=True, value=displayAnnotationValue)
        
        # declaring the index color list to override and background color of buttons:
         #Manually add the "none" color
        colorList = [[0.627, 0.627, 0.627]]
        #WARNING --> color index in maya start to 1
        colorList += [cmds.colorIndex(iColor, q=True) for iColor in range(1,32)]

        '''
        self.colorList = [  [0.627, 0.627, 0.627],
                            [0, 0, 0],
                            [0.247, 0.247, 0.247],
                            [0.498, 0.498, 0.498],
                            [0.608, 0, 0.157],
                            [0, 0.016, 0.373],
                            [0, 0, 1],
                            [0, 0.275, 0.094],
                            [0.145, 0, 0.263],
                            [0.780, 0, 0.78],
                            [0.537, 0.278, 0.2],
                            [0.243, 0.133, 0.122],
                            [0.600, 0.145, 0],
                            [1, 0, 0],
                            [0, 1, 0],
                            [0, 0.255, 0.6],
                            [1, 1, 1],
                            [1, 1, 0],
                            [0.388, 0.863, 1],
                            [0.263, 1, 0.635],
                            [1, 0.686, 0.686],
                            [0.890, 0.675, 0.475],
                            [1, 1, 0.384],
                            [0, 0.6, 0.325],
                            [0.627, 0.412, 0.188],
                            [0.620, 0.627, 0.188],
                            [0.408, 0.627, 0.188],
                            [0.188, 0.627, 0.365],
                            [0.188, 0.627, 0.627],
                            [0.188, 0.404, 0.627],
                            [0.435, 0.188, 0.627],
                            [0.627, 0.188, 0.412] ]
        '''
        
        # edit current colorIndex:
        currentIndexColor = cmds.getAttr(self.moduleGrp+'.guideColor')
        self.setColorModule(currentIndexColor)
        self.reCreateEditSelectedModuleLayout(self)
    
    
    def clearSelectedModuleLayout(self, *args):
        """ Clear the selected module layout, because the module was rigged, deleted or unselected maybe.
        """
        try:
            cmds.deleteUI("selectedColumn")
        except:
            pass
    
    
    def reCreateEditSelectedModuleLayout(self, bSelect=True, *args):
        """ Select the moduleGuide, clear the selectedModuleLayout and re-create the mirrorLayout.
        """
        # verify the integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            # select the module to be re-build the selectedLayout:
            if (bSelect):
                cmds.select(self.moduleGrp)
            self.clearSelectedModuleLayout(self)
            try:
                # edit label of frame layout:
                cmds.frameLayout('editSelectedModuleLayoutA', edit=True, label=self.langDic[self.langName]['i011_selectedModule']+" :  "+self.langDic[self.langName][self.title]+" - "+self.userGuideName)
                # edit button with "S" letter indicating it is selected:
                cmds.button(self.selectButton, edit=True, label="S", backgroundColor=(1.0, 1.0, 1.0))
                cmds.columnLayout("selectedColumn", adjustableColumn=True, parent="selectedModuleLayout")
                # re-create segment layout:
                self.segDelColumn = cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 140, 50, 75), columnAlign=[(1, 'right'), (2, 'left'), (3, 'left'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedColumn" )
                self.flipAttrExists = cmds.objExists(self.moduleGrp+".flip")
                self.nJointsAttrExists = cmds.objExists(self.moduleGrp+".nJoints")
                if self.nJointsAttrExists:
                    nJointsAttr = cmds.getAttr(self.moduleGrp+".nJoints")
                    if nJointsAttr > 0:
                        self.nSegmentsText = cmds.text(label=self.langDic[self.langName]['m003_segments'], parent=self.segDelColumn)
                        self.nJointsIF = cmds.intField(value=nJointsAttr, minValue=1, changeCommand=partial(self.changeJointNumber, 0), parent=self.segDelColumn)
                    else:
                        self.nSegmentsText = cmds.text(label=self.langDic[self.langName]['m003_segments'], parent=self.segDelColumn)
                        self.nJointsIF = cmds.intField(value=nJointsAttr, minValue=0, editable=False, parent=self.segDelColumn)
                else:
                    cmds.text(" ", parent=self.segDelColumn)
                    cmds.text(" ", parent=self.segDelColumn)
                # create Delete button:
                self.deleteButton = cmds.button(label=self.langDic[self.langName]['m005_delete'], command=self.deleteModule, backgroundColor=(1.0, 0.7, 0.7), parent=self.segDelColumn)
                self.duplicateButton = cmds.button(label=self.langDic[self.langName]['m070_duplicate'], command=self.duplicateModule, backgroundColor=(0.7, 0.6, 0.8), annotation=self.langDic[self.langName]['i068_CtrlD'], parent=self.segDelColumn)
                
                # reCreate mirror layout:
                self.doubleRigColumn = cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedColumn" )
                cmds.text(self.langDic[self.langName]['m010_Mirror'], parent=self.doubleRigColumn)
                self.mirrorMenu = cmds.optionMenu("mirrorMenu", label='', changeCommand=self.changeMirror, parent=self.doubleRigColumn)
                mirrorMenuItemList = ['off', 'X', 'Y', 'Z', 'XY', 'XZ', 'YZ', 'XYZ']
                for item in mirrorMenuItemList:
                    cmds.menuItem(label=item, parent=self.mirrorMenu)
                # verify if there are a list of mirrorNames to menuOption:
                currentMirrorNameList = cmds.getAttr(self.moduleGrp+".mirrorNameList")
                if currentMirrorNameList:
                    menuNameItemList = str(currentMirrorNameList).split(';')
                else:
                    L = self.langDic[self.langName]['p002_left']
                    R = self.langDic[self.langName]['p003_right']
                    T = self.langDic[self.langName]['p006_top']
                    B = self.langDic[self.langName]['p007_bottom']
                    F = self.langDic[self.langName]['p008_front']
                    Bk= self.langDic[self.langName]['p009_back']
                    menuNameItemList = [L+' --> '+R, R+' --> '+L, T+' --> '+B, B+' --> '+T, F+' --> '+Bk, Bk+' --> '+F]
                # create items for mirrorName menu:
                self.mirrorNameMenu = cmds.optionMenu("mirrorNameMenu", label='', changeCommand=self.changeMirrorName, parent=self.doubleRigColumn)
                menuNameItemText = ""
                for item in menuNameItemList:
                    if item != "":
                        cmds.menuItem(label=item, parent=self.mirrorNameMenu)
                        menuNameItemText += item + ";"
                cmds.setAttr(self.moduleGrp+".mirrorNameList", menuNameItemText, type='string')
                # verify if it is the first time to creation this instance or re-loading an existing guide:
                firstTime = cmds.getAttr(self.moduleGrp+".mirrorAxis")
                if firstTime == "" or firstTime == None:
                    # set initial values to guide base:
                    cmds.setAttr(self.moduleGrp+".mirrorAxis", mirrorMenuItemList[0], type='string')
                    cmds.setAttr(self.moduleGrp+".mirrorName", menuNameItemList[0], type='string')
                else:
                    # get initial values from guide base:
                    initialMirror = cmds.getAttr(self.moduleGrp+".mirrorAxis")
                    initialMirrorName = cmds.getAttr(self.moduleGrp+".mirrorName")
                    # set layout with theses values:
                    cmds.optionMenu(self.mirrorMenu, edit=True, value=initialMirror)
                    cmds.optionMenu(self.mirrorNameMenu, edit=True, value=initialMirrorName)
                    # verify if there is a mirror in a father maybe:
                    self.checkFatherMirror()
                    
                # create Rig button:
                self.rigButton = cmds.button(label="Rig", command=self.rigModule, backgroundColor=(1.0, 1.0, 0.7), parent=self.doubleRigColumn)
                
                # create a flip layout:
                if self.flipAttrExists:
                    self.doubleFlipColumn = cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedColumn" )
                    cmds.text(" ", parent=self.doubleFlipColumn)
                    flipValue = cmds.getAttr(self.moduleGrp+".flip")
                    self.flipCB = cmds.checkBox(label="flip", value=flipValue, changeCommand=self.changeFlip, parent=self.doubleFlipColumn)
            except:
                pass
    
    
    def colorizeModuleUI(self, colorIndex, *args):
        """ Show a little window to choose the color of the button and the override the guide.
        """
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            # creating colorIndex Window:
            if cmds.window('dpColorIndexWindow', query=True, exists=True):
                cmds.deleteUI('dpColorIndexWindow', window=True)
            colorIndex_winWidth  = 305
            colorIndex_winHeight = 250
            self.dpColorIndexWin = cmds.window('dpColorIndexWindow', title='Color Index', iconName='dpColorIndex', widthHeight=(colorIndex_winWidth, colorIndex_winHeight), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
            # creating layout:
            colorIndexLayout = cmds.gridLayout('colorIndexLayout', numberOfColumns=8, cellWidthHeight=(20,20))
            # creating buttons:
            for colorIndex, colorValues in enumerate(self.colorList):
                cmds.button('indexColor_'+str(colorIndex)+'_BT', label=str(colorIndex), backgroundColor=(colorValues[0], colorValues[1], colorValues[2]), command=partial(self.setColorModule, colorIndex), parent=colorIndexLayout)
            # call colorIndex Window:
            cmds.showWindow(self.dpColorIndexWin)
    
    
    def setColorModule(self, colorIndex, *args):
        """ Receives the colorIndex to set the backgroudColor of the module layout and set the overrideColor attribute of the moduleGrp.
        """
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            # set color override of the guideModule:
            cmds.setAttr(self.moduleGrp+'.overrideEnabled', 1)
            cmds.setAttr(self.moduleGrp+'.overrideColor', colorIndex)
            cmds.setAttr(self.moduleGrp+'.guideColor', colorIndex)
            # set the backGround of the button in UI:
            try:
                cmds.button(self.colorButton, edit=True, backgroundColor=self.colorList[colorIndex])
                cmds.deleteUI(self.dpColorIndexWin, window=True)
            except:
                pass
            # disable colorOverride of all shapes inside of the moduleGrp:
            childrenModuleList = cmds.listRelatives(self.moduleGrp, allDescendents=True)
            if childrenModuleList:
                if colorIndex != 0:
                    for child in childrenModuleList:
                        if cmds.getAttr(child+'.overrideEnabled') == 1:
                            cmds.setAttr(child+'.overrideEnabled', 0)
                else:
                    for child in childrenModuleList:
                        if cmds.getAttr(child+'.overrideColor') != 0:
                            cmds.setAttr(child+'.overrideEnabled', 1)
    
    
    def displayAnnotation(self, value, *args):
        """ Get the current display setting from interface to show or hide the Annotation for this module.
        """
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            self.annotation = self.moduleGrp+"_Ant"
            cmds.setAttr(self.annotation+'.visibility', value)
            cmds.setAttr(self.moduleGrp+'.displayAnnotation', value)
    
    
    def checkFatherMirror(self, *args):
        """ Check all fathers and verify if there are mirror applied to father.
            Then, stop mirror for this guide or continue creating its mirror.
        """
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            mirroredGuideFather = utils.mirroredGuideFather(self.moduleGrp)
            if mirroredGuideFather:
                cmds.setAttr(self.moduleGrp+".mirrorEnable", 0)
                # get initial values from father guide base:
                fatherMirror = cmds.getAttr(mirroredGuideFather+".mirrorAxis")
                fatherMirrorName = cmds.getAttr(mirroredGuideFather+".mirrorName")
                # set values to guide base:
                cmds.setAttr(self.moduleGrp+".mirrorAxis", fatherMirror, type='string')
                cmds.setAttr(self.moduleGrp+".mirrorName", fatherMirrorName, type='string')
                # set layout as theses values:
                try:
                    cmds.optionMenu(self.mirrorMenu, edit=True, value=fatherMirror, enable=False)
                    cmds.optionMenu(self.mirrorNameMenu, edit=True, value=fatherMirrorName, enable=False)
                except:
                    pass
                # returns a string 'stopIt' if there is mirrored father guide:
                return "stopIt"
    
    
    def changeFlip(self, *args):
        """ Set the attribute value for flip.
        """
        cmds.setAttr(self.moduleGrp+".flip", cmds.checkBox(self.flipCB, query=True, value=True))
    
    
    def changeShapeSize(self, *args):
        """ Set the attribute value for shapeSize.
        """
        cmds.setAttr(self.moduleGrp+".shapeSize", cmds.floatField(self.shapeSizeFF, query=True, value=True))
    
    
    def changeMirror(self, item, *args):
        """ This function receives the mirror menu item and set it as a string in the guide base (moduleGrp).
            Also, call the builder of the preview mirror (for the viewport).
        """
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            # check if the father guide is in X=0 in order to permit mirror:
            stopMirrorOperation = self.checkFatherMirror()
            # loading Maya matrix node (for mirror porpuses)
            if not (cmds.pluginInfo("decomposeMatrix", query=True, loaded=True)):
                try:
                    # Maya 2012
                    cmds.loadPlugin("decomposeMatrix.mll")
                except:
                    try:
                        # Maya 2013
                        cmds.loadPlugin("matrixNodes.mll")
                    except:
                        print self.langDic[self.langName]['e002_decomposeMatrixNotFound']
                        stopMirrorOperation = "stopIt"
            if not stopMirrorOperation:
                self.mirrorAxis = item
                cmds.setAttr(self.moduleGrp+".mirrorAxis", self.mirrorAxis, type='string')
                self.createPreviewMirror()
    
    
    def changeMirrorName(self, item, *args):
        """ This function receives the mirror menu name item and set it as a string in the guide base (moduleGrp).
        """
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            cmds.setAttr(self.moduleGrp+".mirrorName", item, type='string')
    
    
    def createPreviewMirror(self, *args):
        # re-declaring guideMirror and previewMirror groups:
        self.previewMirrorGrpName = self.moduleGrp[:self.moduleGrp.find(":")]+'_MirrorGrp'
        if cmds.objExists(self.previewMirrorGrpName):
            cmds.delete(self.previewMirrorGrpName)
        
        # verify if there is not any guide module in the guideMirrorGrp and then delete it:
        self.guideMirrorGrp = 'dpAR_GuideMirror_Grp'
        utils.clearNodeGrp(nodeGrpName=self.guideMirrorGrp, attrFind='guideBaseMirror', unparent=False)
        
        # get children, verifying if there are children guides:
        guideChildrenList = utils.getGuideChildrenList(self.moduleGrp)
        
        self.mirrorAxis = cmds.getAttr(self.moduleGrp+".mirrorAxis")
        if self.mirrorAxis != 'off':
            if not cmds.objExists(self.guideMirrorGrp):
                self.guideMirrorGrp = cmds.group(name=self.guideMirrorGrp, empty=True)
                cmds.setAttr(self.guideMirrorGrp+".template", 1)
                cmds.addAttr(self.guideMirrorGrp, longName="selectionChanges", defaultValue=0, attributeType="byte")
            if not cmds.objExists(self.previewMirrorGrpName):
                if guideChildrenList:
                    guideFatherNameList = []
                    for guideChild in guideChildrenList:
                        # get guide father name:
                        guideFatherName = cmds.listRelatives(guideChild, parent=True)
                        guideFatherNameList.append(guideFatherName)
                        # unparent this child guide in order to make the mirror and after return it to the parent:
                        cmds.parent(guideChild, world=True)
                        # set child guide as not mirrorable:
                        cmds.setAttr(guideChild+".mirrorEnable", 0)
                        # get initial values from father guide base:
                        fatherMirrorName = cmds.getAttr(self.moduleGrp+".mirrorName")
                        # set values to guide base:
                        cmds.setAttr(guideChild+".mirrorAxis", self.mirrorAxis, type='string')
                        cmds.setAttr(guideChild+".mirrorName", fatherMirrorName, type='string')
                
                # duplicating the moduleGuide
                duplicated = cmds.duplicate(self.moduleGrp, returnRootsOnly=True)[0]
                duplicatedList = cmds.listRelatives(duplicated, allDescendents=True, fullPath=True)
                # renaming  and reShaping all its children nodes:
                if duplicatedList:
                    for dup in duplicatedList:
                        if cmds.objExists(dup):
                            if "_RadiusCtrl" in dup or "_Ant" in dup:
                                cmds.delete(dup)
                            else:
                                if cmds.objectType(dup) == 'transform' or cmds.objectType(dup) == 'joint':
                                    # rename duplicated node:
                                    dupRenamed = cmds.rename(dup, self.moduleGrp[:self.moduleGrp.find(":")]+'_'+dup[dup.rfind("|")+1:]+'_Mirror')
                                    originalGuide = self.moduleGrp[:self.moduleGrp.find(":")+1]+dup[dup.rfind("|")+1:]
                                    # unlock and unhide all attributes and connect original guide node transformations to the mirror guide node:
                                    attrList = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']
                                    for attr in attrList:
                                        cmds.setAttr(dupRenamed+"."+attr, lock=False, keyable=True)
                                        cmds.connectAttr(originalGuide+'.'+attr, dupRenamed+'.'+attr, force=True)
                                    
                                    # rebuild the shape as a nurbsSphere:
                                    if cmds.objectType(dupRenamed) == 'transform':
                                        childrenShapeList = cmds.listRelatives(dupRenamed, shapes=True, children=True)
                                        if childrenShapeList:
                                            cmds.delete(childrenShapeList)
                                            newSphere = cmds.sphere(name=dupRenamed+"Sphere", radius=0.1, constructionHistory=False)
                                            newSphereShape = cmds.listRelatives(newSphere, shapes=True, children=True)[0]
                                            cmds.parent(newSphereShape, dupRenamed, shape=True, relative=True)
                                            cmds.delete(newSphere)
                                elif cmds.objectType(dup) != 'nurbsCurve':
                                    cmds.delete(dup)
                
                # renaming the previewMirrorGuide:
                self.previewMirrorGuide = cmds.rename(duplicated, self.moduleGrp.replace(":", "_")+'_Mirror')
                cmds.delete(self.previewMirrorGuide+'Shape')
                
                # create a decomposeMatrix node in order to get the worldSpace transformations (like using xform):
                decomposeMatrix = cmds.createNode('decomposeMatrix', name=self.previewMirrorGuide+"_dm")
                cmds.connectAttr(self.moduleGrp+'.worldMatrix', decomposeMatrix+'.inputMatrix', force=True)
                
                # connect original guide base decomposeMatrix node output transformations to the mirror guide base node:
                axisList = ['X', 'Y', 'Z']
                for axis in axisList:
                    cmds.connectAttr(decomposeMatrix+'.outputTranslate'+axis, self.previewMirrorGuide+'.translate'+axis, force=True)
                    cmds.connectAttr(decomposeMatrix+'.outputRotate'+axis, self.previewMirrorGuide+'.rotate'+axis, force=True)
                    cmds.connectAttr(decomposeMatrix+'.outputScale'+axis, self.previewMirrorGuide+'.scale'+axis, force=True)
                
                # analysis if there were children guides for this guide in order to re-parent them:
                if guideChildrenList:
                    for p, guideChild in enumerate(guideChildrenList):
                        # re-parent this child guide to the correct guideFatherName:
                        cmds.parent(guideChild, guideFatherNameList[p])
                
                # create previewMirror group:
                self.previewMirrorGrp = cmds.group(name=self.previewMirrorGrpName, empty=True)
                cmds.parent( self.previewMirrorGuide, self.previewMirrorGrpName, absolute=True )
                # parent the previewMirror group to the guideMirror group:
                cmds.parent(self.previewMirrorGrp, self.guideMirrorGrp, relative=True)
                
                # add attributes to be read as mirror guide when re-creating this module:
                cmds.addAttr(self.previewMirrorGrp, longName='guideBaseMirror', attributeType='bool')
                cmds.setAttr(self.previewMirrorGrp+".guideBaseMirror", 1)
            
            # reset all scale values to 1:
            cmds.setAttr(self.previewMirrorGrp+'.scaleX', 1)
            cmds.setAttr(self.previewMirrorGrp+'.scaleY', 1)
            cmds.setAttr(self.previewMirrorGrp+'.scaleZ', 1)
            # set a negative value to the scale mirror axis:
            for axis in self.mirrorAxis:
                cmds.setAttr(self.previewMirrorGrp+'.scale'+axis, -1)
        
        else:
            if guideChildrenList:
                for guideChild in guideChildrenList:
                    # get initial values from father guide base:
                    fatherMirrorName = cmds.getAttr(self.moduleGrp+".mirrorName")
                    # set values to guide base:
                    cmds.setAttr(guideChild+".mirrorAxis", "off", type='string')
                    cmds.setAttr(guideChild+".mirrorName", fatherMirrorName, type='string')
        
        cmds.select(self.moduleGrp)
