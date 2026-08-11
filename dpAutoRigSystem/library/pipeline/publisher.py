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
        # self.ar.data.lang['m046_publisher'] = self.ar.data.lang['m046_publisher']
        # self.currentAssetName = None
        # self.shortAssetName = None


    def get_file_type_by_extension(self, file_name):
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
            savedScene = self.ar.pipeliner.confirm_save_this_scene(True)
            return
        if savedScene:
            # window
            publisher_winWidth  = 450
            publisher_winHeight = 160
            cmds.window('dpPublisherWindow', title=self.ar.data.lang['m046_publisher']+" "+str(self.ar.data.version), widthHeight=(publisher_winWidth, publisher_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
            cmds.showWindow('dpPublisherWindow')
            # create UI layout and elements:
            publisherLayout = cmds.columnLayout('publisherLayout', adjustableColumn=True, columnOffset=("both", 10))
            cmds.separator(style="none", height=20, parent=publisherLayout)
            # fields
            self.filePathFBG = cmds.textFieldButtonGrp('filePathFBG', label=self.ar.data.lang['i220_filePath'], text='', buttonLabel=self.ar.data.lang['i187_load'], buttonCommand=self.user_load_file_path, adjustableColumn=2, changeCommand=self.edit_publish_path, parent=publisherLayout)
            self.fileNameTFG = cmds.textFieldGrp('fileNameTFG', label=self.ar.data.lang['i221_fileName'], text='', adjustableColumn=2, editable=True, parent=publisherLayout)
            self.commentTFG = cmds.textFieldGrp('commentTFG', label=self.ar.data.lang['i219_comments'], text='', adjustableColumn=2, editable=True, parent=publisherLayout)
            self.verifyValidatorsCB = cmds.checkBox("verifyValidatorsCB", label=self.ar.data.lang['i217_verifyChecked'], align="left", height=20, value=True, parent=publisherLayout)
            # buttons
            publisherBPLayout = cmds.paneLayout('publisherBPLayout', configuration='vertical4', paneSize=[(1, 20, 20), (2, 20, 20), (3, 45, 20), (2, 20, 20)], parent=publisherLayout)
            cmds.button(label="Pipeliner", command=partial(self.ar.pipeliner.mainUI, self.ar), parent=publisherBPLayout)
            cmds.button('diagnoseBT', label=self.ar.data.lang['i224_diagnose'], command=self.run_diagnosing, height=30, backgroundColor=(0.5, 0.5, 0.5), parent=publisherBPLayout)
            cmds.button('publishBT', label=self.ar.data.lang['i216_publish'], command=partial(self.run_publishing, True, self.ar.data.verbose), height=30, backgroundColor=(0.75, 0.75, 0.75), parent=publisherBPLayout)
            cmds.button('publishBatchBT', label=self.ar.data.lang['i358_batch'], command=partial(self.ar.pipeliner.load_asset, mode=2), height=30, backgroundColor=(0.75, 0.75, 0.75), parent=publisherBPLayout)

            # workaround to load pipeliner data correctly
            # TODO find a way to load without UI
            self.ar.pipeliner.mainUI(self.ar)
            self.ar.utils.close_ui('dpPipelinerWindow')
            self.setPublishFilePath()


    def edit_publish_path(self, *args):
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


    def user_load_file_path(self, *args):
        """ Ask user to load a file path.
        """
        dialog_result = cmds.fileDialog2(fileFilter="Maya Files (*.ma *.mb);;", fileMode=3, dialogStyle=2, okCaption=self.ar.data.lang['i187_load'])
        if dialog_result:
            self.setPublishFilePath(dialog_result[0])


    def run_checked_validators(self, first_mode=True, stop_if_found_block=True, publish_log=None):
        """ Run the verify of fix of checked validators.
        """
        validators = self.ar.config.get_validator_instances()
        if validators:
            validation_results = self.ar.ui_manager.run_selected_actions(validators, first_mode, True, stop_if_found_block, publish_log)
            if validation_results[1]: #found issue
                stopped_message = self.ar.data.lang['v020_publishStopped']+" "+validators[validation_results[2]].name                    
                return stopped_message
        return False
        

    def run_diagnosing(self, *args):
        """ Check all active validators in the verify mode and return the result in a log window.
        """
        validation_results = self.run_checked_validators() #verify mode
        if validation_results:
            mel.eval('warning \"'+validation_results+'\";')
            self.ar.utils.setProgress(endIt=True)
        else:
            validation_results = self.ar.data.lang['v007_allOk']
        self.ar.logger.infoWin('i019_log', 'i224_diagnose', validation_results, "left", 250, 150)


    def run_publishing(self, from_ui=False, verify_validator=True, comments=False, *args):
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
            - packaging the delivered files as toClient zip_file, toCloud dropbox, toHist folders
            - generate the image preview
            If it fails, it'll reopen the current file without save any change and returns False.
        """
        if self.ar.pipeliner.pipe_data['publishPath']:
            # Starting progress window
            self.ar.utils.setProgress(self.ar.data.lang['i335_starting']+"...", self.ar.data.lang['m046_publisher'], 5, add_one=False, add_number=False)

            # check if there'a a file name to publish this scene
            publish_filename = self.ar.pipeliner.get_pipe_filename(self.ar.pipeliner.pipe_data['publishPath'])
            if from_ui:
                publish_filename = cmds.textFieldGrp(self.fileNameTFG, query=True, text=True)
            if publish_filename:
                # start logging
                publish_log = {}
                publish_log["scene"] = self.ar.pipeliner.pipe_data['sceneName']
                if not publish_filename[-3:-1] == ".m":
                    publish_filename += ".m"+self.ar.pipeliner.pipe_data['sceneName'][-1]
                self.ar.pipeliner.pipe_data['publishFileName'] = publish_filename
                publish_log["published"] = self.ar.pipeliner.pipe_data['publishPath']+"/"+publish_filename
                publish_log["exportPath"] = self.ar.pipeliner.pipe_data['f_drive']+"/"+self.ar.pipeliner.pipe_data['f_studio']+"/"+self.ar.pipeliner.pipe_data['f_project']+"/"+self.ar.pipeliner.pipe_data['f_toClient']+"/"+self.ar.pipeliner.get_today()
                # comments
                publish_log["comments"] = ""
                comment_value = comments
                if from_ui and not comments:
                    comment_value = cmds.textFieldGrp(self.commentTFG, query=True, text=True)
                if comment_value:
                    publish_log["comments"] = comment_value
                
                # checking validators
                validation_results = False
                if verify_validator:
                    if from_ui:
                        verify_validator = cmds.checkBox(self.verifyValidatorsCB, query=True, value=True)
                if verify_validator:
                    validation_results = self.run_checked_validators(False, True, publish_log) #fix mode
                if validation_results:
                    self.abort_publishing(validation_results)
                    return False
                else:
                    self.ar.utils.setProgress(self.ar.data.lang['i336_storingData']+"...", add_number=False)
                    
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
                        cmds.setAttr(all_grp+".comment", comment_value, type="string")
                        # model version
                        short_name = cmds.file(query=True, sceneName=True, shortName=True)
                        if self.ar.pipeliner.pipe_data['s_model'] in short_name:
                            model_version = short_name[short_name.find(self.ar.pipeliner.pipe_data['s_model'])+len(self.ar.pipeliner.pipe_data['s_model']):]
                            model_version = int(model_version[:model_version.find("_")])
                            if not cmds.objExists(all_grp+".modelVersion"):
                                cmds.addAttr(all_grp, longName="modelVersion", attributeType="long")
                            cmds.setAttr(all_grp+".modelVersion", model_version)
                            self.ar.pipeliner.pipe_data['modelVersion'] = model_version
                        if cmds.objExists(all_grp+".system"):
                            built_version = cmds.getAttr(all_grp+".system")
                            if "dpAutoRig_" in built_version: #suport old rigged files
                                built_version = built_version.split("dpAutoRig_")[1]
                    else:
                        built_version = self.ar.data.version

                    self.ar.utils.setProgress(self.ar.data.lang['i227_getImage']+"...", add_number=False)

                    # publishing file
                    # create folders to publish file if needed
                    if not os.path.exists(self.ar.pipeliner.pipe_data['publishPath']):
                        try:
                            os.makedirs(self.ar.pipeliner.pipe_data['publishPath'])
                        except:
                            self.abort_publishing(self.ar.data.lang['v022_noFilePath'])
                            return False
                    
                    # mount folders
                    if self.ar.pipeliner.pipe_data['b_deliver']:
                        self.ar.pipeliner.mount_package_path()
                        if self.ar.pipeliner.pipe_data['toClientPath']:
                            # rigging preview image
                            if self.ar.pipeliner.pipe_data['b_imager']:
                                self.ar.pipeliner.pipe_data['imagePreviewPath'] = self.ar.packager.imager(self.ar.pipeliner.pipe_data, built_version, self.ar.pipeliner.get_today())
                                self.ar.utils.setProgress(endIt=True)
                                self.ar.utils.setProgress(self.ar.data.lang['i225_savingFile']+"...", self.ar.data.lang['m046_publisher'], 8, add_one=False, add_number=False)
                    else:
                        self.ar.utils.setProgress(self.ar.data.lang['i225_savingFile']+"...", add_number=False)
                    
                    # save published file
                    cmds.file(rename=self.ar.pipeliner.pipe_data['publishPath']+"/"+publish_filename)
                    cmds.file(save=True, type=cmds.file(query=True, type=True)[0], force=True)

                    # packager
                    if self.ar.pipeliner.pipe_data['b_deliver']:
                        if self.ar.pipeliner.pipe_data['toClientPath']:
                            # toClient
                            self.ar.utils.setProgress(self.ar.data.lang['i226_exportFiles']+"... Zipping", add_number=False)
                            zip_file = self.ar.packager.create_zip_to_client(self.ar.pipeliner.pipe_data['publishPath'], publish_filename, self.ar.pipeliner.pipe_data['toClientPath'], self.ar.pipeliner.get_today())
                            # dropbox
                            self.ar.utils.setProgress(self.ar.data.lang['i226_exportFiles']+"... Clouding", add_number=False)
                            if zip_file:
                                if self.ar.pipeliner.pipe_data['dropboxPath']:
                                    self.ar.packager.to_dropbox(zip_file, self.ar.pipeliner.pipe_data['dropboxPath'])
                            # open folder
                            self.ar.utils.setProgress(self.ar.data.lang['i226_exportFiles']+"... Folder openning", add_number=False)
                            self.ar.packager.open_folder(self.ar.pipeliner.pipe_data['toClientPath'])
                        # hist
                        if self.ar.pipeliner.pipe_data['historyPath']:
                            self.ar.utils.setProgress(self.ar.data.lang['i226_exportFiles']+"... dpHist", add_number=False)
                            self.ar.packager.to_history(self.ar.pipeliner.pipe_data['scenePath'], self.ar.pipeliner.pipe_data['shortName'], self.ar.pipeliner.pipe_data['historyPath'])
                        # organize old published files
                        if self.ar.pipeliner.asset_names:
                            self.ar.utils.setProgress(self.ar.data.lang['i226_exportFiles']+"... dpOld", add_number=False)
                            self.ar.packager.to_old(self.ar.pipeliner.pipe_data['publishPath'], publish_filename, self.ar.pipeliner.asset_names, self.ar.pipeliner.pipe_data['publishPath']+"/"+self.ar.pipeliner.pipe_data['s_old'])
                        # discord
                        if self.ar.pipeliner.pipe_data['b_discord']:
                            self.ar.utils.setProgress(self.ar.data.lang['i226_exportFiles']+"... dpLog", add_number=False)
                            message_text = self.ar.pipeliner.pipe_data["sceneName"]+"\n"+self.ar.pipeliner.pipe_data['publishPath']+"/**"+self.ar.pipeliner.pipe_data['publishFileName']+"**\n*"+self.ar.pipeliner.pipe_data["comments"]+"*"
                            result = self.ar.packager.to_discord(self.ar.pipeliner.pipe_data['publishedWebhook'], message_text)
                            if result: #error
                                print(self.ar.data.lang[result])

                    # publishing callback
                    if self.ar.pipeliner.pipe_data['s_callback']:
                        self.ar.utils.setProgress("Callback...", add_number=False)
                        if self.ar.pipeliner.pipe_data['callbackPath'] and self.ar.pipeliner.pipe_data['callbackFile']:
                            callback_result = self.ar.packager.to_callback(self.ar.pipeliner.pipe_data['callbackPath'], self.ar.pipeliner.pipe_data['callbackFile'], self.ar.pipeliner.pipe_data)
                            if callback_result:
                                print("Callback result =", callback_result)

                    # publisher log window
                    self.successPublishedWindow(publish_filename)
                    self.ar.utils.setProgress(endIt=True)
                    self.ar.utils.close_ui('dpPublisherWindow')
                    if from_ui:
                        self.ask_user_choose_file(publish_filename)

            else:
                mel.eval('warning \"'+self.ar.data.lang['v021_noFileName']+'\";')
        else:
            mel.eval('warning \"'+self.ar.data.lang['v022_noFilePath']+'\";')


    def abort_publishing(self, raison=None):
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


    def ask_user_choose_file(self, publish_filename):
        """ Ask user witch file want to open:
            1 - WIP file
            2 - Published file
        """
        wip = "1 - "+self.ar.pipeliner.pipe_data['shortName']
        pub = "2 - "+publish_filename
        result = cmds.confirmDialog(title=self.ar.data.lang['m046_publisher'], message=self.ar.data.lang['v098_askUserChooseFile'], button=[wip, pub], defaultButton=pub, cancelButton=pub, dismissString=pub)
        if result == wip:
            cmds.file(self.ar.pipeliner.pipe_data['sceneName'], open=True, force=True)


    def successPublishedWindow(self, publishedFile, errors=False, *args):
        """ If everything works well we can call a success publishing window here.
        """
        self.ar.utils.close_ui('dpSuccessPublishedWindow')
        self.ar.utils.setProgress(endIt=True)
        # window
        winWidth  = 250
        winHeight = 130
        cmds.window('dpSuccessPublishedWindow', title=self.ar.data.lang['m046_publisher']+" "+str(self.ar.data.version), widthHeight=(winWidth, winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpSuccessPublishedWindow')
        # create UI layout and elements:
        succesLayout = cmds.columnLayout('succesLayout', adjustableColumn=True, columnOffset=("both", 10))
        if publishedFile:
            cmds.separator(style="none", height=20, parent=succesLayout)
            cmds.text(label=self.ar.data.lang['v023_successPublished'], font='boldLabelFont', parent=succesLayout)
            cmds.separator(style="none", height=20, parent=succesLayout)
            cmds.text(label=publishedFile, parent=succesLayout)
        if errors:
            cmds.separator(style="in", height=20, parent=succesLayout)
            cmds.text(label=self.ar.data.lang['i141_error']+":", font='boldLabelFont', parent=succesLayout)
            cmds.text(label=self.ar.data.lang['i074_attention'], parent=succesLayout)
            cmds.separator(style="none", height=20, parent=succesLayout)
            for errorFile in errors:
                cmds.button(label=errorFile, command=partial(self.ar.pipeliner.load_asset, file=errorFile), backgroundColor=(0.95, 0.55, 0.55), parent=succesLayout)
            cmds.separator(style="none", height=20, parent=succesLayout)
        else:
            cmds.separator(style="none", height=20, parent=succesLayout)
            cmds.text(label=self.ar.data.lang['i018_thanks'], parent=succesLayout)


    def load_publishing_batch(self, path, assets=None, comments=None, *args):
        """ Load assets to batch publish them.
        """
        if path:
            published_items, errors = [], []
            if not comments:
                comments = cmds.textFieldGrp(self.ar.pipeliner.commentBatchTFG, query=True, text=True)
                if not comments:
                    comments = self.ar.data.lang['m046_publisher']+" v"+str(self.ar.data.version)
            if not comments.endswith(self.ar.data.lang['i358_batch']):
                comments = self.ar.data.lang['i358_batch']+" - "+comments
            if not assets:
                assets = [a[a.rfind("|")+1:-2] for a in self.ar.pipeliner.selectedBatchList if cmds.checkBox(a, query=True, value=True)]
            if assets:
                print(self.ar.data.lang['i335_starting']+" "+self.ar.data.lang['i358_batch']+" "+self.ar.data.lang['m046_publisher']+"...")
                print(self.ar.data.lang['i219_comments']+":", comments)
                print(self.ar.data.lang['i303_asset']+"s:", assets)
                for asset in assets:
                    self.ar.pipeliner.load_asset(path, asset)
                    publishResult = self.run_publishing(from_ui=False, comments=comments)
                    if publishResult == False:
                        errors.append(asset)
                    else:
                        published_items.append(self.ar.pipeliner.pipe_data['publishFileName'])
                if errors:
                    self.successPublishedWindow("\n".join(published_items), errors)
                else:
                    cmds.file(newFile=True, force=True)
                    self.successPublishedWindow("\n".join(published_items))
            self.ar.utils.close_ui("dpSelectAssetCBWindow")
