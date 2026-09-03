#import libraries
from maya import cmds


class FacialConnectionUI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self, app):
        """ This is the main method to load the Facial Connection UI.
        """
        self.app = app
        self.ar.ui_manager.close_ui('dpFacialConnectionWindow')
        width  = 230
        height = 330
        cmds.window('dpFacialConnectionWindow', title=self.ar.data.lang["m085_facialConnection"]+" "+str(self.ar.data.version), widthHeight=(width, height), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)
        # creating layout:
        cmds.columnLayout('facial_connect_cl', columnOffset=("both", 10), rowSpacing=10)
        cmds.separator(height=5, style="in", horizontal=True, parent='facial_connect_cl')
        cmds.button('facial_connect_create_targets_bt', label=self.ar.data.lang['m140_createTargets'], annotation=self.ar.data.lang["m141_createTargetsDesc"], width=220, command=self.app.create_targets_from_ui, align="center", parent='facial_connect_cl')
        cmds.checkBox('facial_connect_bs_cb', label=self.ar.data.lang['m258_createBSNode'], annotation=self.ar.data.lang["m259_createBSNodeDesc"], value=1, parent='facial_connect_cl')
        cmds.checkBox('facial_connect_comb_cb', label=self.ar.data.lang['m260_combinationTargets'], annotation=self.ar.data.lang["m261_combinationTargetsDesc"], value=1, parent='facial_connect_cl')
        cmds.checkBox('facial_connect_tweak_only_cb', label=self.ar.data.lang['m262_tweakTargetOnly'], annotation=self.ar.data.lang["m263_tweakTargetOnlyDesc"], value=0, changeCommand=self.disable_combination, parent='facial_connect_cl')
        cmds.separator(height=5, style="single", horizontal=True, parent='facial_connect_cl')
        cmds.text('facial_connect_recreate_txt', label=self.ar.data.lang['m264_rebuildTargetsText'], parent='facial_connect_cl')
        cmds.button('facial_connect_recreate_bt', label=self.ar.data.lang['m265_recreateTargets'], annotation=self.ar.data.lang["m266_recreateTargetsDesc"], width=220, command=self.app.recreate_targets, parent='facial_connect_cl')
        cmds.separator(height=5, style="single", horizontal=True, parent='facial_connect_cl')
        cmds.text('facial_connect_connect_txt', label=self.ar.data.lang['m142_connectFacialAttr'], parent='facial_connect_cl')
        cmds.button('facial_connect_bs_bt', label=self.ar.data.lang['m170_blendShapes']+" - "+self.ar.data.lang['i185_animation'], annotation="Create selected facial controls.", width=220, command=self.app.connect_to_blendshape, parent='facial_connect_cl')
        cmds.button('facial_connect_joint_bt', label=self.ar.data.lang['i181_facialJoint']+" - "+self.ar.data.lang['i186_gaming'], annotation="Create default facial controls package.", width=220, command=self.app.connect_to_joints, parent='facial_connect_cl')
        # call facialControlUI Window:
        cmds.showWindow('dpFacialConnectionWindow')


    def disable_combination(self, value, *args):
        """ If the tweakTgtOnlyCB is checked, turn off and disable the combinationTgtCB.
        """
        if value:
            cmds.checkBox('facial_connect_comb_cb', edit=True, enable=False, value=False)
        else:
            cmds.checkBox('facial_connect_comb_cb', edit=True, enable=True)
