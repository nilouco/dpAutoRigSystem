# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "Tweaks"
TITLE = "m081_tweaks"
DESCRIPTION = "m082_tweaksDesc"
ICON = "/Icons/dp_tweaks.png"


def Tweaks(dpAutoRigInst):
    """ This function will create all guides needed to compose a good facial tweaks controls with integrated Single modules using indirect skinning.
    """
    # check modules integrity:
    guideDir = 'Modules'
    checkModuleList = ['dpSingle']
    checkResultList = dpAutoRigInst.startGuideModules(guideDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        # Starting progress window
        progressAmount = 0
        cmds.progressWindow(title='Tweaks Guides', progress=progressAmount, status=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': 0%', isInterruptable=False)
        maxProcess = 6 # number of modules to create

        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m081_tweaks']))
        
        # defining naming
        # part names:
        tweaksName = dpAutoRigInst.langDic[dpAutoRigInst.langName]['m081_tweaks']
        middleName = dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_middle']
        eyebrowName = dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_eyebrow']
        eyelidName = dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_eyelid']
        cornerName = dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_corner']
        upperName = dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_upper']
        lowerName = dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_lower']
        lipName = dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_lip']
        holderName = dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_holder']
        squintName = dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_squint']
        cheekName = dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_cheek']
        
        holderMainName = tweaksName+"_"+holderName
        # eybrows names:
        eyebrowMiddleName = tweaksName+"_"+middleName+"_"+eyebrowName
        eyebrowMainName = tweaksName+"_"+eyebrowName
        eyebrowName1 = tweaksName+"_"+eyebrowName+"_01"
        eyebrowName2 = tweaksName+"_"+eyebrowName+"_02"
        eyebrowName3 = tweaksName+"_"+eyebrowName+"_03"
        # eyelids names:
        eyelidMainName = tweaksName+"_"+eyelidName
        upperEyelidName0 = tweaksName+"_"+upperName+"_"+eyelidName+"_00"
        upperEyelidName1 = tweaksName+"_"+upperName+"_"+eyelidName+"_01"
        upperEyelidName2 = tweaksName+"_"+upperName+"_"+eyelidName+"_02"
        lowerEyelidName0 = tweaksName+"_"+lowerName+"_"+eyelidName+"_00"
        lowerEyelidName1 = tweaksName+"_"+lowerName+"_"+eyelidName+"_01"
        lowerEyelidName2 = tweaksName+"_"+lowerName+"_"+eyelidName+"_02"
        eyelidCornerName0 = tweaksName+"_"+cornerName+"_"+eyelidName+"_00"
        eyelidCornerName1 = tweaksName+"_"+cornerName+"_"+eyelidName+"_01"
        # squints names:
        squintMainName = tweaksName+"_"+squintName
        squintName1 = tweaksName+"_"+squintName+"_01"
        squintName2 = tweaksName+"_"+squintName+"_02"
        squintName3 = tweaksName+"_"+squintName+"_03"
        # cheeks names:
        cheekName1 = tweaksName+"_"+cheekName+"_01"
        # lip names:
        lipMainName = tweaksName+"_"+lipName
        upperLipMiddleName = tweaksName+"_"+upperName+"_"+lipName+"_00"
        upperLipName1 = tweaksName+"_"+upperName+"_"+lipName+"_01"
        upperLipName2 = tweaksName+"_"+upperName+"_"+lipName+"_02"
        lowerLipMiddleName = tweaksName+"_"+lowerName+"_"+lipName+"_00"
        lowerLipName1 = tweaksName+"_"+lowerName+"_"+lipName+"_01"
        lowerLipName2 = tweaksName+"_"+lowerName+"_"+lipName+"_02"
        lipCornerName = tweaksName+"_"+cornerName+"_"+lipName
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_eyebrow']))
        
        # creating Single instances:
        holderMainInstance = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(holderMainInstance, checkText=holderMainName)
        
        eyebrowMiddleInstance = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(eyebrowMiddleInstance, checkText=eyebrowMiddleName)
        
        eyebrowMainInstance = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(eyebrowMainInstance, checkText=eyebrowMainName)
        dpAutoRigInst.guide.Single.changeMirror(eyebrowMainInstance, "X")
        
        eyebrowInstance1 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(eyebrowInstance1, checkText=eyebrowName1)
        dpAutoRigInst.guide.Single.changeMirror(eyebrowInstance1, "X")
        
        eyebrowInstance2 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(eyebrowInstance2, checkText=eyebrowName2)
        dpAutoRigInst.guide.Single.changeMirror(eyebrowInstance2, "X")
        
        eyebrowInstance3 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(eyebrowInstance3, checkText=eyebrowName3)
        dpAutoRigInst.guide.Single.changeMirror(eyebrowInstance3, "X")
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_eyelid']))

        eyelidMainInstance = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(eyelidMainInstance, checkText=eyelidMainName)
        dpAutoRigInst.guide.Single.changeMirror(eyelidMainInstance, "X")
        
        upperEyelidInstance0 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(upperEyelidInstance0, checkText=upperEyelidName0)
        dpAutoRigInst.guide.Single.changeMirror(upperEyelidInstance0, "X")
        
        upperEyelidInstance1 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(upperEyelidInstance1, checkText=upperEyelidName1)
        dpAutoRigInst.guide.Single.changeMirror(upperEyelidInstance1, "X")
        
        upperEyelidInstance2 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(upperEyelidInstance2, checkText=upperEyelidName2)
        dpAutoRigInst.guide.Single.changeMirror(upperEyelidInstance2, "X")
        
        lowerEyelidInstance0 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(lowerEyelidInstance0, checkText=lowerEyelidName0)
        dpAutoRigInst.guide.Single.changeMirror(lowerEyelidInstance0, "X")
        
        lowerEyelidInstance1 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(lowerEyelidInstance1, checkText=lowerEyelidName1)
        dpAutoRigInst.guide.Single.changeMirror(lowerEyelidInstance1, "X")
        
        lowerEyelidInstance2 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(lowerEyelidInstance2, checkText=lowerEyelidName2)
        dpAutoRigInst.guide.Single.changeMirror(lowerEyelidInstance2, "X")
        
        eyelidCornerInstance0 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(eyelidCornerInstance0, checkText=eyelidCornerName0)
        dpAutoRigInst.guide.Single.changeMirror(eyelidCornerInstance0, "X")
        
        eyelidCornerInstance1 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(eyelidCornerInstance1, checkText=eyelidCornerName1)
        dpAutoRigInst.guide.Single.changeMirror(eyelidCornerInstance1, "X")
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_squint']))
        
        squintMainInstance = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(squintMainInstance, checkText=squintMainName)
        dpAutoRigInst.guide.Single.changeMirror(squintMainInstance, "X")
        
        squintInstance1 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(squintInstance1, checkText=squintName1)
        dpAutoRigInst.guide.Single.changeMirror(squintInstance1, "X")
        
        squintInstance2 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(squintInstance2, checkText=squintName2)
        dpAutoRigInst.guide.Single.changeMirror(squintInstance2, "X")
        
        squintInstance3 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(squintInstance3, checkText=squintName3)
        dpAutoRigInst.guide.Single.changeMirror(squintInstance3, "X")


        cheekInstance1 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(cheekInstance1, checkText=cheekName1)
        dpAutoRigInst.guide.Single.changeMirror(cheekInstance1, "X")

        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' '+dpAutoRigInst.langDic[dpAutoRigInst.langName]['c_lip']))

        lipMainInstance = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(lipMainInstance, checkText=lipMainName)
        
        upperLipMiddleInstance = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(upperLipMiddleInstance, checkText=upperLipMiddleName)
        
        upperLipInstance1 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(upperLipInstance1, checkText=upperLipName1)
        dpAutoRigInst.guide.Single.changeMirror(upperLipInstance1, "X")
        
        upperLipInstance2 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(upperLipInstance2, checkText=upperLipName2)
        dpAutoRigInst.guide.Single.changeMirror(upperLipInstance2, "X")
        
        lowerLipMiddleInstance = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(lowerLipMiddleInstance, checkText=lowerLipMiddleName)
        
        lowerLipInstance1 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(lowerLipInstance1, checkText=lowerLipName1)
        dpAutoRigInst.guide.Single.changeMirror(lowerLipInstance1, "X")
        
        lowerLipInstance2 = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(lowerLipInstance2, checkText=lowerLipName2)
        dpAutoRigInst.guide.Single.changeMirror(lowerLipInstance2, "X")
        
        lipCornerInstance = dpAutoRigInst.initGuide('dpSingle', guideDir)
        dpAutoRigInst.guide.Single.editUserName(lipCornerInstance, checkText=lipCornerName)
        dpAutoRigInst.guide.Single.changeMirror(lipCornerInstance, "X")
        
        
        # woking with Single indirect skinning setup:
        # declaring a instanceList in order to clear the code a little:
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
        cmds.setAttr(holderMainInstance.moduleGrp+"."+holderName, 0.7)
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(dpAutoRigInst.langDic[dpAutoRigInst.langName]['m094_doing']+': ' + `progressAmount` + ' hierarchy'))
        
        # working on hierarchy
        cmds.parent([eyebrowMiddleInstance.moduleGrp, eyebrowMainInstance.moduleGrp, eyelidMainInstance.moduleGrp, squintMainInstance.moduleGrp, cheekInstance1.moduleGrp, lipMainInstance.moduleGrp], holderMainInstance.moduleGrp, absolute=True)
        cmds.parent([eyebrowInstance1.moduleGrp, eyebrowInstance2.moduleGrp, eyebrowInstance3.moduleGrp, ], eyebrowMainInstance.moduleGrp, absolute=True)
        cmds.parent([upperEyelidInstance0.moduleGrp, upperEyelidInstance1.moduleGrp, upperEyelidInstance2.moduleGrp, lowerEyelidInstance0.moduleGrp, lowerEyelidInstance1.moduleGrp, lowerEyelidInstance2.moduleGrp, eyelidCornerInstance0.moduleGrp, eyelidCornerInstance1.moduleGrp], eyelidMainInstance.moduleGrp, absolute=True)
        cmds.parent([squintInstance1.moduleGrp, squintInstance2.moduleGrp, squintInstance3.moduleGrp], squintMainInstance.moduleGrp, absolute=True)
        cmds.parent([upperLipMiddleInstance.moduleGrp, upperLipInstance1.moduleGrp, upperLipInstance2.moduleGrp, lowerLipMiddleInstance.moduleGrp, lowerLipInstance1.moduleGrp, lowerLipInstance2.moduleGrp, lipCornerInstance.moduleGrp], lipMainInstance.moduleGrp, absolute=True)
        
        # try to parent to HEAD guide or control
        if cmds.objExists("*__*:Guide_head"):
            cmds.parent(holderMainInstance.moduleGrp, cmds.ls("*__*:Guide_head")[0], relative=True)
        elif cmds.objExists("Head_Head_Ctrl"):
            cmds.parent(holderMainInstance.moduleGrp, "Head_Head_Ctrl", relative=True)
            
        
        # set tweaks guides position
        cmds.setAttr(eyebrowMiddleInstance.moduleGrp+".translateY", 2.8)
        cmds.setAttr(eyebrowMiddleInstance.moduleGrp+".translateZ", 2)
        
        cmds.setAttr(eyebrowMainInstance.moduleGrp+".translateX", 0.65)
        cmds.setAttr(eyebrowMainInstance.moduleGrp+".translateY", 2.8)
        cmds.setAttr(eyebrowMainInstance.moduleGrp+".translateZ", 2)
        
        cmds.setAttr(eyelidMainInstance.moduleGrp+".translateX", 0.5)
        cmds.setAttr(eyelidMainInstance.moduleGrp+".translateY", 2)
        cmds.setAttr(eyelidMainInstance.moduleGrp+".translateZ", 1.3)
        
        cmds.setAttr(lipMainInstance.moduleGrp+".translateY", 1)
        cmds.setAttr(lipMainInstance.moduleGrp+".translateZ", 1)
        
        cmds.setAttr(eyebrowInstance1.moduleGrp+".translateX", -0.2)
        cmds.setAttr(eyebrowInstance1.moduleGrp+".translateZ", 0.1)
        
        cmds.setAttr(eyebrowInstance2.moduleGrp+".translateY", 0.05)
        cmds.setAttr(eyebrowInstance2.moduleGrp+".translateZ", 0.1)
        
        cmds.setAttr(eyebrowInstance3.moduleGrp+".translateX", 0.2)
        cmds.setAttr(eyebrowInstance3.moduleGrp+".translateZ", 0.1)
        
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
        
        # Close progress window
        cmds.progressWindow(endProgress=True)

        cmds.select(holderMainInstance.moduleGrp)
        print dpAutoRigInst.langDic[dpAutoRigInst.langName]['m093_createdTweaks']
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpAutoRigInst.langDic[dpAutoRigInst.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
