# importing libraries:
from maya import cmds
from maya import mel
from ..Base import dpBaseLibrary
from importlib import reload

# global variables to this module:    
CLASS_NAME = "Quadruped"
TITLE = "m037_quadruped"
DESCRIPTION = "m038_quadrupedDesc"
ICON = "/Icons/dp_quadruped.png"
WIKI = "03-‐-Guides#-quadruped"

DP_QUADRUPED_VERSION = 2.06


class Quadruped(dpBaseLibrary.BaseLibrary):
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
        self.check_modules = ['dpLimb', 'dpFoot', 'dpSpine', 'dpHead', 'dpFkLine', 'dpEye', 'dpNose', 'dpSingle']


    def build_template(self, *args):
        """ This function will create all guides needed to compose a quadruped.
        """
        # check modules integrity:
        guideDir = 'Modules.Standard'
        #standardDir = 'Modules/Standard'
        #checkModuleList = ['dpLimb', 'dpFoot', 'dpSpine', 'dpHead', 'dpFkLine', 'dpEye', 'dpNose', 'dpSingle']
        missing_modules = self.ar.check_missing_modules(self.ar.data.standard_folder, self.check_modules)
        
        if not missing_modules:
            self.ar.data.collapse_edit_sel_mod = True
            # defining naming:
            doingName = self.ar.data.lang['m094_doing']
            quadrupedStyleName = self.ar.data.lang['m037_quadruped']
            # part names:
            spineName = self.ar.data.lang['m011_spine']
            headName = self.ar.data.lang['c024_head']
            eyeName = self.ar.data.lang['c036_eye']
            legName = self.ar.data.lang['m030_leg'].capitalize()
            footName = self.ar.data.lang['c038_foot']
            earName = self.ar.data.lang['m040_ear']
            upperTeethName = self.ar.data.lang['m075_upperTeeth']
            upperTeethMiddleName = self.ar.data.lang['m075_upperTeeth']+self.ar.data.lang['c029_middle'].capitalize()
            upperTeethSideName = self.ar.data.lang['m075_upperTeeth']+self.ar.data.lang['c016_revFoot_G'].capitalize()
            lowerTeethName = self.ar.data.lang['m076_lowerTeeth']
            lowerTeethMiddleName = self.ar.data.lang['m076_lowerTeeth']+self.ar.data.lang['c029_middle'].capitalize()
            lowerTeethSideName = self.ar.data.lang['m076_lowerTeeth']+self.ar.data.lang['c016_revFoot_G'].capitalize()
            noseName = self.ar.data.lang['m078_nose']
            tongueName = self.ar.data.lang['m077_tongue']
            tailName = self.ar.data.lang['m039_tail']
            toeName = self.ar.data.lang['c013_revFoot_D'].capitalize()
            frontName = self.ar.data.lang['c056_front']
            backName = self.ar.data.lang['c057_back']
            simple   = self.ar.data.lang['i175_simple']
            complete = self.ar.data.lang['i176_complete']
            cancel   = self.ar.data.lang['i132_cancel']
            userMessage = self.ar.data.lang['i177_chooseMessage']
            breathName = self.ar.data.lang['c095_breath']
            bellyName = self.ar.data.lang['c096_belly']
            baseName = self.ar.data.lang['c106_base']
            upperName = self.ar.data.lang['c044_upper']
            lowerName = self.ar.data.lang['c045_lower']
            quadrupedGuideName = self.ar.data.lang['m037_quadruped']+" "+self.ar.data.lang['i205_guide']
            
            # getting Simple or Complete module guides to create:
            user_choice = self.ask_build_detail(self.title, simple, complete, cancel, complete, userMessage)
            if not user_choice == cancel:
                # number of modules to create:
                maxProcess = 22
                if user_choice == simple:
                    maxProcess = 8
                
                    
                # Starting progress window
                self.ar.utils.setProgress(self.ar.data.lang['m094_doing'], quadrupedGuideName, maxProcess, addOne=False, addNumber=False)

                # getting module instances:
                limb = self.ar.config.get_instance("dpLimb", [guideDir])
                foot = self.ar.config.get_instance("dpFoot", [guideDir])
                spine = self.ar.config.get_instance("dpSpine", [guideDir])
                head = self.ar.config.get_instance("dpHead", [guideDir])
                fkline = self.ar.config.get_instance("dpFkLine", [guideDir])
                eye = self.ar.config.get_instance("dpEye", [guideDir])
                nose = self.ar.config.get_instance("dpNose", [guideDir])
                single = self.ar.config.get_instance("dpSingle", [guideDir])

                # working with SPINE system:
                self.ar.utils.setProgress(doingName+spineName)
                # create spine module instance:
                #spine_guide = spine.build_raw_guide()
                spine, spine_guide = self.ar.maker.create_raw_guide("dpSpine")
                # editing spine base guide informations:
                spine.editGuideModuleName(spineName)
                cmds.setAttr(spine_guide+".translateY", 10)
                cmds.setAttr(spine_guide+".translateZ", -5)
                cmds.setAttr(spine_guide+".rotateX", 0)
                cmds.setAttr(spine_guide+".rotateY", 0)
                cmds.setAttr(spine_guide+".rotateZ", 90)
                cmds.setAttr(spine.cvLocator+".translateZ", 6)
                cmds.setAttr(spine.annotation+".translateX", 6)
                cmds.setAttr(spine.annotation+".translateY", 0)
                #spine.changeStyle(bipedStyleName)
                spine.changeStyle(quadrupedStyleName)
                cmds.refresh()
                
                # working with HEAD system:
                self.ar.utils.setProgress(doingName+headName)
                # create head module instance:
                head_guide = head.build_raw_guide()
                # editing head base guide informations:
                head.editGuideModuleName(headName)
                cmds.setAttr(head_guide+".translateY", 9.5)
                cmds.setAttr(head_guide+".translateZ", 5.5)
                cmds.setAttr(head_guide+".rotateX", 0)
                cmds.setAttr(head_guide+".rotateY", 45)
                cmds.setAttr(head_guide+".rotateZ", 90)
                cmds.setAttr(head.cvHeadLoc+".translateY", 5)
                cmds.setAttr(head.cvHeadLoc+".rotateX", -45)
                cmds.setAttr(head.cvUpperJawLoc+".translateY", 0.5)
                cmds.setAttr(head.cvUpperJawLoc+".translateZ", 1.3)
                cmds.setAttr(head.cvJawLoc+".translateY", -1.0)
                cmds.setAttr(head.cvJawLoc+".translateZ", 2.0)
                cmds.setAttr(head.cvJawLoc+".rotateY", 0)
                cmds.setAttr(head.cvLCornerLipLoc+".translateX", 0.6)
                cmds.setAttr(head.cvLCornerLipLoc+".translateY", -0.15)
                cmds.setAttr(head.cvLCornerLipLoc+".translateZ", 1.6)
                cmds.setAttr(head.cvUpperLipLoc+".translateY", -1.4)
                cmds.setAttr(head.cvUpperLipLoc+".translateZ", 3.5)
                cmds.setAttr(head.cvLowerLipLoc+".translateY", -0.2)
                cmds.setAttr(head.cvLowerLipLoc+".translateZ", 2.5)
                cmds.setAttr(head.annotation+".translateX", 4)
                cmds.setAttr(head.annotation+".translateY", 0)
                head.changeJointNumber(3)
                head.changeStyle(quadrupedStyleName)
                # parent head guide to chest guide:
                cmds.parent(head_guide, spine.cvLocator, absolute=True)
                cmds.refresh()
                
                # working with Eye system:
                self.ar.utils.setProgress(doingName+eyeName)
                # create eyeLookAt module instance:
                eye_guide = eye.build_raw_guide()
                # editing eyeLookAt base guide informations:
                eye.editGuideModuleName(eyeName)
                # setting X mirror:
                eye.changeMirror("X")
                cmds.setAttr(eye_guide+".translateX", 0.5)
                cmds.setAttr(eye_guide+".translateY", 13.5)
                cmds.setAttr(eye_guide+".translateZ", 11)
                cmds.setAttr(eye.annotation+".translateY", 3.5)
                cmds.setAttr(eye.radiusCtrl+".translateX", 0.5)
                cmds.setAttr(eye.cvEndJoint+".translateZ", 7)
                cmds.setAttr(eye_guide+".flip", 1)
                # parent head guide to spine guide:
                cmds.parent(eye_guide, head.cvUpperHeadLoc, absolute=True)
                cmds.refresh()
                
                # working with BACK LEG (B) system:
                self.ar.utils.setProgress(doingName+legName)
                # create back leg module instance:
                back_leg_guide = limb.build_raw_guide()
                # change limb guide to back leg type:
                limb.changeType(legName)
                # change limb guide to back leg style (quadruped):
                limb.changeStyle(quadrupedStyleName) 
                limb.changeNumBend(3)
                # change name to back leg:
                limb.editGuideModuleName(legName+backName)
                cmds.setAttr(limb.annotation+".translateY", -4)
                # editing back leg base guide informations:
                cmds.setAttr(back_leg_guide+".type", 1)
                cmds.setAttr(back_leg_guide+".translateX", 3)
                cmds.setAttr(back_leg_guide+".translateY", 9.5)
                cmds.setAttr(back_leg_guide+".translateZ", -6.5)
                cmds.setAttr(back_leg_guide+".rotateX", 0)
                # edit before, main and corners:
                cmds.setAttr(limb.cvBeforeLoc+".translateX", 1)
                cmds.setAttr(limb.cvBeforeLoc+".translateY", 0,5)
                cmds.setAttr(limb.cvBeforeLoc+".translateZ", -2.5)
                cmds.setAttr(limb.cvBeforeLoc+".rotateX", 20)
                cmds.setAttr(limb.cvBeforeLoc+".rotateY", 10)
                cmds.setAttr(limb.cvBeforeLoc+".rotateZ", -105)
                cmds.setAttr(limb.cvCornerLoc+".translateX", 0.7)
                cmds.setAttr(limb.cvCornerLoc+".translateZ", -0.7)
                # edit location of back leg ankle guide:
                cmds.setAttr(limb.cvExtremLoc+".translateZ", 8)
                # edit location of double back leg joint:
                cmds.setAttr(limb.cvCornerBLoc+".translateX", -2)
                # parent back leg guide to spine base guide:
                cmds.parent(back_leg_guide, spine_guide, absolute=True)
                # setting X mirror:
                limb.changeMirror("X")
                cmds.refresh()
                
                self.ar.utils.setProgress(doingName+footName)
                # create BACK FOOT (B) module instance:
                back_foot_guide = foot.build_raw_guide()
                foot.editGuideModuleName(footName+backName)
                cmds.setAttr(foot.annotation+".translateY", -3)
                cmds.setAttr(back_foot_guide+".translateX", 3)
                cmds.setAttr(back_foot_guide+".translateZ", -6.5)
                cmds.setAttr(foot.cvFootLoc+".translateZ", 1.5)
                cmds.setAttr(foot.cvRFALoc+".translateX", 0)
                cmds.setAttr(foot.cvRFBLoc+".translateX", 0)
                cmds.setAttr(foot.cvRFDLoc+".translateX", -1.5)
                cmds.setAttr(foot.cvRFFLoc+".translateZ", 1)
                # parent back foot guide to back leg ankle guide:
                cmds.parent(back_foot_guide, limb.cvExtremLoc, absolute=True)
                foot.checkFatherMirror()
                cmds.refresh()

                if user_choice == complete:
                    limb.setCorrective(1)
                    self.ar.utils.setProgress(doingName+toeName+backName)
                    # create toe1 module instance:
                    fkline, back_toe_1_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # change name to toe:
                    fkline.editGuideModuleName(toeName+backName+"_1")
                    # editing toe base guide informations:
                    cmds.setAttr(back_toe_1_guide+".shapeSize", 0.3)
                    cmds.setAttr(back_toe_1_guide+".translateX", 2.5)
                    cmds.setAttr(back_toe_1_guide+".translateY", 0.5)
                    cmds.setAttr(back_toe_1_guide+".translateZ", -5.33)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(back_toe_1_guide+".flip", 1)
                    fkline.displayAnnotation(0)
                    # parent toe1 guide to foot middle guide:
                    cmds.parent(back_toe_1_guide, foot.cvRFFLoc, absolute=True)
                    fkline.checkFatherMirror()
                    cmds.refresh()
                    
                    self.ar.utils.setProgress(doingName+toeName+backName)
                    # create toe2 module instance:
                    fkline, back_toe_2_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # change name to toe:
                    fkline.editGuideModuleName(toeName+backName+"_2")
                    # editing toe base guide informations:
                    cmds.setAttr(back_toe_2_guide+".shapeSize", 0.3)
                    cmds.setAttr(back_toe_2_guide+".translateX", 2.85)
                    cmds.setAttr(back_toe_2_guide+".translateY", 0.5)
                    cmds.setAttr(back_toe_2_guide+".translateZ", -5.33)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(back_toe_2_guide+".flip", 1)
                    fkline.displayAnnotation(0)
                    # parent toe2 guide to foot middle guide:
                    cmds.parent(back_toe_2_guide, foot.cvRFFLoc, absolute=True)
                    fkline.checkFatherMirror()
                    cmds.refresh()
                    
                    self.ar.utils.setProgress(doingName+toeName+backName)
                    # create toe3 module instance:
                    fkline, back_toe_3_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # change name to toe:
                    fkline.editGuideModuleName(toeName+backName+"_3")
                    # editing toe base guide informations:
                    cmds.setAttr(back_toe_3_guide+".shapeSize", 0.3)
                    cmds.setAttr(back_toe_3_guide+".translateX", 3.15)
                    cmds.setAttr(back_toe_3_guide+".translateY", 0.5)
                    cmds.setAttr(back_toe_3_guide+".translateZ", -5.33)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(back_toe_3_guide+".flip", 1)
                    fkline.displayAnnotation(0)
                    # parent toe3 guide to foot middle guide:
                    cmds.parent(back_toe_3_guide, foot.cvRFFLoc, absolute=True)
                    fkline.checkFatherMirror()
                    cmds.refresh()
                    
                    self.ar.utils.setProgress(doingName+toeName+backName)
                    # create toe4 module instance:
                    fkline, back_toe_4_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # change name to toe:
                    fkline.editGuideModuleName(toeName+backName+"_4")
                    # editing toe base guide informations:
                    cmds.setAttr(back_toe_4_guide+".shapeSize", 0.3)
                    cmds.setAttr(back_toe_4_guide+".translateX", 3.45)
                    cmds.setAttr(back_toe_4_guide+".translateY", 0.5)
                    cmds.setAttr(back_toe_4_guide+".translateZ", -5.33)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(back_toe_4_guide+".flip", 1)
                    fkline.displayAnnotation(0)
                    # parent toe4 guide to foot middle guide:
                    cmds.parent(back_toe_4_guide, foot.cvRFFLoc, absolute=True)
                    fkline.checkFatherMirror()
                    cmds.refresh()
                
                # working with FRONT LEG (A) system:
                self.ar.utils.setProgress(doingName+legName)
                # create front leg module instance:
                front_leg_guide = limb.build_raw_guide()
                # change limb guide to front leg type:
                limb.changeType(legName)
                # change limb guide to front leg style (biped):
                limb.changeStyle(quadrupedStyleName)
                limb.changeNumBend(3)
                # change name to front leg:
                limb.editGuideModuleName(legName+frontName)
                cmds.setAttr(limb.annotation+".translateY", -4)
                # editing front leg base guide informations:
                cmds.setAttr(front_leg_guide+".type", 1)
                cmds.setAttr(front_leg_guide+".translateX", 2.5)
                cmds.setAttr(front_leg_guide+".translateY", 8)
                cmds.setAttr(front_leg_guide+".translateZ", 5.5)
                cmds.setAttr(front_leg_guide+".rotateX", 0)
                # edit before, main and corners:
                cmds.setAttr(limb.cvBeforeLoc+".translateX", -0.75)
                cmds.setAttr(limb.cvBeforeLoc+".translateY", 0.5)
                cmds.setAttr(limb.cvBeforeLoc+".translateZ", -2.5)
                cmds.setAttr(limb.cvBeforeLoc+".rotateX", -15)
                cmds.setAttr(limb.cvBeforeLoc+".rotateY", 15)
                cmds.setAttr(limb.cvBeforeLoc+".rotateZ", -90)
                cmds.setAttr(limb.mainAic+".offsetY", -1)
                cmds.setAttr(limb.cvCornerLoc+".translateX", -2.0)
                cmds.setAttr(limb.cvCornerLoc+".translateZ", -0.6)
                # edit location of front leg ankle guide:
                cmds.setAttr(limb.cvExtremLoc+".translateZ", 6.5)
                # edit location of double front leg joint:
                cmds.setAttr(limb.cvCornerBLoc+".translateX", 1.75)
                cmds.setAttr(limb.cvCornerBLoc+".translateZ", 2.75)
                cmds.setAttr(limb.cvCornerBLoc+".rotateY", 10)
                # parent front leg guide to spine chest guide:
                cmds.parent(front_leg_guide, spine.cvLocator, absolute=True)
                # setting X mirror:
                limb.changeMirror("X")
                if user_choice == complete:
                    limb.setCorrective(1)
                cmds.refresh()

                self.ar.utils.setProgress(doingName+footName)
                # create FRONT FOOT (A) module instance:
                front_foot_guide = foot.build_raw_guide()
                foot.editGuideModuleName(footName+frontName)
                cmds.setAttr(foot.annotation+".translateY", -3)
                cmds.setAttr(front_foot_guide+".translateX", 2.5)
                cmds.setAttr(front_foot_guide+".translateZ", 5.5)
                cmds.setAttr(foot.cvFootLoc+".translateZ", 1.5)
                cmds.setAttr(foot.cvRFALoc+".translateX", 0)
                cmds.setAttr(foot.cvRFBLoc+".translateX", 0)
                cmds.setAttr(foot.cvRFDLoc+".translateX", -1.5)
                cmds.setAttr(foot.cvRFFLoc+".translateZ", 1)
                # parent front foot guide to front leg ankle guide:
                cmds.parent(front_foot_guide, limb.cvExtremLoc, absolute=True)
                foot.checkFatherMirror()
                cmds.refresh()
                
                if user_choice == complete:
                    limb.setCorrective(1)
                    self.ar.utils.setProgress(doingName+toeName+frontName)
                    # create toe1 module instance:
                    fkline, front_toe_1_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # change name to toe:
                    fkline.editGuideModuleName(toeName+frontName+"_1")
                    # editing toe base guide informations:
                    cmds.setAttr(front_toe_1_guide+".shapeSize", 0.3)
                    cmds.setAttr(front_toe_1_guide+".translateX", 2)
                    cmds.setAttr(front_toe_1_guide+".translateY", 0.5)
                    cmds.setAttr(front_toe_1_guide+".translateZ", 6.7)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(front_toe_1_guide+".flip", 1)
                    fkline.displayAnnotation(0)
                    # parent toe1 guide to foot middle guide:
                    cmds.parent(front_toe_1_guide, foot.cvRFFLoc, absolute=True)
                    fkline.checkFatherMirror()
                    cmds.refresh()
                    
                    self.ar.utils.setProgress(doingName+toeName+frontName)
                    # create toe2 module instance:
                    fkline, front_toe_2_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # change name to toe:
                    fkline.editGuideModuleName(toeName+frontName+"_2")
                    # editing toe base guide informations:
                    cmds.setAttr(front_toe_2_guide+".shapeSize", 0.3)
                    cmds.setAttr(front_toe_2_guide+".translateX", 2.35)
                    cmds.setAttr(front_toe_2_guide+".translateY", 0.5)
                    cmds.setAttr(front_toe_2_guide+".translateZ", 6.7)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(front_toe_2_guide+".flip", 1)
                    fkline.displayAnnotation(0)
                    # parent toe2 guide to foot middle guide:
                    cmds.parent(front_toe_2_guide, foot.cvRFFLoc, absolute=True)
                    fkline.checkFatherMirror()
                    cmds.refresh()
                    
                    self.ar.utils.setProgress(doingName+toeName+frontName)
                    # create toe3 module instance:
                    fkline, front_toe_3_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # change name to toe:
                    fkline.editGuideModuleName(toeName+frontName+"_3")
                    # editing toe base guide informations:
                    cmds.setAttr(front_toe_3_guide+".shapeSize", 0.3)
                    cmds.setAttr(front_toe_3_guide+".translateX", 2.65)
                    cmds.setAttr(front_toe_3_guide+".translateY", 0.5)
                    cmds.setAttr(front_toe_3_guide+".translateZ", 6.7)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(front_toe_3_guide+".flip", 1)
                    fkline.displayAnnotation(0)
                    # parent toe31 guide to foot middle guide:
                    cmds.parent(front_toe_3_guide, foot.cvRFFLoc, absolute=True)
                    fkline.checkFatherMirror()
                    cmds.refresh()

                    self.ar.utils.setProgress(doingName+toeName+frontName)
                    # create toe4 module instance:
                    fkline, front_toe_4_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # change name to toe:
                    fkline.editGuideModuleName(toeName+frontName+"_4")
                    # editing toe base guide informations:
                    cmds.setAttr(front_toe_4_guide+".shapeSize", 0.3)
                    cmds.setAttr(front_toe_4_guide+".translateX", 2.95)
                    cmds.setAttr(front_toe_4_guide+".translateY", 0.5)
                    cmds.setAttr(front_toe_4_guide+".translateZ", 6.7)
                    fkline.changeJointNumber(2)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    fkline.changeJointNumber(3)
                    cmds.setAttr(fkline.cvJointLoc+".translateZ", 0.25)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.2)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(front_toe_4_guide+".flip", 1)
                    fkline.displayAnnotation(0)
                    # parent toe4 guide to foot middle guide:
                    cmds.parent(front_toe_4_guide, foot.cvRFFLoc, absolute=True)
                    fkline.checkFatherMirror()
                    cmds.refresh()



                # working with TAIL system:
                self.ar.utils.setProgress(doingName+tailName)
                # create FkLine module instance:
                fkline, tail_guide = self.ar.maker.create_raw_guide("dpFkLine")
                # editing tail base guide informations:
                fkline.editGuideModuleName(tailName)
                cmds.setAttr(tail_guide+".translateY", 9.8)
                cmds.setAttr(tail_guide+".translateZ", -7.6)
                cmds.setAttr(tail_guide+".rotateX", 180)
                cmds.setAttr(tail_guide+".rotateY", 20)
                cmds.setAttr(tail_guide+".rotateZ", 90)
                cmds.setAttr(fkline.annotation+".translateX", 4)
                cmds.setAttr(fkline.annotation+".translateY", 0)
                cmds.setAttr(fkline.radiusCtrl+".translateX", 1)
                cmds.setAttr(tail_guide+".mainControls", 1)
                # change the number of joints to the tail module:
                fkline.changeJointNumber(3)
                
                if user_choice == simple:
                    # parent tail guide to spine guide:
                    cmds.parent(tail_guide, spine_guide, absolute=True)
                
                #
                # complete part:
                #
                if user_choice == complete:
                    
                    # working with TAIL system:
                    self.ar.utils.setProgress(doingName+tailName+baseName)
                    # create FkLine module instance:
                    fkline, tail_base_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # editing tail base guide informations:
                    fkline.editGuideModuleName(tailName+baseName)
                    cmds.setAttr(tail_base_guide+".translateY", 10.0)
                    cmds.setAttr(tail_base_guide+".translateZ", -7)
                    cmds.setAttr(tail_base_guide+".rotateX", 180)
                    cmds.setAttr(tail_base_guide+".rotateZ", 90)
                    cmds.setAttr(fkline.annotation+".translateX", 4)
                    cmds.setAttr(fkline.annotation+".translateY", 0)
                    # parent tail base guide to spine guide:
                    cmds.parent(tail_base_guide, spine_guide, absolute=True)
                    # parent tail guide to tail base guide:
                    cmds.parent(tail_guide, tail_base_guide, absolute=True)
                    cmds.refresh()

                    # set guides attributes to complete system
                    head.changeDeformer(1)
                    head.changeFacial(1)
                    eye.setCorrective(1)
                    
                    # working with EAR system:
                    self.ar.utils.setProgress(doingName+earName)
                    # create FkLine module instance:
                    fkline, ear_base_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # editing ear base guide informations:
                    fkline.editGuideModuleName(earName+baseName)
                    cmds.setAttr(ear_base_guide+".translateX", 0.11)
                    cmds.setAttr(ear_base_guide+".translateY", 14)
                    cmds.setAttr(ear_base_guide+".translateZ", 10)
                    cmds.setAttr(ear_base_guide+".rotateX", 90)
                    cmds.setAttr(ear_base_guide+".rotateY", 20)
                    cmds.setAttr(ear_base_guide+".rotateZ", 127)
                    cmds.setAttr(fkline.annotation+".translateX", 4)
                    cmds.setAttr(fkline.annotation+".translateY", 0)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.5)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.5)
                    cmds.setAttr(ear_base_guide+".deformedBy", 1)
                    cmds.setAttr(ear_base_guide+".flip", 1)
                    fkline.changeMirror("X")
                    cmds.parent(ear_base_guide, head.cvUpperHeadLoc, absolute=True)

                    self.ar.utils.setProgress(doingName+earName)
                    # create FkLine module instance:
                    fkline, ear_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # editing ear base guide informations:
                    fkline.editGuideModuleName(earName)
                    cmds.setAttr(ear_guide+".translateX", 0.8)
                    cmds.setAttr(ear_guide+".translateY", 14.5)
                    cmds.setAttr(ear_guide+".translateZ", 10)
                    cmds.setAttr(ear_guide+".rotateX", 90)
                    cmds.setAttr(ear_guide+".rotateY", 20)
                    cmds.setAttr(ear_guide+".rotateZ", 127)
                    cmds.setAttr(fkline.annotation+".translateX", 4)
                    cmds.setAttr(fkline.annotation+".translateY", 0)
                    cmds.setAttr(fkline.annotation+".translateZ", 1.4)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 1)
                    cmds.setAttr(ear_guide+".mainControls", 1)
                    cmds.setAttr(ear_guide+".deformedBy", 1)
                    cmds.setAttr(ear_guide+".scaleX", 0.5)
                    cmds.setAttr(ear_guide+".scaleY", 0.5)
                    cmds.setAttr(ear_guide+".scaleZ", 0.5)
                    # change the number of joints to the ear module:
                    fkline.changeJointNumber(2)
                    cmds.setAttr(ear_guide+".flip", 1)
                    fkline.changeMirror("X")
                    cmds.parent(ear_guide, ear_base_guide, absolute=True)
                    ear_cv_joint_loc = fkline.cvJointLoc

                    self.ar.utils.setProgress(doingName+upperName+earName)
                    # create FkLine module instance:
                    fkline, upper_ear_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # editing ear upper guide informations:
                    fkline.editGuideModuleName(upperName+earName)
                    cmds.setAttr(upper_ear_guide+".translateX", 1.401)
                    cmds.setAttr(upper_ear_guide+".translateY", 15.365)
                    cmds.setAttr(upper_ear_guide+".translateZ", 9.88)
                    cmds.setAttr(upper_ear_guide+".rotateX", 90)
                    cmds.setAttr(upper_ear_guide+".rotateY", 20)
                    cmds.setAttr(upper_ear_guide+".rotateZ", 127)
                    cmds.setAttr(fkline.annotation+".translateX", 4)
                    cmds.setAttr(fkline.annotation+".translateY", 0)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.3)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.5)
                    cmds.setAttr(upper_ear_guide+".scaleX", 0.4)
                    cmds.setAttr(upper_ear_guide+".scaleY", 0.4)
                    cmds.setAttr(upper_ear_guide+".scaleZ", 0.4)
                    cmds.setAttr(upper_ear_guide+".deformedBy", 1)
                    cmds.setAttr(upper_ear_guide+".flip", 1)
                    fkline.changeMirror("X")
                    cmds.parent(upper_ear_guide, ear_cv_joint_loc, absolute=True)
                    
                    self.ar.utils.setProgress(doingName+lowerName+earName)
                    # create FkLine module instance:
                    fkline, lower_ear_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # editing ear upper guide informations:
                    fkline.editGuideModuleName(lowerName+earName)
                    cmds.setAttr(lower_ear_guide+".translateX", 1.796)
                    cmds.setAttr(lower_ear_guide+".translateY", 14.839)
                    cmds.setAttr(lower_ear_guide+".translateZ", 10.12)
                    cmds.setAttr(lower_ear_guide+".rotateX", 90)
                    cmds.setAttr(lower_ear_guide+".rotateY", 20)
                    cmds.setAttr(lower_ear_guide+".rotateZ", 127)
                    cmds.setAttr(fkline.annotation+".translateX", 4)
                    cmds.setAttr(fkline.annotation+".translateY", 0)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.3)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.5)
                    cmds.setAttr(lower_ear_guide+".scaleX", 0.4)
                    cmds.setAttr(lower_ear_guide+".scaleY", 0.4)
                    cmds.setAttr(lower_ear_guide+".scaleZ", 0.4)
                    cmds.setAttr(lower_ear_guide+".deformedBy", 1)
                    cmds.setAttr(lower_ear_guide+".flip", 1)
                    fkline.changeMirror("X")
                    cmds.parent(lower_ear_guide, ear_cv_joint_loc, absolute=True)
                    cmds.refresh()

                    # working with Teeth system:
                    self.ar.utils.setProgress(doingName+upperTeethName)
                    # create FkLine module instance:
                    fkline, upper_teeth_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # editing upperTeeth base guide informations:
                    fkline.editGuideModuleName(upperTeethName)
                    cmds.setAttr(upper_teeth_guide+".translateY", 12.5)
                    cmds.setAttr(upper_teeth_guide+".translateZ", 12.7)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.5)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.1)
                    cmds.setAttr(upper_teeth_guide+".shapeSize", 0.5)
                    cmds.setAttr(upper_teeth_guide+".deformedBy", 3)
                    upper_teeth_cv_joint_loc = fkline.cvJointLoc
                    # create FkLine module instance:
                    fkline, upper_teeth_middle_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # editing upperTeethMiddle base guide informations:
                    fkline.editGuideModuleName(upperTeethMiddleName)
                    cmds.setAttr(upper_teeth_middle_guide+".translateY", 12.3)
                    cmds.setAttr(upper_teeth_middle_guide+".translateZ", 12.7)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.1)
                    cmds.setAttr(upper_teeth_middle_guide+".shapeSize", 0.3)
                    cmds.setAttr(upper_teeth_middle_guide+".deformedBy", 3)
                    fkline.displayAnnotation(0)
                    # parent upperTeethMiddle guide to upperTeeth guide:
                    cmds.parent(upper_teeth_middle_guide, upper_teeth_cv_joint_loc, absolute=True)
                    # create FkLine module instance:
                    fkline, upper_teeth_side_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # editing upperTeethSide base guide informations:
                    fkline.editGuideModuleName(upperTeethSideName)
                    cmds.setAttr(upper_teeth_side_guide+".translateX", 0.2)
                    cmds.setAttr(upper_teeth_side_guide+".translateY", 12.3)
                    cmds.setAttr(upper_teeth_side_guide+".translateZ", 12.3)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.1)
                    cmds.setAttr(upper_teeth_side_guide+".shapeSize", 0.3)
                    cmds.setAttr(upper_teeth_side_guide+".deformedBy", 3)
                    cmds.setAttr(upper_teeth_side_guide+".flip", 1)
                    fkline.changeMirror("X")
                    fkline.displayAnnotation(0)
                    # parent upperTeethSide guide to upperTeeth guide:
                    cmds.parent(upper_teeth_side_guide, upper_teeth_cv_joint_loc, absolute=True)
                    # create FkLine module instance:
                    fkline, lower_teeth_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # editing lowerTeeth base guide informations:
                    fkline.editGuideModuleName(lowerTeethName)
                    cmds.setAttr(lower_teeth_guide+".translateY", 11.7)
                    cmds.setAttr(lower_teeth_guide+".translateZ", 12.7)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.5)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.1)
                    cmds.setAttr(lower_teeth_guide+".shapeSize", 0.5)
                    cmds.setAttr(lower_teeth_guide+".deformedBy", 3)
                    lower_teeth_cv_joint_loc = fkline.cvJointLoc
                    # parent lowerTeeth guide to head guide:
                    cmds.parent(lower_teeth_guide, head.cvChinLoc, absolute=True)
                    # create FkLine module instance:
                    fkline, lower_teeth_middle_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # editing lowerTeethMiddle base guide informations:
                    fkline.editGuideModuleName(lowerTeethMiddleName)
                    cmds.setAttr(lower_teeth_middle_guide+".translateY", 11.9)
                    cmds.setAttr(lower_teeth_middle_guide+".translateZ", 12.7)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.1)
                    cmds.setAttr(lower_teeth_middle_guide+".shapeSize", 0.3)
                    cmds.setAttr(lower_teeth_middle_guide+".deformedBy", 3)
                    fkline.displayAnnotation(0)
                    # parent lowerTeeth guide to lowerTeeth guide:
                    cmds.parent(lower_teeth_middle_guide, lower_teeth_cv_joint_loc, absolute=True)
                    # create FkLine module instance:
                    fkline, lower_teeth_side_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # editing lowerTeethSide base guide informations:
                    fkline.editGuideModuleName(lowerTeethSideName)
                    cmds.setAttr(lower_teeth_side_guide+".translateX", 0.2)
                    cmds.setAttr(lower_teeth_side_guide+".translateY", 11.9)
                    cmds.setAttr(lower_teeth_side_guide+".translateZ", 12.3)
                    cmds.setAttr(fkline.radiusCtrl+".translateX", 0.2)
                    cmds.setAttr(fkline.cvEndJoint+".translateZ", 0.1)
                    cmds.setAttr(lower_teeth_side_guide+".shapeSize", 0.3)
                    cmds.setAttr(lower_teeth_side_guide+".deformedBy", 3)
                    cmds.setAttr(lower_teeth_side_guide+".flip", 1)
                    fkline.changeMirror("X")
                    fkline.displayAnnotation(0)
                    # parent lowerTeethSide guide to lowerTeeth guide:
                    cmds.parent(lower_teeth_side_guide, lower_teeth_cv_joint_loc, absolute=True)
                    cmds.refresh()
                    
                    # working with Tongue system:
                    self.ar.utils.setProgress(doingName+tongueName)
                    # create FkLine module instance:
                    fkline, tongue_guide = self.ar.maker.create_raw_guide("dpFkLine")
                    # editing tongue base guide informations:
                    fkline.editGuideModuleName(tongueName)
                    cmds.setAttr(tongue_guide+".translateY", 12)
                    cmds.setAttr(tongue_guide+".translateZ", 12)
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
                    
                    # working with Nose system:
                    self.ar.utils.setProgress(doingName+noseName)
                    # create Nose module instance:
                    nose_guide = nose.build_raw_guide()
                    # editing upperTeeth base guide informations:
                    nose.editGuideModuleName(noseName)
                    cmds.setAttr(nose_guide+".translateY", 13)
                    cmds.setAttr(nose_guide+".translateZ", 11.5)
                    cmds.setAttr(nose.radiusCtrl+".translateX", 0.3)
                    cmds.setAttr(nose.cvTopLoc+".rotateX", 25)
                    nose.changeJointNumber(2)
                    cmds.setAttr(nose.cvTopLoc+".translateY", 0.1)
                    cmds.setAttr(nose.cvTopLoc+".translateZ", 0.7)
                    cmds.setAttr(nose.cvTopLoc+".rotateX", -17)
                    cmds.setAttr(nose.cvMiddleLoc+".translateY", 0.3)
                    cmds.setAttr(nose.cvMiddleLoc+".translateZ", 1.3)
                    cmds.setAttr(nose.cvMiddleLoc+".rotateX", -25)
                    cmds.setAttr(nose_guide+".shapeSize", 0.5)
                    # parent nose guide and upperTeeth to head guide:
                    cmds.parent(upper_teeth_guide, nose_guide, absolute=True)
                    cmds.parent(nose_guide, head.cvUpperJawLoc, absolute=True)
                    cmds.refresh()
                    
                    self.ar.utils.setProgress(doingName+breathName)
                    # create breath module instance:
                    breath_guide = single.build_raw_guide()
                    # change name to breath:
                    single.editGuideModuleName(breathName)
                    # editing breath base guide informations:
                    cmds.setAttr(single.radiusCtrl+".translateX", 0.8)
                    cmds.setAttr(breath_guide+".translateY", 7)
                    cmds.setAttr(breath_guide+".translateZ", 4)
                    # parent breath guide to spine chest guide:
                    cmds.parent(breath_guide, spine.cvLocator, absolute=True)
                    cmds.refresh()

                    self.ar.utils.setProgress(doingName+bellyName)
                    # create belly module instance:
                    belly_guide = single.build_raw_guide()
                    # change name to belly:
                    single.editGuideModuleName(bellyName)
                    # editing belly base guide informations:
                    cmds.setAttr(single.radiusCtrl+".translateX", 0.8)
                    cmds.setAttr(belly_guide+".translateY", 8.5)
                    cmds.setAttr(belly_guide+".translateZ", -3.5)
                    # parent breath guide to spine chest guide:
                    cmds.parent(belly_guide, spine_guide, absolute=True)
                
                # Close progress window
                self.ar.utils.setProgress(endIt=True)
                
                # select spineGuide_Base:
                self.ar.data.collapse_edit_sel_mod = False
                cmds.select(spine_guide)
                print(self.ar.data.lang['m090_createdQuadruped'])

#
#
# TEST TODO:
#                print("TESTING HERE filling guides 1")
#                self.ar.filler.fill_created_guides()
#                print("TESTING HERE filling guides 2")

        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(missing_modules) +'\";')
