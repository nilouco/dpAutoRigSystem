# importing libraries:
from maya import cmds
from .. import dpBaseActionClass

# global variables to this module:
CLASS_NAME = "ModelIO"
TITLE = "r003_modelIO"
DESCRIPTION = "r004_modelIODesc"
ICON = "/Icons/dp_modelIO.png"

DP_MODELIO_VERSION = 1.0


class ModelIO(dpBaseActionClass.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_MODELIO_VERSION
        dpBaseActionClass.ActionStartClass.__init__(self, *args, **kwargs)
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If firstMode parameter is False, it'll run in import mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()
        
        # ---
        # --- rebuilder code --- beginning
        meshList = None
        print(self.pipeliner.pipeData["s_modelIO"])
        if objList:
            meshList = cmds.listRelatives(objList, children=True, allDescendents=True, type="mesh")
        else:
            meshList = self.getRenderMeshList(True)
        if meshList:
            progressAmount = 0
            maxProcess = len(meshList)
            for item in meshList:
                if self.verbose:
                    # Update progress window
                    progressAmount += 1
                    cmds.progressWindow(edit=True, maxValue=maxProcess, progress=progressAmount, status=(self.dpUIinst.lang[self.title]+': '+repr(progressAmount)))
                # get transform node
                parentNode = cmds.listRelatives(item, parent=True)[0]
                if self.firstMode: #export
                    try:
                        # WIP
                        print("EXPORTING HERE")
                        
                        self.wellDoneIO(parentNode)
                    except:
                        self.notWorkedWellIO(parentNode)
                else: #import
                    try:
                        # WIP
                        print("IMPORTING HERE")
                        if not "_Mesh" in parentNode:
                            cmds.rename(parentNode, parentNode+"_Mesh")
                        
                        self.wellDoneIO(parentNode)
                    except:
                        self.notWorkedWellIO(parentNode)
        else:
            self.notWorkedWellIO("Render_Grp")
        # --- rebuilder code --- end
        # ---

        # finishing
        self.updateButtonColors()
        self.reportLog()
        self.endProgressBar()
        return self.dataLogDic
