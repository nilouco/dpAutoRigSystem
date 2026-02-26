# importing libraries:
from maya import cmds
import time
from functools import partial

DP_LOGGER_VERSION = 1.02


class Logger(object):
    def __init__(self, dpUIinst, ui=True, verbose=True):
        """ Initialize the module class loading variables.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        self.ui = ui
        self.verbose = verbose
        self.lang = dpUIinst.lang
        self.utils = dpUIinst.utils
        

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
        self.dpUIinst.utils.closeUI("dpInfoWindow")
        dpInfoWin = cmds.window('dpInfoWindow', title='dpAutoRig - v'+self.dpUIinst.dpARVersion+' - '+self.lang['i013_info']+' - '+self.lang[self.info_title], iconName='dpInfo', widthHeight=(self.info_winWidth, self.info_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
        # creating text layout:
        infoColumnLayout = cmds.columnLayout('infoColumnLayout', adjustableColumn=True, columnOffset=['both', 20], parent=dpInfoWin)
        cmds.separator(style='none', height=10, parent=infoColumnLayout)
        infoLayout = cmds.scrollLayout('infoLayout', parent=infoColumnLayout)
        if self.info_description:
            infoDesc = cmds.text(self.lang[self.info_description], align=self.info_align, parent=infoLayout)
        if self.info_text:
            infoText = cmds.text(self.info_text, align=self.info_align, parent=infoLayout)
            if buttonList:
                if not buttonList[0] == "None":
                    cmds.button(label=buttonList[0], command=partial(buttonList[1], buttonList[2]), parent=infoLayout)
                else:
                    noneText = cmds.text(self.lang['i305_none'], align=self.info_align, parent=infoLayout)
        if wiki:
            cmds.separator(style='none', height=20, parent=infoLayout)
            cmds.button(label="Wiki", command=partial(self.utils.visitWebSite, self.dpUIinst.data.wiki_url+wiki), backgroundColor=[1, 1, 1], align=self.info_align, parent=infoLayout)
        # call Info Window:
        cmds.showWindow(dpInfoWin)


    def logWin(self, *args):
        """ Just create a window with all information log and print the principal result.
        """
        # create the logText:
        logText = self.lang['i014_logStart'] + '\n'
        logText += str( time.asctime( time.localtime(time.time()) ) ) + '\n\n'
        # get the number of riggedModules:
        nRiggedModule = len(self.dpUIinst.riggedModuleDic)
        # pass for rigged module to add informations in logText:
        if nRiggedModule != 0:
            if nRiggedModule == 1:
                logText += str(nRiggedModule).zfill(3) + ' ' + self.lang['i015_success'] + ':\n\n'
                print('\ndpAutoRigSystem Log: ' + str(nRiggedModule).zfill(3) + ' ' + self.lang['i015_success'] + ', thanks!\n')
            else:
                logText += str(nRiggedModule).zfill(3) + ' ' + self.lang['i016_success'] + ':\n\n'
                print('\ndpAutoRigSystem Log: ' + str(nRiggedModule).zfill(3) + ' ' + self.lang['i016_success'] + ', thanks!\n')
            riggedGuideModuleList = []
            for riggedGuideModule in self.dpUIinst.riggedModuleDic:
                riggedGuideModuleList.append(riggedGuideModule)
            riggedGuideModuleList.sort()
            for riggedGuideModule in riggedGuideModuleList:
                moduleCustomName= self.dpUIinst.riggedModuleDic[riggedGuideModule]
                if moduleCustomName == None:
                    logText += riggedGuideModule + '\n'
                else:
                    logText += riggedGuideModule + " as " + moduleCustomName + '\n'
        else:
            logText += self.lang['i017_nothing'] + '\n'
        logText += '\n' + self.lang['i018_thanks']
        
        # creating a info window to show the log:
        self.infoWin('i019_log', None, logText, 'center', 250, min((350, 150+(nRiggedModule*13))))
