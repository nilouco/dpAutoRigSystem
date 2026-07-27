# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "VisibilityIO"
TITLE = "r070_visibilityIO"
DESCRIPTION = "r071_visibilityIODesc"
WIKI = "10-‐-Rebuilder#-visibility"



class VisibilityIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_visibilityIO"
        self.startName = "dpVisibility"
        self.ignoreList = ["defaultLayer"]
    

    def runAction(self, first_mode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If first_mode parameter is False, it'll run in import mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start(True)
        
        # ---
        # --- rebuilder code --- beginning
        if not cmds.file(query=True, reference=True):
            if self.ar.pipeliner.checkAssetContext():
                self.io_path = self.get_io_path(self.io_folder)
                if self.io_path:
                    itemList = None
                    if objList:
                        itemList = objList
                    else:
                        itemList = cmds.ls(selection=False)#, type="transform")
                    if itemList:
                        if self.first_mode: #export
                            self.exportDicToJsonFile(self.getVisibilityDataDic(itemList))
                        else: #import
                            visDic = self.importLatestJsonFile(self.get_exported_items())
                            if visDic:
                                self.importVisibilityData(visDic)
                            else:
                                self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
                    else:
                        self.maybe_done_io("Ctrls_Grp")
                else:
                    self.fail_io(self.ar.data.lang['r010_notFoundPath'])
            else:
                self.fail_io(self.ar.data.lang['r027_noAssetContext'])
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.endProgress()
        self.refresh_view()
        return self.log_data


    def getVisibilityDataDic(self, itemList, *args):
        """ Processes the given item list to check the visibility value if it doesn't have input connection.
            Returns the dictionary to export.
        """
        dic = {}
        self.ar.utils.setProgress(max=len(itemList), addOne=False, addNumber=False)
        for item in itemList:
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            if cmds.objExists(item):
                if "visibility" in cmds.listAttr(item):
                    if not cmds.listConnections(item+".visibility", source=True, destination=False):
                        dic[item] = cmds.getAttr(item+".visibility")
        return dic


    def importVisibilityData(self, visDic, *args):
        """ Import visibility attribute values from exported dictionary.
        """
        self.ar.utils.setProgress(max=len(visDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in visDic.keys():
            notFoundNodesList = []
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            # check attribute
            if not cmds.objExists(item):
                item = item[item.rfind("|")+1:] #short name (after last "|")
            if cmds.objExists(item):
                if not cmds.getAttr(item+".visibility", lock=True):
                    if not item in self.ignoreList:
                        try:
                            cmds.setAttr(item+".visibility", visDic[item])
                            if not item in wellImportedList:
                                wellImportedList.append(item)
                        except Exception as e:
                            self.fail_io(item+" - "+str(e))
            else:
                notFoundNodesList.append(item)
        if wellImportedList:
            self.well_done_io(self.latestDataFile)
        else:
            self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(notFoundNodesList))
