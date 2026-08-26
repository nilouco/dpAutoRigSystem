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


# Import libraries
from importlib import reload
from ..library.util import utils
from ..library.util import controllers
from ..library.util import skinning
from ..library.base import standard
from ..library.base import curve
from ..library.tool import update_guides
from ..library.tool import custom_attr
from ..library.language import translator
from ..library.pipeline import pipeliner
from ..library.pipeline import publisher
from ..library.pipeline import packager
from ..library.pipeline import logger
from . import settings
from . import variables
from . import loading
from . import manager
from . import librarian
from . import filler
from . import updater
from . import maker
from . import job
from ..ui import auto_rig_ui
from ..ui import update_ui
from ..ui import donate_ui
from ..ui import pipeline_ui
from ..ui import publish_ui
from ..ui import guide_ui
from ..ui import copy_paste_attr_ui
from .. import version


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


    def load_opening(self, intro:bool=True):
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
            reload(utils)
            reload(controllers)
            reload(skinning)
            reload(standard)
            reload(curve)
            reload(update_guides)
            reload(custom_attr)
            reload(translator)
            reload(pipeliner)
            reload(publisher)
            reload(packager)
            reload(logger)
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
            reload(auto_rig_ui)
            reload(update_ui)
            reload(donate_ui)
            reload(pipeline_ui)
            reload(publish_ui)
            reload(guide_ui)
            reload(copy_paste_attr_ui)
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
        self.composer = maker.Composer(self)
        self.utils = utils.Utils(self)
        self.pipeliner = pipeliner.Pipeliner(self)
        self.packager = packager.Packager(self)
        self.ctrls = controllers.Controllers(self)
        self.publisher = publisher.Publisher(self)
        self.custom_attr = custom_attr.CustomAttr(self)
        self.skin = skinning.Skinning(self)
        self.logger = logger.Logger(self)
        self.translator = translator.Translator(self)


    def load_library(self):
        self.lib = librarian.Lib(self)
        self.filler = filler.UIFiller(self)
        self.lib.start_library()


    def load_ui(self):
        self.ui_manager = manager.UIManager(self)
        self.auto_rig_ui = auto_rig_ui.MainUI(self)
        self.update_ui = update_ui.UpdateUI(self)
        self.donate_ui = donate_ui.DonateUI(self)
        self.pipeline_ui = pipeline_ui.PipelineUI(self)
        self.publish_ui = publish_ui.PublishUI(self)
        self.guide_ui = guide_ui.GuideUI(self)
        self.copy_paste_attr_ui = copy_paste_attr_ui.CopyPasteAttrUI(self)


    def ui(self):
        self.auto_rig_ui.create_ui()
