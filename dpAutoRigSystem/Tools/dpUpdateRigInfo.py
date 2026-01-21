# importing libraries:
from maya import cmds

# global variables to this module:    
CLASS_NAME = "UpdateRigInfo"
TITLE = "m057_updateRigInfo"
DESCRIPTION = "m058_updateRigInfoDesc"
ICON = "/Icons/dp_updateRigInfo.png"
WIKI = "06-‐-Tools#-update-rig-info"

DP_UPDATERIGINFO_VERSION = 2.01


class UpdateRigInfo(object):
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
            print("Control List = "+ctrlString)
            print("Mesh List = "+meshString)
            print("Updated Rig Info: "+masterGrp)
