# importing libraries:
from maya import cmds
from maya import mel

# global variables to this module:
CLASS_NAME = "Renamer"
TITLE = "m214_renamer"
DESCRIPTION = "m215_renamerDesc"
ICON = "/Icons/dp_renamer.png"

DP_RENAMER_VERSION = 1.1


class Renamer():
    def __init__(self, dpUIinst, ui=True, *args, **kwargs):
        # defining variables
        self.dpUIinst = dpUIinst
        self.selOption = 1 #Selected
        self.originalList, self.previewList = [], []
        self.addSequence = None
        self.addPrefix = None
        self.addSuffix = None
        self.searchReplace = None
        self.sequenceName = None
        self.prefixName = None
        self.suffixName = None
        self.searchName = None
        self.replaceName = None
        self.padding = 2
        self.start = 0
        self.ui = ui
        # call main function
        if self.ui:
            self.renamerUI()
            cmds.scriptJob(event=('SelectionChanged', self.refreshPreview), parent='dpRenamerWin', replacePrevious=True, killWithScene=True, compressUndo=True, force=True)
    
    
    def closeRenamerUI(self, *args):
        """ Check if the UI exists then close it.
        """
        if cmds.window('dpRenamerWin', exists=True):
            cmds.deleteUI('dpRenamerWin', window=True)
    
    
    def renamerUI(self, *args):
        """ UI (window).
        """
        self.closeRenamerUI()
        # UI:
        renamerWidth = 530
        renamerHeight = 280
        dpRenamerWin = cmds.window('dpRenamerWin', title=self.dpUIinst.lang['m214_renamer']+' - v'+str(DP_RENAMER_VERSION), width=renamerWidth, height=renamerHeight, sizeable=False, minimizeButton=False, maximizeButton=False)
        # UI elements:
        mainLayout = cmds.rowColumnLayout('mainLayout', numberOfColumns=2, columnWidth=[(1, 200), (2, 200)], columnSpacing=[(1, 10), (2, 10)])
        # fields
        fieldsLayout = cmds.columnLayout('fieldsLayout', adjustableColumn=True, width=150, parent=mainLayout)
        self.selectRB = cmds.radioButtonGrp('selectRB', labelArray2=[self.dpUIinst.lang["i266_selected"], self.dpUIinst.lang["m216_hierarchy"]], numberOfRadioButtons=2, select=self.selOption, changeCommand=self.changeSelOption, parent=fieldsLayout)
        cmds.separator(style="in", height=20, parent=fieldsLayout)
        self.sequenceCB = cmds.checkBox('sequenceCB', label=self.dpUIinst.lang['m220_sequence'], changeCommand=self.sequenceCBChange, value=False, parent=fieldsLayout)
        self.sequenceTFG = cmds.textFieldGrp('sequenceTFG', label=self.dpUIinst.lang['m222_name'], textChangedCommand=self.nameChange, columnAlign=[(1, "right"), (2, "right")], columnWidth=[(1, 30), (2, 100)], adjustableColumn2=True, parent=fieldsLayout)
        self.startIFG = cmds.intFieldGrp('startIFG', label=self.dpUIinst.lang['c110_start'], changeCommand=self.refreshPreview, value1=self.start, columnAlign=[(1, "right"), (2, "right")], columnWidth=[(1, 30), (2, 100)], adjustableColumn2=True, parent=fieldsLayout)
        self.paddingIFG = cmds.intFieldGrp('paddingIFG', label=self.dpUIinst.lang['m221_padding'], changeCommand=self.refreshPreview, value1=self.padding, columnAlign=[(1, "right"), (2, "right")], columnWidth=[(1, 30), (2, 100)], adjustableColumn2=True, parent=fieldsLayout)
        cmds.separator(style="in", height=20, parent=fieldsLayout)
        prePosLayout = cmds.rowColumnLayout('prePosLayout', numberOfColumns=2, columnWidth=[(1, 90), (2, 97)], columnSpacing=[(2, 5)], parent=fieldsLayout)
        self.prefixCB = cmds.checkBox('prefixCB', label=self.dpUIinst.lang['i144_prefix'], changeCommand=self.refreshPreview, value=False, parent=prePosLayout)
        self.suffixCB = cmds.checkBox('suffixCB', label=self.dpUIinst.lang['m217_suffix'], changeCommand=self.refreshPreview, value=False, parent=prePosLayout)
        self.prefixTF = cmds.textField('prefixTF', textChangedCommand=self.prefixChange, parent=prePosLayout)
        self.suffixTF = cmds.textField('suffixTF', textChangedCommand=self.suffixChange, parent=prePosLayout)
        cmds.separator(style="in", height=20, parent=fieldsLayout)
        self.searchReplaceCB = cmds.checkBox('searchReplaceCB', label=self.dpUIinst.lang['m218_search']+" - "+self.dpUIinst.lang['m219_replace'], changeCommand=self.searchReplaceCBChange, value=False, parent=fieldsLayout)
        self.searchTFG = cmds.textFieldGrp('searchTFG', label=self.dpUIinst.lang['i036_from'], textChangedCommand=self.searchChange, columnAlign=[(1, "right"), (2, "right")], columnWidth=[(1, 30), (2, 136)], adjustableColumn2=True, parent=fieldsLayout)
        self.replaceTFG = cmds.textFieldGrp('replaceTFG', label=self.dpUIinst.lang['i037_to'], textChangedCommand=self.searchChange, columnAlign=[(1, "right"), (2, "right")], columnWidth=[(1, 30), (2, 136)], adjustableColumn2=True, parent=fieldsLayout)
        # loaded items
        itemsLayout = cmds.columnLayout('itemsLayout', adjustableColumn=True, width=300, parent=mainLayout)
        cmds.text(label=self.dpUIinst.lang['m223_preview'], align="center", height=20, font="boldLabelFont", parent=itemsLayout)
        scrollsLayout = cmds.rowColumnLayout('scrollsLayout', numberOfColumns=2, columnWidth=[(1, 140), (2, 140)], columnSpacing=[(1, 5), (2, 5)], columnAlign=[(1, "center"), (2, "center")], rowSpacing=[(1, 5), (2, 5)], parent=itemsLayout)
        cmds.text(label=self.dpUIinst.lang['i276_current'], parent=scrollsLayout)
        cmds.text(label=self.dpUIinst.lang['m224_rename']+" "+self.dpUIinst.lang['i037_to'], parent=scrollsLayout)
        self.originalSL = cmds.textScrollList('selectedSL', width=130, height=193, enable=True, parent=scrollsLayout)
        self.previewSL = cmds.textScrollList('previewSL', width=130, height=193, enable=True, parent=scrollsLayout)
        # footer
        footerLayout = cmds.columnLayout('footerLayout', adjustableColumn=True, width=100, parent=itemsLayout)
        cmds.separator(style="none", height=5, parent=footerLayout)
        cmds.button('runRenamerBT', label=self.dpUIinst.lang['m224_rename'], command=self.runRenamerByUI, parent=footerLayout)
        # calling UI:
        cmds.showWindow(dpRenamerWin)


    def setSequenceFieldsEnable(self, value, *args):
        """
        """
        cmds.textFieldGrp(self.sequenceTFG, edit=True, enable=value)
        cmds.intFieldGrp(self.startIFG, edit=True, enable=value)
        cmds.intFieldGrp(self.paddingIFG, edit=True, enable=value)   


    def setSearchReplaceFieldsEnable(self, value, *args):
        """
        """
        cmds.textFieldGrp(self.searchTFG, edit=True, enable=value)
        cmds.textFieldGrp(self.replaceTFG, edit=True, enable=value)


    def sequenceCBChange(self, value, *args):
        """ Active or desactive the search and replace field because it doesn't work well with sequence field.
        """
        if value:
            cmds.checkBox(self.searchReplaceCB, edit=True, value=False)
            self.setSearchReplaceFieldsEnable(False)
            self.setSequenceFieldsEnable(True)
        else:
            self.setSearchReplaceFieldsEnable(True)
        self.refreshPreview()


    def searchReplaceCBChange(self, value, *args):
        """ Active or desactive the sequence field because it doesn't work well with search and replace field.
        """
        if value:
            cmds.checkBox(self.sequenceCB, edit=True, value=False)
            self.setSequenceFieldsEnable(False)
            self.setSearchReplaceFieldsEnable(True)
        else:
            self.setSequenceFieldsEnable(True)
        self.refreshPreview()


    def nameChange(self, value, *args):
        """ Set sequence checkbox on or off.
        """
        if value == "":
            cmds.checkBox(self.sequenceCB, edit=True, value=False)
            self.setSearchReplaceFieldsEnable(True)
        else:
            cmds.checkBox(self.sequenceCB, edit=True, value=True)
            cmds.checkBox(self.searchReplaceCB, edit=True, value=False)
            self.setSearchReplaceFieldsEnable(False)
        self.refreshPreview()


    def prefixChange(self, value, *args):
        """ Set prefix checkbox on or off.
        """
        if value == "":
            cmds.checkBox(self.prefixCB, edit=True, value=False)
        else:
            cmds.checkBox(self.prefixCB, edit=True, value=True)
        self.refreshPreview()


    def suffixChange(self, value, *args):
        """ Set suffix checkbox on or off.
        """
        if value == "":
            cmds.checkBox(self.suffixCB, edit=True, value=False)
        else:
            cmds.checkBox(self.suffixCB, edit=True, value=True)
        self.refreshPreview()


    def searchChange(self, value, *args):
        """ Set search checkbox on or off.
        """
        if value == "":
            if cmds.textFieldGrp(self.searchTFG, query=True, text=True) == "":
                cmds.checkBox(self.searchReplaceCB, edit=True, value=False)
                self.setSequenceFieldsEnable(True)
        else:
            cmds.checkBox(self.searchReplaceCB, edit=True, value=True)
            self.setSequenceFieldsEnable(False)
        self.refreshPreview()


    def changeSelOption(self, *args):
        """ Read the current UI selected radio button option.
            Update self.selOption queried value.
            Return the current value
        """
        self.selOption = cmds.radioButtonGrp(self.selectRB, query=True, select=True)
        self.refreshPreview()
        return self.selOption

    
    def refreshOriginal(self, *args):
        """ Refresh the original selected item list and update the UI textScrollList.
        """
        self.getObjList()
        if self.originalList:
            cmds.textScrollList(self.originalSL, edit=True, removeAll=True)
            cmds.textScrollList(self.originalSL, edit=True, append=self.originalList)


    def refreshPreview(self, *args):
        """ Reload the preview naming list and populate its UI textScrollList.
        """
        self.refreshOriginal()
        self.generatePreviewList(None)
        if self.previewList:
            cmds.textScrollList(self.previewSL, edit=True, removeAll=True)
            cmds.textScrollList(self.previewSL, edit=True, append=self.previewList)
    

    def getInfoFromUI(self, *args):
        """ Just load the member variables with info from UI.
        """
        # checkBoxes
        self.addSequence = cmds.checkBox(self.sequenceCB, query=True, value=True)
        self.addPrefix = cmds.checkBox(self.prefixCB, query=True, value=True)
        self.addSuffix = cmds.checkBox(self.suffixCB, query=True, value=True)
        self.searchReplace = cmds.checkBox(self.searchReplaceCB, query=True, value=True)
        # textFields
        self.sequenceName = cmds.textFieldGrp(self.sequenceTFG, query=True, text=True)
        self.prefixName = cmds.textField(self.prefixTF, query=True, text=True)
        self.suffixName = cmds.textField(self.suffixTF, query=True, text=True)
        self.searchName = cmds.textFieldGrp(self.searchTFG, query=True, text=True)
        self.replaceName = cmds.textFieldGrp(self.replaceTFG, query=True, text=True)
        # intFields
        self.start = cmds.intFieldGrp(self.startIFG, query=True, value1=True)
        self.padding = cmds.intFieldGrp(self.paddingIFG, query=True, value1=True)
        
    
    def generatePreviewList(self, *args):
        """ Generate a renamed preview list used to rename the original listed items.
        """
        self.getObjList()
        if self.originalList:
            self.previewList = []
            previewDic = {}
            # get UI info
            self.getInfoFromUI()
            for i, item in enumerate(self.originalList):
                if cmds.objExists(item):
                    # new:
                    newName = item
                    if "|" in item:
                        newName = item[item.rfind("|")+1:]
                    previewDic[item] = newName
                    # sequence
                    if self.addSequence:
                        previewDic[item] = self.sequenceName+str(self.start+i).zfill(self.padding)
                    # replace
                    if self.searchReplace:
                        if not self.searchName == "":
                            previewDic[item] = previewDic[item].replace(self.searchName, self.replaceName)
                    if self.addPrefix:
                        previewDic[item] = self.prefixName+previewDic[item]
                    if self.addSuffix:
                        previewDic[item] = previewDic[item]+self.suffixName
            if previewDic:
                for item in self.originalList:
                    self.previewList.append(previewDic[item])
    

    def getObjList(self, *args):
        """ Get the listed objects to rename them.
        """
        # list current selection
        self.originalList = cmds.ls(selection=True)
        if self.originalList:
            # check if need to add hierarchy children
            if self.selOption == 2: #Hierarchy
                for item in self.originalList:
                    try:
                        childrenList = cmds.listRelatives(item, allDescendents=True)
                        if childrenList:
                            for child in childrenList:
                                if not child in self.originalList:
                                    self.originalList.append(child)
                    except: #more than one object with the same name
                        mel.eval("warning \""+self.dpUIinst.lang['i075_moreOne']+' '+self.dpUIinst.lang['i076_sameName']+"\";")
        return self.originalList


    def runRenamerByUI(self, *args):
        """ Rename originalList from UI info.
        """
        self.getObjList()
        if self.originalList:
            self.generatePreviewList()
            if self.previewList:
                for i, item in enumerate(self.originalList):
                    if not cmds.objExists(item):
                        itemList = cmds.ls("*"+item+"*")
                        if itemList:
                            item = itemList[0]
                    if cmds.objExists(item):
                        cmds.rename(item, self.previewList[i])
                    else:
                        mel.eval("warning \""+self.dpUIinst.lang['v005_cantFix']+" "+item+"\";")
            self.resetUI()
            self.refreshPreview()
        else:
            mel.eval("warning \""+self.dpUIinst.lang['m225_selectAnything']+"\";")
            

    def resetUI(self, *args):
        """ Just back UI to default initial values.
        """
        if self.ui:
            cmds.radioButtonGrp(self.selectRB, edit=True, select=1)
            # checkBoxes
            cmds.checkBox(self.sequenceCB, edit=True, value=False)
            cmds.checkBox(self.prefixCB, edit=True, value=False)
            cmds.checkBox(self.suffixCB, edit=True, value=False)
            cmds.checkBox(self.searchReplaceCB, edit=True, value=False)
            # textFields
            cmds.textFieldGrp(self.sequenceTFG, edit=True, text="")
            cmds.textField(self.prefixTF, edit=True, text="")
            cmds.textField(self.suffixTF, edit=True, text="")
            cmds.textFieldGrp(self.searchTFG, edit=True, text="")
            cmds.textFieldGrp(self.replaceTFG, edit=True, text="")
            # intFields
            cmds.intFieldGrp(self.startIFG, edit=True, value1=self.start)
            cmds.intFieldGrp(self.paddingIFG, edit=True, value1=self.padding)
