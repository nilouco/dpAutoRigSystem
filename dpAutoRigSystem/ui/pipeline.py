#import libraries
from maya import cmds
from functools import partial


class PipelineUI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self, loaded_file_info=False, *args):
        """ Open an UI to load, set and save the pipeline info.
        """
        self.ar.utils.close_ui('dpPipelinerWindow')
        self.ar.pipeliner.get_pipeline_data(loaded_file_info)
        # window
        if self.ar.data.ui_state:
            win_width  = 380
            win_height = 480
            cmds.window('dpPipelinerWindow', title="Pipeliner "+str(self.ar.data.version), widthHeight=(win_width, win_height), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
            cmds.showWindow('dpPipelinerWindow')
            # create UI layout and elements:
            cmds.columnLayout('pipeline_cl', adjustableColumn=True, columnOffset=("both", 10))
            # pipeline info
            cmds.columnLayout('pipeline_info_cl', adjustableColumn=True, columnOffset=("left", 10), parent='pipeline_cl')
            cmds.separator(style='in', height=20, parent='pipeline_info_cl')
            cmds.text('pipeline_info_txt', label="Pipeline "+self.ar.data.lang['i013_info'], height=30, font='boldLabelFont', parent='pipeline_info_cl')
            cmds.textFieldButtonGrp('pipeline_path_data_tfbg', label=self.ar.data.lang['i220_filePath'], text=self.ar.pipeliner.get_path_data(), buttonLabel=self.ar.data.lang['i187_load'], buttonCommand=self.ar.pipeliner.load_pipe_info, changeCommand=partial(self.ar.pipeliner.load_pipe_info, True), adjustableColumn=2, parent='pipeline_info_cl')
            cmds.separator(style='in', height=20, parent='pipeline_info_cl')
            # pipeline data
            cmds.text('pipeline_data_txt', height=30, label="Pipeline Data", font='boldLabelFont', parent='pipeline_info_cl')
            cmds.scrollLayout('pipeline_sl', parent='pipeline_cl')
            cmds.columnLayout('pipeline_data_cl', adjustableColumn=True, width=400, columnOffset=("left", 10), parent='pipeline_sl')
            cmds.columnLayout('pipeline_footer_cl', adjustableColumn=True, width=400, columnOffset=("left", 10), parent='pipeline_cl')
            # load data from pipeline info
            self.load_ui_data()


    def load_ui_data(self, *args):
        """ Populate the UI with loaded data file info.
        """
        cmds.deleteUI('pipeline_data_cl')
        cmds.deleteUI('pipeline_footer_cl')
        cmds.columnLayout('pipeline_data_cl', adjustableColumn=True, width=400, columnOffset=("left", 10), parent='pipeline_sl')
        if self.ar.pipeliner.pipe_info:
            self.ui_info = {}
            for key in list(self.ar.pipeliner.pipe_info):
                if "_" in key:
                    if key.startswith("f_"):
                        self.ui_info[key] = cmds.textFieldButtonGrp(key, label=key[2:], text=self.ar.pipeliner.pipe_info[key], annotation=self.ar.data.lang[self.ar.pipeliner.pipeline_annotation[key]], buttonLabel=self.ar.data.lang['i187_load'], buttonCommand=partial(self.load_info_key, key), adjustableColumn=2, parent='pipeline_data_cl')
                    elif key.startswith("i_"):
                        self.ui_info[key] = cmds.intFieldGrp(key, label=key[2:], value1=self.ar.pipeliner.pipe_info[key], annotation=self.ar.data.lang[self.ar.pipeliner.pipeline_annotation[key]], numberOfFields=1, parent='pipeline_data_cl')
                    elif key.startswith("b_"):
                        self.ui_info[key] = cmds.checkBox(key, label=key[2:], value=self.ar.pipeliner.pipe_info[key], annotation=self.ar.data.lang[self.ar.pipeliner.pipeline_annotation[key]], parent='pipeline_data_cl')
                    elif key.startswith("s_"):
                        self.ui_info[key] = cmds.textFieldGrp(key, label=key[2:], text=self.ar.pipeliner.pipe_info[key], annotation=self.ar.data.lang[self.ar.pipeliner.pipeline_annotation[key]], parent='pipeline_data_cl')
            # try to force loading empty data info
            try:
                if self.ar.pipeliner.pipe_data['sceneName']:
                    if not cmds.textFieldButtonGrp(self.ui_info['f_drive'], query=True, text=True):
                        self.ar.pipeliner.get_info_by_path("f_drive", None)
                        cmds.textFieldButtonGrp(self.ui_info['f_drive'], edit=True, text=self.ar.pipeliner.pipe_data['f_drive'])
                    if not cmds.textFieldButtonGrp(self.ui_info['f_studio'], query=True, text=True):
                        self.ar.pipeliner.get_info_by_path("f_studio", "f_drive")
                        cmds.textFieldButtonGrp(self.ui_info['f_studio'], edit=True, text=self.ar.pipeliner.pipe_data['f_studio'])
                    if not cmds.textFieldButtonGrp(self.ui_info['f_project'], query=True, text=True):
                        self.ar.pipeliner.get_info_by_path("f_project", "f_studio")
                        cmds.textFieldButtonGrp(self.ui_info['f_project'], edit=True, text=self.ar.pipeliner.pipe_data['f_project'])
            except:
                pass
            cmds.columnLayout('pipeline_footer_cl', adjustableColumn=True, width=400, columnOffset=("left", 10), parent='pipeline_cl')
            cmds.separator(style='in', height=20, parent='pipeline_footer_cl')
            cmds.paneLayout("pipeline_footer_buttons_pl", configuration="vertical3", separatorThickness=2.0, parent='pipeline_footer_cl')
            cmds.button('pipeline_reset_info_bt', label=self.ar.data.lang['i271_reset'], command=self.ar.pipeliner.reset_pipe_info, backgroundColor=(0.75, 0.75, 0.75), parent='pipeline_footer_buttons_pl')
            cmds.button('pipeline_new_info_bt', label=self.ar.data.lang['i304_new'], command=self.ar.pipeliner.new_pipe_info, backgroundColor=(0.75, 0.75, 0.75), parent='pipeline_footer_buttons_pl')
            cmds.button('pipeline_save_info_bt', label=self.ar.data.lang['i222_save'], command=self.ar.pipeliner.save_pipe_info, backgroundColor=(0.75, 0.75, 0.75), parent='pipeline_footer_buttons_pl')
            cmds.separator(style='none', height=5, parent='pipeline_footer_cl')
        else:
            cmds.text('pipeline_path_data_txt', label=self.ar.pipeliner.get_path_data(), parent='pipeline_data_cl')


    def get_ui_data_to_save(self):
        """ Read the UI fields and load them values in the ar.pipeliner.pipe_data dictionary.
        """
        for k, key in enumerate(list(self.ui_info)):
            if key.startswith("f_"):
                self.ar.pipeliner.pipe_data[key] = cmds.textFieldButtonGrp(self.ui_info[key], query=True, text=True)
            elif key.startswith("i_"):
                self.ar.pipeliner.pipe_data[key] = cmds.intFieldGrp(self.ui_info[key], query=True, value1=True)
            elif key.startswith("b_"):
                self.ar.pipeliner.pipe_data[key] = cmds.checkBox(self.ui_info[key], query=True, value=True)
            elif key.startswith("s_"):
                self.ar.pipeliner.pipe_data[key] = cmds.textFieldGrp(self.ui_info[key], query=True, text=True)


    def load_info_key(self, item, *args):
        """ Method called by the Pipeliner UI button to load the info about the item.
        """
        result_items = cmds.fileDialog2(fileMode=3, dialogStyle=2)
        if result_items:
            conform_info = self.conform_loaded_info(item, result_items)
            cmds.textFieldButtonGrp(self.ui_info[item], edit=True, text=conform_info)
            self.set_pipeline_info_file()


    def save_version_ui(self, *args):
        """ UI to chose save asset version options.
        """
        if self.ar.pipeliner.check_asset_context():
            # declaring variables:
            saveVersion_title = 'dpAutoRig - '+self.ar.data.lang['i222_save']+" "+self.ar.data.lang['i303_asset']+" "+self.ar.data.lang['m205_version'].lower()
            saveVersion_winWidth = 380
            saveVersion_winHeight = 220
            saveVersion_align = "left"
            # window:
            self.ar.utils.close_ui("dpSaveVersionWindow")
            cmds.window('dpSaveVersionWindow', title=saveVersion_title, iconName='dpInfo', widthHeight=(saveVersion_winWidth, saveVersion_winHeight), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False)
            # creating text layout:
            cmds.columnLayout('save_version_cl', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=3, parent='dpSaveVersionWindow')
            cmds.separator(style='none', height=10, parent='save_version_cl')
            cmds.textFieldGrp('save_version_current_path_tfg', label="Path", text=self.ar.pipeliner.pipe_data['wipPath'], columnWidth2=(80, 150), editable=False, adjustableColumn=2, parent='save_version_cl')
            cmds.textFieldGrp('save_version_current_filename_tfg', label=self.ar.data.lang['i276_current'], text=self.ar.pipeliner.get_current_filename(), columnWidth2=(80, 150), editable=False, adjustableColumn=2, parent='save_version_cl')
            cmds.textFieldGrp('save_version_model_tfg', label="Model "+self.ar.data.lang['m205_version'].lower(), text=str(int(self.ar.pipeliner.get_model_version())), columnWidth2=(80, 50), textChangedCommand=self.ar.pipeliner.get_save_version_preview_text, parent='save_version_cl')
            cmds.textFieldGrp('save_version_rig_tfg', label="WIP "+self.ar.data.lang['m205_version'].lower(), text=str(int(self.ar.pipeliner.get_wip_rig_version())+1), columnWidth2=(80, 50), textChangedCommand=self.ar.pipeliner.get_save_version_preview_text, parent='save_version_cl')
            cmds.separator(style='none', height=10, parent='save_version_cl')
            cmds.text('save_version_preview_header_txt', label="Preview:", font="obliqueLabelFont", align=saveVersion_align, parent='save_version_cl')
            cmds.scrollLayout("save_version_preview_sl", height=35, parent='save_version_cl')
            cmds.text('save_version_preview_txt', label="", font="boldLabelFont", align="center", parent='save_version_preview_sl')
            cmds.button('save_version_run_bt', label=self.ar.data.lang['i222_save'], align=saveVersion_align, command=self.ar.pipeliner.save_version, parent='save_version_cl')
            # call save asset version Window:
            cmds.showWindow('dpSaveVersionWindow')
            self.ar.pipeliner.get_save_version_preview_text()
        else:
            cmds.confirmDialog(title=self.ar.data.lang['i222_save']+" "+self.ar.data.lang['i303_asset']+" "+self.ar.data.lang['m205_version'].lower(), message=self.ar.data.lang['r069_noAssetToSaveVersion'], button="Ok")


    def select_asset_ui(self, assets, path, mode, *args):
        """ Let user select the asset file we use in the given mode (load or replaceData).
            Button will call the load_asset method again passing the choose arguments.
            Works well for load and replace data.
        """
        # declaring variables:
        selectAsset_title = 'dpAutoRig - '+self.ar.data.lang['m004_select']+" "+self.ar.data.lang['i303_asset']
        select_winWidth = 240
        select_winHeight = 285
        select_align = "center"
        self.ar.utils.close_ui("dpSelectAssetWindow")
        cmds.window('dpSelectAssetWindow', title=selectAsset_title, iconName='dpInfo', widthHeight=(select_winWidth, select_winHeight), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False)
        # creating layout:
        cmds.columnLayout('select_asset_cl', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=10, parent='dpSelectAssetWindow')
        cmds.separator(style='none', height=10, parent='select_asset_cl')
        cmds.text(label=self.ar.data.lang['m004_select']+" "+self.ar.data.lang['i303_asset']+":", align="left", parent='select_asset_cl')
        cmds.textScrollList('select_asset_tsl', allowMultiSelection=False, append=assets, parent='select_asset_cl')
        cmds.button('run_select_asset_bt', label=self.ar.data.lang['m004_select'], align=select_align, command=partial(self.load_selected_asset, path, mode), parent='select_asset_cl')
        # call Window:
        cmds.showWindow('dpSelectAssetWindow')


    def load_selected_asset(self, path, mode, *args):
        """ Transfer path and mode arguments to load_asset method and also pass the selected item from the text scroll list UI.
        """
        selected_items = cmds.textScrollList('select_asset_tsl', query=True, selectItem=True)
        if selected_items:
            self.ar.pipeliner.load_asset(path, selected_items[0], mode)
            self.ar.utils.close_ui("dpSelectAssetWindow")


    def refresh_project_ui(self, path):
        """ Just edit the UI with the pipeliner project data.
        """
        cmds.textFieldGrp("asset_maya_project_tfg", edit=True, text=self.ar.pipeliner.pipe_data['mayaProject'])
        cmds.textFieldGrp("asset_pipeline_tfg", edit=True, text=self.ar.pipeliner.pipe_data['projectPath'])
        cmds.button("asset_open_folder_bt", edit=True, command=partial(self.ar.packager.open_folder, path))


    def select_asset_checkbox_ui(self, assets, path):
        """ Let user select the assets to publish in batch.
        """
        # declaring variables:
        selectAssetCB_title = 'dpAutoRig - '+self.ar.data.lang['m046_publisher']+" "+self.ar.data.lang['i358_batch']
        selectCB_winWidth = 240
        selectCB_winHeight = 285
        selectCB_align = "center"
        self.ar.utils.close_ui("dpSelectAssetCBWindow")
        cmds.window('dpSelectAssetCBWindow', title=selectAssetCB_title, iconName='dpInfo', widthHeight=(selectCB_winWidth, selectCB_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
        # creating layout:
        cmds.columnLayout('select_asset_batch_cl', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=10, parent='dpSelectAssetCBWindow')
        cmds.separator(style='none', height=10, parent='select_asset_batch_cl')
        cmds.text(label=self.ar.data.lang['m004_select']+" "+self.ar.data.lang['i303_asset']+"s:", align="left", parent='select_asset_batch_cl')
        if len(assets) > 1:
            cmds.checkBox(label=self.ar.data.lang['m004_select']+" "+self.ar.data.lang['i211_all'], value=False, changeCommand=self.select_all_assets, parent='select_asset_batch_cl')
        cmds.separator(style='in', height=10, parent='select_asset_batch_cl')
        cmds.scrollLayout('select_asset_batch_sl', parent='select_asset_batch_cl')
        cmds.columnLayout('select_asset_batch_checkbox_cl', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=10, parent='select_asset_batch_sl')
        # assets checkboxes
        self.select_asset_checkboxes = []
        for asset in assets:
            self.select_asset_checkboxes.append(cmds.checkBox(asset+"_cb", label=asset, parent='select_asset_batch_checkbox_cl'))
        cmds.separator(style='in', height=10, parent='select_asset_batch_cl')
        cmds.textFieldGrp('comment_batch_tfg', label=self.ar.data.lang['i219_comments'], text='', adjustableColumn=2, editable=True, columnAlign2=("left", "left"), columnAttach2=("left", "left"), columnWidth=[(1, 55), (2, 50)], parent='select_asset_batch_cl')
        cmds.button('run_select_assets_bt', label=self.ar.data.lang['i216_publish'], align=selectCB_align, command=partial(self.ar.publisher.load_publishing_batch, path), height=30, backgroundColor=(0.75, 0.75, 0.75), parent='select_asset_batch_cl')
        cmds.separator(style='none', height=5, parent='select_asset_batch_cl')
        # call Window:
        cmds.showWindow('dpSelectAssetCBWindow')


    def select_all_assets(self, cb_value, *args):
        """ Set all existing asset checkbox values.
        """
        for item in self.select_asset_checkboxes:
            cmds.checkBox(item, edit=True, value=cb_value)


    def load_project_path(self, *args):
        """ Open a file dialog to get the project path and write it in the respective field.
        """
        result_items = cmds.fileDialog2(fileMode=3, dialogStyle=2)
        if result_items:
            cmds.textFieldButtonGrp('project_path_tfbg', edit=True, text=result_items[0])
    

    def create_new_asset_ui(self, *args):
        """ A simple UI to get the asset info like name, model version, wip rig version in order to create a new asset context.
        """
        # declaring variables:
        title     = 'dpAutoRig - '+self.ar.data.lang['i158_create']+" "+self.ar.data.lang['i304_new']+" "+self.ar.data.lang['i303_asset']
        winWidth  = 380
        winHeight = 220
        align     = "left"
        # creating New Asset Window:
        self.ar.utils.close_ui("dpNewAssetWindow")
        cmds.window('dpNewAssetWindow', title=title, iconName='dpInfo', widthHeight=(winWidth, winHeight), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False)
        # creating text layout:
        cmds.columnLayout('new_asset_cl', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=3, parent='dpNewAssetWindow')
        cmds.separator(style='none', height=10, parent='new_asset_cl')
        cmds.textFieldGrp('new_asset_name_tfg', label=self.ar.data.lang['i303_asset']+" "+self.ar.data.lang['m006_name'].lower(), columnWidth2=(80, 150), textChangedCommand=self.get_new_asset_preview_text, adjustableColumn=2, parent='new_asset_cl')
        cmds.textFieldGrp('new_model_version_tfg', label="Model "+self.ar.data.lang['m205_version'].lower(), text="0", columnWidth2=(80, 50), textChangedCommand=self.get_new_asset_preview_text, parent='new_asset_cl')
        cmds.textFieldGrp('new_wip_version_tfg', label="WIP "+self.ar.data.lang['m205_version'].lower(), text="0", columnWidth2=(80, 50), textChangedCommand=self.get_new_asset_preview_text, parent='new_asset_cl')
        cmds.textFieldButtonGrp('project_path_tfbg', label=self.ar.data.lang['i301_project']+" path", text="", columnWidth3=(80, 150, 30), buttonLabel=self.ar.data.lang['i187_load'], buttonCommand=self.load_project_path, adjustableColumn=2, textChangedCommand=self.get_new_asset_preview_text, parent='new_asset_cl')
        if 'projectPath' in list(self.ar.pipeliner.pipe_data.keys()):
            cmds.textFieldButtonGrp('project_path_tfbg', edit=True, text=self.ar.pipeliner.pipe_data['projectPath'])
        cmds.separator(style='none', height=10, parent='new_asset_cl')
        cmds.text('create_new_asset_preview_txt', label="Preview:", font="obliqueLabelFont", align=align, parent='new_asset_cl')
        cmds.scrollLayout('preview_text_sl', height=35, parent='new_asset_cl')
        cmds.text('new_asset_preview_txt', label="", font="boldLabelFont", align="center", parent='preview_text_sl')
        cmds.button('run_create_new_asset_bt', label=self.ar.data.lang['i158_create'], align=align, command=self.ar.pipeliner.create_new_asset, parent='new_asset_cl')
        # call New Asset Window:
        cmds.showWindow('dpNewAssetWindow')
        self.get_new_asset_preview_text()


    def get_new_asset_preview_text(self, *args):
        """ Generate and return the new asset file name with complete path, using the UI info.
        """
        self.ar.pipeliner.new_asset_file = ""
        new_asset_name = cmds.textFieldGrp('new_asset_name_tfg', query=True, text=True)
        new_model_version = cmds.textFieldGrp('new_model_version_tfg', query=True, text=True)
        new_wip_version = cmds.textFieldGrp('new_wip_version_tfg', query=True, text=True)
        project_path = cmds.textFieldButtonGrp('project_path_tfbg', query=True, text=True)
        if project_path:
            if not project_path.endswith("/"):
                project_path = project_path+"/"
            wip_folder = self.ar.pipeliner.pipe_data['f_wip']
            if wip_folder:
                if not wip_folder.endswith("/"):
                    wip_folder = wip_folder+"/"
            if new_wip_version and new_model_version and new_asset_name:
                self.ar.pipeliner.new_asset_file = project_path+wip_folder+new_asset_name+"/"+new_asset_name+self.ar.pipeliner.pipe_data['s_model']+new_model_version.zfill(self.ar.pipeliner.pipe_data['i_padding'])+self.ar.pipeliner.pipe_data['s_rig']+new_wip_version.zfill(self.ar.pipeliner.pipe_data['i_padding'])+".ma"
        if self.ar.pipeliner.new_asset_file:
            cmds.text('new_asset_preview_txt', edit=True, label=self.ar.pipeliner.new_asset_file)
        return self.ar.pipeliner.new_asset_file


    def replace_data_ui(self, fromAssetName):
        """ UI to list exist items as a checkboxes to let the user choose what to replace in the dpData.
        """
        # declaring variables:
        title     = 'dpAutoRig - '+self.ar.data.lang['m219_replace']+" "+self.ar.data.dp_data+" - "+self.ar.data.lang['i303_asset']
        winWidth  = 220
        winHeight = 330+(len(self.ar.pipeliner.ios)*16)
        align     = "left"
        # creating replace dpData Window:
        self.ar.utils.close_ui('dpReplaceDPDataWindow')
        cmds.window('dpReplaceDPDataWindow', title=title, iconName='dpInfo', widthHeight=(winWidth, winHeight), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False)
        # creating layout:
        cmds.columnLayout('replace_data_cl', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=5, parent='dpReplaceDPDataWindow')
        cmds.separator(style='none', height=10, parent='replace_data_cl')
        cmds.text("replace_data_txt", label=self.ar.data.lang['i308_toReplaceDPData'], parent='replace_data_cl')
        cmds.text("replace_data_asset_txt", label="\n"+self.ar.pipeliner.pipe_data['assetName'], font="boldLabelFont", parent='replace_data_cl')
        cmds.separator(style='none', height=10, parent='replace_data_cl')
        for item in self.ar.pipeliner.ios:
            cmds.checkBox(item+"_cb", label=item, value=True)
        cmds.separator(style='none', height=10, parent='replace_data_cl')
        if len(self.ar.pipeliner.ios) > 1:
            cmds.checkBox(label=self.ar.data.lang['m004_select']+" "+self.ar.data.lang['i211_all'], value=True, changeCommand=self.select_all_data_to_replace, parent='replace_data_cl')
            cmds.separator(style='none', height=10, parent='replace_data_cl')
        cmds.button('run_replace_data_bt', label=self.ar.data.lang['m219_replace'].upper()+"\n"+fromAssetName+" -> "+self.ar.pipeliner.pipe_data['assetName'], align=align, command=self.set_replace_data, parent='replace_data_cl')
        # call New Asset Window:
        cmds.showWindow('dpReplaceDPDataWindow')
        
    
    def select_all_data_to_replace(self, cb_value, *args):
        """ Set all existing data checkbox values.
        """
        for item in self.ar.pipeliner.ios:
            cmds.checkBox(item+"_cb", edit=True, value=cb_value)


    def set_replace_data(self, *args):
        """ Read the dpReplaceDPDataWindow UI to get the active checkBoxes in order to return it in a list.
        """
        self.to_replace_datas = []
        for item in self.ar.pipeliner.ios:
            if cmds.checkBox(item+"_cb", query=True, value=True):
                self.to_replace_datas.append(item)
        if self.to_replace_datas:
            self.ar.pipeliner.replace_data()
            self.ar.utils.close_ui('dpReplaceDPDataWindow')
