# importing libraries:
from maya import cmds
from maya import mel

# global variables to this module:    
CLASS_NAME = "Tweaks"
TITLE = "m081_tweaks"
DESCRIPTION = "m082_tweaksDesc"
ICON = "/Icons/dp_tweaks.png"
WIKI = "03-‐-Guides#-tweaks"

DP_TWEAKS_VERSION = 2.03


def getUserDetail(opt1, opt2, cancel, default, userMessage):
    """ Ask user the detail level we'll create the guides by a confirm dialog box window.
        Options:
            Simple
            Complete
        Returns the user choose option or None if canceled.
    """
    result = cmds.confirmDialog(title=CLASS_NAME, message=userMessage, button=[opt1, opt2, cancel], defaultButton=default, cancelButton=cancel, dismissString=cancel)
    return result


def Tweaks(dpUIinst):
    """ This function will create all guides needed to compose a good facial tweaks controls with integrated Single modules using indirect skinning.
    """
    # check modules integrity:
    guideDir = 'Modules.Standard'
    standardDir = 'Modules/Standard'
    checkModuleList = ['dpSingle']
    checkResultList = dpUIinst.startGuideModules(standardDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        dpUIinst.collapseEditSelModFL = True
        # defining naming:
        doingName = dpUIinst.lang['m094_doing']
        # part names:
        mainName = dpUIinst.lang['c058_main']
        tweaksName = dpUIinst.lang['m081_tweaks']
        middleName = dpUIinst.lang['c029_middle']
        eyebrowName = dpUIinst.lang['c041_eyebrow']
        eyelidName = dpUIinst.lang['c042_eyelid']
        eyeSocketName = dpUIinst.lang['c127_eyeSocket']
        cornerName = dpUIinst.lang['c043_corner']
        upperName = dpUIinst.lang['c044_upper']
        lowerName = dpUIinst.lang['c045_lower']
        lipName = dpUIinst.lang['c039_lip']
        holderName = dpUIinst.lang['c046_holder']
        squintName = dpUIinst.lang['c054_squint']
        cheekName = dpUIinst.lang['c055_cheek']
        tweaksGuideName = dpUIinst.lang['m081_tweaks']+" "+dpUIinst.lang['i205_guide']
        
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
        simple   = dpUIinst.lang['i175_simple']
        complete = dpUIinst.lang['i176_complete']
        cancel   = dpUIinst.lang['i132_cancel']
        userMessage = dpUIinst.lang['i177_chooseMessage']
        
        # use indirect skinning or joints:
        indSkin     = dpUIinst.lang['i180_indirectSkin']+"\n"+dpUIinst.lang['i185_animation']
        faceJoint   = dpUIinst.lang['i181_facialJoint']+"\n"+dpUIinst.lang['i186_gaming']
        faceMessage = dpUIinst.lang['i182_facialMessage']
        
        # getting Simple or Complete module guides to create:
        userDetail = getUserDetail(simple, complete, cancel, complete, userMessage)
        if not userDetail == cancel:
            # number of modules to create:
            if userDetail == simple:
                maxProcess = 3
            else:
                maxProcess = 6
            
            # getting Indirect Skinning user prefer:
            userIndirectSkin = getUserDetail(indSkin, faceJoint, cancel, indSkin, faceMessage)
            if not userIndirectSkin == cancel:
                if userIndirectSkin == indSkin:
                    indSkinValue = 1
                else:
                    indSkinValue = 0
            
                # Starting progress window
                dpUIinst.utils.setProgress(doingName, tweaksGuideName, maxProcess, addOne=False, addNumber=False)
                
                dpUIinst.utils.setProgress(doingName+eyebrowMainName)
                # creating Single instances:
                holderMainInstance = dpUIinst.initGuide('dpSingle', guideDir)
                holderMainInstance.editGuideModuleName(holderMainName)
                
                eyebrowMainInstance = dpUIinst.initGuide('dpSingle', guideDir)
                eyebrowMainInstance.editGuideModuleName(eyebrowMainName)
                eyebrowMainInstance.changeMirror("X")
                cmds.setAttr(eyebrowMainInstance.moduleGrp+".deformedBy", 1)
                
                eyebrowInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
                eyebrowInstance1.editGuideModuleName(eyebrowName1)
                eyebrowInstance1.changeMirror("X")
                
                eyebrowInstance2 = dpUIinst.initGuide('dpSingle', guideDir)
                eyebrowInstance2.editGuideModuleName(eyebrowName2)
                eyebrowInstance2.changeMirror("X")
                
                eyebrowInstance3 = dpUIinst.initGuide('dpSingle', guideDir)
                eyebrowInstance3.editGuideModuleName(eyebrowName3)
                eyebrowInstance3.changeMirror("X")
                cmds.refresh()
                
                dpUIinst.utils.setProgress(doingName+lipMainName)

                lipMainInstance = dpUIinst.initGuide('dpSingle', guideDir)
                lipMainInstance.editGuideModuleName(lipMainName)
                cmds.setAttr(lipMainInstance.moduleGrp+".deformedBy", 3)
                
                upperLipMiddleInstance = dpUIinst.initGuide('dpSingle', guideDir)
                upperLipMiddleInstance.editGuideModuleName(upperLipMiddleName)
                
                upperLipInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
                upperLipInstance1.editGuideModuleName(checkText=upperLipName1)
                upperLipInstance1.changeMirror("X")
                
                upperLipInstance2 = dpUIinst.initGuide('dpSingle', guideDir)
                upperLipInstance2.editGuideModuleName(upperLipName2)
                upperLipInstance2.changeMirror("X")
                
                lowerLipMiddleInstance = dpUIinst.initGuide('dpSingle', guideDir)
                lowerLipMiddleInstance.editGuideModuleName(lowerLipMiddleName)
                
                lowerLipInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
                lowerLipInstance1.editGuideModuleName(lowerLipName1)
                lowerLipInstance1.changeMirror("X")
                
                lowerLipInstance2 = dpUIinst.initGuide('dpSingle', guideDir)
                lowerLipInstance2.editGuideModuleName(lowerLipName2)
                lowerLipInstance2.changeMirror("X")
                
                lipCornerInstance = dpUIinst.initGuide('dpSingle', guideDir)
                lipCornerInstance.editGuideModuleName(lipCornerName)
                lipCornerInstance.changeMirror("X")
                cmds.refresh()
                
                #
                # complete part:
                #
                if userDetail == complete:
                    
                    dpUIinst.utils.setProgress(doingName+eyelidMainName)

                    eyebrowMiddleInstance = dpUIinst.initGuide('dpSingle', guideDir)
                    eyebrowMiddleInstance.editGuideModuleName(eyebrowMiddleName)

                    eyebrowInstance4 = dpUIinst.initGuide('dpSingle', guideDir)
                    eyebrowInstance4.editGuideModuleName(eyebrowName4)
                    eyebrowInstance4.changeMirror("X")

                    if userIndirectSkin == indSkin:
                        eyelidMainInstance = dpUIinst.initGuide('dpSingle', guideDir)
                        eyelidMainInstance.editGuideModuleName(eyelidMainName)
                        eyelidMainInstance.changeMirror("X")
                        cmds.setAttr(eyelidMainInstance.moduleGrp+".deformedBy", 1)
                        
                        upperEyelidInstance0 = dpUIinst.initGuide('dpSingle', guideDir)
                        upperEyelidInstance0.editGuideModuleName(upperEyelidName0)
                        upperEyelidInstance0.changeMirror("X")
                        
                        upperEyelidInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
                        upperEyelidInstance1.editGuideModuleName(upperEyelidName1)
                        upperEyelidInstance1.changeMirror("X")
                        
                        upperEyelidInstance2 = dpUIinst.initGuide('dpSingle', guideDir)
                        upperEyelidInstance2.editGuideModuleName(upperEyelidName2)
                        upperEyelidInstance2.changeMirror("X")
                        
                        lowerEyelidInstance0 = dpUIinst.initGuide('dpSingle', guideDir)
                        lowerEyelidInstance0.editGuideModuleName(lowerEyelidName0)
                        lowerEyelidInstance0.changeMirror("X")
                        
                        lowerEyelidInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
                        lowerEyelidInstance1.editGuideModuleName(lowerEyelidName1)
                        lowerEyelidInstance1.changeMirror("X")
                        
                        lowerEyelidInstance2 = dpUIinst.initGuide('dpSingle', guideDir)
                        lowerEyelidInstance2.editGuideModuleName(lowerEyelidName2)
                        lowerEyelidInstance2.changeMirror("X")
                        
                        eyelidCornerInstance0 = dpUIinst.initGuide('dpSingle', guideDir)
                        eyelidCornerInstance0.editGuideModuleName(eyelidCornerName0)
                        eyelidCornerInstance0.changeMirror("X")
                        
                        eyelidCornerInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
                        eyelidCornerInstance1.editGuideModuleName(eyelidCornerName1)
                        eyelidCornerInstance1.changeMirror("X")

                        upperEyeSocketInstance0 = dpUIinst.initGuide('dpSingle', guideDir)
                        upperEyeSocketInstance0.editGuideModuleName(upperEyeSocketName0)
                        upperEyeSocketInstance0.changeMirror("X")
                        
                        upperEyeSocketInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
                        upperEyeSocketInstance1.editGuideModuleName(upperEyeSocketName1)
                        upperEyeSocketInstance1.changeMirror("X")
                        
                        upperEyeSocketInstance2 = dpUIinst.initGuide('dpSingle', guideDir)
                        upperEyeSocketInstance2.editGuideModuleName(upperEyeSocketName2)
                        upperEyeSocketInstance2.changeMirror("X")
                        
                        lowerEyeSocketInstance0 = dpUIinst.initGuide('dpSingle', guideDir)
                        lowerEyeSocketInstance0.editGuideModuleName(lowerEyeSocketName0)
                        lowerEyeSocketInstance0.changeMirror("X")
                        
                        lowerEyeSocketInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
                        lowerEyeSocketInstance1.editGuideModuleName(lowerEyeSocketName1)
                        lowerEyeSocketInstance1.changeMirror("X")
                        
                        lowerEyeSocketInstance2 = dpUIinst.initGuide('dpSingle', guideDir)
                        lowerEyeSocketInstance2.editGuideModuleName(lowerEyeSocketName2)
                        lowerEyeSocketInstance2.changeMirror("X")

                    cmds.refresh()                    
                    dpUIinst.utils.setProgress(doingName+eyeSocketName)



                    cmds.refresh()                    
                    dpUIinst.utils.setProgress(doingName+squintMainName)
                    
                    squintMainInstance = dpUIinst.initGuide('dpSingle', guideDir)
                    squintMainInstance.editGuideModuleName(squintMainName)
                    squintMainInstance.changeMirror("X")
                    cmds.setAttr(squintMainInstance.moduleGrp+".deformedBy", 1)
                    
                    squintInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
                    squintInstance1.editGuideModuleName(checkText=squintName1)
                    squintInstance1.changeMirror("X")
                    
                    squintInstance2 = dpUIinst.initGuide('dpSingle', guideDir)
                    squintInstance2.editGuideModuleName(squintName2)
                    squintInstance2.changeMirror("X")
                    
                    squintInstance3 = dpUIinst.initGuide('dpSingle', guideDir)
                    squintInstance3.editGuideModuleName(squintName3)
                    squintInstance3.changeMirror("X")

                    cheekInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
                    cheekInstance1.editGuideModuleName(cheekName1)
                    cheekInstance1.changeMirror("X")

                    cheekInstance2 = dpUIinst.initGuide('dpSingle', guideDir)
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
                
                dpUIinst.utils.setProgress(doingName+" hierarchy")
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
                dpUIinst.utils.setProgress(endIt=True)

                dpUIinst.collapseEditSelModFL = False
                cmds.select(holderMainInstance.moduleGrp)
                print(dpUIinst.lang['m093_createdTweaks'])
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpUIinst.lang['e001_guideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
