# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "EmptyTransform"
TITLE = "v138_emptyTransform"
DESCRIPTION = "v139_emptyTransformDesc"
WIKI = "07-‐-Validator#-empty-transform-cleaner"



class EmptyTransform(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
    

    def run_action(self, first_mode=True, inputs=None, *args):
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
        if not cmds.file(query=True, reference=True):
            if inputs:
                check_items = inputs
            else:
                check_items = cmds.ls(selection=False, long=True, type="transform") #list all transforms in the scene
            if check_items:
                self.ar.utils.setProgress(max=len(check_items), add_one=False, add_number=False)
                emptyTransformList = self.filterEmptyTransformList(check_items)
                emptyTransformList.extend(self.filterEmptyTransformList(self.getIgnoreConnected(), True))
                # conditional to check here
                if emptyTransformList:
                    for item in emptyTransformList:
                        self.ar.utils.setProgress(self.ar.data.lang[self.title])
                        self.checked_items.append(self.ar.utils.getShortName(item, False))
                        self.found_issues.append(True)
                        if self.first_mode:
                            self.good_results.append(False)
                        else: #fix
                            try:
                                if "dpKeepIt" in cmds.listAttr(item) and cmds.getAttr(item+".dpKeepIt") == True:
                                    pass
                                else:
                                    cmds.lockNode(item, lock=False)
                                    cmds.delete(item)
                                self.good_results.append(True)
                                self.messages.append(self.ar.data.lang['v004_fixed']+": "+item)
                            except:
                                self.good_results.append(False)
                                self.messages.append(self.ar.data.lang['v005_cantFix']+": "+item)
            else:
                self.not_found_node()
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data
    
    
    def filterEmptyTransformList(self, transforms=None, connected=False, *args):
        """ Filter the transform list to remove those without children or connections.
            Returns a list of transforms that are empty.
        """
        filtered_items = self.ar.utils.filterTransformList(transforms, verbose=self.ar.data.verbose, title=self.ar.data.lang[self.title])
        filtered_items = self.reorder_list(filtered_items)
        emptyTransforms = []
        for transform in filtered_items:
            if connected:
                hasConnection = False
            else:
                hasConnection = cmds.listConnections(transform)
                if hasConnection:
                    nodeGraphList = cmds.listConnections(transform, type="nodeGraphEditorInfo") or []
                    hasConnection = set(hasConnection)-set(nodeGraphList)
            if not hasConnection:
                children = cmds.listRelatives(transform, children=True, fullPath=True)
                if not children:
                    emptyTransforms.append(transform)
                elif len(list(set(children).intersection(emptyTransforms))) == len(children):
                    emptyTransforms.append(transform)
        return emptyTransforms
    

    def getIgnoreConnected(self, *args):
        """ Ignore dpAr default nodes
        """
        ignoredList = ["supportGrp", "renderGrp", "proxyGrp", "fxGrp", "blendShapesGrp", "wipGrp"]
        nodes = []
        for item in ignoredList:
            gotNode = self.ar.utils.getNodeByMessage(item)
            if gotNode:
                nodes.append(gotNode)
        return nodes
    