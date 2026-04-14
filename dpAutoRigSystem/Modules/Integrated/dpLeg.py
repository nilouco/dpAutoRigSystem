# importing libraries:
from maya import cmds
from maya import mel
from ..Base import dpBaseLibrary
from importlib import reload

# global variables to this module:    
CLASS_NAME = "Leg"
TITLE = "m030_leg"
DESCRIPTION = "m031_legDesc"
ICON = "/Icons/dp_leg.png"
WIKI = "03-‐-Guides#-leg"

DP_LEG_VERSION = 2.02


class Leg(dpBaseLibrary.BaseLibrary):
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
        self.check_modules = ['dpLimb', 'dpFoot', 'dpFkLine']


    def build_template(self, *args):
        """ This function will create all guides needed to compose a leg.
        """
        # check modules integrity:
        guideDir = 'Modules.Standard'
        standardDir = 'Modules/Standard'
        checkModuleList = ['dpLimb', 'dpFoot', 'dpFkLine']
        missing_modules = self.ar.ui_manager.check_missing_modules(self.ar.data.standard_folder, self.check_modules)
        
        if not missing_modules:
            self.ar.data.collapse_edit_sel_mod = True
            # defining naming:
            doingName = self.ar.data.lang['m094_doing']
            # part names:
            legName = self.ar.data.lang['m030_leg'].capitalize()
            footName = self.ar.data.lang['c038_foot']
            toeName = self.ar.data.lang['c013_revFoot_D'].capitalize()
            simple   = self.ar.data.lang['i175_simple']
            complete = self.ar.data.lang['i176_complete']
            cancel   = self.ar.data.lang['i132_cancel']
            userMessage = self.ar.data.lang['i177_chooseMessage']
            legGuideName = self.ar.data.lang['m030_leg']+" "+self.ar.data.lang['i205_guide']
            
            # getting Simple or Complete module guides to create:
            user_choice = self.ask_build_detail(self.title, simple, complete, cancel, simple, userMessage)
            if not user_choice == cancel:
                # number of modules to create:
                maxProcess = 7
                if user_choice == simple:
                    maxProcess = 2
                
                    
                # Starting progress window
                self.ar.utils.setProgress(self.ar.data.lang['m094_doing'], legGuideName, maxProcess, addOne=False, addNumber=False)

                # getting module instances:
                limb = self.ar.config.get_instance("dpLimb", [guideDir])
                foot = self.ar.config.get_instance("dpFoot", [guideDir])
                fkline = self.ar.config.get_instance("dpFkLine", [guideDir])
                
                self.ar.utils.setProgress(doingName+legName)
                # create leg module instance:
                leg_guide = limb.build_raw_guide()
                # change limb guide to leg type:
                limb.changeType(legName)
                # change name to leg:
                limb.editGuideModuleName(legName)
                # editing leg base guide informations:
                cmds.setAttr(leg_guide+".type", 1)
                cmds.setAttr(leg_guide+".translateX", 1.5)
                cmds.setAttr(leg_guide+".translateY", 10)
                cmds.setAttr(leg_guide+".rotateX", 0)
                cmds.setAttr(limb.radiusCtrl+".translateX", 1.5)
                limb.changeStyle(self.ar.data.lang['m026_biped'])
                # edit location of leg ankle guide:
                cmds.setAttr(limb.cvExtremLoc+".translateZ", 8.5)
                cmds.refresh()
                
                self.ar.utils.setProgress(doingName+footName)
                # create foot module instance:
                foot_guide = foot.build_raw_guide()
                foot.editGuideModuleName(footName)
                cmds.setAttr(foot_guide+".translateX", 1.5)
                cmds.setAttr(foot.cvFootLoc+".translateZ", 1.5)
                # parent foot guide to leg ankle guide:
                cmds.parent(foot_guide, limb.cvExtremLoc, absolute=True)
                cmds.refresh()
                
                #
                # complete part:
                #
                if user_choice == complete:
                    
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
                    cmds.refresh()
                
                # Close progress window
                self.ar.utils.setProgress(endIt=True)

                # select the legGuide_Base:
                self.ar.data.collapse_edit_sel_mod = False
                cmds.select(leg_guide)
                print(self.ar.data.lang['m092_createdLeg'])
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(missing_modules) +'\";')
