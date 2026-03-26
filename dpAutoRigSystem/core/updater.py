import os
import io
import shutil
import zipfile
import urllib.request
from io import TextIOWrapper
from maya import cmds


class Updater(object):
    def __init__(self, ar):
        self.ar = ar
        self.version_start_length = 20 #__version__: str = "
        self.version_end_length = -2 #"
        self.download_extension = "zip"


    def load_update(self):
        if self.ar.data.ui_state and not self.ar.dev:
            if cmds.optionVar(exists=self.ar.data.check_update_option_var):
                if cmds.optionVar(query=self.ar.data.check_update_option_var):
                    if not cmds.optionVar(query=self.ar.data.check_update_last_option_var) == self.ar.config.today:
                        self.check_for_update()
            else:
                self.ar.opt.set_option_var(self.ar.data.check_update_option_var, 1, False)
                self.check_for_update()
            self.ar.opt.set_option_var(self.ar.data.check_update_last_option_var, self.ar.config.today)



    def check_for_update(self, *args):
        """ Check if there's an update for this current script version.
            Output the result in a window.
        """
        print("\n"+self.ar.data.lang['i084_checkUpdate'])
        
        # compare current version with GitHub master
        raw_results = self.check_raw_version_url()

        if self.ar.data.ui_state:
            # call Update Window about rawRsult:
            if raw_results[0] == 0:
                if self.ar.data.verbose:
                    self.ar.update_ui.create_ui(raw_results, 'i085_updated')
            elif raw_results[0] == 1:
                self.ar.update_ui.create_ui(raw_results, 'i086_newVersion')
            elif raw_results[0] == 2:
                if self.ar.data.verbose:
                    self.ar.update_ui.create_ui(raw_results, 'i087_rawURLFail')
            elif raw_results[0] == 3:
                if self.ar.data.verbose:
                    self.ar.update_ui.create_ui(raw_results, 'i088_internetFail')
            elif raw_results[0] == 4:
                if self.ar.data.verbose:
                    self.ar.update_ui.create_ui(raw_results, 'e008_failCheckUpdate')
        else:
            if raw_results[0] == 1: #there's an update
                return raw_results
        

    def check_raw_version_url(self):
        """ Check for update using raw url.
            Compares the remote version from GitHub to the current version.
            
            Returns a list with CheckedNumber and RemoteVersion or None.
            
            CheckedNumber:
                    0 - the current version is up to date
                    1 - there's a new version
                    2 - remote file not found using the given raw url
                    3 - internet connection fail (probably)
                    4 - error
                    
            if we have an update to do:
                return [CheckedNumber, RemoteVersion, RemoteLog]
            if not or ok:
                return [CheckedNumber, None]
        """
        try:
            got_remote_file = False
            # getting version.py file from GitHub website using the Raw URL:
            remote_source = urllib.request.urlopen(self.ar.data.version_url)
            remote_contents = TextIOWrapper(remote_source, encoding='utf-8')
            # find the line with the version and compare them:
            for line in remote_contents:
                if "__version__" in line:
                    got_remote_file = True
                    remote_version = line[self.version_start_length:self.version_end_length] #these magic numbers filter only the version XX.YY.ZZ
                    if remote_version == self.ar.data.version:
                        # 0 - the current version is up to date
                        return [0, None, None]
                    else:
                        # 1 - there's a new version
                        for extra_line in remote_contents:
                            if "_update_log" in extra_line:
                                remote_log = extra_line[self.version_start_length:self.version_end_length] #these magic numbers filter only the log string sentence
                                return [1, remote_version, remote_log]
                        return [1, remote_version, None]
            if not got_remote_file:
                # 2 - remote file not found using given raw url
                return [2, None, None]
        except:
            # 3 - internet connection fail (probably)
            return [3, None, None]
        # 4 - error
        return [4, None, None]


    def download(self, url, ext="zip", *args):
        """ Download the file from given url and ask user to choose a folder and a file name to save it.
        """
        ext_filter = "*."+ext
        folder = cmds.fileDialog2(fileFilter=ext_filter, dialogStyle=2)
        if folder:
            self.ar.utils.setProgress('Downloading...', 'Download Update', amount=50)
            try:
                urllib.request.urlretrieve(url, folder[0])
                button_label = self.ar.data.lang['c108_open']+" "+self.ar.data.lang['i298_folder']
                button_command = self.ar.packager.openFolder
                button_argument = folder[0][:folder[0].rfind("/")]
                self.ar.logger.infoWin('i094_downloadUpdate', 'i096_downloaded', folder[0]+'\n\n'+self.ar.data.lang['i018_thanks'], 'center', 205, 270, buttonList=[button_label, button_command, button_argument])
                self.ar.utils.closeUI('dpUpdateWindow')
            except:
                self.ar.logger.infoWin('i094_downloadUpdate', 'e009_failDownloadUpdate', folder[0]+'\n\n'+self.ar.data.lang['i097_sorry'], 'center', 205, 270)
            self.ar.utils.setProgress(endIt=True)
    

    def install(self, url, new_version, *args):
        """ Install the last version from the given url address to download file
        """
        continue_bt = self.ar.data.lang['i174_continue']
        cancel_bt = self.ar.data.lang['i132_cancel']
        confirm_auto_install = continue_bt
        if self.ar.data.ui_state:
            confirm_auto_install = cmds.confirmDialog(title=self.ar.data.lang['i098_installing'], message=self.ar.data.lang['i172_updateManual'], button=[continue_bt, cancel_bt], defaultButton=continue_bt, cancelButton=cancel_bt, dismissString=cancel_bt)
        if confirm_auto_install == continue_bt:
            print(self.ar.data.lang['i098_installing'])
            # declaring variables:
            ar_name = "dpAutoRigSystem"
            dest_folder = self.ar.data.dp_auto_rig_path
            self.ar.utils.setProgress('Installing: 0%', self.ar.data.lang['i098_installing'])
            
            try:
                # get remote file from url:
                remote_source = urllib.request.urlopen(url)
                self.ar.utils.setProgress('Installing')
                
                # read the downloaded Zip file stored in the RAM memory:
                ar_zip = zipfile.ZipFile(io.BytesIO(remote_source.read()))
                self.ar.utils.setProgress('Installing')

                # list Zip file contents in order to extract them in a temporarily folder:
                zip_names = ar_zip.namelist()
                for file_name in zip_names:
                    if ar_name in file_name:
                        ar_zip.extract(file_name, dest_folder)
                ar_zip.close()
                self.ar.utils.setProgress('Installing')
                
                # declare temporarily folder:
                temp_folder = dest_folder+"/"+zip_names[0]+ar_name

                # store custom presets in order to avoid overwrite them when installing the update:
                self.keep_files_when_update(dest_folder+"/"+self.ar.data.language_folder.replace(".", "/"), temp_folder+"/"+self.ar.data.language_folder.replace(".", "/"))
                self.keep_files_when_update(dest_folder+"/"+self.ar.data.curve_preset_folder.replace(".", "/"), temp_folder+"/"+self.ar.data.curve_preset_folder.replace(".", "/"))
                # keep dpPipelineInfo data
                if os.path.exists(dest_folder+"/"+self.ar.data.pipeline_folder.replace(".", "/")+"/dpPipelineSettings.json"):
                    shutil.copy2(os.path.join(dest_folder, self.ar.data.pipeline_folder.replace(".", "/")+"/dpPipelineSettings.json"), temp_folder+"/"+self.ar.data.pipeline_folder.replace(".", "/"))
                if os.path.exists(dest_folder+"/dpPipelineInfo.json"):
                    shutil.copy2(os.path.join(dest_folder, "dpPipelineInfo.json"), temp_folder)

                # remove all old live files and folders for this current version, that means delete myself, OMG!
                for each_folder in next(os.walk(dest_folder))[1]:
                    if not "-"+ar_name+"-" in each_folder:
                        shutil.rmtree(dest_folder+"/"+each_folder, ignore_errors=True)
                for each_file in next(os.walk(dest_folder))[2]:
                    os.remove(dest_folder+"/"+each_file)

                # pass in all files to copy them (doing the simple installation):
                for source_folder, folders, files in os.walk(temp_folder):       
                    # declare destination directory:
                    dest_path = source_folder.replace(temp_folder, dest_folder, 1).replace("\\", "/")
                    self.ar.utils.setProgress('Installing')
                    
                    # make sure we have all folders needed, otherwise, create them in the dest_path directory:
                    if not os.path.exists(dest_path):
                        os.makedirs(dest_path)

                    for ar_file in files:
                        source_file = os.path.join(source_folder, ar_file).replace("\\", "/")
                        dest_file = os.path.join(dest_path, ar_file).replace("\\", "/")
                        # if the file exists (we expect that yes) then delete it:
                        self.ar.utils.deleteFile(dest_file)
                        # copy the ar_file:
                        shutil.copy2(source_file, dest_path)
                        self.ar.utils.setProgress('Installing')

                # delete the temporarily folder used to download and install the update:
                shutil.rmtree(dest_folder+"/"+zip_names[0])

                # quit UI in order to force user to refresh dpAutoRigSystem creating a new instance:
                self.ar.ui_manager.delete_exist_window()
                # report finished update installation:
                button_label = self.ar.data.lang['c110_start']
                button_command = self.ar.ui_manager.reload_ui
                button_argument = None
                self.ar.logger.infoWin('i095_installUpdate', 'i099_installed', '\n\n'+new_version+'\n\n'+self.ar.data.lang['i173_reloadScript']+'\n\n'+self.ar.data.lang['i018_thanks'], 'center', 205, 270, buttonList=[button_label, button_command, button_argument])
            except Exception as e:
                # report fail update installation:
                print(self.ar.data.lang["i141_error"]+": "+e)
                self.ar.logger.infoWin('i095_installUpdate', 'e010_failInstallUpdate', '\n\n'+new_version+'\n\n'+self.ar.data.lang['i097_sorry']+'\n\n'+str(e), 'center', 205, 270)
            self.ar.utils.setProgress(endIt=True)
        else:
            print(self.ar.data.lang['i038_canceled'])


    def keep_files_when_update(self, folder, temp_folder, ext="json", *args):
        """ Check in given folder if we have custom json files and keep then when we install a new update.
            It will just check if there are user created json files, and copy them to temporarily extracted update folder.
            So when the install overwrite all files, they will be copied (restored) again.
        """
        updates = []
        # list all new json files:
        for new_root, new_directories, new_files in os.walk(temp_folder):
            for new_item in new_files:
                if new_item.endswith(f".{ext}"):
                    updates.append(new_item)
        
        # check if some current json file is a custom file created by user to copy it to new update directory in order to avoid overwrite it:
        for root, directories, current_files in os.walk(folder):
            for item in current_files:
                if item.endswith(f".{ext}"):
                    if not item in updates:
                        # found custom file, then copy it to keep it when install the new update
                        shutil.copy2(os.path.join(root, item), temp_folder)
