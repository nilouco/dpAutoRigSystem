import os
import sys
import stat
import shutil
from maya import cmds
from maya import mel


# Required function for drag-and-drop
def onMayaDroppedPythonFile(*args):
    """ Maya installer for the dpAutoRigSystem by copying files and creating a shelf button.
    """
    try:
        installer = MayaInstaller()
        installer.define_paths()
        installer.delete_old_files()
        installer.copy_files()
        installer.create_shelf_button()
        installer.finish()
    except Exception as e:
        cmds.confirmDialog(title="Error", message=str(e))



class MayaInstaller(object):
    def __init__(self, *args):
        self.ar_name = "dpAutoRigSystem"
        self.shelf_code = f"import {self.ar_name}\nfrom {self.ar_name}.core import main\nar = main.Start()\nar.ui()"


    def define_paths(self, remove_last_folder=True):
        self.installer_folder = os.path.dirname(__file__).replace('\\', '/')
        if remove_last_folder:
            self.installer_folder = self.installer_folder[:self.installer_folder.rfind("/")] #remove '/install'
        scripts_folder = os.path.normpath(os.path.join(cmds.about(preferences=True), "../scripts")).replace('\\', '/')
        self.dp_ar_folder = os.path.join(scripts_folder, self.ar_name).replace('\\', '/')
        self.shelf_image = str(f"{self.dp_ar_folder}/icons/ar.png").replace("\\", "/")
        return self.dp_ar_folder


    def remove_readonly(self, func, path, excinfo):
        """Clear the read-only bit and retry the cleanup."""
        os.chmod(path, stat.S_IWRITE)
        func(path)


    def delete_old_files(self, folder=None):
        # remove all old live files and folders for this current version, that means delete myself, OMG!
        print("Deleting old files...")
        if not folder:
            folder = self.dp_ar_folder
        for each_file in next(os.walk(folder))[2]:
            os.remove(f"{folder}/{each_file}")
        for each_folder in next(os.walk(folder))[1]:
            if not f"-{self.ar_name}-" in each_folder:
                try:
                    shutil.rmtree(f"{folder}/{each_folder}", onexc=self.remove_readonly)
                except:
                    shutil.rmtree(f"{folder}/{each_folder}", onerror=self.remove_readonly) #for Python 3.11 and older
        print("Successfully deleted all old files.")


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
            folder = self.dp_ar_folder
        # Create or update the dpAutoRigSystem shelf button
        top_shelf = mel.eval('$tmpGL = $gShelfTopLevel')
        current_shelf = cmds.tabLayout(top_shelf, query=True, selectTab=True)
        all_buttons = cmds.shelfLayout(current_shelf, query=True, childArray=True) or []
        button_exists = False
        if all_buttons:
            for btn in all_buttons:
                if cmds.shelfButton(btn, query=True, exists=True):
                    if self.ar_name in cmds.shelfButton(btn, query=True, command=True):
                        cmds.shelfButton(
                                            btn, 
                                            edit=True, 
                                            label=self.ar_name, 
                                            annotation=self.ar_name, 
                                            imageOverlayLabel="", 
                                            image=self.shelf_image, 
                                            command=self.shelf_code, 
                                            sourceType="python"
                                        )
                        button_exists = True
        if not button_exists:
            cmds.shelfButton(
                                label=self.ar_name, 
                                annotation=self.ar_name, 
                                imageOverlayLabel="", 
                                image=self.shelf_image, 
                                command=self.shelf_code,
                                parent=current_shelf
                            )
        print("Created dpAutoRigSystem shelf button.")


    def create_folder(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    
    def finish(self):
        cmds.refresh()
        cmds.confirmDialog(title="Success", message=f"{self.ar_name} installed!")
        print(f"\n----------\nSuccessfully installed {self.ar_name}. Enjoy it, thanks!\n----------\n")
        cmds.evalDeferred(self.shelf_code, lowestPriority=True)
