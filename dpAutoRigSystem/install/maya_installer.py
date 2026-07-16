import os
import shutil
from maya import cmds
from maya import mel


# Required function for drag-and-drop
def onMayaDroppedPythonFile(*args):
    """ Maya installer for the dpAutoRigSystem by copying files and creating a shelf button.
    """
    try:
        installer = MayaInstaller()
        folder = installer.define_paths()
        installer.copy_files()
        installer.create_shelf_button(folder)
        installer.finish()
    except Exception as e:
        cmds.confirmDialog(title="Error", message=str(e))



class MayaInstaller(object):
    def __init__(self, *args):
        self.shelf_code = "import dpAutoRigSystem\nfrom dpAutoRigSystem.core import main\nar = main.Start()\nar.ui()"


    def define_paths(self, remove_last_folder=True):
        self.installer_folder = os.path.dirname(__file__).replace('\\', '/')
        if remove_last_folder:
            self.installer_folder = self.installer_folder[:self.installer_folder.rfind("/")] #remove '/install'
        scripts_folder = os.path.normpath(os.path.join(cmds.about(preferences=True), "../scripts"))
        self.dp_ar_folder = os.path.join(scripts_folder, 'dpAutoRigSystem')
        return self.dp_ar_folder


    def copy_files(self):
        # copy files to scripts
        self.create_folder(self.dp_ar_folder)
        for source_folder, folders, files in os.walk(self.installer_folder):       
            dest_path = source_folder.replace(self.installer_folder, self.dp_ar_folder, 1).replace("\\", "/")
            self.create_folder(dest_path)
            for ar_file in files:
                source_file = os.path.join(source_folder, ar_file).replace("\\", "/")
                shutil.copy2(source_file, dest_path)


    def create_shelf_button(self, folder=None):
        if not folder:
            folder = self.define_paths()
        # Create or update the dpAutoRigSystem shelf button
        shelf_image = str(f"{folder}/icons/ar.png").replace("\\", "/")
        top_shelf = mel.eval('$tmpGL = $gShelfTopLevel')
        current_shelf = cmds.tabLayout(top_shelf, query=True, selectTab=True)
        all_buttons = cmds.shelfLayout(current_shelf, query=True, childArray=True) or []
        button_exists = False
        if all_buttons:
            for btn in all_buttons:
                if cmds.shelfButton(btn, query=True, exists=True):
                    if "dpAutoRigSystem" in cmds.shelfButton(btn, query=True, command=True):
                        cmds.shelfButton(
                                            btn, 
                                            edit=True, 
                                            label="dpAutoRigSystem", 
                                            annotation="dpAutoRigSystem", 
                                            imageOverlayLabel="", 
                                            image=shelf_image, 
                                            command=self.shelf_code, 
                                            sourceType="python"
                                        )
                        button_exists = True
        if not button_exists:
            cmds.shelfButton(
                                label="dpAutoRigSystem", 
                                annotation="dpAutoRigSystem", 
                                imageOverlayLabel="", 
                                image=shelf_image, 
                                command=self.shelf_code,
                                parent=current_shelf
                            )
        print("Created dpAutoRigSystem shelf button.")


    def finish(self):
        cmds.refresh()
        cmds.confirmDialog(title="Success", message="dpAutoRigSystem installed!")
        print("\n----------\nSuccessfully installed dpAutoRigSystem. Enjoy it, thanks!\n----------\n")
        cmds.evalDeferred(self.shelf_code, lowestPriority=True)


    def create_folder(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)
