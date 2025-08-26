# importing libraries:
from maya import cmds
from itertools import zip_longest

# global variables to this module:    
CLASS_NAME = "OneSkeleton"
TITLE = "m254_oneSkeleton"
DESCRIPTION = "m255_oneSkeletonDesc"
ICON = "/Icons/dp_oneSkeleton.png"

DP_ONESKELETON_VERSION = 1.0


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
            self.createOneSkeleton(self.oneSkeletonPromptDialog())

    
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


    def createOneSkeleton(self, root=None, *args):
        """ Create one skeleton hierarchy using the given name as a root joint name or use the default root name.
        """
        if not root:
            root = self.rootName
        if root:
            
            # WIP

            print("name = ", root)
            if not cmds.objExists(root):
                cmds.select(clear=True)
                cmds.joint(name=root)
                cmds.setAttr(root+".visibility", 0)
                self.ctrls.setLockHide([root], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], cb=True)
            if self.utils.getAllGrp():
                renderGrp = self.utils.getNodeByMessage("renderGrp")
                if renderGrp:
                    print("renderGrp =", renderGrp)

                    meshList = cmds.listRelatives(renderGrp, children=True, allDescendents=True, type="mesh")
                    if meshList:
                        print("meshList =", meshList)
                    
                        skinClusterList = []
                        for transformNode in list(set(cmds.listRelatives(meshList, type="transform", parent=True, fullPath=True))):
                            skinClusterList.extend(self.dpUIinst.skin.checkExistingDeformerNode(transformNode)[2])
                        
                        if skinClusterList:
                            uniqueInfList = []
                            print("skinCluster List =", skinClusterList)
                            for skinClusterNode in skinClusterList:
                                infList = cmds.skinCluster(skinClusterNode, query=True, influence=True)
                                if infList:
                                    for item in infList:
                                        if not item in uniqueInfList:
                                            uniqueInfList.append(item)
                            if uniqueInfList:
                                print("uniqueInfList =", uniqueInfList)
                                newJointList = self.transferJoint(uniqueInfList)
                                if newJointList:
                                    newJointList.sort()
                                    print("newJointList =", newJointList)
                                    cmds.parent(newJointList, root)
                                    cmds.select(root)

                        else:
                            print("there's no skinCluster nodes")
                    else:
                        print("not found meshList")
                else:
                    print("there's no Render_Grp")
            else:
                print("there's no All_Grp")
        else:
            print("cant continue without a name")


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
        for sourceNode in sourceList:
            cmds.select(clear=True)
            newJoint = cmds.createNode("joint", name=self.prefix+sourceNode+self.suffix)
            newJointList.append(newJoint)
            # Transfer skinCluster + bindPose connection from the original
            connectionList = cmds.listConnections(sourceNode, destination=True, source=False, connections=True, plugs=True) or []
            for src, dest in self.grouper(connectionList, 2):
                sourceNode, sourceAttr = src.split(".", 1)
                destNode, destAttr = dest.split(".", 1)
                if cmds.nodeType(destNode) in {"skinCluster", "dagPose"}:
                    
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
            scc = cmds.scaleConstraint([sourceNode, newJoint], name=newJoint+"_ScC")[0]
            # Ensure the new joint doesn't have segmentScaleCompensate enabled
            # But do allow the scale constraint to compensate
            cmds.setAttr(f"{newJoint}.segmentScaleCompensate", False)
            cmds.setAttr(f"{scc}.constraintScaleCompensate", True)
            # dpIDs
            self.dpUIinst.customAttr.addAttr(0, [newJoint, pac, scc]) #dpID
        return newJointList
