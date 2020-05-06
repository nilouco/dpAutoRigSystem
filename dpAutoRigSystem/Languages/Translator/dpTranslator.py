#!/usr/bin/python
# -*- coding: utf-8 -*-

# importing libraries:
import maya.cmds as cmds
import datetime
import re

DPT_VERSION = 1.2


LANGUAGES = "Languages"

class Translator:
    def __init__(self, dpUIinst, langDic, langName, *args):
        """ Initialize the module class defining variables to use creating languages.
        """
        # declaring variables
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.translatorString = "dpAutoRigSystem - "+self.langDic[self.langName]['t000_translator']
        self.sourceLangList = sorted(self.langDic[self.langName])
        self.keyLen = len(self.sourceLangList) - 1
        self.langIndexStart = 7 #after userInfo
        self.langIndex = self.langIndexStart
        self.newLangList = []
        self.resultString = None
        self.validadeNoSpecialChar = re.compile('[^a-zA-Z]')
    
    
    def dpTranslatorBack(self, *args):
        """ Back to previews sentence translated.
        """
        if self.langIndex > 0:
            self.dpTranslatorBackward()
        else:
            cmds.button(self.backBT, edit=True, enable=False, backgroundColor=(0.8, 0.8, 0.8))
    
    
    def dpTranslatorSame(self, *args):
        """ Get the text from source scrollField in order to use it as a translated text.
        """
        # get info from source scrollField:
        if self.langIndex <= self.keyLen:
            self.newLangList[self.langIndex] = cmds.scrollField(self.sourceTextSF, query=True, text=True)
            self.dpTranslatorForward()
    
    
    def dpTranslatorNext(self, *args):
        """ Get the text from newLangText scrollField to use it as the user translated text.
        """
        # get info from translated scrollField:
        if self.langIndex <= self.keyLen:
            validatedValue = False
            currentText = cmds.scrollField(self.newLangTextSF, query=True, text=True)
            if not currentText == None:
                if not currentText == "":
                    if not currentText == " ":
                        if not currentText == self.langDic[self.langName]['t007_writeText']:
                            sourceText = cmds.scrollField(self.sourceTextSF, query=True, text=True)
                            
                            if sourceText.startswith("\n"):
                                if not currentText.startswith("\n"):
                                    currentText = "\n"+currentText
                            elif sourceText[0].isupper():
                                currentText = currentText[0].upper()+currentText[1:]
                            elif sourceText[0].islower():
                                currentText = currentText[0].lower()+currentText[1:]
                            if sourceText.endswith("\n"):
                                if not currentText.endswith("\n"):
                                    currentText = currentText+"\n"
                            else:
                                if currentText.endswith("\n"):
                                    currentText = currentText[:-1]
                                elif sourceText.endswith("."):
                                    if not currentText.endswith("."):
                                        currentText = currentText+"."
                                elif sourceText.endswith(":"):
                                    if not currentText.endswith(":"):
                                        currentText = currentText+":"
                            
                            if self.sourceLangList[self.langIndex].startswith("c"): #control
                                if not self.validadeNoSpecialChar.search(currentText): #no special char
                                    validatedValue = True
                            else:
                                validatedValue = True
            if validatedValue:
                self.newLangList[self.langIndex] = currentText
                self.dpTranslatorForward()
            else:
                cmds.scrollField(self.newLangTextSF, edit=True, text=self.langDic[self.langName]['t007_writeText'])
        else:
            self.dpTranslatorForward()
    
    
    def dpTranslatorBackward(self, *args):
        """ Move index backward and update UI in order to load the previews translated sentence.
        """
        # edit UI buttons:
        cmds.button(self.backBT, edit=True, enable=True, backgroundColor=(0.3, 0.7, 0.8))
        cmds.button(self.sameBT, edit=True, enable=True, backgroundColor=(0.2, 0.8, 0.9))
        cmds.button(self.nextBT, edit=True, enable=True, backgroundColor=(0.1, 0.9, 1.0))
        cmds.button(self.finishBT, edit=True, enable=False, backgroundColor=(0.8, 0.8, 0.8))
        # return back index to get a new translated text or just for user check:
        self.langIndex -= 1
        self.dpTranslatorUpdateUI()
    
    
    def dpTranslatorForward(self, *args):
        """ Move index forward and update UI in order to get a new translated sentence.
        """
        # if finished keyLen then disable Same and Next buttons and enable Finish button
        if self.langIndex >= self.keyLen:
            cmds.button(self.sameBT, edit=True, enable=False, backgroundColor=(0.8, 0.8, 0.8))
            cmds.button(self.nextBT, edit=True, enable=False, backgroundColor=(0.8, 0.8, 0.8))
            cmds.button(self.finishBT, edit=True, enable=True, backgroundColor=(0.1, 0.9, 1.0))
        else:
            cmds.button(self.backBT, edit=True, enable=True, backgroundColor=(0.3, 0.7, 0.8))
            # pass to next index to get a new translated text from user:
            self.langIndex += 1
            self.dpTranslatorUpdateUI()
    
    
    def dpTranslatorFinish(self, *args):
        """ Finish the translation process parsing the new lang string to generate json dictionary.
            Save new language json file and load it in the main dpAutoRig UI.
        """
        # parse newLangList to newLangString:
        for i, indexID in enumerate(self.sourceLangList):
            self.resultString += ',"'+indexID+'":"'+self.newLangList[i]+'"'
        self.resultString += "}"
        
        # avoid json fail changing "\" to "\\":
        self.resultString = self.resultString.replace("\n", "\\n")
        
        # create json file:
        resultDict = self.dpUIinst.createJsonFile(self.resultString, LANGUAGES, '_language')
        # set this new lang as userDefined language:
        self.dpUIinst.langDic[resultDict['_language']] = resultDict
        self.dpUIinst.langName = resultDict['_language']
        cmds.optionVar(remove="dpAutoRigLastLanguage")
        cmds.optionVar(stringValue=("dpAutoRigLastLanguage", self.dpUIinst.langName))
        # closes translator UI:
        self.dpClearTranslatorUI(2)
        # show preset creation result window:
        self.dpUIinst.info('i149_createLanguage', 'i150_languageCreated', '\n'+self.dpUIinst.langName+'\n\n'+self.dpUIinst.langDic[self.dpUIinst.langName]['i134_rememberPublish']+'\n\n'+self.authorName+' '+self.dpUIinst.langDic[self.dpUIinst.langName]['t008_finishMessage'].lower(), 'center', 205, 270)
        # close and reload dpAR UI in order to avoide Maya crash:
        self.dpUIinst.jobReloadUI()
    
    
    def dpTranslatorMain(self, *args):
        """ Open a serie of dialog boxes to get user input to mount a new language json dictionary.
            We show a window to translate step by step.
        """
        # give info:
        greetingsDialog = cmds.confirmDialog(
                                            title=self.langDic[self.langName]['t000_translator'],
                                            message=self.langDic[self.langName]['t001_greeting'],
                                            button=[self.langDic[self.langName]['i131_ok'], self.langDic[self.langName]['i132_cancel']],
                                            defaultButton=self.langDic[self.langName]['i131_ok'],
                                            cancelButton=self.langDic[self.langName]['i132_cancel'],
                                            dismissString=self.langDic[self.langName]['i132_cancel'])
        if greetingsDialog == self.langDic[self.langName]['i131_ok']:
            self.dpGetUserInfoUI()
    
    
    def dpClearTranslatorUI(self, win, *args):
        """ Check if the window exists then delete it if true.
        """
        if cmds.window('dpARTranslatorWin'+str(win), query=True, exists=True):
            cmds.deleteUI('dpARTranslatorWin'+str(win), window=True)
    
    
    def dpCollectUserInfo(self, *args):
        """ Get all inicial info from user UI in order to complete the key ids starting with "_".
            Verify if the user is trying to create a new language using the same existing name then confirm if it will be overwritten.
        """
        # get author name:
        self.authorName = cmds.textFieldGrp(self.authorTFG, query=True, text=True)
        # get email contact:
        emailName = cmds.textFieldGrp(self.emailTFG, query=True, text=True)
        # get website contact:
        websiteName = cmds.textFieldGrp(self.websiteTFG, query=True, text=True)
        # get language name:
        self.newLangName = cmds.textFieldGrp(self.newLanguageTFG, query=True, text=True)
        
        # parse user info:
        if self.authorName and self.newLangName:
            contactName = ""
            if emailName and websiteName:
                contactName = emailName+"\n"+websiteName
            self.newLangName = self.newLangName[0].upper()+self.newLangName[1:]
            date = str(datetime.datetime.now().date())
            
            # verify if we have an existing language with the same name:
            confirmSameLangName = self.langDic[self.langName]['i071_yes']
            if self.newLangName in self.langDic:
                confirmSameLangName = cmds.confirmDialog(
                                                        title=self.langDic[self.langName]['t000_translator'],
                                                        message=self.langDic[self.langName]['i135_existingName'], 
                                                        button=[self.langDic[self.langName]['i071_yes'], self.langDic[self.langName]['i072_no']], 
                                                        defaultButton=self.langDic[self.langName]['i071_yes'], 
                                                        cancelButton=self.langDic[self.langName]['i072_no'], 
                                                        dismissString=self.langDic[self.langName]['i072_no'])
            if confirmSameLangName == self.langDic[self.langName]['i071_yes']:
                # starting newLangList appends:
                self.newLangList.append(self.authorName)
                self.newLangList.append(contactName)
                self.newLangList.append(date)
                self.newLangList.append(self.newLangName)
                self.newLangList.append("dpTranslator v"+str(DPT_VERSION))
                self.newLangList.append(date)
                # fill newLangList it "" (nothing) in order to generate all list array and just update its values:
                for i in range(self.langIndex, self.keyLen+1):
                    self.newLangList.append(None)
                print self.newLangList
                # starting result string:
                self.resultString = '{"_author":"'+self.authorName+'","_contact":"'+contactName+'","_date":"'+date+'","_language":"'+self.newLangName+'","_translator":"dpTranslator v'+str(DPT_VERSION)+'","_updated":"'+date+'"'

                self.dpClearTranslatorUI(1)
                self.dpGetLangStringUI()
    
    
    def dpGetUserInfoUI(self, *args):
        """ First window UI to get the basic user info for sentence ids starting with "_".
        """
        self.dpClearTranslatorUI(1)
        # starting window:
        dpARTranslatorWin1 = cmds.window('dpARTranslatorWin1', title=self.translatorString, iconName='dpAutoRig', widthHeight=(500, 180), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=True)
        dpARTranslatorLayout1 = cmds.columnLayout('dpARTranslatorLayout1', adjustableColumn=True, columnOffset=('both', 10), rowSpacing=10, parent=dpARTranslatorWin1)
        cmds.separator(style='none', parent=dpARTranslatorLayout1)
        self.authorTFG = cmds.textFieldGrp('authorTFG', label=self.langDic[self.langName]['t002_yourName'], text='', adjustableColumn2=1, parent=dpARTranslatorLayout1)
        self.emailTFG = cmds.textFieldGrp('emailTFG', label=self.langDic[self.langName]['t003_emailContact'], text='', adjustableColumn2=1, parent=dpARTranslatorLayout1)
        self.websiteTFG = cmds.textFieldGrp('websiteTFG', label=self.langDic[self.langName]['t004_websiteContact'], text='', adjustableColumn2=1, parent=dpARTranslatorLayout1)
        self.newLanguageTFG = cmds.textFieldGrp('newLanguageTFG', label=self.langDic[self.langName]['t005_langName'], text='', adjustableColumn2=1, parent=dpARTranslatorLayout1)
        cmds.button('startTranslationBT', label=self.langDic[self.langName]['t006_startTranslator'], command=self.dpCollectUserInfo, parent=dpARTranslatorLayout1)
        # show UI:
        cmds.showWindow(dpARTranslatorWin1)
    
    
    def dpTranslatorUpdateUI(self, *args):
        """ Method to update the main UI with info from translated text, id, type, name, etc.
        """
        cmds.text(self.curIndexTxt, edit=True, label=str(self.langIndex))
        if self.langIndex >= self.keyLen:
            cmds.text(self.keyIDTxt, edit=True, label=self.sourceLangList[self.keyLen])
        else:
            cmds.text(self.keyIDTxt, edit=True, label=self.sourceLangList[self.langIndex])
        cmds.scrollField(self.sourceTextSF, edit=True, text=self.langDic[self.langName][self.sourceLangList[self.langIndex]])
        
        if self.langIndex >= self.keyLen:
            cmds.scrollField(self.newLangTextSF, edit=True, text='')
        elif self.newLangList[self.langIndex] == None:
            cmds.scrollField(self.newLangTextSF, edit=True, text='')
        else:
            cmds.scrollField(self.newLangTextSF, edit=True, text=self.newLangList[self.langIndex])
        
        # case indexID for each type:
        footerText = ""
        if self.sourceLangList[self.langIndex].startswith("_"):
            curKeyType = self.langDic[self.langName]['i013_info']
        elif self.sourceLangList[self.langIndex].startswith("a"):
            curKeyType = self.langDic[self.langName]['i153_presentation']
        elif self.sourceLangList[self.langIndex].startswith("b"):
            curKeyType = self.langDic[self.langName]['i139_bug']
        elif self.sourceLangList[self.langIndex].startswith("c"):
            curKeyType = self.langDic[self.langName]['i140_control']
            footerText = self.langDic[self.langName]['i152_noSpecialChar']
        elif self.sourceLangList[self.langIndex].startswith("e"):
            curKeyType = self.langDic[self.langName]['i141_error']
        elif self.sourceLangList[self.langIndex].startswith("i"):
            curKeyType = self.langDic[self.langName]['i142_interface']
        elif self.sourceLangList[self.langIndex].startswith("m"):
            curKeyType = self.langDic[self.langName]['i143_module']
        elif self.sourceLangList[self.langIndex].startswith("p"):
            curKeyType = self.langDic[self.langName]['i144_prefix']
        elif self.sourceLangList[self.langIndex].startswith("t"):
            curKeyType = self.langDic[self.langName]['t000_translator']
        
        # update UI elements:
        cmds.text(self.keyTypeTxt, edit=True, label=curKeyType)
        cmds.text(self.extraInfoTxt, edit=True, label=footerText)
        
    
    
    def dpGetLangStringUI(self, *args):
        """ Show main UI in order to get user translated input texts.
            It will call update UI to start using predefined list of user info.
        """
        self.dpClearTranslatorUI(2)
        
        # translator UI:
        dpARTranslatorWin2 = cmds.window('dpARTranslatorWin2', title=self.translatorString, iconName='dpAutoRig', widthHeight=(400, 400), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=True)
        dpARTranslatorLayout = cmds.columnLayout('dpARTranslatorLayout', adjustableColumn=True, columnOffset=('both', 10), rowSpacing=10, parent=dpARTranslatorWin2)
        cmds.separator(style='none', parent=dpARTranslatorLayout)
        langNameLayout = cmds.rowColumnLayout('langNameLayout', numberOfColumns=2, columnWidth=[(1, 70), (2, 200)], columnAlign=[(1, 'right'), (2, 'left')], columnAttach=[(1, 'right', 5), (2, 'left', 0)], parent=dpARTranslatorLayout)
        cmds.text('langNameTxt', label=self.langDic[self.langName]['i151_language']+":", parent=langNameLayout)
        cmds.text('newLangNameTxt', label=self.newLangName, parent=langNameLayout)
        # counter:
        counterLayout = cmds.rowColumnLayout('counterLayout', numberOfColumns=4, columnWidth=[(1, 70), (2, 20), (3, 10), (4, 30)], columnAlign=[(1, 'right'), (2, 'left'), (3, 'center'), (4, 'left')], columnAttach=[(1, 'right', 5), (2, 'left', 0), (3, 'left', 5), (4, 'left', 5)], parent=dpARTranslatorLayout)
        cmds.text('sentenceTxt', label=self.langDic[self.langName]['i136_sentence']+":", parent=counterLayout)
        self.curIndexTxt = cmds.text('curIndexTxt', label='0', parent=counterLayout)
        cmds.text('counterHifenTxt', label='/', parent=counterLayout)
        cmds.text('keyLenTxt', label=self.keyLen, parent=counterLayout)
        # lang Key Type:
        langKeyTypeLayout = cmds.rowColumnLayout('langKeyTypeLayout', numberOfColumns=2, columnWidth=[(1, 70), (2, 200)], columnAlign=[(1, 'right'), (2, 'left')], columnAttach=[(1, 'right', 5), (2, 'left', 0)], parent=dpARTranslatorLayout)
        cmds.text('langKeyTypeTxt', label=self.langDic[self.langName]['i138_type']+":", parent=langKeyTypeLayout)
        self.keyTypeTxt = cmds.text('keyTypeTxt', label='0', parent=langKeyTypeLayout)
        # lang Key ID:
        langKeyLayout = cmds.rowColumnLayout('langKeyLayout', numberOfColumns=2, columnWidth=[(1, 70), (2, 200)], columnAlign=[(1, 'right'), (2, 'left')], columnAttach=[(1, 'right', 5), (2, 'left', 0)], parent=dpARTranslatorLayout)
        cmds.text('langKeyIDTxt', label=self.langDic[self.langName]['i137_id']+":", parent=langKeyLayout)
        self.keyIDTxt = cmds.text('keyIDTxt', label='0', parent=langKeyLayout)
        # translator text scrollFields:
        textsPL = cmds.paneLayout('textsPL', configuration='horizontal2', parent=dpARTranslatorLayout)
        self.sourceTextSF = cmds.scrollField('sourceTextSF', editable=False, wordWrap=False, text='', parent=textsPL)
        self.newLangTextSF = cmds.scrollField('newLangTextSF', editable=True, wordWrap=False, text='', parent=textsPL)
        self.extraInfoTxt = cmds.text('extraInfoTxt', label='', parent=dpARTranslatorLayout)
        # translator buttons:
        buttonsPL = cmds.paneLayout('buttonsPL', configuration='vertical3', parent=dpARTranslatorLayout)
        self.backBT = cmds.button('backBT', label=self.langDic[self.langName]['i145_back'], backgroundColor=(0.3, 0.6, 0.7), command=self.dpTranslatorBack, parent=buttonsPL)
        self.sameBT = cmds.button('sameBT', label=self.langDic[self.langName]['i146_same'], backgroundColor=(0.2, 0.8, 0.9), command=self.dpTranslatorSame, parent=buttonsPL)
        self.nextBT = cmds.button('nextBT', label=self.langDic[self.langName]['i147_next'], backgroundColor=(0.1, 0.9, 1.0), command=self.dpTranslatorNext, parent=buttonsPL)
        self.finishBT = cmds.button('finishBT', label=self.langDic[self.langName]['i148_finish'], backgroundColor=(0.8, 0.8, 0.8), enable=False, command=self.dpTranslatorFinish, parent=dpARTranslatorLayout)
        cmds.separator(style='none', parent=dpARTranslatorLayout)
        cmds.showWindow(dpARTranslatorWin2)
        
        # update translator UI:
        self.dpTranslatorUpdateUI()
        