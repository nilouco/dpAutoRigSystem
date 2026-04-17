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
                    self.mountHierarchy(newJointList, root)
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


    def mountHierarchy(self, joints, root, *args):
        hierarchyData = self.getHierarchyData()
        for item in hierarchyData.keys():
            if cmds.objExists(self.prefix+item+self.suffix):
                for p, parent in enumerate(hierarchyData[item]):
                    if cmds.objExists(self.prefix+hierarchyData[item][p]+self.suffix):
                        cmds.parent(self.prefix+item+self.suffix, self.prefix+hierarchyData[item][p]+self.suffix)
                        break
                    else:
                        cmds.parent(self.prefix+item+self.suffix, root)
            joints.remove(self.prefix+item+self.suffix)
        cmds.parent(joints, root)


    def getHierarchyData(self, *args):
        data = {
                "Arm_00_Clavicle_Jar" : ["Arm_00_Clavicle_Jnt"],
                "Arm_01_Shoulder_Jar" : ["Arm_00_Clavicle_Jnt"],
                "Arm_02_Jnt" : ["Arm_01_Shoulder_Jar"],
                "Arm_03_Jnt" : ["Arm_02_Jnt"],
                "Arm_04_Jnt" : ["Arm_03_Jnt"],
                "Arm_05_Jnt" : ["Arm_04_Jnt"],
                "Arm_06_Jnt" : ["Arm_05_Jnt"],
                "Arm_07_Elbow_Jar" : ["Arm_06_Jnt"],
                "Arm_08_Jnt" : ["Arm_07_Elbow_Jar"],
                "Arm_09_Jnt" : ["Arm_08_Jnt"],
                "Arm_10_Jnt" : ["Arm_09_Jnt"],
                "Arm_11_Jnt" : ["Arm_10_Jnt"],
                "Arm_12_Jnt" : ["Arm_11_Jnt"],
                "Arm_13_Wrist_Jnt" : ["Arm_12_Jnt"],
                "Arm_13_Wrist_Jar" : ["Arm_13_Wrist_Jnt", "Arm_12_Jnt"],
                "Finger_Thumb_00_Jnt" : ["Arm_13_Wrist_Jar", "Arm_13_Wrist_Jnt"],
                "Finger_Thumb_01_Jnt" : ["Finger_Thumb_00_Jnt"],
                "Finger_Thumb_01_Jar" : ["Finger_Thumb_01_Jnt"],
                "Finger_Thumb_02_Jnt" : ["Finger_Thumb_01_Jar", "Finger_Thumb_01_Jnt"],
                "Finger_Thumb_02_Jar" : ["Finger_Thumb_02_Jnt"],
                "Finger_Index_00_Jnt" : ["Arm_13_Wrist_Jar", "Arm_13_Wrist_Jnt"],
                "Finger_Index_01_Jnt" : ["Finger_Index_00_Jnt"],
                "Finger_Index_01_Jar" : ["Finger_Index_01_Jnt"],
                "Finger_Index_02_Jnt" : ["Finger_Index_01_Jar", "Finger_Index_01_Jnt"],
                "Finger_Index_02_Jar" : ["Finger_Index_02_Jnt"],
                "Finger_Index_03_Jnt" : ["Finger_Index_02_Jar", "Finger_Index_02_Jnt"],
                "Finger_Index_03_Jar" : ["Finger_Index_03_Jnt"],
                "Finger_Middle_00_Jnt" : ["Arm_13_Wrist_Jar", "Arm_13_Wrist_Jnt"],
                "Finger_Middle_01_Jnt" : ["Finger_Middle_00_Jnt"],
                "Finger_Middle_01_Jar" : ["Finger_Middle_01_Jnt"],
                "Finger_Middle_02_Jnt" : ["Finger_Middle_01_Jar", "Finger_Middle_01_Jnt"],
                "Finger_Middle_02_Jar" : ["Finger_Middle_02_Jnt"],
                "Finger_Middle_03_Jnt" : ["Finger_Middle_02_Jar", "Finger_Middle_02_Jnt"],
                "Finger_Middle_03_Jar" : ["Finger_Middle_03_Jnt"],
                "Finger_Ring_00_Jnt" : ["Arm_13_Wrist_Jar", "Arm_13_Wrist_Jnt"],
                "Finger_Ring_01_Jnt" : ["Finger_Ring_00_Jnt"],
                "Finger_Ring_01_Jar" : ["Finger_Ring_01_Jnt"],
                "Finger_Ring_02_Jnt" : ["Finger_Ring_01_Jar", "Finger_Ring_01_Jnt"],
                "Finger_Ring_02_Jar" : ["Finger_Ring_02_Jnt"],
                "Finger_Ring_03_Jnt" : ["Finger_Ring_02_Jar", "Finger_Ring_02_Jnt"],
                "Finger_Ring_03_Jar" : ["Finger_Ring_03_Jnt"],
                "Finger_Pinky_00_Jnt" : ["Arm_13_Wrist_Jar", "Arm_13_Wrist_Jnt"],
                "Finger_Pinky_01_Jnt" : ["Finger_Pinky_00_Jnt"],
                "Finger_Pinky_01_Jar" : ["Finger_Pinky_01_Jnt"],
                "Finger_Pinky_02_Jnt" : ["Finger_Pinky_01_Jar", "Finger_Pinky_01_Jnt"],
                "Finger_Pinky_02_Jar" : ["Finger_Pinky_02_Jnt"],
                "Finger_Pinky_03_Jnt" : ["Finger_Pinky_02_Jar", "Finger_Pinky_02_Jnt"],
                "Finger_Pinky_03_Jar" : ["Finger_Pinky_03_Jnt"]
                # "" : [""],
                # "" : [""],
                # "" : [""],
                # "" : [""],
                # "" : [""],

        }


        return data




#TODO:
# UI
#   prefix
#   suffix
#   hierarchy/float joint
# translate dic
# sides
# All_Grp.prefix
# many ribbons options (joints naming, numbers)
# 