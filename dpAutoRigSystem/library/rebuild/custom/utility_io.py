# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "UtilityIO"
TITLE = "r054_utilityIO"
DESCRIPTION = "r055_utilityIODesc"
WIKI = "10-‐-Rebuilder#-utility"



class UtilityIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_utilityIO"
        self.start_name = "dpUtility"
    

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
                    utilityList = None
                    if objList:
                        utilityList = objList
                    else:
                        utilityList = cmds.ls(selection=False, type=self.ar.utils.utilityTypeList)
                    if self.first_mode: #export
                        if utilityList:
                            self.export_json_file(self.getUtilityDataDic(utilityList))
                        else:
                            self.maybe_done_io("Utility nodes.")
                    else: #import
                        utilityDic = self.import_latest_json_file(self.get_exported_items())
                        if utilityDic:
                            self.importUtilityData(utilityDic)
                        else:
                            self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
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
        self.end_progress()
        self.refresh_view()
        return self.log_data


    def getUtilityDataDic(self, utilityList, *args):
        """ Processes the given utility list to collect and mount the info data.
            Returns the dictionary to export.
        """
        dic = {}
        self.ar.utils.setProgress(max=len(utilityList), addOne=False, addNumber=False)
        for item in utilityList:
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            if not cmds.attributeQuery(self.ar.data.dp_id, node=item, exists=True) or not self.ar.utils.validateID(item):
                # getting attributes values
                nodeType = cmds.objectType(item)
                dic[item] = {"attributes" : {},
                                "type"       : nodeType,
                                "name"       : item
                            }
                for attr in self.ar.utils.typeAttrDic[nodeType]:
                    if cmds.attributeQuery(attr, node=item, exists=True):
                        dic[item]["attributes"][attr] = cmds.getAttr(item+"."+attr)
                # compound attributes
                if nodeType in self.ar.utils.typeMultiAttrDic.keys():
                    for multiAttr in self.ar.utils.typeMultiAttrDic[nodeType].keys():
                        indexList = cmds.getAttr(item+"."+multiAttr, multiIndices=True)
                        if indexList:
                            dot = ""
                            attributes = [""]
                            if self.ar.utils.typeMultiAttrDic[nodeType][multiAttr]:
                                dot = "."
                                attributes = self.ar.utils.typeMultiAttrDic[nodeType][multiAttr]
                            for i in indexList:
                                for attr in attributes:
                                    attrName = multiAttr+"["+str(i)+"]"+dot+attr
                                    attrValue = cmds.getAttr(item+"."+attrName)
                                    dic[item]["attributes"][attrName] = attrValue
                                    if isinstance(attrValue, list):
                                        dic[item]["attributes"][attrName] = attrValue[0]
        return dic


    def importUtilityData(self, utilityDic, *args):
        """ Import utility nodes from exported dictionary.
            Create missing utility nodes and set them values if they don't exists.
        """
        self.ar.utils.setProgress(max=len(utilityDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in utilityDic.keys():
            existingNodesList = []
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            # create utility node if it needs
            if not cmds.objExists(item):
                cmds.createNode(utilityDic[item]["type"], name=utilityDic[item]["name"])
                # set attribute values
                if utilityDic[item]["attributes"]:
                    for attr in utilityDic[item]["attributes"].keys():
                        #if isinstance(attr, list): 
                        if str(utilityDic[item]["attributes"][attr]).count(",") > 1: #support vector attributes like color_Color
                            cmds.setAttr(item+"."+attr, utilityDic[item]["attributes"][attr][0], utilityDic[item]["attributes"][attr][1], utilityDic[item]["attributes"][attr][2], type="double3")
                        else:
                            cmds.setAttr(item+"."+attr, utilityDic[item]["attributes"][attr])
                wellImportedList.append(item)
            else:
                existingNodesList.append(item)
        if wellImportedList:
            self.well_done_io(self.latest_data_file)
        else:
            if existingNodesList:
                self.well_done_io(self.ar.data.lang['r032_notImportedData'])
            else:
                self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(existingNodesList))
