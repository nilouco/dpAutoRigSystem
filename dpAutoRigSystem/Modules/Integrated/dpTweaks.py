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
        # dependence module list:
        self.check_modules = ['dpSingle']


    def build_template(self, *args):
        """ This function will create all guides needed to compose a good facial tweaks controls with integrated Single modules using indirect skinning.
        """
        # check modules integrity:
        guideDir = 'Modules.Standard'
        standardDir = 'Modules/Standard'
        checkModuleList = ['dpSingle']
        missing_modules = self.ar.ui_manager.check_missing_modules(self.ar.data.standard_folder, self.check_modules)
        
        if not missing_modules:
            self.ar.data.collapse_edit_sel_mod = True
            # defining naming:
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
            user_choice = self.ask_build_detail(self.title, simple, complete, cancel, complete, userMessage)
            if not user_choice == cancel:
                # number of modules to create:
                maxProcess = 37
                if user_choice == simple:
                    maxProcess = 14
                
                
                # getting Indirect Skinning user prefer:
                userIndirectSkin = self.ask_build_detail(self.title, indSkin, faceJoint, cancel, indSkin, faceMessage)
                if not userIndirectSkin == cancel:
                    if userIndirectSkin == indSkin:
                        self.indSkinValue = 1
                    else:
                        self.indSkinValue = 0
                
                    # Starting progress window
                    self.ar.utils.setProgress(self.ar.data.lang['m094_doing'], tweaksGuideName, maxProcess, addOne=False, addNumber=False)
                    
                    # getting module instances:
                    self.single = self.ar.config.get_instance("dpSingle", [guideDir])

                    # creating guides:
                    holder_main_guide = self.setTweak(holderMainName, radius=2, mirror=None)
                    cmds.setAttr(holder_main_guide+".holder", 1)
                    # brows
                    brow_main_guide = self.setTweak(eyebrowMainName, tx=0.65, ty=2.8, tz=2, radius=0.3, deformed=1, mirror="X")
                    brow_1_guide = self.setTweak(eyebrowName1, tx=0.45, ty=2.8, tz=2.1, mirror="X")
                    brow_2_guide = self.setTweak(eyebrowName2, tx=0.65, ty=2.85, tz=2.1, mirror="X")
                    brow_3_guide = self.setTweak(eyebrowName3, tx=0.85, ty=2.8, tz=2.1, mirror="X")
                    cmds.refresh()
                    # lips
                    lip_main_guide = self.setTweak(lipMainName, ty=1, tz=1, radius=0.3, mirror=None, deformed=3)
                    upper_lip_middle_guide = self.setTweak(upperLipMiddleName, ty=1.1, tz=2.5, mirror=None)
                    upper_lip_1_guide = self.setTweak(upperLipName1, tx=0.2, ty=1.07, tz=2.5, mirror="X")
                    upper_lip_2_guide = self.setTweak(upperLipName2, tx=0.4, ty=1.05, tz=2.5, mirror="X")
                    lower_lip_middle_guide = self.setTweak(lowerLipMiddleName, ty=0.9, tz=2.5, mirror=None)
                    lower_lip_1_guide = self.setTweak(lowerLipName1, tx=0.2, ty=0.93, tz=2.5, mirror="X")
                    lower_lip_2_guide = self.setTweak(lowerLipName2, tx=0.4, ty=0.95, tz=2.5, mirror="X")
                    lip_corner_guide = self.setTweak(lipCornerName, tx=0.55, ty=1, tz=2.5, mirror="X")
                    cmds.refresh()
                    
                    if user_choice == complete:
                        brow_middle_guide = self.setTweak(eyebrowMiddleName, ty=2.8, tz=2, mirror=None)
                        brow_4_guide = self.setTweak(eyebrowName4, tx=1.05, ty=2.7, tz=2.1, mirror="X")
                        # eyelids, eyesockets
                        if userIndirectSkin == indSkin:
                            eyelid_main_guide = self.setTweak(eyelidMainName, tx=0.5, ty=2, tz=1.3, radius=0.3, deformed=1, mirror="X")
                            upper_eyelid_0_guide = self.setTweak(upperEyelidName0, tx=0.33, ty=2.1, tz=1.8, mirror="X")
                            upper_eyelid_1_guide = self.setTweak(upperEyelidName1, tx=0.5, ty=2.14, tz=1.8, mirror="X")
                            upper_eyelid_2_guide = self.setTweak(upperEyelidName2, tx=0.67, ty=2.1, tz=1.8, mirror="X")
                            lower_eyelid_0_guide = self.setTweak(lowerEyelidName0, tx=0.33, ty=1.9, tz=1.8, mirror="X")
                            lower_eyelid_1_guide = self.setTweak(lowerEyelidName1, tx=0.5, ty=1.86, tz=1.8, mirror="X")
                            lower_eyelid_2_guide = self.setTweak(lowerEyelidName2, tx=0.67, ty=1.9, tz=1.8, mirror="X")
                            eyelid_corner_0_guide = self.setTweak(eyelidCornerName0, tx=0.2, ty=2, tz=1.8, mirror="X")
                            eyelid_corner_1_guide = self.setTweak(eyelidCornerName1, tx=0.8, ty=2, tz=1.8, mirror="X")
                            upper_eyesocket_0_guide = self.setTweak(upperEyeSocketName0, tx=0.25, ty=2.25, tz=1.8, mirror="X")
                            upper_eyesocket_1_guide = self.setTweak(upperEyeSocketName1, tx=0.5, ty=2.3, tz=1.8, mirror="X")
                            upper_eyesocket_2_guide = self.setTweak(upperEyeSocketName2, tx=0.75, ty=2.25, tz=1.8, mirror="X")
                            lower_eyesocket_0_guide = self.setTweak(lowerEyeSocketName0, tx=0.25, ty=1.75, tz=1.8, mirror="X")
                            lower_eyesocket_1_guide = self.setTweak(lowerEyeSocketName1, tx=0.5, ty=1.7, tz=1.8, mirror="X")
                            lower_eyesocket_2_guide = self.setTweak(lowerEyeSocketName2, tx=0.75, ty=1.75, tz=1.8, mirror="X")
                        cmds.refresh()
                        # squint
                        squint_main_guide = self.setTweak(squintMainName, tx=0.5, ty=1.4, tz=1.6, radius=0.3, deformed=1, mirror="X")
                        squint_1_guide = self.setTweak(squintName1, tx=0.32, ty=1.47, tz=2.02, mirror="X")
                        squint_2_guide = self.setTweak(squintName2, tx=0.57, ty=1.36, tz=1.95, mirror="X")
                        squint_3_guide = self.setTweak(squintName3, tx=0.86, ty=1.39, tz=1.8, mirror="X")
                        cheek_1_guide = self.setTweak(cheekName1, tx=1.1, ty=0.9, tz=2.1, mirror="X")
                        cheek_2_guide = self.setTweak(cheekName2, tx=0.8, ty=1.15, tz=2.3, mirror="X")
                    
                    cmds.refresh()
                    self.ar.utils.setProgress(self.ar.data.lang['m094_doing']+" hierarchy")
                    
                    # working on hierarchy
                    cmds.parent([brow_main_guide, lip_main_guide], holder_main_guide, absolute=True)
                    cmds.parent([upper_lip_middle_guide, upper_lip_1_guide, upper_lip_2_guide, lower_lip_middle_guide, lower_lip_1_guide, lower_lip_2_guide, lip_corner_guide], lip_main_guide, absolute=True)
                    
                    if user_choice == complete:
                        cmds.parent([brow_middle_guide, squint_main_guide, cheek_1_guide, cheek_2_guide], holder_main_guide, absolute=True)
                        cmds.parent([squint_1_guide, squint_2_guide, squint_3_guide], squint_main_guide, absolute=True)
                        cmds.parent([brow_1_guide, brow_2_guide, brow_3_guide, brow_4_guide], brow_main_guide, absolute=True)
                        if userIndirectSkin == indSkin:
                            cmds.parent(eyelid_main_guide, holder_main_guide, absolute=True)
                            cmds.parent([upper_eyelid_0_guide, upper_eyelid_1_guide, upper_eyelid_2_guide, lower_eyelid_0_guide, lower_eyelid_1_guide, lower_eyelid_2_guide, eyelid_corner_0_guide, eyelid_corner_1_guide, upper_eyesocket_0_guide, upper_eyesocket_1_guide, upper_eyesocket_2_guide, lower_eyesocket_0_guide, lower_eyesocket_1_guide, lower_eyesocket_2_guide], eyelid_main_guide, absolute=True)
                    else:
                        cmds.parent([brow_1_guide, brow_2_guide, brow_3_guide], brow_main_guide, absolute=True)
                            
                    # try to parent to HEAD guide or control
                    if cmds.objExists("*__*:Guide_Head"):
                        if cmds.objExists("*__*:Guide_UpperJaw"):
                            cmds.parent(holder_main_guide, cmds.ls("*__*:Guide_Head")[0], relative=True)
                            cmds.parent(holder_main_guide, cmds.ls("*__*:Guide_UpperJaw")[0], relative=False)
                        else:
                            cmds.parent(holder_main_guide, cmds.ls("*__*:Guide_Head")[0], relative=True)
                    elif cmds.objExists("Head_UpperJaw_Ctrl"):
                        cmds.parent(holder_main_guide, "Head_UpperJaw_Ctrl", relative=True)
                    
                    # Close progress window
                    self.ar.utils.setProgress(endIt=True)

                    self.ar.data.collapse_edit_sel_mod = False
                    cmds.select(holder_main_guide)
                    print(self.ar.data.lang['m093_createdTweaks'])
        else:
            # error checking modules in the folder:
            mel.eval('error \"'+ self.ar.data.lang['e001_guideNotChecked'] +' - '+ (", ").join(missing_modules) +'\";')


    def setTweak(self, name, tx=0, ty=0, tz=0, radius=0.05, end=0.1, mirror="X", deformed=0):
        self.ar.utils.setProgress(self.ar.data.lang['m094_doing']+name)
        guide = self.single.build_raw_guide()
        self.single.editGuideModuleName(name)
        cmds.setAttr(self.single.radiusCtrl+".translateX", radius)
        cmds.setAttr(self.single.cvEndJoint+".translateZ", end)
        cmds.setAttr(guide+".translateX", tx)
        cmds.setAttr(guide+".translateY", ty)
        cmds.setAttr(guide+".translateZ", tz)
        cmds.setAttr(guide+".indirectSkin", self.indSkinValue)
        cmds.setAttr(guide+".deformedBy", deformed)
        if mirror:
            self.single.changeMirror(mirror)
            cmds.setAttr(guide+".flip", 1)
        cmds.setAttr(guide+".displayAnnotation", 0)
        cmds.setAttr(guide+"_Ant.visibility", 0)
        cmds.setAttr(guide+".shapeSize", 0.03)
        return guide
