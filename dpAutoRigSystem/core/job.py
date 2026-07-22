#import libraries
from maya import cmds
from functools import partial



class Job(object):
    def __init__(self, ar):
        self.ar = ar


    def garbage_collector(self):
        self.delete_old_job("dpAutoRigSystem")


    def delete_old_job(self, item, *args):
        """ Try to find an existing script job already running for this item name and kill it.
        """
        for job in cmds.scriptJob(listJobs=True):
            if item in job:
                cmds.scriptJob(kill=int(job[:job.find(":")]), force=True)


    def start_jobs(self):
        """ Create scriptJobs to read:
            - uiDeleted
            - SceneOpened
            - deleteAll = new scene
            - SceneSaved
            - SelectionChanged
            - WorkspaceChanged = not documented
        """
        cmds.scriptJob(uiDeleted=('dpAutoRigSystemWC', partial(self.ar.ui_manager.set_ui_state, False)))
        cmds.scriptJob(event=('SceneOpened', partial(self.ar.ui_manager.refresh_ui, clearSel=True)), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
        cmds.scriptJob(event=('deleteAll', self.ar.ui_manager.refresh_ui), parent='dpAutoRigSystemWC', replacePrevious=True, killWithScene=False, compressUndo=False, force=True)
        #cmds.scriptJob(event=('NewSceneOpened', self.ar.ui_manager.refresh_ui), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
        cmds.scriptJob(event=('SceneSaved', partial(self.ar.ui_manager.refresh_ui, savedScene=True, resetButtons=False)), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
        cmds.scriptJob(event=('workspaceChanged', self.ar.pipeliner.refreshAssetData), parent='dpAutoRigSystemWC', killWithScene=False, compressUndo=True)
        self.start_corrective_edit_mode()
        self.selection_change()
        self.selected_guide()


    def selection_change(self):
        try:
            old_job_id = self.ar.data.select_change_job_id
            self.ar.data.select_change_job_id = cmds.scriptJob(event=('SelectionChanged', self.selected_guide), parent='main_menu_bar', replacePrevious=True, killWithScene=False, compressUndo=True)
            if not old_job_id == 0:
                if cmds.scriptJob(exists=old_job_id):
                    cmds.scriptJob(kill=old_job_id, force=True)
        except: #due duplicate guides
            self.ar.data.select_change_job_id = cmds.scriptJob(event=('SelectionChanged', self.selected_guide), parent='main_menu_bar', replacePrevious=False, killWithScene=False, compressUndo=True)


    def selected_guide(self):
        """ This scriptJob read if the selected item in the scene is a guideModule and reload the UI.
        """
        self.selected_instances = []
        selected_guides = []
        selected_nodes = []
        # get selected items:
        selected_nodes = cmds.ls(selection=True, long=True)
        if selected_nodes:
            updated_guide_nodes = []
            need_update_select = False
            for selected_item in selected_nodes:
                if self.ar.data.guide_base_attr in cmds.listAttr(selected_item) and cmds.getAttr(selected_item+"."+self.ar.data.guide_base_attr) == 1:
                    if not ":" in selected_item[selected_item.rfind("|"):]:
                        updated_guide_nodes.append(self.ar.maker.setup_duplicated_guide(selected_item))
                        need_update_select = True
                    else:
                        selected_guides.append(selected_item)
            if need_update_select:
                self.ar.ui_manager.refresh_ui()
                cmds.select(updated_guide_nodes)
        # update UI
        for m, module_instance in enumerate(self.ar.data.guide_instances):
            if cmds.objExists(module_instance.guide_base):
                if module_instance.selectButton:
                    current_colors = self.ar.ctrls.getGuideRGBColorList(module_instance)
                    if current_colors:
                        cmds.button(module_instance.selectButton, edit=True, label=" ", backgroundColor=current_colors)
                    if selected_guides:
                        for selected_guide in selected_guides:
                            if str(module_instance) == cmds.getAttr(selected_guide+"."+self.ar.data.module_instance_info_attr):
                                cmds.button(module_instance.selectButton, edit=True, label="S", backgroundColor=(1.0, 1.0, 1.0))
                                self.selected_instances.append(module_instance)
        # delete module layout:
        if not selected_guides:
            if self.ar.data.ui_state:
                if cmds.frameLayout("rig_edit_selected_module_fl", query=True, exists=True):
                    cmds.frameLayout("rig_edit_selected_module_fl", edit=True, label=self.ar.data.lang['i011_editSelected']+" "+self.ar.data.lang['i143_module'])
                if cmds.columnLayout("rig_selected_module_cl", query=True, exists=True):
                    cmds.deleteUI("rig_selected_module_cl")
        # re-create module layout:
        if self.selected_instances:
            self.selected_instances[-1].reCreateEditSelectedModuleLayout(bSelect=False)
        # call reload the geometries in skin UI:
        self.ar.filler.populate_geometries()


    def create_corrective_edit_mode(self, item):
        """ Create a scriptJob to read this attribute change.
        """
        self.delete_old_job(item)
        cmds.scriptJob(attributeChange=[str(item+".editMode"), lambda node=item: self.corrective_edit_mode(node)], killWithScene=False, compressUndo=True)
        if cmds.getAttr(item+".editMode"):
            self.ar.ctrls.colorShape([item], 'bonina', rgb=True)


    def corrective_edit_mode(self, item):
        """ Edit mode to corrective control by scriptJob.
        """
        if "editMode" in cmds.listAttr(item):
            if cmds.getAttr(item+".editMode"):
                self.ar.ctrls.colorShape([item], 'bonina', rgb=True)
            else:
                shapes = cmds.listRelatives(item, shapes=True, children=True, fullPath=True)
                if shapes:
                    for shape in shapes:
                        cmds.setAttr(shape+".overrideRGBColors", 0)
                self.set_corrective_calibration(item)


    def start_corrective_edit_mode(self, items=None):
        """ Reload editMode job for existing corrective controllers.
        """
        if not items:
            items = cmds.ls(selection=False, type="transform")
        if items:
            for item in items:
                if "editMode" in cmds.listAttr(item):
                    self.create_corrective_edit_mode(item)


    def set_corrective_calibration(self, item):
        """ Remove corrective controller editMode setup.
            Calculate the results of transformations to set the calibration attributes.
        """
        if cmds.objExists(item):
            duplicated_temp = cmds.duplicate(item, name=item+"_TEMP")[0]
            cmds.parent(duplicated_temp, item+"_Zero_1_Grp")
            for attr in ["T", "R", "S"]:
                for axis in ["X", "Y", "Z"]:
                    new_value = cmds.getAttr(duplicated_temp+"."+attr.lower()+axis.lower())
                    if attr == "S":
                        cmds.setAttr(item+"."+attr.lower()+axis.lower(), 1) #scale
                    else:
                        cmds.setAttr(item+"."+attr.lower()+axis.lower(), 0) #translate, rotate
                    cmds.setAttr(item+".calibrate"+attr+axis, new_value)
            cmds.delete(duplicated_temp)
            cmds.select(item)


    def create_pin_guide(self, item):
        """ Add pinGuide attribute if it doesn't exist yet.
            Create a scriptJob to read this attribute change.
        """
        if not item.endswith("_JointEnd"):
            if not item.endswith("_RadiusCtrl"):
                if not "pinGuide" in cmds.listAttr(item):
                    cmds.addAttr(item, longName="pinGuide", attributeType="bool")
                    cmds.setAttr(item+".pinGuide", channelBox=True)
                    cmds.addAttr(item, longName="pinGuideConstraint", attributeType="message")
                    cmds.addAttr(item, longName="lockedList", dataType="string")
                self.delete_old_job(item)
                cmds.scriptJob(attributeChange=[str(item+".pinGuide"), lambda node=item: self.pin_guide(node)], killWithScene=False, compressUndo=True)
                self.pin_guide(item) # just forcing pinGuide setup run before wait for the job be trigger by the attribute


    def set_pinned_guide_color(self, item, status, color="red"):
        """ Set the color override for pinned guide shapes.
        """
        cmds.setAttr(item+".overrideEnabled", status)
        cmds.setAttr(item+".overrideColor", self.ar.ctrls.dic_colors[color])
        shapes = cmds.listRelatives(item, children=True, fullPath=False, shapes=True)
        if shapes:
            for shape in shapes:
                if status:
                    cmds.setAttr(shape+".overrideEnabled", 0)
                else:
                    cmds.setAttr(shape+".overrideEnabled", 1)


    def pin_guide(self, item):
        """ Pin temporally the guide by scriptJob.
        """
        if "pinGuide" in cmds.listAttr(item):
            # extracting namespace... need to find an ellegant way using message or stored attribute instead:
            namespace_name = None
            cmds.namespace(set=":")
            if ":" in item:
                if "|" in item:
                    namespace_name = item[item.rfind("|")+1:item.rfind(":")]
                else:
                    namespace_name = item[:item.rfind(":")]
            # work with locked attributes
            pin_value = cmds.getAttr(item+".pinGuide")
            pac = item+"_PinGuide_PaC"
            if pin_value:
                if cmds.objExists(self.ar.data.temp_grp):
                    if not cmds.listConnections(item+".pinGuideConstraint", destination=False, source=True):
                        self.store_lockeds(item)
                        if namespace_name:
                            cmds.namespace(set=namespace_name)
                        for attr in self.ar.data.transform_attrs:
                            cmds.setAttr(item+"."+attr, lock=False)
                        pc = cmds.parentConstraint(self.ar.data.temp_grp, item, maintainOffset=True, name=pac)[0]
                        cmds.connectAttr(pc+".message", item+".pinGuideConstraint")
                        for attr in self.ar.data.transform_attrs:
                            cmds.setAttr(item+"."+attr, lock=True)
                        if "worldSize" in cmds.listAttr(item):
                            cmds.setAttr(item+".worldSize", lock=True)
            else:
                pacs = cmds.listConnections(item+".pinGuideConstraint", destination=False, source=True)
                if pacs:
                    cmds.delete(pacs[0])
                    for attr in self.ar.data.transform_attrs:
                        cmds.setAttr(item+"."+attr, lock=False)
                    self.restore_lockeds(item)
                    if "worldSize" in cmds.listAttr(item):
                        cmds.setAttr(item+".worldSize", lock=False)
            self.set_pinned_guide_color(item, pin_value)
            cmds.namespace(set=":")


    def start_pin_guide(self, item):
        """ Reload pinGuide job for already created guide.
        """
        if cmds.objExists(item):
            children = cmds.listRelatives(item, children=True, allDescendents=True, fullPath=True, type="transform")
            if children:
                for child in children:
                    if "pinGuide" in cmds.listAttr(child):
                        self.create_pin_guide(child)
            if "pinGuide" in cmds.listAttr(item):
                self.create_pin_guide(item)


    def unpin_guide(self, items=None, force=False):
        """ Remove pinGuide setup.
            We expect to have the scriptJob running here to clean-up the pin setup, or just force it to run.
        """
        if not items:
            items = [guide for guide in cmds.ls(selection=False, type="transform") if "pinGuide" in cmds.listAttr(guide)]
        if items:
            for guide in items:
                cmds.setAttr(guide+".pinGuide", 0)
                if force:
                    self.pin_guide(guide)


    def store_lockeds(self, item):
        """ Store a string of a list of found locked attributes.
        """
        locked_attr = ""
        if not "lockedList" in cmds.listAttr(item):
            cmds.addAttr(item, longName="lockedList", dataType="string")
        locked_attrs = cmds.listAttr(item, locked=True)
        if locked_attrs:
            locked_attr = ';'.join(str(e) for e in locked_attrs)
        cmds.setAttr(item+".lockedList", locked_attr, type="string")


    def restore_lockeds(self, item):
        """ Lock again the stored attributes.
        """
        if "lockedList" in cmds.listAttr(item):
            locked_attr = cmds.getAttr(item+".lockedList")
            if locked_attr:
                locked_attrs = locked_attr.split(";")
                if locked_attrs:
                    for attr in locked_attrs:
                        cmds.setAttr(item+"."+attr, lock=True)


    def refresh_preview_win(self, func, win):
        cmds.scriptJob(event=('SelectionChanged', func), parent=win, replacePrevious=True, killWithScene=True, compressUndo=True, force=True)
