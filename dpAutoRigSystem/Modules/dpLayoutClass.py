# importing libraries:
from maya import cmds
from functools import partial

DP_LAYOUTCLASS_VERSION = 2.5


class LayoutClass(object):
    def __init__(self, dpUIinst, userGuideName, CLASS_NAME, TITLE, DESCRIPTION, ICON):
        """ Initialize the layout class.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        self.guideModuleName = CLASS_NAME
        self.title = TITLE
        self.description = DESCRIPTION
        self.icon = ICON
        self.userGuideName = userGuideName
        self.utils = dpUIinst.utils
    
    
    def basicModuleLayout(self, *args):
        """ Create a Basic Module dpLayoutClass.
        """
        # declaring facial variables
        self.browTgtList = ["BrowFrown", "BrowSad", "BrowDown", "BrowUp"]
        self.eyelidTgtList = [None, None, "EyelidsClose", "EyelidsOpen"]
        self.mouthTgtList = ["MouthNarrow", "MouthWide", "MouthSad", "MouthSmile"]
        self.lipsTgtList = ["R_LipsSide", "L_LipsSide", "LipsDown", "LipsUp", "LipsBack", "LipsFront"]
        self.sneerTgtList = ["R_Sneer", "L_Sneer", None, None, "UpperLipBack", "UpperLipFront"]
        self.grimaceTgtList = ["R_Grimace", "L_Grimace", None, None, "LowerLipBack", "LowerLipFront"]
        self.faceTgtList = ["L_Puff", "R_Puff", "Pucker", "SoftSmile", "BigSmile", "AAA", "OOO", "UUU", "FFF", "MMM"]
        self.bsType = "bsType"
        self.jointsType = "jointsType"
        self.facialUserType = self.bsType
        # plus icon
        path = self.utils.findPath("dpAutoRig.py")
        self.iconPlus = path.replace("Modules", "/Icons/dp_plusInfo.png")
        # BASIC MODULE LAYOUT:
        self.basicColumn = cmds.rowLayout(numberOfColumns=3, width=190, columnWidth3=(30, 120, 20), adjustableColumn=2, columnAlign=[(1, 'left'), (2, 'left'), (3, 'left')], columnAttach=[(1, 'both', 2), (2, 'both', 4), (3, 'both', 0)], parent=self.topColumn)
        # create basic module UI:
        self.selectButton = cmds.button(label=" ", annotation=self.dpUIinst.lang['m004_select'], command=partial(self.reCreateEditSelectedModuleLayout, True), backgroundColor=(0.5, 0.5, 0.5), parent=self.basicColumn)
        self.userName = cmds.textField('userName', annotation=self.dpUIinst.lang['i101_customName'], text=cmds.getAttr(self.moduleGrp+".customName"), changeCommand=self.editUserName, parent=self.basicColumn)
        cmds.iconTextButton(image=self.iconPlus, height=30, width=17, style='iconOnly', command=partial(self.plusInfoWin, self), parent=self.basicColumn)
        self.reCreateEditSelectedModuleLayout(self)
    
    
    def clearSelectedModuleLayout(self, *args):
        """ Clear the selected module layout, because the module was rigged, deleted or unselected maybe.
        """
        try:
            cmds.deleteUI("selectedModuleColumn")
        except:
            pass
    
    
    def loadGeo(self, *args):
        """ Loads the selected node to geoTextField in selectedModuleLayout.
        """
        isGeometry = False
        selList = cmds.ls(selection=True)
        if selList:
            if cmds.objExists(selList[0]):
                childList = cmds.listRelatives(selList[0], children=True, allDescendents=True)
                if childList:
                    for item in childList:
                        itemType = cmds.objectType(item)
                        if itemType == "mesh" or itemType == "nurbsSurface":
                            isGeometry = True
        if isGeometry:
            cmds.textField(self.geoTF, edit=True, text=selList[0])
            cmds.setAttr(self.moduleGrp+".geo", selList[0], type='string')
    
    
    def reCreateEditSelectedModuleLayout(self, bSelect=True, *args):
        """ Select the moduleGuide, clear the selectedModuleLayout and re-create the mirrorLayout and custom attribute layouts.
        """
        self.fatherMirrorExists = None
        self.fatherFlipExists = None
        # verify the integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            # select the module to be re-build the selectedLayout:
            if bSelect:
                cmds.select(self.moduleGrp)
            self.clearSelectedModuleLayout(self)
            try:
                # check if attributes existing:
                self.nJointsAttrExists = cmds.objExists(self.moduleGrp+".nJoints")
                self.aimDirectionAttrExists = cmds.objExists(self.moduleGrp+".aimDirection")
                self.flipAttrExists = cmds.objExists(self.moduleGrp+".flip")
                self.indirectSkinAttrExists = cmds.objExists(self.moduleGrp+".indirectSkin")
                self.eyelidExists = cmds.objExists(self.moduleGrp+".eyelid")
                self.degreeExists = cmds.objExists(self.moduleGrp+".degree")
                self.geoExists = cmds.objExists(self.moduleGrp+".geo")
                self.startFrameExists = cmds.objExists(self.moduleGrp+".startFrame")
                self.steeringExists = cmds.objExists(self.moduleGrp+".steering")
                self.fatherBExists = cmds.objExists(self.moduleGrp+".fatherB")
                self.articulationExists = cmds.objExists(self.moduleGrp+".articulation")
                self.nostrilExists = cmds.objExists(self.moduleGrp+".nostril")
                self.correctiveExists = cmds.objExists(self.moduleGrp+".corrective")
                self.nMainCtrlAttrExists = cmds.objExists(self.moduleGrp+".mainControls")
                self.dynamicExists = cmds.objExists(self.moduleGrp+".dynamic")
                self.deformerExists = cmds.objExists(self.moduleGrp+".deformer")
                self.facialExists = cmds.objExists(self.moduleGrp+".facial")
                self.deformedByExists = cmds.objExists(self.moduleGrp+".deformedBy")
                
                # UI
                # edit label of frame layout:
                guideName = cmds.getAttr(self.moduleGrp+".customName")
                if not guideName:
                    guideName = self.userGuideName
                cmds.frameLayout('editSelectedModuleLayoutA', edit=True, label=self.dpUIinst.lang['i011_editSelected']+" "+self.dpUIinst.lang['i143_module']+" :  "+self.dpUIinst.lang[self.title]+" - "+guideName)
                # edit button with "S" letter indicating it is selected:
                cmds.button(self.selectButton, edit=True, label="S", backgroundColor=(1.0, 1.0, 1.0))
                cmds.columnLayout("selectedModuleColumn", adjustableColumn=True, parent="selectedModuleLayout")
                # re-create segment layout:
                self.segDelColumn = cmds.rowLayout('segDelColumn', numberOfColumns=4, columnWidth4=(100, 140, 50, 75), columnAlign=[(1, 'right'), (2, 'left'), (3, 'left'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'left', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedModuleColumn" )
                if self.nJointsAttrExists:
                    self.nJointsAttr = cmds.getAttr(self.moduleGrp+".nJoints")
                    if self.nJointsAttr > 0:
                        self.nSegmentsText = cmds.text(label=self.dpUIinst.lang['m003_segments'], parent=self.segDelColumn)
                        self.nJointsIF = cmds.intField(value=self.nJointsAttr, minValue=1, changeCommand=partial(self.changeJointNumber, 0), parent=self.segDelColumn)
                    else:
                        self.nSegmentsText = cmds.text(label=self.dpUIinst.lang['m003_segments'], parent=self.segDelColumn)
                        self.nJointsIF = cmds.intField(value=self.nJointsAttr, minValue=0, editable=False, parent=self.segDelColumn)
                else:
                    cmds.text(" ", parent=self.segDelColumn)
                    cmds.text(" ", parent=self.segDelColumn)
                # create Delete button:
                self.deleteButton = cmds.button(label=self.dpUIinst.lang['m005_delete'], command=self.deleteModule, backgroundColor=(1.0, 0.7, 0.7), parent=self.segDelColumn)
                self.duplicateButton = cmds.button(label=self.dpUIinst.lang['m070_duplicate'], command=self.duplicateModule, backgroundColor=(0.7, 0.6, 0.8), annotation=self.dpUIinst.lang['i068_CtrlD'], parent=self.segDelColumn)

                # reCreate mirror layout:
                self.doubleRigColumn = cmds.rowLayout('doubleRigColumn', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedModuleColumn" )
                cmds.text(self.dpUIinst.lang['m010_mirror'], parent=self.doubleRigColumn)
                self.mirrorMenu = cmds.optionMenu("mirrorMenu", label='', changeCommand=self.changeMirror, parent=self.doubleRigColumn)
                mirrorMenuItemList = ['off', 'X', 'Y', 'Z', 'XY', 'XZ', 'YZ', 'XYZ']
                for item in mirrorMenuItemList:
                    cmds.menuItem(label=item, parent=self.mirrorMenu)
                # verify if there are a list of mirrorNames to menuOption:
                currentMirrorNameList = cmds.getAttr(self.moduleGrp+".mirrorNameList")
                if currentMirrorNameList:
                    menuNameItemList = str(currentMirrorNameList).split(';')
                else:
                    L = self.dpUIinst.lang['p002_left']
                    R = self.dpUIinst.lang['p003_right']
                    T = self.dpUIinst.lang['p004_top']
                    B = self.dpUIinst.lang['p005_bottom']
                    F = self.dpUIinst.lang['p006_front']
                    Bk= self.dpUIinst.lang['p007_back']
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
                    self.fatherMirrorExists = self.checkFatherMirror()
                    
                # create Rig button:
                self.rigButton = cmds.button(label="Rig", command=self.rigModule, backgroundColor=(1.0, 1.0, 0.7), parent=self.doubleRigColumn)
                
                # aim direction for eye look at:
                if self.aimDirectionAttrExists:
                    self.aimDirectionLayout = cmds.rowLayout('aimDirectionLayout', numberOfColumns=4, columnWidth4=(100, 50, 180, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedModuleColumn" )
                    cmds.text(self.dpUIinst.lang['i082_aimDirection'], parent=self.aimDirectionLayout)
                    self.aimMenu = cmds.optionMenu("aimMenu", label='', changeCommand=self.changeAimDirection, parent=self.aimDirectionLayout)
                    self.aimMenuItemList = ['+X', '-X', '+Y', '-Y', '+Z', '-Z']
                    for item in self.aimMenuItemList:
                        cmds.menuItem(label=item, parent=self.aimMenu)
                    currentAimDirection = cmds.getAttr(self.moduleGrp+".aimDirection")
                    # set layout with the current value:
                    cmds.optionMenu(self.aimMenu, edit=True, value=self.aimMenuItemList[currentAimDirection])
                
                # create a flip layout:
                if self.flipAttrExists:
                    self.flipLayout = cmds.rowLayout('flipLayout', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedModuleColumn" )
                    cmds.text(" ", parent=self.flipLayout)
                    flipValue = cmds.getAttr(self.moduleGrp+".flip")
                    self.flipCB = cmds.checkBox(label="flip", value=flipValue, changeCommand=self.changeFlip, parent=self.flipLayout)
                    if self.fatherMirrorExists:
                        if self.fatherFlipExists:
                            cmds.checkBox(self.flipCB, edit=True, enable=False)
                    
                # create an indirectSkin layout:
                if self.indirectSkinAttrExists:
                    self.indirectSkinLayout = cmds.rowLayout('indirectSkinLayout', numberOfColumns=4, columnWidth4=(100, 150, 10, 40), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedModuleColumn" )
                    cmds.text(" ", parent=self.indirectSkinLayout)
                    indirectSkinValue = cmds.getAttr(self.moduleGrp+".indirectSkin")
                    self.indirectSkinCB = cmds.checkBox(label="Indirect Skinning", value=indirectSkinValue, changeCommand=self.changeIndirectSkin, parent=self.indirectSkinLayout)
                    cmds.text(" ", parent=self.indirectSkinLayout)
                    holderValue = cmds.getAttr(self.moduleGrp+".holder")
                    self.holderCB = cmds.checkBox(label=self.dpUIinst.lang['c046_holder'], value=holderValue, enable=False, changeCommand=self.changeHolder, parent=self.indirectSkinLayout)
                    self.sdkLocatorLayout = cmds.rowLayout('sdkLocatorLayout', numberOfColumns=4, columnWidth4=(100, 150, 10, 40), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedModuleColumn" )
                    cmds.text(" ", parent=self.sdkLocatorLayout)
                    cmds.text(" ", parent=self.sdkLocatorLayout)
                    cmds.text(" ", parent=self.sdkLocatorLayout)
                    sdkLocatorValue = cmds.getAttr(self.moduleGrp+".sdkLocator")
                    self.sdkLocatorCB = cmds.checkBox(label="SDK Locator", value=sdkLocatorValue, enable=False, changeCommand=self.changeSDKLocator, parent=self.sdkLocatorLayout)
                    self.changeIndirectSkin()
                    
                # create eyelid layout:
                if self.eyelidExists:
                    self.eyelidLayout = cmds.rowLayout('eyelidLayout', numberOfColumns=6, columnWidth6=(30, 75, 75, 80, 40, 60), columnAlign=[(1, 'right'), (2, 'left'), (6, 'right')], adjustableColumn=6, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 2), (5, 'both', 2), (6, 'both', 2)], parent="selectedModuleColumn" )
                    cmds.text(" ", parent=self.eyelidLayout)
                    eyelidValue = cmds.getAttr(self.moduleGrp+".eyelid")
                    self.eyelidCB = cmds.checkBox(label=self.dpUIinst.lang['i079_eyelid'], value=eyelidValue, changeCommand=self.changeEyelid, parent=self.eyelidLayout)
                    lidPivotValue = cmds.getAttr(self.moduleGrp+".lidPivot")
                    self.lidPivotCB = cmds.checkBox(label=self.dpUIinst.lang['i283_pivot'], value=lidPivotValue, changeCommand=self.changeLidPivot, parent=self.eyelidLayout)
                    specValue = cmds.getAttr(self.moduleGrp+".specular")
                    self.specCB = cmds.checkBox(label=self.dpUIinst.lang['i184_specular'], value=specValue, changeCommand=self.changeSpecular, parent=self.eyelidLayout)
                    irisValue = cmds.getAttr(self.moduleGrp+".iris")
                    self.irisCB = cmds.checkBox(label=self.dpUIinst.lang['i080_iris'], value=irisValue, changeCommand=self.changeIris, parent=self.eyelidLayout)
                    pupilValue = cmds.getAttr(self.moduleGrp+".pupil")
                    self.pupilCB = cmds.checkBox(label=self.dpUIinst.lang['i081_pupil'], value=pupilValue, changeCommand=self.changePupil, parent=self.eyelidLayout)
                
                # create geometry layout:
                if self.geoExists:
                    self.geoColumn = cmds.rowLayout('geoColumn', numberOfColumns=3, columnWidth3=(100, 100, 70), columnAlign=[(1, 'right'), (3, 'right')], adjustableColumn=3, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2)], parent="selectedModuleColumn" )
                    cmds.button(label=self.dpUIinst.lang["m146_geo"]+" >", command=self.loadGeo, parent=self.geoColumn)
                    self.geoTF = cmds.textField('geoTF', text='', enable=True, changeCommand=self.changeGeo, parent=self.geoColumn)
                    currentGeo = cmds.getAttr(self.moduleGrp+".geo")
                    if currentGeo:
                        cmds.textField(self.geoTF, edit=True, text=currentGeo, parent=self.geoColumn)
                
                # create startFrame layout:
                if self.startFrameExists:
                    self.startFrameColumn = cmds.rowLayout('startFrameColumn', numberOfColumns=4, columnWidth4=(100, 60, 70, 40), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedModuleColumn" )
                    cmds.text(self.dpUIinst.lang["i169_startFrame"], parent=self.startFrameColumn)
                    self.startFrameIF = cmds.intField('startFrameIF', value=1, changeCommand=self.changeStartFrame, parent=self.startFrameColumn)
                    currentStartFrame = cmds.getAttr(self.moduleGrp+".startFrame")
                    if currentStartFrame:
                        cmds.intField(self.startFrameIF, edit=True, value=currentStartFrame, parent=self.startFrameColumn)
                
                # create steering layout:
                if self.steeringExists:
                    if self.startFrameExists:
                        self.wheelLayout = self.startFrameColumn
                    else:
                        self.wheelLayout = cmds.rowLayout('wheelLayout', numberOfColumns=4, columnWidth4=(100, 60, 70, 40), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedModuleColumn" )
                    steeringValue = cmds.getAttr(self.moduleGrp+".steering")
                    self.steeringCB = cmds.checkBox(label=self.dpUIinst.lang['m158_steering'], value=steeringValue, changeCommand=self.changeSteering, parent=self.wheelLayout)
                    showControlsValue = cmds.getAttr(self.moduleGrp+".showControls")
                    self.showControlsCB = cmds.checkBox(label=self.dpUIinst.lang['i170_showControls'], value=showControlsValue, changeCommand=self.changeShowControls, parent=self.wheelLayout)
                
                # create fatherB layout:
                if self.fatherBExists:
                    self.fatherBColumn = cmds.rowLayout('fatherBColumn', numberOfColumns=3, columnWidth3=(100, 100, 70), columnAlign=[(1, 'right'), (3, 'right')], adjustableColumn=3, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2)], parent="selectedModuleColumn" )
                    cmds.button(label=self.dpUIinst.lang["m160_fatherB"]+" >", command=self.loadFatherB, parent=self.fatherBColumn)
                    self.fatherBTF = cmds.textField('fatherBTF', text='', enable=True, changeCommand=self.changeFatherB, parent=self.fatherBColumn)
                    currentFatherB = cmds.getAttr(self.moduleGrp+".fatherB")
                    if currentFatherB:
                        cmds.textField(self.fatherBTF, edit=True, text=currentFatherB, parent=self.fatherBColumn)
                
                # create degree layout:
                if self.degreeExists:
                    self.degreeColumn = cmds.rowLayout('degreeColumn', numberOfColumns=3, columnWidth3=(100, 100, 70), columnAlign=[(1, 'right'), (3, 'right')], adjustableColumn=3, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2)], parent="selectedModuleColumn" )
                    cmds.text(self.dpUIinst.lang['i119_curveDegree'], parent=self.degreeColumn)
                    self.degreeMenu = cmds.optionMenu("degreeMenu", label='', changeCommand=self.changeDegree, parent=self.degreeColumn)
                    self.degreeMenuItemList = ['0 - Preset', '1 - Linear', '3 - Cubic']
                    for item in self.degreeMenuItemList:
                        cmds.menuItem(label=item, parent=self.degreeMenu)
                    currentDegree = cmds.getAttr(self.moduleGrp+".degree")
                    # set layout with the current value:
                    if currentDegree == 0:
                        cmds.optionMenu(self.degreeMenu, edit=True, value='0 - Preset')
                    elif currentDegree == 1:
                        cmds.optionMenu(self.degreeMenu, edit=True, value='1 - Linear')
                    else:
                        cmds.optionMenu(self.degreeMenu, edit=True, value='3 - Cubic')
                        
                # create articulation joint layout:
                if self.articulationExists:
                    self.articLayout = cmds.rowLayout('articLayout', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedModuleColumn" )
                    cmds.text(self.dpUIinst.lang['m173_articulation'], parent=self.articLayout)
                    articValue = cmds.getAttr(self.moduleGrp+".articulation")
                    self.articCB = cmds.checkBox(label="", value=articValue, changeCommand=self.changeArticulation, parent=self.articLayout)
                
                # create nostril:
                if self.nostrilExists:
                    cmds.text(" ", parent=self.articLayout)
                    nostrilValue = cmds.getAttr(self.moduleGrp+".nostril")
                    self.nostrilCB = cmds.checkBox(label=self.dpUIinst.lang['m079_nostril'], value=nostrilValue, changeCommand=self.changeNostril, parent=self.articLayout)

                # create corrective layout:
                if self.correctiveExists:
                    self.correctiveLayout = cmds.rowLayout('correctiveLayout', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedModuleColumn" )
                    self.correctiveTxt = cmds.text(self.dpUIinst.lang['c124_corrective'].capitalize(), parent=self.correctiveLayout)
                    correctiveValue = cmds.getAttr(self.moduleGrp+".corrective")
                    self.correctiveCB = cmds.checkBox(label="", value=correctiveValue, changeCommand=self.changeCorrective, parent=self.correctiveLayout)
                    if self.articulationExists:
                        articulationValue = cmds.getAttr(self.moduleGrp+".articulation")
                        cmds.text(self.correctiveTxt, edit=True, enable=articulationValue)
                        cmds.checkBox(self.correctiveCB, edit=True, enable=articulationValue)

                # create dynamic layout:
                if self.dynamicExists:
                    self.dynamicLayout = cmds.rowLayout('dynamicLayout', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedModuleColumn" )
                    cmds.text(self.dpUIinst.lang['m097_dynamic'], parent=self.dynamicLayout)
                    dynamicValue = cmds.getAttr(self.moduleGrp+".dynamic")
                    self.dynamicCB = cmds.checkBox(label="", value=dynamicValue, changeCommand=self.changeDynamic, parent=self.dynamicLayout)

                # create main controllers layout:
                if self.nJointsAttrExists:
                    if self.nMainCtrlAttrExists:
                        if self.nJointsAttr > 0:
                            self.mainCtrlColumn = cmds.rowLayout('mainCtrlColumn', numberOfColumns=2, columnWidth2=(100, 100), columnAlign=[(1, 'right'), (2, 'left')], adjustableColumn=2, columnAttach=[(1, 'right', 2), (2, 'left', 2)], parent="selectedModuleColumn" )
                            hasMain = cmds.getAttr(self.moduleGrp+".mainControls")
                            nMainCtrlAttr = cmds.getAttr(self.moduleGrp+".nMain")
                            if self.nJointsAttr > 1:
                                self.mainCtrlsCB = cmds.checkBox(label=self.dpUIinst.lang['m227_mainCtrls'], value=hasMain, enable=True, changeCommand=self.setAddMainCtrls, parent=self.mainCtrlColumn)
                                self.nMainCtrlIF = cmds.intField(value=nMainCtrlAttr, minValue=1, changeCommand=partial(self.changeMainCtrlsNumber, 0), editable=hasMain, parent=self.mainCtrlColumn)
                            else:
                                self.mainCtrlsCB = cmds.checkBox(label=self.dpUIinst.lang['m227_mainCtrls'], value=False, enable=True, changeCommand=self.setAddMainCtrls, parent=self.mainCtrlColumn)
                                self.nMainCtrlIF = cmds.intField(value=nMainCtrlAttr, minValue=1, changeCommand=partial(self.changeMainCtrlsNumber, 0), editable=False, parent=self.mainCtrlColumn)
                                cmds.setAttr(self.moduleGrp+".mainControls", 0)

                if self.deformerExists:
                    self.deformerLayout = cmds.rowLayout('deformerLayout', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedModuleColumn" )
                    cmds.text(self.dpUIinst.lang['c097_deformer'].capitalize(), parent=self.deformerLayout)
                    self.deformerCB = cmds.checkBox('deformerCB', label="", value=cmds.getAttr(self.moduleGrp+".deformer"), changeCommand=self.changeDeformer, parent=self.deformerLayout)
                
                # create head facial controllers layout:
                if self.facialExists:
                    self.facialLayout = cmds.rowLayout('facialLayout', numberOfColumns=4, columnWidth4=(100, 50, 80, 70), columnAlign=[(1, 'right'), (4, 'right')], adjustableColumn=4, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2), (4, 'both', 10)], parent="selectedModuleColumn" )
                    cmds.text(self.dpUIinst.lang['c059_facial'].capitalize(), parent=self.facialLayout)
                    facialValue = cmds.getAttr(self.moduleGrp+".facial")
                    self.facialCB = cmds.checkBox('facialCB', label="", value=facialValue, changeCommand=self.changeFacial, parent=self.facialLayout)
                    collapsed = False
                    if not facialValue:
                        collapsed = True
                    # facial frame layout
                    self.facialCtrlFrameLayout = cmds.frameLayout('facialCtrlFrameLayout', label=self.dpUIinst.lang['m139_facialCtrlsAttr'], collapsable=True, collapse=collapsed, enable=facialValue, parent="selectedModuleColumn")
                    facialCBLayout = cmds.rowColumnLayout('facialCBLayout', numberOfColumns=2, columnWidth=[(1, 70), (2, 300)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 20)], parent=self.facialCtrlFrameLayout)
                    # facial element checkboxes
                    self.facialBrowCB = cmds.checkBox('facialBrowCB', label=self.dpUIinst.lang["c060_brow"], value=cmds.getAttr(self.moduleGrp+".facialBrow"), changeCommand=partial(self.changeFacialElement, "facialBrowCB", "facialBrow"), parent=facialCBLayout)
                    cmds.text(label=', '.join(self.browTgtList), parent=facialCBLayout)
                    self.facialEyelidCB = cmds.checkBox('facialEyelidCB', label=self.dpUIinst.lang["c042_eyelid"], value=cmds.getAttr(self.moduleGrp+".facialEyelid"), changeCommand=partial(self.changeFacialElement, "facialEyelidCB", "facialEyelid"), parent=facialCBLayout)
                    cmds.text(label=', '.join(self.eyelidTgtList[2:]), parent=facialCBLayout)
                    self.facialMouthCB = cmds.checkBox('facialMouthCB', label=self.dpUIinst.lang["c061_mouth"], value=cmds.getAttr(self.moduleGrp+".facialMouth"), changeCommand=partial(self.changeFacialElement, "facialMouthCB", "facialMouth"), parent=facialCBLayout)
                    cmds.text(label=', '.join(self.mouthTgtList), parent=facialCBLayout)
                    self.facialLipsCB = cmds.checkBox('facialLipsCB', label=self.dpUIinst.lang["c062_lips"], value=cmds.getAttr(self.moduleGrp+".facialLips"), changeCommand=partial(self.changeFacialElement, "facialLipsCB", "facialLips"), parent=facialCBLayout)
                    cmds.text(label=', '.join(self.lipsTgtList), parent=facialCBLayout)
                    self.facialSneerCB = cmds.checkBox('facialSneerCB', label=self.dpUIinst.lang["c063_sneer"], value=cmds.getAttr(self.moduleGrp+".facialSneer"), changeCommand=partial(self.changeFacialElement, "facialSneerCB", "facialSneer"), parent=facialCBLayout)
                    cmds.text(label=', '.join(self.sneerTgtList[:2]+self.sneerTgtList[4:]), parent=facialCBLayout)
                    self.facialGrimaceCB = cmds.checkBox('facialGrimaceCB', label=self.dpUIinst.lang["c064_grimace"], value=cmds.getAttr(self.moduleGrp+".facialGrimace"), changeCommand=partial(self.changeFacialElement, "facialGrimaceCB", "facialGrimace"), parent=facialCBLayout)
                    cmds.text(label=', '.join(self.grimaceTgtList[:2]+self.grimaceTgtList[4:]), parent=facialCBLayout)
                    self.facialFaceCB = cmds.checkBox('facialFaceCB', label=self.dpUIinst.lang["c065_face"], value=cmds.getAttr(self.moduleGrp+".facialFace"), changeCommand=partial(self.changeFacialElement, "facialFaceCB", "facialFace"), parent=facialCBLayout)
                    cmds.text(label=', '.join(self.faceTgtList), parent=facialCBLayout)
                    cmds.separator(style='none', height=5, parent=facialCBLayout)
                    self.facialTypeLayout = cmds.columnLayout('facialTypeLayout', parent=self.facialCtrlFrameLayout)
                    userType = cmds.getAttr(self.moduleGrp+".connectUserType")
                    self.facialTypeRC = cmds.radioCollection('facialTypeRC', parent=self.facialTypeLayout)
                    bs = cmds.radioButton(label=self.dpUIinst.lang['m170_blendShapes']+" - "+self.dpUIinst.lang['i185_animation']+": #_Recept_BS", annotation=self.bsType, onCommand=self.dpChangeType)
                    jnt = cmds.radioButton(label=self.dpUIinst.lang['i181_facialJoint']+" - "+self.dpUIinst.lang['i186_gaming'], annotation=self.jointsType, onCommand=self.dpChangeType)
                    cmds.radioCollection(self.facialTypeRC, edit=True, select=bs)
                    if userType:
                        cmds.radioCollection(self.facialTypeRC, edit=True, select=jnt)
                    
                if self.deformedByExists:
                    self.deformedByLayout = cmds.rowLayout('deformedByLayout', numberOfColumns=3, columnWidth3=(100, 170, 30), columnAlign=[(1, 'right'), (3, 'right')], adjustableColumn=3, columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2)], parent="selectedModuleColumn" )
                    cmds.text(self.dpUIinst.lang['i313_deformedBy'], parent=self.deformedByLayout)
                    self.deformedByMenu = cmds.optionMenu("deformedByMenu", label='', changeCommand=self.changeDeformedBy, parent=self.deformedByLayout)
                    self.deformedByMenuItemList = ['0 - None', '1 - Head Deformer', '2 - Jaw Deformer', '3 - Head and Jaw Deformers']
                    for item in self.deformedByMenuItemList:
                        cmds.menuItem(label=item, parent=self.deformedByMenu)
                    currentDeformedByValue = cmds.getAttr(self.moduleGrp+".deformedBy")
                    # set layout with the current value:
                    if currentDeformedByValue == 1:
                        cmds.optionMenu(self.deformedByMenu, edit=True, value='1 - Head Deformer')
                    elif currentDeformedByValue == 2:
                        cmds.optionMenu(self.deformedByMenu, edit=True, value='2 - Jaw Deformer')
                    elif currentDeformedByValue == 3:
                        cmds.optionMenu(self.deformedByMenu, edit=True, value='3 - Head and Jaw Deformers')
                    else:
                        cmds.optionMenu(self.deformedByMenu, edit=True, value='0 - None')
                if cmds.window(self.dpUIinst.plusInfoWinName, query=True, exists=True):
                    self.plusInfoWin()
            except:
                pass
    
    
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
            Return "stopIt" if there's a father guide mirror.
        """
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            mirroredGuideFather = self.utils.mirroredGuideFather(self.moduleGrp)
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
                # update flip attribute info from fatherGuide:
                self.fatherFlipExists = cmds.objExists(mirroredGuideFather+".flip")
                if self.fatherFlipExists:
                    fatherFlip = cmds.getAttr(mirroredGuideFather+".flip")
                    if cmds.objExists(self.moduleGrp+".flip"):
                        cmds.setAttr(self.moduleGrp+".flip", fatherFlip)
                # returns a string 'stopIt' if there is mirrored father guide:
                return "stopIt"
    
    
    def changeFlip(self, flipValue, *args):
        """ Set the attribute value for flip.
        """
        #flipValue = cmds.checkBox(self.flipCB, query=True, value=True)
        cmds.setAttr(self.moduleGrp+".flip", flipValue)
    
    
    def changeShapeSize(self, *args):
        """ Set the attribute value for shapeSize.
        """
        cmds.setAttr(self.moduleGrp+".shapeSize", cmds.floatSliderGrp(self.shapeSizeFSG, query=True, value=True))
    
    
    def changeRadiusSize(self, *args):
        """ Set the attribute value for the viewport radius size.
        """
        cmds.setAttr(self.radiusCtrl+".translateX", cmds.floatSliderGrp(self.radiusSizeFSG, query=True, value=True))
        

    def changeMirror(self, item, *args):
        """ This function receives the mirror menu item and set it as a string in the guide base (moduleGrp).
            Also, call the builder of the preview mirror (for the viewport).
        """
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            # check if the father guide is in X=0 in order to permit mirror:
            stopMirrorOperation = self.checkFatherMirror()
            if not stopMirrorOperation:
                # loading Maya matrix node (for mirror porpuses)
                loadedMatrixPlugin = self.utils.checkLoadedPlugin("matrixNodes", self.dpUIinst.lang['e002_matrixPluginNotFound'])
                if loadedMatrixPlugin:
                    self.mirrorAxis = item
                    cmds.setAttr(self.moduleGrp+".mirrorAxis", self.mirrorAxis, type='string')
                    self.createPreviewMirror()
    
    
    def changeMirrorName(self, item, *args):
        """ This function receives the mirror menu name item and set it as a string in the guide base (moduleGrp).
        """
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            cmds.setAttr(self.moduleGrp+".mirrorName", item, type='string')
    
    
    def changeArticulation(self, articulationValue, *args):
        """ Set the attribute value for articulation.
        """
        #articulationValue = cmds.checkBox(self.articCB, query=True, value=True)
        cmds.setAttr(self.moduleGrp+".articulation", articulationValue)
        try:
            cmds.text(self.correctiveTxt, edit=True, enable=articulationValue)
            cmds.checkBox(self.correctiveCB, edit=True, enable=articulationValue)
            if not articulationValue:
                cmds.checkBox(self.correctiveCB, edit=True, value=articulationValue)
                cmds.setAttr(self.moduleGrp+".corrective", articulationValue)
        except:
            pass


    def changeCorrective(self, correctiveValue, *args):
        """ Set the attribute value for corrective.
        """
        #correctiveValue = cmds.checkBox(self.correctiveCB, query=True, value=True)
        cmds.setAttr(self.moduleGrp+".corrective", correctiveValue)
    
    
    def changeDegree(self, item, *args):
        """ This function receives the degree menu name item string and set it as a int in the guide base (moduleGrp).
        """
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            if item == '3 - Cubic':
                cmds.setAttr(self.moduleGrp+".degree", 3)
            else:
                cmds.setAttr(self.moduleGrp+".degree", 1)
    

    def changeDynamic(self, dynamicValue, *args):
        """ Set the attribute value for dynamic.
        """
        #dynamicValue = cmds.checkBox(self.dynamicCB, query=True, value=True)
        cmds.setAttr(self.moduleGrp+".dynamic", dynamicValue)

    
    def createPreviewMirror(self, *args):
        # re-declaring guideMirror and previewMirror groups:
        self.previewMirrorGrpName = self.moduleGrp[:self.moduleGrp.find(":")]+'_MirrorGrp'
        if cmds.objExists(self.previewMirrorGrpName):
            cmds.delete(self.previewMirrorGrpName)
        
        # verify if there is not any guide module in the guideMirrorGrp and then delete it:
        self.guideMirrorGrp = self.dpUIinst.guideMirrorGrp
        self.utils.clearNodeGrp(self.guideMirrorGrp, 'guideBaseMirror', unparent=False)
        
        # get children, verifying if there are children guides:
        guideChildrenList = self.utils.getGuideChildrenList(self.moduleGrp)
        
        self.mirrorAxis = cmds.getAttr(self.moduleGrp+".mirrorAxis")
        if self.mirrorAxis != 'off':
            if not cmds.objExists(self.guideMirrorGrp):
                self.guideMirrorGrp = cmds.group(name=self.guideMirrorGrp, empty=True)
                cmds.addAttr(self.guideMirrorGrp, longName="selectionChanges", defaultValue=0, attributeType="byte")
                cmds.setAttr(self.guideMirrorGrp+".template", 1)
                cmds.setAttr(self.guideMirrorGrp+".hiddenInOutliner", 1)
                for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']:
                    cmds.setAttr(self.guideMirrorGrp+"."+attr, lock=True, keyable=False)
                        
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
                                        # make this previewMirrorGuide as not skinable from dpAR_UI:
                                        self.utils.addCustomAttr([dupRenamed], self.dpUIinst.skin.ignoreSkinningAttr)
                                        childrenShapeList = cmds.listRelatives(dupRenamed, shapes=True, children=True)
                                        if childrenShapeList:
                                            cmds.delete(childrenShapeList)
                                            newSphere = cmds.sphere(name=dupRenamed+"Sphere", radius=0.1, constructionHistory=True)
                                            newSphereShape = cmds.listRelatives(newSphere, shapes=True, children=True)[0]
                                            cmds.parent(newSphereShape, dupRenamed, shape=True, relative=True)
                                            cmds.delete(newSphere[0]) #transform
                                            szMD = cmds.createNode("multiplyDivide", name=dupRenamed+"_MD")
                                            szClp = cmds.createNode("clamp", name=dupRenamed+"_Clp")
                                            cmds.connectAttr(self.moduleGrp+".shapeSize", szMD+".input1X", force=True)
                                            cmds.connectAttr(szMD+".outputX", szClp+".inputR", force=True)
                                            cmds.connectAttr(szClp+".outputR", newSphere[1]+".radius", force=True)
                                            cmds.setAttr(szMD+".input2X", 0.1)
                                            cmds.setAttr(szClp+".minR", 0.001)
                                            cmds.setAttr(szClp+".maxR", 1000)
                                            cmds.rename(newSphere[1], dupRenamed+"_MNS")
                                elif cmds.objectType(dup) != 'nurbsCurve':
                                    cmds.delete(dup)
                
                # renaming the previewMirrorGuide:
                self.previewMirrorGuide = cmds.rename(duplicated, self.moduleGrp.replace(":", "_")+'_Mirror')
                cmds.deleteAttr(self.previewMirrorGuide+".guideBase")
                cmds.delete(cmds.listRelatives(self.previewMirrorGuide, shapes=True, type="nurbsCurve"))
                
                # clean up old module attributes in order to avoid numbering issue:
                if cmds.objExists(self.previewMirrorGuide+".customName"):
                    customNameMirror = "_Mirror"
                    currentCustomName = cmds.getAttr(self.previewMirrorGuide+".customName")
                    if currentCustomName:
                        customNameMirror = currentCustomName+"_Mirror"
                    cmds.setAttr(self.previewMirrorGuide+".customName", customNameMirror, type="string")
                
                # create a decomposeMatrix node in order to get the worldSpace transformations (like using xform):
                decomposeMatrix = cmds.createNode('decomposeMatrix', name=self.previewMirrorGuide+"_dm")
                cmds.connectAttr(self.moduleGrp+'.worldMatrix', decomposeMatrix+'.inputMatrix', force=True)
                
                # connect original guide base decomposeMatrix node output transformations to the mirror guide base node:
                axisList = ["X", "Y", "Z"]
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
        
        cmds.select(self.moduleGrp)


    def changeDeformedBy(self, item, *args):
        """ This function receives the deformedBy menu name item and set it as a integer value in the guide base (moduleGrp).
        """
        # verify integrity of the guideModule:
        if self.verifyGuideModuleIntegrity():
            cmds.setAttr(self.moduleGrp+".deformedBy", int(item[0]))


    def plusInfoWin(self, instance=None, *args):
        """ Open plus info attributes to each module
        """
        # declaring variables:
        plus_winWidth  = 250
        plus_winHeight = 180
        widthSize = (0.8*plus_winWidth)
        # creating Plus Info Window:
        self.dpUIinst.utils.closeUI(self.dpUIinst.colorOverrideWinName)
        if cmds.window(self.dpUIinst.plusInfoWinName, query=True, exists=True):
            cmds.deleteUI('plusFL')
            self.dpPlusInfo = self.dpUIinst.plusInfoWinName
        else:
            self.dpPlusInfo = cmds.window(self.dpUIinst.plusInfoWinName, title='dpAutoRig - '+self.dpUIinst.lang['i205_guide']+" "+self.dpUIinst.lang['i013_info'], iconName='dpPlus', widthHeight=(plus_winWidth, plus_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
        plusFL = cmds.formLayout('plusFL', numberOfDivisions=100, parent=self.dpPlusInfo)
        plusSL = cmds.scrollLayout('plusSL', parent=plusFL)
        cmds.formLayout(plusFL, edit=True, attachForm=((plusSL, 'bottom', 10), (plusSL, 'top', 10), (plusSL, 'left', 10), (plusSL, 'right', 10)))
        # get selected module guides
        guideInstanceList = self.dpUIinst.selectedModuleInstanceList.copy()
        if not guideInstanceList:
            guideInstanceList = [self]
        if instance:
            if not instance in guideInstanceList:
                guideInstanceList.insert(0, instance)
        for guideInstance in guideInstanceList:
            guideName = guideInstance.guideNamespace.split("__")[-1]
            customName = cmds.getAttr(guideInstance.moduleGrp+".customName")
            if not customName:
                customName = ""
            # creating text layout:
            cmds.separator(style='none', height=10, parent=plusSL)
            headerRCL = cmds.rowColumnLayout(numberOfColumns=2, adjustableColumn=2, columnWidth=[(1, 55), (2, 150)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 0), (2, 'left', 10)], parent=plusSL)
            cmds.text(label=guideName, align='left', parent=headerRCL)
            cmds.text(label=customName, align='left', font='boldLabelFont', parent=headerRCL)
            cmds.separator(style='none', height=10, parent=plusSL)
            guideInstance.annotationCheckBox = cmds.checkBox(label=guideInstance.dpUIinst.lang['m014_annotation'], annotation=guideInstance.dpUIinst.lang['m014_annotation'], value=cmds.getAttr(guideInstance.moduleGrp+'.displayAnnotation'), onCommand=partial(guideInstance.displayAnnotation, 1), offCommand=partial(guideInstance.displayAnnotation, 0), parent=plusSL)
            cmds.separator(style='none', height=5, parent=plusSL)
            guideInstance.radiusSizeFSG = cmds.floatSliderGrp(label=guideInstance.dpUIinst.lang['c067_radius'].capitalize(), field=True, width=widthSize, minValue=0.001, maxValue=10.0, fieldMinValue=0.001, fieldMaxValue=100.0, precision=2, value=cmds.getAttr(guideInstance.radiusCtrl+".translateX"), changeCommand=guideInstance.changeRadiusSize, dragCommand=guideInstance.changeRadiusSize, columnWidth=[(1, 55), (2, 60), (3, 30)], parent=plusSL)
            cmds.separator(style='none', height=5, parent=plusSL)
            guideInstance.shapeSizeFSG = cmds.floatSliderGrp(label=guideInstance.dpUIinst.lang['m067_shape']+" "+guideInstance.dpUIinst.lang['i115_size'], width=widthSize, field=True, minValue=0.001, maxValue=10.0, fieldMinValue=0.001, fieldMaxValue=100.0, precision=2, value=cmds.getAttr(guideInstance.moduleGrp+'.shapeSize'), changeCommand=guideInstance.changeShapeSize, dragCommand=guideInstance.changeShapeSize, columnWidth=[(1, 55), (2, 60), (3, 30)], parent=plusSL)
            cmds.separator(style='none', height=10, parent=plusSL)
            currentRGBGuideColor = guideInstance.dpUIinst.ctrls.getGuideRGBColorList(guideInstance)
            guideInstance.colorButton = cmds.button(label=guideInstance.dpUIinst.lang['m013_color'], annotation=guideInstance.dpUIinst.lang['m013_color'], width=widthSize, align="center", command=partial(guideInstance.ctrls.colorizeUI, guideInstance), backgroundColor=currentRGBGuideColor, parent=plusSL)
            cmds.separator(style='none', height=5, parent=plusSL)
            cmds.separator(style='in', height=10, width=widthSize, parent=plusSL)
        # call Info Window:
        cmds.showWindow(self.dpPlusInfo)
