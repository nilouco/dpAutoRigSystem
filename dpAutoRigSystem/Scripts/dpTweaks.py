# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "Tweaks"
TITLE = "m081_tweaks"
DESCRIPTION = "m082_tweaksDesc"
ICON = "/Icons/dp_tweaks.png"



def getUserDetail(opt1, opt2, cancel, userMessage):
    """ Ask user the detail level we'll create the guides by a confirm dialog box window.
        Options:
            Simple
            Complete
        Returns the user choose option or None if canceled.
    """
    result = cmds.confirmDialog(title=CLASS_NAME, message=userMessage, button=[opt1, opt2, cancel], defaultButton=opt2, cancelButton=cancel, dismissString=cancel)
    return result


def Tweaks(dpUIinst):
    """ This function will create all guides needed to compose a good facial tweaks controls with integrated Single modules using indirect skinning.
    """
    # check modules integrity:
    guideDir = 'Modules'
    checkModuleList = ['dpSingle']
    checkResultList = dpUIinst.startGuideModules(guideDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        # defining naming:
        doingName = dpUIinst.langDic[dpUIinst.langName]['m094_doing']
        # part names:
        mainName = dpUIinst.langDic[dpUIinst.langName]['c058_main']
        tweaksName = dpUIinst.langDic[dpUIinst.langName]['m081_tweaks']
        middleName = dpUIinst.langDic[dpUIinst.langName]['c029_middle']
        eyebrowName = dpUIinst.langDic[dpUIinst.langName]['c041_eyebrow']
        eyelidName = dpUIinst.langDic[dpUIinst.langName]['c042_eyelid']
        cornerName = dpUIinst.langDic[dpUIinst.langName]['c043_corner']
        upperName = dpUIinst.langDic[dpUIinst.langName]['c044_upper']
        lowerName = dpUIinst.langDic[dpUIinst.langName]['c045_lower']
        lipName = dpUIinst.langDic[dpUIinst.langName]['c039_lip']
        holderName = dpUIinst.langDic[dpUIinst.langName]['c046_holder']
        squintName = dpUIinst.langDic[dpUIinst.langName]['c054_squint']
        cheekName = dpUIinst.langDic[dpUIinst.langName]['c055_cheek']
        
        holderMainName = tweaksName+"_"+holderName+"_"+mainName
        # eybrows names:
        eyebrowMiddleName = tweaksName+"_"+middleName+"_"+eyebrowName
        eyebrowMainName = tweaksName+"_"+eyebrowName+"_"+mainName
        eyebrowName1 = tweaksName+"_"+eyebrowName+"_01"
        eyebrowName2 = tweaksName+"_"+eyebrowName+"_02"
        eyebrowName3 = tweaksName+"_"+eyebrowName+"_03"
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
        # squints names:
        squintMainName = tweaksName+"_"+squintName+"_"+mainName
        squintName1 = tweaksName+"_"+squintName+"_01"
        squintName2 = tweaksName+"_"+squintName+"_02"
        squintName3 = tweaksName+"_"+squintName+"_03"
        # cheeks names:
        cheekName1 = tweaksName+"_"+cheekName+"_01"
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
        simple   = dpUIinst.langDic[dpUIinst.langName]['i175_simple']
        complete = dpUIinst.langDic[dpUIinst.langName]['i176_complete']
        cancel   = dpUIinst.langDic[dpUIinst.langName]['i132_cancel']
        userMessage = dpUIinst.langDic[dpUIinst.langName]['i177_chooseMessage']
        
        
        # getting Simple or Complete module guides to create:
        userDetail = getUserDetail(simple, complete, cancel, userMessage)
        if not userDetail == cancel:
            # number of modules to create:
            if userDetail == simple:
                maxProcess = 3
            else:
                maxProcess = 5
        
            # Starting progress window
            progressAmount = 0
            cmds.progressWindow(title='Tweaks Guides', progress=progressAmount, status=dpUIinst.langDic[dpUIinst.langName]['m094_doing']+': 0%', isInterruptable=False)
            
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+eyebrowMainName))
            
            # creating Single instances:
            holderMainInstance = dpUIinst.initGuide('dpSingle', guideDir)
            holderMainInstance.editUserName(holderMainName)
            
            eyebrowMainInstance = dpUIinst.initGuide('dpSingle', guideDir)
            eyebrowMainInstance.editUserName(eyebrowMainName)
            eyebrowMainInstance.changeMirror("X")
            
            eyebrowInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
            eyebrowInstance1.editUserName(eyebrowName1)
            eyebrowInstance1.changeMirror("X")
            
            eyebrowInstance2 = dpUIinst.initGuide('dpSingle', guideDir)
            eyebrowInstance2.editUserName(eyebrowName2)
            eyebrowInstance2.changeMirror("X")
            
            eyebrowInstance3 = dpUIinst.initGuide('dpSingle', guideDir)
            eyebrowInstance3.editUserName(eyebrowName3)
            eyebrowInstance3.changeMirror("X")
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+lipMainName))

            lipMainInstance = dpUIinst.initGuide('dpSingle', guideDir)
            lipMainInstance.editUserName(lipMainName)
            
            upperLipMiddleInstance = dpUIinst.initGuide('dpSingle', guideDir)
            upperLipMiddleInstance.editUserName(upperLipMiddleName)
            
            upperLipInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
            upperLipInstance1.editUserName(checkText=upperLipName1)
            upperLipInstance1.changeMirror("X")
            
            upperLipInstance2 = dpUIinst.initGuide('dpSingle', guideDir)
            upperLipInstance2.editUserName(upperLipName2)
            upperLipInstance2.changeMirror("X")
            
            lowerLipMiddleInstance = dpUIinst.initGuide('dpSingle', guideDir)
            lowerLipMiddleInstance.editUserName(lowerLipMiddleName)
            
            lowerLipInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
            lowerLipInstance1.editUserName(lowerLipName1)
            lowerLipInstance1.changeMirror("X")
            
            lowerLipInstance2 = dpUIinst.initGuide('dpSingle', guideDir)
            lowerLipInstance2.editUserName(lowerLipName2)
            lowerLipInstance2.changeMirror("X")
            
            lipCornerInstance = dpUIinst.initGuide('dpSingle', guideDir)
            lipCornerInstance.editUserName(lipCornerName)
            lipCornerInstance.changeMirror("X")
            
            if userDetail == complete:
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+eyelidMainName))
                
                eyebrowMiddleInstance = dpUIinst.initGuide('dpSingle', guideDir)
                eyebrowMiddleInstance.editUserName(eyebrowMiddleName)
            
                eyelidMainInstance = dpUIinst.initGuide('dpSingle', guideDir)
                eyelidMainInstance.editUserName(eyelidMainName)
                eyelidMainInstance.changeMirror("X")
                
                upperEyelidInstance0 = dpUIinst.initGuide('dpSingle', guideDir)
                upperEyelidInstance0.editUserName(upperEyelidName0)
                upperEyelidInstance0.changeMirror("X")
                
                upperEyelidInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
                upperEyelidInstance1.editUserName(upperEyelidName1)
                upperEyelidInstance1.changeMirror("X")
                
                upperEyelidInstance2 = dpUIinst.initGuide('dpSingle', guideDir)
                upperEyelidInstance2.editUserName(upperEyelidName2)
                upperEyelidInstance2.changeMirror("X")
                
                lowerEyelidInstance0 = dpUIinst.initGuide('dpSingle', guideDir)
                lowerEyelidInstance0.editUserName(lowerEyelidName0)
                lowerEyelidInstance0.changeMirror("X")
                
                lowerEyelidInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
                lowerEyelidInstance1.editUserName(lowerEyelidName1)
                lowerEyelidInstance1.changeMirror("X")
                
                lowerEyelidInstance2 = dpUIinst.initGuide('dpSingle', guideDir)
                lowerEyelidInstance2.editUserName(lowerEyelidName2)
                lowerEyelidInstance2.changeMirror("X")
                
                eyelidCornerInstance0 = dpUIinst.initGuide('dpSingle', guideDir)
                eyelidCornerInstance0.editUserName(eyelidCornerName0)
                eyelidCornerInstance0.changeMirror("X")
                
                eyelidCornerInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
                eyelidCornerInstance1.editUserName(eyelidCornerName1)
                eyelidCornerInstance1.changeMirror("X")
                
                # Update progress window
                progressAmount += 1
                cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+squintMainName))
                
                squintMainInstance = dpUIinst.initGuide('dpSingle', guideDir)
                squintMainInstance.editUserName(squintMainName)
                squintMainInstance.changeMirror("X")
                
                squintInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
                squintInstance1.editUserName(checkText=squintName1)
                squintInstance1.changeMirror("X")
                
                squintInstance2 = dpUIinst.initGuide('dpSingle', guideDir)
                squintInstance2.editUserName(squintName2)
                squintInstance2.changeMirror("X")
                
                squintInstance3 = dpUIinst.initGuide('dpSingle', guideDir)
                squintInstance3.editUserName(squintName3)
                squintInstance3.changeMirror("X")


                cheekInstance1 = dpUIinst.initGuide('dpSingle', guideDir)
                cheekInstance1.editUserName(cheekName1)
                cheekInstance1.changeMirror("X")
            
            # woking with Single indirect skinning setup:
            # declaring a instanceList in order to clear the code a little:
            instanceList = [holderMainInstance, eyebrowMainInstance, eyebrowInstance1, eyebrowInstance2, eyebrowInstance3, lipMainInstance, upperLipMiddleInstance, upperLipInstance1, upperLipInstance2, lowerLipMiddleInstance, lowerLipInstance1, lowerLipInstance2, lipCornerInstance]
            sideInstanceList = [eyebrowMainInstance, eyebrowInstance1, eyebrowInstance2, eyebrowInstance3, upperLipInstance1, upperLipInstance2, lowerLipInstance1, lowerLipInstance2, lipCornerInstance]
            mainInstanceList = [eyebrowMainInstance, lipMainInstance]
            
            if userDetail == complete:
                instanceList = [holderMainInstance, eyebrowMiddleInstance, eyebrowMainInstance, eyebrowInstance1, eyebrowInstance2, eyebrowInstance3, eyelidMainInstance, upperEyelidInstance0, upperEyelidInstance1, upperEyelidInstance2, lowerEyelidInstance0, lowerEyelidInstance1, lowerEyelidInstance2, eyelidCornerInstance0, eyelidCornerInstance1, squintMainInstance, squintInstance1, squintInstance2, squintInstance3, cheekInstance1, lipMainInstance, upperLipMiddleInstance, upperLipInstance1, upperLipInstance2, lowerLipMiddleInstance, lowerLipInstance1, lowerLipInstance2, lipCornerInstance]
                sideInstanceList = [eyebrowMainInstance, eyebrowInstance1, eyebrowInstance2, eyebrowInstance3, eyelidMainInstance, upperEyelidInstance0, upperEyelidInstance1, upperEyelidInstance2, lowerEyelidInstance0, lowerEyelidInstance1, lowerEyelidInstance2, eyelidCornerInstance0, eyelidCornerInstance1, squintMainInstance, squintInstance1, squintInstance2, squintInstance3, cheekInstance1, upperLipInstance1, upperLipInstance2, lowerLipInstance1, lowerLipInstance2, lipCornerInstance]
                mainInstanceList = [eyebrowMainInstance, eyelidMainInstance, squintMainInstance, lipMainInstance]
            
            # turn on indirectSkinning:
            for inst in instanceList:
                cmds.setAttr(inst.moduleGrp+".indirectSkin", 1)
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
            
            # Update progress window
            progressAmount += 1
            cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' hierarchy'))
            
            # working on hierarchy
            cmds.parent([eyebrowMainInstance.moduleGrp, lipMainInstance.moduleGrp], holderMainInstance.moduleGrp, absolute=True)
            cmds.parent([eyebrowInstance1.moduleGrp, eyebrowInstance2.moduleGrp, eyebrowInstance3.moduleGrp, ], eyebrowMainInstance.moduleGrp, absolute=True)
            cmds.parent([upperLipMiddleInstance.moduleGrp, upperLipInstance1.moduleGrp, upperLipInstance2.moduleGrp, lowerLipMiddleInstance.moduleGrp, lowerLipInstance1.moduleGrp, lowerLipInstance2.moduleGrp, lipCornerInstance.moduleGrp], lipMainInstance.moduleGrp, absolute=True)
            
            if userDetail == complete:
                cmds.parent([eyebrowMiddleInstance.moduleGrp, eyelidMainInstance.moduleGrp, squintMainInstance.moduleGrp, cheekInstance1.moduleGrp], holderMainInstance.moduleGrp, absolute=True)
                cmds.parent([upperEyelidInstance0.moduleGrp, upperEyelidInstance1.moduleGrp, upperEyelidInstance2.moduleGrp, lowerEyelidInstance0.moduleGrp, lowerEyelidInstance1.moduleGrp, lowerEyelidInstance2.moduleGrp, eyelidCornerInstance0.moduleGrp, eyelidCornerInstance1.moduleGrp], eyelidMainInstance.moduleGrp, absolute=True)
                cmds.parent([squintInstance1.moduleGrp, squintInstance2.moduleGrp, squintInstance3.moduleGrp], squintMainInstance.moduleGrp, absolute=True)
            
            # try to parent to HEAD guide or control
            if cmds.objExists("*__*:Guide_Head"):
                cmds.parent(holderMainInstance.moduleGrp, cmds.ls("*__*:Guide_Head")[0], relative=True)
            elif cmds.objExists("Head_Head_Ctrl"):
                cmds.parent(holderMainInstance.moduleGrp, "Head_Head_Ctrl", relative=True)
                
            
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
                
                cmds.setAttr(eyelidCornerInstance0.moduleGrp+".translateX", -0.3)
                cmds.setAttr(eyelidCornerInstance0.moduleGrp+".translateZ", 0.5)
                
                cmds.setAttr(eyelidCornerInstance1.moduleGrp+".translateX", 0.3)
                cmds.setAttr(eyelidCornerInstance1.moduleGrp+".translateZ", 0.5)
            
            
            # Close progress window
            cmds.progressWindow(endProgress=True)

            cmds.select(holderMainInstance.moduleGrp)
            print dpUIinst.langDic[dpUIinst.langName]['m093_createdTweaks']+"\n",
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpUIinst.langDic[dpUIinst.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
