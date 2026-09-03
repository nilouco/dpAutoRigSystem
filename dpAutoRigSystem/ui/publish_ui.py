#import libraries
from maya import cmds
from functools import partial


class PublishUI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self, *args):
        """ This is the main method to load the Publisher UI.
        """
        self.ar.ui_manager.close_ui('dpSuccessPublishedWindow')
        self.ar.ui_manager.close_ui('dpPublisherWindow')
        saved_scene = self.ar.utils.check_saved_scene()
        if not saved_scene:
            saved_scene = self.ar.pipeliner.confirm_save_this_scene(True)
            return
        if saved_scene:
            # window
            win_width  = 450
            win_height = 160
            cmds.window('dpPublisherWindow', title=self.ar.data.lang['m046_publisher']+" "+str(self.ar.data.version), widthHeight=(win_width, win_height), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
            # create UI layout and elements:
            cmds.columnLayout('publisher_cl', adjustableColumn=True, columnOffset=("both", 10))
            cmds.separator(style="none", height=20, parent='publisher_cl')
            # fields
            cmds.textFieldButtonGrp('publisher_file_path_tfbg', label=self.ar.data.lang['i220_filePath'], text='', buttonLabel=self.ar.data.lang['i187_load'], buttonCommand=self.user_load_file_path, adjustableColumn=2, changeCommand=self.edit_publish_path, parent='publisher_cl')
            cmds.textFieldGrp('publisher_filename_tfg', label=self.ar.data.lang['i221_fileName'], text='', adjustableColumn=2, editable=True, parent='publisher_cl')
            cmds.textFieldGrp('publisher_comment_tfg', label=self.ar.data.lang['i219_comments'], text='', adjustableColumn=2, editable=True, parent='publisher_cl')
            cmds.checkBox("publisher_verify_validators_cb", label=self.ar.data.lang['i217_verifyChecked'], align="left", height=20, value=self.ar.publisher.validate_checked, changeCommand=self.ar.publisher.set_publish_validate_checked, parent='publisher_cl')
            # buttons
            cmds.paneLayout('publisher_pl', configuration='vertical4', paneSize=[(1, 20, 20), (2, 20, 20), (3, 45, 20), (2, 20, 20)], parent='publisher_cl')
            cmds.button('pipeliner_bt', label="Pipeliner", command=self.ar.pipeline_ui.create_ui, parent='publisher_pl')
            cmds.button('diagnosing_bt', label=self.ar.data.lang['i224_diagnose'], command=self.ar.publisher.run_diagnosing, height=30, backgroundColor=(0.5, 0.5, 0.5), parent='publisher_pl')
            cmds.button('run_publishing_bt', label=self.ar.data.lang['i216_publish'], command=partial(self.ar.publisher.run_publishing, True, self.ar.data.verbose), height=30, backgroundColor=(0.75, 0.75, 0.75), parent='publisher_pl')
            cmds.button('publish_batch_bt', label=self.ar.data.lang['i358_batch'], command=partial(self.ar.pipeliner.load_asset, mode=2), height=30, backgroundColor=(0.75, 0.75, 0.75), parent='publisher_pl')
            cmds.showWindow('dpPublisherWindow')
            # load pipeliner data correctly
            self.ar.pipeliner.get_info_by_path("f_drive", None)
            self.ar.pipeliner.get_info_by_path("f_studio", "f_drive")
            self.ar.pipeliner.get_info_by_path("f_project", "f_studio")
            self.set_publish_file_path()


    def user_load_file_path(self, *args):
        """ Ask user to load a file path.
        """
        dialog_result = cmds.fileDialog2(fileFilter="Maya Files (*.ma *.mb);;", fileMode=3, dialogStyle=2, okCaption=self.ar.data.lang['i187_load'])
        if dialog_result:
            self.set_publish_file_path(dialog_result[0])


    def edit_publish_path(self, *args):
        """ Set the current publish path as the entered text in the textField.
        """
        self.ar.pipeliner.pipe_data['publishPath'] = cmds.textFieldButtonGrp('publisher_file_path_tfbg', query=True, text=True)


    def set_publish_file_path(self, file_path=None):
        """ Set the publish file path and return it.
        """
        if not file_path:
            # try to load a pipeline structure to get the file_path to set it up
            file_path = self.ar.pipeliner.load_publish_path()
        if file_path:
            if self.ar.data.ui_state and cmds.window('dpPublisherWindow', query=True, exists=True):
                cmds.textFieldButtonGrp('publisher_file_path_tfbg', edit=True, text=str(file_path))
                cmds.textFieldGrp('publisher_filename_tfg', edit=True, text=str(self.ar.pipeliner.get_pipe_filename(file_path)))
            self.ar.pipeliner.pipe_data['publishPath'] = file_path


    def success_published_ui(self, published_file, errors=False, *args):
        """ If everything works well we can call a success publishing window here.
        """
        self.ar.ui_manager.close_ui('dpSuccessPublishedWindow')
        self.ar.ui_manager.set_progress(end_it=True)
        # window
        win_width  = 250
        win_height = 130
        cmds.window('dpSuccessPublishedWindow', title=self.ar.data.lang['m046_publisher']+" "+str(self.ar.data.version), widthHeight=(win_width, win_height), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        # create UI layout and elements:
        cmds.columnLayout('success_published_cl', adjustableColumn=True, columnOffset=("both", 10))
        if published_file:
            cmds.separator(style="none", height=20, parent='success_published_cl')
            cmds.text(label=self.ar.data.lang['v023_successPublished'], font='boldLabelFont', parent='success_published_cl')
            cmds.separator(style="none", height=20, parent='success_published_cl')
            cmds.text(label=published_file, parent='success_published_cl')
        if errors:
            cmds.separator(style="in", height=20, parent='success_published_cl')
            cmds.text(label=self.ar.data.lang['i141_error']+":", font='boldLabelFont', parent='success_published_cl')
            cmds.text(label=self.ar.data.lang['i074_attention'], parent='success_published_cl')
            cmds.separator(style="none", height=20, parent='success_published_cl')
            for error_file in errors:
                cmds.button(label=error_file, command=partial(self.ar.pipeliner.load_asset, file=error_file), backgroundColor=(0.95, 0.55, 0.55), parent='success_published_cl')
            cmds.separator(style="none", height=20, parent='success_published_cl')
        else:
            cmds.separator(style="none", height=20, parent='success_published_cl')
            cmds.text(label=self.ar.data.lang['i018_thanks'], parent='success_published_cl')
        cmds.showWindow('dpSuccessPublishedWindow')
