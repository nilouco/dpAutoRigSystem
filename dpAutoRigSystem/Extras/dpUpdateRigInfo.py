# importing libraries:
import maya.cmds as cmds
import maya.mel as mel

try:
    import pymel.core as pymel
    loadedSqBindPose = False
    try:
        import sstk.maya.animation.sqBindPose as sqBindPose
        reload(sqBindPose)
        loadedSqBindPose = True
    except:
        pass
except Exception as e:
    print "Error: importing python modules!!!\n",
    print e

# global variables to this module:    
CLASS_NAME = "UpdateRigInfo"
TITLE = "m057_updateRigInfo"
DESCRIPTION = "m058_updateRigInfoDesc"
ICON = "/Icons/dp_updateRigInfo.png"


class UpdateRigInfo():
    def __init__(self, *args, **kwargs):
        # call main function
        self.dpMain(self)
    
    
    def dpMain(self, *args):
        """ Main function.
            Just call the update function.
        """
        self.updateRigInfoLists()
    

    @staticmethod
    def updateRigInfoLists(*args):
        """
        """
        masterGrp = None
        masterGrpAttr = "masterGrp"
        allList = cmds.ls(selection=False)
        for nodeItem in allList:
            if cmds.objExists(nodeItem+"."+masterGrpAttr) and \
                (cmds.getAttr(nodeItem+"."+masterGrpAttr, type=True) == "bool" or \
                cmds.getAttr(nodeItem+"."+masterGrpAttr, type=True) == "long") and \
                cmds.getAttr(nodeItem+"."+masterGrpAttr) == 1:
                masterGrp = nodeItem
        if masterGrp:
            ctrlList = cmds.ls("*_Ctrl")
            ctrlString = ""
            if ctrlList:
                for i, item in enumerate(ctrlList):
                    if (loadedSqBindPose):
                        nCurNode = pymel.PyNode(item)
                        if sqBindPose.is_pose_outdated(nCurNode):
                            sqBindPose.store_pose(pymel.PyNode(item))
                    ctrlString = ctrlString + str(item)
                    if i < len(ctrlList):
                        ctrlString = ctrlString + ";"
                cmds.setAttr(masterGrp+".controlList", ctrlString, type="string")
            
            meshList = cmds.ls("*_Mesh")
            meshString = ""
            if meshList:
                for i, item in enumerate(meshList):
                    meshString = meshString + str(item)
                    if i < len(meshList):
                        meshString = meshString + ";"
                cmds.setAttr(masterGrp+".geometryList", meshString, type="string")
            print "Control List = ", ctrlString
            print "Mesh List    = ", meshString
            print "Updated Rig Info: "+masterGrp,
