# importing libraries:
from maya import cmds
from maya import mel
from itertools import zip_longest

# global variables to this module:    
CLASS_NAME = "OneSkeleton"
TITLE = "m254_oneSkeleton"
DESCRIPTION = "m255_oneSkeletonDesc"
ICON = "/Icons/dp_oneSkeleton.png"
WIKI = "06-‐-Tools#-one-skeleton"

DP_ONESKELETON_VERSION = 1.03


class OneSkeleton(object):
    def __init__(self, dpUIinst, ui=True, *args, **kwargs):
        # defining variables:
        self.dpUIinst = dpUIinst
        self.utils = dpUIinst.utils
        self.ctrls = dpUIinst.ctrls
        self.prefix = "Web_"
        self.rootName = "Root"
        self.suffix = "_Joint"
        self.sides = [f"{self.dpUIinst.lang['p002_left']}_", f"{self.dpUIinst.lang['p003_right']}_", ""]
        self.ui = ui
        # call main UI function
        if self.ui:
            name = self.oneSkeletonPromptDialog()
            if name:
                self.createOneSkeleton(name)

    
    def oneSkeletonPromptDialog(self, *args):
        """ Prompt dialog to get the name of the root joint to receive all the web joints as children.
        """
        btContinue = self.dpUIinst.lang['i174_continue']
        btCancel = self.dpUIinst.lang['i132_cancel']
        result = cmds.promptDialog(title=CLASS_NAME, 
                                   message=self.dpUIinst.lang["m006_name"], 
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


    def createOneSkeleton(self, root=None, hierarchy=True, *args):
        """ Create one skeleton hierarchy using the given name as a root joint name or use the default root name.
        """
        if not root:
            root = self.rootName
        uniqueInfList = self.getInfList(self.getMeshList())
        if uniqueInfList:
            if not cmds.objExists(root):
                self.createRootJoint(root)
            newJointList = self.transferJoint(uniqueInfList)
            if newJointList:
                #newJointList.sort()
                if hierarchy:
                    self.mount_hierarchy(newJointList, root)
                else:
                    cmds.parent(newJointList, root)
                cmds.select(root)
            self.ctrls.setControllerScaleCompensate(False)
            self.utils.setProgress(endIt=True)
        else:
            mel.eval('warning \"'+self.dpUIinst.lang["v014_notFoundNodes"]+'\";')


    def grouper(self, iterable, n, fillvalue=None, *args):
        """ Collect data into fixed-length chunks or blocks.
            Example:
                grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
        """
        args = [iter(iterable)] * n
        return zip_longest(fillvalue=fillvalue, *args)


    def transferJoint(self, sourceList, *args):
        """ Make a duplicated joints and transfer connections and deformation to them.
            Returns the new created joint list.
        """
        newJointList = []
        self.utils.setProgress(self.dpUIinst.lang['m254_oneSkeleton'], self.dpUIinst.lang['m254_oneSkeleton'], max=len(sourceList), addOne=False, addNumber=False)
        for sourceNode in sourceList:
            self.utils.setProgress("Joint")
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
            # fixes for negative scale joints
            parentList = cmds.listRelatives(sourceNode, parent=True)
            if parentList:
                if not "_Jar" in parentList[0]:
                    for axis in ["X", "Y", "Z"]:
                        if cmds.getAttr(parentList[0]+".scale"+axis) < 0: #negative scale OMG
                            for a in ["X", "Y", "Z"]:
                                if not a == axis:
                                    cmds.setAttr(scc+".offset"+a, -1)
            # corrective joints
            if "_Jcr" in newJoint:
                for axis in ["X", "Y", "Z"]:
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
            self.dpUIinst.customAttr.addAttr(0, [newJoint, pac, scc]) #dpID
        return newJointList


    def getMeshList(self, *args):
        """ Returns the Render_Grp meshes or all meshes in the scene.
        """
        if self.utils.getAllGrp():
            renderGrp = self.utils.getNodeByMessage("renderGrp")
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
            mel.eval('warning \"'+self.dpUIinst.lang['i041_meshConnEmpty']+'\";')
            return
        for transformNode in list(set(cmds.listRelatives(meshList, type="transform", parent=True, fullPath=True))):
            skinClusterList.extend(self.dpUIinst.skin.checkExistingDeformerNode(transformNode)[2] or [])
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
        cmds.setAttr(root+".visibility", 0)
        self.ctrls.setLockHide([root], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], cb=True)


    def mount_hierarchy(self, joints, root, *args):
        hierarchy_data = self.get_hierarchy_data()
        for side in self.sides:
            for item in hierarchy_data.keys():
                if cmds.objExists(f"{self.prefix}{side}{item}{self.suffix}"):
                    for p, parent in enumerate(hierarchy_data[item]):
                        if cmds.objExists(f"{self.prefix}{side}{hierarchy_data[item][p]}{self.suffix}"):
                            cmds.parent(f"{self.prefix}{side}{item}{self.suffix}", f"{self.prefix}{side}{hierarchy_data[item][p]}{self.suffix}")
                            break
                        else:
                            cmds.parent(f"{self.prefix}{side}{item}{self.suffix}", root)
                if f"{self.prefix}{side}{item}{self.suffix}" in joints:
                    joints.remove(f"{self.prefix}{side}{item}{self.suffix}")
        cmds.parent(joints, root)


    def get_hierarchy_data(self, *args):
        # getting names
        arm = self.dpUIinst.lang['c037_arm']
        clavicle = self.dpUIinst.lang['c000_arm_before']
        shoulder = self.dpUIinst.lang['c001_arm_main']
        elbow = self.dpUIinst.lang['c002_arm_corner']
        wrist = self.dpUIinst.lang['c004_arm_extrem']
        forearm = self.dpUIinst.lang['c030_forearm']
        
        hip = self.dpUIinst.lang['c005_leg_before']
        leg = self.dpUIinst.lang['c006_leg_main']
        knee = self.dpUIinst.lang['c007_leg_corner']
        ankle = self.dpUIinst.lang['c009_leg_extrem']
        
        finger = self.dpUIinst.lang['m007_finger']
        thumb = self.dpUIinst.lang['m036_thumb']
        index = self.dpUIinst.lang['m032_index']
        middle = self.dpUIinst.lang['m033_middle']
        ring = self.dpUIinst.lang['m034_ring']
        pinky = self.dpUIinst.lang['m035_pinky']
        
        foot = self.dpUIinst.lang['c038_foot']
        toe = self.dpUIinst.lang['c013_revFoot_D'].capitalize()
        

        # declaring result dictionary
        data = {
                # arm
                f"{arm}_{shoulder}_Jnt" : [f"{arm}_{clavicle}_Jnt"],
                f"{arm}_{elbow}_Jar" : [f"{arm}_{shoulder}_Jnt"],
                f"{arm}_{elbow}_Jnt" : [f"{arm}_{shoulder}_Jnt"],
                f"{arm}_{forearm}_Jnt" : [f"{arm}_{elbow}_Jar", f"{arm}_{elbow}_Jnt"],
                f"{arm}_{wrist}_Jnt" : [f"{arm}_{forearm}_Jnt", f"{arm}_{elbow}_Jar", f"{arm}_{elbow}_Jnt"],
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
                f"{arm}_13_{wrist}_Jar" : [f"{arm}_13_{wrist}_Jnt", f"{arm}_12_Jnt"],
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
                f"{leg}_{leg}_Jnt" : [f"{leg}_{hip}_Jnt"],
                f"{leg}_{knee}_Jar" : [f"{leg}_{leg}_Jnt"],
                f"{leg}_{knee}_Jnt" : [f"{leg}_{leg}_Jnt"],
                f"{leg}_{ankle}_Jnt" : [f"{leg}_{knee}_Jar", f"{leg}_{knee}_Jnt"],
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
                f"{leg}_13_{ankle}_Jar" : [f"{leg}_13_{ankle}_Jnt", f"{leg}_12_Jnt"],
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
                f"{toe}_5_02_Jnt" : [f"{toe}_5_01_Jnt"]

                # f"{}" : [f"{}"],
                # f"{}" : [f"{}"],
                # f"{}" : [f"{}"],
                # f"{}" : [f"{}"],
                # f"{}" : [f"{}"],
                

        }


        return data




#TODO:
# UI
#   prefix
#   suffix
#   hierarchy/float joint
# All_Grp.prefix
# many ribbons options (joints naming, numbers)
# 
# Foot
# Head
# Spine
# Tweak
# Nose
# Ear
# Tongue
# Teeth
# Eye
# Toes
#