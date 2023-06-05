# importing libraries:
from maya import cmds
from ..Modules.Library import dpUtils
from functools import partial

# global variables to this module:
CLASS_NAME = "CustomAttr"
TITLE = "m212_customAttr"
DESCRIPTION = "m213_customAttrDesc"
ICON = "/Icons/dp_customAttr.png"

ATTR_START = "dp"
ATTR_DPID = "dpID"
ATTR_LIST = [ATTR_DPID, "dpDoNotSkinIt", "dpKeepIt", "dpIgnoreIt", "dpControl"]
IGNORE_LIST = ['persp', 'top', 'front', 'side']
DONOTDISPLAY_LIST = ['PaC', 'PoC', 'OrC', 'ScC', 'AiC', 'Jxt', 'Jar', 'Jad', 'Jcr', 'Jis', 'Jax', 'Jzt', 'JEnd', 'Eff', 'IKH', 'Handle', 'PVC']

DP_CUSTOMATTR_VERSION = 1.1


class CustomAttr(object):
    def __init__(self, dpUIinst, ui=True, *args, **kwargs):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.ui = ui
        self.mainWindowName = "dpCustomAttributesWindow"
        self.addWindowName = "dpAddCustomAttributesWindow"
        self.removeWindowName = "dpRemoveCustomAttributesWindow"
        # call main UI function
        if self.ui:
            dpUtils.closeUI(self.mainWindowName)
            dpUtils.closeUI(self.addWindowName)
            dpUtils.closeUI(self.removeWindowName)
            self.getItemFilter()
            self.mainUI()


    def getItemFilter(self, *args):
        """ Create a selection filter by transform type excluding the ignoreIt list.
        """
        self.itemF = cmds.itemFilter(byType="transform")
        for ignoreIt in IGNORE_LIST:
            self.itemF = cmds.itemFilter(difference=(self.itemF, cmds.itemFilter(byName=ignoreIt)))


    def mainUI(self, *args):
        """ Create window, layouts and elements for the main UI.
        """
        # window
        customAttributes_winWidth  = 380
        customAttributes_winHeight = 300
        cmds.window(self.mainWindowName, title=self.dpUIinst.lang['m212_customAttr']+" "+str(DP_CUSTOMATTR_VERSION), widthHeight=(customAttributes_winWidth, customAttributes_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        # create UI layout and elements:
        customAttributesLayout = cmds.columnLayout('customAttributesLayout', adjustableColumn=True, columnOffset=("both", 10))
        mainLayout = cmds.columnLayout('mainLayout', adjustableColumn=True, columnOffset=("both", 10), parent=customAttributesLayout)
        cmds.text("headerTxt", label=self.dpUIinst.lang['i267_customHeader']+' "'+ATTR_START+'"', align="left", height=30, font='boldLabelFont', parent=mainLayout)
        # filter
        filterLayout = cmds.columnLayout("filterLayout", adjustableColumn=True, parent=mainLayout)
        self.itemFilterTFG = cmds.textFieldButtonGrp("itemFilterTFG", label=self.dpUIinst.lang['i268_filterByName'], text="", buttonLabel=self.dpUIinst.lang['m004_select']+" "+self.dpUIinst.lang['i211_all'], buttonCommand=self.selectAllTransforms, changeCommand=self.filterByName, adjustableColumn=2, parent=filterLayout)
        cmds.separator(style='none', height=5, parent=filterLayout)
        # items and attributes layout
        tablePaneLayout = cmds.paneLayout("tablePaneLayout", parent=mainLayout)
        self.itemSC = cmds.selectionConnection(activeList=True)
        self.mainSSE = cmds.spreadSheetEditor(mainListConnection=self.itemSC, filter=self.itemF, attrRegExp=ATTR_START, niceNames=False, keyableOnly=False, parent=tablePaneLayout)
        # bottom layout for buttons
        cmds.separator(style='none', height=10, parent=mainLayout)
        buttonLayout = cmds.rowColumnLayout("buttonLayout", numberOfColumns=3, columnWidth=[(1, 80), (2, 80), (3, 100)], columnOffset=[(1, "both", 5), (2, "both", 5), (3, "both", 5)], parent=mainLayout)
        cmds.button("addButton", label=self.dpUIinst.lang['i063_skinAddBtn'], backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.addAttrUI, parent=buttonLayout)
        cmds.button("removeButton", label=self.dpUIinst.lang['i064_skinRemBtn'], backgroundColor=(0.4, 0.4, 0.4), width=70, command=self.removeAttrUI, parent=buttonLayout)
        cmds.button("updateIDButton", label=self.dpUIinst.lang['i089_update']+" "+ATTR_DPID, backgroundColor=(0.5, 0.5, 0.5), width=100, command=self.updateID, parent=buttonLayout)
        # call window
        cmds.showWindow(self.mainWindowName)


    def selectAllTransforms(self, *args):
        """ Just select all transform nodes in the scene.
        """
        cleanTransformList = []
        allTransformList = cmds.ls(selection=False, type="transform")
        for item in allTransformList:
            if not item in cleanTransformList:
                addThisItem = True
                for suffix in DONOTDISPLAY_LIST:
                    if suffix in item:
                        addThisItem = False
                if addThisItem:
                    cleanTransformList.append(item)
        cmds.select(cleanTransformList)


    def filterByName(self, filterName=None, *args):
        """ Sort items by name filter.
        """
        if not filterName:
            filterName = cmds.textFieldButtonGrp(self.itemFilterTFG, query=True, text=True)
        if filterName:
            currentItemList = cmds.selectionConnection(self.itemSC, query=True, object=True)
            if currentItemList:
                filteredItemList = dpUtils.filterName(filterName, currentItemList, " ")
                filteredItemList = list(set(filteredItemList) - set(IGNORE_LIST))
                filteredItemList.sort()
                cmds.selectionConnection(self.itemSC, edit=True, clear=True)
                for item in filteredItemList:
                    cmds.selectionConnection(self.itemSC, edit=True, select=item)
        cmds.textFieldButtonGrp(self.itemFilterTFG, edit=True, text="")


    def addAttrUI(self, *args):
        """ Create a window with buttons to add new attributes.
        """
        dpUtils.closeUI(self.addWindowName)
        add_winWidth  = 220
        add_winHeight = 260
        cmds.window(self.addWindowName, title=self.dpUIinst.lang['m212_customAttr']+" "+str(DP_CUSTOMATTR_VERSION), widthHeight=(add_winWidth, add_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        addAttrLayout = cmds.columnLayout('addAttrLayout', adjustableColumn=True, columnOffset=("both", 10))
        cmds.text("headerAddTxt", label=self.dpUIinst.lang['i045_add']+" "+self.dpUIinst.lang['m212_customAttr'], align="left", height=30, font='boldLabelFont', parent=addAttrLayout)
        cmds.separator(style='none', height=10, parent=addAttrLayout)
        for a, attr in enumerate(ATTR_LIST):
            cmds.button("addButton"+str(a), label=attr, backgroundColor=(0.6, 0.6, 0.6), command=partial(self.addAttr, a), parent=addAttrLayout)
            cmds.separator(style='none', height=5, parent=addAttrLayout)
        cmds.separator(style='single', height=10, parent=addAttrLayout)
        cmds.text("customAddTxt", label=self.dpUIinst.lang['m212_customAttr']+":", align="left", height=30, parent=addAttrLayout)
        self.addCustomAttrTFG = cmds.textFieldButtonGrp("addCustumAttrTFG", label="", text="", buttonLabel=self.dpUIinst.lang['i045_add'], buttonCommand=partial(self.addAttr, "custom", False), adjustableColumn=2, columnWidth=[(1, 0), (2, 50), (3, 30)], parent=addAttrLayout)
        cmds.showWindow(self.addWindowName)


    def addAttr(self, attrIndex, itemList=None, attrName=None, *args):
        """ Create attributes in the selected transform if they don't exists yet.
        """
        attr = None
        if not itemList:
            itemList = cmds.ls(selection=True)
        if itemList:
            for item in itemList:
                if attrIndex == "custom":
                    if attrName:
                        attr = attrName
                    elif self.ui:
                        attr = cmds.textFieldButtonGrp(self.addCustomAttrTFG, query=True, text=True)
                        if attr:
                            if not attr == ATTR_START:
                                if not attr.startswith(ATTR_START):
                                    attr = ATTR_START+attr[0].capitalize()+attr[1:]
                                else:
                                    point = len(ATTR_START)
                                    attr = attr[:point]+attr[point].capitalize()+attr[point+1:]
                            else:
                                attr = None
                elif attrIndex == 0: #dpID
                    if not cmds.objExists(item+"."+ATTR_DPID):
                        id = dpUtils.generateID(item)
                        cmds.addAttr(item, longName=ATTR_DPID, dataType="string")
                        cmds.setAttr(item+"."+ATTR_DPID, id, type="string", lock=True)
                else:
                    attr = ATTR_LIST[attrIndex]
                if attr:
                    if not cmds.objExists(item+"."+attr):
                        cmds.addAttr(item, longName=attr, attributeType="bool", defaultValue=1, keyable=False)
                        cmds.setAttr(item+"."+attr, edit=True, channelBox=False)
            if self.ui:
                if cmds.textFieldButtonGrp(self.addCustomAttrTFG, query=True, exists=True):
                    cmds.textFieldButtonGrp(self.addCustomAttrTFG, edit=True, text="")


    def removeAttrUI(self, *args):
        """ Create a window showing the current dp custom attributes to delete them.
        """
        dpUtils.closeUI(self.removeWindowName)
        remove_winWidth  = 200
        remove_winHeight = 250
        cmds.window(self.removeWindowName, title=self.dpUIinst.lang['m212_customAttr']+" "+str(DP_CUSTOMATTR_VERSION), widthHeight=(remove_winWidth, remove_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        removeAttrLayout = cmds.columnLayout('removeAttrLayout', adjustableColumn=True, columnOffset=("both", 10))
        cmds.text("headerRemoveTxt", label=self.dpUIinst.lang['i046_remove']+" "+self.dpUIinst.lang['m212_customAttr'], align="left", height=30, font='boldLabelFont', parent=removeAttrLayout)
        cmds.separator(style='none', height=10, parent=removeAttrLayout)
        toRemoveAttrList = self.getCustomAttrList()
        if toRemoveAttrList:
            toRemoveAttrList = list(set(toRemoveAttrList))
            toRemoveAttrList.sort()
            for rAttr in toRemoveAttrList:
                cmds.button("removeButton"+rAttr, label=rAttr, backgroundColor=(0.6, 0.6, 0.6), command=partial(self.removeAttr, rAttr), parent=removeAttrLayout)
                cmds.separator(style='none', height=5, parent=removeAttrLayout)
        else:
            cmds.text("noCustomAttrTxt", label=self.dpUIinst.lang['i062_notFound']+" "+self.dpUIinst.lang['m212_customAttr'])
        cmds.showWindow(self.removeWindowName)


    def removeAttr(self, attr, itemList=None, *args):
        """ Delete the given attribute and reload the removeAttrUI.
        """
        itemList = self.getItemList(itemList)
        if itemList:
            for item in itemList:
                if cmds.objExists(item+"."+attr):
                    cmds.setAttr(item+"."+attr, edit=True, lock=False)
                    cmds.deleteAttr(item+"."+attr)
                    if self.ui:
                        if cmds.button("removeButton"+attr, query=True, exists=True):
                            cmds.deleteUI("removeButton"+attr)


    def getCustomAttrList(self, itemList=None, *args):
        """ Return all boolean attributes starting "dp".
        """
        customAttrList = []
        itemList = self.getItemList(itemList)
        if itemList:    
            for item in itemList:
                currentItemAttrList = cmds.listAttr(item)
                if currentItemAttrList:
                    if ATTR_DPID in currentItemAttrList:
                        customAttrList.append(ATTR_DPID)
                    for attr in currentItemAttrList:
                        if attr.startswith(ATTR_START):
                            if cmds.getAttr(item+"."+attr, type=True) == "bool":
                                customAttrList.append(attr)
        return customAttrList


    def getItemList(self, itemList=None, *args):
        """ Check if the itemList is a valid item or select all transform to return it.
        """
        if not itemList:
            return cmds.ls(selection=True, type="transform")
        return itemList


    def updateID(self, itemList=None, *args):
        """ Remove and Add a new dpID attribute.
        """
        self.removeAttr(ATTR_DPID, itemList)
        self.addAttr(0, itemList)
