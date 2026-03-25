import urllib.request
from io import TextIOWrapper
from maya import cmds


class Updater(object):
    def __init__(self, ar):
        self.ar = ar

        print("WIP... update")
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

    
        print("raw_url =", self.ar.data.raw_url)



    def check_for_update(self, *args):
        """ Check if there's an update for this current script version.
            Output the result in a window.
        """
        print("\n"+self.ar.data.lang['i084_checkUpdate'])
        
        # compare current version with GitHub master
        rawResult = self.check_raw_url_for_update(self.ar.data.raw_url)
        print("rawResult =", rawResult)
        # call Update Window about rawRsult:
        if rawResult[0] == 0:
            if self.ar.data.verbose:
                self.ar.updateWin(rawResult, 'i085_updated')
        elif rawResult[0] == 1:
            self.ar.updateWin(rawResult, 'i086_newVersion')
        elif rawResult[0] == 2:
            if self.ar.data.verbose:
                self.ar.updateWin(rawResult, 'i087_rawURLFail')
        elif rawResult[0] == 3:
            if self.ar.data.verbose:
                self.ar.updateWin(rawResult, 'i088_internetFail')
        elif rawResult[0] == 4:
            if self.ar.data.verbose:
                self.ar.updateWin(rawResult, 'e008_failCheckUpdate')


        
    def check_raw_url_for_update(self, rawURL, *args):
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
        print("hehre 0000")
        try:
            gotRemoteFile = False
            # getting dpAutoRig.py file from GitHub website using the Raw URL:
            remoteSource = urllib.request.urlopen(rawURL)
            remoteContents = TextIOWrapper(remoteSource, encoding='utf-8')
            # find the line with the version and compare them:
            for line in remoteContents:
                if "DPAR_VERSION_5 = " in line:
                    gotRemoteFile = True
                    remoteVersion = line[18:-2] #these magic numbers filter only the version XX.YY.ZZ
                    if remoteVersion == self.ar.dpARVersion:
                        # 0 - the current version is up to date
                        return [0, None, None]
                    else:
                        # 1 - there's a new version
                        for extraLine in remoteContents:
                            if "DPAR_UPDATELOG = " in extraLine:
                                remoteLog = extraLine[18:-2] #these magic numbers filter only the log string sentence
                                return [1, remoteVersion, remoteLog]
                        return [1, remoteVersion, None]
            if not gotRemoteFile:
                # 2 - remote file not found using given raw url
                return [2, None, None]
        except:
            # 3 - internet connection fail (probably)
            return [3, None, None]
        # 4 - error
        return [4, None, None]



