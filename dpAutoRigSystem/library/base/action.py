# importing libraries:
from maya import cmds
from maya import mel
from . import base
from functools import partial
import os
import getpass
import shutil
from importlib import reload

# global variables to this module:
DEFAULT_COLOR = (0.5, 0.5, 0.5)
CHECKED_COLOR = (0.7, 1.0, 0.7)
WARNING_COLOR = (1.0, 1.0, 0.5)
ISSUE_COLOR = (1.0, 0.65, 0.65)
RUNNING_COLOR = (1.0, 1.0, 1.0)


class BaseAction(base.BaseLibrary):
    def __init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI, verbose=True):
        """ Initialize the module class for validating and rebuilding.
        """
        # defining variables:
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        self.verbose = verbose
        self.active = True
        self.action_cb = None
        self.first_bt = None
        self.second_bt = None
        self.delete_data_itb = None
        self.action_type = "v000_validator" #or r000_rebuilder
        self.first_bt_enable = True
        self.second_bt_enable = True
        self.delete_data_bt_enable = False
        self.first_bt_label = None
        self.second_bt_label = None
        self.first_bt_custom_label = None
        self.second_bt_custom_label = None
        self.io_folder = None
        self.maybe_done = False
        self.info_text = self.ar.data.lang['i305_none']
        self.constraint_types = ["parentConstraint", "pointConstraint", "orientConstraint", "scaleConstraint", "aimConstraint", "pointOnPolyConstraint", "geometryConstraint", "normalConstraint", "poleVectorConstraint", "tangentConstraint"]
        self.custom_name = ''
        # returned lists
        self.checked_items = []
        self.found_issues = []
        self.good_results = []
        self.messages = []
        self.log_data = {}
        # start action type
        self.set_action_type(self.action_type)


    def set_action_type(self, value):
        """ Define the button label texts.
        """
        self.action_type = value
        if self.action_type == "v000_validator":
            self.first_bt_label = self.ar.data.lang['i210_verify']
            self.second_bt_label = self.ar.data.lang['c052_fix']
        else: #r000_rebuilder
            self.first_bt_label = self.ar.data.lang['i164_export']
            self.second_bt_label = self.ar.data.lang['i196_import']
        if self.first_bt_custom_label:
            self.first_bt_label = self.first_bt_custom_label
        if self.second_bt_custom_label:
            self.second_bt_label = self.second_bt_custom_label


    def change_active(self, value, *args):
        """ Set active attribute to given value.
            If there's an UI it will work to update the checkBox and buttons.
        """
        self.active = value
        if self.ar.data.ui_state:
            if self.action_cb and cmds.checkBox(self.action_cb, query=True, exists=True):
                cmds.checkBox(self.action_cb, edit=True, value=value)
            if self.first_bt and cmds.button(self.first_bt, query=True, exists=True):
                cmds.button(self.first_bt, edit=True, enable=value)
            if self.second_bt and cmds.button(self.second_bt, query=True, exists=True):
                cmds.button(self.second_bt, edit=True, enable=value)


    def cleanup_to_start(self, rebuilding=False):
        """ Just redeclare variables and close openned window to run the code properly.
        """
        print(f"\n----------\n{self.ar.data.lang['c110_start']}: {self.get_title()} IO")
        if self.verbose:
            self.ar.utils.setProgress(self.get_title()+': '+self.ar.data.lang['c110_start'], self.ar.data.lang[self.action_type], addOne=False, addNumber=False)
        # redeclare variables
        self.ar.data.rebuilding = rebuilding
        self.checked_items = []
        self.found_issues = []
        self.good_results = []
        self.messages = []
        self.log_data = {}
        # close info log window if it exists
        if cmds.window('dpInfoWindow', query=True, exists=True):
            cmds.deleteUI('dpInfoWindow', window=True)
        self.update_button_colors(True) #running
        cmds.refresh()


    def reset_button_colors(self):
        """ Just set the button colors as default.
        """
        if self.ar.data.ui_state:
            if cmds.button(self.first_bt, exists=True):
                cmds.button(self.first_bt, edit=True, backgroundColor=DEFAULT_COLOR)
                cmds.button(self.second_bt, edit=True, backgroundColor=DEFAULT_COLOR)


    def update_button_colors(self, running=False):
        """ Update button background colors if using UI.
        """
        if self.ar.data.ui_state:
            if self.first_bt and cmds.button(self.first_bt, exists=True):
                if running:
                    if self.first_mode: #verify/export
                        cmds.button(self.first_bt, edit=True, backgroundColor=RUNNING_COLOR)
                        cmds.button(self.second_bt, edit=True, backgroundColor=DEFAULT_COLOR)
                    else: #fix/import
                        cmds.button(self.first_bt, edit=True, backgroundColor=DEFAULT_COLOR)
                        cmds.button(self.second_bt, edit=True, backgroundColor=RUNNING_COLOR)
                elif self.maybe_done:
                    if self.first_mode: #verify/export
                        cmds.button(self.first_bt, edit=True, backgroundColor=WARNING_COLOR)
                        cmds.button(self.second_bt, edit=True, backgroundColor=DEFAULT_COLOR)
                    else: #fix/import
                        cmds.button(self.first_bt, edit=True, backgroundColor=DEFAULT_COLOR)
                        cmds.button(self.second_bt, edit=True, backgroundColor=WARNING_COLOR)
                elif self.checked_items: #ran
                    if self.first_mode: #verify/export
                        if True in self.found_issues:
                            cmds.button(self.first_bt, edit=True, backgroundColor=ISSUE_COLOR)
                            if self.action_type == "v000_validator":
                                cmds.button(self.second_bt, edit=True, backgroundColor=WARNING_COLOR)
                            else:
                                cmds.button(self.second_bt, edit=True, backgroundColor=DEFAULT_COLOR)
                        else:
                            cmds.button(self.first_bt, edit=True, backgroundColor=CHECKED_COLOR)
                            cmds.button(self.second_bt, edit=True, backgroundColor=DEFAULT_COLOR)
                    else: #fix/import
                        if False in self.good_results:
                            if self.action_type == "v000_validator":
                                cmds.button(self.first_bt, edit=True, backgroundColor=WARNING_COLOR)
                            else:
                                cmds.button(self.first_bt, edit=True, backgroundColor=DEFAULT_COLOR)
                            cmds.button(self.second_bt, edit=True, backgroundColor=ISSUE_COLOR)
                        else:
                            cmds.button(self.first_bt, edit=True, backgroundColor=DEFAULT_COLOR)
                            cmds.button(self.second_bt, edit=True, backgroundColor=CHECKED_COLOR)
                else: #wellDone
                    if self.first_mode: #verify/export
                        cmds.button(self.first_bt, edit=True, backgroundColor=CHECKED_COLOR)
                        cmds.button(self.second_bt, edit=True, backgroundColor=DEFAULT_COLOR)
                    else: #fix/import
                        cmds.button(self.first_bt, edit=True, backgroundColor=DEFAULT_COLOR)
                        cmds.button(self.second_bt, edit=True, backgroundColor=CHECKED_COLOR)
    

    def update_info_data_button(self):
        """ Just get the latest exported data and edit the info button text.
        """
        self.info_text = "\n\n"+self.ar.data.lang['r060_latestExportedData']+"\n"
        button_label = self.get_latest_exported_data()
        button_command = self.ar.packager.openFolder
        button_argument = self.io_path
        if cmds.iconTextButton(self.name+"_itb", query=True, exists=True):
            #functools.partial(<bound method Logger.infoWin of <dpAutoRigSystem.Pipeline.dpLogger.Logger object at 0x00000259E390BD10>>, 'r003_modelIO', 'r004_modelIODesc', None, 'center', 305, 250, wiki='10-‐-Rebuilder#-model')
            this_wiki = str(cmds.iconTextButton(self.name+"_itb", query=True, command=True)).split("wiki='")[1][:-2]
            cmds.iconTextButton(self.name+"_itb", edit=True, command=partial(self.ar.logger.infoWin, self.title, self.description, self.info_text, 'center', 305, 250, buttonList=[button_label, button_command, button_argument], wiki=this_wiki))


    def get_latest_exported_data(self, *args):
        """ Returns the latest exported data or "None".
        """
        latest_data = self.ar.data.lang['i305_none']
        exported_items = self.get_exported_items()
        if exported_items:
            exported_items.sort()
            latest_data = exported_items[-1]
        return latest_data


    def update_action_buttons(self, running=False, color=True):
        """ Update buttons colors and enable.
        """
        if color:
            self.update_button_colors(running)
        if self.action_type == "r000_rebuilder":
            self.updateDeleteDataButton()
            self.update_info_data_button()


    def get_title(self):
        """ Check if there's a key in the dictionary with the current title.
            Returns its value or the current title text only.
        """
        title_text = self.title
        if self.title in self.ar.data.lang.keys():
            title_text = self.ar.data.lang[self.title]
        return title_text


    def report_log(self):
        """ Prepare the log output text and data dictionary for this checked validator/rebuilder.
        """
        # header
        log_text = self.ar.data.lang['m006_name']+": "+self.get_title()+"\n"
        # mode
        log_text += self.ar.data.lang['v003_mode']+": "
        action_text = self.second_bt_label.upper()
        if self.first_mode:
            action_text = self.first_bt_label.upper()
        log_text += action_text+"\n"
        # issues
        if True in self.found_issues:
            log_text += self.ar.data.lang['v006_foundIssue']+":\n"
            for i, item in enumerate(self.found_issues):
                if item == True:
                    log_text += self.checked_items[i]
                    if i != len(self.checked_items)-1:
                        log_text += "\n"
        else:
            log_text += self.ar.data.lang['v007_allOk']
        # messages
        if self.messages:
            for msg in self.messages:
                log_text += "\n"+msg
        log_text += "\n"
        # dataLog
        self.log_data["log"] = self.ar.data.lang[self.action_type]
        self.log_data["user"] = getpass.getuser()
        self.log_data["time"] = self.ar.pipeliner.getToday(True)
        self.log_data["dpARVersion"] = self.ar.data.version
        self.log_data["module"] = self.name
        self.log_data["name"] = self.title
        self.log_data["mode"] = action_text
        self.log_data["checked_items"] = self.checked_items
        self.log_data["found_issues"] = self.found_issues
        self.log_data["good_results"] = self.good_results
        self.log_data["messages"] = self.messages
        self.log_data["log_text"] = log_text
        # verbose call info window
        if self.verbose:
            self.ar.logger.infoWin('i019_log', self.action_type, self.log_data["time"]+"\n\n"+log_text, "left", 250, 250)
            print("\n-------------\n"+self.ar.data.lang[self.action_type]+"\n"+self.log_data["time"]+"\n\n"+log_text)
            if not self.ar.utils.exportLogDicToJson(self.log_data, sub_folder=self.ar.data.dp_data+"/"+self.ar.data.dp_log):
                print(self.ar.data.lang['i201_saveScene'])

    
    def not_found_node(self, item=None):
        """ Set dataLog when don't have any objects to verify.
        """
        self.checked_items.append(item)
        self.found_issues.append(False)
        self.good_results.append(True)
        self.messages.append(self.ar.data.lang['v014_notFoundNodes'])


    def fail_io(self, item=""):
        """ Set dataLog when IO not working well for rebuilders.
        """
        self.checked_items.append(item)
        self.found_issues.append(True)
        self.good_results.append(False)
        self.messages.append(self.ar.data.lang['r005_notWorkedWell'])


    def well_done_io(self, item="", text="r006_wellDone"):
        """ Set dataLog when rebuilder IO worked well.
        """
        self.checked_items.append(item)
        self.found_issues.append(False)
        self.good_results.append(True)
        self.messages.append(self.ar.data.lang[text]+": "+item)


    def maybe_done_io(self, item=""):
        """ Set dataLog when IO possible worked well for rebuilders, maybe.
        """
        self.maybe_done = True
        self.checked_items.append(item)
        self.found_issues.append(False)
        self.good_results.append(True)
        self.messages.append(self.ar.data.lang['r063_maybeDoneIO']+": "+item)


    def get_io_path(self, io_folder):
        """ Returns the IO path for the current scene.
        """
        if "assetPath" in self.ar.pipeliner.pipeData.keys() and io_folder:
            return self.ar.pipeliner.pipeData['assetPath']+"/"+self.ar.pipeliner.pipeData[io_folder]


    def get_exported_items(self, items=None, sub_folder="", ask_has_data=False, get_any=False):
        """ Returns the exported file list in the current asset folder IO or the given items.
        """
        exported_items = None
        result = []
        self.io_path = self.get_io_path(self.io_folder)
        if self.io_path:
            if ask_has_data:
                return os.path.exists(self.io_path)
            if items:
                exported_items = items
                if not type(items) == list:
                    exported_items = [items]
            elif get_any:
                if os.path.exists(self.io_path):
                    exported_items = next(os.walk(self.io_path))[2]
            else:
                if os.path.exists(self.io_path+"/"+sub_folder):
                    exported_items = next(os.walk(self.io_path+"/"+sub_folder))[2]
            if exported_items:
                if sub_folder or get_any:
                    return exported_items
                asset_name = self.ar.pipeliner.pipeData["assetName"]
                for item in exported_items:
                    if asset_name in item:
                        result.append(item)
        return result


    def run_actions_in_silence(self, action_names, action_instances, first_mode, items):
        """ Run action from a list without verbose.
        """
        if action_instances:
            for action_name in action_names:
                for action_instance in action_instances:
                    if action_name in str(action_instance):
                        action_instance.verbose = False
                        action_instance.runAction(first_mode, items)
                        action_instance.verbose = True


    def refresh_view(self):
        """ Just refresh the viewport and fit the view camera to all visible nodes.
        """
        cmds.refresh()
        cmds.viewFit(allObjects=True, animate=True)
        mel.eval("flushUndo;")
        cmds.select(clear=True)


    def change_node_state(self, items, find_deform=True, state=None, dic=None):
        """ Useful for rebuilder to set deformer node state as has no effect before export a not edited mesh.
            Returns the current node state dictionary of the given node list and all descendent hierarchy too.
        """
        result_data = {}
        to_change_items = []
        if find_deform:
            for item in items:
                children = cmds.listRelatives(item, children=True, allDescendents=True)
                if children:
                    children.append(item)
                else:
                    children = [item]
                for child in children:
                    try:
                        input_deformers = cmds.findDeformers(child)
                    except:
                        self.messages.append(self.ar.data.lang['i075_moreOne']+": "+child)
                        input_deformers = False
                    if input_deformers:
                        for deformer_node in input_deformers:
                            if not deformer_node in to_change_items:
                                to_change_items.append(deformer_node)
        elif dic:
            to_change_items = dic.keys()
        else:
            to_change_items = items
        if to_change_items:
            for node in to_change_items:
                if not cmds.listConnections(node+".nodeState", source=True, destination=False):
                    value = state
                    if dic:
                        value = dic[node]
                    result_data[node] = cmds.getAttr(node+".nodeState")
                    lock_attr_status = cmds.getAttr(node+".nodeState", lock=True)
                    lock_node_status = cmds.lockNode(node, query=True, lock=True)[0]
                    cmds.lockNode(node, lock=False)
                    cmds.setAttr(node+".nodeState", lock=False)
                    # set nodeState attribute value
                    cmds.setAttr(node+".nodeState", value)
                    cmds.setAttr(node+".nodeState", lock=lock_attr_status)
                    if lock_node_status:
                        cmds.lockNode(node, lock=True)
        return result_data
    

    def get_broken_id_data(self, toCheckList=None):
        """ Return a dictionary with the broken ID nodes as keys and them father nodes as values.
        """
        dic = {"BrokenID" : {}}
        if not toCheckList:
            toCheckList = cmds.ls(selection=False, long=True, type="transform", noIntermediate=True)
        if toCheckList:
            self.ar.utils.setProgress(self.ar.data.lang[self.title], self.ar.data.lang[self.action_type], addOne=False, addNumber=False)
            self.ar.utils.setProgress(max=len(toCheckList), addOne=False, addNumber=False)
            filteredList = self.ar.utils.filterTransformList(toCheckList, verbose=self.verbose, title=self.ar.data.lang[self.title]+" "+self.ar.data.lang['i329_broken'])
            if filteredList:
                for item in filteredList:
                    shortName = item[item.rfind("|")+1:]
                    if not self.ar.utils.validateID(shortName):
                        itemType = cmds.objectType(item)
                        if not itemType in dic["BrokenID"].keys():
                            dic["BrokenID"][itemType] = {}
                        dic["BrokenID"][itemType][shortName] = None
                        fatherList = cmds.listRelatives(item, parent=True, fullPath=True)
                        if fatherList:
                            dic["BrokenID"][itemType][shortName] = fatherList[0]
        return dic


    def endProgress(self, update_guides=False, *args):
        print(f"{self.ar.data.lang['m184_end']}: {self.get_title()} IO\n----------")
        if self.verbose:
            self.ar.utils.setProgress(endIt=True)
        if update_guides:
            self.ar.ui_manager.clear_guide_layout()
            self.ar.filler.fill_created_guides()
        self.ar.data.rebuilding = False


    def exportDicToJsonFile(self, dic, *args):
        """ Export given dictionary to json file using ioPath and startName as prefix of the current file name.
        """
        if dic:
            try:
                # export json file
                self.ar.pipeliner.makeDirIfNotExists(self.io_path)
                jsonName = self.io_path+"/"+self.startName+"_"+self.ar.pipeliner.pipeData['currentFileName']+".json"
                self.ar.pipeliner.saveJsonFile(dic, jsonName)
                self.well_done_io(jsonName)
            except Exception as e:
                self.fail_io(jsonName+": "+str(e))
        else:
            self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])


    def exportAlembicFile(self, items, path=None, startName=None, fileName=None, attr=True, curve=False, *args):
        """ Export given mesh list to alembic file.
            If curve argument is True, it'll also accept export nurbsCurve shapes.
        """
        try:
            if not path:
                path = self.io_path
            if not startName:
                startName = self.startName
            if not fileName:
                fileName = self.ar.pipeliner.pipeData['currentFileName']
            nodeStateDic = self.change_node_state(items, state=1) #has no effect
            # export alembic
            self.ar.pipeliner.makeDirIfNotExists(path)
            ioItems = ' -root '.join(items)
            attrStr = ""
            if attr:
                items.extend(cmds.listRelatives(items, type="mesh", children=True, allDescendents=True, noIntermediate=True) or [])
                if curve:
                    items.extend(cmds.listRelatives(items, type="nurbsCurve", children=True, allDescendents=True, noIntermediate=True) or [])
                for mesh in items:
                    self.ar.utils.setProgress(self.ar.data.lang[self.title])
                    userDefAttrList = cmds.listAttr(mesh, userDefined=True)
                    if userDefAttrList:
                        for userDefAttr in userDefAttrList:
                            attrStr += " -attr "+userDefAttr
            abcName = path+"/"+startName+"_"+fileName+".abc"
            cmds.AbcExport(jobArg="-frameRange 0 0 -uvWrite -writeVisibility -writeUVSets -worldSpace -dataFormat ogawa -root "+ioItems+attrStr+" -file "+abcName)
            if nodeStateDic:
                self.change_node_state(items, find_deform=False, dic=nodeStateDic) #back deformer as before
            self.well_done_io(abcName)
        except Exception as e:
            self.fail_io(', '.join(items)+": "+str(e))


    def importLatestAlembicFile(self, exported_items, *args):
        """ Import the latest alembic file from given exported list.
        """
        self.latestDataFile = None
        if exported_items:
            self.ar.utils.setProgress(self.ar.data.lang[self.title], addOne=False, addNumber=False)
            try:
                # import alembic
                exported_items.sort()
                self.latestDataFile = exported_items[-1]
                abcToImport = self.io_path+"/"+self.latestDataFile
                #cmds.AbcImport(jobArg="-mode import \""+abcToImport+"\"")
                mel.eval("AbcImport -mode import \""+abcToImport+"\";")
                self.well_done_io(self.latestDataFile)
            except Exception as e:
                self.fail_io(self.latestDataFile+": "+str(e))
        else:
            self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])


    def importLatestJsonFile(self, exported_items, path=None, *args):
        """ Return the latest exported json file from given list.
        """
        self.latestDataFile = None
        if exported_items:
            if not path:
                path = self.io_path
            exported_items.sort()
            self.latestDataFile = exported_items[-1]
            return self.ar.pipeliner.getJsonContent(self.io_path+"/"+exported_items[-1])
        else:
            self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])


    def updateDeleteDataButton(self, *args):
        """ Check if there's some exported data for this module and update the delete data button as enable or disable.
        """
        if self.io_folder and cmds.iconTextButton(self.delete_data_itb, query=True, exists=True):
            if self.get_exported_items(ask_has_data=True):
                cmds.iconTextButton(self.delete_data_itb, edit=True, enable=True)
            else:
                cmds.iconTextButton(self.delete_data_itb, edit=True, enable=False)


    def deleteData(self, *args):
        """ Confirm if the user really want to delete the rebuilding exported data, then delete its folder.
        """
        # to confirm before delete data
        confirm = cmds.confirmDialog(title=self.ar.data.lang[self.title], icon="question", message=self.ar.data.lang['r059_deleteData'], button=[self.ar.data.lang['i071_yes'], self.ar.data.lang['i072_no']], defaultButton=self.ar.data.lang['i072_no'], cancelButton=self.ar.data.lang['i072_no'], dismissString=self.ar.data.lang['i072_no'])
        if confirm == self.ar.data.lang['i071_yes']:
            oldFirstBTLabel = self.first_bt_label
            self.first_mode = True
            self.first_bt_label = self.ar.data.lang['i344_deleted']
            try:
                shutil.rmtree(self.io_path, ignore_errors=False)
                self.updateDeleteDataButton()
                self.update_info_data_button()
                self.well_done_io(self.io_path, 'i344_deleted')
            except:
                self.fail_io(self.io_path)
            self.report_log()
            self.first_bt_label = oldFirstBTLabel


    def getUsedMaterialList(self, *args):
        """ List all materials used by geometry in the scene.
            https://discourse.techart.online/t/list-all-materials-used-in-scene/10185
        """
        usedMaterialList = []
        shadingEngineList = cmds.ls(type='shadingEngine')
        for shadEng in shadingEngineList:
            # if an shadingEngine has 'sets' members, it is used in the scene
            if cmds.sets(shadEng, query=True):
                matList = cmds.listConnections('{}.surfaceShader'.format(shadEng))
                if matList:
                    usedMaterialList.extend(matList)
        usedMaterialList = list(set(usedMaterialList))
        usedMaterialList.sort()
        return usedMaterialList


    def getModelToExportList(self, *args):
        """ Returns a list of higher father mesh node list or the children nodes in Render_Grp.
        """
        meshList, tempList = [], []
        renderGrp = self.ar.utils.getNodeByMessage("renderGrp")
        if renderGrp:
            meshList = cmds.listRelatives(renderGrp, allDescendents=True, fullPath=True, noIntermediate=True, type="mesh") or []
            if meshList:
                return cmds.listRelatives(renderGrp, children=True, type="transform")
        if not meshList:
            unparentedMeshList = cmds.ls(selection=False, noIntermediate=True, long=True, type="mesh")
            if unparentedMeshList:
                for item in unparentedMeshList:
                    if not cmds.objExists(item+"."+self.ar.data.master_attr):
                        fatherNode = item[:item[1:].find("|")+1]
                        if fatherNode:
                            if not cmds.objExists(fatherNode+"."+self.ar.data.master_attr):
                                if not fatherNode in tempList:
                                    tempList.append(fatherNode)
        if tempList:
            for node in tempList:
                isCleaned = True
                if not cmds.objExists(node+".guideBase") and not cmds.objExists(node+".dpGuide"):
                    children = cmds.listRelatives(node, children=True, allDescendents=True)
                    if children:
                        for child in children:
                            if cmds.objExists(child+".guideBase") or cmds.objExists(child+".dpGuide"):
                                isCleaned = False
                else:
                    isCleaned = False
                if isCleaned:
                    meshList.append(node)
        return meshList


    def getMeshTransformList(self, shapeList=None, *args):
        """ Returns a list of transforms that have mesh polygons.
        """
        if not shapeList:
            shapeList = cmds.ls(selection=False, type='mesh')
        if shapeList:
            # Get only transform nodes
            return list(set(cmds.listRelatives(shapeList, type="transform", parent=True, fullPath=True)))


    def reorderList(self, items, *args):
        """ Returns a list with high to low counting of '|' in the item list given. That means a descending order.
        """
        return sorted(items, key = lambda x: x.count("|"), reverse=True)


    def getConstraintDataDic(self, constraintList, *args):
        """ Processes the given constraint list to collect and mount the info data.
            Returns the dictionary to export.
        """
        dic = {}
        attrList = ["interpType", "constraintOffsetPolarity", "aimVectorX", "aimVectorY", "aimVectorZ", "upVectorX", "upVectorY", "upVectorZ", "worldUpType", "worldUpVectorX", "worldUpVectorY", "worldUpVectorZ"]
        outputAttrList = ["constraintTranslateX", "constraintTranslateY",  "constraintTranslateZ",  "constraintRotateX",  "constraintRotateY",  "constraintRotateZ",  "constraintScaleX",  "constraintScaleY",  "constraintScaleZ"]
        #typeAttrDic = {
        #                "parentConstraint" : ["interpType"],
        #                "orientConstraint" : ["interpType"],
        #                "pointConstraint"  : ["constraintOffsetPolarity"],
        #                "normalConstraint" : ["aimVectorX", "aimVectorY", "aimVectorZ", "upVectorX", "upVectorY", "upVectorZ", "worldUpType", "worldUpVectorX", "worldUpVectorY", "worldUpVectorZ"],
        #                "aimConstraint"    : ["aimVectorX", "aimVectorY", "aimVectorZ", "upVectorX", "upVectorY", "upVectorZ", "worldUpType", "worldUpVectorX", "worldUpVectorY", "worldUpVectorZ"]
        #            }
        self.ar.utils.setProgress(max=len(constraintList), addOne=False, addNumber=False)
        for const in constraintList:
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            if not cmds.attributeQuery(self.ar.data.dp_id, node=const, exists=True):
                # getting attributes if they exists
                dic[const] = {"attributes" : {},
                              "output"     : {},
                              "type"       : cmds.objectType(const)
                            }
                for attr in attrList:
                    if cmds.objExists(const+"."+attr):
                        dic[const]["attributes"][attr] = cmds.getAttr(const+"."+attr)
                dic[const]["worldUpMatrix"] = []
                if cmds.objExists(const+".worldUpMatrix"):
                    dic[const]["worldUpMatrix"] = cmds.listConnections(const+".worldUpMatrix", source=True, destination=False)
                dic[const]["constraintParentInverseMatrix"] = cmds.listConnections(const+".constraintParentInverseMatrix", source=True, destination=False)
                dic[const]["target"] = {}
                if cmds.objExists(const+".target"):
                    targetAttr = None
                    if cmds.objExists(const+".target[0].targetParentMatrix"):
                        targetAttr = "targetParentMatrix"
                    elif cmds.objExists(const+".target[0].targetGeometry"):
                        targetAttr = "targetGeometry"
                    elif cmds.objExists(const+".target[0].targetMesh"):
                        targetAttr = "targetMesh"
                    if targetAttr:
                        dic[const]["target"][targetAttr] = {}
                        targetList = cmds.getAttr(const+".target", multiIndices=True)
                        for t in targetList:
                            dic[const]["target"][targetAttr][t] = [cmds.listConnections(const+".target["+str(t)+"]."+targetAttr, source=True, destination=False)[0], cmds.getAttr(const+".target["+str(t)+"].targetWeight")]
                # store connection info to disconnect when import if need to skip the constraint driving
                for outAttr in outputAttrList:
                    dic[const]["output"][outAttr] = None
                    if cmds.objExists(const+"."+outAttr):
                        if cmds.listConnections(const+"."+outAttr, source=False, destination=True):
                            dic[const]["output"][outAttr] = True
                        else:
                            dic[const]["output"][outAttr] = False
        return dic


    def importConstraintData(self, constDic, verbose=True, *args):
        """ Import constraints from exported dictionary.
            Create missing constraints and set them values if they don't exists.
        """
        self.ar.utils.setProgress(max=len(constDic.keys()), addOne=False, addNumber=False)
        # define lists to check result
        wellImportedList = []
        for item in constDic.keys():
            existingNodesList = []
            self.ar.utils.setProgress(self.ar.data.lang[self.title])
            # create constraint node if it needs
            if not cmds.objExists(item):
                constType = constDic[item]["type"]
                targetList, valueList = [], []
                if constDic[item]["target"]:
                    targetAttr = list(constDic[item]["target"].keys())[0]
                    keyList = list(constDic[item]["target"][targetAttr].keys())
                    keyList.sort()
                    for k in keyList:
                        targetList.append(constDic[item]["target"][targetAttr][k][0])
                        valueList.append(constDic[item]["target"][targetAttr][k][1])
                toNodeList = constDic[item]["constraintParentInverseMatrix"]
                # create the missing constraint
                if targetList and toNodeList:
                    if cmds.objExists(toNodeList[0]) and not [tgt for tgt in targetList if not cmds.objExists(tgt)]:
                        if constType == "parentConstraint":
                            const = cmds.parentConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                        elif constType == "pointConstraint":
                            const = cmds.pointConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                        elif constType == "orientConstraint":
                            const = cmds.orientConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                        elif constType == "scaleConstraint":
                            const = cmds.scaleConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                        elif constType == "aimConstraint":
                            const = cmds.aimConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                        elif constType == "pointOnPolyConstraint":
                            const = cmds.pointOnPolyConstraint(targetList, toNodeList[0], maintainOffset=True, name=item)[0]
                        elif constType == "geometryConstraint":
                            const = cmds.geometryConstraint(targetList, toNodeList[0], name=item)[0]
                        elif constType == "normalConstraint":
                            const = cmds.normalConstraint(targetList, toNodeList[0], name=item)[0]
                        elif constType == "poleVectorConstraint":
                            const = cmds.poleVectorConstraint(targetList, toNodeList[0], name=item)[0]
                        elif constType == "tangentConstraint":
                            const = cmds.tangentConstraint(targetList, toNodeList[0], name=item)[0]
                        # set attribute values
                        if constDic[item]["attributes"]:
                            for attr in constDic[item]["attributes"].keys():
                                cmds.setAttr(const+"."+attr, constDic[item]["attributes"][attr])
                        # set weight values
                        for v, value in enumerate(valueList):
                            cmds.setAttr(item+"."+targetList[v]+"W"+str(v), value)
                        if constDic[item]["worldUpMatrix"]:
                            cmds.connectAttr(constDic[item]["worldUpMatrix"][0]+".worldMatrix", const+".worldUpMatrix", force=True)
                        # disconnect to keep the same exported skip option
                        for outAttr in constDic[item]["output"].keys():
                            if cmds.objExists(const+"."+outAttr):
                                if not constDic[item]["output"][outAttr]:
                                    connectedList = cmds.listConnections(const+"."+outAttr, source=False, destination=True, plugs=True)
                                    if connectedList:
                                        cmds.disconnectAttr(const+"."+outAttr, connectedList[0])
                        wellImportedList.append(const)
                else:
                    cmds.createNode(constType, name=item) #broken node
                    if verbose:
                        self.fail_io(self.ar.data.lang['i329_broken']+" node - "+item)
            else:
                existingNodesList.append(item)
        if verbose:
            if wellImportedList:
                self.well_done_io(self.latestDataFile)
            else:
                if existingNodesList:
                    self.well_done_io(self.ar.data.lang['r032_notImportedData'])
                else:
                    self.fail_io(self.ar.data.lang['v014_notFoundNodes']+": "+', '.join(existingNodesList))


    def removeConstraints(self, items, *args):
        """ Delete the existing contraints from the given list and descendents.
            Store their info data in a dictionary and return it.
        """
        dataDic = {}
        constraintList = []
        constraintList.extend(cmds.ls(items, type=self.constraint_types))
        constraintList.extend(cmds.ls(cmds.listRelatives(items, children=True, allDescendents=True), type=self.constraint_types))
        if constraintList:
            dataDic = self.getConstraintDataDic(constraintList)
            cmds.delete(constraintList)
        return dataDic
