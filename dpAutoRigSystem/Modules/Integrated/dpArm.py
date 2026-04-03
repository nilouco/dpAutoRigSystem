# importing libraries:
from maya import cmds
from maya import mel
from ..Base import dpBaseLibrary
from importlib import reload

# global variables to this module:    
CLASS_NAME = "Arm"
TITLE = "m028_arm"
DESCRIPTION = "m029_armDesc"
ICON = "/Icons/dp_arm.png"
WIKI = "03-‐-Guides#-arm"

DP_ARM_VERSION = 2.02


class Arm(dpBaseLibrary.BaseLibrary):
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
        self.check_modules = ['dpLimb', 'dpFinger']
        

    def build_template(self, *args):
        """ This function will create all guides needed to compose an arm.
        """
        # check modules integrity:
        missing_modules = self.ar.check_missing_modules(self.ar.data.standard_folder, self.check_modules)
        if not missing_modules:
            self.ar.data.collapse_edit_sel_mod = True
            
            # defining naming:
            arm = self.ar.data.lang['c037_arm'].capitalize()
            index = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m032_index']
            middle = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m033_middle']
            ring = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m034_ring']
            pinky = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m035_pinky']
            thumb = self.ar.data.lang['m007_finger']+"_"+self.ar.data.lang['m036_thumb']
            arm_guide_name = self.ar.data.lang['c037_arm']+" "+self.ar.data.lang['i205_guide']

            # Starting progress window
            maxProcess = 6 # number of modules to create
            self.ar.utils.setProgress(self.ar.data.lang['m094_doing'], arm_guide_name, maxProcess, addOne=False, addNumber=False)

            # creating arm:
            limb, arm_guide = self.ar.maker.set_new_guide("dpLimb", arm, t=(2.5, 16, 0), r=(90, 0, 90), annot=0, radius=1.5)
            cmds.setAttr(limb.cvExtremLoc+".translateZ", 7)
            limb.changeStyle(self.ar.data.lang['m026_biped'])

            # finger guides:
            finger_names = [thumb, index, middle, ring, pinky]
            tz_fingers = [0.72, 0.6, 0.2, -0.2, -0.6]
            for n, finger_name in enumerate(finger_names):
                finger, finger_guide = self.ar.maker.set_new_guide("dpFinger", finger_name, t=(11, 16, tz_fingers[n]), r=(90, 0, 90), annot=0, size=0.3, radius=0.3, parent=limb.cvExtremLoc)
                if n == 0: #thumb
                    cmds.setAttr(finger_guide+".translateY", 0.72)
                    cmds.setAttr(finger_guide+".translateZ", 0.6)
                    cmds.setAttr(finger_guide+".rotateX", -30)
                    finger.changeJointNumber(2)
            
            # Close progress window
            self.ar.utils.setProgress(endIt=True)
            # select the armGuide_Base:
            self.ar.data.collapse_edit_sel_mod = False
            cmds.select(arm_guide)
            print(self.ar.data.lang['m091_createdArm'])
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(missing_modules) +'\";')
