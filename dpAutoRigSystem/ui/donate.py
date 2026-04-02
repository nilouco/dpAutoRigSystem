from functools import partial
from maya import cmds


class DonateUI(object):
    def __init__(self, ar):
        self.ar = ar


    def create_ui(self, *args):
        """ Simple window with links to donate in order to support this free and openSource code via PayPal.
        """
        # declaring variables:
        donate_title = 'dpAutoRig - v'+self.ar.data.version+' - '+self.ar.data.lang['i167_donate']
        donate_description = self.ar.data.lang['i168_donateDesc']
        donate_winWidth = 305
        donate_winHeight = 300
        donate_align = "center"
        # creating Donate Window:
        self.ar.utils.closeUI('dpDonateWindow')
        cmds.window('dpDonateWindow', title=donate_title, iconName='dpInfo', widthHeight=(donate_winWidth, donate_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False)
        # creating text layout:
        cmds.columnLayout("donate_cl", adjustableColumn=True, columnOffset=['both', 20], rowSpacing=5, parent="dpDonateWindow")
        cmds.separator(style='none', height=10, parent="donate_cl")
        infoDesc = cmds.text(donate_description, align=donate_align, parent="donate_cl")
        cmds.separator(style='none', height=10, parent="donate_cl")
        brPaypalButton = cmds.button('brlPaypalButton', label=self.ar.data.lang['i167_donate']+" - R$ - Real", align=donate_align, command=partial(self.ar.utils.visitWebSite, self.ar.data.donate_url+"BRL"), parent="donate_cl")
        #usdPaypalButton = cmds.button('usdPaypalButton', label=self.ar.data.lang['i167_donate']+" - USD - Dollar", align=donate_align, command=partial(self.ar.utils.visitWebSite, self.donateURL+"USD"), parent="donate_cl")
        # call Donate Window:
        cmds.showWindow("dpDonateWindow")