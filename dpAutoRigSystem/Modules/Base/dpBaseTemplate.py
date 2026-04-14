# importing libraries:
from maya import cmds
from . import dpBaseLibrary
from importlib import reload

DP_BASETEMPLATE_VERSION = 1.00


class BaseTemplate(dpBaseLibrary.BaseLibrary):
    def __init__(self, *args, **kwargs):
        dpBaseLibrary.BaseLibrary.__init__(self, *args, **kwargs)
        if self.ar.dev:
            reload(dpBaseLibrary)
        self.template_data = {}


    def ask_build_detail(self, title, options):
        """ Ask user the detail level we'll create the guides by a confirm dialog box window.
            Returns the user choose option or 'Cancel' if canceled.
        """
        option_buttons = [opt.title() for opt in options]
        user_message = self.ar.data.lang['i177_chooseMessage']
        cancel = self.ar.data.lang['i132_cancel']
        option_buttons.append(cancel)
        return cmds.confirmDialog(title=title, message=user_message, button=option_buttons, defaultButton=options[0], cancelButton=cancel, dismissString=cancel)


    def build_template(self, *args):
        template_data = self.template_data
        if "_" in self.name:
            base_name = self.name.split("_")[0]
            names, splitted = self.get_template_variations(base_name)
            if len(names) > 1:
                user_choice = self.ask_build_detail(base_name.capitalize(), splitted)
                if user_choice == self.ar.data.lang['i132_cancel']:
                    return
                template_data = self.ar.data.lib[self.ar.data.template_folder]["content"][f"{base_name}_{user_choice.lower()}"]
        guide_io = self.ar.config.get_instance("dpGuideIO", [self.ar.data.setup_folder])
        guide_io.importGuide(template_data, False)
        guide_io.setupGuideBaseParenting(template_data)
        self.ar.utils.setProgress(endIt=True)
        self.ar.ui_manager.refresh_ui()
        print(self.ar.data.lang["m089_createdTemplate"]+self.name)


    def get_template_variations(self, name):
        names, splitted = [], []
        for item in self.ar.data.lib[self.ar.data.template_folder]["templates"]:
            if item.startswith(name):
                names.append(item)
                splitted.append(item.split("_")[1])
        return names, splitted
    