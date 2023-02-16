# importing libraries:
from maya import cmds
from ..Modules.Library import dpUtils





# TODO check if we need these modules here
from ..Modules.Library import dpControls





# global variables to this module:    
CLASS_NAME = "CustomAttr"
TITLE = "m212_customAttr"
DESCRIPTION = "m213_customAttrDesc"
ICON = "/Icons/dp_customAttr.png"

DPCUSTOMATTR_VERSION = 1.0

ATTR_LIST = ['dpKeepIt']
ATTR_START = "dp"
IGNORE_LIST = ['persp', 'top', 'front', 'side']


class CustomAttr(object):
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, ui=True, *args, **kwargs):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.ui = ui
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
        self.itemList = []
        # call main UI function
        if self.ui:
            self.closeUI()
            self.mainUI()
            self.refreshUI()
            self.jobChangeSelection()
            

    def refreshUI(self, *args):
        """ Just call populate UI and actualize layout methodes.
        """
        self.populateItems()
#        self.populateAttrs()
#        self.actualizeEditLayout()

        
    def closeUI(self, *args):
        """ Delete existing CustomAttributes window if it exists.
        """
        if cmds.window('dpCustomAttributesWindow', query=True, exists=True):
            cmds.deleteUI('dpCustomAttributesWindow', window=True)


    def mainUI(self, *args):
        """ Create window, layouts and elements for the main UI.
        """
        self.attrUI = {}
        # window
        customAttributes_winWidth  = 380
        customAttributes_winHeight = 300
        cmds.window('dpCustomAttributesWindow', title=self.langDic[self.langName]['m212_customAttr']+" "+str(DPCUSTOMATTR_VERSION), widthHeight=(customAttributes_winWidth, customAttributes_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpCustomAttributesWindow')
        # create UI layout and elements:
        customAttributesLayout = cmds.columnLayout('customAttributesLayout', adjustableColumn=True, columnOffset=("both", 10))
        mainLayout = cmds.columnLayout('mainLayout', adjustableColumn=True, columnOffset=("both", 10), parent=customAttributesLayout)
        cmds.text("headerTxt", label=self.langDic[self.langName]['i267_customHeader']+' "'+ATTR_START+'"', align="left", height=30, font='boldLabelFont', parent=mainLayout)
        # selection collection
        self.selectionCollection = cmds.radioCollection('selectionCollection', parent=mainLayout)
        cmds.radioButton(label=self.langDic[self.langName]['i211_all'].capitalize(), annotation="all", onCommand=self.populateItems)
        cmds.radioButton(label=self.langDic[self.langName]['i266_selected'], annotation="selected", onCommand=self.populateItems)
        existing = cmds.radioButton(label=self.langDic[self.langName]['m071_existing'], annotation="existing", onCommand=self.populateItems)
        # items and attributes layout
        tablePaneLayout = cmds.paneLayout("tablePaneLayout", configuration="vertical2", separatorThickness=2, parent=mainLayout)
        leftColumnLayout = cmds.columnLayout('leftColumnLayout', adjustableColumn=True, columnOffset=("both", 2), parent=tablePaneLayout)
        cmds.separator(height=5, style="none", parent=leftColumnLayout)
        self.itemFilterTF = cmds.textField("itemFilterTF", text="", changeCommand=self.populateItems, parent=leftColumnLayout)
        cmds.separator(height=5, style="none", parent=leftColumnLayout)
        self.itemSL = cmds.textScrollList("itemSL", width=30, allowMultiSelection=True, selectCommand=self.actualizeFooter, parent=leftColumnLayout)
        # attribute layout
        self.rightColumnLayout = cmds.columnLayout('rightColumnLayout', adjustableColumn=True, columnOffset=("both", 2), parent=tablePaneLayout)
        
        # bottom layout for buttons
        buttonLayout = cmds.rowColumnLayout("buttonLayout", numberOfColumns=4, columnWidth=[(1, 60), (2, 60), (3, 100), (4, 60)], parent=mainLayout)
        cmds.button("addButton", label=self.langDic[self.langName]['i063_skinAddBtn'], backgroundColor=(0.6, 0.6, 0.6), parent=buttonLayout)
        cmds.button("removeButton", label=self.langDic[self.langName]['i064_skinRemBtn'], backgroundColor=(0.4, 0.4, 0.4), parent=buttonLayout)
        cmds.text("", parent=buttonLayout)
        cmds.button("refreshButton", label=self.langDic[self.langName]['m181_refresh'], backgroundColor=(0.5, 0.5, 0.5), command=self.populateItems, parent=buttonLayout)
        # set ui
        cmds.radioCollection(self.selectionCollection, edit=True, select=existing)

        
    def jobChangeSelection(self, *args):
        """ Create a scriptJob to read the selection changing to update the UI.
        """
        cmds.scriptJob(event=('SelectionChanged', self.refreshUI), parent='dpCustomAttributesWindow', replacePrevious=True, killWithScene=True, compressUndo=True, force=True)
    
    
    def populateItems(self, *args):
        """ Fill the items scroll list element with the choosen option (all, selected or existing).
        """
        # get current selection type (all, selected or existing custom attributes)
        selectionRadioButton = cmds.radioCollection(self.selectionCollection, query=True, select=True)
        radioButtonAnnotation = cmds.radioButton(selectionRadioButton, query=True, annotation=True)
        # fill conform
        if radioButtonAnnotation == "all":
            self.updateItemsList(cmds.ls(selection=False, type="transform"))
        elif radioButtonAnnotation == "selected":
            self.updateItemsList(cmds.ls(selection=True, type="transform"))
        elif radioButtonAnnotation == "existing":
            self.updateItemsList(self.getExistingList())
        self.populateAttrs()


    def getExistingList(self, *args):
        """ Check all nodes in the Maya's scene to find existing custom attributes.
            Return the existing custom attributes list of nodes.
        """
        existList = []
        allNodeList = cmds.ls(selection=False, type="transform")
        if allNodeList:
            for node in allNodeList:
                customAttrList = self.getCustomAttrList([node])
                if customAttrList:
                    existList.append(node)
        return existList


    def updateItemsList(self, thisList, *args):
        """ Use the given list to update the items scroll list in the UI.
        """
        self.itemList = list(set(thisList) - set(IGNORE_LIST))
        self.itemList.sort()
        cmds.textScrollList(self.itemSL, edit=True, removeAll=True)
        if thisList:
            self.filterList(thisList)
            cmds.textScrollList(self.itemSL, edit=True, append=self.itemList)


    def filterList(self, thisList, *args):
        """ Sort items by name filter.
            Redeclare self.itemList with the filtered list.
        """
        itemName = cmds.textField(self.itemFilterTF, query=True, text=True)
        if thisList and itemName:
            self.itemList = dpUtils.filterName(itemName, thisList, " ")


    def actualizeFooter(self, *args):
        """
        """
        #
        # WIP
        #
        print("fooooooter here")

    
    def populateAttrs(self, *args):
        """
        """
        self.cleanUpAttrData()
        customAttrList = self.getCustomAttrList(self.itemList)
        # fill with item list data
        if customAttrList:
            customAttrList = list(set(customAttrList)) #removes duplicated items
            for c, customAttr in enumerate(customAttrList):
                self.attrUI["attrTxt"+str(c)] = cmds.text("attrTxt"+str(c), label=customAttr[2:], align="center", height=30, font='boldLabelFont', parent=self.rightColumnLayout)
#                self.attrUI["attrSL"+str(c)] = cmds.textScrollList("attrSL"+str(c), width=30, allowMultiSelection=True, selectCommand=self.actualizeFooter, parent=self.rightColumnLayout)


    def cleanUpAttrData(self, *args):
        """ Delete the current attributes UI elements
        """
        if self.attrUI:
            for element in list(self.attrUI):
                cmds.deleteUI(self.attrUI[element])
            self.attrUI = {}


    def getCustomAttrList(self, thisList, *args):
        """
        """
        customAttrList = []
        if thisList:
            for item in thisList:
                currentItemAttrList = cmds.listAttr(item)
                for attr in currentItemAttrList:
                    if attr.startswith(ATTR_START):
                        if cmds.getAttr(item+"."+attr, type=True) == "bool":
                            customAttrList.append(attr)
        return customAttrList

##
#
#TODO
#
# define a good layout with scroll
# populate checkboxes
# custom attributes by user defined
# select item and activate just its checkboxes
# dpAttrList
# dpID
# 