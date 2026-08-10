# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
import os



class Publisher(object):
    def __init__(self, ar):
        """ Initialize the module class loading variables.
        """
        # defining variables:
        self.ar = ar
        self.publisherName = self.ar.data.lang['m046_publisher']
        self.currentAssetName = None
        self.shortAssetName = None


    def getFileTypeByExtension(self, file_name, *args):
        """ Return the file type based in the extension of the given file name.
        """
        ext = file_name[-2:]
        if ext == "mb":
            return "mayaBinary"
        return "mayaAscii"


    def mainUI(self, *args):
        """ This is the main method to load the Publisher UI.
        """
        self.ar.utils.close_ui('dpSuccessPublishedWindow')
        self.ar.utils.close_ui('dpPublisherWindow')
        savedScene = self.ar.utils.checkSavedScene()
        if not savedScene:
            savedScene = self.ar.pipeliner.userSaveThisScene(True)
            return
        if savedScene:
            # window
            publisher_winWidth  = 450
            publisher_winHeight = 160
            cmds.window('dpPublisherWindow', title=self.publisherName+" "+str(self.ar.data.version), widthHeight=(publisher_winWidth, publisher_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
            cmds.showWindow('dpPublisherWindow')
            # create UI layout and elements:
            publisherLayout = cmds.columnLayout('publisherLayout', adjustableColumn=True, columnOffset=("both", 10))
            cmds.separator(style="none", height=20, parent=publisherLayout)
            # fields
            self.filePathFBG = cmds.textFieldButtonGrp('filePathFBG', label=self.ar.data.lang['i220_filePath'], text='', buttonLabel=self.ar.data.lang['i187_load'], buttonCommand=self.userLoadFilePath, adjustableColumn=2, changeCommand=self.editPublishPath, parent=publisherLayout)
            self.fileNameTFG = cmds.textFieldGrp('fileNameTFG', label=self.ar.data.lang['i221_fileName'], text='', adjustableColumn=2, editable=True, parent=publisherLayout)
            self.commentTFG = cmds.textFieldGrp('commentTFG', label=self.ar.data.lang['i219_comments'], text='', adjustableColumn=2, editable=True, parent=publisherLayout)
            self.verifyValidatorsCB = cmds.checkBox("verifyValidatorsCB", label=self.ar.data.lang['i217_verifyChecked'], align="left", height=20, value=True, parent=publisherLayout)
            # buttons
            publisherBPLayout = cmds.paneLayout('publisherBPLayout', configuration='vertical4', paneSize=[(1, 20, 20), (2, 20, 20), (3, 45, 20), (2, 20, 20)], parent=publisherLayout)
            cmds.button(label="Pipeliner", command=partial(self.ar.pipeliner.mainUI, self.ar), parent=publisherBPLayout)
            cmds.button('diagnoseBT', label=self.ar.data.lang['i224_diagnose'], command=self.runDiagnosing, height=30, backgroundColor=(0.5, 0.5, 0.5), parent=publisherBPLayout)
            cmds.button('publishBT', label=self.ar.data.lang['i216_publish'], command=partial(self.runPublishing, True, self.ar.data.verbose), height=30, backgroundColor=(0.75, 0.75, 0.75), parent=publisherBPLayout)
            cmds.button('publishBatchBT', label=self.ar.data.lang['i358_batch'], command=partial(self.ar.pipeliner.load_asset, mode=2), height=30, backgroundColor=(0.75, 0.75, 0.75), parent=publisherBPLayout)

            # workaround to load pipeliner data correctly
            # TODO find a way to load without UI
            self.ar.pipeliner.mainUI(self.ar)
            self.ar.utils.close_ui('dpPipelinerWindow')
            self.setPublishFilePath()


    def editPublishPath(self, *args):
        """ Set the current publish path as the entered text in the textField.
        """
        self.ar.pipeliner.pipe_data['publishPath'] = cmds.textFieldButtonGrp(self.filePathFBG, query=True, text=True)


    def setPublishFilePath(self, file_path=None, *args):
        """ Set the publish file path and return it.
        """
        if not file_path:
            # try to load a pipeline structure to get the file_path to set it up
            file_path = self.ar.pipeliner.load_publish_path()
        if file_path:
            try:
                cmds.textFieldButtonGrp(self.filePathFBG, edit=True, text=str(file_path))
                cmds.textFieldGrp(self.fileNameTFG, edit=True, text=str(self.ar.pipeliner.get_pipe_filename(file_path)))
                self.ar.pipeliner.pipe_data['publishPath'] = file_path
            except:
                pass
        return file_path


    def userLoadFilePath(self, *args):
        """ Ask user to load a file path.
        """
        dialogResult = cmds.fileDialog2(fileFilter="Maya Files (*.ma *.mb);;", fileMode=3, dialogStyle=2, okCaption=self.ar.data.lang['i187_load'])
        if dialogResult:
            self.setPublishFilePath(dialogResult[0])

    

    def runCheckedValidators(self, first_mode=True, stop_if_found_block=True, publish_log=None, *args):
        """ Run the verify of fix of checked validators.
        """
        validators = self.ar.config.get_validator_instances()
        if validators:
            validationResultDataList = self.ar.ui_manager.run_selected_actions(validators, first_mode, True, stop_if_found_block, publish_log)
            if validationResultDataList[1]: #found issue
                stoppedMessage = self.ar.data.lang['v020_publishStopped']+" "+validators[validationResultDataList[2]].name                    
                return stoppedMessage
        return False
        

    def runDiagnosing(self, *args):
        """ Check all active validators in the verify mode and return the result in a log window.
        """
        validatorsResult = self.runCheckedValidators() #verify mode
        if validatorsResult:
            mel.eval('warning \"'+validatorsResult+'\";')
            self.ar.utils.setProgress(endIt=True)
        else:
            validatorsResult = self.ar.data.lang['v007_allOk']
        self.ar.logger.infoWin('i019_log', 'i224_diagnose', validatorsResult, "left", 250, 150)


    def runPublishing(self, fromUI, verifyValidator=True, comments=False, *args):
        """ Start the publishing process
            - use dpPipeliner.pipe_data info to publish the current file
            - check if there's a publish path to export the file
            - check if there's a file name to publish the file
            - get comments to log
            - run validators in a fix mode (or not)
            - store data info like publishedFromFile and model version into the All_Grp if it exists
            - create the folders to publish file if them not exists yet
            - save the published file
            - backup old published file version in the dpOld folder
            - packaging the delivered files as toClient zipFile, toCloud dropbox, toHist folders
            - generate the image preview
            If it fails, it'll reopen the current file without save any change and returns False.
        """
        if self.ar.pipeliner.pipe_data['publishPath']:
            # Starting progress window
            self.ar.utils.setProgress(self.ar.data.lang['i335_starting']+"...", self.publisherName, 5, addOne=False, addNumber=False)

            # check if there'a a file name to publish this scene
            publishFileName = self.ar.pipeliner.get_pipe_filename(self.ar.pipeliner.pipe_data['publishPath'])
            if fromUI:
                publishFileName = cmds.textFieldGrp(self.fileNameTFG, query=True, text=True)
            if publishFileName:
                # start logging
                publish_log = {}
                publish_log["scene"] = self.ar.pipeliner.pipe_data['sceneName']
                if not publishFileName[-3:-1] == ".m":
                    publishFileName += ".m"+self.ar.pipeliner.pipe_data['sceneName'][-1]
                self.ar.pipeliner.pipe_data['publishFileName'] = publishFileName
                publish_log["published"] = self.ar.pipeliner.pipe_data['publishPath']+"/"+publishFileName
                publish_log["exportPath"] = self.ar.pipeliner.pipe_data['f_drive']+"/"+self.ar.pipeliner.pipe_data['f_studio']+"/"+self.ar.pipeliner.pipe_data['f_project']+"/"+self.ar.pipeliner.pipe_data['f_toClient']+"/"+self.ar.pipeliner.get_today()
                # comments
                publish_log["comments"] = ""
                commentValue = comments
                if fromUI and not comments:
                    commentValue = cmds.textFieldGrp(self.commentTFG, query=True, text=True)
                if commentValue:
                    publish_log["comments"] = commentValue
                
                # checking validators
                validatorsResult = False
                if verifyValidator:
                    if fromUI:
                        verifyValidator = cmds.checkBox(self.verifyValidatorsCB, query=True, value=True)
                if verifyValidator:
                    validatorsResult = self.runCheckedValidators(False, True, publish_log) #fix mode
                if validatorsResult:
                    self.abortPublishing(validatorsResult)
                    return False
                else:
                    self.ar.utils.setProgress(self.ar.data.lang['i336_storingData']+"...", addNumber=False)
                    
                    self.ar.pipeliner.pipe_data.update(publish_log)

                    # try to store data into All_Grp if it exists
                    self.ar.pipeliner.pipe_data['modelVersion'] = None
                    all_grp = self.ar.utils.getAllGrp()
                    if all_grp:
                        # published from file
                        if not cmds.objExists(all_grp+".publishedFromFile"):
                            cmds.addAttr(all_grp, longName="publishedFromFile", dataType="string")
                        cmds.setAttr(all_grp+".publishedFromFile", self.ar.pipeliner.pipe_data['sceneName'], type="string")
                        # asset name
                        if not cmds.objExists(all_grp+".assetName"):
                            cmds.addAttr(all_grp, longName="assetName", dataType="string")
                        cmds.setAttr(all_grp+".assetName", self.ar.pipeliner.pipe_data['assetName'], type="string")
                        # comments
                        if not cmds.objExists(all_grp+".comment"):
                            cmds.addAttr(all_grp, longName="comment", dataType="string")
                        cmds.setAttr(all_grp+".comment", commentValue, type="string")
                        # model version
                        shortName = cmds.file(query=True, sceneName=True, shortName=True)
                        if self.ar.pipeliner.pipe_data['s_model'] in shortName:
                            modelVersion = shortName[shortName.find(self.ar.pipeliner.pipe_data['s_model'])+len(self.ar.pipeliner.pipe_data['s_model']):]
                            modelVersion = int(modelVersion[:modelVersion.find("_")])
                            if not cmds.objExists(all_grp+".modelVersion"):
                                cmds.addAttr(all_grp, longName="modelVersion", attributeType="long")
                            cmds.setAttr(all_grp+".modelVersion", modelVersion)
                            self.ar.pipeliner.pipe_data['modelVersion'] = modelVersion
                        if cmds.objExists(all_grp+".system"):
                            builtVersion = cmds.getAttr(all_grp+".system")
                            if "dpAutoRig_" in builtVersion: #suport old rigged files
                                builtVersion = builtVersion.split("dpAutoRig_")[1]
                    else:
                        builtVersion = self.ar.data.version

                    self.ar.utils.setProgress(self.ar.data.lang['i227_getImage']+"...", addNumber=False)

                    # publishing file
                    # create folders to publish file if needed
                    if not os.path.exists(self.ar.pipeliner.pipe_data['publishPath']):
                        try:
                            os.makedirs(self.ar.pipeliner.pipe_data['publishPath'])
                        except:
                            self.abortPublishing(self.ar.data.lang['v022_noFilePath'])
                            return False
                    
                    # mount folders
                    if self.ar.pipeliner.pipe_data['b_deliver']:
                        self.ar.pipeliner.mount_package_path()
                        if self.ar.pipeliner.pipe_data['toClientPath']:
                            # rigging preview image
                            if self.ar.pipeliner.pipe_data['b_imager']:
                                self.ar.pipeliner.pipe_data['imagePreviewPath'] = self.ar.packager.imager(self.ar.pipeliner.pipe_data, builtVersion, self.ar.pipeliner.get_today())
                                self.ar.utils.setProgress(endIt=True)
                                self.ar.utils.setProgress(self.ar.data.lang['i225_savingFile']+"...", self.publisherName, 8, addOne=False, addNumber=False)
                    else:
                        self.ar.utils.setProgress(self.ar.data.lang['i225_savingFile']+"...", addNumber=False)
                    
                    # save published file
                    cmds.file(rename=self.ar.pipeliner.pipe_data['publishPath']+"/"+publishFileName)
                    cmds.file(save=True, type=cmds.file(query=True, type=True)[0], force=True)

                    # packager
                    if self.ar.pipeliner.pipe_data['b_deliver']:
                        if self.ar.pipeliner.pipe_data['toClientPath']:
                            # toClient
                            self.ar.utils.setProgress(self.ar.data.lang['i226_exportFiles']+"... Zipping", addNumber=False)
                            zipFile = self.ar.packager.create_zip_to_client(self.ar.pipeliner.pipe_data['publishPath'], publishFileName, self.ar.pipeliner.pipe_data['toClientPath'], self.ar.pipeliner.get_today())
                            # dropbox
                            self.ar.utils.setProgress(self.ar.data.lang['i226_exportFiles']+"... Clouding", addNumber=False)
                            if zipFile:
                                if self.ar.pipeliner.pipe_data['dropboxPath']:
                                    self.ar.packager.to_dropbox(zipFile, self.ar.pipeliner.pipe_data['dropboxPath'])
                            # open folder
                            self.ar.utils.setProgress(self.ar.data.lang['i226_exportFiles']+"... Folder openning", addNumber=False)
                            self.ar.packager.open_folder(self.ar.pipeliner.pipe_data['toClientPath'])
                        # hist
                        if self.ar.pipeliner.pipe_data['historyPath']:
                            self.ar.utils.setProgress(self.ar.data.lang['i226_exportFiles']+"... dpHist", addNumber=False)
                            self.ar.packager.to_history(self.ar.pipeliner.pipe_data['scenePath'], self.ar.pipeliner.pipe_data['shortName'], self.ar.pipeliner.pipe_data['historyPath'])
                        # organize old published files
                        if self.ar.pipeliner.assetNameList:
                            self.ar.utils.setProgress(self.ar.data.lang['i226_exportFiles']+"... dpOld", addNumber=False)
                            self.ar.packager.to_old(self.ar.pipeliner.pipe_data['publishPath'], publishFileName, self.ar.pipeliner.assetNameList, self.ar.pipeliner.pipe_data['publishPath']+"/"+self.ar.pipeliner.pipe_data['s_old'])
                        # discord
                        if self.ar.pipeliner.pipe_data['b_discord']:
                            self.ar.utils.setProgress(self.ar.data.lang['i226_exportFiles']+"... dpLog", addNumber=False)
                            messageText = self.ar.pipeliner.pipe_data["sceneName"]+"\n"+self.ar.pipeliner.pipe_data['publishPath']+"/**"+self.ar.pipeliner.pipe_data['publishFileName']+"**\n*"+self.ar.pipeliner.pipe_data["comments"]+"*"
                            result = self.ar.packager.to_discord(self.ar.pipeliner.pipe_data['publishedWebhook'], messageText)
                            if result: #error
                                print(self.ar.data.lang[result])

                    # publishing callback
                    if self.ar.pipeliner.pipe_data['s_callback']:
                        self.ar.utils.setProgress("Callback...", addNumber=False)
                        if self.ar.pipeliner.pipe_data['callbackPath'] and self.ar.pipeliner.pipe_data['callbackFile']:
                            callbackResult = self.ar.packager.to_callback(self.ar.pipeliner.pipe_data['callbackPath'], self.ar.pipeliner.pipe_data['callbackFile'], self.ar.pipeliner.pipe_data)
                            if callbackResult:
                                print("Callback result =", callbackResult)

                    # publisher log window
                    self.successPublishedWindow(publishFileName)
                    self.ar.utils.setProgress(endIt=True)
                    self.ar.utils.close_ui('dpPublisherWindow')
                    if fromUI:
                        self.askUserChooseFile(publishFileName)

            else:
                mel.eval('warning \"'+self.ar.data.lang['v021_noFileName']+'\";')
        else:
            mel.eval('warning \"'+self.ar.data.lang['v022_noFilePath']+'\";')


    def abortPublishing(self, raison=None, *args):
        """ Stop the publishing process because we found an error somewhere.
            Reopen the rig file.
            Log error in a window.
            End progressWindow.
            Warning the raison of the error.
        """
        self.ar.utils.setProgress(endIt=True)
        self.ar.utils.close_ui('dpPublisherWindow')
        # reopen current file
        cmds.file(self.ar.pipeliner.pipe_data['sceneName'], open=True, force=True)
        # report the error in a log window
        if raison:
            self.ar.logger.infoWin('i019_log', 'i216_publish', raison, "left", 250, 150)
            mel.eval('warning \"'+raison+'\";')


    def askUserChooseFile(self, publishFileName, *args):
        """ Ask user witch file want to open:
            1 - WIP file
            2 - Published file
        """
        optWip = "1 - "+self.ar.pipeliner.pipe_data['shortName']
        optPub = "2 - "+publishFileName
        result = cmds.confirmDialog(title=self.publisherName, message=self.ar.data.lang['v098_askUserChooseFile'], button=[optWip, optPub], defaultButton=optPub, cancelButton=optPub, dismissString=optPub)
        if result == optWip:
            cmds.file(self.ar.pipeliner.pipe_data['sceneName'], open=True, force=True)


    def successPublishedWindow(self, publishedFile, errorList=False, *args):
        """ If everything works well we can call a success publishing window here.
        """
        self.ar.utils.close_ui('dpSuccessPublishedWindow')
        self.ar.utils.setProgress(endIt=True)
        # window
        winWidth  = 250
        winHeight = 130
        cmds.window('dpSuccessPublishedWindow', title=self.publisherName+" "+str(self.ar.data.version), widthHeight=(winWidth, winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpSuccessPublishedWindow')
        # create UI layout and elements:
        succesLayout = cmds.columnLayout('succesLayout', adjustableColumn=True, columnOffset=("both", 10))
        if publishedFile:
            cmds.separator(style="none", height=20, parent=succesLayout)
            cmds.text(label=self.ar.data.lang['v023_successPublished'], font='boldLabelFont', parent=succesLayout)
            cmds.separator(style="none", height=20, parent=succesLayout)
            cmds.text(label=publishedFile, parent=succesLayout)
        if errorList:
            cmds.separator(style="in", height=20, parent=succesLayout)
            cmds.text(label=self.ar.data.lang['i141_error']+":", font='boldLabelFont', parent=succesLayout)
            cmds.text(label=self.ar.data.lang['i074_attention'], parent=succesLayout)
            cmds.separator(style="none", height=20, parent=succesLayout)
            for errorFile in errorList:
                cmds.button(label=errorFile, command=partial(self.ar.pipeliner.load_asset, file=errorFile), backgroundColor=(0.95, 0.55, 0.55), parent=succesLayout)
            cmds.separator(style="none", height=20, parent=succesLayout)
        else:
            cmds.separator(style="none", height=20, parent=succesLayout)
            cmds.text(label=self.ar.data.lang['i018_thanks'], parent=succesLayout)


    def loadPublishingBatch(self, path, assetList=None, comments=None, *args):
        """ Load assets to batch publish them.
        """
        if path:
            publishedList, errorList = [], []
            if not comments:
                comments = cmds.textFieldGrp(self.ar.pipeliner.commentBatchTFG, query=True, text=True)
                if not comments:
                    comments = self.ar.data.lang['m046_publisher']+" v"+str(self.ar.data.version)
            if not comments.endswith(self.ar.data.lang['i358_batch']):
                comments = self.ar.data.lang['i358_batch']+" - "+comments
            if not assetList:
                assetList = [a[a.rfind("|")+1:-2] for a in self.ar.pipeliner.selectedBatchList if cmds.checkBox(a, query=True, value=True)]
            if assetList:
                print(self.ar.data.lang['i335_starting']+" "+self.ar.data.lang['i358_batch']+" "+self.ar.data.lang['m046_publisher']+"...")
                print(self.ar.data.lang['i219_comments']+":", comments)
                print(self.ar.data.lang['i303_asset']+"s:", assetList)
                for asset in assetList:
                    self.ar.pipeliner.load_asset(path, asset)
                    publishResult = self.runPublishing(fromUI=False, comments=comments)
                    if publishResult == False:
                        errorList.append(asset)
                    else:
                        publishedList.append(self.ar.pipeliner.pipe_data['publishFileName'])
                if errorList:
                    self.successPublishedWindow("\n".join(publishedList), errorList)
                else:
                    cmds.file(newFile=True, force=True)
                    self.successPublishedWindow("\n".join(publishedList))
            self.ar.utils.close_ui("dpSelectAssetCBWindow")
