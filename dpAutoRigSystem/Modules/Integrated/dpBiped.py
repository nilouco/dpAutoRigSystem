# importing libraries:
from maya import cmds
from maya import mel
from ..Base import dpBaseLibrary
from importlib import reload

# global variables to this module:    
CLASS_NAME = "Biped"
TITLE = "m026_biped"
DESCRIPTION = "m027_bipedDesc"
ICON = "/Icons/dp_biped.png"
WIKI = "03-‐-Guides#-biped"

DP_BIPED_VERSION = 2.04


class Biped(dpBaseLibrary.BaseLibrary):
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
        # dependence module list:
        self.check_modules = ['dpLimb', 'dpFoot', 'dpFinger', 'dpSpine', 'dpHead', 'dpFkLine', 'dpEye', 'dpNose', 'dpSingle']


    def build_template(self, *args):
        """ This function will create all guides needed to compose a biped.
        """
        # check modules integrity:
        guideDir = 'Modules.Standard'
        standardDir = 'Modules/Standard'
        checkModuleList = ['dpLimb', 'dpFoot', 'dpFinger', 'dpSpine', 'dpHead', 'dpFkLine', 'dpEye', 'dpNose', 'dpSingle']
        missing_modules = self.ar.ui_manager.check_missing_modules(self.ar.data.standard_folder, self.check_modules)
        
        if not missing_modules:
            self.ar.data.collapse_edit_sel_mod = True
            # defining naming:
            doingName = self.ar.data.lang['m094_doing']
            bipedStyleName = self.ar.data.lang['m026_biped']
            # part names:
            spineName = self.ar.data.lang['m011_spine']
            headName = self.ar.data.lang['c024_head']
            eyeName = self.ar.data.lang['c036_eye']
            legName = self.ar.data.lang['m030_leg'].capitalize()
            footName = self.ar.data.lang['c038_foot']
            armName = self.ar.data.lang['c037_arm'].capitalize()
            fingerIndexName = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m032_index']
            fingerMiddleName = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m033_middle']
            fingerRingName = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m034_ring']
            fingerPinkyName = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m035_pinky']
            fingerThumbName = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m036_thumb']
            earName = self.ar.data.lang['m040_ear']
            upperTeethName = self.ar.data.lang['m075_upperTeeth']
            upperTeethMiddleName = self.ar.data.lang['m075_upperTeeth']+self.ar.data.lang['c029_middle'].capitalize()
            upperTeethSideName = self.ar.data.lang['m075_upperTeeth']+self.ar.data.lang['c016_revFoot_G'].capitalize()
            lowerTeethName = self.ar.data.lang['m076_lowerTeeth']
            lowerTeethMiddleName = self.ar.data.lang['m076_lowerTeeth']+self.ar.data.lang['c029_middle'].capitalize()
            lowerTeethSideName = self.ar.data.lang['m076_lowerTeeth']+self.ar.data.lang['c016_revFoot_G'].capitalize()
            noseName = self.ar.data.lang['m078_nose']
            tongueName = self.ar.data.lang['m077_tongue']
            toeName = self.ar.data.lang['c013_revFoot_D'].capitalize()
            breathName = self.ar.data.lang['c095_breath']
            bellyName = self.ar.data.lang['c096_belly']
            simple   = self.ar.data.lang['i175_simple']
            complete = self.ar.data.lang['i176_complete']
            cancel   = self.ar.data.lang['i132_cancel']
            userMessage = self.ar.data.lang['i177_chooseMessage']
            bipedGuideName = self.ar.data.lang['m026_biped']+" "+self.ar.data.lang['i205_guide']
            
            
            # getting Simple or Complete module guides to create:
            user_choice = self.ask_build_detail(self.title, simple, complete, cancel, complete, userMessage)
            if not user_choice == cancel:
                # number of modules to create:
                maxProcess = 18
                if user_choice == simple:
                    maxProcess = 7
                
            
                # Starting progress window
                self.ar.utils.setProgress(self.ar.data.lang['m094_doing'], bipedGuideName, maxProcess, addOne=False, addNumber=False)

                # getting module instances:
                limb = self.ar.config.get_instance("dpLimb", [guideDir])
                foot = self.ar.config.get_instance("dpFoot", [guideDir])
                finger = self.ar.config.get_instance("dpFinger", [guideDir])
                spine = self.ar.config.get_instance("dpSpine", [guideDir])
                head = self.ar.config.get_instance("dpHead", [guideDir])
                fkline = self.ar.config.get_instance("dpFkLine", [guideDir])
                eye = self.ar.config.get_instance("dpEye", [guideDir])
                nose = self.ar.config.get_instance("dpNose", [guideDir])
                single = self.ar.config.get_instance("dpSingle", [guideDir])

                # working with SPINE system:
                self.ar.utils.setProgress(doingName+spineName)
                # create spine module instance:
                spine_guide = spine.build_raw_guide()
                # editing spine base guide informations:
                spine.editGuideModuleName(spineName)
                spine.changeStyle(bipedStyleName)
                cmds.setAttr(spine_guide+".translateY", 11)
                cmds.setAttr(spine.annotation+".translateY", -6)
                cmds.setAttr(spine.radiusCtrl+".translateX", 2.5)
                cmds.refresh()
                
                # working with HEAD system:
                self.ar.utils.setProgress(doingName+headName)
                # create head module instance:
                head_guide = head.build_raw_guide()
                # editing head base guide informations:
                head.editGuideModuleName(headName)
                head.changeJointNumber(2)
                cmds.setAttr(head_guide+".translateY", 17)
                cmds.setAttr(head.annotation+".translateY", 3.5)
                # parent head guide to spine guide:
                cmds.parent(head_guide, spine.cvLocator, absolute=True)
                head.changeStyle(bipedStyleName)
                cmds.refresh()
                
                # working with Eye system:
                self.ar.utils.setProgress(doingName+eyeName)
                # create eye module instance:
                eye_guide = eye.build_raw_guide()
                # editing eyeLookAt base guide informations:
                eye.editGuideModuleName(eyeName)
                # setting X mirror:
                eye.changeMirror("X")
                cmds.setAttr(eye_guide+".translateX", 0.5)
                cmds.setAttr(eye_guide+".translateY", 21)
                cmds.setAttr(eye_guide+".translateZ", 1.5)
                cmds.setAttr(eye.annotation+".translateY", 3.5)
                cmds.setAttr(eye.radiusCtrl+".translateX", 0.5)
                cmds.setAttr(eye.cvEndJoint+".translateZ", 7)
                cmds.setAttr(eye_guide+".flip", 1)
                # parent eye guide to spine guide:
                cmds.parent(eye_guide, head.cvUpperHeadLoc, absolute=True)
                if user_choice == complete:
                        eye.setCorrective(1)
                cmds.refresh()
                
                # working with LEG system:
                self.ar.utils.setProgress(doingName+legName)
                # create leg module instance:
                leg_guide = limb.build_raw_guide()
                # change name to leg:
                limb.editGuideModuleName(legName)
                # setting X mirror:
                limb.changeMirror("X")
                # change limb guide to leg type:
                limb.changeType(legName)
                # change limb style to biped:
                limb.changeStyle(bipedStyleName)
                cmds.setAttr(limb.annotation+".translateY", -4)
                # editing leg base guide informations:
                cmds.setAttr(leg_guide+".type", 1)
                cmds.setAttr(leg_guide+".translateX", 1.5)
                cmds.setAttr(leg_guide+".translateY", 10)
                cmds.setAttr(leg_guide+".rotateX", 0)
                cmds.setAttr(limb.radiusCtrl+".translateX", 1.5)
                # edit location of leg ankle guide:
                cmds.setAttr(limb.cvExtremLoc+".translateZ", 8.5)
                # parent leg guide to spine base guide:
                cmds.parent(leg_guide, spine_guide, absolute=True)
                if user_choice == complete:
                        limb.setCorrective(1)
                cmds.refresh()
                
                # working with FOOT system:
                self.ar.utils.setProgress(doingName+footName)
                # create foot module instance:
                foot_guide = foot.build_raw_guide()
                foot.editGuideModuleName(footName)
                cmds.setAttr(foot.annotation+".translateY", -3)
                cmds.setAttr(foot_guide+".translateX", 1.5)
                cmds.setAttr(foot.cvFootLoc+".translateZ", 1.5)
                # parent foot guide to leg ankle guide:
                cmds.parent(foot_guide, limb.cvExtremLoc, absolute=True)
                foot.checkFatherMirror()
                cmds.refresh()
                
                # working with ARM system:
                self.ar.utils.setProgress(doingName+armName)
                # creating module instances:
                arm_guide = limb.build_raw_guide()
                # change name to arm:
                limb.editGuideModuleName(armName)
                # setting X mirror:
                limb.changeMirror("X")
                # change limb style to biped:
                limb.changeStyle(bipedStyleName)
                cmds.setAttr(limb.annotation+".translateX", 3)
                cmds.setAttr(limb.annotation+".translateY", 0)
                cmds.setAttr(limb.annotation+".translateZ", 2)
                # edit arm limb guide:
                cmds.setAttr(arm_guide+".translateX", 2.5)
                cmds.setAttr(arm_guide+".translateY", 16)
                cmds.setAttr(limb.cvExtremLoc+".translateZ", 7)
                cmds.setAttr(limb.radiusCtrl+".translateX", 1.5)
                # parent arm guide to spine chest guide:
                cmds.parent(arm_guide, spine.cvLocator, absolute=True)
                if user_choice == complete:
                        limb.setCorrective(1)
                cmds.refresh()
                
                # working with FINGERS system:
                self.ar.utils.setProgress(doingName+self.ar.data.lang['m007_finger'])
                # edit finger guides:
                finger_names = [fingerThumbName, fingerIndexName, fingerMiddleName, fingerRingName, fingerPinkyName]
                fingerTZList = [0.72, 0.6, 0.2, -0.2, -0.6]
                for n, finger_name in enumerate(finger_names):
                    self.ar.utils.setProgress(doingName+self.ar.data.lang['m007_finger'])
                    finger_guide = finger.build_raw_guide()
                    finger.editGuideModuleName(finger_name)
                    cmds.setAttr(finger_guide+".translateX", 11)
                    cmds.setAttr(finger_guide+".translateY", 16)
                    cmds.setAttr(finger_guide+".translateZ", fingerTZList[n])
                    cmds.setAttr(finger_guide+".displayAnnotation", 0)
                    cmds.setAttr(finger_guide+".shapeSize", 0.3)
                    cmds.setAttr(finger.radiusCtrl+".translateX", 0.3)
                    cmds.setAttr(finger.annotation+".visibility", 0)
                    if n == 0:
                        # correct not commun values for thumb guide:
                        cmds.setAttr(finger_guide+".translateX", 10.1)
                        cmds.setAttr(finger_guide+".rotateX", 60)
                        finger.changeJointNumber(2)
                        cmds.setAttr(finger_guide+".nJoints", 2)
                    # parent finger guide to the arm wrist guide:
                    cmds.parent(finger_guide, limb.cvExtremLoc, absolute=True)
                    if user_choice == complete:
                        finger.setCorrective(1)
                    cmds.refresh()
                
                #
                # complete part:
                #
                if user_choice == complete:
                
                    # set guides attributes to complete system
                    head.changeDeformer(1)
                    head.changeFacial(1)

                    # working with EAR system:
                    self.ar.utils.setProgress(doingName+earName)
                    # create FkLine module instance:
                    ear_guide = fkline.build_raw_guide()
                    # editing ear base guide informations:
                    fkline.editGuideModuleName(earName)
                    cmds.setAttr(ear_guide+".translateX", 1)
                    cmds.setAttr(ear_guide+".translateY", 21)
                    cmds.setAttr(ear_guide+".rotateY", 110)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.5)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.3)
                    # parent ear guide to head guide:
                    cmds.parent(ear_guide, head.cvUpperHeadLoc, absolute=True)
                    # setting X mirror:
                    fkline.changeMirror("X")
                    cmds.setAttr(ear_guide+".flip", 1)
                    cmds.setAttr(ear_guide+".deformedBy", 1)
                    cmds.refresh()

                    # working with Teeth system:
                    self.ar.utils.setProgress(doingName+upperTeethName)
                    # create FkLine module instance:
                    upper_teeth_guide = fkline.build_raw_guide()
                    upper_teeth_cv_joint_loc = fkline.cvJointLoc
                    # editing upperTeeth base guide informations:
                    fkline.editGuideModuleName(upperTeethName)
                    cmds.setAttr(upper_teeth_guide+".translateY", 20.3)
                    cmds.setAttr(upper_teeth_guide+".translateZ", 2.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.5)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.1)
                    cmds.setAttr(upper_teeth_guide+".shapeSize", 0.5)
                    cmds.setAttr(upper_teeth_guide+".deformedBy", 3)
                    # parent upperTeeth guide to head guide:
                    cmds.parent(upper_teeth_guide, head.cvUpperJawLoc, absolute=True)
                    # create FkLine module instance:
                    upper_teeth_middle_guide = fkline.build_raw_guide()
                    # editing upperTeethMiddle base guide informations:
                    fkline.editGuideModuleName(upperTeethMiddleName)
                    cmds.setAttr(upper_teeth_middle_guide+".translateY", 20.1)
                    cmds.setAttr(upper_teeth_middle_guide+".translateZ", 2.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.1)
                    cmds.setAttr(upper_teeth_middle_guide+".shapeSize", 0.3)
                    cmds.setAttr(upper_teeth_middle_guide+".deformedBy", 3)
                    fkline.displayAnnotation(0)
                    # parent upperTeethMiddle guide to upperTeeth guide:
                    cmds.parent(upper_teeth_middle_guide, upper_teeth_cv_joint_loc, absolute=True)
                    # create FkLine module instance:
                    upper_teeth_side_guide = fkline.build_raw_guide()
                    # editing upperTeethSide base guide informations:
                    fkline.editGuideModuleName(upperTeethSideName)
                    cmds.setAttr(upper_teeth_side_guide+".translateX", 0.2)
                    cmds.setAttr(upper_teeth_side_guide+".translateY", 20.1)
                    cmds.setAttr(upper_teeth_side_guide+".translateZ", 2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.1)
                    cmds.setAttr(upper_teeth_side_guide+".shapeSize", 0.3)
                    cmds.setAttr(upper_teeth_side_guide+".deformedBy", 3)
                    fkline.changeMirror("X")
                    cmds.setAttr(upper_teeth_side_guide+".flip", 1)
                    fkline.displayAnnotation(0)
                    # parent upperTeethSide guide to upperTeeth guide:
                    cmds.parent(upper_teeth_side_guide, upper_teeth_cv_joint_loc, absolute=True)
                    # create FkLine module instance:
                    lower_teeth_guide = fkline.build_raw_guide()
                    lower_teeth_cv_joint_loc = fkline.cvJointLoc
                    # editing lowerTeeth base guide informations:
                    fkline.editGuideModuleName(lowerTeethName)
                    cmds.setAttr(lower_teeth_guide+".translateY", 19.5)
                    cmds.setAttr(lower_teeth_guide+".translateZ", 2.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.5)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.1)
                    cmds.setAttr(lower_teeth_guide+".shapeSize", 0.5)
                    cmds.setAttr(lower_teeth_guide+".deformedBy", 3)
                    # parent lowerTeeth guide to head guide:
                    cmds.parent(lower_teeth_guide, head.cvChinLoc, absolute=True)
                    # create FkLine module instance:
                    lower_teeth_middle_guide = fkline.build_raw_guide()
                    # editing lowerTeethMiddle base guide informations:
                    fkline.editGuideModuleName(lowerTeethMiddleName)
                    cmds.setAttr(lower_teeth_middle_guide+".translateY", 19.7)
                    cmds.setAttr(lower_teeth_middle_guide+".translateZ", 2.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.1)
                    cmds.setAttr(lower_teeth_middle_guide+".shapeSize", 0.3)
                    cmds.setAttr(lower_teeth_middle_guide+".deformedBy", 3)
                    fkline.displayAnnotation(0)
                    # parent lowerTeeth guide to lowerTeeth guide:
                    cmds.parent(lower_teeth_middle_guide, lower_teeth_cv_joint_loc, absolute=True)
                    # create FkLine module instance:
                    lower_teeth_side_guide = fkline.build_raw_guide()
                    # editing lowerTeethSide base guide informations:
                    fkline.editGuideModuleName(lowerTeethSideName)
                    cmds.setAttr(lower_teeth_side_guide+".translateX", 0.2)
                    cmds.setAttr(lower_teeth_side_guide+".translateY", 19.7)
                    cmds.setAttr(lower_teeth_side_guide+".translateZ", 2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.1)
                    cmds.setAttr(lower_teeth_side_guide+".shapeSize", 0.3)
                    cmds.setAttr(lower_teeth_side_guide+".deformedBy", 3)
                    fkline.changeMirror("X")
                    cmds.setAttr(lower_teeth_side_guide+".flip", 1)
                    fkline.displayAnnotation(0)
                    # parent lowerTeethSide guide to lowerTeeth guide:
                    cmds.parent(lower_teeth_side_guide, lower_teeth_cv_joint_loc, absolute=True)
                    cmds.refresh()
                    
                    # working with Nose systems:
                    self.ar.utils.setProgress(doingName+noseName)
                    # create FkLine module instance:
                    nose_guide = nose.build_raw_guide()
                    # editing upperTeeth base guide informations:
                    nose.editGuideModuleName(noseName)
                    cmds.setAttr(nose_guide+".translateY", 21.2)
                    cmds.setAttr(nose_guide+".translateZ", 2)
                    cmds.setAttr(nose.radiusCtrl+".translateX", 0.3)
                    nose.changeJointNumber(2)
                    # parent nose guide to head guide:
                    cmds.parent(nose_guide, head.cvUpperJawLoc, absolute=True)
                    cmds.refresh()
                    
                    # working with Tongue system:
                    self.ar.utils.setProgress(doingName+tongueName)
                    # create FkLine module instance:
                    tongue_guide = fkline.build_raw_guide()
                    # editing tongue base guide informations:
                    fkline.editGuideModuleName(tongueName)
                    cmds.setAttr(tongue_guide+".translateY", 19.85)
                    cmds.setAttr(tongue_guide+".translateZ", 1.45)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.35)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(tongue_guide+".nJoints", 2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.3)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(tongue_guide+".nJoints", 3)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.3)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.2)
                    cmds.setAttr(tongue_guide+".shapeSize", 0.4)
                    cmds.setAttr(tongue_guide+".deformedBy", 3)
                    # parent tongue guide to head guide:
                    cmds.parent(tongue_guide, head.cvChinLoc, absolute=True)
                    cmds.refresh()
                    
                    # working with Toes system:
                    self.ar.utils.setProgress(doingName+toeName)
                    # create toe1 module instance:
                    toe_1_guide = fkline.build_raw_guide()
                    # change name to toe:
                    fkline.editGuideModuleName(toeName+"_1")
                    # editing toe base guide informations:
                    cmds.setAttr(toe_1_guide+".shapeSize", 0.3)
                    cmds.setAttr(toe_1_guide+".translateX", 1)
                    cmds.setAttr(toe_1_guide+".translateY", 0.5)
                    cmds.setAttr(toe_1_guide+".translateZ", 2.7)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(toe_1_guide+".flip", 1)
                    fkline.displayAnnotation(0)
                    # parent toe1 guide to foot middle guide:
                    cmds.parent(toe_1_guide, foot.cvRFFLoc, absolute=True)
                    fkline.checkFatherMirror()
                    cmds.refresh()
                    
                    self.ar.utils.setProgress(doingName+toeName)
                    # create toe2 module instance:
                    toe_2_guide = fkline.build_raw_guide()
                    # change name to toe:
                    fkline.editGuideModuleName(toeName+"_2")
                    # editing toe base guide informations:
                    cmds.setAttr(toe_2_guide+".shapeSize", 0.3)
                    cmds.setAttr(toe_2_guide+".translateX", 1.35)
                    cmds.setAttr(toe_2_guide+".translateY", 0.5)
                    cmds.setAttr(toe_2_guide+".translateZ", 2.7)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(toe_2_guide+".flip", 1)
                    fkline.displayAnnotation(0)
                    # parent toe2 guide to foot middle guide:
                    cmds.parent(toe_2_guide, foot.cvRFFLoc, absolute=True)
                    fkline.checkFatherMirror()
                    cmds.refresh()
                    
                    self.ar.utils.setProgress(doingName+toeName)
                    # create toe3 module instance:
                    toe_3_guide = fkline.build_raw_guide()
                    # change name to toe:
                    fkline.editGuideModuleName(toeName+"_3")
                    # editing toe base guide informations:
                    cmds.setAttr(toe_3_guide+".shapeSize", 0.3)
                    cmds.setAttr(toe_3_guide+".translateX", 1.65)
                    cmds.setAttr(toe_3_guide+".translateY", 0.5)
                    cmds.setAttr(toe_3_guide+".translateZ", 2.7)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(toe_3_guide+".flip", 1)
                    fkline.displayAnnotation(0)
                    # parent toe3 guide to foot middle guide:
                    cmds.parent(toe_3_guide, foot.cvRFFLoc, absolute=True)
                    fkline.checkFatherMirror()
                    cmds.refresh()

                    self.ar.utils.setProgress(doingName+toeName)
                    # create toe4 module instance:
                    toe_4_guide = fkline.build_raw_guide()
                    # change name to toe:
                    fkline.editGuideModuleName(toeName+"_4")
                    # editing toe base guide informations:
                    cmds.setAttr(toe_4_guide+".shapeSize", 0.3)
                    cmds.setAttr(toe_4_guide+".translateX", 1.95)
                    cmds.setAttr(toe_4_guide+".translateY", 0.5)
                    cmds.setAttr(toe_4_guide+".translateZ", 2.7)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(toe_4_guide+".flip", 1)
                    fkline.displayAnnotation(0)
                    # parent toe4 guide to foot middle guide:
                    cmds.parent(toe_4_guide, foot.cvRFFLoc, absolute=True)
                    fkline.checkFatherMirror()
                    cmds.refresh()
                    
                    self.ar.utils.setProgress(doingName+toeName)
                    # create toe5 module instance:
                    toe_5_guide = fkline.build_raw_guide()
                    # change name to toe:
                    fkline.editGuideModuleName(toeName+"_5")
                    # editing toe base guide informations:
                    cmds.setAttr(toe_5_guide+".shapeSize", 0.3)
                    cmds.setAttr(toe_5_guide+".translateX", 2.25)
                    cmds.setAttr(toe_5_guide+".translateY", 0.5)
                    cmds.setAttr(toe_5_guide+".translateZ", 2.7)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(toe_5_guide+".flip", 1)
                    fkline.displayAnnotation(0)
                    # parent toe5 guide to foot middle guide:
                    cmds.parent(toe_5_guide, foot.cvRFFLoc, absolute=True)
                    fkline.checkFatherMirror()
                    cmds.refresh()
                    
                    # working with Breath system:
                    self.ar.utils.setProgress(doingName+breathName)
                    # create FkLine module instance:
                    breath_guide = single.build_raw_guide()
                    # editing breath base guide informations:
                    single.editGuideModuleName(breathName)
                    cmds.setAttr(breath_guide+".shapeSize", 0.3)
                    cmds.setAttr(breath_guide+".translateY", 14.5)
                    cmds.setAttr(breath_guide+".translateZ", 0.3)
                    cmds.setAttr(single.radiusCtrl+".translateX", 0.35)
                    cmds.setAttr(single.cvEndJoint+".translateZ", 0.2)
                    single.displayAnnotation(0)
                    # parent breath guide to chest guide:
                    cmds.parent(breath_guide, spine.cvLocator, absolute=True)
                    cmds.refresh()

                    # working with Belly system:
                    self.ar.utils.setProgress(doingName+bellyName)
                    # create FkLine module instance:
                    belly_guide = single.build_raw_guide()
                    # editing belly base guide informations:
                    single.editGuideModuleName(bellyName)
                    cmds.setAttr(belly_guide+".shapeSize", 0.3)
                    cmds.setAttr(belly_guide+".translateY", 11.75)
                    cmds.setAttr(belly_guide+".translateZ", 0.75)
                    cmds.setAttr(single.radiusCtrl+".translateX", 0.35)
                    cmds.setAttr(single.cvEndJoint+".translateZ", 0.2)
                    single.displayAnnotation(0)
                    # parent belly guide to chest guide:
                    cmds.parent(belly_guide, spine_guide, absolute=True)
                
                # Close progress window
                self.ar.utils.setProgress(endIt=True)
                
                # select spineGuide_Base:
                self.ar.data.collapse_edit_sel_mod = False
                cmds.select(spine_guide)
                print(self.ar.data.lang['m089_createdBiped'])
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(missing_modules) +'\";')
