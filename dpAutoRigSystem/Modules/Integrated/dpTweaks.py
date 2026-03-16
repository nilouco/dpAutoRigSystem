# importing libraries:
from maya import cmds
from maya import mel
from ..Base import dpBaseLibrary
from importlib import reload

# global variables to this module:    
CLASS_NAME = "Tweaks"
TITLE = "m081_tweaks"
DESCRIPTION = "m082_tweaksDesc"
ICON = "/Icons/dp_tweaks.png"
WIKI = "03-‐-Guides#-tweaks"

DP_TWEAKS_VERSION = 2.03


class Tweaks(dpBaseLibrary.BaseLibrary):
    def __init__(self,  *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        kwargs["WIKI"] = WIKI
        dpBaseLibrary.BaseLibrary.__init__(self, *args, **kwargs)
        if self.ar.dev:
            reload(dpBaseLibrary)


    def build_template(self, *args):
        """ This function will create all guides needed to compose a good facial tweaks controls with integrated Single modules using indirect skinning.
        """
        # check modules integrity:
        guideDir = 'Modules.Standard'
        standardDir = 'Modules/Standard'
        checkModuleList = ['dpSingle']
        checkResultList = self.ar.startGuideModules(standardDir, "check", checkModuleList=checkModuleList)
        
        if len(checkResultList) == 0:
            self.ar.collapseEditSelModFL = True
            # defining naming:
            doingName = self.ar.data.lang['m094_doing']
            # part names:
            mainName = self.ar.data.lang['c058_main']
            tweaksName = self.ar.data.lang['m081_tweaks']
            middleName = self.ar.data.lang['c029_middle']
            eyebrowName = self.ar.data.lang['c041_eyebrow']
            eyelidName = self.ar.data.lang['c042_eyelid']
            eyeSocketName = self.ar.data.lang['c127_eyeSocket']
            cornerName = self.ar.data.lang['c043_corner']
            upperName = self.ar.data.lang['c044_upper']
            lowerName = self.ar.data.lang['c045_lower']
            lipName = self.ar.data.lang['c039_lip']
            holderName = self.ar.data.lang['c046_holder']
            squintName = self.ar.data.lang['c054_squint']
            cheekName = self.ar.data.lang['c055_cheek']
            tweaksGuideName = self.ar.data.lang['m081_tweaks']+" "+self.ar.data.lang['i205_guide']
            
            holderMainName = tweaksName+"_"+holderName+"_"+mainName
            # eyebrows names:
            eyebrowMiddleName = tweaksName+"_"+middleName+"_"+eyebrowName
            eyebrowMainName = tweaksName+"_"+eyebrowName+"_"+mainName
            eyebrowName1 = tweaksName+"_"+eyebrowName+"_01"
            eyebrowName2 = tweaksName+"_"+eyebrowName+"_02"
            eyebrowName3 = tweaksName+"_"+eyebrowName+"_03"
            eyebrowName4 = tweaksName+"_"+eyebrowName+"_04"
            # eyelids names:
            eyelidMainName = tweaksName+"_"+eyelidName+"_"+mainName
            upperEyelidName0 = tweaksName+"_"+upperName+"_"+eyelidName+"_00"
            upperEyelidName1 = tweaksName+"_"+upperName+"_"+eyelidName+"_01"
            upperEyelidName2 = tweaksName+"_"+upperName+"_"+eyelidName+"_02"
            lowerEyelidName0 = tweaksName+"_"+lowerName+"_"+eyelidName+"_00"
            lowerEyelidName1 = tweaksName+"_"+lowerName+"_"+eyelidName+"_01"
            lowerEyelidName2 = tweaksName+"_"+lowerName+"_"+eyelidName+"_02"
            eyelidCornerName0 = tweaksName+"_"+cornerName+"_"+eyelidName+"_00"
            eyelidCornerName1 = tweaksName+"_"+cornerName+"_"+eyelidName+"_01"
            # eyeSockets names:
            upperEyeSocketName0 = tweaksName+"_"+upperName+"_"+eyeSocketName+"_00"
            upperEyeSocketName1 = tweaksName+"_"+upperName+"_"+eyeSocketName+"_01"
            upperEyeSocketName2 = tweaksName+"_"+upperName+"_"+eyeSocketName+"_02"
            lowerEyeSocketName0 = tweaksName+"_"+lowerName+"_"+eyeSocketName+"_00"
            lowerEyeSocketName1 = tweaksName+"_"+lowerName+"_"+eyeSocketName+"_01"
            lowerEyeSocketName2 = tweaksName+"_"+lowerName+"_"+eyeSocketName+"_02"
            # squints names:
            squintMainName = tweaksName+"_"+squintName+"_"+mainName
            squintName1 = tweaksName+"_"+squintName+"_01"
            squintName2 = tweaksName+"_"+squintName+"_02"
            squintName3 = tweaksName+"_"+squintName+"_03"
            # cheeks names:
            cheekName1 = tweaksName+"_"+cheekName+"_01"
            cheekName2 = tweaksName+"_"+cheekName+"_02"
            # lip names:
            lipMainName = tweaksName+"_"+lipName+"_"+mainName
            upperLipMiddleName = tweaksName+"_"+upperName+"_"+lipName+"_00"
            upperLipName1 = tweaksName+"_"+upperName+"_"+lipName+"_01"
            upperLipName2 = tweaksName+"_"+upperName+"_"+lipName+"_02"
            lowerLipMiddleName = tweaksName+"_"+lowerName+"_"+lipName+"_00"
            lowerLipName1 = tweaksName+"_"+lowerName+"_"+lipName+"_01"
            lowerLipName2 = tweaksName+"_"+lowerName+"_"+lipName+"_02"
            lipCornerName = tweaksName+"_"+cornerName+"_"+lipName
            
            # kind guides:
            simple   = self.ar.data.lang['i175_simple']
            complete = self.ar.data.lang['i176_complete']
            cancel   = self.ar.data.lang['i132_cancel']
            userMessage = self.ar.data.lang['i177_chooseMessage']
            
            # use indirect skinning or joints:
            indSkin     = self.ar.data.lang['i180_indirectSkin']+"\n"+self.ar.data.lang['i185_animation']
            faceJoint   = self.ar.data.lang['i181_facialJoint']+"\n"+self.ar.data.lang['i186_gaming']
            faceMessage = self.ar.data.lang['i182_facialMessage']
            
            # getting Simple or Complete module guides to create:
            userDetail = self.ask_build_detail(simple, complete, cancel, complete, userMessage)
            if not userDetail == cancel:
                # number of modules to create:
                if userDetail == simple:
                    maxProcess = 3
                else:
                    maxProcess = 6
                
                # getting Indirect Skinning user prefer:
                userIndirectSkin = self.ask_build_detail(indSkin, faceJoint, cancel, indSkin, faceMessage)
                if not userIndirectSkin == cancel:
                    if userIndirectSkin == indSkin:
                        indSkinValue = 1
                    else:
                        indSkinValue = 0
                
                    # Starting progress window
                    self.ar.utils.setProgress(doingName, tweaksGuideName, maxProcess, addOne=False, addNumber=False)
                    
                    self.ar.utils.setProgress(doingName+eyebrowMainName)
                    # creating Single instances:
                    holderMainInstance = self.ar.initGuide('dpSingle', guideDir)
                    holderMainInstance.editGuideModuleName(holderMainName)
                    
                    eyebrowMainInstance = self.ar.initGuide('dpSingle', guideDir)
                    eyebrowMainInstance.editGuideModuleName(eyebrowMainName)
                    eyebrowMainInstance.changeMirror("X")
                    cmds.setAttr(eyebrowMainInstance.moduleGrp+".deformedBy", 1)
                    
                    eyebrowInstance1 = self.ar.initGuide('dpSingle', guideDir)
                    eyebrowInstance1.editGuideModuleName(eyebrowName1)
                    eyebrowInstance1.changeMirror("X")
                    
                    eyebrowInstance2 = self.ar.initGuide('dpSingle', guideDir)
                    eyebrowInstance2.editGuideModuleName(eyebrowName2)
                    eyebrowInstance2.changeMirror("X")
                    
                    eyebrowInstance3 = self.ar.initGuide('dpSingle', guideDir)
                    eyebrowInstance3.editGuideModuleName(eyebrowName3)
                    eyebrowInstance3.changeMirror("X")
                    cmds.refresh()
                    
                    self.ar.utils.setProgress(doingName+lipMainName)

                    lipMainInstance = self.ar.initGuide('dpSingle', guideDir)
                    lipMainInstance.editGuideModuleName(lipMainName)
                    cmds.setAttr(lipMainInstance.moduleGrp+".deformedBy", 3)
                    
                    upperLipMiddleInstance = self.ar.initGuide('dpSingle', guideDir)
                    upperLipMiddleInstance.editGuideModuleName(upperLipMiddleName)
                    
                    upperLipInstance1 = self.ar.initGuide('dpSingle', guideDir)
                    upperLipInstance1.editGuideModuleName(checkText=upperLipName1)
                    upperLipInstance1.changeMirror("X")
                    
                    upperLipInstance2 = self.ar.initGuide('dpSingle', guideDir)
                    upperLipInstance2.editGuideModuleName(upperLipName2)
                    upperLipInstance2.changeMirror("X")
                    
                    lowerLipMiddleInstance = self.ar.initGuide('dpSingle', guideDir)
                    lowerLipMiddleInstance.editGuideModuleName(lowerLipMiddleName)
                    
                    lowerLipInstance1 = self.ar.initGuide('dpSingle', guideDir)
                    lowerLipInstance1.editGuideModuleName(lowerLipName1)
                    lowerLipInstance1.changeMirror("X")
                    
                    lowerLipInstance2 = self.ar.initGuide('dpSingle', guideDir)
                    lowerLipInstance2.editGuideModuleName(lowerLipName2)
                    lowerLipInstance2.changeMirror("X")
                    
                    lipCornerInstance = self.ar.initGuide('dpSingle', guideDir)
                    lipCornerInstance.editGuideModuleName(lipCornerName)
                    lipCornerInstance.changeMirror("X")
                    cmds.refresh()
                    
                    #
                    # complete part:
                    #
                    if userDetail == complete:
                        
                        self.ar.utils.setProgress(doingName+eyelidMainName)

                        eyebrowMiddleInstance = self.ar.initGuide('dpSingle', guideDir)
                        eyebrowMiddleInstance.editGuideModuleName(eyebrowMiddleName)

                        eyebrowInstance4 = self.ar.initGuide('dpSingle', guideDir)
                        eyebrowInstance4.editGuideModuleName(eyebrowName4)
                        eyebrowInstance4.changeMirror("X")

                        if userIndirectSkin == indSkin:
                            eyelidMainInstance = self.ar.initGuide('dpSingle', guideDir)
                            eyelidMainInstance.editGuideModuleName(eyelidMainName)
                            eyelidMainInstance.changeMirror("X")
                            cmds.setAttr(eyelidMainInstance.moduleGrp+".deformedBy", 1)
                            
                            upperEyelidInstance0 = self.ar.initGuide('dpSingle', guideDir)
                            upperEyelidInstance0.editGuideModuleName(upperEyelidName0)
                            upperEyelidInstance0.changeMirror("X")
                            
                            upperEyelidInstance1 = self.ar.initGuide('dpSingle', guideDir)
                            upperEyelidInstance1.editGuideModuleName(upperEyelidName1)
                            upperEyelidInstance1.changeMirror("X")
                            
                            upperEyelidInstance2 = self.ar.initGuide('dpSingle', guideDir)
                            upperEyelidInstance2.editGuideModuleName(upperEyelidName2)
                            upperEyelidInstance2.changeMirror("X")
                            
                            lowerEyelidInstance0 = self.ar.initGuide('dpSingle', guideDir)
                            lowerEyelidInstance0.editGuideModuleName(lowerEyelidName0)
                            lowerEyelidInstance0.changeMirror("X")
                            
                            lowerEyelidInstance1 = self.ar.initGuide('dpSingle', guideDir)
                            lowerEyelidInstance1.editGuideModuleName(lowerEyelidName1)
                            lowerEyelidInstance1.changeMirror("X")
                            
                            lowerEyelidInstance2 = self.ar.initGuide('dpSingle', guideDir)
                            lowerEyelidInstance2.editGuideModuleName(lowerEyelidName2)
                            lowerEyelidInstance2.changeMirror("X")
                            
                            eyelidCornerInstance0 = self.ar.initGuide('dpSingle', guideDir)
                            eyelidCornerInstance0.editGuideModuleName(eyelidCornerName0)
                            eyelidCornerInstance0.changeMirror("X")
                            
                            eyelidCornerInstance1 = self.ar.initGuide('dpSingle', guideDir)
                            eyelidCornerInstance1.editGuideModuleName(eyelidCornerName1)
                            eyelidCornerInstance1.changeMirror("X")

                            upperEyeSocketInstance0 = self.ar.initGuide('dpSingle', guideDir)
                            upperEyeSocketInstance0.editGuideModuleName(upperEyeSocketName0)
                            upperEyeSocketInstance0.changeMirror("X")
                            
                            upperEyeSocketInstance1 = self.ar.initGuide('dpSingle', guideDir)
                            upperEyeSocketInstance1.editGuideModuleName(upperEyeSocketName1)
                            upperEyeSocketInstance1.changeMirror("X")
                            
                            upperEyeSocketInstance2 = self.ar.initGuide('dpSingle', guideDir)
                            upperEyeSocketInstance2.editGuideModuleName(upperEyeSocketName2)
                            upperEyeSocketInstance2.changeMirror("X")
                            
                            lowerEyeSocketInstance0 = self.ar.initGuide('dpSingle', guideDir)
                            lowerEyeSocketInstance0.editGuideModuleName(lowerEyeSocketName0)
                            lowerEyeSocketInstance0.changeMirror("X")
                            
                            lowerEyeSocketInstance1 = self.ar.initGuide('dpSingle', guideDir)
                            lowerEyeSocketInstance1.editGuideModuleName(lowerEyeSocketName1)
                            lowerEyeSocketInstance1.changeMirror("X")
                            
                            lowerEyeSocketInstance2 = self.ar.initGuide('dpSingle', guideDir)
                            lowerEyeSocketInstance2.editGuideModuleName(lowerEyeSocketName2)
                            lowerEyeSocketInstance2.changeMirror("X")

                        cmds.refresh()                    
                        self.ar.utils.setProgress(doingName+eyeSocketName)



                        cmds.refresh()                    
                        self.ar.utils.setProgress(doingName+squintMainName)
                        
                        squintMainInstance = self.ar.initGuide('dpSingle', guideDir)
                        squintMainInstance.editGuideModuleName(squintMainName)
                        squintMainInstance.changeMirror("X")
                        cmds.setAttr(squintMainInstance.moduleGrp+".deformedBy", 1)
                        
                        squintInstance1 = self.ar.initGuide('dpSingle', guideDir)
                        squintInstance1.editGuideModuleName(checkText=squintName1)
                        squintInstance1.changeMirror("X")
                        
                        squintInstance2 = self.ar.initGuide('dpSingle', guideDir)
                        squintInstance2.editGuideModuleName(squintName2)
                        squintInstance2.changeMirror("X")
                        
                        squintInstance3 = self.ar.initGuide('dpSingle', guideDir)
                        squintInstance3.editGuideModuleName(squintName3)
                        squintInstance3.changeMirror("X")

                        cheekInstance1 = self.ar.initGuide('dpSingle', guideDir)
                        cheekInstance1.editGuideModuleName(cheekName1)
                        cheekInstance1.changeMirror("X")

                        cheekInstance2 = self.ar.initGuide('dpSingle', guideDir)
                        cheekInstance2.editGuideModuleName(cheekName2)
                        cheekInstance2.changeMirror("X")
                    
                    # woking with Single indirect skinning setup:
                    # declaring a instanceList in order to clear the code a little:
                    instanceList = [holderMainInstance, eyebrowMainInstance, eyebrowInstance1, eyebrowInstance2, eyebrowInstance3, lipMainInstance, upperLipMiddleInstance, upperLipInstance1, upperLipInstance2, lowerLipMiddleInstance, lowerLipInstance1, lowerLipInstance2, lipCornerInstance]
                    sideInstanceList = [eyebrowMainInstance, eyebrowInstance1, eyebrowInstance2, eyebrowInstance3, upperLipInstance1, upperLipInstance2, lowerLipInstance1, lowerLipInstance2, lipCornerInstance]
                    mainInstanceList = [eyebrowMainInstance, lipMainInstance]
                    
                    if userDetail == complete:
                        if userIndirectSkin == indSkin:
                            instanceList = [holderMainInstance, eyebrowMiddleInstance, eyebrowMainInstance, eyebrowInstance1, eyebrowInstance2, eyebrowInstance3, eyebrowInstance4, eyelidMainInstance, upperEyelidInstance0, upperEyelidInstance1, upperEyelidInstance2, lowerEyelidInstance0, lowerEyelidInstance1, lowerEyelidInstance2, upperEyeSocketInstance0, upperEyeSocketInstance1, upperEyeSocketInstance2, lowerEyeSocketInstance0, lowerEyeSocketInstance1, lowerEyeSocketInstance2, eyelidCornerInstance0, eyelidCornerInstance1, squintMainInstance, squintInstance1, squintInstance2, squintInstance3, cheekInstance1, cheekInstance2, lipMainInstance, upperLipMiddleInstance, upperLipInstance1, upperLipInstance2, lowerLipMiddleInstance, lowerLipInstance1, lowerLipInstance2, lipCornerInstance]
                            sideInstanceList = [eyebrowMainInstance, eyebrowInstance1, eyebrowInstance2, eyebrowInstance3, eyebrowInstance4, eyelidMainInstance, upperEyelidInstance0, upperEyelidInstance1, upperEyelidInstance2, lowerEyelidInstance0, lowerEyelidInstance1, lowerEyelidInstance2, upperEyeSocketInstance0, upperEyeSocketInstance1, upperEyeSocketInstance2, lowerEyeSocketInstance0, lowerEyeSocketInstance1, lowerEyeSocketInstance2, eyelidCornerInstance0, eyelidCornerInstance1, squintMainInstance, squintInstance1, squintInstance2, squintInstance3, cheekInstance1, cheekInstance2, upperLipInstance1, upperLipInstance2, lowerLipInstance1, lowerLipInstance2, lipCornerInstance]
                            mainInstanceList = [eyebrowMainInstance, eyelidMainInstance, squintMainInstance, lipMainInstance]
                        else:
                            instanceList = [holderMainInstance, eyebrowMiddleInstance, eyebrowMainInstance, eyebrowInstance1, eyebrowInstance2, eyebrowInstance3, eyebrowInstance4, squintMainInstance, squintInstance1, squintInstance2, squintInstance3, cheekInstance1, cheekInstance2, lipMainInstance, upperLipMiddleInstance, upperLipInstance1, upperLipInstance2, lowerLipMiddleInstance, lowerLipInstance1, lowerLipInstance2, lipCornerInstance]
                            sideInstanceList = [eyebrowMainInstance, eyebrowInstance1, eyebrowInstance2, eyebrowInstance3, eyebrowInstance4, squintMainInstance, squintInstance1, squintInstance2, squintInstance3, cheekInstance1, cheekInstance2, upperLipInstance1, upperLipInstance2, lowerLipInstance1, lowerLipInstance2, lipCornerInstance]
                            mainInstanceList = [eyebrowMainInstance, squintMainInstance, lipMainInstance]
                    
                    # turn on indirectSkinning:
                    for inst in instanceList:
                        cmds.setAttr(inst.moduleGrp+".indirectSkin", indSkinValue)
                        cmds.setAttr(inst.radiusCtrl+".translateX", 0.05)
                        cmds.setAttr(inst.cvEndJoint+".translateZ", 0.1)
                        cmds.setAttr(inst.moduleGrp+".displayAnnotation", 0)
                        cmds.setAttr(inst.moduleGrp+"_Ant.visibility", 0)
                        cmds.setAttr(inst.moduleGrp+".shapeSize", 0.03)

                    # turn on mirroring and flipping:
                    for sideInst in sideInstanceList:
                        cmds.setAttr(sideInst.moduleGrp+".flip", 1)
                        
                    # change main size:
                    for mainInst in mainInstanceList:
                        cmds.setAttr(mainInst.radiusCtrl+".translateX", 0.3)
                    
                    cmds.setAttr(holderMainInstance.radiusCtrl+".translateX", 2)
                    cmds.setAttr(holderMainInstance.moduleGrp+".holder", 0.7)
                    
                    self.ar.utils.setProgress(doingName+" hierarchy")
                    cmds.refresh()
                    
                    # working on hierarchy
                    cmds.parent([eyebrowMainInstance.moduleGrp, lipMainInstance.moduleGrp], holderMainInstance.moduleGrp, absolute=True)
                    cmds.parent([upperLipMiddleInstance.moduleGrp, upperLipInstance1.moduleGrp, upperLipInstance2.moduleGrp, lowerLipMiddleInstance.moduleGrp, lowerLipInstance1.moduleGrp, lowerLipInstance2.moduleGrp, lipCornerInstance.moduleGrp], lipMainInstance.moduleGrp, absolute=True)
                    
                    if userDetail == complete:
                        cmds.parent([eyebrowMiddleInstance.moduleGrp, squintMainInstance.moduleGrp, cheekInstance1.moduleGrp, cheekInstance2.moduleGrp], holderMainInstance.moduleGrp, absolute=True)
                        cmds.parent([squintInstance1.moduleGrp, squintInstance2.moduleGrp, squintInstance3.moduleGrp], squintMainInstance.moduleGrp, absolute=True)
                        cmds.parent([eyebrowInstance1.moduleGrp, eyebrowInstance2.moduleGrp, eyebrowInstance3.moduleGrp, eyebrowInstance4.moduleGrp], eyebrowMainInstance.moduleGrp, absolute=True)
                        if userIndirectSkin == indSkin:
                            cmds.parent(eyelidMainInstance.moduleGrp, holderMainInstance.moduleGrp, absolute=True)
                            cmds.parent([upperEyelidInstance0.moduleGrp, upperEyelidInstance1.moduleGrp, upperEyelidInstance2.moduleGrp, lowerEyelidInstance0.moduleGrp, lowerEyelidInstance1.moduleGrp, lowerEyelidInstance2.moduleGrp, eyelidCornerInstance0.moduleGrp, eyelidCornerInstance1.moduleGrp, upperEyeSocketInstance0.moduleGrp, upperEyeSocketInstance1.moduleGrp, upperEyeSocketInstance2.moduleGrp, lowerEyeSocketInstance0.moduleGrp, lowerEyeSocketInstance1.moduleGrp, lowerEyeSocketInstance2.moduleGrp], eyelidMainInstance.moduleGrp, absolute=True)
                    else:
                        cmds.parent([eyebrowInstance1.moduleGrp, eyebrowInstance2.moduleGrp, eyebrowInstance3.moduleGrp], eyebrowMainInstance.moduleGrp, absolute=True)
                            
                    # try to parent to HEAD guide or control
                    if cmds.objExists("*__*:Guide_Head"):
                        if cmds.objExists("*__*:Guide_UpperJaw"):
                            cmds.parent(holderMainInstance.moduleGrp, cmds.ls("*__*:Guide_Head")[0], relative=True)
                            cmds.parent(holderMainInstance.moduleGrp, cmds.ls("*__*:Guide_UpperJaw")[0], relative=False)
                        else:
                            cmds.parent(holderMainInstance.moduleGrp, cmds.ls("*__*:Guide_Head")[0], relative=True)
                    elif cmds.objExists("Head_UpperJaw_Ctrl"):
                        cmds.parent(holderMainInstance.moduleGrp, "Head_UpperJaw_Ctrl", relative=True)
                        
                    # set tweaks guides position
                    cmds.setAttr(eyebrowMainInstance.moduleGrp+".translateX", 0.65)
                    cmds.setAttr(eyebrowMainInstance.moduleGrp+".translateY", 2.8)
                    cmds.setAttr(eyebrowMainInstance.moduleGrp+".translateZ", 2)
                    
                    cmds.setAttr(eyebrowInstance1.moduleGrp+".translateX", -0.2)
                    cmds.setAttr(eyebrowInstance1.moduleGrp+".translateZ", 0.1)
                    
                    cmds.setAttr(eyebrowInstance2.moduleGrp+".translateY", 0.05)
                    cmds.setAttr(eyebrowInstance2.moduleGrp+".translateZ", 0.1)
                    
                    cmds.setAttr(eyebrowInstance3.moduleGrp+".translateX", 0.2)
                    cmds.setAttr(eyebrowInstance3.moduleGrp+".translateZ", 0.1)
                    
                    cmds.setAttr(lipMainInstance.moduleGrp+".translateY", 1)
                    cmds.setAttr(lipMainInstance.moduleGrp+".translateZ", 1)
                    
                    cmds.setAttr(upperLipMiddleInstance.moduleGrp+".translateY", 0.1)
                    cmds.setAttr(upperLipMiddleInstance.moduleGrp+".translateZ", 1.5)
                    
                    cmds.setAttr(lowerLipMiddleInstance.moduleGrp+".translateY", -0.1)
                    cmds.setAttr(lowerLipMiddleInstance.moduleGrp+".translateZ", 1.5)
                    
                    cmds.setAttr(upperLipInstance1.moduleGrp+".translateX", 0.2)
                    cmds.setAttr(upperLipInstance1.moduleGrp+".translateY", 0.07)
                    cmds.setAttr(upperLipInstance1.moduleGrp+".translateZ", 1.5)
                    
                    cmds.setAttr(upperLipInstance2.moduleGrp+".translateX", 0.4)
                    cmds.setAttr(upperLipInstance2.moduleGrp+".translateY", 0.05)
                    cmds.setAttr(upperLipInstance2.moduleGrp+".translateZ", 1.5)
                    
                    cmds.setAttr(lowerLipInstance1.moduleGrp+".translateX", 0.2)
                    cmds.setAttr(lowerLipInstance1.moduleGrp+".translateY", -0.07)
                    cmds.setAttr(lowerLipInstance1.moduleGrp+".translateZ", 1.5)
                    
                    cmds.setAttr(lowerLipInstance2.moduleGrp+".translateX", 0.4)
                    cmds.setAttr(lowerLipInstance2.moduleGrp+".translateY", -0.05)
                    cmds.setAttr(lowerLipInstance2.moduleGrp+".translateZ", 1.5)
                    
                    cmds.setAttr(lipCornerInstance.moduleGrp+".translateX", 0.55)
                    cmds.setAttr(lipCornerInstance.moduleGrp+".translateZ", 1.5)
                    
                    if userDetail == complete:
                        
                        cmds.setAttr(eyebrowMiddleInstance.moduleGrp+".translateY", 2.8)
                        cmds.setAttr(eyebrowMiddleInstance.moduleGrp+".translateZ", 2)

                        cmds.setAttr(eyebrowInstance4.moduleGrp+".translateX", 0.4)
                        cmds.setAttr(eyebrowInstance4.moduleGrp+".translateY", -0.1)
                        cmds.setAttr(eyebrowInstance4.moduleGrp+".translateZ", 0.1)
                        
                        cmds.setAttr(squintMainInstance.moduleGrp+".translateX", 0.5)
                        cmds.setAttr(squintMainInstance.moduleGrp+".translateY", 1.4)
                        cmds.setAttr(squintMainInstance.moduleGrp+".translateZ", 1.6)
                        
                        cmds.setAttr(squintInstance1.moduleGrp+".translateX", -0.18)
                        cmds.setAttr(squintInstance1.moduleGrp+".translateY", 0.07)
                        cmds.setAttr(squintInstance1.moduleGrp+".translateZ", 0.42)
                        
                        cmds.setAttr(squintInstance2.moduleGrp+".translateX", 0.07)
                        cmds.setAttr(squintInstance2.moduleGrp+".translateY", -0.04)
                        cmds.setAttr(squintInstance2.moduleGrp+".translateZ", 0.35)
                        
                        cmds.setAttr(squintInstance3.moduleGrp+".translateX", 0.36)
                        cmds.setAttr(squintInstance3.moduleGrp+".translateY", -0.01)
                        cmds.setAttr(squintInstance3.moduleGrp+".translateZ", 0.2)
                        
                        cmds.setAttr(cheekInstance1.moduleGrp+".translateX", 1.1)
                        cmds.setAttr(cheekInstance1.moduleGrp+".translateY", 0.9)
                        cmds.setAttr(cheekInstance1.moduleGrp+".translateZ", 2.1)
                        
                        cmds.setAttr(cheekInstance2.moduleGrp+".translateX", 0.8)
                        cmds.setAttr(cheekInstance2.moduleGrp+".translateY", 1.15)
                        cmds.setAttr(cheekInstance2.moduleGrp+".translateZ", 2.3)
                        
                        if userIndirectSkin == indSkin:
                            cmds.setAttr(eyelidMainInstance.moduleGrp+".translateX", 0.5)
                            cmds.setAttr(eyelidMainInstance.moduleGrp+".translateY", 2)
                            cmds.setAttr(eyelidMainInstance.moduleGrp+".translateZ", 1.3)
                            
                            cmds.setAttr(upperEyelidInstance0.moduleGrp+".translateX", -0.17)
                            cmds.setAttr(upperEyelidInstance0.moduleGrp+".translateY", 0.1)
                            cmds.setAttr(upperEyelidInstance0.moduleGrp+".translateZ", 0.5)
                            
                            cmds.setAttr(upperEyelidInstance1.moduleGrp+".translateY", 0.14)
                            cmds.setAttr(upperEyelidInstance1.moduleGrp+".translateZ", 0.5)
                            
                            cmds.setAttr(upperEyelidInstance2.moduleGrp+".translateX", 0.17)
                            cmds.setAttr(upperEyelidInstance2.moduleGrp+".translateY", 0.1)
                            cmds.setAttr(upperEyelidInstance2.moduleGrp+".translateZ", 0.5)
                            
                            cmds.setAttr(lowerEyelidInstance0.moduleGrp+".translateX", -0.17)
                            cmds.setAttr(lowerEyelidInstance0.moduleGrp+".translateY", -0.1)
                            cmds.setAttr(lowerEyelidInstance0.moduleGrp+".translateZ", 0.5)
                            
                            cmds.setAttr(lowerEyelidInstance1.moduleGrp+".translateY", -0.14)
                            cmds.setAttr(lowerEyelidInstance1.moduleGrp+".translateZ", 0.5)
                            
                            cmds.setAttr(lowerEyelidInstance2.moduleGrp+".translateX", 0.17)
                            cmds.setAttr(lowerEyelidInstance2.moduleGrp+".translateY", -0.1)
                            cmds.setAttr(lowerEyelidInstance2.moduleGrp+".translateZ", 0.5)
                            
                            cmds.setAttr(eyelidCornerInstance0.moduleGrp+".translateX", -0.3)
                            cmds.setAttr(eyelidCornerInstance0.moduleGrp+".translateZ", 0.5)
                            
                            cmds.setAttr(eyelidCornerInstance1.moduleGrp+".translateX", 0.3)
                            cmds.setAttr(eyelidCornerInstance1.moduleGrp+".translateZ", 0.5)

                            cmds.setAttr(upperEyeSocketInstance0.moduleGrp+".translateX", -0.25)
                            cmds.setAttr(upperEyeSocketInstance0.moduleGrp+".translateY", 0.25)
                            cmds.setAttr(upperEyeSocketInstance0.moduleGrp+".translateZ", 0.5)
                            
                            cmds.setAttr(upperEyeSocketInstance1.moduleGrp+".translateY", 0.3)
                            cmds.setAttr(upperEyeSocketInstance1.moduleGrp+".translateZ", 0.5)
                            
                            cmds.setAttr(upperEyeSocketInstance2.moduleGrp+".translateX", 0.25)
                            cmds.setAttr(upperEyeSocketInstance2.moduleGrp+".translateY", 0.25)
                            cmds.setAttr(upperEyeSocketInstance2.moduleGrp+".translateZ", 0.5)
                            
                            cmds.setAttr(lowerEyeSocketInstance0.moduleGrp+".translateX", -0.25)
                            cmds.setAttr(lowerEyeSocketInstance0.moduleGrp+".translateY", -0.25)
                            cmds.setAttr(lowerEyeSocketInstance0.moduleGrp+".translateZ", 0.5)
                            
                            cmds.setAttr(lowerEyeSocketInstance1.moduleGrp+".translateY", -0.3)
                            cmds.setAttr(lowerEyeSocketInstance1.moduleGrp+".translateZ", 0.5)
                            
                            cmds.setAttr(lowerEyeSocketInstance2.moduleGrp+".translateX", 0.25)
                            cmds.setAttr(lowerEyeSocketInstance2.moduleGrp+".translateY", -0.25)
                            cmds.setAttr(lowerEyeSocketInstance2.moduleGrp+".translateZ", 0.5)
                    
                    # Close progress window
                    self.ar.utils.setProgress(endIt=True)

                    self.ar.collapseEditSelModFL = False
                    cmds.select(holderMainInstance.moduleGrp)
                    print(self.ar.data.lang['m093_createdTweaks'])
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
