# importing libraries:
from maya import cmds
from maya import mel
from itertools import zip_longest
from ..base import base
from importlib import reload

# global variables to this module:    
CLASS_NAME = "OneSkeleton"
TITLE = "m254_oneSkeleton"
DESCRIPTION = "m255_oneSkeletonDesc"
WIKI = "06-‐-Tools#-one-skeleton"



class OneSkeleton(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        self.prefix = "Engine_"
        self.rootName = "Root"
        self.suffix = "_Joint"
        self.sides = [f"{self.ar.data.lang['p002_left']}_", f"{self.ar.data.lang['p003_right']}_", ""]


    def build_tool(self, *args):
        # call main UI function
        if self.ar.data.ui_state:
            self.create_ui()
            

    def create_ui(self, *args):
        # creating Window:
        self.ar.utils.close_ui('one_skeleton_win')
        winWidth  = 230
        winHeight = 230
        cmds.window('one_skeleton_win', title=self.ar.data.lang["m254_oneSkeleton"]+" "+str(self.ar.data.version), widthHeight=(winWidth, winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        cmds.columnLayout('main_layout', columnOffset=("both", 10), rowSpacing=10, adjustableColumn=True, parent='one_skeleton_win')
        cmds.separator(height=5, style="in", horizontal=True, parent='main_layout')
        cmds.rowColumnLayout('naming_rcl', numberOfColumns=2, adjustableColumn=2, columnWidth=(80, 100), rowSpacing=(7, 7), parent='main_layout')
        cmds.text('prefix_txt', label=self.ar.data.lang['i144_prefix'], parent='naming_rcl')
        cmds.textField('prefix_tf', text=self.prefix, textChangedCommand=self.change_prefix, parent='naming_rcl')
        cmds.text('root_txt', label="Root", parent='naming_rcl')
        cmds.textField('root_tf', text=self.rootName, textChangedCommand=self.change_root, parent='naming_rcl')
        cmds.text('suffix_txt', label=self.ar.data.lang['m217_suffix'], parent='naming_rcl')
        cmds.textField('suffix_tf', text=self.suffix, textChangedCommand=self.change_suffix, parent='naming_rcl')
        cmds.text('header_txt', label=self.ar.data.lang['m223_preview'], parent='naming_rcl')
        cmds.text('preview_txt', label=f"{self.prefix}{self.rootName}{self.suffix}", font="boldLabelFont", parent='naming_rcl')
        cmds.radioButtonGrp("skeleton_rbg", label=self.ar.data.lang['i138_type'], labelArray2=["Floating Joints", self.ar.data.lang['m216_hierarchy']], vertical=True, numberOfRadioButtons=2, columnAlign2=("left", "left"), columnAttach2=("left", "left"), columnWidth2=(40, 100), parent="main_layout")
        cmds.radioButtonGrp("skeleton_rbg", edit=True, select=2) #hierarchy = 2
        cmds.checkBox("use_scale_cb", label="Scale constraint", value=False, parent="main_layout")
        cmds.button("run_one_skeleton_bt", label=self.ar.data.lang['i158_create'], command=self.create_by_ui, parent="main_layout")
        cmds.separator(height=5, style="in", horizontal=True, parent='main_layout')
        # call Window:
        cmds.showWindow('one_skeleton_win')
        

    def create_by_ui(self, *args):
        joint_type = cmds.radioButtonGrp('skeleton_rbg', query=True, select=True)-1
        use_scale = cmds.checkBox('use_scale_cb', query=True, value=True)
        self.createOneSkeleton(hierarchy=joint_type, scale=use_scale)
        self.ar.utils.close_ui('one_skeleton_win')


    def change_prefix(self, value, *args):
        self.prefix = value
        self.refresh_preview()

    
    def change_root(self, value, *args):
        self.rootName = value
        self.refresh_preview()


    def change_suffix(self, value, *args):
        self.suffix = value
        self.refresh_preview()


    def refresh_preview(self, *args):
        """ Reload the preview naming list and populate its UI textScrollList.
        """
        cmds.text('preview_txt', edit=True, label=f"{self.prefix}{self.rootName}{self.suffix}")
    

    def oneSkeletonPromptDialog(self, *args):
        """ Prompt dialog to get the name of the root joint to receive all the web joints as children.
        """
        btContinue = self.ar.data.lang['i174_continue']
        btCancel = self.ar.data.lang['i132_cancel']
        result = cmds.promptDialog(title=CLASS_NAME, 
                                   message=self.ar.data.lang["m006_name"], 
                                   text=self.prefix+self.rootName+self.suffix,
                                   button=[btContinue, btCancel], 
                                   defaultButton=btContinue, 
                                   cancelButton=btCancel, 
                                   dismissString=btCancel)
        if result == btContinue:
            dialogName = cmds.promptDialog(query=True, text=True)
            return dialogName
        elif result is None:
            return None


    def createOneSkeleton(self, root=None, hierarchy=True, scale=True, *args):
        """ Create one skeleton hierarchy using the given name as a root joint name or use the default root name.
        """
        if not root:
            root = f"{self.prefix}{self.rootName}{self.suffix}"
        uniqueInfList = self.getInfList(self.getMeshList())
        if uniqueInfList:
            if not cmds.objExists(root):
                self.createRootJoint(root)
            newJointList = self.transferJoint(uniqueInfList, scale)
            if newJointList:
                #newJointList.sort()
                if hierarchy:
                    self.mount_hierarchy(newJointList, root)
                else:
                    cmds.parent(newJointList, root)
                cmds.select(root)
            self.ar.ctrls.setControllerScaleCompensate(False)
            self.ar.utils.setProgress(endIt=True)
        else:
            mel.eval('warning \"'+self.ar.data.lang["v014_notFoundNodes"]+'\";')


    def grouper(self, iterable, n, fillvalue=None, *args):
        """ Collect data into fixed-length chunks or blocks.
            Example:
                grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
        """
        args = [iter(iterable)] * n
        return zip_longest(fillvalue=fillvalue, *args)


    def transferJoint(self, sourceList, scale=True, *args):
        """ Make a duplicated joints and transfer connections and deformation to them.
            Returns the new created joint list.
        """
        scale_constraints = []
        newJointList = []
        self.ar.utils.setProgress(self.ar.data.lang['m254_oneSkeleton'], self.ar.data.lang['m254_oneSkeleton'], max=len(sourceList), add_one=False, add_number=False)
        for sourceNode in sourceList:
            self.ar.utils.setProgress("Joint")
            cmds.select(clear=True)
            newJoint = cmds.joint(name=self.prefix+sourceNode+self.suffix, scaleCompensate=False)
            newJointList.append(newJoint)
            # Transfer skinCluster + bindPose connection from the original
            connectionList = cmds.listConnections(sourceNode, destination=True, source=False, connections=True, plugs=True) or []
            for src, dest in self.grouper(connectionList, 2):
                sourceNode, sourceAttr = src.split(".", 1)
                destNode, destAttr = dest.split(".", 1)
                if cmds.nodeType(destNode) in {"skinCluster", "dagPose"}:
                    # pass if the attribute doesn't exists in the source node
                    if not cmds.attributeQuery(sourceAttr, node=sourceNode, exists=True):
                        print(f"Attribute {sourceAttr} does not exist on {sourceNode}")
                        continue
                    if sourceAttr in cmds.listAttr(newJoint):
                        # Transfer connection to the new node
                        cmds.disconnectAttr(src, dest)
                        cmds.connectAttr(newJoint+"."+sourceAttr, dest, force=True)
            # Match joint orient
            for attr in ["jointOrientX", "jointOrientY", "jointOrientZ"]:
                value = cmds.getAttr(f"{sourceNode}.{attr}")
                cmds.setAttr(f"{newJoint}.{attr}", value)
            # Constraint to the original
            pac = cmds.parentConstraint([sourceNode, newJoint], maintainOffset=False, name=newJoint+"_PaC")[0]
            scc = cmds.scaleConstraint([sourceNode, newJoint], name=newJoint+"_ScC", maintainOffset=False)[0]
            scale_constraints.append(scc)
            # fixes for negative scale joints
            parentList = cmds.listRelatives(sourceNode, parent=True)
            if parentList:
                if not "_Jar" in parentList[0]:
                    for axis in self.ar.data.axis:
                        if cmds.getAttr(parentList[0]+".scale"+axis) < 0: #negative scale OMG
                            for a in self.ar.data.axis:
                                if not a == axis:
                                    cmds.setAttr(scc+".offset"+a, -1)
            # corrective joints
            if "_Jcr" in newJoint:
                for axis in self.ar.data.axis:
                    if cmds.getAttr(sourceNode+".scale"+axis) < 0 or cmds.getAttr(newJoint+".scale"+axis) < 0:
                        cmds.setAttr(pac+".target[0].targetOffsetRotate"+axis, 180)
                    cmds.setAttr(scc+".offset"+axis, 1)
            # Ensure the new joint doesn't have segmentScaleCompensate enabled
            # But do allow the scale constraint to compensate
            cmds.refresh()
            cmds.setAttr(f"{newJoint}.segmentScaleCompensate", False)
            try:
                cmds.setAttr(f"{sourceNode}.segmentScaleCompensate", False)
            except:
                pass
            cmds.setAttr(f"{scc}.constraintScaleCompensate", True)
            # dpIDs
            self.ar.custom_attr.addAttr(0, [newJoint, pac]) #dpID
        if not scale:
            cmds.delete(scale_constraints)
        return newJointList


    def getMeshList(self, *args):
        """ Returns the Render_Grp meshes or all meshes in the scene.
        """
        if self.ar.utils.getAllGrp():
            renderGrp = self.ar.utils.getNodeByMessage("renderGrp")
            if renderGrp:
                meshList = cmds.listRelatives(renderGrp, children=True, allDescendents=True, type="mesh")
                if meshList:
                    return meshList
        return cmds.ls(type="mesh")
    
    
    def getInfList(self, meshList, *args):
        """ Returns the influenceList of a given meshList.
        """
        uniqueInfList = []
        skinClusterList = []
        if not cmds.listRelatives(meshList, type="transform", parent=True, fullPath=True):
            mel.eval('warning \"'+self.ar.data.lang['i041_meshConnEmpty']+'\";')
            return
        for transformNode in list(set(cmds.listRelatives(meshList, type="transform", parent=True, fullPath=True))):
            skinClusterList.extend(self.ar.skin.checkExistingDeformerNode(transformNode)[2] or [])
        if skinClusterList:
            for skinClusterNode in skinClusterList:
                infList = cmds.skinCluster(skinClusterNode, query=True, influence=True)
                if infList:
                    for item in infList:
                        if not item in uniqueInfList:
                            uniqueInfList.append(item)
        return uniqueInfList


    def createRootJoint(self, root, *args):
        """ Create a base joint as root.
        """
        cmds.select(clear=True)
        cmds.joint(name=root, scaleCompensate=False)
        cmds.addAttr(root, longName="dpRootJoint", attributeType="bool", defaultValue=1)
        cmds.setAttr(root+".visibility", 0)
        self.ar.ctrls.setLockHide([root], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'dpRootJoint'], cb=True)


    def mount_hierarchy(self, joints, root, *args):
        hierarchy_data = self.get_hierarchy_data()
        integration_data = self.get_integration_data()
        for side in self.sides:
            for item in hierarchy_data.keys():
                if cmds.objExists(f"{self.prefix}{side}{item}{self.suffix}"):
                    for p, parent in enumerate(hierarchy_data[item]):
                        if cmds.objExists(f"{self.prefix}{side}{hierarchy_data[item][p]}{self.suffix}"):
                            cmds.parent(f"{self.prefix}{side}{item}{self.suffix}", f"{self.prefix}{side}{hierarchy_data[item][p]}{self.suffix}")
                            break
                        elif item in integration_data.keys():
                            if cmds.objExists(f"{self.prefix}{integration_data[item][p]}{self.suffix}"):
                                cmds.parent(f"{self.prefix}{side}{item}{self.suffix}", f"{self.prefix}{integration_data[item][p]}{self.suffix}")
                                break
                        else:
                            cmds.parent(f"{self.prefix}{side}{item}{self.suffix}", root)
                if f"{self.prefix}{side}{item}{self.suffix}" in joints:
                    joints.remove(f"{self.prefix}{side}{item}{self.suffix}")
        cmds.parent(joints, root)


    def get_hierarchy_data(self, *args):
        # getting default names
        arm = self.ar.data.lang['c037_arm']
        clavicle = self.ar.data.lang['c000_arm_before']
        shoulder = self.ar.data.lang['c001_arm_main']
        elbow = self.ar.data.lang['c002_arm_corner']
        wrist = self.ar.data.lang['c004_arm_extrem']
        forearm = self.ar.data.lang['c030_forearm']
        
        hip = self.ar.data.lang['c005_leg_before']
        leg = self.ar.data.lang['c006_leg_main']
        knee = self.ar.data.lang['c007_leg_corner']
        ankle = self.ar.data.lang['c009_leg_extrem']
        
        finger = self.ar.data.lang['m007_finger']
        thumb = self.ar.data.lang['m036_thumb']
        index = self.ar.data.lang['m032_index']
        middle = self.ar.data.lang['m033_middle']
        ring = self.ar.data.lang['m034_ring']
        pinky = self.ar.data.lang['m035_pinky']
        
        foot = self.ar.data.lang['c038_foot']
        toe = self.ar.data.lang['c013_revFoot_D'].capitalize()

        back = self.ar.data.lang['c057_back']
        front = self.ar.data.lang['c056_front']
        
        spine = self.ar.data.lang['m011_spine']
        base = self.ar.data.lang['c106_base']
        tip = self.ar.data.lang['c120_tip']
        hips = self.ar.data.lang['c027_hips']
        chest = self.ar.data.lang['c028_chest']
        
        neck = self.ar.data.lang['c023_neck']
        head = self.ar.data.lang['c024_head']
        jaw = self.ar.data.lang['c025_jaw']
        chin = self.ar.data.lang['c026_chin']
        chew = self.ar.data.lang['c048_chew']
        upper = self.ar.data.lang['c044_upper']
        lower = self.ar.data.lang['c045_lower']
        lip = self.ar.data.lang['c039_lip']
        corner = self.ar.data.lang['c043_corner']
        
        upper_teeth = self.ar.data.lang['m075_upperTeeth']
        lower_teeth = self.ar.data.lang['m076_lowerTeeth']
        tongue = self.ar.data.lang['m077_tongue']
        ear = self.ar.data.lang['m040_ear']
        
        nose = self.ar.data.lang['m078_nose']
        nostril = self.ar.data.lang['m079_nostril']
        bottom = self.ar.data.lang['c100_bottom']
        
        eye = self.ar.data.lang['c036_eye']
        eyelid = self.ar.data.lang['c042_eyelid']
        pupil = self.ar.data.lang['i081_pupil']
        iris = self.ar.data.lang['i080_iris']
        
        breath = self.ar.data.lang['c095_breath']
        belly = self.ar.data.lang['c096_belly']

        tail = self.ar.data.lang['m039_tail']
        
        tweaks = self.ar.data.lang['m081_tweaks']
        eyebrow = self.ar.data.lang['c041_eyebrow']
        squint = self.ar.data.lang['c054_squint']
        cheek = self.ar.data.lang['c055_cheek']
        main = self.ar.data.lang['c058_main']
        holder = self.ar.data.lang['c046_holder']

        # declaring result dictionary
        data = {
                # arm
                f"{arm}_{clavicle}_Jar" : [f"{arm}_{clavicle}_Jnt"],
                f"{arm}_{clavicle}_0_Jcr" : [f"{arm}_{clavicle}_Jnt"],
                f"{arm}_{shoulder}_Jnt" : [f"{arm}_{clavicle}_Jnt"],
                f"{arm}_{elbow}_Jar" : [f"{arm}_{elbow}_Jnt", f"{arm}_{shoulder}_Jnt"],
                f"{arm}_{elbow}_0_Jcr" : [f"{arm}_{elbow}_Jar"],
                f"{arm}_{elbow}_1_Jcr" : [f"{arm}_{elbow}_Jar"],
                f"{arm}_{elbow}_2_Jcr" : [f"{arm}_{elbow}_Jar"],
                f"{arm}_{elbow}_Jnt" : [f"{arm}_{shoulder}_Jnt"],
                f"{arm}_{forearm}_Jnt" : [f"{arm}_{elbow}_Jar", f"{arm}_{elbow}_Jnt"],
                f"{arm}_{wrist}_Jnt" : [f"{arm}_{forearm}_Jnt", f"{arm}_{elbow}_Jar", f"{arm}_{elbow}_Jnt"],
                f"{arm}_{wrist}_0_Jcr" : [f"{arm}_13_{wrist}_Jar"],
                f"{arm}_{wrist}_1_Jcr" : [f"{arm}_13_{wrist}_Jar"],
                f"{arm}_{wrist}_2_Jcr" : [f"{arm}_13_{wrist}_Jar"],
                f"{arm}_{wrist}_3_Jcr" : [f"{arm}_13_{wrist}_Jar"],
                f"{arm}_00_{clavicle}_Jar" : [f"{arm}_00_{clavicle}_Jnt"],
                f"{arm}_00_{clavicle}_0_Jcr" : [f"{arm}_00_{clavicle}_Jar", f"{arm}_00_{clavicle}_Jnt"],
                f"{arm}_01_{shoulder}_Jar" : [f"{arm}_01_{shoulder}_Jnt", f"{arm}_00_{clavicle}_Jnt", f"{arm}_{shoulder}_Jnt"],
                f"{arm}_{shoulder}_0_Jcr" : [f"{arm}_01_{shoulder}_Jar"],
                f"{arm}_{shoulder}_1_Jcr" : [f"{arm}_01_{shoulder}_Jar"],
                f"{arm}_02_Jnt" : [f"{arm}_01_{shoulder}_Jar"],
                f"{arm}_03_Jnt" : [f"{arm}_02_Jnt"],
                f"{arm}_04_Jnt" : [f"{arm}_03_Jnt"],
                f"{arm}_05_Jnt" : [f"{arm}_04_Jnt"],
                f"{arm}_05_{elbow}_Jar" : [f"{arm}_04_Jnt"],
                f"{arm}_05_{elbow}_0_Jcr" : [f"{arm}_05_{elbow}_Jar"],
                f"{arm}_05_{elbow}_1_Jcr" : [f"{arm}_05_{elbow}_Jar"],
                f"{arm}_05_{elbow}_2_Jcr" : [f"{arm}_05_{elbow}_Jar"],
                f"{arm}_06_Jnt" : [f"{arm}_05_{elbow}_Jar", f"{arm}_05_Jnt"],
                f"{arm}_07_Jnt" : [f"{arm}_06_Jnt"],
                f"{arm}_07_{elbow}_Jar" : [f"{arm}_06_Jnt"],
                f"{arm}_07_{elbow}_0_Jcr" : [f"{arm}_07_{elbow}_Jar"],
                f"{arm}_07_{elbow}_1_Jcr" : [f"{arm}_07_{elbow}_Jar"],
                f"{arm}_07_{elbow}_2_Jcr" : [f"{arm}_07_{elbow}_Jar"],
                f"{arm}_08_Jnt" : [f"{arm}_07_{elbow}_Jar", f"{arm}_07_Jnt"],
                f"{arm}_09_Jnt" : [f"{arm}_08_Jnt"],
                f"{arm}_09_{elbow}_Jar" : [f"{arm}_08_Jnt"],
                f"{arm}_09_{elbow}_0_Jcr" : [f"{arm}_09_{elbow}_Jar"],
                f"{arm}_09_{elbow}_1_Jcr" : [f"{arm}_09_{elbow}_Jar"],
                f"{arm}_09_{elbow}_2_Jcr" : [f"{arm}_09_{elbow}_Jar"],
                f"{arm}_09_{wrist}_Jnt" : [f"{arm}_08_Jnt"],
                f"{arm}_09_{wrist}_Jar" : [f"{arm}_09_{wrist}_Jnt", f"{arm}_08_Jnt"],
                f"{arm}_09_{wrist}_0_Jcr" : [f"{arm}_09_{wrist}_Jar"],
                f"{arm}_09_{wrist}_1_Jcr" : [f"{arm}_09_{wrist}_Jar"],
                f"{arm}_09_{wrist}_2_Jcr" : [f"{arm}_09_{wrist}_Jar"],
                f"{arm}_09_{wrist}_3_Jcr" : [f"{arm}_09_{wrist}_Jar"],
                f"{arm}_10_Jnt" : [f"{arm}_09_{elbow}_Jar", f"{arm}_09_Jnt"],
                f"{arm}_11_Jnt" : [f"{arm}_10_Jnt"],
                f"{arm}_12_Jnt" : [f"{arm}_11_Jnt"],
                f"{arm}_13_{wrist}_Jnt" : [f"{arm}_12_Jnt"],
                f"{arm}_13_{wrist}_Jar" : [f"{arm}_13_{wrist}_Jnt", f"{arm}_12_Jnt", f"{arm}_{elbow}_Jnt"],
                f"{arm}_13_{wrist}_0_Jcr" : [f"{arm}_13_{wrist}_Jar"],
                f"{arm}_13_{wrist}_1_Jcr" : [f"{arm}_13_{wrist}_Jar"],
                f"{arm}_13_{wrist}_2_Jcr" : [f"{arm}_13_{wrist}_Jar"],
                f"{arm}_13_{wrist}_3_Jcr" : [f"{arm}_13_{wrist}_Jar"],
                f"{arm}_13_Jnt" : [f"{arm}_12_Jnt"],
                f"{arm}_14_Jnt" : [f"{arm}_13_Jnt"],
                f"{arm}_15_Jnt" : [f"{arm}_14_Jnt"],
                f"{arm}_16_Jnt" : [f"{arm}_15_Jnt"],
                f"{arm}_17_{wrist}_Jnt" : [f"{arm}_16_Jnt"],
                f"{arm}_17_{wrist}_Jar" : [f"{arm}_17_{wrist}_Jnt", f"{arm}_16_Jnt"],
                f"{arm}_17_{wrist}_0_Jcr" : [f"{arm}_17_{wrist}_Jar"],
                f"{arm}_17_{wrist}_1_Jcr" : [f"{arm}_17_{wrist}_Jar"],
                f"{arm}_17_{wrist}_2_Jcr" : [f"{arm}_17_{wrist}_Jar"],
                f"{arm}_17_{wrist}_3_Jcr" : [f"{arm}_17_{wrist}_Jar"],
                
                # fingers
                f"{finger}_{thumb}_00_Jnt" : [f"{arm}_13_{wrist}_Jar", f"{arm}_13_{wrist}_Jnt", f"{arm}_17_{wrist}_Jar", f"{arm}_17_{wrist}_Jnt", f"{arm}_09_{wrist}_Jar", f"{arm}_09_{wrist}_Jnt", f"{arm}_{wrist}_Jnt"],
                f"{finger}_{thumb}_01_Jnt" : [f"{finger}_{thumb}_00_Jnt"],
                f"{finger}_{thumb}_01_Jar" : [f"{finger}_{thumb}_01_Jnt"],
                f"{finger}_{thumb}_01_0_Jcr" : [f"{finger}_{thumb}_01_Jar"],
                f"{finger}_{thumb}_02_Jnt" : [f"{finger}_{thumb}_01_Jar", f"{finger}_{thumb}_01_Jnt"],
                f"{finger}_{thumb}_02_Jar" : [f"{finger}_{thumb}_02_Jnt"],
                f"{finger}_{thumb}_02_0_Jcr" : [f"{finger}_{thumb}_02_Jar"],
                f"{finger}_{index}_00_Jnt" : [f"{arm}_13_{wrist}_Jar", f"{arm}_13_{wrist}_Jnt", f"{arm}_17_{wrist}_Jar", f"{arm}_17_{wrist}_Jnt", f"{arm}_09_{wrist}_Jar", f"{arm}_09_{wrist}_Jnt", f"{arm}_{wrist}_Jnt"],
                f"{finger}_{index}_01_Jnt" : [f"{finger}_{index}_00_Jnt"],
                f"{finger}_{index}_01_Jar" : [f"{finger}_{index}_01_Jnt"],
                f"{finger}_{index}_01_0_Jcr" : [f"{finger}_{index}_01_Jar"],
                f"{finger}_{index}_02_Jnt" : [f"{finger}_{index}_01_Jar", f"{finger}_{index}_01_Jnt"],
                f"{finger}_{index}_02_Jar" : [f"{finger}_{index}_02_Jnt"],
                f"{finger}_{index}_02_0_Jcr" : [f"{finger}_{index}_02_Jar"],
                f"{finger}_{index}_03_Jnt" : [f"{finger}_{index}_02_Jar", f"{finger}_{index}_02_Jnt"],
                f"{finger}_{index}_03_Jar" : [f"{finger}_{index}_03_Jnt"],
                f"{finger}_{index}_03_0_Jcr" : [f"{finger}_{index}_03_Jar"],
                f"{finger}_{middle}_00_Jnt" : [f"{arm}_13_{wrist}_Jar", f"{arm}_13_{wrist}_Jnt", f"{arm}_17_{wrist}_Jar", f"{arm}_17_{wrist}_Jnt", f"{arm}_09_{wrist}_Jar", f"{arm}_09_{wrist}_Jnt", f"{arm}_{wrist}_Jnt"],
                f"{finger}_{middle}_01_Jnt" : [f"{finger}_{middle}_00_Jnt"],
                f"{finger}_{middle}_01_Jar" : [f"{finger}_{middle}_01_Jnt"],
                f"{finger}_{middle}_01_0_Jcr" : [f"{finger}_{middle}_01_Jar"],
                f"{finger}_{middle}_02_Jnt" : [f"{finger}_{middle}_01_Jar", f"{finger}_{middle}_01_Jnt"],
                f"{finger}_{middle}_02_Jar" : [f"{finger}_{middle}_02_Jnt"],
                f"{finger}_{middle}_02_0_Jcr" : [f"{finger}_{middle}_02_Jar"],
                f"{finger}_{middle}_03_Jnt" : [f"{finger}_{middle}_02_Jar", f"{finger}_{middle}_02_Jnt"],
                f"{finger}_{middle}_03_Jar" : [f"{finger}_{middle}_03_Jnt"],
                f"{finger}_{middle}_03_0_Jcr" : [f"{finger}_{middle}_03_Jar"],
                f"{finger}_{ring}_00_Jnt" : [f"{arm}_13_{wrist}_Jar", f"{arm}_13_{wrist}_Jnt", f"{arm}_17_{wrist}_Jar", f"{arm}_17_{wrist}_Jnt", f"{arm}_09_{wrist}_Jar", f"{arm}_09_{wrist}_Jnt", f"{arm}_{wrist}_Jnt"],
                f"{finger}_{ring}_01_Jnt" : [f"{finger}_{ring}_00_Jnt"],
                f"{finger}_{ring}_01_Jar" : [f"{finger}_{ring}_01_Jnt"],
                f"{finger}_{ring}_01_0_Jcr" : [f"{finger}_{ring}_01_Jar"],
                f"{finger}_{ring}_02_Jnt" : [f"{finger}_{ring}_01_Jar", f"{finger}_{ring}_01_Jnt"],
                f"{finger}_{ring}_02_Jar" : [f"{finger}_{ring}_02_Jnt"],
                f"{finger}_{ring}_02_0_Jcr" : [f"{finger}_{ring}_02_Jar"],
                f"{finger}_{ring}_03_Jnt" : [f"{finger}_{ring}_02_Jar", f"{finger}_{ring}_02_Jnt"],
                f"{finger}_{ring}_03_Jar" : [f"{finger}_{ring}_03_Jnt"],
                f"{finger}_{ring}_03_0_Jcr" : [f"{finger}_{ring}_03_Jar"],
                f"{finger}_{pinky}_00_Jnt" : [f"{arm}_13_{wrist}_Jar", f"{arm}_13_{wrist}_Jnt", f"{arm}_17_{wrist}_Jar", f"{arm}_17_{wrist}_Jnt", f"{arm}_09_{wrist}_Jar", f"{arm}_09_{wrist}_Jnt", f"{arm}_{wrist}_Jnt"],
                f"{finger}_{pinky}_01_Jnt" : [f"{finger}_{pinky}_00_Jnt"],
                f"{finger}_{pinky}_01_Jar" : [f"{finger}_{pinky}_01_Jnt"],
                f"{finger}_{pinky}_01_0_Jcr" : [f"{finger}_{pinky}_01_Jar"],
                f"{finger}_{pinky}_02_Jnt" : [f"{finger}_{pinky}_01_Jar", f"{finger}_{pinky}_01_Jnt"],
                f"{finger}_{pinky}_02_Jar" : [f"{finger}_{pinky}_02_Jnt"],
                f"{finger}_{pinky}_02_0_Jcr" : [f"{finger}_{pinky}_02_Jar"],
                f"{finger}_{pinky}_03_Jnt" : [f"{finger}_{pinky}_02_Jar", f"{finger}_{pinky}_02_Jnt"],
                f"{finger}_{pinky}_03_Jar" : [f"{finger}_{pinky}_03_Jnt"],
                f"{finger}_{pinky}_03_0_Jcr" : [f"{finger}_{pinky}_03_Jar"],

                # leg
                f"{leg}_{hip}_Jar" : [f"{leg}_{hip}_Jnt"],
                f"{leg}_{hip}_0_Jcr" : [f"{leg}_{hip}_Jnt"],
                f"{leg}_{leg}_Jnt" : [f"{leg}_{hip}_Jnt"],
                f"{leg}_{knee}_Jar" : [f"{leg}_{knee}_Jnt", f"{leg}_{leg}_Jnt"],
                f"{leg}_{knee}_0_Jcr" : [f"{leg}_{knee}_Jar"],
                f"{leg}_{knee}_1_Jcr" : [f"{leg}_{knee}_Jar"],
                f"{leg}_{knee}_2_Jcr" : [f"{leg}_{knee}_Jar"],
                f"{leg}_{knee}_Jnt" : [f"{leg}_{leg}_Jnt"],
                f"{leg}_{ankle}_Jnt" : [f"{leg}_{knee}_Jar", f"{leg}_{knee}_Jnt"],
                f"{leg}_{ankle}_0_Jcr" : [f"{leg}_13_{ankle}_Jar"],
                f"{leg}_{ankle}_1_Jcr" : [f"{leg}_13_{ankle}_Jar"],
                f"{leg}_{ankle}_2_Jcr" : [f"{leg}_13_{ankle}_Jar"],
                f"{leg}_{ankle}_3_Jcr" : [f"{leg}_13_{ankle}_Jar"],
                f"{leg}_00_{hip}_Jar" : [f"{leg}_00_{hip}_Jnt"],
                f"{leg}_00_{hip}_0_Jcr" : [f"{leg}_00_{hip}_Jar", f"{leg}_00_{hip}_Jnt"],
                f"{leg}_01_{leg}_Jar" : [f"{leg}_00_{leg}_Jnt", f"{leg}_00_{hip}_Jnt", f"{leg}_{leg}_Jnt"],
                f"{leg}_{leg}_0_Jcr" : [f"{leg}_01_{leg}_Jar"],
                f"{leg}_{leg}_1_Jcr" : [f"{leg}_01_{leg}_Jar"],
                f"{leg}_02_Jnt" : [f"{leg}_01_{leg}_Jar"],
                f"{leg}_03_Jnt" : [f"{leg}_02_Jnt"],
                f"{leg}_04_Jnt" : [f"{leg}_03_Jnt"],
                f"{leg}_05_Jnt" : [f"{leg}_04_Jnt"],
                f"{leg}_05_{knee}_Jar" : [f"{leg}_04_Jnt"],
                f"{leg}_05_{knee}_0_Jcr" : [f"{leg}_05_{knee}_Jar"],
                f"{leg}_05_{knee}_1_Jcr" : [f"{leg}_05_{knee}_Jar"],
                f"{leg}_05_{knee}_2_Jcr" : [f"{leg}_05_{knee}_Jar"],
                f"{leg}_06_Jnt" : [f"{leg}_05_{knee}_Jar", f"{leg}_05_Jnt"],
                f"{leg}_07_Jnt" : [f"{leg}_06_Jnt"],
                f"{leg}_07_{knee}_Jar" : [f"{leg}_06_Jnt"],
                f"{leg}_07_{knee}_0_Jcr" : [f"{leg}_07_{knee}_Jar"],
                f"{leg}_07_{knee}_1_Jcr" : [f"{leg}_07_{knee}_Jar"],
                f"{leg}_07_{knee}_2_Jcr" : [f"{leg}_07_{knee}_Jar"],
                f"{leg}_08_Jnt" : [f"{leg}_07_{knee}_Jar", f"{leg}_07_Jnt"],
                f"{leg}_09_Jnt" : [f"{leg}_08_Jnt"],
                f"{leg}_09_{knee}_Jar" : [f"{leg}_08_Jnt"],
                f"{leg}_09_{knee}_0_Jcr" : [f"{leg}_09_{knee}_Jar"],
                f"{leg}_09_{knee}_1_Jcr" : [f"{leg}_09_{knee}_Jar"],
                f"{leg}_09_{knee}_2_Jcr" : [f"{leg}_09_{knee}_Jar"],
                f"{leg}_09_{ankle}_Jnt" : [f"{leg}_08_Jnt"],
                f"{leg}_09_{ankle}_Jar" : [f"{leg}_09_{ankle}_Jnt", f"{leg}_08_Jnt"],
                f"{leg}_09_{ankle}_0_Jcr" : [f"{leg}_09_{ankle}_Jar"],
                f"{leg}_09_{ankle}_1_Jcr" : [f"{leg}_09_{ankle}_Jar"],
                f"{leg}_09_{ankle}_2_Jcr" : [f"{leg}_09_{ankle}_Jar"],
                f"{leg}_09_{ankle}_3_Jcr" : [f"{leg}_09_{ankle}_Jar"],
                f"{leg}_10_Jnt" : [f"{leg}_09_{knee}_Jar", f"{leg}_09_Jnt"],
                f"{leg}_11_Jnt" : [f"{leg}_10_Jnt"],
                f"{leg}_12_Jnt" : [f"{leg}_11_Jnt"],
                f"{leg}_13_{ankle}_Jnt" : [f"{leg}_12_Jnt"],
                f"{leg}_13_{ankle}_Jar" : [f"{leg}_13_{ankle}_Jnt", f"{leg}_12_Jnt", f"{leg}_{knee}_Jnt"],
                f"{leg}_13_{ankle}_0_Jcr" : [f"{leg}_13_{ankle}_Jar"],
                f"{leg}_13_{ankle}_1_Jcr" : [f"{leg}_13_{ankle}_Jar"],
                f"{leg}_13_{ankle}_2_Jcr" : [f"{leg}_13_{ankle}_Jar"],
                f"{leg}_13_{ankle}_3_Jcr" : [f"{leg}_13_{ankle}_Jar"],
                f"{leg}_13_Jnt" : [f"{leg}_12_Jnt"],
                f"{leg}_14_Jnt" : [f"{leg}_13_Jnt"],
                f"{leg}_15_Jnt" : [f"{leg}_14_Jnt"],
                f"{leg}_16_Jnt" : [f"{leg}_15_Jnt"],
                f"{leg}_17_{ankle}_Jnt" : [f"{leg}_16_Jnt"],
                f"{leg}_17_{ankle}_Jar" : [f"{leg}_17_{ankle}_Jnt", f"{leg}_16_Jnt"],
                f"{leg}_17_{ankle}_0_Jcr" : [f"{leg}_17_{ankle}_Jar"],
                f"{leg}_17_{ankle}_1_Jcr" : [f"{leg}_17_{ankle}_Jar"],
                f"{leg}_17_{ankle}_2_Jcr" : [f"{leg}_17_{ankle}_Jar"],
                f"{leg}_17_{ankle}_3_Jcr" : [f"{leg}_17_{ankle}_Jar"],
                
                # foot
                f"{foot}_{ankle}_Jnt" : [f"{leg}_17_{ankle}_Jar", f"{leg}_13_{ankle}_Jar", f"{leg}_09_{ankle}_Jar", f"{leg}_17_{ankle}_Jnt", f"{leg}_13_{ankle}_Jnt", f"{leg}_09_{ankle}_Jnt", f"{leg}_{knee}_Jar", f"{leg}_{knee}_Jnt"],
                f"{foot}_{middle}_Jnt" : [f"{foot}_{ankle}_Jar", f"{foot}_{ankle}_Jnt"],
                
                # toes
                f"{toe}_1_00_Jnt" : [f"{foot}_{middle}_Jar", f"{foot}_{middle}_Jnt"],
                f"{toe}_1_01_Jnt" : [f"{toe}_1_00_Jnt"],
                f"{toe}_1_02_Jnt" : [f"{toe}_1_01_Jnt"],
                f"{toe}_2_00_Jnt" : [f"{foot}_{middle}_Jar", f"{foot}_{middle}_Jnt"],
                f"{toe}_2_01_Jnt" : [f"{toe}_2_00_Jnt"],
                f"{toe}_2_02_Jnt" : [f"{toe}_2_01_Jnt"],
                f"{toe}_3_00_Jnt" : [f"{foot}_{middle}_Jar", f"{foot}_{middle}_Jnt"],
                f"{toe}_3_01_Jnt" : [f"{toe}_3_00_Jnt"],
                f"{toe}_3_02_Jnt" : [f"{toe}_3_01_Jnt"],
                f"{toe}_4_00_Jnt" : [f"{foot}_{middle}_Jar", f"{foot}_{middle}_Jnt"],
                f"{toe}_4_01_Jnt" : [f"{toe}_4_00_Jnt"],
                f"{toe}_4_02_Jnt" : [f"{toe}_4_01_Jnt"],
                f"{toe}_5_00_Jnt" : [f"{foot}_{middle}_Jar", f"{foot}_{middle}_Jnt"],
                f"{toe}_5_01_Jnt" : [f"{toe}_5_00_Jnt"],
                f"{toe}_5_02_Jnt" : [f"{toe}_5_01_Jnt"],

                # -----
                # quadruped
                # back
                f"{leg}{back}_{hip}_Jar" : [f"{leg}{back}_{hip}_Jnt"],
                f"{leg}{back}_{hip}_0_Jcr" : [f"{leg}{back}_{hip}_Jnt"],
                f"{leg}{back}_{leg}_Jnt" : [f"{leg}{back}_{hip}_Jnt"],
                f"{leg}{back}_{knee}_Jar" : [f"{leg}{back}_{knee}_Jnt", f"{leg}{back}_{leg}_Jnt"],
                f"{leg}{back}_{knee}_0_Jcr" : [f"{leg}{back}_{knee}_Jar"],
                f"{leg}{back}_{knee}_1_Jcr" : [f"{leg}{back}_{knee}_Jar"],
                f"{leg}{back}_{knee}_2_Jcr" : [f"{leg}{back}_{knee}_Jar"],
                f"{leg}{back}_{knee}_Jnt" : [f"{leg}{back}_{leg}_Jnt"],
                f"{leg}{back}_{ankle}_Jnt" : [f"{leg}{back}_{knee}_Jar", f"{leg}{back}_{knee}_Jnt", f"{leg}{back}_09_Jnt", f"{leg}{back}_13_Jnt", f"{leg}{back}_19_Jnt"],
                f"{leg}{back}_{ankle}_0_Jcr" : [f"{leg}{back}_13_{ankle}_Jar"],
                f"{leg}{back}_{ankle}_1_Jcr" : [f"{leg}{back}_13_{ankle}_Jar"],
                f"{leg}{back}_{ankle}_2_Jcr" : [f"{leg}{back}_13_{ankle}_Jar"],
                f"{leg}{back}_{ankle}_3_Jcr" : [f"{leg}{back}_13_{ankle}_Jar"],
                f"{leg}{back}_00_{hip}_Jar" : [f"{leg}{back}_00_{hip}_Jnt"],
                f"{leg}{back}_00_{hip}_0_Jcr" : [f"{leg}{back}_00_{hip}_Jar", f"{leg}{back}_00_{hip}_Jnt"],
                f"{leg}{back}_01_{leg}_Jar" : [f"{leg}{back}_00_{leg}_Jnt", f"{leg}{back}_00_{hip}_Jnt", f"{leg}{back}_{leg}_Jnt"],
                f"{leg}{back}_{leg}_0_Jcr" : [f"{leg}{back}_01_{leg}_Jar"],
                f"{leg}{back}_{leg}_1_Jcr" : [f"{leg}{back}_01_{leg}_Jar"],
                f"{leg}{back}_02_Jnt" : [f"{leg}{back}_01_{leg}_Jar", f"{leg}{back}_01_Jnt"],
                f"{leg}{back}_03_Jnt" : [f"{leg}{back}_02_Jnt"],
                f"{leg}{back}_04_Jnt" : [f"{leg}{back}_03_Jnt"],
                f"{leg}{back}_05_Jnt" : [f"{leg}{back}_04_Jnt"],
                f"{leg}{back}_05_{knee}_Jar" : [f"{leg}{back}_04_Jnt"],
                f"{leg}{back}_05_{knee}_0_Jcr" : [f"{leg}{back}_05_{knee}_Jar"],
                f"{leg}{back}_05_{knee}_1_Jcr" : [f"{leg}{back}_05_{knee}_Jar"],
                f"{leg}{back}_05_{knee}_2_Jcr" : [f"{leg}{back}_05_{knee}_Jar"],
                f"{leg}{back}_06_Jnt" : [f"{leg}{back}_05_{knee}_Jar", f"{leg}{back}_05_Jnt", f"{leg}{back}_05_{knee}B_Jar"],
                f"{leg}{back}_07_Jnt" : [f"{leg}{back}_06_Jnt"],
                f"{leg}{back}_07_{knee}_Jar" : [f"{leg}{back}_06_Jnt", f"{leg}{back}_{knee}_Jnt"],
                f"{leg}{back}_07_{knee}_0_Jcr" : [f"{leg}{back}_07_{knee}_Jar"],
                f"{leg}{back}_07_{knee}_1_Jcr" : [f"{leg}{back}_07_{knee}_Jar"],
                f"{leg}{back}_07_{knee}_2_Jcr" : [f"{leg}{back}_07_{knee}_Jar"],
                f"{leg}{back}_08_Jnt" : [f"{leg}{back}_07_{knee}_Jar", f"{leg}{back}_07_Jnt", f"{leg}{back}_07_{knee}B_Jar"],
                f"{leg}{back}_09_Jnt" : [f"{leg}{back}_08_Jnt"],
                f"{leg}{back}_09_{knee}_Jar" : [f"{leg}{back}_08_Jnt"],
                f"{leg}{back}_09_{knee}_0_Jcr" : [f"{leg}{back}_09_{knee}_Jar"],
                f"{leg}{back}_09_{knee}_1_Jcr" : [f"{leg}{back}_09_{knee}_Jar"],
                f"{leg}{back}_09_{knee}_2_Jcr" : [f"{leg}{back}_09_{knee}_Jar"],
                f"{leg}{back}_09_{knee}B_Jar" : [f"{leg}{back}_08_Jnt"],
                f"{leg}{back}_09_{knee}B_0_Jcr" : [f"{leg}{back}_09_{knee}B_Jar"],
                f"{leg}{back}_09_{knee}B_1_Jcr" : [f"{leg}{back}_09_{knee}B_Jar"],
                f"{leg}{back}_09_{knee}B_2_Jcr" : [f"{leg}{back}_09_{knee}B_Jar"],
                f"{leg}{back}_09_{ankle}_Jnt" : [f"{leg}{back}_08_Jnt"],
                f"{leg}{back}_09_{ankle}_Jar" : [f"{leg}{back}_09_{ankle}_Jnt", f"{leg}{back}_08_Jnt"],
                f"{leg}{back}_09_{ankle}_0_Jcr" : [f"{leg}{back}_09_{ankle}_Jar"],
                f"{leg}{back}_09_{ankle}_1_Jcr" : [f"{leg}{back}_09_{ankle}_Jar"],
                f"{leg}{back}_09_{ankle}_2_Jcr" : [f"{leg}{back}_09_{ankle}_Jar"],
                f"{leg}{back}_09_{ankle}_3_Jcr" : [f"{leg}{back}_09_{ankle}_Jar"],
                f"{leg}{back}_10_Jnt" : [f"{leg}{back}_09_{knee}_Jar", f"{leg}{back}_09_Jnt", f"{leg}{back}_09_{knee}B_Jar"],
                f"{leg}{back}_11_Jnt" : [f"{leg}{back}_10_Jnt"],
                f"{leg}{back}_12_Jnt" : [f"{leg}{back}_11_Jnt"],
                f"{leg}{back}_{knee}B_Jnt" : [f"{leg}{back}_07_{knee}_Jar", f"{leg}{back}_{knee}_Jnt"],
                f"{leg}{back}_13_{knee}B_Jar" : [f"{leg}{back}_12_Jnt", f"{leg}{back}_{knee}B_Jnt"],
                f"{leg}{back}_13_{knee}B_0_Jcr" : [f"{leg}{back}_13_{knee}B_Jar"],
                f"{leg}{back}_13_{knee}B_1_Jcr" : [f"{leg}{back}_13_{knee}B_Jar"],
                f"{leg}{back}_13_{knee}B_2_Jcr" : [f"{leg}{back}_13_{knee}B_Jar"],
                f"{leg}{back}_13_{ankle}_Jnt" : [f"{leg}{back}_12_Jnt"],
                f"{leg}{back}_13_{ankle}_Jar" : [f"{leg}{back}_13_{ankle}_Jnt", f"{leg}{back}_12_Jnt", f"{leg}{back}_{knee}_Jnt"],
                f"{leg}{back}_13_{ankle}_0_Jcr" : [f"{leg}{back}_13_{ankle}_Jar"],
                f"{leg}{back}_13_{ankle}_1_Jcr" : [f"{leg}{back}_13_{ankle}_Jar"],
                f"{leg}{back}_13_{ankle}_2_Jcr" : [f"{leg}{back}_13_{ankle}_Jar"],
                f"{leg}{back}_13_{ankle}_3_Jcr" : [f"{leg}{back}_13_{ankle}_Jar"],
                f"{leg}{back}_13_Jnt" : [f"{leg}{back}_12_Jnt"],
                f"{leg}{back}_14_Jnt" : [f"{leg}{back}_13_Jnt", f"{leg}{back}_13_{knee}B_Jar"],
                f"{leg}{back}_15_Jnt" : [f"{leg}{back}_14_Jnt"],
                f"{leg}{back}_16_Jnt" : [f"{leg}{back}_15_Jnt"],
                f"{leg}{back}_17_{knee}B_Jar" : [f"{leg}{back}_16_Jnt"],
                f"{leg}{back}_17_{knee}B_0_Jcr" : [f"{leg}{back}_17_{knee}B_Jar"],
                f"{leg}{back}_17_{knee}B_1_Jcr" : [f"{leg}{back}_17_{knee}B_Jar"],
                f"{leg}{back}_17_{knee}B_2_Jcr" : [f"{leg}{back}_17_{knee}B_Jar"],
                f"{leg}{back}_17_{ankle}_Jnt" : [f"{leg}{back}_16_Jnt"],
                f"{leg}{back}_17_{ankle}_Jar" : [f"{leg}{back}_17_{ankle}_Jnt", f"{leg}{back}_16_Jnt"],
                f"{leg}{back}_17_{ankle}_0_Jcr" : [f"{leg}{back}_17_{ankle}_Jar"],
                f"{leg}{back}_17_{ankle}_1_Jcr" : [f"{leg}{back}_17_{ankle}_Jar"],
                f"{leg}{back}_17_{ankle}_2_Jcr" : [f"{leg}{back}_17_{ankle}_Jar"],
                f"{leg}{back}_17_{ankle}_3_Jcr" : [f"{leg}{back}_17_{ankle}_Jar"],
                f"{leg}{back}_17_Jnt" : [f"{leg}{back}_16_Jnt"],
                f"{leg}{back}_18_Jnt" : [f"{leg}{back}_17_Jnt", f"{leg}{back}_17_{knee}B_Jar"],
                f"{leg}{back}_19_Jnt" : [f"{leg}{back}_18_Jnt"],
                f"{leg}{back}_19_{ankle}_Jnt" : [f"{leg}{back}_18_Jnt"],
                f"{leg}{back}_19_{ankle}_Jar" : [f"{leg}{back}_19_{ankle}_Jnt", f"{leg}{back}_18_Jnt", f"{leg}{back}_13_{knee}_Jar", f"{leg}{back}_{knee}B_Jnt"],
                f"{leg}{back}_19_{ankle}_0_Jcr" : [f"{leg}{back}_19_{ankle}_Jar"],
                f"{leg}{back}_19_{ankle}_1_Jcr" : [f"{leg}{back}_19_{ankle}_Jar"],
                f"{leg}{back}_19_{ankle}_2_Jcr" : [f"{leg}{back}_19_{ankle}_Jar"],
                f"{leg}{back}_19_{ankle}_3_Jcr" : [f"{leg}{back}_19_{ankle}_Jar"],
                f"{leg}{back}_20_Jnt" : [f"{leg}{back}_19_Jnt"],
                f"{leg}{back}_21_Jnt" : [f"{leg}{back}_20_Jnt"],
                f"{leg}{back}_22_Jnt" : [f"{leg}{back}_21_Jnt"],
                f"{leg}{back}_23_Jnt" : [f"{leg}{back}_22_Jnt"],
                f"{leg}{back}_24_Jnt" : [f"{leg}{back}_23_Jnt"],
                f"{leg}{back}_25_{ankle}_Jnt" : [f"{leg}{back}_24_Jnt"],
                f"{leg}{back}_25_{ankle}_Jar" : [f"{leg}{back}_25_{ankle}_Jnt", f"{leg}{back}_24_Jnt"],
                f"{leg}{back}_25_{ankle}_0_Jcr" : [f"{leg}{back}_25_{ankle}_Jar"],
                f"{leg}{back}_25_{ankle}_1_Jcr" : [f"{leg}{back}_25_{ankle}_Jar"],
                f"{leg}{back}_25_{ankle}_2_Jcr" : [f"{leg}{back}_25_{ankle}_Jar"],
                f"{leg}{back}_25_{ankle}_3_Jcr" : [f"{leg}{back}_25_{ankle}_Jar"],
                # foot
                f"{foot}{back}_{ankle}_Jnt" : [f"{leg}{back}_25_{ankle}_Jar", f"{leg}{back}_19_{ankle}_Jar", f"{leg}{back}_17_{ankle}_Jar", f"{leg}{back}_13_{ankle}_Jar", f"{leg}{back}_09_{ankle}_Jar", f"{leg}{back}_25_{ankle}_Jnt", f"{leg}{back}_19_{ankle}_Jnt", f"{leg}{back}_17_{ankle}_Jnt", f"{leg}{back}_13_{ankle}_Jnt", f"{leg}{back}_09_{ankle}_Jnt", f"{leg}{back}_{knee}_Jar", f"{leg}{back}_{knee}_Jnt", f"{leg}{back}_09_Jnt", f"{leg}{back}_13_Jnt", f"{leg}{back}_19_Jnt"],
                f"{foot}{back}_{middle}_Jnt" : [f"{foot}{back}_{ankle}_Jar", f"{foot}{back}_{ankle}_Jnt"],
                # toes
                f"{toe}{back}_1_00_Jnt" : [f"{foot}{back}_{middle}_Jar", f"{foot}{back}_{middle}_Jnt"],
                f"{toe}{back}_1_01_Jnt" : [f"{toe}{back}_1_00_Jnt"],
                f"{toe}{back}_1_02_Jnt" : [f"{toe}{back}_1_01_Jnt"],
                f"{toe}{back}_2_00_Jnt" : [f"{foot}{back}_{middle}_Jar", f"{foot}{back}_{middle}_Jnt"],
                f"{toe}{back}_2_01_Jnt" : [f"{toe}{back}_2_00_Jnt"],
                f"{toe}{back}_2_02_Jnt" : [f"{toe}{back}_2_01_Jnt"],
                f"{toe}{back}_3_00_Jnt" : [f"{foot}{back}_{middle}_Jar", f"{foot}{back}_{middle}_Jnt"],
                f"{toe}{back}_3_01_Jnt" : [f"{toe}{back}_3_00_Jnt"],
                f"{toe}{back}_3_02_Jnt" : [f"{toe}{back}_3_01_Jnt"],
                f"{toe}{back}_4_00_Jnt" : [f"{foot}{back}_{middle}_Jar", f"{foot}{back}_{middle}_Jnt"],
                f"{toe}{back}_4_01_Jnt" : [f"{toe}{back}_4_00_Jnt"],
                f"{toe}{back}_4_02_Jnt" : [f"{toe}{back}_4_01_Jnt"],
                f"{toe}{back}_5_00_Jnt" : [f"{foot}{back}_{middle}_Jar", f"{foot}{back}_{middle}_Jnt"],
                f"{toe}{back}_5_01_Jnt" : [f"{toe}{back}_5_00_Jnt"],
                f"{toe}{back}_5_02_Jnt" : [f"{toe}{back}_5_01_Jnt"],
                # front
                f"{leg}{front}_{hip}_Jar" : [f"{leg}{front}_{hip}_Jnt"],
                f"{leg}{front}_{hip}_0_Jcr" : [f"{leg}{front}_{hip}_Jnt"],
                f"{leg}{front}_{leg}_Jnt" : [f"{leg}{front}_{hip}_Jnt"],
                f"{leg}{front}_{knee}_Jar" : [f"{leg}{front}_{knee}_Jnt", f"{leg}{front}_{leg}_Jnt"],
                f"{leg}{front}_{knee}_0_Jcr" : [f"{leg}{front}_{knee}_Jar"],
                f"{leg}{front}_{knee}_1_Jcr" : [f"{leg}{front}_{knee}_Jar"],
                f"{leg}{front}_{knee}_2_Jcr" : [f"{leg}{front}_{knee}_Jar"],
                f"{leg}{front}_{knee}_Jnt" : [f"{leg}{front}_{leg}_Jnt"],
                f"{leg}{front}_{ankle}_Jnt" : [f"{leg}{front}_{knee}_Jar", f"{leg}{front}_{knee}_Jnt", f"{leg}{front}_09_Jnt", f"{leg}{front}_13_Jnt", f"{leg}{front}_19_Jnt"],
                f"{leg}{front}_{ankle}_0_Jcr" : [f"{leg}{front}_13_{ankle}_Jar"],
                f"{leg}{front}_{ankle}_1_Jcr" : [f"{leg}{front}_13_{ankle}_Jar"],
                f"{leg}{front}_{ankle}_2_Jcr" : [f"{leg}{front}_13_{ankle}_Jar"],
                f"{leg}{front}_{ankle}_3_Jcr" : [f"{leg}{front}_13_{ankle}_Jar"],
                f"{leg}{front}_00_{hip}_Jar" : [f"{leg}{front}_00_{hip}_Jnt"],
                f"{leg}{front}_00_{hip}_0_Jcr" : [f"{leg}{front}_00_{hip}_Jar", f"{leg}{front}_00_{hip}_Jnt"],
                f"{leg}{front}_01_{leg}_Jar" : [f"{leg}{front}_00_{leg}_Jnt", f"{leg}{front}_00_{hip}_Jnt", f"{leg}{front}_{leg}_Jnt"],
                f"{leg}{front}_{leg}_0_Jcr" : [f"{leg}{front}_01_{leg}_Jar"],
                f"{leg}{front}_{leg}_1_Jcr" : [f"{leg}{front}_01_{leg}_Jar"],
                f"{leg}{front}_02_Jnt" : [f"{leg}{front}_01_{leg}_Jar", f"{leg}{front}_01_Jnt"],
                f"{leg}{front}_03_Jnt" : [f"{leg}{front}_02_Jnt"],
                f"{leg}{front}_04_Jnt" : [f"{leg}{front}_03_Jnt"],
                f"{leg}{front}_05_Jnt" : [f"{leg}{front}_04_Jnt"],
                f"{leg}{front}_05_{knee}_Jar" : [f"{leg}{front}_04_Jnt"],
                f"{leg}{front}_05_{knee}_0_Jcr" : [f"{leg}{front}_05_{knee}_Jar"],
                f"{leg}{front}_05_{knee}_1_Jcr" : [f"{leg}{front}_05_{knee}_Jar"],
                f"{leg}{front}_05_{knee}_2_Jcr" : [f"{leg}{front}_05_{knee}_Jar"],
                f"{leg}{front}_06_Jnt" : [f"{leg}{front}_05_{knee}_Jar", f"{leg}{front}_05_Jnt", f"{leg}{front}_05_{knee}B_Jar"],
                f"{leg}{front}_07_Jnt" : [f"{leg}{front}_06_Jnt"],
                f"{leg}{front}_07_{knee}_Jar" : [f"{leg}{front}_06_Jnt", f"{leg}{front}_{knee}_Jnt"],
                f"{leg}{front}_07_{knee}_0_Jcr" : [f"{leg}{front}_07_{knee}_Jar"],
                f"{leg}{front}_07_{knee}_1_Jcr" : [f"{leg}{front}_07_{knee}_Jar"],
                f"{leg}{front}_07_{knee}_2_Jcr" : [f"{leg}{front}_07_{knee}_Jar"],
                f"{leg}{front}_08_Jnt" : [f"{leg}{front}_07_{knee}_Jar", f"{leg}{front}_07_Jnt", f"{leg}{front}_07_{knee}B_Jar"],
                f"{leg}{front}_09_Jnt" : [f"{leg}{front}_08_Jnt"],
                f"{leg}{front}_09_{knee}_Jar" : [f"{leg}{front}_08_Jnt"],
                f"{leg}{front}_09_{knee}_0_Jcr" : [f"{leg}{front}_09_{knee}_Jar"],
                f"{leg}{front}_09_{knee}_1_Jcr" : [f"{leg}{front}_09_{knee}_Jar"],
                f"{leg}{front}_09_{knee}_2_Jcr" : [f"{leg}{front}_09_{knee}_Jar"],
                f"{leg}{front}_09_{knee}B_Jar" : [f"{leg}{front}_08_Jnt"],
                f"{leg}{front}_09_{knee}B_0_Jcr" : [f"{leg}{front}_09_{knee}B_Jar"],
                f"{leg}{front}_09_{knee}B_1_Jcr" : [f"{leg}{front}_09_{knee}B_Jar"],
                f"{leg}{front}_09_{knee}B_2_Jcr" : [f"{leg}{front}_09_{knee}B_Jar"],
                f"{leg}{front}_09_{ankle}_Jnt" : [f"{leg}{front}_08_Jnt"],
                f"{leg}{front}_09_{ankle}_Jar" : [f"{leg}{front}_09_{ankle}_Jnt", f"{leg}{front}_08_Jnt"],
                f"{leg}{front}_09_{ankle}_0_Jcr" : [f"{leg}{front}_09_{ankle}_Jar"],
                f"{leg}{front}_09_{ankle}_1_Jcr" : [f"{leg}{front}_09_{ankle}_Jar"],
                f"{leg}{front}_09_{ankle}_2_Jcr" : [f"{leg}{front}_09_{ankle}_Jar"],
                f"{leg}{front}_09_{ankle}_3_Jcr" : [f"{leg}{front}_09_{ankle}_Jar"],
                f"{leg}{front}_10_Jnt" : [f"{leg}{front}_09_{knee}_Jar", f"{leg}{front}_09_Jnt", f"{leg}{front}_09_{knee}B_Jar"],
                f"{leg}{front}_11_Jnt" : [f"{leg}{front}_10_Jnt"],
                f"{leg}{front}_12_Jnt" : [f"{leg}{front}_11_Jnt"],
                f"{leg}{front}_{knee}B_Jnt" : [f"{leg}{front}_07_{knee}_Jar", f"{leg}{front}_{knee}_Jnt"],
                f"{leg}{front}_13_{knee}B_Jar" : [f"{leg}{front}_12_Jnt", f"{leg}{front}_{knee}B_Jnt"],
                f"{leg}{front}_13_{knee}B_0_Jcr" : [f"{leg}{front}_13_{knee}B_Jar"],
                f"{leg}{front}_13_{knee}B_1_Jcr" : [f"{leg}{front}_13_{knee}B_Jar"],
                f"{leg}{front}_13_{knee}B_2_Jcr" : [f"{leg}{front}_13_{knee}B_Jar"],
                f"{leg}{front}_13_{ankle}_Jnt" : [f"{leg}{front}_12_Jnt"],
                f"{leg}{front}_13_{ankle}_Jar" : [f"{leg}{front}_13_{ankle}_Jnt", f"{leg}{front}_12_Jnt", f"{leg}{front}_{knee}_Jnt"],
                f"{leg}{front}_13_{ankle}_0_Jcr" : [f"{leg}{front}_13_{ankle}_Jar"],
                f"{leg}{front}_13_{ankle}_1_Jcr" : [f"{leg}{front}_13_{ankle}_Jar"],
                f"{leg}{front}_13_{ankle}_2_Jcr" : [f"{leg}{front}_13_{ankle}_Jar"],
                f"{leg}{front}_13_{ankle}_3_Jcr" : [f"{leg}{front}_13_{ankle}_Jar"],
                f"{leg}{front}_13_Jnt" : [f"{leg}{front}_12_Jnt"],
                f"{leg}{front}_14_Jnt" : [f"{leg}{front}_13_Jnt", f"{leg}{front}_13_{knee}B_Jar"],
                f"{leg}{front}_15_Jnt" : [f"{leg}{front}_14_Jnt"],
                f"{leg}{front}_16_Jnt" : [f"{leg}{front}_15_Jnt"],
                f"{leg}{front}_17_{knee}B_Jar" : [f"{leg}{front}_16_Jnt"],
                f"{leg}{front}_17_{knee}B_0_Jcr" : [f"{leg}{front}_17_{knee}B_Jar"],
                f"{leg}{front}_17_{knee}B_1_Jcr" : [f"{leg}{front}_17_{knee}B_Jar"],
                f"{leg}{front}_17_{knee}B_2_Jcr" : [f"{leg}{front}_17_{knee}B_Jar"],
                f"{leg}{front}_17_{ankle}_Jnt" : [f"{leg}{front}_16_Jnt"],
                f"{leg}{front}_17_{ankle}_Jar" : [f"{leg}{front}_17_{ankle}_Jnt", f"{leg}{front}_16_Jnt"],
                f"{leg}{front}_17_{ankle}_0_Jcr" : [f"{leg}{front}_17_{ankle}_Jar"],
                f"{leg}{front}_17_{ankle}_1_Jcr" : [f"{leg}{front}_17_{ankle}_Jar"],
                f"{leg}{front}_17_{ankle}_2_Jcr" : [f"{leg}{front}_17_{ankle}_Jar"],
                f"{leg}{front}_17_{ankle}_3_Jcr" : [f"{leg}{front}_17_{ankle}_Jar"],
                f"{leg}{front}_17_Jnt" : [f"{leg}{front}_16_Jnt"],
                f"{leg}{front}_18_Jnt" : [f"{leg}{front}_17_Jnt", f"{leg}{front}_17_{knee}B_Jar"],
                f"{leg}{front}_19_Jnt" : [f"{leg}{front}_18_Jnt"],
                f"{leg}{front}_19_{ankle}_Jnt" : [f"{leg}{front}_18_Jnt"],
                f"{leg}{front}_19_{ankle}_Jar" : [f"{leg}{front}_19_{ankle}_Jnt", f"{leg}{front}_18_Jnt", f"{leg}{front}_13_{knee}_Jar", f"{leg}{front}_{knee}B_Jnt"],
                f"{leg}{front}_19_{ankle}_0_Jcr" : [f"{leg}{front}_19_{ankle}_Jar"],
                f"{leg}{front}_19_{ankle}_1_Jcr" : [f"{leg}{front}_19_{ankle}_Jar"],
                f"{leg}{front}_19_{ankle}_2_Jcr" : [f"{leg}{front}_19_{ankle}_Jar"],
                f"{leg}{front}_19_{ankle}_3_Jcr" : [f"{leg}{front}_19_{ankle}_Jar"],
                f"{leg}{front}_20_Jnt" : [f"{leg}{front}_19_Jnt"],
                f"{leg}{front}_21_Jnt" : [f"{leg}{front}_20_Jnt"],
                f"{leg}{front}_22_Jnt" : [f"{leg}{front}_21_Jnt"],
                f"{leg}{front}_23_Jnt" : [f"{leg}{front}_22_Jnt"],
                f"{leg}{front}_24_Jnt" : [f"{leg}{front}_23_Jnt"],
                f"{leg}{front}_25_{ankle}_Jnt" : [f"{leg}{front}_24_Jnt"],
                f"{leg}{front}_25_{ankle}_Jar" : [f"{leg}{front}_25_{ankle}_Jnt", f"{leg}{front}_24_Jnt"],
                f"{leg}{front}_25_{ankle}_0_Jcr" : [f"{leg}{front}_25_{ankle}_Jar"],
                f"{leg}{front}_25_{ankle}_1_Jcr" : [f"{leg}{front}_25_{ankle}_Jar"],
                f"{leg}{front}_25_{ankle}_2_Jcr" : [f"{leg}{front}_25_{ankle}_Jar"],
                f"{leg}{front}_25_{ankle}_3_Jcr" : [f"{leg}{front}_25_{ankle}_Jar"],
                # foot
                f"{foot}{front}_{ankle}_Jnt" : [f"{leg}{front}_25_{ankle}_Jar", f"{leg}{front}_19_{ankle}_Jar", f"{leg}{front}_17_{ankle}_Jar", f"{leg}{front}_13_{ankle}_Jar", f"{leg}{front}_09_{ankle}_Jar", f"{leg}{front}_25_{ankle}_Jnt", f"{leg}{front}_19_{ankle}_Jnt", f"{leg}{front}_17_{ankle}_Jnt", f"{leg}{front}_13_{ankle}_Jnt", f"{leg}{front}_09_{ankle}_Jnt", f"{leg}{front}_{knee}_Jar", f"{leg}{front}_{knee}_Jnt", f"{leg}{front}_09_Jnt", f"{leg}{front}_13_Jnt", f"{leg}{front}_19_Jnt"],
                f"{foot}{front}_{middle}_Jnt" : [f"{foot}{front}_{ankle}_Jar", f"{foot}{front}_{ankle}_Jnt"],
                # toes
                f"{toe}{front}_1_00_Jnt" : [f"{foot}{front}_{middle}_Jar", f"{foot}{front}_{middle}_Jnt"],
                f"{toe}{front}_1_01_Jnt" : [f"{toe}{front}_1_00_Jnt"],
                f"{toe}{front}_1_02_Jnt" : [f"{toe}{front}_1_01_Jnt"],
                f"{toe}{front}_2_00_Jnt" : [f"{foot}{front}_{middle}_Jar", f"{foot}{front}_{middle}_Jnt"],
                f"{toe}{front}_2_01_Jnt" : [f"{toe}{front}_2_00_Jnt"],
                f"{toe}{front}_2_02_Jnt" : [f"{toe}{front}_2_01_Jnt"],
                f"{toe}{front}_3_00_Jnt" : [f"{foot}{front}_{middle}_Jar", f"{foot}{front}_{middle}_Jnt"],
                f"{toe}{front}_3_01_Jnt" : [f"{toe}{front}_3_00_Jnt"],
                f"{toe}{front}_3_02_Jnt" : [f"{toe}{front}_3_01_Jnt"],
                f"{toe}{front}_4_00_Jnt" : [f"{foot}{front}_{middle}_Jar", f"{foot}{front}_{middle}_Jnt"],
                f"{toe}{front}_4_01_Jnt" : [f"{toe}{front}_4_00_Jnt"],
                f"{toe}{front}_4_02_Jnt" : [f"{toe}{front}_4_01_Jnt"],
                f"{toe}{front}_5_00_Jnt" : [f"{foot}{front}_{middle}_Jar", f"{foot}{front}_{middle}_Jnt"],
                f"{toe}{front}_5_01_Jnt" : [f"{toe}{front}_5_00_Jnt"],
                f"{toe}{front}_5_02_Jnt" : [f"{toe}{front}_5_01_Jnt"],

                # additional ribbons
                f"{arm}_02_01_Jad" : [f"{arm}_02_Jnt"],
                f"{arm}_02_02_Jad" : [f"{arm}_02_Jnt"],
                f"{arm}_02_03_Jad" : [f"{arm}_02_Jnt"],
                f"{arm}_02_04_Jad" : [f"{arm}_02_Jnt"],
                f"{arm}_03_01_Jad" : [f"{arm}_03_Jnt"],
                f"{arm}_03_02_Jad" : [f"{arm}_03_Jnt"],
                f"{arm}_03_03_Jad" : [f"{arm}_03_Jnt"],
                f"{arm}_03_04_Jad" : [f"{arm}_03_Jnt"],
                f"{arm}_04_01_Jad" : [f"{arm}_04_Jnt"],
                f"{arm}_04_02_Jad" : [f"{arm}_04_Jnt"],
                f"{arm}_04_03_Jad" : [f"{arm}_04_Jnt"],
                f"{arm}_04_04_Jad" : [f"{arm}_04_Jnt"],
                f"{arm}_05_01_Jad" : [f"{arm}_05_Jnt"],
                f"{arm}_05_02_Jad" : [f"{arm}_05_Jnt"],
                f"{arm}_05_03_Jad" : [f"{arm}_05_Jnt"],
                f"{arm}_05_04_Jad" : [f"{arm}_05_Jnt"],
                f"{arm}_06_01_Jad" : [f"{arm}_06_Jnt"],
                f"{arm}_06_02_Jad" : [f"{arm}_06_Jnt"],
                f"{arm}_06_03_Jad" : [f"{arm}_06_Jnt"],
                f"{arm}_06_04_Jad" : [f"{arm}_06_Jnt"],
                f"{arm}_07_01_Jad" : [f"{arm}_07_Jnt"],
                f"{arm}_07_02_Jad" : [f"{arm}_07_Jnt"],
                f"{arm}_07_03_Jad" : [f"{arm}_07_Jnt"],
                f"{arm}_07_04_Jad" : [f"{arm}_07_Jnt"],
                f"{arm}_08_01_Jad" : [f"{arm}_08_Jnt"],
                f"{arm}_08_02_Jad" : [f"{arm}_08_Jnt"],
                f"{arm}_08_03_Jad" : [f"{arm}_08_Jnt"],
                f"{arm}_08_04_Jad" : [f"{arm}_08_Jnt"],
                f"{arm}_09_01_Jad" : [f"{arm}_09_Jnt"],
                f"{arm}_09_02_Jad" : [f"{arm}_09_Jnt"],
                f"{arm}_09_03_Jad" : [f"{arm}_09_Jnt"],
                f"{arm}_09_04_Jad" : [f"{arm}_09_Jnt"],
                f"{arm}_10_01_Jad" : [f"{arm}_10_Jnt"],
                f"{arm}_10_02_Jad" : [f"{arm}_10_Jnt"],
                f"{arm}_10_03_Jad" : [f"{arm}_10_Jnt"],
                f"{arm}_10_04_Jad" : [f"{arm}_10_Jnt"],
                f"{arm}_11_01_Jad" : [f"{arm}_11_Jnt"],
                f"{arm}_11_02_Jad" : [f"{arm}_11_Jnt"],
                f"{arm}_11_03_Jad" : [f"{arm}_11_Jnt"],
                f"{arm}_11_04_Jad" : [f"{arm}_11_Jnt"],
                f"{arm}_12_01_Jad" : [f"{arm}_12_Jnt"],
                f"{arm}_12_02_Jad" : [f"{arm}_12_Jnt"],
                f"{arm}_12_03_Jad" : [f"{arm}_12_Jnt"],
                f"{arm}_12_04_Jad" : [f"{arm}_12_Jnt"],
                f"{arm}_13_01_Jad" : [f"{arm}_13_Jnt"],
                f"{arm}_13_02_Jad" : [f"{arm}_13_Jnt"],
                f"{arm}_13_03_Jad" : [f"{arm}_13_Jnt"],
                f"{arm}_13_04_Jad" : [f"{arm}_13_Jnt"],
                f"{arm}_14_01_Jad" : [f"{arm}_14_Jnt"],
                f"{arm}_14_02_Jad" : [f"{arm}_14_Jnt"],
                f"{arm}_14_03_Jad" : [f"{arm}_14_Jnt"],
                f"{arm}_14_04_Jad" : [f"{arm}_14_Jnt"],
                f"{arm}_15_01_Jad" : [f"{arm}_15_Jnt"],
                f"{arm}_15_02_Jad" : [f"{arm}_15_Jnt"],
                f"{arm}_15_03_Jad" : [f"{arm}_15_Jnt"],
                f"{arm}_15_04_Jad" : [f"{arm}_15_Jnt"],
                f"{arm}_16_01_Jad" : [f"{arm}_16_Jnt"],
                f"{arm}_16_02_Jad" : [f"{arm}_16_Jnt"],
                f"{arm}_16_03_Jad" : [f"{arm}_16_Jnt"],
                f"{arm}_16_04_Jad" : [f"{arm}_16_Jnt"],
                f"{leg}_02_01_Jad" : [f"{leg}_02_Jnt"],
                f"{leg}_02_02_Jad" : [f"{leg}_02_Jnt"],
                f"{leg}_02_03_Jad" : [f"{leg}_02_Jnt"],
                f"{leg}_02_04_Jad" : [f"{leg}_02_Jnt"],
                f"{leg}_03_01_Jad" : [f"{leg}_03_Jnt"],
                f"{leg}_03_02_Jad" : [f"{leg}_03_Jnt"],
                f"{leg}_03_03_Jad" : [f"{leg}_03_Jnt"],
                f"{leg}_03_04_Jad" : [f"{leg}_03_Jnt"],
                f"{leg}_04_01_Jad" : [f"{leg}_04_Jnt"],
                f"{leg}_04_02_Jad" : [f"{leg}_04_Jnt"],
                f"{leg}_04_03_Jad" : [f"{leg}_04_Jnt"],
                f"{leg}_04_04_Jad" : [f"{leg}_04_Jnt"],
                f"{leg}_05_01_Jad" : [f"{leg}_05_Jnt"],
                f"{leg}_05_02_Jad" : [f"{leg}_05_Jnt"],
                f"{leg}_05_03_Jad" : [f"{leg}_05_Jnt"],
                f"{leg}_05_04_Jad" : [f"{leg}_05_Jnt"],
                f"{leg}_06_01_Jad" : [f"{leg}_06_Jnt"],
                f"{leg}_06_02_Jad" : [f"{leg}_06_Jnt"],
                f"{leg}_06_03_Jad" : [f"{leg}_06_Jnt"],
                f"{leg}_06_04_Jad" : [f"{leg}_06_Jnt"],
                f"{leg}_07_01_Jad" : [f"{leg}_07_Jnt"],
                f"{leg}_07_02_Jad" : [f"{leg}_07_Jnt"],
                f"{leg}_07_03_Jad" : [f"{leg}_07_Jnt"],
                f"{leg}_07_04_Jad" : [f"{leg}_07_Jnt"],
                f"{leg}_08_01_Jad" : [f"{leg}_08_Jnt"],
                f"{leg}_08_02_Jad" : [f"{leg}_08_Jnt"],
                f"{leg}_08_03_Jad" : [f"{leg}_08_Jnt"],
                f"{leg}_08_04_Jad" : [f"{leg}_08_Jnt"],
                f"{leg}_09_01_Jad" : [f"{leg}_09_Jnt"],
                f"{leg}_09_02_Jad" : [f"{leg}_09_Jnt"],
                f"{leg}_09_03_Jad" : [f"{leg}_09_Jnt"],
                f"{leg}_09_04_Jad" : [f"{leg}_09_Jnt"],
                f"{leg}_10_01_Jad" : [f"{leg}_10_Jnt"],
                f"{leg}_10_02_Jad" : [f"{leg}_10_Jnt"],
                f"{leg}_10_03_Jad" : [f"{leg}_10_Jnt"],
                f"{leg}_10_04_Jad" : [f"{leg}_10_Jnt"],
                f"{leg}_11_01_Jad" : [f"{leg}_11_Jnt"],
                f"{leg}_11_02_Jad" : [f"{leg}_11_Jnt"],
                f"{leg}_11_03_Jad" : [f"{leg}_11_Jnt"],
                f"{leg}_11_04_Jad" : [f"{leg}_11_Jnt"],
                f"{leg}_12_01_Jad" : [f"{leg}_12_Jnt"],
                f"{leg}_12_02_Jad" : [f"{leg}_12_Jnt"],
                f"{leg}_12_03_Jad" : [f"{leg}_12_Jnt"],
                f"{leg}_12_04_Jad" : [f"{leg}_12_Jnt"],
                f"{leg}_13_01_Jad" : [f"{leg}_13_Jnt"],
                f"{leg}_13_02_Jad" : [f"{leg}_13_Jnt"],
                f"{leg}_13_03_Jad" : [f"{leg}_13_Jnt"],
                f"{leg}_13_04_Jad" : [f"{leg}_13_Jnt"],
                f"{leg}_14_01_Jad" : [f"{leg}_14_Jnt"],
                f"{leg}_14_02_Jad" : [f"{leg}_14_Jnt"],
                f"{leg}_14_03_Jad" : [f"{leg}_14_Jnt"],
                f"{leg}_14_04_Jad" : [f"{leg}_14_Jnt"],
                f"{leg}_15_01_Jad" : [f"{leg}_15_Jnt"],
                f"{leg}_15_02_Jad" : [f"{leg}_15_Jnt"],
                f"{leg}_15_03_Jad" : [f"{leg}_15_Jnt"],
                f"{leg}_15_04_Jad" : [f"{leg}_15_Jnt"],
                f"{leg}_16_01_Jad" : [f"{leg}_16_Jnt"],
                f"{leg}_16_02_Jad" : [f"{leg}_16_Jnt"],
                f"{leg}_16_03_Jad" : [f"{leg}_16_Jnt"],
                f"{leg}_16_04_Jad" : [f"{leg}_16_Jnt"],
                f"{leg}{back}_02_01_Jad" : [f"{leg}{back}_02_Jnt"],
                f"{leg}{back}_02_02_Jad" : [f"{leg}{back}_02_Jnt"],
                f"{leg}{back}_02_03_Jad" : [f"{leg}{back}_02_Jnt"],
                f"{leg}{back}_02_04_Jad" : [f"{leg}{back}_02_Jnt"],
                f"{leg}{back}_03_01_Jad" : [f"{leg}{back}_03_Jnt"],
                f"{leg}{back}_03_02_Jad" : [f"{leg}{back}_03_Jnt"],
                f"{leg}{back}_03_03_Jad" : [f"{leg}{back}_03_Jnt"],
                f"{leg}{back}_03_04_Jad" : [f"{leg}{back}_03_Jnt"],
                f"{leg}{back}_04_01_Jad" : [f"{leg}{back}_04_Jnt"],
                f"{leg}{back}_04_02_Jad" : [f"{leg}{back}_04_Jnt"],
                f"{leg}{back}_04_03_Jad" : [f"{leg}{back}_04_Jnt"],
                f"{leg}{back}_04_04_Jad" : [f"{leg}{back}_04_Jnt"],
                f"{leg}{back}_05_01_Jad" : [f"{leg}{back}_05_Jnt"],
                f"{leg}{back}_05_02_Jad" : [f"{leg}{back}_05_Jnt"],
                f"{leg}{back}_05_03_Jad" : [f"{leg}{back}_05_Jnt"],
                f"{leg}{back}_05_04_Jad" : [f"{leg}{back}_05_Jnt"],
                f"{leg}{back}_06_01_Jad" : [f"{leg}{back}_06_Jnt"],
                f"{leg}{back}_06_02_Jad" : [f"{leg}{back}_06_Jnt"],
                f"{leg}{back}_06_03_Jad" : [f"{leg}{back}_06_Jnt"],
                f"{leg}{back}_06_04_Jad" : [f"{leg}{back}_06_Jnt"],
                f"{leg}{back}_07_01_Jad" : [f"{leg}{back}_07_Jnt"],
                f"{leg}{back}_07_02_Jad" : [f"{leg}{back}_07_Jnt"],
                f"{leg}{back}_07_03_Jad" : [f"{leg}{back}_07_Jnt"],
                f"{leg}{back}_07_04_Jad" : [f"{leg}{back}_07_Jnt"],
                f"{leg}{back}_08_01_Jad" : [f"{leg}{back}_08_Jnt"],
                f"{leg}{back}_08_02_Jad" : [f"{leg}{back}_08_Jnt"],
                f"{leg}{back}_08_03_Jad" : [f"{leg}{back}_08_Jnt"],
                f"{leg}{back}_08_04_Jad" : [f"{leg}{back}_08_Jnt"],
                f"{leg}{back}_09_01_Jad" : [f"{leg}{back}_09_Jnt"],
                f"{leg}{back}_09_02_Jad" : [f"{leg}{back}_09_Jnt"],
                f"{leg}{back}_09_03_Jad" : [f"{leg}{back}_09_Jnt"],
                f"{leg}{back}_09_04_Jad" : [f"{leg}{back}_09_Jnt"],
                f"{leg}{back}_10_01_Jad" : [f"{leg}{back}_10_Jnt"],
                f"{leg}{back}_10_02_Jad" : [f"{leg}{back}_10_Jnt"],
                f"{leg}{back}_10_03_Jad" : [f"{leg}{back}_10_Jnt"],
                f"{leg}{back}_10_04_Jad" : [f"{leg}{back}_10_Jnt"],
                f"{leg}{back}_11_01_Jad" : [f"{leg}{back}_11_Jnt"],
                f"{leg}{back}_11_02_Jad" : [f"{leg}{back}_11_Jnt"],
                f"{leg}{back}_11_03_Jad" : [f"{leg}{back}_11_Jnt"],
                f"{leg}{back}_11_04_Jad" : [f"{leg}{back}_11_Jnt"],
                f"{leg}{back}_12_01_Jad" : [f"{leg}{back}_12_Jnt"],
                f"{leg}{back}_12_02_Jad" : [f"{leg}{back}_12_Jnt"],
                f"{leg}{back}_12_03_Jad" : [f"{leg}{back}_12_Jnt"],
                f"{leg}{back}_12_04_Jad" : [f"{leg}{back}_12_Jnt"],
                f"{leg}{back}_13_01_Jad" : [f"{leg}{back}_13_Jnt"],
                f"{leg}{back}_13_02_Jad" : [f"{leg}{back}_13_Jnt"],
                f"{leg}{back}_13_03_Jad" : [f"{leg}{back}_13_Jnt"],
                f"{leg}{back}_13_04_Jad" : [f"{leg}{back}_13_Jnt"],
                f"{leg}{back}_14_01_Jad" : [f"{leg}{back}_14_Jnt"],
                f"{leg}{back}_14_02_Jad" : [f"{leg}{back}_14_Jnt"],
                f"{leg}{back}_14_03_Jad" : [f"{leg}{back}_14_Jnt"],
                f"{leg}{back}_14_04_Jad" : [f"{leg}{back}_14_Jnt"],
                f"{leg}{back}_15_01_Jad" : [f"{leg}{back}_15_Jnt"],
                f"{leg}{back}_15_02_Jad" : [f"{leg}{back}_15_Jnt"],
                f"{leg}{back}_15_03_Jad" : [f"{leg}{back}_15_Jnt"],
                f"{leg}{back}_15_04_Jad" : [f"{leg}{back}_15_Jnt"],
                f"{leg}{back}_16_01_Jad" : [f"{leg}{back}_16_Jnt"],
                f"{leg}{back}_16_02_Jad" : [f"{leg}{back}_16_Jnt"],
                f"{leg}{back}_16_03_Jad" : [f"{leg}{back}_16_Jnt"],
                f"{leg}{back}_16_04_Jad" : [f"{leg}{back}_16_Jnt"],
                f"{leg}{front}_02_01_Jad" : [f"{leg}{front}_02_Jnt"],
                f"{leg}{front}_02_02_Jad" : [f"{leg}{front}_02_Jnt"],
                f"{leg}{front}_02_03_Jad" : [f"{leg}{front}_02_Jnt"],
                f"{leg}{front}_02_04_Jad" : [f"{leg}{front}_02_Jnt"],
                f"{leg}{front}_03_01_Jad" : [f"{leg}{front}_03_Jnt"],
                f"{leg}{front}_03_02_Jad" : [f"{leg}{front}_03_Jnt"],
                f"{leg}{front}_03_03_Jad" : [f"{leg}{front}_03_Jnt"],
                f"{leg}{front}_03_04_Jad" : [f"{leg}{front}_03_Jnt"],
                f"{leg}{front}_04_01_Jad" : [f"{leg}{front}_04_Jnt"],
                f"{leg}{front}_04_02_Jad" : [f"{leg}{front}_04_Jnt"],
                f"{leg}{front}_04_03_Jad" : [f"{leg}{front}_04_Jnt"],
                f"{leg}{front}_04_04_Jad" : [f"{leg}{front}_04_Jnt"],
                f"{leg}{front}_05_01_Jad" : [f"{leg}{front}_05_Jnt"],
                f"{leg}{front}_05_02_Jad" : [f"{leg}{front}_05_Jnt"],
                f"{leg}{front}_05_03_Jad" : [f"{leg}{front}_05_Jnt"],
                f"{leg}{front}_05_04_Jad" : [f"{leg}{front}_05_Jnt"],
                f"{leg}{front}_06_01_Jad" : [f"{leg}{front}_06_Jnt"],
                f"{leg}{front}_06_02_Jad" : [f"{leg}{front}_06_Jnt"],
                f"{leg}{front}_06_03_Jad" : [f"{leg}{front}_06_Jnt"],
                f"{leg}{front}_06_04_Jad" : [f"{leg}{front}_06_Jnt"],
                f"{leg}{front}_07_01_Jad" : [f"{leg}{front}_07_Jnt"],
                f"{leg}{front}_07_02_Jad" : [f"{leg}{front}_07_Jnt"],
                f"{leg}{front}_07_03_Jad" : [f"{leg}{front}_07_Jnt"],
                f"{leg}{front}_07_04_Jad" : [f"{leg}{front}_07_Jnt"],
                f"{leg}{front}_08_01_Jad" : [f"{leg}{front}_08_Jnt"],
                f"{leg}{front}_08_02_Jad" : [f"{leg}{front}_08_Jnt"],
                f"{leg}{front}_08_03_Jad" : [f"{leg}{front}_08_Jnt"],
                f"{leg}{front}_08_04_Jad" : [f"{leg}{front}_08_Jnt"],
                f"{leg}{front}_09_01_Jad" : [f"{leg}{front}_09_Jnt"],
                f"{leg}{front}_09_02_Jad" : [f"{leg}{front}_09_Jnt"],
                f"{leg}{front}_09_03_Jad" : [f"{leg}{front}_09_Jnt"],
                f"{leg}{front}_09_04_Jad" : [f"{leg}{front}_09_Jnt"],
                f"{leg}{front}_10_01_Jad" : [f"{leg}{front}_10_Jnt"],
                f"{leg}{front}_10_02_Jad" : [f"{leg}{front}_10_Jnt"],
                f"{leg}{front}_10_03_Jad" : [f"{leg}{front}_10_Jnt"],
                f"{leg}{front}_10_04_Jad" : [f"{leg}{front}_10_Jnt"],
                f"{leg}{front}_11_01_Jad" : [f"{leg}{front}_11_Jnt"],
                f"{leg}{front}_11_02_Jad" : [f"{leg}{front}_11_Jnt"],
                f"{leg}{front}_11_03_Jad" : [f"{leg}{front}_11_Jnt"],
                f"{leg}{front}_11_04_Jad" : [f"{leg}{front}_11_Jnt"],
                f"{leg}{front}_12_01_Jad" : [f"{leg}{front}_12_Jnt"],
                f"{leg}{front}_12_02_Jad" : [f"{leg}{front}_12_Jnt"],
                f"{leg}{front}_12_03_Jad" : [f"{leg}{front}_12_Jnt"],
                f"{leg}{front}_12_04_Jad" : [f"{leg}{front}_12_Jnt"],
                f"{leg}{front}_13_01_Jad" : [f"{leg}{front}_13_Jnt"],
                f"{leg}{front}_13_02_Jad" : [f"{leg}{front}_13_Jnt"],
                f"{leg}{front}_13_03_Jad" : [f"{leg}{front}_13_Jnt"],
                f"{leg}{front}_13_04_Jad" : [f"{leg}{front}_13_Jnt"],
                f"{leg}{front}_14_01_Jad" : [f"{leg}{front}_14_Jnt"],
                f"{leg}{front}_14_02_Jad" : [f"{leg}{front}_14_Jnt"],
                f"{leg}{front}_14_03_Jad" : [f"{leg}{front}_14_Jnt"],
                f"{leg}{front}_14_04_Jad" : [f"{leg}{front}_14_Jnt"],
                f"{leg}{front}_15_01_Jad" : [f"{leg}{front}_15_Jnt"],
                f"{leg}{front}_15_02_Jad" : [f"{leg}{front}_15_Jnt"],
                f"{leg}{front}_15_03_Jad" : [f"{leg}{front}_15_Jnt"],
                f"{leg}{front}_15_04_Jad" : [f"{leg}{front}_15_Jnt"],
                f"{leg}{front}_16_01_Jad" : [f"{leg}{front}_16_Jnt"],
                f"{leg}{front}_16_02_Jad" : [f"{leg}{front}_16_Jnt"],
                f"{leg}{front}_16_03_Jad" : [f"{leg}{front}_16_Jnt"],
                f"{leg}{front}_16_04_Jad" : [f"{leg}{front}_16_Jnt"],

                # spine
                f"{spine}_01_Jnt" : [f"{spine}_00_{base}_Jnt", f"{spine}_00_{hips}_Jnt"],
                f"{spine}_02_Jnt" : [f"{spine}_01_Jnt"],
                f"{spine}_03_Jnt" : [f"{spine}_02_Jnt"],
                f"{spine}_04_Jnt" : [f"{spine}_03_Jnt"],
                f"{spine}_05_Jnt" : [f"{spine}_04_Jnt"],
                f"{spine}_06_Jnt" : [f"{spine}_05_Jnt"],
                f"{spine}_04_{tip}_Jnt" : [f"{spine}_03_Jnt"],
                f"{spine}_04_{chest}_Jnt" : [f"{spine}_03_Jnt"],
                f"{spine}_05_{tip}_Jnt" : [f"{spine}_04_Jnt"],
                f"{spine}_05_{chest}_Jnt" : [f"{spine}_04_Jnt"],
                f"{spine}_06_{tip}_Jnt" : [f"{spine}_05_Jnt"],
                f"{spine}_06_{chest}_Jnt" : [f"{spine}_05_Jnt"],
                f"{spine}_07_{tip}_Jnt" : [f"{spine}_06_Jnt"],
                f"{spine}_07_{chest}_Jnt" : [f"{spine}_06_Jnt"],

                # head
                f"{head}_{neck}_00_Jnt" : [f"{spine}_04_{chest}_Jnt", f"{spine}_04_{tip}_Jnt", f"{spine}_05_{chest}_Jnt", f"{spine}_05_{tip}_Jnt", f"{spine}_06_{chest}_Jnt", f"{spine}_06_{tip}_Jnt", f"{spine}_05_{chest}_Jnt", f"{spine}_05_{tip}_Jnt"],
                f"{head}_{neck}_00_Jar" : [f"{head}_{neck}_00_Jnt"],
                f"{head}_{neck}_01_Jnt" : [f"{head}_{neck}_00_Jnt"],
                f"{head}_{neck}_01_Jar" : [f"{head}_{neck}_01_Jnt"],
                f"{head}_{neck}_02_Jnt" : [f"{head}_{neck}_01_Jnt"],
                f"{head}_{neck}_02_Jar" : [f"{head}_{neck}_02_Jnt"],
                f"{head}_{neck}_03_Jnt" : [f"{head}_{neck}_02_Jnt"],
                f"{head}_{neck}_03_Jar" : [f"{head}_{neck}_03_Jnt"],
                f"{head}_{neck}_04_Jnt" : [f"{head}_{neck}_03_Jnt"],
                f"{head}_{neck}_04_Jar" : [f"{head}_{neck}_04_Jnt"],
                f"{head}_{neck}_05_Jnt" : [f"{head}_{neck}_04_Jnt"],
                f"{head}_{neck}_05_Jar" : [f"{head}_{neck}_05_Jnt"],
                f"{head}_{neck}_06_Jnt" : [f"{head}_{neck}_05_Jnt"],
                f"{head}_{neck}_06_Jar" : [f"{head}_{neck}_06_Jnt"],
                f"{head}_{neck}_07_Jnt" : [f"{head}_{neck}_06_Jnt"],
                f"{head}_{neck}_07_Jar" : [f"{head}_{neck}_07_Jnt"],
                f"{head}_01_{head}_Jnt" : [f"{head}_{neck}_07_Jar", f"{head}_{neck}_07_Jnt", f"{head}_{neck}_06_Jar", f"{head}_{neck}_06_Jnt", f"{head}_{neck}_05_Jar", f"{head}_{neck}_05_Jnt", f"{head}_{neck}_04_Jar", f"{head}_{neck}_04_Jnt", f"{head}_{neck}_03_Jar", f"{head}_{neck}_03_Jnt", f"{head}_{neck}_02_Jar", f"{head}_{neck}_02_Jnt", f"{head}_{neck}_01_Jar", f"{head}_{neck}_01_Jnt", f"{head}_{neck}_00_Jar", f"{head}_{neck}_00_Jnt"],
                f"{head}_01_{head}_Jar" : [f"{head}_01_{head}_Jnt"],
                f"{head}_02_{head}_Jnt" : [f"{head}_01_{head}_Jar", f"{head}_01_{head}_Jnt"],
                f"{head}_02_{head}_Jar" : [f"{head}_02_{head}_Jnt"],
                f"{head}_{upper}{jaw}_Jnt" : [f"{head}_01_{head}_Jar", f"{head}_01_{head}_Jnt"],
                f"{head}_{upper}{head}_Jnt" : [f"{head}_{upper}{jaw}_Jnt"],
                f"{head}_{upper}{lip}_Jnt" : [f"{head}_{upper}{jaw}_Jnt"],
                f"{head}_{jaw}_Jnt" : [f"{head}_01_{head}_Jar", f"{head}_01_{head}_Jnt"],
                f"{head}_{chin}_Jnt" : [f"{head}_{jaw}_Jnt"],
                f"{head}_{lower}{lip}_Jnt" : [f"{head}_{jaw}_Jnt"],
                f"{head}_L_{corner}{lip}_Jnt" : [f"{head}_{jaw}_Jnt"],
                f"{head}_R_{corner}{lip}_Jnt" : [f"{head}_{jaw}_Jnt"],
                f"{head}_E_{corner}{lip}_Jnt" : [f"{head}_{jaw}_Jnt"],
                f"{head}_D_{corner}{lip}_Jnt" : [f"{head}_{jaw}_Jnt"],
                f"{head}_{chew}_Jnt" : [f"{head}_{chin}_Jnt"],

                # nose
                f"{nose}_00_Jnt" : [f"{head}_{upper}{jaw}_Jnt", f"{head}_01_{head}_Jnt"],
                f"{nose}_00_Jar" : [f"{nose}_00_Jnt"],
                f"{nose}_01_Jnt" : [f"{nose}_00_Jar", f"{nose}_00_Jnt"],
                f"{nose}_01_Jar" : [f"{nose}_01_Jnt"],
                f"{nose}_02_{middle}_Jnt" : [f"{nose}_01_Jar", f"{nose}_01_Jnt"],
                f"{nose}_02_{middle}_Jar" : [f"{nose}_02_{middle}_Jnt"],
                f"{nose}_03_{tip}_Jnt" : [f"{nose}_02_{middle}_Jar", f"{nose}_02_{middle}_Jnt"],
                f"{nose}_03_{bottom}_Jnt" : [f"{nose}_02_{middle}_Jar", f"{nose}_02_{middle}_Jnt"],
                f"{nose}_04_L_Side_Jnt" : [f"{nose}_02_{middle}_Jar", f"{nose}_02_{middle}_Jnt"],
                f"{nose}_04_R_Side_Jnt" : [f"{nose}_02_{middle}_Jar", f"{nose}_02_{middle}_Jnt"],
                f"{nose}_04_E_Side_Jnt" : [f"{nose}_02_{middle}_Jar", f"{nose}_02_{middle}_Jnt"],
                f"{nose}_04_D_Side_Jnt" : [f"{nose}_02_{middle}_Jar", f"{nose}_02_{middle}_Jnt"],
                f"{nose}_05_L_{nostril}_Jnt" : [f"{nose}_04_L_Side_Jar", f"{nose}_04_L_Side_Jnt"],
                f"{nose}_05_R_{nostril}_Jnt" : [f"{nose}_04_R_Side_Jar", f"{nose}_04_R_Side_Jnt"],
                f"{nose}_05_E_{nostril}_Jnt" : [f"{nose}_04_E_Side_Jar", f"{nose}_04_E_Side_Jnt"],
                f"{nose}_05_D_{nostril}_Jnt" : [f"{nose}_04_D_Side_Jar", f"{nose}_04_D_Side_Jnt"],
                
                # ear
                f"{ear}_01_Jnt" : [f"{ear}_00_Jnt"],
                f"{ear}_02_Jnt" : [f"{ear}_01_Jnt"],
                f"{upper}{ear}_00_Jnt" : [f"{ear}_01_Jnt"],
                f"{lower}{ear}_00_Jnt" : [f"{ear}_01_Jnt"],

                # tongue
                f"{tongue}_00_Jnt" : [f"{head}_{chin}_Jnt"],
                f"{tongue}_01_Jnt" : [f"{tongue}_00_Jnt"],
                f"{tongue}_02_Jnt" : [f"{tongue}_01_Jnt"],
                f"{tongue}_03_Jnt" : [f"{tongue}_02_Jnt"],
                f"{tongue}_04_Jnt" : [f"{tongue}_03_Jnt"],

                # teeth
                f"{upper_teeth}_00_Jnt" : [f"{head}_{upper}{jaw}_Jnt", f"{head}_01_{head}_Jnt"],
                f"{lower_teeth}_00_Jnt" : [f"{head}_{chin}_Jnt", f"{head}_{jaw}_Jnt", f"{head}_01_{head}_Jnt"],
                f"{upper_teeth}{middle}_00_Jnt" : [f"{upper_teeth}_00_Jnt", f"{head}_{upper}{jaw}_Jnt", f"{head}_01_{head}_Jnt"],
                f"{lower_teeth}{middle}_00_Jnt" : [f"{lower_teeth}_00_Jnt", f"{head}_{chin}_Jnt", f"{head}_{jaw}_Jnt", f"{head}_01_{head}_Jnt"],
                
                # eye
                f"{eye}_1_Jnt" : [f"{eye}Base_1_Jnt", f"{head}_{upper}{head}_Jnt"],
                f"{eye}Scale_1_Jnt" : [f"{eye}_1_Jnt", f"{eye}Base_1_Jnt", f"{head}_{upper}{head}_Jnt"],
                f"{eye}_{iris}_1_Jnt" : [f"{eye}Scale_1_Jnt", f"{eye}_1_Jnt", f"{eye}Base_1_Jnt"],
                f"{eye}_{pupil}_1_Jnt" : [f"{eye}Scale_1_Jnt", f"{eye}_1_Jnt", f"{eye}Base_1_Jnt"],
                f"{eye}_{upper}_{eyelid}_Jnt" : [f"{eye}Scale_1_Jnt", f"{eye}_1_Jnt", f"{eye}Base_1_Jnt"],
                f"{eye}_{lower}_{eyelid}_Jnt" : [f"{eye}Scale_1_Jnt", f"{eye}_1_Jnt", f"{eye}Base_1_Jnt"],
                f"{eye}_{upper}_{eyelid}{middle}_Jnt" : [f"{eye}Scale_1_Jnt", f"{eye}_1_Jnt", f"{eye}Base_1_Jnt"],
                f"{eye}_{lower}_{eyelid}{middle}_Jnt" : [f"{eye}Scale_1_Jnt", f"{eye}_1_Jnt", f"{eye}Base_1_Jnt"],

                # singles
                f"{breath}_Jnt" : [f"{spine}_04_{chest}_Jnt", f"{spine}_04_{tip}_Jnt", f"{spine}_05_{chest}_Jnt", f"{spine}_05_{tip}_Jnt", f"{spine}_06_{chest}_Jnt", f"{spine}_06_{tip}_Jnt", f"{spine}_05_{chest}_Jnt", f"{spine}_05_{tip}_Jnt"],
                f"{belly}_Jnt" : [f"{spine}_00_{base}_Jnt", f"{spine}_00_{hips}_Jnt"],

                # tail
                f"{tail}{base}_00_Jnt" : [f"{spine}_00_{base}_Jnt", f"{spine}_00_{hips}_Jnt"],
                f"{tail}_00_Jnt" : [f"{tail}{base}_00_Jnt", f"{spine}_00_{base}_Jnt", f"{spine}_00_{hips}_Jnt"],
                f"{tail}_01_Jnt" : [f"{tail}_00_Jnt"],
                f"{tail}_02_Jnt" : [f"{tail}_01_Jnt"],
                f"{tail}_03_Jnt" : [f"{tail}_02_Jnt"],
                f"{tail}_04_Jnt" : [f"{tail}_03_Jnt"],
                f"{tail}_05_Jnt" : [f"{tail}_04_Jnt"],
                f"{tail}_06_Jnt" : [f"{tail}_05_Jnt"],
                f"{tail}_07_Jnt" : [f"{tail}_06_Jnt"],
                f"{tail}_08_Jnt" : [f"{tail}_07_Jnt"],
                f"{tail}_09_Jnt" : [f"{tail}_08_Jnt"],
                f"{tail}_10_Jnt" : [f"{tail}_09_Jnt"],

                # tweaks
                f"{tweaks}_{squint}_01_Jnt" : [f"{tweaks}_{squint}_{main}_Jnt"],
                f"{tweaks}_{squint}_02_Jnt" : [f"{tweaks}_{squint}_{main}_Jnt"],
                f"{tweaks}_{squint}_03_Jnt" : [f"{tweaks}_{squint}_{main}_Jnt"],
                f"{tweaks}_{eyebrow}_01_Jnt" : [f"{tweaks}_{eyebrow}_{main}_Jnt"],
                f"{tweaks}_{eyebrow}_02_Jnt" : [f"{tweaks}_{eyebrow}_{main}_Jnt"],
                f"{tweaks}_{eyebrow}_03_Jnt" : [f"{tweaks}_{eyebrow}_{main}_Jnt"],
                f"{tweaks}_{eyebrow}_04_Jnt" : [f"{tweaks}_{eyebrow}_{main}_Jnt"],
                f"{tweaks}_{middle}_{eyebrow}_Jnt" : [f"{head}_{upper}{head}_Jnt", f"{head}_01_{head}_Jnt"],
                f"{tweaks}_{holder}_{main}_Jnt" : [f"{head}_01_{head}_Jnt"],

                # to be integrated after
                f"{leg}_{hip}_Jnt" : [""],
                f"{leg}{back}_{hip}_Jnt" : [""],
                f"{leg}{front}_{hip}_Jnt" : [""],
                f"{arm}_{clavicle}_Jnt" : [""],
                f"{leg}_00_{hip}_Jnt" : [""],
                f"{leg}{back}_00_{hip}_Jnt" : [""],
                f"{leg}{front}_00_{hip}_Jnt" : [""],
                f"{arm}_00_{clavicle}_Jnt" : [""],
                f"{ear}_00_Jnt" : [f"{ear}{base}_00_Jnt"],
                f"{ear}{base}_00_Jnt" : [""],
                f"{upper_teeth}Side_00_Jnt" : [""],
                f"{lower_teeth}Side_00_Jnt" : [""],
                f"{eye}_1_Jnt" : [""],
                f"{tweaks}_{squint}_{main}_Jnt" : [""],
                f"{tweaks}_{cheek}_01_Jnt" : [""],
                f"{tweaks}_{cheek}_02_Jnt" : [""],
                f"{tweaks}_{eyebrow}_{main}_Jnt" : [""],
                f"{tweaks}_{lip}_{main}_Jnt" : [""],
                f"{tweaks}_{upper}_{lip}_00_Jnt" : [""],
                f"{tweaks}_{upper}_{lip}_01_Jnt" : [""],
                f"{tweaks}_{upper}_{lip}_02_Jnt" : [""],
                f"{tweaks}_{corner}_{lip}_Jnt" : [""],
                f"{tweaks}_{lower}_{lip}_00_Jnt" : [""],
                f"{tweaks}_{lower}_{lip}_01_Jnt" : [""],
                f"{tweaks}_{lower}_{lip}_02_Jnt" : [""],
        }
        return data


    def get_integration_data(self, *args):
        # getting default names
        middle = self.ar.data.lang['m033_middle']

        arm = self.ar.data.lang['c037_arm']
        clavicle = self.ar.data.lang['c000_arm_before']
        hip = self.ar.data.lang['c005_leg_before']
        leg = self.ar.data.lang['c006_leg_main']
        back = self.ar.data.lang['c057_back']
        front = self.ar.data.lang['c056_front']
        spine = self.ar.data.lang['m011_spine']
        base = self.ar.data.lang['c106_base']
        tip = self.ar.data.lang['c120_tip']
        hips = self.ar.data.lang['c027_hips']
        chest = self.ar.data.lang['c028_chest']
        
        head = self.ar.data.lang['c024_head']
        upper = self.ar.data.lang['c044_upper']
        jaw = self.ar.data.lang['c025_jaw']
        
        upper_teeth = self.ar.data.lang['m075_upperTeeth']
        lower_teeth = self.ar.data.lang['m076_lowerTeeth']
        ear = self.ar.data.lang['m040_ear']
        eye = self.ar.data.lang['c036_eye']

        tweaks = self.ar.data.lang['m081_tweaks']
        eyebrow = self.ar.data.lang['c041_eyebrow']
        squint = self.ar.data.lang['c054_squint']
        cheek = self.ar.data.lang['c055_cheek']
        main = self.ar.data.lang['c058_main']
        lower = self.ar.data.lang['c045_lower']
        lip = self.ar.data.lang['c039_lip']
        corner = self.ar.data.lang['c043_corner']
        
        # declaring result dictionary
        data = {
                # integrations modules
                # limb
                f"{leg}_{hip}_Jnt" : [f"{spine}_00_{base}_Jnt", f"{spine}_00_{hips}_Jnt"],
                f"{leg}{back}_{hip}_Jnt" : [f"{spine}_00_{base}_Jnt", f"{spine}_00_{hips}_Jnt"],
                f"{leg}{front}_{hip}_Jnt" : [f"{spine}_04_{tip}_Jnt", f"{spine}_04_{chest}_Jnt"],
                f"{arm}_{clavicle}_Jnt" : [f"{spine}_04_{tip}_Jnt", f"{spine}_04_{chest}_Jnt"],
                f"{leg}_00_{hip}_Jnt" : [f"{spine}_00_{base}_Jnt", f"{spine}_00_{hips}_Jnt"],
                f"{leg}{back}_00_{hip}_Jnt" : [f"{spine}_00_{base}_Jnt", f"{spine}_00_{hips}_Jnt"],
                f"{leg}{front}_00_{hip}_Jnt" : [f"{spine}_04_{tip}_Jnt", f"{spine}_04_{chest}_Jnt"],
                f"{arm}_00_{clavicle}_Jnt" : [f"{spine}_04_{tip}_Jnt", f"{spine}_04_{chest}_Jnt"],
                # ear
                f"{ear}_00_Jnt" : [f"{head}_{upper}{head}_Jnt", f"{head}_1_{head}_Jnt"],
                f"{ear}{base}_00_Jnt" : [f"{head}_{upper}{head}_Jnt", f"{head}_1_{head}_Jnt"],
                f"{upper_teeth}Side_00_Jnt" : [f"{upper_teeth}{middle}_00_Jnt", f"{head}_1_{head}_Jnt"],
                f"{lower_teeth}Side_00_Jnt" : [f"{lower_teeth}{middle}_00_Jnt", f"{head}_1_{head}_Jnt"],
                # eye
                f"{eye}_1_Jnt" : [f"{head}_{upper}{head}_Jnt", f"{head}_1_{head}_Jnt"],
                # tweaks
                f"{tweaks}_{cheek}_01_Jnt" : [f"{head}_{upper}{jaw}_Jnt", f"{head}_01_{head}_Jnt"],
                f"{tweaks}_{cheek}_02_Jnt" : [f"{head}_{upper}{jaw}_Jnt", f"{head}_01_{head}_Jnt"],
                f"{tweaks}_{squint}_{main}_Jnt" : [f"{head}_{upper}{jaw}_Jnt", f"{head}_01_{head}_Jnt"],
                f"{tweaks}_{eyebrow}_{main}_Jnt" : [f"{head}_{upper}{head}_Jnt", f"{head}_01_{head}_Jnt"],
                f"{tweaks}_{lip}_{main}_Jnt" : [f"{head}_01_{head}_Jnt"],
                f"{tweaks}_{upper}_{lip}_00_Jnt" : [f"{tweaks}_{lip}_{main}_Jnt"],
                f"{tweaks}_{upper}_{lip}_01_Jnt" : [f"{tweaks}_{lip}_{main}_Jnt"],
                f"{tweaks}_{upper}_{lip}_02_Jnt" : [f"{tweaks}_{lip}_{main}_Jnt"],
                f"{tweaks}_{corner}_{lip}_Jnt" : [f"{tweaks}_{lip}_{main}_Jnt"],
                f"{tweaks}_{lower}_{lip}_00_Jnt" : [f"{tweaks}_{lip}_{main}_Jnt"],
                f"{tweaks}_{lower}_{lip}_01_Jnt" : [f"{tweaks}_{lip}_{main}_Jnt"],
                f"{tweaks}_{lower}_{lip}_02_Jnt" : [f"{tweaks}_{lip}_{main}_Jnt"],
        }
        return data
