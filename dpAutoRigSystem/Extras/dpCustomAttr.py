# importing libraries:
from maya import cmds
from ..Modules.Library import dpUtils


# global variables to this module:
CLASS_NAME = "CustomAttr"
TITLE = "m212_customAttr"
DESCRIPTION = "m213_customAttrDesc"
ICON = "/Icons/dp_customAttr.png"

DPCUSTOMATTR_VERSION = 1.0

ATTR_LIST = ['dpKeepIt']
ATTR_START = "dp"
ATTR_DPID = "dpID"
ATTR_IGNORE = "Count"
IGNORE_LIST = ['persp', 'top', 'front', 'side']
DONOTDISPLAY_LIST = ['PaC', 'PoC', 'OrC', 'ScC', 'AiC', 'Jxt', 'Jar', 'Jad', 'Jcr', 'Jis', 'Jax', 'Jzt', 'JEnd', 'Eff', 'IKH', 'Handle', 'PVC']


class CustomAttr(object):
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, ui=True, *args, **kwargs):
        # redeclaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
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
        """
        """
        self.itemF = cmds.itemFilter(byType="transform")
        for ignoreIt in IGNORE_LIST:
            self.itemF = cmds.itemFilter(difference=(self.itemF, cmds.itemFilter(byName=ignoreIt)))


    def mainUI(self, *args):
        """ Create window, layouts and elements for the main UI.
        """
        self.attrUI = {}
        # window
        customAttributes_winWidth  = 380
        customAttributes_winHeight = 300
        cmds.window(self.mainWindowName, title=self.langDic[self.langName]['m212_customAttr']+" "+str(DPCUSTOMATTR_VERSION), widthHeight=(customAttributes_winWidth, customAttributes_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        # create UI layout and elements:
        customAttributesLayout = cmds.columnLayout('customAttributesLayout', adjustableColumn=True, columnOffset=("both", 10))
        mainLayout = cmds.columnLayout('mainLayout', adjustableColumn=True, columnOffset=("both", 10), parent=customAttributesLayout)
        cmds.text("headerTxt", label=self.langDic[self.langName]['i267_customHeader']+' "'+ATTR_START+'"', align="left", height=30, font='boldLabelFont', parent=mainLayout)
        # filter
        filterLayout = cmds.columnLayout("filterLayout", adjustableColumn=True, parent=mainLayout)
        self.itemFilterTFG = cmds.textFieldButtonGrp("itemFilterTFG", label=self.langDic[self.langName]['i268_filterByName'], text="", buttonLabel=self.langDic[self.langName]['m004_select']+" "+self.langDic[self.langName]['i211_all'], buttonCommand=self.selectAllTransforms, changeCommand=self.filterByName, adjustableColumn=2, parent=filterLayout)
        cmds.separator(style='none', height=5, parent=filterLayout)
        # items and attributes layout
        tablePaneLayout = cmds.paneLayout("tablePaneLayout", parent=mainLayout)
        self.itemSC = cmds.selectionConnection(activeList=True)
        self.mainSSE = cmds.spreadSheetEditor(mainListConnection=self.itemSC, filter=self.itemF, attrRegExp=ATTR_START, niceNames=False, keyableOnly=False, parent=tablePaneLayout)
        # bottom layout for buttons
        cmds.separator(style='none', height=10, parent=mainLayout)
        buttonLayout = cmds.rowColumnLayout("buttonLayout", numberOfColumns=2, columnWidth=[(1, 60), (2, 60)], columnOffset=[(1, "both", 5), (2, "both", 5)], parent=mainLayout)
        cmds.button("addButton", label=self.langDic[self.langName]['i063_skinAddBtn'], backgroundColor=(0.6, 0.6, 0.6), command=self.addAttrUI, parent=buttonLayout)
        cmds.button("removeButton", label=self.langDic[self.langName]['i064_skinRemBtn'], backgroundColor=(0.4, 0.4, 0.4), command=self.removeAttrUI, parent=buttonLayout)
        # call window
        cmds.showWindow(self.mainWindowName)


    def selectAllTransforms(self, *args):
        """
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
        """
        """
        print("merci")


    def removeAttrUI(self, *args):
        """
        """
        print("thanks")

    
    def addAttr(self, attr, itemList, *args):
        """
        """
        print("kombi")


    def removeAttr(self, attr, itemList, *args):
        """
        """
        print("netoDaPrefeitura")


    def generateID(self, itemList, *args):
        """
        """
        print("Affrixieieity")



#####################
#
#TODO
#
# buttons
#   add
#   remove
#   refresh?
# dpAttrList
# dpID
#
# review UI
# 