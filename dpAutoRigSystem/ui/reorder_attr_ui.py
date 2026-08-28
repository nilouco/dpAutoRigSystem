#import libraries
from maya import cmds
from functools import partial


class ReorderAttrUI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self, app):
        """ This is the main method to load the Reorder Attr UI.
        """
        self.app = app
        # creating dpReorderAttrUI Window:
        self.ar.utils.close_ui('dpReorderAttrWindow')
        width  = 175
        height = 75
        cmds.window('dpReorderAttrWindow', title=self.ar.data.lang["m087_reorderAttr"]+" "+str(self.ar.data.version), widthHeight=(width, height), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        cmds.columnLayout('reorder_attr_cl', columnOffset=("left", 30))
        cmds.separator(style='none', height=7, parent='reorder_attr_cl')
        cmds.button('reorder_attr_up_bt', label=self.ar.data.lang["i154_up"], annotation=self.ar.data.lang["i155_upDesc"], width=110, backgroundColor=(0.45, 1.0, 0.6), command=partial(self.app.move_attr, 1, None, None, True, True), parent='reorder_attr_cl')
        cmds.separator(style='in', height=10, width=110, parent='reorder_attr_cl')
        cmds.button('reorder_attr_down_bt', label=self.ar.data.lang["i156_down"], annotation=self.ar.data.lang["i157_downDesc"], width=110, backgroundColor=(1.0, 0.45, 0.45), command=partial(self.app.move_attr, 0, None, None, True, True), parent='reorder_attr_cl')
        # call dpReorderAttrUI Window:
        cmds.showWindow('dpReorderAttrWindow')
