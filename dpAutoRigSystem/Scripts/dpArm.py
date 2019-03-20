# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

# global variables to this module:    
CLASS_NAME = "Arm"
TITLE = "m028_arm"
DESCRIPTION = "m029_armDesc"
ICON = "/Icons/dp_arm.png"


def Arm(dpAutoRigInst):
    """ This function will create all guides needed to compose an arm.
    """
    # check modules integrity:
    guideDir = 'Modules'
    checkModuleList = ['dpLimb', 'dpFinger']
    checkResultList = dpAutoRigInst.startGuideModules(guideDir, "check", None, checkModuleList=checkModuleList)
    
    if len(checkResultList) == 0:
        # creating module instances:
        armLimbInstance = dpAutoRigInst.initGuide('dpLimb', guideDir)
        # change name to arm:
        dpAutoRigInst.guide.Limb.editUserName(armLimbInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m028_arm'].capitalize())
        # create finger instances:
        indexFingerInstance  = dpAutoRigInst.initGuide('dpFinger', guideDir)
        dpAutoRigInst.guide.Finger.editUserName(indexFingerInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m007_finger']+"_"+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m032_index'])
        middleFingerInstance = dpAutoRigInst.initGuide('dpFinger', guideDir)
        dpAutoRigInst.guide.Finger.editUserName(middleFingerInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m007_finger']+"_"+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m033_middle'])
        ringFingerInstance   = dpAutoRigInst.initGuide('dpFinger', guideDir)
        dpAutoRigInst.guide.Finger.editUserName(ringFingerInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m007_finger']+"_"+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m034_ring'])
        pinkyFingerInstance   = dpAutoRigInst.initGuide('dpFinger', guideDir)
        dpAutoRigInst.guide.Finger.editUserName(pinkyFingerInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m007_finger']+"_"+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m035_pinky'])
        thumbFingerInstance  = dpAutoRigInst.initGuide('dpFinger', guideDir)
        dpAutoRigInst.guide.Finger.editUserName(thumbFingerInstance, checkText=dpAutoRigInst.langDic[dpAutoRigInst.langName]['m007_finger']+"_"+dpAutoRigInst.langDic[dpAutoRigInst.langName]['m036_thumb'])
        
        # edit arm limb guide:
        armBaseGuide = armLimbInstance.moduleGrp
        cmds.setAttr(armBaseGuide+".translateX", 2.5)
        cmds.setAttr(armBaseGuide+".translateY", 16)
        cmds.setAttr(armBaseGuide+".displayAnnotation", 0)
        cmds.setAttr(armLimbInstance.cvExtremLoc+".translateZ", 7)
        cmds.setAttr(armLimbInstance.radiusCtrl+".translateX", 1.5)
        
        # edit finger guides:
        fingerInstanceList = [indexFingerInstance, middleFingerInstance, ringFingerInstance, pinkyFingerInstance, thumbFingerInstance]
        fingerTZList       = [0.6, 0.2, -0.2, -0.6, 0.72]
        for n, fingerInstance in enumerate(fingerInstanceList):
            cmds.setAttr(fingerInstance.moduleGrp+".translateX", 11)
            cmds.setAttr(fingerInstance.moduleGrp+".translateY", 16)
            cmds.setAttr(fingerInstance.moduleGrp+".translateZ", fingerTZList[n])
            cmds.setAttr(fingerInstance.moduleGrp+".displayAnnotation", 0)
            cmds.setAttr(fingerInstance.radiusCtrl+".translateX", 0.3)
            cmds.setAttr(fingerInstance.annotation+".visibility", 0)
            cmds.setAttr(fingerInstance.moduleGrp+".shapeSize", 0.3)
            
            if n == len(fingerInstanceList)-1:
                # correct not commun values for thumb guide:
                cmds.setAttr(thumbFingerInstance.moduleGrp+".translateX", 10.1)
                cmds.setAttr(thumbFingerInstance.moduleGrp+".rotateX", 60)
                dpAutoRigInst.guide.Finger.changeJointNumber(thumbFingerInstance, 2)
                cmds.setAttr(thumbFingerInstance.moduleGrp+".nJoints", 2)
            
            # parent finger guide to the arm wrist guide:
            cmds.parent(fingerInstance.moduleGrp, armLimbInstance.cvExtremLoc, absolute=True)
        
        # select the armGuide_Base:
        cmds.select(armBaseGuide)
        
    else:
        # error checking modules in the folder:
        mel.eval('error \"'+ dpAutoRigInst.langDic[dpAutoRigInst.langName]['e001_GuideNotChecked'] +' - '+ (", ").join(checkResultList) +'\";')
