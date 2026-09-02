# importing libraries:
from maya import cmds
import time
from functools import partial



class Logger(object):
    def __init__(self, ar, ui=True, verbose=True):
        """ Initialize the module class loading variables.
        """
        # defining variables:
        self.ar = ar
        self.ar.data.verbose = verbose
        self.lang = ar.data.lang
        

    def infoWin(self, title, description, text, align, width, height, buttonList=False, wiki=None, *args):
        """ Create a window showing the text info with the description about any module.
        """
        # declaring variables:
        self.info_title       = title
        self.info_description = description
        self.info_text        = text
        self.info_winWidth    = width
        self.info_winHeight   = height
        self.info_align       = align
        # creating Info Window:
        self.ar.utils.close_ui("dpInfoWindow")
        cmds.window('dpInfoWindow', title='dpAutoRig - v'+self.ar.data.version+' - '+self.lang['i013_info']+' - '+self.lang[self.info_title], iconName='dpInfo', widthHeight=(self.info_winWidth, self.info_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
        # creating text layout:
        infoColumnLayout = cmds.columnLayout('infoColumnLayout', adjustableColumn=True, columnOffset=['both', 20], parent="dpInfoWindow")
        cmds.separator(style='none', height=10, parent=infoColumnLayout)
        infoLayout = cmds.scrollLayout('infoLayout', parent=infoColumnLayout)
        if self.info_description:
            infoDesc = cmds.text(self.lang[self.info_description], align=self.info_align, parent=infoLayout)
        if self.info_text:
            info_text = cmds.text(self.info_text, align=self.info_align, parent=infoLayout)
            if buttonList:
                if not buttonList[0] == "None":
                    cmds.button(label=buttonList[0], command=partial(buttonList[1], buttonList[2]), parent=infoLayout)
                else:
                    noneText = cmds.text(self.lang['i305_none'], align=self.info_align, parent=infoLayout)
        if wiki:
            cmds.separator(style='none', height=20, parent=infoLayout)
            cmds.button(label="Wiki", command=partial(self.ar.utils.visit_website, self.ar.data.wiki_url+wiki), backgroundColor=[1, 1, 1], align=self.info_align, parent=infoLayout)
        # call Info Window:
        cmds.showWindow("dpInfoWindow")


    def logWin(self, *args):
        """ Just create a window with all information log and print the principal result.
        """
        # create the log_text:
        log_text = self.lang['i014_logStart'] + '\n'
        log_text += str( time.asctime( time.localtime(time.time()) ) ) + '\n\n'
        # get the number of riggedModules:
        nRiggedModule = len(self.ar.maker.guides_to_rig)
        # pass for rigged module to add informations in log_text:
        if nRiggedModule != 0:
            success = 'i016_success'
            if nRiggedModule == 1:
                success = 'i015_success'
            log_text += str(nRiggedModule).zfill(3) + ' ' + self.lang[success] + ':\n\n'
            print('\ndpAutoRigSystem Log: ' + str(nRiggedModule).zfill(3) + ' ' + self.lang[success] + ', thanks!\n')
            for item in self.ar.maker.guides_to_rig:
                log_text += item.guide_namespace
                if item.custom_name:
                    log_text += " as " + item.custom_name
                log_text += '\n'
        else:
            log_text += self.lang['i017_nothing'] + '\n'
        log_text += '\n' + self.lang['i018_thanks']
        # creating a info window to show the log:
        self.infoWin('i019_log', None, log_text, 'center', 250, min((350, 150+(nRiggedModule*13))))
