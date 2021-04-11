# importing libraries:
import maya.cmds as cmds
from functools import partial
from ..Modules.Library import dpControls

# global variables to this module:
CLASS_NAME = "Renamer"
TITLE = "m178_renamer"
DESCRIPTION = "m179_renamerDesc"
ICON = "/Icons/dp_renamer.png"

DPRENAMER_VERSION = "0.5"


class Renamer():
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, ui=True, *args, **kwargs):
        # defining variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
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
        self.selectRB = cmds.radioButtonGrp('selectRB', labelArray2=[self.langDic[self.langName]["m180_selected"], self.langDic[self.langName]["m181_hierarchy"]], numberOfRadioButtons=2, select=self.selOption, changeCommand=self.changeSelOption, parent=fieldsLayout)
        cmds.text('dpRenamer - WIP')
        cmds.button('getInfoFromUI', label="getInfoFromUI", command=self.getInfoFromUI)#self.langDic[self.langName]['i124_copyPasteAttr']"", command=partial(self.ctrls.copyAndPasteAttr, True), backgroundColor=(0.7, 0.9, 1.0), parent=mainLayout)
        
        self.sequenceCB = cmds.checkBox('sequenceCB', label=self.langDic[self.langName]['m185_sequence'], value=False)
        self.sequenceTFG = cmds.textFieldGrp('sequenceTFG', label=self.langDic[self.langName]['m187_name'], text="")
        self.startIFG = cmds.intFieldGrp('startIFG', label=self.langDic[self.langName]['c110_start'], value1=self.start)
        self.paddingIFG = cmds.intFieldGrp('paddingIFG', label=self.langDic[self.langName]['m186_padding'], value1=self.padding)
        cmds.button('sequenceBT', label=self.langDic[self.langName]['m185_sequence'], command=partial(self.runRenamer, self.originalList, True, False, False, False), backgroundColor=(1.0, 0.4, 0.2), parent=fieldsLayout)

        cmds.text(label="")
        self.prefixCB = cmds.checkBox('prefixCB', label=self.langDic[self.langName]['i144_prefix'], value=False)
        self.prefixTF = cmds.textField('prefixTF', text="")
        cmds.button('prefixBT', label=self.langDic[self.langName]['i144_prefix'], command=partial(self.runRenamer, self.originalList, False, True, False, False), backgroundColor=(0.7, 0.9, 1.0), parent=fieldsLayout)
        
        cmds.text(label="")
        self.suffixCB = cmds.checkBox('suffixCB', label=self.langDic[self.langName]['m182_suffix'], value=False)
        self.suffixTF = cmds.textField('suffixTF', text="")
        cmds.button('suffixBT', label=self.langDic[self.langName]['m182_suffix'], command=partial(self.runRenamer, self.originalList, False, False, True, False), backgroundColor=(0.9, 0.9, 0.7), parent=fieldsLayout)
        
        cmds.text(label="")
        self.searchReplaceCB = cmds.checkBox('searchReplaceCB', label=self.langDic[self.langName]['m183_search']+" - "+self.langDic[self.langName]['m184_replace'], value=False)
        self.searchTF = cmds.textField('searchTF', text="")
        self.replaceTF = cmds.textField('replaceTF', text="")
        cmds.button('replaceBT', label=self.langDic[self.langName]['m184_replace'], command=partial(self.runRenamer, self.originalList, False, False, False, True), backgroundColor=(0.9, 1.0, 0.5), parent=fieldsLayout)
        
        cmds.text(label="")
        cmds.text(label="----")
        cmds.button('refreshOriginalBT', label="Refresh Original", command=self.refreshOriginal, backgroundColor=(0.7, 0.7, 0.9), parent=fieldsLayout)
        cmds.button('refreshPreviewBT', label="Refresh Preview", command=self.refreshPreview, backgroundColor=(0.9, 1.0, 0.7), parent=fieldsLayout)

        selectedLayout = cmds.columnLayout('selectedLayout', adjustableColumn=True, width=190, parent=mainLayout)
        cmds.text(label="hello", parent=selectedLayout)
        self.originalSL = cmds.textScrollList('selectedSL', width=150, enable=True, parent=selectedLayout)
        cmds.text(label="merci", parent=selectedLayout)

        previewLayout = cmds.columnLayout('previewLayout', adjustableColumn=True, width=100, parent=mainLayout)
        self.previewSL = cmds.textScrollList('previewSL', width=150, enable=True, parent=previewLayout)

        footerLayout = cmds.columnLayout('footerLayout', adjustableColumn=True, width=100, parent=mainLayout)
        cmds.button('runRenamerBT', label="Run Forest Run!", command=self.runRenamer, parent=footerLayout)

        # edit formLayout in order to get a good scalable window:
        cmds.formLayout(mainLayout, edit=True,
                        attachForm=[(fieldsLayout, 'top', 5), (fieldsLayout, 'left', 5), (selectedLayout, 'top', 5), (previewLayout, 'right', 5), (footerLayout, 'left', 5), (footerLayout, 'bottom', 5), (footerLayout, 'right', 5), (previewLayout, 'right', 5)],
                        attachControl=[(selectedLayout, 'left', 5, fieldsLayout), (selectedLayout, 'bottom', 5, footerLayout), (footerLayout, 'left', 5, fieldsLayout)],
                        attachPosition=[(fieldsLayout, 'right', 5, 150)],
                        attachNone=[(footerLayout, 'top')]
                        )



        self.refreshOriginal()
        self.refreshPreview()

        # calling UI:
        cmds.showWindow(dpRenamerWin)


    

    def changeSelOption(self, *args):
        """ Read the current UI selected radio button option.
            Update self.selOption queried value.
            Return the current value
        """
        self.selOption = cmds.radioButtonGrp(self.selectRB, query=True, select=True)
        return self.selOption



# WIP:
    def testeWip(self, addPrefix, *args):
        print "teste wip"
    
    def selectSource(self, *args):
        print "selected soucr in sl"

    
    def refreshOriginal(self, *args):
        self.getObjList()
        if self.originalList:
            cmds.textScrollList(self.originalSL, edit=True, removeAll=True)
            cmds.textScrollList(self.originalSL, edit=True, append=self.originalList)


    def refreshPreview(self, *args):
        self.generatePreviewList(None)
        if self.previewList:
            cmds.textScrollList(self.previewSL, edit=True, removeAll=True)
            cmds.textScrollList(self.previewSL, edit=True, append=self.previewList)
    

    def getInfoFromUI(self, *args):
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
        self.getObjList()
        if self.originalList:
            self.previewList = []
            previewDic = {}
            # get UI info
            self.getInfoFromUI()
            for i, item in enumerate(self.originalList):
                if cmds.objExists(item):
                    previewDic[item] = item
                    if self.addSequence:
                        previewDic[item] = self.sequenceName+str(self.start+i).zfill(self.padding)

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
        # list current selection
        self.originalList = cmds.ls(selection=True)
        if self.originalList:
            # check if need to add hierarchy children
            if self.selOption == 2: #Hierarchy
                for item in self.originalList:
                    childrenList = cmds.listRelatives(item, allDescendents=True)
                    if childrenList:
                        for child in childrenList:
                            self.originalList.append(child)
        return self.originalList


    def runRenamer(self, objList, doSequence, doPrefix, doSuffix, doReplace, *args):
        if not objList:
            self.getObjList()
            
        if self.originalList:
            self.generatePreviewList(doSequence, doPrefix, doSuffix, doReplace)
            if self.previewList:
                for i, item in enumerate(self.originalList):
                    cmds.rename(item, self.previewList[i])
            
            
        else:
            mel.eval("warning \"Need to select anything to run.\";")
            
