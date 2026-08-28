# importing libraries:
from maya import cmds
from maya import mel
from ..base import base
from importlib import reload

# global variables to this module:
CLASS_NAME = "Renamer"
TITLE = "m214_renamer"
DESCRIPTION = "m215_renamerDesc"
WIKI = "06-‐-Tools#-renamer"



class Renamer(base.BaseLibrary):
    def __init__(self, ar):
        base.BaseLibrary.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        if self.ar.dev:
            reload(base)
        self.sel_option = 1 #Selected
        self.originals, self.previews = [], []
        self.add_sequence = None
        self.add_prefix = None
        self.add_suffix = None
        self.search_replace = None
        self.sequence_name = None
        self.prefix_name = None
        self.suffix_name = None
        self.search_name = None
        self.replace_name = None
        self.padding = 2
        self.start = 0
        

    def build_tool(self, *args):
        # call main function
        if self.ar.data.ui_state:
            self.ar.renamer_ui.create_ui(self)
            self.ar.job.refresh_preview_win(self.ar.renamer_ui.ar.renamer_ui.refresh_preview, 'dpRenamerWin')
            self.ar.renamer_ui.ar.renamer_ui.refresh_preview()

    
    def generate_previews(self):
        """ Generate a renamed preview list used to rename the original listed items.
        """
        self.get_originals()
        if self.originals:
            self.previews = []
            preview_data = {}
            # get UI info
            self.ar.renamer_ui.get_info_from_ui()
            for i, item in enumerate(self.originals):
                if cmds.objExists(item):
                    # new:
                    new_name = item
                    if "|" in item:
                        new_name = item[item.rfind("|")+1:]
                    preview_data[item] = new_name
                    # sequence
                    if self.add_sequence:
                        preview_data[item] = self.sequence_name+str(self.start+i).zfill(self.padding)
                    # replace
                    if self.search_replace:
                        if not self.search_name == "":
                            preview_data[item] = preview_data[item].replace(self.search_name, self.replace_name)
                    if self.add_prefix:
                        preview_data[item] = self.prefix_name+preview_data[item]
                    if self.add_suffix:
                        preview_data[item] = preview_data[item]+self.suffix_name
            if preview_data:
                for item in self.originals:
                    self.previews.append(preview_data[item])
    

    def get_originals(self):
        """ Get the listed objects to rename them.
        """
        # list current selection
        self.originals = cmds.ls(selection=True)
        if self.originals:
            # check if need to add hierarchy children
            if self.sel_option == 2: #Hierarchy
                for item in self.originals:
                    try:
                        children = cmds.listRelatives(item, allDescendents=True)
                        if children:
                            for child in children:
                                if not child in self.originals:
                                    self.originals.append(child)
                    except: #more than one object with the same name
                        mel.eval("warning \""+self.ar.data.lang['i075_moreOne']+' '+self.ar.data.lang['i076_sameName']+"\";")
        return self.originals


    def run_renamer_by_ui(self, *args):
        """ Rename originals from UI info.
        """
        self.get_originals()
        if self.originals:
            self.generate_previews()
            if self.previews:
                for i, item in enumerate(self.originals):
                    if not cmds.objExists(item):
                        items = cmds.ls("*"+item+"*")
                        if items:
                            item = items[0]
                    if cmds.objExists(item):
                        cmds.rename(item, self.previews[i])
                    else:
                        mel.eval("warning \""+self.ar.data.lang['v005_cantFix']+" "+item+"\";")
            self.ar.renamer_ui.reset_ui()
            self.ar.renamer_ui.refresh_preview()
        else:
            mel.eval("warning \""+self.ar.data.lang['m225_selectAnything']+"\";")
