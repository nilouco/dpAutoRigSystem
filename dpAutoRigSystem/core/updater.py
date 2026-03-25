import urllib.request
from io import TextIOWrapper
from maya import cmds


class Updater(object):
    def __init__(self, ar):
        self.ar = ar
        self.version_start_length = 21 #__version__: str = "
        self.version_end_length = -2 #"
        self.download_extension = "zip"

        print("WIP... update")
        print("raw_url =", self.ar.data.raw_url)
        # TODO: bring update setting to here


    def load_update(self):
#        if self.ar.data.ui_state and not self.ar.dev:
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
        print("raw_results =", raw_results)

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
                    print("remote_version =", remote_version)
                    print("current version =", self.ar.data.version)
                    if remote_version == self.ar.data.version:
                        # 0 - the current version is up to date
                        return [0, None, None]
                    else:
                        # 1 - there's a new version
                        for extra_line in remote_contents:
                            if "_update_log" in extra_line:
                                remote_log = extra_line[self.version_start_length:self.version_end_length] #these magic numbers filter only the log string sentence
                                print("remote_log =", remote_log)
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
                # closes dpUpdateWindow:
                self.ar.utils.closeUI('dpUpdateWindow')
            except:
                self.ar.logger.infoWin('i094_downloadUpdate', 'e009_failDownloadUpdate', folder[0]+'\n\n'+self.ar.data.lang['i097_sorry'], 'center', 205, 270)
            self.ar.utils.setProgress(endIt=True)
    

    def install(self):
        print("WIP install upadte here...")
