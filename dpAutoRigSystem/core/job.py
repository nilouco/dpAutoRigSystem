#import libraries
from maya import cmds
from functools import partial



class Job(object):
    def __init__(self, ar):
        self.ar = ar


    def start_jobs(self):
        #
        # TODO: test all script jobs
        #
        
        """ Create scriptJobs to read:
            - NewSceneOpened
            - SceneSaved
            - deleteAll = new scene (disable to don't reset the asset context when running a new scene for the first module)
            - SelectionChanged
            - WorkspaceChanged = not documented
        """
        
        print("WIP = starting script jobs...")

        cmds.scriptJob(uiDeleted=('dpAutoRigSystemWC', partial(self.ar.ui_manager.set_ui_state, False)))
        cmds.scriptJob(event=('SceneOpened', partial(self.ar.ui_manager.refresh_ui, clearSel=True)), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
        #cmds.scriptJob(event=('deleteAll', self.ar.ui_manager.refresh_ui), parent='dpAutoRigSystemWC', replacePrevious=True, killWithScene=False, compressUndo=False, force=True)
        cmds.scriptJob(event=('NewSceneOpened', self.ar.ui_manager.refresh_ui), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
        cmds.scriptJob(event=('SceneSaved', partial(self.ar.ui_manager.refresh_ui, savedScene=True, resetButtons=False)), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
        cmds.scriptJob(event=('workspaceChanged', self.ar.pipeliner.refreshAssetData), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
        self.ar.data.select_change_job_id = cmds.scriptJob(event=('SelectionChanged', self.selected_guide), parent='language_menu', replacePrevious=True, killWithScene=False, compressUndo=True, force=True)
        self.ar.ctrls.startCorrectiveEditMode()
        self.selected_guide()


    def selected_guide(self):
        """ This scriptJob read if the selected item in the scene is a guideModule and reload the UI.
        """
        # run the UI part:
        self.selectedModuleInstanceList = []
        selectedGuideNodeList = []
        selectedList = []
        # get selected items:
        selectedList = cmds.ls(selection=True, long=True)
        if selectedList:
            updatedGuideNodeList = []
            needUpdateSelect = False
            for selectedItem in selectedList:
                if cmds.objExists(selectedItem+"."+self.ar.data.guide_base_attr) and cmds.getAttr(selectedItem+"."+self.ar.data.guide_base_attr) == 1:
                    if not ":" in selectedItem[selectedItem.rfind("|"):]:
                        newGuide = self.ar.maker.setup_duplicated_guide(selectedItem)
                        updatedGuideNodeList.append(newGuide)
                        needUpdateSelect = True
                    else:
                        selectedGuideNodeList.append(selectedItem)
            if needUpdateSelect:
                self.ar.ui_manager.refresh_ui()
                cmds.select(updatedGuideNodeList)
        # update UI
        for m, moduleInstance in enumerate(self.ar.data.standard_instances):
            if cmds.objExists(moduleInstance.moduleGrp):
                if moduleInstance.selectButton:
                    currentColorList = self.ar.ctrls.getGuideRGBColorList(moduleInstance)
                    if currentColorList:
                        cmds.button(moduleInstance.selectButton, edit=True, label=" ", backgroundColor=currentColorList)
                    if selectedGuideNodeList:
                        for selectedGuide in selectedGuideNodeList:
                            selectedGuideInfo = cmds.getAttr(selectedGuide+"."+self.ar.data.module_instance_info_attr)
                            if selectedGuideInfo == str(moduleInstance):
                                cmds.button(moduleInstance.selectButton, edit=True, label="S", backgroundColor=(1.0, 1.0, 1.0))
                                self.selectedModuleInstanceList.append(moduleInstance)
        # delete module layout:
        if not selectedGuideNodeList:
            try:
                cmds.frameLayout("rig_edit_selected_module_fl", edit=True, label=self.ar.data.lang['i011_editSelected']+" "+self.ar.data.lang['i143_module'])
                cmds.deleteUI("rig_selected_module_cl")
            except:
                pass
        # re-create module layout:
        if self.selectedModuleInstanceList:
            self.selectedModuleInstanceList[-1].reCreateEditSelectedModuleLayout(bSelect=False)
        # call reload the geometries in skin UI:
        self.ar.filler.populate_geometries()

