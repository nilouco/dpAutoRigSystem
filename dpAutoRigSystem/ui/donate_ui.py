#import libraries
from maya import cmds
from functools import partial


class DonateUI(object):
    def __init__(self, ar):
        self.ar = ar


    def create_ui(self, *args):
        """ Simple window with links to donate in order to support this free and openSource code via PayPal.
        """
        # declaring variables:
        win_title = 'dpAutoRig - v'+self.ar.data.version+' - '+self.ar.data.lang['i167_donate']
        win_description = self.ar.data.lang['i168_donateDesc']
        win_width = 305
        win_height = 300
        win_align = "center"
        # creating Donate Window:
        self.ar.ui_manager.close_ui('dpDonateWindow')
        cmds.window('dpDonateWindow', title=win_title, iconName='dpInfo', widthHeight=(win_width, win_height), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
        # creating text layout:
        cmds.columnLayout("donate_cl", adjustableColumn=True, columnOffset=['both', 20], rowSpacing=5, parent="dpDonateWindow")
        cmds.separator(style='none', height=10, parent="donate_cl")
        cmds.text(win_description, align=win_align, parent="donate_cl")
        cmds.separator(style='none', height=10, parent="donate_cl")
        #brPaypalButton:
        cmds.button('brlPaypalButton', label=self.ar.data.lang['i167_donate']+" - R$ - Real", align=win_align, command=partial(self.ar.web.visit_website, self.ar.data.donate_url+"BRL"), parent="donate_cl")
        #usdPaypalButton = cmds.button('usdPaypalButton', label=self.ar.data.lang['i167_donate']+" - USD - Dollar", align=align, command=partial(self.ar.web.visit_website, self.donateURL+"USD"), parent="donate_cl")
        # call Donate Window:
        cmds.showWindow("dpDonateWindow")
