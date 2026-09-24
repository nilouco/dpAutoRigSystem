from functools import partial

from maya import cmds


class UpdateUI:
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self, raw_result, text):
        """ Create a window showing the text info with the description about any module.
        """
        # declaring variables:
        #checked_number = raw_result[0]
        remote_version = raw_result[1]
        remote_log = raw_result[2]
        win_width = 305
        win_height = 300
        # creating Update Window:
        self.ar.ui_manager.close_ui(self.ar.data.terms_cond_win_name)
        cmds.window(self.ar.data.terms_cond_win_name, title=f"dpAutoRigSystem - {self.ar.data.lang['i089_update']}", iconName='info', widthHeight=(win_width, win_height), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
        # creating text layout:
        cmds.columnLayout('update_cl', adjustableColumn=True, columnOffset=['both', 20], rowSpacing=5, parent=self.ar.data.terms_cond_win_name)
        cmds.text('update_description_txt', label=f"\n{self.ar.data.lang[text]}", align='center', parent='update_cl')
        cmds.text('update_current_version_txt', label=f"\n{self.ar.data.version}{self.ar.data.lang['i090_currentVersion']}", align='left', parent='update_cl')
        if remote_version:
            remote_version = remote_version.replace('\\n', '\n')
            cmds.text('update_remote_version_txt', label=f"{remote_version}{self.ar.data.lang['i091_onlineVersion']}", align='left', parent='update_cl')
            cmds.separator(height=30)
            if remote_log:
                remote_log = remote_log.replace('\\n', '\n')
                cmds.text('update_log_txt', label=f"{self.ar.data.lang['i171_updateLog']}:\n", align='center', parent='update_cl')
                cmds.text('update_remote_log_txt', label=remote_log, align='left', parent='update_cl')
                cmds.separator(height=30)
            cmds.button('update_whats_changed_bt', label=self.ar.data.lang['i117_whatsChanged'], align='center', command=partial(self.ar.web.visit_website, self.ar.data.whats_changed_url), parent='update_cl')
            cmds.button('update_visit_github_bt', label=self.ar.data.lang['i093_gotoWebSite'], align='center', command=partial(self.ar.web.visit_website, self.ar.data.github_url), parent='update_cl')
            cmds.button('update_download_bt', label=self.ar.data.lang['i094_downloadUpdate'], align='center', command=partial(self.ar.updater.download, self.ar.data.master_url, 'zip'), parent='update_cl')
            cmds.button('update_install_bt', label=self.ar.data.lang['i095_installUpdate'], align='center', command=partial(self.ar.updater.install, self.ar.data.master_url, remote_version), parent='update_cl')
        # automatically check for updates:
        cmds.separator(height=30)
        cmds.checkBox('update_auto_check_cb', label=self.ar.data.lang['i092_autoCheckUpdate'], align='left', value=self.ar.data.auto_check_update, changeCommand=self.ar.opt.set_auto_check_update, parent='update_cl')
        cmds.separator(height=30)
        # call Update Window:
        cmds.showWindow(self.ar.data.terms_cond_win_name)
