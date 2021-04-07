# importing libraries:
import maya.cmds as cmds
from functools import partial
from ..Modules.Library import dpControls

# global variables to this module:
CLASS_NAME = "Renamer"
TITLE = "m178_renamer"
DESCRIPTION = "m179_renamerDesc"
ICON = "/Icons/dp_renamer.png"

DPRENAMER_VERSION = "0.3"


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
        self.objList, self.previewList = [], []
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
        cmds.button('testButton', label="testButton", command=self.testeWip)#self.langDic[self.langName]['i124_copyPasteAttr']"", command=partial(self.ctrls.copyAndPasteAttr, True), backgroundColor=(0.7, 0.9, 1.0), parent=mainLayout)
        self.prefixTF = cmds.textField('prefixTF', text="")
        cmds.button('prefixBT', label=self.langDic[self.langName]['i144_prefix'], command=partial(self.runRenamer, self.objList, True, False), backgroundColor=(0.7, 0.9, 1.0), parent=fieldsLayout)
        self.suffixTF = cmds.textField('suffixTF', text="")
        cmds.button('suffixBT', label=self.langDic[self.langName]['m182_suffix'], command=partial(self.runRenamer, self.objList, False, True), backgroundColor=(0.9, 0.9, 0.7), parent=fieldsLayout)
        cmds.button('refreshPreviewBT', label="Refresh Preview", command=self.refreshPreview, backgroundColor=(0.9, 1.0, 0.7), parent=fieldsLayout)

        #selectedLayout = cmds.columnLayout('selectedLayout', adjustableColumn=True, width=190, parent=mainLayout)
        self.selectedSL = cmds.textScrollList('selectedSL', width=150, enable=False, parent=mainLayout)

        #previewLayout = cmds.columnLayout('previewLayout', adjustableColumn=True, width=100, parent=mainLayout)
        self.previewSL = cmds.textScrollList('previewSL', width=150, enable=False, parent=mainLayout)

        footerLayout = cmds.columnLayout('footerLayout', adjustableColumn=True, width=100, parent=mainLayout)
        cmds.button('runRenamerBT', label="Run Forest Run!", command=self.testeWip, parent=footerLayout)

        # edit formLayout in order to get a good scalable window:
        cmds.formLayout(mainLayout, edit=True,
                        attachForm=[(fieldsLayout, 'top', 5), (fieldsLayout, 'left', 5), (self.selectedSL, 'top', 5), (self.previewSL, 'right', 5), (footerLayout, 'left', 5), (footerLayout, 'bottom', 5), (footerLayout, 'right', 5), (self.previewSL, 'right', 5)],
                        attachControl=[(self.selectedSL, 'left', 5, fieldsLayout), (self.selectedSL, 'bottom', 5, footerLayout), (footerLayout, 'left', 5, fieldsLayout)],
                        attachPosition=[(fieldsLayout, 'right', 5, 150)],
                        attachNone=[(footerLayout, 'top')]
                        )



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

    def refreshPreview(self, *args):
        selList = cmds.ls(selection=True)
        if selList:
            cmds.textScrollList(self.selectedSL, edit=True, removeAll=True)
            cmds.textScrollList(self.selectedSL, edit=True, append=selList)


    def getObjList(self, *args):
        # list current selection
        self.objList = cmds.ls(selection=True)
        if self.objList:
            # check if need to add hierarchy children
            if self.selOption == 2: #Hierarchy
                for item in self.objList:
                    childrenList = cmds.listRelatives(item, allDescendents=True)
                    if childrenList:
                        for child in childrenList:
                            self.objList.append(child)


    def runRenamer(self, objList, addPrefix, addSuffix, *args):
        if not self.objList:
            self.getObjList()
            
        if self.objList:
            # get prefix name
            prefix = cmds.textField(self.prefixTF, query=True, text=True)
            for item in self.objList:
                if addPrefix:
                    if cmds.objExists(item):
                        cmds.rename(item, prefix+item)

            # get suffix name
            suffix = cmds.textField(self.suffixTF, query=True, text=True)
            for item in self.objList:
                if addSuffix:
                    if cmds.objExists(item):
                        cmds.rename(item, item+suffix)
        else:
            mel.eval("warning \"Need to select anything to run.\";")
            
