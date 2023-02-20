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
        # call main UI function
        if self.ui:
            self.getItemFilter()
            self.closeUI()
            self.mainUI()


    def getItemFilter(self, *args):
        """
        """
        self.itemF = cmds.itemFilter(byType="transform")
        for ignoreIt in IGNORE_LIST:
            self.itemF = cmds.itemFilter(difference=(self.itemF, cmds.itemFilter(byName=ignoreIt)))


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
        # create UI layout and elements:
        customAttributesLayout = cmds.columnLayout('customAttributesLayout', adjustableColumn=True, columnOffset=("both", 10))
        mainLayout = cmds.columnLayout('mainLayout', adjustableColumn=True, columnOffset=("both", 10), parent=customAttributesLayout)
        cmds.text("headerTxt", label=self.langDic[self.langName]['i267_customHeader']+' "'+ATTR_START+'"', align="left", height=30, font='boldLabelFont', parent=mainLayout)
        
        filterLayout = cmds.columnLayout("filterLayout", adjustableColumn=True, parent=mainLayout)
        self.itemFilterTFG = cmds.textFieldButtonGrp("itemFilterTFG", label=self.langDic[self.langName]['i268_filterByName'], text="", buttonLabel=self.langDic[self.langName]['m004_select']+" "+self.langDic[self.langName]['i211_all'], buttonCommand=self.selectAllTransforms, changeCommand=self.filterByName, adjustableColumn=2, parent=filterLayout)

        # items and attributes layout
        tablePaneLayout = cmds.paneLayout("tablePaneLayout", parent=mainLayout)
        self.itemSC = cmds.selectionConnection(activeList=True)
        self.mainSSE = cmds.spreadSheetEditor(mainListConnection=self.itemSC, filter=self.itemF, attrRegExp=ATTR_START, niceNames=False, keyableOnly=False, parent=tablePaneLayout)
        
        # bottom layout for buttons
        buttonLayout = cmds.rowColumnLayout("buttonLayout", numberOfColumns=4, columnWidth=[(1, 60), (2, 60), (3, 100), (4, 60)], parent=mainLayout)
        cmds.button("addButton", label=self.langDic[self.langName]['i063_skinAddBtn'], backgroundColor=(0.6, 0.6, 0.6), parent=buttonLayout)
        cmds.button("removeButton", label=self.langDic[self.langName]['i064_skinRemBtn'], backgroundColor=(0.4, 0.4, 0.4), parent=buttonLayout)
        cmds.text("", parent=buttonLayout)
        cmds.button("refreshButton", label=self.langDic[self.langName]['m181_refresh'], backgroundColor=(0.5, 0.5, 0.5), parent=buttonLayout)
        
        # set ui
        cmds.showWindow('dpCustomAttributesWindow')


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