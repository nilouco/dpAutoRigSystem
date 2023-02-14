# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
from . import dpRivet
from ..Modules.Library import dpControls
from ..Modules.Library import dpUtils


# global variables to this module:    
CLASS_NAME = "CustomAttr"
TITLE = "m212_customAttr"
DESCRIPTION = "m213_customAttrDesc"
ICON = "/Icons/dp_customAttr.png"

DPCUSTOMATTR_VERSION = 1.0



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
        # call main UI function
        if self.ui:
            self.closeUI()
            self.mainUI()
#            self.refreshUI()
            

#    def refreshUI(self, *args):
#        """ Just call populate UI and actualize layout methodes.
#        """
#        self.pupulateItems()
#        self.actualizeEditLayout()

        
    def closeUI(self, *args):
        """ Delete existing CustomAttributes window if it exists.
        """
        if cmds.window('dpCustomAttributesWindow', query=True, exists=True):
            cmds.deleteUI('dpCustomAttributesWindow', window=True)


    def mainUI(self, *args):
        """ Create window, layouts and elements for the main UI.
        """
        # window
        customAttributes_winWidth  = 380
        customAttributes_winHeight = 300
        cmds.window('dpCustomAttributesWindow', title=self.langDic[self.langName]['m212_customAttr']+" "+str(DPCUSTOMATTR_VERSION), widthHeight=(customAttributes_winWidth, customAttributes_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpCustomAttributesWindow')
        # create UI layout and elements:
        customAttributesLayout = cmds.columnLayout('customAttributesLayout', adjustableColumn=True, columnOffset=("both", 10))
#        cmds.text("infoTxt", label=self.langDic[self.langName]['m066_selectTwo'], align="left", height=30, font='boldLabelFont', parent=customAttributesLayout)
        mainLayout = cmds.columnLayout('mainLayout', adjustableColumn=True, columnOffset=("both", 10), parent=customAttributesLayout)

        self.selectionCollection = cmds.radioCollection('selectionCollection', parent=mainLayout)
        cmds.radioButton(label=self.langDic[self.langName]['i211_all'].capitalize(), annotation="all", onCommand=self.populateItems)
        cmds.radioButton(label=self.langDic[self.langName]['i266_selected'], annotation="selected", onCommand=self.populateItems)
        existing = cmds.radioButton(label=self.langDic[self.langName]['m071_existing'], annotation="existing", onCommand=self.populateItems)
        cmds.radioCollection(self.selectionCollection, edit=True, select=existing)

        tablePaneLayout = cmds.paneLayout("tablePaneLayout", configuration="vertical2", separatorThickness=2, parent=mainLayout)
        leftColumnLayout = cmds.columnLayout('leftColumnLayout', adjustableColumn=True, columnOffset=("both", 2), parent=tablePaneLayout)
        cmds.text("itemsTxt", label="Nodes", align="left", height=30, font='boldLabelFont', parent=leftColumnLayout)
        self.itemSL = cmds.textScrollList("itemSL", width=30, allowMultiSelection=True, selectCommand=self.actualizeFooter, parent=leftColumnLayout)
        
        rightColumnLayout = cmds.columnLayout('rightColumnLayout', adjustableColumn=True, columnOffset=("both", 2), parent=tablePaneLayout)
        rightRowColumnLayout = cmds.rowColumnLayout("rightRowColumnLayout", numberOfColumns=3, parent=rightColumnLayout)
        cmds.text("attr1Txt", label="Attr1", align="center", height=30, font='boldLabelFont', parent=rightRowColumnLayout)
        cmds.text("attr2Txt", label="Attr2", align="center", height=30, font='boldLabelFont', parent=rightRowColumnLayout)
        cmds.text("attr3Txt", label="Attr3", align="center", height=30, font='boldLabelFont', parent=rightRowColumnLayout)
        self.attr1SL = cmds.textScrollList("attr1SL", width=30, allowMultiSelection=True, selectCommand=self.actualizeFooter, parent=rightRowColumnLayout)
        self.attr3SL = cmds.textScrollList("attr2SL", width=30, allowMultiSelection=True, selectCommand=self.actualizeFooter, parent=rightRowColumnLayout)
        self.attr3SL = cmds.textScrollList("attr3SL", width=30, allowMultiSelection=True, selectCommand=self.actualizeFooter, parent=rightRowColumnLayout)

        buttonLayout = cmds.rowColumnLayout("buttonLayout", numberOfColumns=4, columnWidth=[(1, 60), (2, 60), (3, 100), (4, 60)], parent=mainLayout)
        cmds.button("addButton", label=self.langDic[self.langName]['i063_skinAddBtn'], backgroundColor=(0.6, 0.6, 0.6), parent=buttonLayout)
        cmds.button("removeButton", label=self.langDic[self.langName]['i064_skinRemBtn'], backgroundColor=(0.4, 0.4, 0.4), parent=buttonLayout)
        cmds.text("")
        cmds.button("refreshButton", label=self.langDic[self.langName]['m181_refresh'], backgroundColor=(0.5, 0.5, 0.5), parent=buttonLayout)

        

    
    
    def populateItems(self, *args):
        """
        """
        # get current selection type (all, selected or existing custom attributes)
        selectionRadioButton = cmds.radioCollection(self.selectionCollection, query=True, select=True)
        radioButtonAnnotation = cmds.radioButton(selectionRadioButton, query=True, annotation=True)
        
        
        #
        # WIP
        #

        

        if radioButtonAnnotation == "all":
            print("all, merci")
        elif radioButtonAnnotation == "selected":
            print("selected, merci2")
        elif radioButtonAnnotation == "existing":
            print("existing, merci3")





    def actualizeFooter(self, *args):
        """
        """
        #
        # WIP
        #
        print("fooooooter here")