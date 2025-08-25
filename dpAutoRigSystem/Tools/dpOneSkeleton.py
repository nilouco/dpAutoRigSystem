# importing libraries:
from maya import cmds

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
        self.rootName = "Web_Root_Joint"
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
                                   text=self.rootName, 
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
                            print("skinCluster List =", skinClusterList)
                            for skinClusterNode in skinClusterList:
                                infList = cmds.skinCluster(skinClusterNode, query=True, influence=True)
                                print("infList =", infList)
                                
                                
                                #TODO call patch for this infList



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
