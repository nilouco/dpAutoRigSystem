# importing libraries:
from maya import cmds
import datetime
import re



class Translator(object):
    def __init__(self, ar):
        """ Initialize the module class defining variables to use creating languages.
        """
        # declaring variables
        self.ar = ar
        self.translator_title = "dpAutoRigSystem - "+self.ar.data.lang['t000_translator']
        self.source_langs = list(self.ar.data.lang)
        self.key_len = len(self.source_langs) - 1
        self.lang_index_start = 7 #after userInfo
        self.lang_index = self.lang_index_start
        self.new_langs = []
        self.str_result = []
        self.check_no_special_char = re.compile('[^a-zA-Z]')
    
    
    def go_back(self, *args):
        """ Back to previews sentence translated.
        """
        if self.lang_index > 0:
            self.backward()
        else:
            cmds.button('back_bt', edit=True, enable=False, backgroundColor=(0.8, 0.8, 0.8))
    
    
    def go_same(self, *args):
        """ Get the text from source scrollField in order to use it as a translated text.
        """
        # get info from source scrollField:
        if self.lang_index <= self.key_len:
            self.new_langs[self.lang_index] = cmds.scrollField(self.source_text_sf, query=True, text=True)
            self.forward()
    
    
    def go_next(self, *args):
        """ Get the text from newLangText scrollField to use it as the user translated text.
        """
        # get info from translated scrollField:
        if self.lang_index <= self.key_len:
            validated = False
            current_text = cmds.scrollField(self.new_lang_text_sf, query=True, text=True)
            if not current_text == None:
                if not current_text == "":
                    if not current_text == " ":
                        if not current_text == self.ar.data.lang['t007_writeText']:
                            sourceText = cmds.scrollField(self.source_text_sf, query=True, text=True)
                            
                            if sourceText.startswith("\n"):
                                if not current_text.startswith("\n"):
                                    current_text = "\n"+current_text
                            elif sourceText[0].isupper():
                                current_text = current_text[0].upper()+current_text[1:]
                            elif sourceText[0].islower():
                                current_text = current_text[0].lower()+current_text[1:]
                            if sourceText.endswith("\n"):
                                if not current_text.endswith("\n"):
                                    current_text = current_text+"\n"
                            else:
                                if current_text.endswith("\n"):
                                    current_text = current_text[:-1]
                                elif sourceText.endswith("."):
                                    if not current_text.endswith("."):
                                        current_text = current_text+"."
                                elif sourceText.endswith(":"):
                                    if not current_text.endswith(":"):
                                        current_text = current_text+":"
                            
                            if self.source_langs[self.lang_index].startswith("c"): #control
                                if not self.check_no_special_char.search(current_text): #no special char
                                    validated = True
                            else:
                                validated = True
            if validated:
                self.new_langs[self.lang_index] = current_text
                self.forward()
            else:
                cmds.scrollField(self.new_lang_text_sf, edit=True, text=self.ar.data.lang['t007_writeText'])
        else:
            self.forward()
    
    
    def backward(self):
        """ Move index backward and update UI in order to load the previews translated sentence.
        """
        # edit UI buttons:
        cmds.button('back_bt', edit=True, enable=True, backgroundColor=(0.3, 0.7, 0.8))
        cmds.button('same_bt', edit=True, enable=True, backgroundColor=(0.2, 0.8, 0.9))
        cmds.button('next_bt', edit=True, enable=True, backgroundColor=(0.1, 0.9, 1.0))
        cmds.button('finish_bt', edit=True, enable=False, backgroundColor=(0.8, 0.8, 0.8))
        # return back index to get a new translated text or just for user check:
        self.lang_index -= 1
        self.update_translator_ui()
    
    
    def forward(self):
        """ Move index forward and update UI in order to get a new translated sentence.
        """
        # if finished key_len then disable Same and Next buttons and enable Finish button
        if self.lang_index == self.key_len:
            cmds.button('same_bt', edit=True, enable=False, backgroundColor=(0.8, 0.8, 0.8))
            cmds.button('next_bt', edit=True, enable=False, backgroundColor=(0.8, 0.8, 0.8))
            cmds.button('finish_bt', edit=True, enable=True, backgroundColor=(0.1, 0.9, 1.0))
        else:
            cmds.button('back_bt', edit=True, enable=True, backgroundColor=(0.3, 0.7, 0.8))
            # pass to next index to get a new translated text from user:
            self.lang_index += 1
            self.update_translator_ui()
    
    
    def go_finish(self, *args):
        """ Finish the translation process parsing the new lang string to generate json dictionary.
            Save new language json file and load it in the main dpAutoRig UI.
        """
        # parse new_langs to newLangString:
        for i, index_id in enumerate(self.source_langs):
            self.str_result += ',"'+index_id+'":"'+self.new_langs[i]+'"'
        self.str_result += "}"
        
        # avoid json fail changing "\" to "\\":
        self.str_result = self.str_result.replace("\n", "\\n")
        
        # create json file:
        result_data = self.ar.config.save_json_file(self.str_result, self.ar.data.language_folder, '_preset')
        # set this new lang as userDefined language:
        self.ar.data.lang = result_data
        self.ar.opt.set_option_var(self.ar.data.language_option_var, result_data['_preset'])
        # closes translator UI:
        self.clear_translator_ui(2)
        # show preset creation result window:
        self.ar.logger.infoWin('i149_createLanguage', 'i150_languageCreated', '\n'+result_data['_preset']+'\n\n'+self.ar.data.lang['i134_rememberPublish']+'\n\n'+self.author_name+' '+self.ar.data.lang['t008_finishMessage'].lower(), 'center', 205, 270)
        # close and reload dpAR UI in order to avoid Maya crash:
        self.ar.ui_manager.reload_ui()
    
    
    def translator_ui(self, *args):
        """ Open a serie of dialog boxes to get user input to mount a new language json dictionary.
            We show a window to translate step by step.
        """
        # give info:
        greetings_dialog = cmds.confirmDialog(
                                            title=self.ar.data.lang['t000_translator'],
                                            message=self.ar.data.lang['t001_greeting'],
                                            button=[self.ar.data.lang['i131_ok'], self.ar.data.lang['i132_cancel']],
                                            defaultButton=self.ar.data.lang['i131_ok'],
                                            cancelButton=self.ar.data.lang['i132_cancel'],
                                            dismissString=self.ar.data.lang['i132_cancel'])
        if greetings_dialog == self.ar.data.lang['i131_ok']:
            self.get_user_info_ui()
    
    
    def clear_translator_ui(self, win, *args):
        """ Check if the window exists then delete it if true.
        """
        if cmds.window('dpARTranslatorWin'+str(win), query=True, exists=True):
            cmds.deleteUI('dpARTranslatorWin'+str(win), window=True)
    
    
    def collect_user_info(self, *args):
        """ Get all inicial info from user UI in order to complete the key ids starting with "_".
            Verify if the user is trying to create a new language using the same existing name then confirm if it will be overwritten.
        """
        # get author name:
        self.author_name = cmds.textFieldGrp(self.author_tfg, query=True, text=True)
        # get email contact:
        email_name = cmds.textFieldGrp(self.email_tfg, query=True, text=True)
        # get website contact:
        website_name = cmds.textFieldGrp(self.website_tfg, query=True, text=True)
        # get language name:
        self.new_lang_name = cmds.textFieldGrp(self.new_lang_tfg, query=True, text=True)
        
        # parse user info:
        if self.author_name and self.new_lang_name:
            contact_name = ""
            if email_name and website_name:
                contact_name = email_name+"\n"+website_name
            self.new_lang_name = self.new_lang_name[0].upper()+self.new_lang_name[1:]
            date = str(datetime.datetime.now().date())
            
            # verify if we have an existing language with the same name:
            confirm_same_lang_name = self.ar.data.lang['i071_yes']
            if self.new_lang_name in self.ar.data.lang_preset_data:
                confirm_same_lang_name = cmds.confirmDialog(
                                                        title=self.ar.data.lang['t000_translator'],
                                                        message=self.ar.data.lang['i135_existingName'], 
                                                        button=[self.ar.data.lang['i071_yes'], self.ar.data.lang['i072_no']], 
                                                        defaultButton=self.ar.data.lang['i071_yes'], 
                                                        cancelButton=self.ar.data.lang['i072_no'], 
                                                        dismissString=self.ar.data.lang['i072_no'])
            if confirm_same_lang_name == self.ar.data.lang['i071_yes']:
                # starting new_langs appends:
                self.new_langs.append(self.author_name)
                self.new_langs.append(self.ar.data.lang['_collaborators'])
                self.new_langs.append(contact_name)
                self.new_langs.append(date)
                self.new_langs.append(self.new_lang_name)
                self.new_langs.append("dpTranslator v"+str(self.ar.data.version))
                self.new_langs.append(date)
                # fill new_langs it "" (nothing) in order to generate all list array and just update its values:
                for i in range(self.lang_index, self.key_len+1):
                    self.new_langs.append("empty")
                # starting result string:
                self.str_result = '{"_author":"'+self.author_name+'","_contact":"'+contact_name+'","_date":"'+date+'","_preset":"'+self.new_lang_name+'","_translator":"dpTranslator v'+str(self.ar.data.version)+'","_updated":"'+date+'"'

                self.clear_translator_ui(1)
                self.translation_lang_ui()
    
    
    def get_user_info_ui(self):
        """ First window UI to get the basic user info for sentence ids starting with "_".
        """
        self.clear_translator_ui(1)
        self.ar.ui_manager.close_ui('translator_get_info_win')
        # starting window:
        cmds.window('translator_get_info_win', title=self.translator_title, iconName='dpAutoRig', widthHeight=(500, 180), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=True)
        cmds.columnLayout('translator_get_info_cl', adjustableColumn=True, columnOffset=('both', 10), rowSpacing=10, parent='translator_get_info_win')
        cmds.separator(style='none', parent='translator_get_info_cl')
        self.author_tfg = cmds.textFieldGrp('author_tfg', label=self.ar.data.lang['t002_yourName'], text='', adjustableColumn2=1, parent='translator_get_info_cl')
        self.email_tfg = cmds.textFieldGrp('email_tfg', label=self.ar.data.lang['t003_emailContact'], text='', adjustableColumn2=1, parent='translator_get_info_cl')
        self.website_tfg = cmds.textFieldGrp('website_tfg', label=self.ar.data.lang['t004_websiteContact'], text='', adjustableColumn2=1, parent='translator_get_info_cl')
        self.new_lang_tfg = cmds.textFieldGrp('new_lang_tfg', label=self.ar.data.lang['t005_langName'], text='', adjustableColumn2=1, parent='translator_get_info_cl')
        cmds.button('startTranslationBT', label=self.ar.data.lang['t006_startTranslator'], command=self.collect_user_info, parent='translator_get_info_cl')
        # show UI:
        cmds.showWindow('translator_get_info_win')
    
    
    def update_translator_ui(self):
        """ Method to update the main UI with info from translated text, id, type, name, etc.
        """
        cmds.text('current_index_txt', edit=True, label=str(self.lang_index))
        cmds.text('key_id_txt', edit=True, label=self.source_langs[self.lang_index])
        cmds.scrollField(self.source_text_sf, edit=True, text=self.ar.data.lang[self.source_langs[self.lang_index]])
        
        if self.lang_index == self.key_len:
            cmds.scrollField(self.new_lang_text_sf, edit=True, text='')
        elif self.new_langs[self.lang_index] == "empty":
            cmds.scrollField(self.new_lang_text_sf, edit=True, text='')
        else:
            cmds.scrollField(self.new_lang_text_sf, edit=True, text=self.new_langs[self.lang_index])
        
        # case index_id for each type:
        footer_text = ""
        if self.source_langs[self.lang_index].startswith("_"):
            current_key_type = self.ar.data.lang['i013_info']
        elif self.source_langs[self.lang_index].startswith("a"):
            current_key_type = self.ar.data.lang['i153_presentation']
        elif self.source_langs[self.lang_index].startswith("b"):
            current_key_type = self.ar.data.lang['i139_bug']
        elif self.source_langs[self.lang_index].startswith("c"):
            current_key_type = self.ar.data.lang['i140_control']
            footer_text = self.ar.data.lang['i152_noSpecialChar']
        elif self.source_langs[self.lang_index].startswith("e"):
            current_key_type = self.ar.data.lang['i141_error']
        elif self.source_langs[self.lang_index].startswith("i"):
            current_key_type = self.ar.data.lang['i142_interface']
        elif self.source_langs[self.lang_index].startswith("m"):
            current_key_type = self.ar.data.lang['i143_module']
        elif self.source_langs[self.lang_index].startswith("p"):
            current_key_type = self.ar.data.lang['i144_prefix']
        elif self.source_langs[self.lang_index].startswith("t"):
            current_key_type = self.ar.data.lang['t000_translator']
        elif self.source_langs[self.lang_index].startswith("r"):
            current_key_type = self.ar.data.lang['r000_rebuilder']
        elif self.source_langs[self.lang_index].startswith("v"):
            current_key_type = self.ar.data.lang['v000_validator']
        
        # update UI elements:
        cmds.text('key_type_txt', edit=True, label=current_key_type)
        cmds.text(self.extra_info_txt, edit=True, label=footer_text)
    
    
    def translation_lang_ui(self):
        """ Show main UI in order to get user translated input texts.
            It will call update UI to start using predefined list of user info.
        """
        self.clear_translator_ui(2)
        self.ar.ui_manager.close_ui('translator_lang_win')
        # translator UI:
        cmds.window('translator_lang_win', title=self.translator_title, iconName='dpAutoRig', widthHeight=(400, 400), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=True)
        cmds.columnLayout('translator_lang_cl', adjustableColumn=True, columnOffset=('both', 10), rowSpacing=10, parent='translator_lang_win')
        cmds.separator(style='none', parent='translator_lang_cl')
        cmds.rowColumnLayout('lang_name_rcl', numberOfColumns=2, columnWidth=[(1, 70), (2, 200)], columnAlign=[(1, 'right'), (2, 'left')], columnAttach=[(1, 'right', 5), (2, 'left', 0)], parent='translator_lang_cl')
        cmds.text('langNameTxt', label=self.ar.data.lang['i151_language']+":", parent='lang_name_rcl')
        cmds.text('newLangNameTxt', label=self.new_lang_name, parent='lang_name_rcl')
        # counter:
        cmds.rowColumnLayout('counter_rcl', numberOfColumns=4, columnWidth=[(1, 70), (2, 30), (3, 10), (4, 30)], columnAlign=[(1, 'right'), (2, 'right'), (3, 'center'), (4, 'left')], columnAttach=[(1, 'right', 5), (2, 'left', 0), (3, 'left', 5), (4, 'left', 5)], parent='translator_lang_cl')
        cmds.text('sentenceTxt', label=self.ar.data.lang['i136_sentence']+":", parent='counter_rcl')
        cmds.text('current_index_txt', label='0', parent='counter_rcl')
        cmds.text('counterHifenTxt', label='/', parent='counter_rcl')
        cmds.text('keyLenTxt', label=self.key_len, parent='counter_rcl')
        # lang Key Type:
        cmds.rowColumnLayout('lang_key_type_rcl', numberOfColumns=2, columnWidth=[(1, 70), (2, 200)], columnAlign=[(1, 'right'), (2, 'left')], columnAttach=[(1, 'right', 5), (2, 'left', 0)], parent='translator_lang_cl')
        cmds.text('langKeyTypeTxt', label=self.ar.data.lang['i138_type']+":", parent='lang_key_type_rcl')
        cmds.text('key_type_txt', label='0', parent='lang_key_type_rcl')
        # lang Key ID:
        cmds.rowColumnLayout('lang_key_rcl', numberOfColumns=2, columnWidth=[(1, 70), (2, 200)], columnAlign=[(1, 'right'), (2, 'left')], columnAttach=[(1, 'right', 5), (2, 'left', 0)], parent='translator_lang_cl')
        cmds.text('langKeyIDTxt', label=self.ar.data.lang['i137_id']+":", parent='lang_key_rcl')
        cmds.text('key_id_txt', label='0', parent='lang_key_rcl')
        # translator text scrollFields:
        cmds.paneLayout('texts_pl', configuration='horizontal2', parent='translator_lang_cl')
        self.source_text_sf = cmds.scrollField('source_text_sf', editable=False, wordWrap=False, text='', parent='texts_pl')
        self.new_lang_text_sf = cmds.scrollField('new_lang_text_sf', editable=True, wordWrap=False, text='', parent='texts_pl')
        self.extra_info_txt = cmds.text('extra_info_txt', label='', parent='translator_lang_cl')
        # translator buttons:
        cmds.paneLayout('buttons_pl', configuration='vertical3', parent='translator_lang_cl')
        cmds.button('back_bt', label=self.ar.data.lang['i145_back'], backgroundColor=(0.3, 0.6, 0.7), command=self.go_back, parent='buttons_pl')
        cmds.button('same_bt', label=self.ar.data.lang['i146_same'], backgroundColor=(0.2, 0.8, 0.9), command=self.go_same, parent='buttons_pl')
        cmds.button('next_bt', label=self.ar.data.lang['i147_next'], backgroundColor=(0.1, 0.9, 1.0), command=self.go_next, parent='buttons_pl')
        cmds.button('finish_bt', label=self.ar.data.lang['i148_finish'], backgroundColor=(0.8, 0.8, 0.8), enable=False, command=self.go_finish, parent='translator_lang_cl')
        cmds.separator(style='none', parent='translator_lang_cl')
        cmds.showWindow('translator_lang_win')
        
        # update translator UI:
        self.update_translator_ui()
