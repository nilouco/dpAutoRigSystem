# importing libraries:
from maya import cmds
from maya import mel
from ....library.base import action

# global variables to this module:
CLASS_NAME = "OneVertex"
TITLE = "v132_oneVertex"
DESCRIPTION = "v133_oneVertexDesc"
WIKI = "07-‐-Validator#-one-vertex"



class OneVertex(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

    def runAction(self, first_mode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If first_mode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start()
        
        # ---
        # --- validator code --- beginning
        if not self.ar.utils.getAllGrp():
            if not self.ar.utils.getNetworkNodeByAttr("dpGuideNet"):
                if not cmds.file(query=True, reference=True):
                    if objList:
                        toCheckList = cmds.ls(objList, type="mesh")
                    else:
                        toCheckList = cmds.ls(selection=False, type="mesh")
                    if toCheckList:
                        self.ar.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                        oneVertexList = self.checkNonManifoldVertex(toCheckList)
                        # conditional to check here
                        if oneVertexList:
                            oneVertexList.sort()
                            for item in oneVertexList:
                                self.checked_items.append(item)
                                self.found_issues.append(True)
                                if self.first_mode:
                                    self.good_results.append(False)
                                else: #fix
                                    self.good_results.append(False)
                                    self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
                            self.messages.append("---\n"+self.ar.data.lang['v121_sharePythonSelect']+"\nmaya.cmds.select("+str(oneVertexList)+")\n---")
                            cmds.select(oneVertexList)
                    else:
                        self.not_found_node()
                else:
                    self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
            else:
                self.fail_io(self.ar.data.lang['v100_cantExistsGuides'])
        else:
            self.fail_io(self.ar.data.lang['v099_cantExistsAllGrp'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.endProgress()
        return self.log_data


    def checkNonManifoldVertex(self, itemList, *args):
        """ Return a list of nonManifold vertex if exists.
        """
        nmVertexList, foundList = [], []
        for item in itemList:
            cmds.select(item)
            foundList.extend(mel.eval('polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0" };'))
        if foundList:
            for sel in foundList:
                if ".vtx[" in sel:
                    nmVertexList.append(sel)
        cmds.select(nmVertexList)
        return nmVertexList
