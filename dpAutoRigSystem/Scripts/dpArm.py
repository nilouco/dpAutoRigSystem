# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "Arm"
TITLE = "m028_arm"
DESCRIPTION = "m029_armDesc"
ICON = "/Icons/dp_arm.png"


def Arm(dpUIinst):
    """ This function will create all guides needed to compose an arm.
    """
    # check modules integrity:
    guideDir = 'Modules'
    checkModuleList = ['dpLimb', 'dpFinger']
    checkResultList = dpUIinst.startGuideModules(guideDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        # defining naming:
        doingName = dpUIinst.langDic[dpUIinst.langName]['m094_doing']
        # part names:
        armName = dpUIinst.langDic[dpUIinst.langName]['c037_arm']
        fingerIndexName = dpUIinst.langDic[dpUIinst.langName]['m007_finger']+"_"+dpUIinst.langDic[dpUIinst.langName]['m032_index']
        fingerMiddleName = dpUIinst.langDic[dpUIinst.langName]['m007_finger']+"_"+dpUIinst.langDic[dpUIinst.langName]['m033_middle']
        fingerRingName = dpUIinst.langDic[dpUIinst.langName]['m007_finger']+"_"+dpUIinst.langDic[dpUIinst.langName]['m034_ring']
        fingerPinkyName = dpUIinst.langDic[dpUIinst.langName]['m007_finger']+"_"+dpUIinst.langDic[dpUIinst.langName]['m035_pinky']
        fingerThumbName = dpUIinst.langDic[dpUIinst.langName]['m007_finger']+"_"+dpUIinst.langDic[dpUIinst.langName]['m036_thumb']
    
        # Starting progress window
        progressAmount = 0
        cmds.progressWindow(title='Arm Guides', progress=progressAmount, status=doingName+': 0%', isInterruptable=False)
        maxProcess = 2 # number of modules to create

        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+armName))
        
        # creating module instances:
        armLimbInstance = dpUIinst.initGuide('dpLimb', guideDir)
        # change name to arm:
        armLimbInstance.editUserName(armName.capitalize())
        # create finger instances:
        thumbFingerInstance  = dpUIinst.initGuide('dpFinger', guideDir)
        thumbFingerInstance.editUserName(fingerThumbName)
        indexFingerInstance  = dpUIinst.initGuide('dpFinger', guideDir)
        indexFingerInstance.editUserName(fingerIndexName)
        middleFingerInstance = dpUIinst.initGuide('dpFinger', guideDir)
        middleFingerInstance.editUserName(fingerMiddleName)
        ringFingerInstance   = dpUIinst.initGuide('dpFinger', guideDir)
        ringFingerInstance.editUserName(fingerRingName)
        pinkyFingerInstance  = dpUIinst.initGuide('dpFinger', guideDir)
        pinkyFingerInstance.editUserName(fingerPinkyName)
        
        # edit arm limb guide:
        armBaseGuide = armLimbInstance.moduleGrp
        cmds.setAttr(armBaseGuide+".translateX", 2.5)
        cmds.setAttr(armBaseGuide+".translateY", 16)
        cmds.setAttr(armBaseGuide+".displayAnnotation", 0)
        cmds.setAttr(armLimbInstance.cvExtremLoc+".translateZ", 7)
        cmds.setAttr(armLimbInstance.radiusCtrl+".translateX", 1.5)
        
        # Update progress window
        progressAmount += 1
        cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(doingName+': ' + `progressAmount` + ' '+dpUIinst.langDic[dpUIinst.langName]['m007_finger']))
        
        # edit finger guides:
        fingerInstanceList = [thumbFingerInstance, indexFingerInstance, middleFingerInstance, ringFingerInstance, pinkyFingerInstance]
        fingerTZList       = [0.72, 0.6, 0.2, -0.2, -0.6]
        for n, fingerInstance in enumerate(fingerInstanceList):
            cmds.setAttr(fingerInstance.moduleGrp+".translateX", 11)
            cmds.setAttr(fingerInstance.moduleGrp+".translateY", 16)
            cmds.setAttr(fingerInstance.moduleGrp+".translateZ", fingerTZList[n])
            cmds.setAttr(fingerInstance.moduleGrp+".displayAnnotation", 0)
            cmds.setAttr(fingerInstance.radiusCtrl+".translateX", 0.3)
            cmds.setAttr(fingerInstance.annotation+".visibility", 0)
            cmds.setAttr(fingerInstance.moduleGrp+".shapeSize", 0.3)
            
            if n == 0:
                # correct not commun values for thumb guide:
                cmds.setAttr(thumbFingerInstance.moduleGrp+".translateX", 10.1)
                cmds.setAttr(thumbFingerInstance.moduleGrp+".rotateX", 60)
                thumbFingerInstance.changeJointNumber(2)
                cmds.setAttr(thumbFingerInstance.moduleGrp+".nJoints", 2)
            
            # parent finger guide to the arm wrist guide:
            cmds.parent(fingerInstance.moduleGrp, armLimbInstance.cvExtremLoc, absolute=True)
        
        # Close progress window
        cmds.progressWindow(endProgress=True)

        # select the armGuide_Base:
        cmds.select(armBaseGuide)
        print dpUIinst.langDic[dpUIinst.langName]['m091_createdArm']+"\n",
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpUIinst.langDic[dpUIinst.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
