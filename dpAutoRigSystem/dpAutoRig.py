#!/usr/bin/env python3

DPAR_VERSION_5 = "6.00.00"
# to make old dpAR version compatible to receive this update message
DPAR_UPDATELOG = "6.00.00 - ATTENTION !!!\n\nThere's a new dpAutoRigSystem released version.\nBut it isn't compatible with this current version 5, sorry.\nYou must download and replace all files manually.\nPlease, delete the folder and copy the new one.\nAlso, recreate your shelf button with the given code in the _shelfButton.txt\nThanks."
DPAR_VERSION_PY3 = "6.00.00 - ATTENTION !!!\n\nThere's a new dpAutoRigSystem released version.\nBut it isn't compatible with this current version 4, sorry.\nYou must download and replace all files manually.\nPlease, delete the folder and copy the new one.\nAlso, recreate your shelf button with the given code in the _shelfButton.txt\nThanks."

# Import libraries
from maya import cmds
from maya import mel
import os
import io
import sys
import stat
import shutil
import zipfile
import urllib.request


class Start(object):
    def __init__(self, *args):
        # keep old v5 compatibility
        mel.eval(f"warning \"{DPAR_UPDATELOG.replace('\n', ' ')}\";")


    def ui(self):
        self.inform_the_user()


    def showUI(self):
        self.inform_the_user()


    def inform_the_user(self):
        """ Notify the user about the new version update.
        """
        # open dialog to confirm repair it
        yes_text = "Yes"
        no_text = "No"
        result = cmds.confirmDialog(
                                    title='Old version', 
                                    message='This is an old dpAutoRigSystem version.\n' \
                                            'You should remove it and install a new one.\n\n' \
                                            'The safest way to update it is to reinstall it manually:\n' \
                                            '1 - delete the dpAutoRigSystem folder\n' \
                                            '2 - download the files from GitHub\n' \
                                            '3 - save a new dpAutoRigSystem folder without override the old\n' \
                                            '4 - recreate the Maya shelf button\n\n' \
                                            'Otherwise, we can try to do it by pressing the "Yes" button.\n' \
                                            'Do you want to try to repair it automatically?', 
                                    button=[yes_text, no_text], 
                                    defaultButton=yes_text, 
                                    cancelButton=no_text, 
                                    dismissString=no_text
                                    )
        if result == yes_text:
            self.repair_it()
            
            
    def repair_it(self):
        repair = Repair()
        repair.delete_old_files()
        repair.reinstall()
        repair.replace_shelf_button()
        repair.finish()



class Repair(object):
    def __init__(self, *args):
        print("\n----------\ndpAutoRigSystem: start repairing old version...")
        self.ar_name = "dpAutoRigSystem"
        self.new_code = "import dpAutoRigSystem\nfrom dpAutoRigSystem.core import main\nar = main.Start()\nar.ui()"
        self.path = str(os.path.join(os.path.dirname(sys._getframe(1).f_code.co_filename))).replace("\\", "/")


    def remove_readonly(self, func, path, excinfo):
        """Clear the read-only bit and retry the cleanup."""
        os.chmod(path, stat.S_IWRITE)
        func(path)


    def delete_old_files(self):
        # remove all old live files and folders for this current version, that means delete myself, OMG!
        print("Deleting old files...")
        for each_file in next(os.walk(self.path))[2]:
            os.remove(self.path+"/"+each_file)
        for each_folder in next(os.walk(self.path))[1]:
            if not "-"+self.ar_name+"-" in each_folder:
                try:
                    shutil.rmtree(self.path+"/"+each_folder, onexc=self.remove_readonly)
                except:
                    shutil.rmtree(self.path+"/"+each_folder, onerror=self.remove_readonly) #for Python 3.11 and older
        print("Successfully deleted all old files.")


    def reinstall(self):
        print("Reinstalling...")
        #
        # TODO change URL to master after 
        #
        #url = "https://github.com/nilouco/dpAutoRigSystem/zipball/master/"
        url = "https://github.com/nilouco/dpAutoRigSystem/zipball/699-dev-mode-reload/"
        
        remote_source = urllib.request.urlopen(url)
        ar_zip = zipfile.ZipFile(io.BytesIO(remote_source.read()))
        zip_names = ar_zip.namelist()
        for file_name in zip_names:
            if f"/{self.ar_name}/" in file_name:
                ar_zip.extract(file_name, self.path)
        ar_zip.close()
        temp_folder = f"{self.path}/{zip_names[0]}{self.ar_name}"
        for source_folder, folders, files in os.walk(temp_folder):       
            dest_path = source_folder.replace(temp_folder, self.path, 1).replace("\\", "/")
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
            for ar_file in files:
                source_file = os.path.join(source_folder, ar_file).replace("\\", "/")
                shutil.copy2(source_file, dest_path)
        shutil.rmtree(f"{self.path}/{zip_names[0]}")
        from . import version
        new_version = version.__version__
        print(f"Successfully reinstalled to the latest version {new_version}")


    def replace_shelf_button(self):
        print("Replacing shelf button...")
        new_icon = "/icons/ar.png"
        top_shelf = mel.eval('$tmpGL = $gShelfTopLevel')
        current_shelf = cmds.tabLayout(top_shelf, query=True, selectTab=True)
        all_buttons = cmds.shelfLayout(current_shelf, query=True, childArray=True) or []
        if all_buttons:
            for btn in all_buttons:
                if "dpAutoRigSystem" in cmds.shelfButton(btn, query=True, command=True):
                    old_image = cmds.shelfButton(btn, query=True, image=True)
                    new_image = f"{old_image[:old_image.rfind('dpAutoRigSystem')+15]}{new_icon}"
                    cmds.shelfButton(
                                        btn, 
                                        edit=True, 
                                        image=new_image,
                                        command=self.new_code, 
                                        sourceType="python"
                                    )
                    print(f"Successfully updated code for shelf button: {btn}")
                    break
        else:
            print("Not found dpAutoRigSystem shelf button.")


    def finish(self):
        print("Successfully updated dpAutoRigSystem: end repairing old version. Thanks!\n----------\n\n")
        cmds.evalDeferred(self.new_code, lowestPriority=True)
