#!/usr/bin/env python3

DPAR_VERSION_5 = "6.00.00"
# to make old dpAR version compatible to receive this update message
DPAR_UPDATELOG = "6.00.00 - ATTENTION !!!\n\nThere's a new dpAutoRigSystem released version.\nBut it isn't compatible with this current version 5, sorry.\nYou must download and replace all files manually.\nPlease, delete the folder and copy the new one.\nAlso, recreate your shelf button with the given code in the _shelfButton.txt\nThanks."
DPAR_VERSION_PY3 = "6.00.00 - ATTENTION !!!\n\nThere's a new dpAutoRigSystem released version.\nBut it isn't compatible with this current version 4, sorry.\nYou must download and replace all files manually.\nPlease, delete the folder and copy the new one.\nAlso, recreate your shelf button with the given code in the _shelfButton.txt\nThanks."

# Import libraries
from maya import cmds
from maya import mel


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
            #
            # WIP
            #
            print("WIP.......")
            repair = Repair()
            repair.delete_old_files()
            repair.reinstall()
            #repair.replace_shelf_button()
            repair.finish()


class Repair(object):
    def __init__(self, *args):
        print("\n----------\ndpAutoRigSystem: start repairing old version...")


    def delete_old_files(self):
        print("Deleting old files...")
        # ATTENTION to don't delete before backup me!

        print("Successfully deleted all old files.")


    def reinstall(self):
        print("Reinstalling...")

        new_version = "6"
        print(f"Successfully reinstalled to the latest version {new_version}")


    def replace_shelf_button(self):
        print("Replacing shelf button...")
        new_code = "import dpAutoRigSystem\nfrom dpAutoRigSystem.core import main\nar = main.Start()\nar.ui()"
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
                                        command=new_code, 
                                        sourceType="python"
                                    )
                    print(f"Successfully updated code for shelf button: {btn}")
                    break
        else:
            print("Not found dpAutoRigSystem shelf button.")


    def finish(self):
        print("Successfully updated dpAutoRigSystem: end repairing old version.\n----------")
