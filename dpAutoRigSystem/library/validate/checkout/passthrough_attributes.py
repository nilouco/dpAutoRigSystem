# https://gist.github.com/BigRoy/7784b266da449a5b5db7ed633302ebad

# importing libraries:
from maya import cmds
from collections import defaultdict
import contextlib
from ....library.base import action

# global variables to this module:
CLASS_NAME = "PassthroughAttributes"
TITLE = "v107_passthroughAttributes"
DESCRIPTION = "v108_passthroughAttributesDesc"
WIKI = "07-‐-Validator#-pasthrough-attributes"



class PassthroughAttributes(action.BaseAction):
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
        self.iterNumber = 5
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if objList:
                check_items = objList
            else:
                check_items = cmds.ls(selection=False) #all
            if check_items:
                if self.first_mode:
                    self.ar.utils.setProgress(max=len(check_items), addOne=False, addNumber=False)
                else:
                    self.ar.utils.setProgress(max=len(check_items)*2, addOne=False, addNumber=False)
                toOptimizeList = []
                for item in check_items:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    # check optimization
                    for plug, connections in self.getConnectionDic(item).items():
                        sources = connections["sourceList"]
                        destinations = connections["destinations"]
                        if not sources or not destinations:
                            continue
                        if len(sources) == 1:
                            source = sources[0]
                            for destination in destinations:
                                toOptimizeList.append(f"{plug} -- {source} -> {destination}")
                # conditional to check here
                if toOptimizeList:
                    self.found_issues.append(True)
                    if self.first_mode:
                        self.checked_items.append("\n".join(toOptimizeList))
                        self.good_results.append(False)
                    else: #fix
                        self.checked_items.append(self.ar.data.lang[self.title])
                        for item in check_items:
                            self.ar.utils.setProgress(self.ar.data.lang[self.title])
                            try:
                                optimizedList = []
                                for i in range(self.iterNumber):
                                    for plug, connections in self.getConnectionDic(item).items():
                                        sources = connections["sourceList"]
                                        destinations = connections["destinations"]
                                        if not sources or not destinations:
                                            continue
                                        if len(sources) == 1:
                                            source = sources[0]
                                            for destination in destinations:
                                                cmds.connectAttr(source, destination, force=True)
                                                optimizedList.append(f"{plug} -- {source} -> {destination}")
                                            # If the plug is a user defined attribute then we assume
                                            # it's a plug that is not used for computation at all.
                                            # And thus we can disconnect the input safely
                                            node, attr = plug.split(".", 1)
                                            user_defined = set(cmds.listAttr(node, userDefined=True) or [])
                                            if attr in user_defined:
                                                self.disconnectInputs(plug)
                                    if not optimizedList:
                                        # Nothing more to optimize
                                        break
                                if optimizedList:
                                    self.good_results.append(True)
                                    self.messages.append(self.ar.data.lang['v004_fixed']+": "+f"\n{self.ar.data.lang['v004_fixed']}: ".join(optimizedList))
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


    def pairwise(self, iterable, *args):
        """ s -> (s0,s1), (s2,s3), (s4, s5), ...
        """
        a = iter(iterable)
        return zip(a, a)
    

    @contextlib.contextmanager
    def unlocked(self, plug, *args):
        """ Unlock attribute during the context
        """
        locked = cmds.getAttr(plug, lock=True)
        if locked:
            cmds.setAttr(plug, lock=False)
        try:
            yield
        finally:
            if locked:
                cmds.setAttr(plug, lock=True)


    def disconnectInputs(self, plug, *args):
        """ Disconnect any input sources for the plug, including for locked attributes that can be unlocked
        """
        sourceList = cmds.listConnections(plug, plugs=True, source=True, destination=True, shapes=True, skipConversionNodes=False) or []
        if not sourceList:
            return
        
        with self.unlocked(plug):
            for dest, source in self.pairwise(sourceList):
                if cmds.isConnected(source, dest):
                    cmds.disconnectAttr(source, dest)
    

    def getConnectionDic(self, nodesOrPlugs, skipConversionNodes=True, *args):
        """ Return 'sources' and 'destinations' per plug for input nodes or plugs.
            Arguments:
                nodesOrPlugs (list or str): List or single string of node or node.attr name.
            Returns:
                dict: {plug: {"sources": sources, "destinations": destination}}
        """
        sourceList = cmds.listConnections(nodesOrPlugs, source=True, destination=False, connections=True, plugs=True, shapes=True, skipConversionNodes=skipConversionNodes) or []
        destinations = cmds.listConnections(nodesOrPlugs, source=False, destination=True, connections=True, plugs=True, shapes=True, skipConversionNodes=skipConversionNodes) or []
        if not sourceList and not destinations:
            return {}
        
        plugs = set()
        sourcesByPlugDic = defaultdict(list)
        for plug, src in self.pairwise(sourceList):
            sourcesByPlugDic[plug].append(src)
            plugs.add(plug)
        
        destinationsByPlugDic = defaultdict(list)
        for plug, dest in self.pairwise(destinations):
            destinationsByPlugDic[plug].append(dest)
            plugs.add(plug)
        
        resultDic = {}
        for plug in plugs:
            resultDic[plug] = {
                "sourceList": sourcesByPlugDic.get(plug, []),
                "destinations": destinationsByPlugDic.get(plug, [])
            }
        return resultDic
