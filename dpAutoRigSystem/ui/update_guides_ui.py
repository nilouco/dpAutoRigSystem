#import libraries
from maya import cmds
from functools import partial


class UpdateGuidesUI(object):
    def __init__(self, ar):
        self.ar = ar
    
    
    def create_ui(self, app):
        """ This is the main method to load the Update Guides UI.
        """
        self.app = app
        self.ar.utils.close_ui('updateGuidesWindow')
        self.ar.utils.close_ui('update_summary_win')
        if self.ar.data.ui_state:
            cmds.window('updateGuidesWindow', title="Guides Info")
            cmds.columnLayout('update_guide_main_cl', adjustableColumn=1, rowSpacing=10, columnOffset=("both", 10), parent='updateGuidesWindow')
            cmds.text('update_guide_header_txt', label='DPAR '+self.ar.data.lang['m194_currentVersion']+' '+str(self.ar.data.version), height=30, align="center", parent='update_guide_main_cl')
            if len(self.app.update_data) > 0:
                cmds.scrollLayout('update_guide_sl', width=330, height=400, parent='update_guide_main_cl')
                cmds.rowColumnLayout('update_guide_base_rcl', numberOfColumns=3, columnSpacing=[(1, 0), (2, 20), (3, 20)], adjustableColumn=2, parent='update_guide_sl')
                cmds.text('update_guide_guide_txt', label=self.ar.data.lang['i205_guide'], align='center', font='boldLabelFont', height=30, parent='update_guide_base_rcl')
                cmds.text('update_guide_name_txt', label=self.ar.data.lang['m006_name'], align='center', font='boldLabelFont', parent='update_guide_base_rcl')
                cmds.text('update_guide_version_title_txt', label=self.ar.data.lang['m205_version'], align='center', font='boldLabelFont', parent='update_guide_base_rcl')
                for guide in self.app.update_data:
                    cmds.text('update_guide_node_txt', label=guide, align='left', parent='update_guide_base_rcl')
                    cmds.text('update_guide_attr_txt', label=str(self.app.update_data[guide]['attributes']['customName']), align='center', parent='update_guide_base_rcl')
                    cmds.text('update_guide_version_txt', label=self.app.update_data[guide]['attributes']['dpARVersion'], align='left', parent='update_guide_base_rcl')
                cmds.separator(style='none', height=10, parent='update_guide_base_rcl')
                cmds.button('update_guide_run_bt', label=self.ar.data.lang['m186_updateGuides'], command=self.app.do_update, backgroundColor=(0.6, 1.0, 0.7), parent='update_guide_main_cl')
            else:
                cmds.text('update_guide_nothing_txt', label=self.ar.data.lang['m188_noGuidesToUpdate'], align='left', parent='update_guide_main_cl')
            cmds.separator(style='none', height=10, parent='update_guide_main_cl')
            cmds.window('updateGuidesWindow', edit=True, height=1)
            cmds.select(clear=True)
            cmds.showWindow('updateGuidesWindow')


    def summary_ui(self):
        """ Update Guides Summary UI for log info.
        """
        self.ar.utils.close_ui('update_summary_win')
        new_data = self.app.get_new_attr()
        cmds.window('update_summary_win', title="Update Summary")
        cmds.columnLayout('summary_cl', adjustableColumn=1, rowSpacing=10, columnOffset=("both", 10), parent='update_summary_win')
        cmds.text('summary_header_txt', label=str(len(self.app.update_data))+' '+self.ar.data.lang['m189_guidesUpdatedSuccess'], align='center', height=30, parent='summary_cl')
        if new_data:
            cmds.text('summary_new_attr_found_txt', label=self.ar.data.lang['m190_newAttrFound'], align='center', parent='summary_cl')
            cmds.scrollLayout('summary_sl', width=330, height=400, parent='summary_cl')
            cmds.rowColumnLayout('summary_update_rcl', numberOfColumns=2, adjustableColumn=2, columnSpacing=[(1, 0), (2, 20)], parent='summary_sl')
            cmds.text('summary_new_guide_title_txt', label=self.ar.data.lang['i205_guide'], align='center', font='boldLabelFont', height=30, parent='summary_update_rcl')
            cmds.text('summary_new_attr_title_txt', label=self.ar.data.lang['m191_newAttr'], align='center', font='boldLabelFont', height=30, parent='summary_update_rcl')
            for guide in new_data:
                for new_attr in new_data[guide]:
                    cmds.text('summary_new_guide_txt', label=guide, align='left', parent='summary_update_rcl')
                    cmds.text('summary_new_attr_txt', label=new_attr, align='center', parent='summary_update_rcl')
        cmds.separator(style='none', height=10, parent='summary_cl')
        cmds.text('summary_ask_old_txt', label=self.ar.data.lang['m192_askOldGuides'], align='center', parent='summary_cl')
        cmds.separator(style='none', height=10, parent='summary_cl')
        cmds.button('summary_delete_old_bt', label=self.ar.data.lang['m193_deleteOldGuides'], command=self.app.do_delete, backgroundColor=(1.0, 0.6, 0.4), parent='summary_cl')
        cmds.separator(style='none', height=10, parent='summary_cl')
        cmds.showWindow('update_summary_win')
