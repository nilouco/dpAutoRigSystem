# https://gist.github.com/BigRoy/7784b266da449a5b5db7ed633302ebad

# importing libraries:
from maya import cmds
from collections import defaultdict
import contextlib
from ....Modules.Base import dpBaseAction

# global variables to this module:
CLASS_NAME = "PassthroughAttributes"
TITLE = "v107_passthroughAttributes"
DESCRIPTION = "v108_passthroughAttributesDesc"
ICON = "/Icons/dp_passthroughAttributes.png"

DP_PASSTHROUGHATTRIBUTES_VERSION = 1.00


class PassthroughAttributes(dpBaseAction.ActionStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        self.version = DP_PASSTHROUGHATTRIBUTES_VERSION
        dpBaseAction.ActionStartClass.__init__(self, *args, **kwargs)
    

    def runAction(self, firstMode=True, objList=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If firstMode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checkedObjList = node list of checked items
                - foundIssueList = True if an issue was found, False if there isn't an issue for the checked node
                - resultOkList = True if well done, False if we got an error
                - messageList = reported text
        """
        # starting
        self.firstMode = firstMode
        self.cleanUpToStart()
        self.iterNumber = 5
        
        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            if objList:
                toCheckList = objList
            else:
                toCheckList = cmds.ls(selection=False) #all
            if toCheckList:
                if self.firstMode:
                    self.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
                else:
                    self.utils.setProgress(max=len(toCheckList)*2, addOne=False, addNumber=False)
                toOptimizeList = []
                for item in toCheckList:
                    self.utils.setProgress(self.dpUIinst.lang[self.title])
                    # check optimization
                    for plug, connections in self.getConnectionDic(item).items():
                        sources = connections["sourceList"]
                        destinations = connections["destinationList"]
                        if not sources or not destinations:
                            continue
                        if len(sources) == 1:
                            source = sources[0]
                            for destination in destinations:
                                toOptimizeList.append(f"{plug} -- {source} -> {destination}")
                # conditional to check here
                if toOptimizeList:
                    self.foundIssueList.append(True)
                    if self.firstMode:
                        self.checkedObjList.append("\n".join(toOptimizeList))
                        self.resultOkList.append(False)
                    else: #fix
                        self.checkedObjList.append(self.dpUIinst.lang[self.title])
                        for item in toCheckList:
                            self.utils.setProgress(self.dpUIinst.lang[self.title])
                            try:
                                optimizedList = []
                                for i in range(self.iterNumber):
                                    for plug, connections in self.getConnectionDic(item).items():
                                        sources = connections["sourceList"]
                                        destinations = connections["destinationList"]
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
                                    self.resultOkList.append(True)
                                    self.messageList.append(self.dpUIinst.lang['v004_fixed']+": "+f"\n{self.dpUIinst.lang['v004_fixed']}: ".join(optimizedList))
                            except:
                                self.resultOkList.append(False)
                                self.messageList.append(self.dpUIinst.lang['v005_cantFix']+": "+item)
            else:
                self.notFoundNodes()
        else:
            self.notWorkedWellIO(self.dpUIinst.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---

        # finishing
        self.updateActionButtons()
        self.reportLog()
        self.endProgress()
        return self.dataLogDic


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
        destinationList = cmds.listConnections(nodesOrPlugs, source=False, destination=True, connections=True, plugs=True, shapes=True, skipConversionNodes=skipConversionNodes) or []
        if not sourceList and not destinationList:
            return {}
        
        plugs = set()
        sourcesByPlugDic = defaultdict(list)
        for plug, src in self.pairwise(sourceList):
            sourcesByPlugDic[plug].append(src)
            plugs.add(plug)
        
        destinationsByPlugDic = defaultdict(list)
        for plug, dest in self.pairwise(destinationList):
            destinationsByPlugDic[plug].append(dest)
            plugs.add(plug)
        
        resultDic = {}
        for plug in plugs:
            resultDic[plug] = {
                "sourceList": sourcesByPlugDic.get(plug, []),
                "destinationList": destinationsByPlugDic.get(plug, [])
            }
        return resultDic
