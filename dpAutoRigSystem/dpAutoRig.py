#!/usr/bin/env python3

###################################################################
#
#    dpAutoRigSystem Free Open Source Python Script for Maya
#
#    author:  Danilo Pinheiro
#
#    contact: nilouco@gmail.com
#             https://nilouco.blogspot.com
#
#    GitHub, Wiki:
#             https://github.com/nilouco/dpAutoRigSystem
#
#    Dev Sheet, Collaborators, Logs:
#             https://docs.google.com/spreadsheets/d/154HoO-bLApA7CKpIJ1bDwSxRF146Kyo2etmHDUJGdiw
#
###################################################################


DPAR_VERSION_5 = "6.00.00"
# to make old dpAR version compatible to receive this update message - it can be deleted in the future
DPAR_UPDATELOG = "6.00.00 - ATTENTION !!!\n\nThere's a new dpAutoRigSystem released version.\nBut it isn't compatible with this current version 5, sorry.\nYou must download and replace all files manually.\nPlease, delete the folder and copy the new one.\nAlso, recreate your shelf button with the given code in the _shelfButton.txt\nThanks."
DPAR_VERSION_PY3 = "6.00.00 - ATTENTION !!!\n\nThere's a new dpAutoRigSystem released version.\nBut it isn't compatible with this current version 4, sorry.\nYou must download and replace all files manually.\nPlease, delete the folder and copy the new one.\nAlso, recreate your shelf button with the given code in the _shelfButton.txt\nThanks."

# Import libraries
from importlib import reload
from .Modules.Library import dpUtils
from .Modules.Library import dpControls
from .Modules.Library import dpSkinning
from .Modules.Base import dpBaseStandard
from .Modules.Base import dpBaseLayout
from .Modules.Base import dpBaseCurve
from .Tools import dpUpdateGuides
from .Tools import dpCustomAttr
from .Languages.Translator import dpTranslator
from .Pipeline import dpPipeliner
from .Pipeline import dpPublisher
from .Pipeline import dpPackager
from .Pipeline import dpLogger
from .core import settings
from .core import variables
from .core import loading
from .core import manager
from .core import librarian
from .core import filler
from .core import updater
from .core import maker
from .core import job
from .ui import main
from .ui import update
from .ui import donate
from . import version


class Start(object):
    def __init__(self, dev:bool=False, intro:bool=True):
        self.dev: bool = dev
        self.load_opening(intro)
        self.reload_modules()
        self.load_variables()
        self.load_settings()
        self.load_components()
        self.load_library()
        self.load_ui()


    def load_opening(self, intro=True):
        """ Just create a Loading window in order to show user that it's working to open the dpAutoRigSystem.
        """
        self.opening = loading.Opening()
        if intro:
            self.opening.create_opening_ui(6) #version 6
    
    
    def reload_modules(self):
        """ Dev reloading modules.
        """ 
        if self.dev:
            print("Dev mode = True")
            reload(dpUtils)
            reload(dpControls)
            reload(dpSkinning)
            reload(dpBaseStandard)
            reload(dpBaseLayout)
            reload(dpBaseCurve)
            reload(dpUpdateGuides)
            reload(dpCustomAttr)
            reload(dpTranslator)
            reload(dpPipeliner)
            reload(dpPublisher)
            reload(dpPackager)
            reload(dpLogger)
            reload(settings)
            reload(variables)
            reload(loading)
            reload(manager)
            reload(librarian)
            reload(filler)
            reload(updater)
            reload(maker)
            reload(job)
            reload(version)
            # ui
            reload(main)
            reload(update)
            reload(donate)
            print("Reloaded imported modules")
    
    
    def load_variables(self):
        self.data = variables.Data()


    def load_settings(self):
        self.version = version
        self.config = settings.Configuration(self)
        self.opt = settings.Option(self)
        self.agree = settings.Agreement(self)
        self.updater = updater.Updater(self)
        self.job = job.Job(self)


    def load_components(self):
        self.maker = maker.Maker(self)
        self.utils = dpUtils.Utils(self)
        self.pipeliner = dpPipeliner.Pipeliner(self)
        self.packager = dpPackager.Packager(self)
        self.ctrls = dpControls.ControlClass(self)
        self.publisher = dpPublisher.Publisher(self)
        self.customAttr = dpCustomAttr.CustomAttr(self)
        self.skin = dpSkinning.Skinning(self)
        self.logger = dpLogger.Logger(self)
        self.translator = dpTranslator.Translator(self)


    def load_library(self):
        self.lib = librarian.Lib(self)
        self.filler = filler.UIFiller(self)
        self.lib.start_library()


    def load_ui(self):
        self.ui_manager = manager.UIManager(self)
        self.main_ui = main.MainUI(self)
        self.update_ui = update.UpdateUI(self)
        self.donate = donate.DonateUI(self)


    def ui(self):
        self.main_ui.create_ui()
