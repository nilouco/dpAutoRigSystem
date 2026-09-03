#import libraries
from maya import cmds
from maya import mel
from functools import partial


class ZipperUI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self, app):
        """ This is the main method to load the Zipper UI.
        """
        self.app = app
        self.ar.ui_manager.close_ui('dpZipperWindow')
        width  = 380
        height = 300
        cmds.window('dpZipperWindow', title=self.app.zipper_name+" "+str(self.ar.data.version), widthHeight=(width, height), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpZipperWindow')
        # create UI layout and elements:
        cmds.columnLayout('zipper_main_cl', adjustableColumn=True, columnOffset=("left", 10))
        cmds.text('zipper_select_poly_txt', label=self.ar.data.lang['i191_selectPoly'], align="left", height=30, font='boldLabelFont', parent='zipper_main_cl')
        # original model layout:
        cmds.rowColumnLayout('zipper_model_rcl', numberOfColumns=2, columnWidth=[(1, 160), (2, 210)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 10), (2, 'both', 10)], parent='zipper_main_cl')
        cmds.button('zipper_model_bt', label=self.ar.data.lang['i187_load']+" "+self.ar.data.lang['m152_originalModel']+" >>", command=self.load_orig_model, backgroundColor=(1.0, 0.9, 0.4), parent='zipper_model_rcl')
        cmds.textField('zipper_model_tf', editable=False, parent='zipper_model_rcl')
        cmds.separator(style='in', height=15, width=100, parent='zipper_main_cl')
        # polygon edges to curves layout:
        cmds.text('zipper_select_edges_txt', label=self.ar.data.lang['i188_selectEdges'], align="left", height=30, font='boldLabelFont', parent='zipper_main_cl')
        cmds.rowColumnLayout('zipper_buttons_rcl', numberOfColumns=2, columnWidth=[(1, 160), (2, 210)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 10), (2, 'both', 10)], rowSpacing=(1, 3), parent='zipper_main_cl')
        cmds.button('zipper_first_bt', label=self.ar.data.lang['i187_load']+" "+self.ar.data.lang['c114_first']+" "+self.ar.data.lang['i189_curve']+" >>", command=partial(self.app.create_curve_from_edge, "c114_first"), backgroundColor=(1.0, 0.9, 0.4), parent='zipper_buttons_rcl')
        cmds.textField('zipper_first_tf', editable=False, parent='zipper_buttons_rcl')
        cmds.button('zipper_second_bt', label=self.ar.data.lang['i187_load']+" "+self.ar.data.lang['c115_second']+" "+self.ar.data.lang['i189_curve']+" >>", command=partial(self.app.create_curve_from_edge, "c115_second"), backgroundColor=(1.0, 0.9, 0.4), parent='zipper_buttons_rcl')
        cmds.textField('zipper_second_tf', editable=False, parent='zipper_buttons_rcl')
        cmds.separator(style='in', height=15, width=100, parent='zipper_main_cl')
        # options layout:
        cmds.text('zipper_options_txt', label=self.ar.data.lang["i002_options"]+":", height=30, font='boldLabelFont', align='left', parent='zipper_main_cl')
        cmds.columnLayout('zipper_options_cl', adjustableColumn=True, columnOffset=("left", 10), rowSpacing=3, parent='zipper_main_cl')
        cmds.radioButtonGrp('zipper_curve_direction_rb', label=self.ar.data.lang['i189_curve']+' '+self.ar.data.lang['i106_direction'], labelArray3=['X', 'Y', 'Z'], columnAlign=[(1, 'left'), (2, 'left')], columnWidth=[(1, 100), (2, 50), (3, 50), (4, 50)], adjustableColumn=4, numberOfRadioButtons=3, select=1, changeCommand=self.get_curve_direction, vertical=False, parent='zipper_options_cl')
        cmds.checkBox('zipper_good_to_dpar_cb', label=self.ar.data.lang['i190_integrateDPAR'], value=1, align='left', parent='zipper_options_cl')
        cmds.separator(style='none', height=15, width=100, parent='zipper_main_cl')
        cmds.columnLayout('zipper_create_cl', columnOffset=("left", 10), parent='zipper_main_cl')
        cmds.button('zipper_create_bt', label=self.ar.data.lang["i158_create"]+" "+self.app.zipper_name, annotation=self.ar.data.lang["i158_create"]+" "+self.app.zipper_name, command=self.app.create_zipper, width=350, backgroundColor=(0.3, 1, 0.7), parent='zipper_create_cl')
    
    
    def update_ui(self, curve_name, zipper_id):
        """ Updates zipper UI with the given curve name and refresh the button, text field and curve variable.
        """        
        if zipper_id == "c114_first":
            cmds.textField('zipper_first_tf', edit=True, text=curve_name)
            cmds.button('zipper_first_bt', edit=True, label=self.app.first_name+" "+self.ar.data.lang['i189_curve'], backgroundColor=(0.3, 0.8, 1.0))
            self.app.first_curve = curve_name
        elif zipper_id == "c115_second":
            cmds.textField('zipper_second_tf', edit=True, text=curve_name)
            cmds.button('zipper_second_bt', edit=True, label=self.app.second_name+" "+self.ar.data.lang['i189_curve'], backgroundColor=(0.3, 0.8, 1.0))
            self.app.second_curve = curve_name
    
    
    def get_curve_direction(self, *args):
        """ Read radioButtonGrp selected item from UI.
            Set curve_axis variable to be used in the curve reverse setup if needed to set up curve direction.
            Update curve_direction variable value to be "X", "Y" or "Z".
        """
        selected_item = cmds.radioButtonGrp('zipper_curve_direction_rb', query=True, select=True)
        self.app.curve_axis = selected_item-1
        if selected_item == 1:
            self.app.curve_direction = "X"
        elif selected_item == 2:
            self.app.curve_direction = "Y"
        elif selected_item == 3:
            self.app.curve_direction = "Z"
    
    
    def load_orig_model(self, *args):
        """ Load selected object as original model.
        """
        selected_nodes = cmds.ls(selection=True)
        if selected_nodes:
            if cmds.objectType(cmds.listRelatives(selected_nodes[0], children=True)[0]) == "mesh":
                cmds.textField('zipper_model_tf', edit=True, text=selected_nodes[0])
                cmds.button('zipper_model_bt', edit=True, label=self.ar.data.lang['m152_originalModel'], backgroundColor=(0.3, 0.8, 1.0))
                self.app.orig_model = selected_nodes[0]
        else:
            mel.eval('warning \"'+self.ar.data.lang['i191_selectPoly']+'\";')
