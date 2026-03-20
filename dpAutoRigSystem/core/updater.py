from maya import cmds


class Updater(object):
    def __init__(self, ar):
        self.ar = ar

        print("WIP... update")
        # TODO: bring update setting to here


    def load_update(self):
        print("loading updater herehre 111")


    #def load_terms_cond(self):
     #   print("loading terms and conditons here...")
        #if not self.ar.dev:
        if cmds.optionVar(exists=self.ar.data.check_update_option_var):
            if cmds.optionVar(query=self.ar.data.check_update_option_var):
                if not cmds.optionVar(query=self.ar.data.check_update_last_option_var) == self.ar.config.today:
                    #self.ar.config.get_local_data()
                    self.check_for_update()
        else:
            self.ar.opt.set_option_var(self.ar.data.check_update_option_var, 1, False)
            #self.ar.config.ask_terms_cond()
            #self.ar.config.get_local_data()
            self.check_for_update()

        self.ar.opt.set_option_var(self.ar.data.check_update_last_option_var, self.ar.config.today)



    def check_for_update(self):
        print("temp, send it to Updater class.")






        


    
    # def autoCheckOptionVar(self, checkOptVar,  lastDateOptVar, mode, *args):
    #     """ Store user choose about automatically check for update or agree terms and conditions in an optionVar.
    #         If active, try to check for update or location once a day.
    #     """
    #     firstTimeOpenDPAR = False
    #     # verify if there is an optionVar of last optionVar checkBox choose value by user in the maya system:
    #     autoCheckExists = cmds.optionVar(exists=checkOptVar)
    #     if not autoCheckExists:
    #         cmds.optionVar(intValue=(checkOptVar, 1))
    #         firstTimeOpenDPAR = True
        
    #     # get its value puting in a self variable:
    #     optVarValue = cmds.optionVar(query=checkOptVar)
    #     if mode == "update":
    #         self.userDefAutoCheckUpdate = optVarValue
    #     else: #terms
    #         self.userDefAgreeTerms = optVarValue
    #     if optVarValue == 1:
    #         # verify if there is an optionVar for store the date of the lastest optionVar ran in order to avoid many hits in the GitHub server:
    #         todayDate = str(datetime.datetime.now().date())
    #         lastAutoCheckExists = cmds.optionVar(exists=lastDateOptVar)
    #         if not lastAutoCheckExists:
    #             cmds.optionVar(stringValue=(lastDateOptVar, todayDate))
    #         # get its value puting in a variable:
    #         lastDateAutoCheck = cmds.optionVar(query=lastDateOptVar)
    #         if not lastDateAutoCheck == todayDate:
    #             cmds.optionVar(stringValue=(lastDateOptVar, todayDate))
    #             if mode == "update":
    #                 self.checkForUpdate(verbose=False)
    #             else: # agree terms and cond
    #                 self.getLocalData()
        
    #     # force checkForUpdate if it's the first time openning the dpAutoRigSystem in this computer:
    #     if firstTimeOpenDPAR:
    #         if mode == "update":
    #             self.checkForUpdate(verbose=True)
    #         else: #terms
    #             self.checkTermsAndCond()

