# importing libraries:
from maya import cmds
from maya import mel

# global variables to this module:
CLASS_NAME = "Renamer"
TITLE = "m214_renamer"
DESCRIPTION = "m215_renamerDesc"
ICON = "/Icons/dp_renamer.png"

DPRENAMER_VERSION = "0.8"


class Renamer():
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, ui=True, *args, **kwargs):
        # defining variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.selOption = 1 #Selection
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
        # call main function
        if ui:
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
        dpRenamerWin = cmds.window('dpRenamerWin', title='Renamer - v'+DPRENAMER_VERSION, width=200, height=575, sizeable=True, minimizeButton=False, maximizeButton=False)
        # UI elements:
        mainLayout  = cmds.formLayout('mainLayout', numberOfDivisions=450, parent=dpRenamerWin)

        fieldsLayout = cmds.columnLayout('fieldsLayout', adjustableColumn=True, width=150, parent=mainLayout)
        self.selectRB = cmds.radioButtonGrp('selectRB', labelArray2=[self.langDic[self.langName]["i266_selected"], self.langDic[self.langName]["m216_hierarchy"]], numberOfRadioButtons=2, select=self.selOption, changeCommand=self.changeSelOption, parent=fieldsLayout)
        cmds.text('dpRenamer - WIP')
        
        self.sequenceCB = cmds.checkBox('sequenceCB', label=self.langDic[self.langName]['m220_sequence'], changeCommand=self.refreshPreview, value=False)
        self.sequenceTFG = cmds.textFieldGrp('sequenceTFG', label=self.langDic[self.langName]['m222_name'], changeCommand=self.refreshPreview, text="")
        self.startIFG = cmds.intFieldGrp('startIFG', label=self.langDic[self.langName]['c110_start'], changeCommand=self.refreshPreview, value1=self.start)
        self.paddingIFG = cmds.intFieldGrp('paddingIFG', label=self.langDic[self.langName]['m221_padding'], changeCommand=self.refreshPreview, value1=self.padding)

        cmds.text(label="")
        self.prefixCB = cmds.checkBox('prefixCB', label=self.langDic[self.langName]['i144_prefix'], changeCommand=self.refreshPreview, value=False)
        self.prefixTF = cmds.textField('prefixTF', changeCommand=self.refreshPreview, text="")
        
        cmds.text(label="")
        self.suffixCB = cmds.checkBox('suffixCB', label=self.langDic[self.langName]['m217_suffix'], changeCommand=self.refreshPreview, value=False)
        self.suffixTF = cmds.textField('suffixTF', changeCommand=self.refreshPreview, text="")

        cmds.text(label="")
        self.searchReplaceCB = cmds.checkBox('searchReplaceCB', label=self.langDic[self.langName]['m218_search']+" - "+self.langDic[self.langName]['m219_replace'], changeCommand=self.refreshPreview, value=False)
        self.searchTF = cmds.textField('searchTF', changeCommand=self.refreshPreview, text="")
        self.replaceTF = cmds.textField('replaceTF', changeCommand=self.refreshPreview, text="")
        
        selectedLayout = cmds.columnLayout('selectedLayout', adjustableColumn=True, width=190, parent=mainLayout)
        cmds.text(label="hello", parent=selectedLayout)
        self.originalSL = cmds.textScrollList('selectedSL', width=150, enable=True, parent=selectedLayout)
        cmds.text(label="merci", parent=selectedLayout)

        previewLayout = cmds.columnLayout('previewLayout', adjustableColumn=True, width=200, parent=mainLayout)
        cmds.text(label="PREVIEW")
        self.previewSL = cmds.textScrollList('previewSL', width=250, enable=True, parent=previewLayout)

        footerLayout = cmds.columnLayout('footerLayout', adjustableColumn=True, width=100, parent=mainLayout)
        cmds.button('runRenamerBT', label="Run Carreto Run!", command=self.runRenamerByUI, parent=footerLayout)

        # edit formLayout in order to get a good scalable window:
        cmds.formLayout(mainLayout, edit=True,
                        attachForm=[(fieldsLayout, 'top', 5), (fieldsLayout, 'left', 5), (selectedLayout, 'top', 5), (previewLayout, 'right', 5), (footerLayout, 'left', 5), (footerLayout, 'bottom', 5), (footerLayout, 'right', 5), (previewLayout, 'right', 5)],
                        attachControl=[(selectedLayout, 'left', 5, fieldsLayout), (selectedLayout, 'bottom', 5, footerLayout), (footerLayout, 'left', 5, fieldsLayout)],
                        attachPosition=[(fieldsLayout, 'right', 5, 150)],
                        attachNone=[(footerLayout, 'top')]
                        )
        # calling UI:
        cmds.showWindow(dpRenamerWin)


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
        self.searchName = cmds.textField(self.searchTF, query=True, text=True)
        self.replaceName = cmds.textField(self.replaceTF, query=True, text=True)
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
                        print("More than one same name here errorr....")
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
                        mel.eval('warning \"Not able to rename:\"'+item+';')
            self.refreshPreview()
        else:
            mel.eval("warning \"Need to select anything to run.\";")
            

# TODO
#
# need to organize layout
# need to translate phrases
# setup scroll layouts
# what to do with item selection in scroll layouts
# or just not enable selection in scroll layouts?
#
#