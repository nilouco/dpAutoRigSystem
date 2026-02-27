import os
import random
from maya import cmds

class Opening(object):
    def create_opening_ui(self, version):
        loading_message = f"Loading dpAutoRigSystem v{version} ... "
        print("\n----------")
        print(loading_message)

        path = os.path.dirname(__file__)
        rand_value = random.randint(0, 7)

        self.close_opening_ui()
        cmds.window('dpar_load_win', title='dpAutoRigSystem', iconName='dpAutoRig', widthHeight=(285, 208), menuBar=False, sizeable=False, minimizeButton=False, maximizeButton=False)
        cmds.columnLayout('dpar_load_cl')
        cmds.image('loading_image', image=(path.replace("core", "Icons").replace("\\", "/")+"/dp_loading_0%i.png" %rand_value), backgroundColor=(0.8, 0.8, 0.8), parent='dpar_load_cl')
        cmds.text('loading_text', label=loading_message, height=20, parent='dpar_load_cl')
        cmds.showWindow('dpar_load_win')
        cmds.window('dpar_load_win', edit=True, widthHeight=(285, 208))


    def close_opening_ui(self):
        if cmds.window('dpar_load_win', query=True, exists=True):
            cmds.deleteUI('dpar_load_win', window=True)