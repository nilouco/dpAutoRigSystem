# importing libraries:
from maya import cmds
from functools import partial

# global variables to this module:
CLASS_NAME = "CustomAttr"
TITLE = "m212_customAttr"
DESCRIPTION = "m213_customAttrDesc"
ICON = "/Icons/dp_customAttr.png"

ATTR_START = "dp"
ATTR_DPID = "dpID"
ATTR_LIST = [ATTR_DPID, "dpControl", "dpDoNotProxyIt", "dpDoNotSkinIt", "dpIgnoreIt", "dpKeepIt", "dpHeadDeformerInfluence", "dpJawDeformerInfluence", "dpNotTransformIO"]
DEFAULTIGNORE_LIST = ['persp', 'top', 'front', 'side']
DEFAULTDONOTDISPLAY_LIST = ['PaC', 'PoC', 'OrC', 'ScC', 'AiC', 'Jxt', 'Jar', 'Jad', 'Jcr', 'Jis', 'Jax', 'Jzt', 'JEnd', 'Eff', 'IKH', 'Handle', 'PVC']
DEFAULTTYPE_LIST = ['transform', 'network']

DP_CUSTOMATTR_VERSION = 1.6


class CustomAttr(object):
    def __init__(self, dpUIinst, ui=True, *args, **kwargs):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.ui = ui
        self.utils = self.dpUIinst.utils
        self.mainWindowName = "dpCustomAttributesWindow"
        self.addWindowName = "dpAddCustomAttributesWindow"
        self.removeWindowName = "dpRemoveCustomAttributesWindow"
        self.doNotDisplayList = DEFAULTDONOTDISPLAY_LIST.copy()
        self.ignoreList = DEFAULTIGNORE_LIST.copy()
        self.typeList = DEFAULTTYPE_LIST.copy()
        # call main UI function
        if self.ui:
            self.utils.closeUI(self.mainWindowName)
            self.utils.closeUI(self.addWindowName)
            self.utils.closeUI(self.removeWindowName)
            self.getItemFilter()
            self.mainUI()


    def getItemFilter(self, *args):
        """ Create a selection filter by node type excluding the ignoreIt list.
        """
        self.itemSC = cmds.selectionConnection(activeList=True)
        self.itemF = cmds.itemFilter(byType=self.typeList)
        for ignoreIt in self.ignoreList:
            self.itemF = cmds.itemFilter(difference=(self.itemF, cmds.itemFilter(byName=ignoreIt)))


    def mainUI(self, *args):
        """ Create window, layouts and elements for the main UI.
        """
        # window
        customAttributes_winWidth  = 380
        customAttributes_winHeight = 350
        cmds.window(self.mainWindowName, title=self.dpUIinst.lang['m212_customAttr']+" "+str(DP_CUSTOMATTR_VERSION), widthHeight=(customAttributes_winWidth, customAttributes_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        # create UI layout and elements:
        customAttributesLayout = cmds.columnLayout('customAttributesLayout', adjustableColumn=True, columnOffset=("both", 10))
        mainLayout = cmds.columnLayout('mainLayout', adjustableColumn=True, columnOffset=("both", 10), parent=customAttributesLayout)
        cmds.text("headerTxt", label=self.dpUIinst.lang['i267_customAttrHeader']+' "'+ATTR_START+'"', align="left", height=30, font='boldLabelFont', parent=mainLayout)
        # filter
        filterLayout = cmds.columnLayout("filterLayout", adjustableColumn=True, parent=mainLayout)
        self.itemFilterTFG = cmds.textFieldButtonGrp("itemFilterTFG", label=self.dpUIinst.lang['i268_filterByName'], text="", buttonLabel=self.dpUIinst.lang['m004_select']+" "+self.dpUIinst.lang['i211_all'], buttonCommand=self.selectNodes, changeCommand=self.filterByName, adjustableColumn=2, parent=filterLayout)
        cmds.separator(style='none', height=5, parent=filterLayout)
        # items and attributes layout
        tablePaneLayout = cmds.paneLayout("tablePaneLayout", parent=mainLayout)
        self.mainSSE = cmds.spreadSheetEditor(mainListConnection=self.itemSC, filter=self.itemF, attrRegExp=ATTR_START, niceNames=False, keyableOnly=False, parent=tablePaneLayout)
        # bottom layout for buttons
        cmds.separator(style='none', height=10, parent=mainLayout)
        buttonLayout = cmds.rowColumnLayout("buttonLayout", numberOfColumns=3, columnWidth=[(1, 80), (2, 80), (3, 100)], columnOffset=[(1, "both", 5), (2, "both", 5), (3, "both", 5)], parent=mainLayout)
        cmds.button("addButton", label=self.dpUIinst.lang['i063_skinAddBtn'], backgroundColor=(0.6, 0.6, 0.6), width=70, command=self.addAttrUI, parent=buttonLayout)
        cmds.button("removeButton", label=self.dpUIinst.lang['i064_skinRemBtn'], backgroundColor=(0.4, 0.4, 0.4), width=70, command=self.removeAttrUI, parent=buttonLayout)
        cmds.button("updateIDButton", label=self.dpUIinst.lang['i089_update']+" "+ATTR_DPID, backgroundColor=(0.5, 0.5, 0.5), width=100, command=self.updateID, parent=buttonLayout)
        cmds.separator(style='none', height=15, parent=mainLayout)
        # settings - frameLayout:
        settingsFL = cmds.frameLayout('settingsFL', label=self.dpUIinst.lang['i215_setAttr'], collapsable=True, collapse=True, parent=mainLayout)
        settingsCL = cmds.columnLayout('settingsCL', adjustableColumn=True, columnOffset=('left', 5), parent=settingsFL)
        # type
        cmds.text('typeTxt', align='left', label=self.dpUIinst.lang['i138_type'], height=30, font='boldLabelFont', parent=settingsCL)

        self.typeAllCB = cmds.checkBox('typeAllCB', label=self.dpUIinst.lang['i339_any'].capitalize(), align='left', value=0, changeCommand=partial(self.updateType, "any"), parent=settingsCL)
        self.typeTransformCB = cmds.checkBox('transform', label="transform", align='left', value=1, changeCommand=partial(self.updateType, "transform"), parent=settingsCL)
        self.typeNetworkCB = cmds.checkBox('network', label="network", align='left', value=1, changeCommand=partial(self.updateType, "network"), parent=settingsCL)
        cmds.separator(style='in', height=15, parent=settingsCL)
        
        # display
        cmds.text('displayTxt', align='left', label=self.dpUIinst.lang['m217_suffix']+" "+self.dpUIinst.lang['c126_display'], height=30, font='boldLabelFont', parent=settingsCL)
        diplayRCL = cmds.rowColumnLayout('displayRCL', numberOfColumns=6, columnWidth=[(1, 70), (2, 70), (3, 70), (4, 70), (5, 70), (6, 70)], columnAlign=[(1, 'left'), (2, 'left'), (3, 'left'), (4, 'left'), (5, 'left'), (6, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 10), (3, 'left', 10), (4, 'left', 10), (5, 'left', 10), (6, 'left', 10)], parent=settingsCL)
        self.displayPaCCB = cmds.checkBox('displayPaCCB', label="PaC", annotation="Parent constraint", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayPoCCB = cmds.checkBox('displayPoCCB', label="PoC", annotation="Point constraint", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayOrCCB = cmds.checkBox('displayOrCCB', label="OrC", annotation="Orient constraint", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayScCCB = cmds.checkBox('displayScCCB', label="ScC", annotation="Scale constraint", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayAiCCB = cmds.checkBox('displayAiCCB', label="AiC", annotation="Aim constraint", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayPVCCB = cmds.checkBox('displayPVCCB', label="PVC", annotation="Pole Vector Constraint", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayJntCB = cmds.checkBox('displayJntCB', label="Jnt", annotation="Skinned joint", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayJxtCB = cmds.checkBox('displayJxtCB', label="Jxt", annotation="Extra joint", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayJarCB = cmds.checkBox('displayJarCB', label="Jar", annotation="Ariticulation joint", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayJadCB = cmds.checkBox('displayJadCB', label="Jad", annotation="Additional joint", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayJcrCB = cmds.checkBox('displayJcrCB', label="Jcr", annotation="Corrective joint", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayJisCB = cmds.checkBox('displayJisCB', label="Jis", annotation="Indirect skinning joint", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayJaxCB = cmds.checkBox('displayJaxCB', label="Jax", annotation="Extra articulation joint", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayJztCB = cmds.checkBox('displayJztCB', label="Jzt", annotation="Zero out joint", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayJEndCB = cmds.checkBox('displayJEndCB', label="JEnd", annotation="End joint", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayEffCB = cmds.checkBox('displayEffCB', label="Eff", annotation="Effector", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayIKHCB = cmds.checkBox('displayIKHCB', label="IKH", annotation="Ik Handle", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        self.displayHandleCB = cmds.checkBox('displayHandleCB', label="Handle", annotation="Deformer Handle", align='left', value=0, changeCommand=self.updateNameDisplay, parent=diplayRCL)
        cmds.separator(style='none', height=15, parent=mainLayout)
        # storing checkBoxes lists
        self.typeCBList = [self.typeTransformCB, self.typeNetworkCB]
        self.displayCBList = [self.displayPaCCB, self.displayPoCCB, self.displayOrCCB, self.displayScCCB, self.displayAiCCB, self.displayPVCCB, self.displayJntCB, self.displayJxtCB, self.displayJarCB, self.displayJadCB, self.displayJcrCB, self.displayJisCB, self.displayJaxCB, self.displayJztCB, self.displayEffCB, self.displayIKHCB, self.displayHandleCB]
        # call window
        cmds.showWindow(self.mainWindowName)


    def updateUI(self, *args):
        self.getItemFilter()
        cmds.spreadSheetEditor(self.mainSSE, edit=True, mainListConnection=self.itemSC, filter=self.itemF, attrRegExp=ATTR_START, niceNames=False, keyableOnly=False)




    def updateNameDisplay(self, *args):
        """ Update item filter name display argument.
        """
        print("argsName....", args)




    def updateType(self, typeName, value, *args):
        """ Change node type to display in the UI.
        """
        if typeName == "any":
            if value:
                self.typeList = []
                for cbItem in self.typeCBList:
                    cmds.checkBox(cbItem, edit=True, value=1, enable=0)
            else:
                self.typeList = DEFAULTTYPE_LIST.copy()
                for cbItem in self.typeCBList:
                    cmds.checkBox(cbItem, edit=True, value=1, enable=1)
        else:
            if value and not typeName in self.typeList:
                self.typeList.append(typeName)
            elif typeName in self.typeList:
                self.typeList.remove(typeName)
        self.updateUI()


    def selectNodes(self, *args):
        """ Select the desired type nodes in the scene.
        """
        toSelectList = []
        if self.typeList:
            nodeList = cmds.ls(type=self.typeList)
        else:
            nodeList = cmds.ls(defaultNodes=False)
        if nodeList:
            for item in nodeList:
                if not item in toSelectList:
                    addThisItem = True
                    for suffix in self.doNotDisplayList:
                        if item.endswith(suffix):
                            addThisItem = False
                    if addThisItem:
                        toSelectList.append(item)
            if toSelectList:
                toSelectList.sort()
            cmds.select(toSelectList)
            self.updateUI()


    def filterByName(self, filterName=None, *args):
        """ Sort items by name filter.
        """
        if not filterName:
            filterName = cmds.textFieldButtonGrp(self.itemFilterTFG, query=True, text=True)
        if filterName:
            currentItemList = cmds.selectionConnection(self.itemSC, query=True, object=True)
            if currentItemList:
                filteredItemList = self.utils.filterName(filterName, currentItemList, " ")
                filteredItemList = list(set(filteredItemList) - set(self.ignoreList))
                filteredItemList.sort()
                cmds.selectionConnection(self.itemSC, edit=True, clear=True)
                for item in filteredItemList:
                    cmds.selectionConnection(self.itemSC, edit=True, select=item)
        cmds.textFieldButtonGrp(self.itemFilterTFG, edit=True, text="")


    def addAttrUI(self, *args):
        """ Create a window with buttons to add new attributes.
        """
        self.utils.closeUI(self.addWindowName)
        add_winWidth  = 220
        add_winHeight = 260
        cmds.window(self.addWindowName, title=self.dpUIinst.lang['m212_customAttr']+" "+str(DP_CUSTOMATTR_VERSION), widthHeight=(add_winWidth, add_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        addAttrLayout = cmds.columnLayout('addAttrLayout', adjustableColumn=True, columnOffset=("both", 10))
        cmds.text("headerAddTxt", label=self.dpUIinst.lang['i045_add']+" "+self.dpUIinst.lang['m212_customAttr'], align="left", height=30, font='boldLabelFont', parent=addAttrLayout)
        cmds.separator(style='none', height=10, parent=addAttrLayout)
        for a, attr in enumerate(ATTR_LIST):
            cmds.button("addButton"+str(a), label=attr, backgroundColor=(0.6, 0.6, 0.6), command=partial(self.addAttr, a), parent=addAttrLayout)
            cmds.separator(style='none', height=5, parent=addAttrLayout)
        cmds.separator(style='in', height=10, parent=addAttrLayout)
        cmds.text("customAddTxt", label=self.dpUIinst.lang['m212_customAttr']+":", align="left", height=30, parent=addAttrLayout)
        self.addCustomAttrTFG = cmds.textFieldButtonGrp("addCustomAttrTFG", label="", text="", buttonLabel=self.dpUIinst.lang['i045_add'], buttonCommand=partial(self.addAttr, "custom", False), adjustableColumn=2, columnWidth=[(1, 0), (2, 50), (3, 30)], parent=addAttrLayout)
        cmds.showWindow(self.addWindowName)


    def getDescendentsList(self, itemList, shapes=True, *args):
        """ Returns the children nodes or shapes from given item list.
        """
        resultList = []
        for item in itemList:
            if cmds.objExists(item):
                childrenList = cmds.listRelatives(item, allDescendents=True, children=True)
                if shapes:
                    childrenList = cmds.listRelatives(item, allDescendents=True, children=True, shapes=True)
                if childrenList:
                    resultList.extend(childrenList)
        return resultList


    def addAttr(self, attrIndex, itemList=None, attrName=None, shapes=True, descendents=False, *args):
        """ Create attributes in the selected node if they don't exists yet.
        """
        attr = None
        if not itemList:
            itemList = cmds.ls(selection=True)
        if itemList:
            if shapes:
                itemList.extend(self.getDescendentsList(itemList))
            if descendents:
                itemList.extend(self.getDescendentsList(itemList, False))
            itemList = list(set(itemList)) # just remove duplicated items
            for item in itemList:
                if cmds.objExists(item):
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
                                cmds.textFieldButtonGrp(self.addCustomAttrTFG, edit=True, text="")
                    elif attrIndex == 0: #dpID
                        #if not cmds.objExists(item+"."+ATTR_DPID):
                        #if not ATTR_DPID in (cmds.listAttr(item, userDefined=True) or []):
                        if not cmds.attributeQuery(ATTR_DPID, node=item, exists=True):
                            id = self.utils.generateID(item)
                            cmds.addAttr(item, longName=ATTR_DPID, dataType="string")
                            cmds.setAttr(item+"."+ATTR_DPID, id, type="string", lock=True)
                        elif not self.utils.validateID(item):
                            self.updateID([item])
                    else:
                        attr = ATTR_LIST[attrIndex]
                    if attr:
                        if not cmds.attributeQuery(attr, node=item, exists=True):
                            cmds.addAttr(item, longName=attr, attributeType="bool", defaultValue=1, keyable=False)
                            cmds.setAttr(item+"."+attr, edit=True, channelBox=False)


    def removeAttrUI(self, *args):
        """ Create a window showing the current dp custom attributes to delete them.
        """
        self.utils.closeUI(self.removeWindowName)
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
                if cmds.attributeQuery(attr, node=item, exists=True):
                    cmds.setAttr(item+"."+attr, edit=True, lock=False)
                    cmds.deleteAttr(item+"."+attr)
                    if self.ui:
                        if cmds.button("removeButton"+attr, query=True, exists=True):
                            cmds.deleteUI("removeButton"+attr)


    def getCustomAttrList(self, itemList=None, *args):
        """ Return all boolean attributes starting with "dp".
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
        """ Check if the itemList is a valid item or select all type to return it.
        """
        if not itemList:
            return cmds.ls(selection=True, type=self.typeList)
        return itemList


    def updateID(self, itemList=None, *args):
        """ Remove and Add a new dpID attribute.
        """
        self.removeAttr(ATTR_DPID, itemList)
        self.addAttr(0, itemList)
