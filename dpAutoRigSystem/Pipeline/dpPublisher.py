# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
import os

DP_PUBLISHER_VERSION = 1.9


class Publisher(object):
    def __init__(self, dpUIinst, ui=True, verbose=True):
        """ Initialize the module class loading variables.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        self.ui = ui
        self.verbose = verbose
        self.publisherName = self.dpUIinst.lang['m046_publisher']
        self.currentAssetName = None
        self.shortAssetName = None
        self.utils = dpUIinst.utils
        self.pipeliner = dpUIinst.pipeliner
        self.packager = dpUIinst.packager


    def getFileTypeByExtension(self, fileName, *args):
        """ Return the file type based in the extension of the given file name.
        """
        ext = fileName[-2:]
        if ext == "mb":
            return "mayaBinary"
        return "mayaAscii"


    def mainUI(self, *args):
        """ This is the main method to load the Publisher UI.
        """
        self.ui = True
        self.utils.closeUI('dpSuccessPublishedWindow')
        self.utils.closeUI('dpPublisherWindow')
        savedScene = self.utils.checkSavedScene()
        if not savedScene:
            savedScene = self.dpUIinst.pipeliner.userSaveThisScene(True)
            return
        if savedScene:
            # window
            publisher_winWidth  = 450
            publisher_winHeight = 200
            cmds.window('dpPublisherWindow', title=self.publisherName+" "+str(DP_PUBLISHER_VERSION), widthHeight=(publisher_winWidth, publisher_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
            cmds.showWindow('dpPublisherWindow')
            # create UI layout and elements:
            publisherLayout = cmds.columnLayout('publisherLayout', adjustableColumn=True, columnOffset=("both", 10))
            cmds.separator(style="none", height=20, parent=publisherLayout)
            # fields
            self.filePathFBG = cmds.textFieldButtonGrp('filePathFBG', label=self.dpUIinst.lang['i220_filePath'], text='', buttonLabel=self.dpUIinst.lang['i187_load'], buttonCommand=self.userLoadFilePath, adjustableColumn=2, changeCommand=self.editPublishPath, parent=publisherLayout)
            self.fileNameTFG = cmds.textFieldGrp('fileNameTFG', label=self.dpUIinst.lang['i221_fileName'], text='', adjustableColumn=2, editable=True, parent=publisherLayout)
            self.commentTFG = cmds.textFieldGrp('commentTFG', label=self.dpUIinst.lang['i219_comments'], text='', adjustableColumn=2, editable=True, parent=publisherLayout)
            self.verifyValidatorsCB = cmds.checkBox("verifyValidatorsCB", label=self.dpUIinst.lang['i217_verifyChecked'], align="left", height=20, value=True, parent=publisherLayout)
            # buttons
            publisherBPLayout = cmds.paneLayout('publisherBPLayout', configuration='vertical3', paneSize=[(1, 20, 20), (2, 20, 20), (3, 50, 20)], parent=publisherLayout)
            cmds.button(label="Pipeliner", command=partial(self.pipeliner.mainUI, self.dpUIinst), parent=publisherBPLayout)
            cmds.button('diagnoseBT', label=self.dpUIinst.lang['i224_diagnose'], command=partial(self.runDiagnosing), height=30, backgroundColor=(0.5, 0.5, 0.5), parent=publisherBPLayout)
            cmds.button('publishBT', label=self.dpUIinst.lang['i216_publish'], command=partial(self.runPublishing, self.ui, self.verbose), height=30, backgroundColor=(0.75, 0.75, 0.75), parent=publisherBPLayout)

            # workaround to load pipeliner data correctly
            # TODO find a way to load without UI
            self.pipeliner.mainUI(self.dpUIinst)
            self.utils.closeUI('dpPipelinerWindow')
            self.setPublishFilePath()


    def editPublishPath(self, *args):
        """ Set the current publish path as the entered text in the textField.
        """
        self.pipeliner.pipeData['publishPath'] = cmds.textFieldButtonGrp(self.filePathFBG, query=True, text=True)


    def setPublishFilePath(self, filePath=None, *args):
        """ Set the publish file path and return it.
        """
        if not filePath:
            # try to load a pipeline structure to get the filePath to set it up
            filePath = self.pipeliner.loadPublishPath()
        if filePath:
            try:
                cmds.textFieldButtonGrp(self.filePathFBG, edit=True, text=str(filePath))
                cmds.textFieldGrp(self.fileNameTFG, edit=True, text=str(self.pipeliner.getPipeFileName(filePath)))
                self.pipeliner.pipeData['publishPath'] = filePath
            except:
                pass
        return filePath


    def userLoadFilePath(self, *args):
        """ Ask user to load a file path.
        """
        dialogResult = cmds.fileDialog2(fileFilter="Maya Files (*.ma *.mb);;", fileMode=3, dialogStyle=2, okCaption=self.dpUIinst.lang['i187_load'])
        if dialogResult:
            self.setPublishFilePath(dialogResult[0])


    def getRigWIPVersion(self, *args):
        """ Find the rig version by scene name and return it.
        """
        rigWipVersion = 0
        shortName = cmds.file(query=True, sceneName=True, shortName=True)
        if self.pipeliner.pipeData['s_rig'] in shortName:
            rigWipVersion = shortName[shortName.rfind(self.pipeliner.pipeData['s_rig'])+len(self.pipeliner.pipeData['s_rig']):shortName.rfind(".")]
        return rigWipVersion
    

    def runCheckedValidators(self, firstMode=True, stopIfFoundBlock=True, publishLog=None, *args):
        """ Run the verify of fix of checked validators.
        """
        toCheckValidatorList = self.dpUIinst.checkAddOnsInstanceList
        toCheckValidatorList.extend(self.dpUIinst.checkInInstanceList)
        toCheckValidatorList.extend(self.dpUIinst.checkOutInstanceList)
        toCheckValidatorList.extend(self.dpUIinst.checkFinishingInstanceList)
        if toCheckValidatorList:
            validationResultDataList = self.dpUIinst.runSelectedActions(toCheckValidatorList, firstMode, True, stopIfFoundBlock, publishLog)
            if validationResultDataList[1]: #found issue
                stoppedMessage = self.dpUIinst.lang['v020_publishStopped']+" "+toCheckValidatorList[validationResultDataList[2]].guideModuleName                    
                return stoppedMessage
        return False
        

    def runDiagnosing(self, *args):
        """ Check all active validators in the verify mode and return the result in a log window.
        """
        validatorsResult = self.runCheckedValidators() #verify mode
        if validatorsResult:
            mel.eval('warning \"'+validatorsResult+'\";')
            self.utils.setProgress(endIt=True)
        else:
            validatorsResult = self.dpUIinst.lang['v007_allOk']
        self.dpUIinst.logger.infoWin('i019_log', 'i224_diagnose', validatorsResult, "left", 250, 150)


    def runPublishing(self, fromUI, verifyValidator=True, comments=False, *args):
        """ Start the publishing process
            - use dpPipeliner.pipeData info to publish the current file
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
            If it fails, it'll reopen the current file without save any change.
        """
        if self.pipeliner.pipeData['publishPath']:
            # Starting progress window
            self.utils.setProgress(self.dpUIinst.lang['i335_starting']+"...", self.publisherName, 5, addOne=False, addNumber=False)

            # check if there'a a file name to publish this scene
            publishFileName = self.pipeliner.getPipeFileName(self.pipeliner.pipeData['publishPath'])
            if fromUI:
                publishFileName = cmds.textFieldGrp(self.fileNameTFG, query=True, text=True)
            if publishFileName:
                # start logging
                publishLog = {}
                publishLog["scene"] = self.pipeliner.pipeData['sceneName']
                if not publishFileName[-3:-1] == ".m":
                    publishFileName += ".m"+self.pipeliner.pipeData['sceneName'][-1]
                self.pipeliner.pipeData['publishFileName'] = publishFileName
                publishLog["published"] = self.pipeliner.pipeData['publishPath']+"/"+publishFileName
                publishLog["exportPath"] = self.pipeliner.pipeData['f_drive']+"/"+self.pipeliner.pipeData['f_studio']+"/"+self.pipeliner.pipeData['f_project']+"/"+self.pipeliner.pipeData['f_toClient']+"/"+self.pipeliner.getToday()
                # comments
                publishLog["comments"] = ""
                commentValue = comments
                if fromUI and not comments:
                    commentValue = cmds.textFieldGrp(self.commentTFG, query=True, text=True)
                if commentValue:
                    publishLog["comments"] = commentValue
                
                # checking validators
                validatorsResult = False
                if verifyValidator:
                    if fromUI:
                        verifyValidator = cmds.checkBox(self.verifyValidatorsCB, query=True, value=True)
                if verifyValidator:
                    validatorsResult = self.runCheckedValidators(False, True, publishLog) #fix mode
                if validatorsResult:
                    self.abortPublishing(validatorsResult)
                else:
                    self.utils.setProgress(self.dpUIinst.lang['i336_storingData']+"...", addNumber=False)
                    
                    self.pipeliner.pipeData.update(publishLog)

                    # try to store data into All_Grp if it exists
                    self.pipeliner.pipeData['modelVersion'] = None
                    if not self.dpUIinst.checkIfNeedCreateAllGrp():
                        # published from file
                        if not cmds.objExists(self.dpUIinst.masterGrp+".publishedFromFile"):
                            cmds.addAttr(self.dpUIinst.masterGrp, longName="publishedFromFile", dataType="string")
                        cmds.setAttr(self.dpUIinst.masterGrp+".publishedFromFile", self.pipeliner.pipeData['sceneName'], type="string")
                        # asset name
                        if not cmds.objExists(self.dpUIinst.masterGrp+".assetName"):
                            cmds.addAttr(self.dpUIinst.masterGrp, longName="assetName", dataType="string")
                        cmds.setAttr(self.dpUIinst.masterGrp+".assetName", self.pipeliner.pipeData['assetName'], type="string")
                        # comments
                        if not cmds.objExists(self.dpUIinst.masterGrp+".comment"):
                            cmds.addAttr(self.dpUIinst.masterGrp, longName="comment", dataType="string")
                        cmds.setAttr(self.dpUIinst.masterGrp+".comment", commentValue, type="string")
                        # model version
                        shortName = cmds.file(query=True, sceneName=True, shortName=True)
                        if self.pipeliner.pipeData['s_model'] in shortName:
                            modelVersion = shortName[shortName.find(self.pipeliner.pipeData['s_model'])+len(self.pipeliner.pipeData['s_model']):]
                            modelVersion = int(modelVersion[:modelVersion.find("_")])
                            if not cmds.objExists(self.dpUIinst.masterGrp+".modelVersion"):
                                cmds.addAttr(self.dpUIinst.masterGrp, longName="modelVersion", attributeType="long")
                            cmds.setAttr(self.dpUIinst.masterGrp+".modelVersion", modelVersion)
                            self.pipeliner.pipeData['modelVersion'] = modelVersion
                        if cmds.objExists(self.dpUIinst.masterGrp+".system"):
                            builtVersion = cmds.getAttr(self.dpUIinst.masterGrp+".system")
                            if "dpAutoRig_" in builtVersion: #suport old rigged files
                                builtVersion = builtVersion.split("dpAutoRig_")[1]
                    else:
                        builtVersion = self.dpUIinst.dpARVersion

                    self.utils.setProgress(self.dpUIinst.lang['i227_getImage']+"...", addNumber=False)

                    # publishing file
                    # create folders to publish file if needed
                    if not os.path.exists(self.pipeliner.pipeData['publishPath']):
                        try:
                            os.makedirs(self.pipeliner.pipeData['publishPath'])
                        except:
                            self.abortPublishing(self.dpUIinst.lang['v022_noFilePath'])
                            return
                    
                    # mount folders
                    if self.pipeliner.pipeData['b_deliver']:
                        self.pipeliner.mountPackagePath()
                        if self.pipeliner.pipeData['toClientPath']:
                            # rigging preview image
                            if self.pipeliner.pipeData['b_imager']:
                                self.pipeliner.pipeData['imagePreviewPath'] = self.packager.imager(self.pipeliner.pipeData, builtVersion, self.pipeliner.getToday())
                                self.utils.setProgress(endIt=True)
                                self.utils.setProgress(self.dpUIinst.lang['i225_savingFile']+"...", self.publisherName, 8, addOne=False, addNumber=False)
                    else:
                        self.utils.setProgress(self.dpUIinst.lang['i225_savingFile']+"...", addNumber=False)
                    
                    # save published file
                    cmds.file(rename=self.pipeliner.pipeData['publishPath']+"/"+publishFileName)
                    cmds.file(save=True, type=cmds.file(query=True, type=True)[0], force=True)

                    # packager
                    if self.pipeliner.pipeData['b_deliver']:
                        if self.pipeliner.pipeData['toClientPath']:
                            # toClient
                            self.utils.setProgress(self.dpUIinst.lang['i226_exportFiles']+"... Zipping", addNumber=False)
                            zipFile = self.packager.zipToClient(self.pipeliner.pipeData['publishPath'], publishFileName, self.pipeliner.pipeData['toClientPath'], self.pipeliner.getToday())
                            # dropbox
                            self.utils.setProgress(self.dpUIinst.lang['i226_exportFiles']+"... Clouding", addNumber=False)
                            if zipFile:
                                if self.pipeliner.pipeData['dropboxPath']:
                                    self.packager.toDropbox(zipFile, self.pipeliner.pipeData['dropboxPath'])
                            # open folder
                            self.utils.setProgress(self.dpUIinst.lang['i226_exportFiles']+"... Folder openning", addNumber=False)
                            self.packager.openFolder(self.pipeliner.pipeData['toClientPath'])
                        # hist
                        if self.pipeliner.pipeData['historyPath']:
                            self.utils.setProgress(self.dpUIinst.lang['i226_exportFiles']+"... dpHist", addNumber=False)
                            self.packager.toHistory(self.pipeliner.pipeData['scenePath'], self.pipeliner.pipeData['shortName'], self.pipeliner.pipeData['historyPath'])
                        # organize old published files
                        if self.pipeliner.assetNameList:
                            self.utils.setProgress(self.dpUIinst.lang['i226_exportFiles']+"... dpOld", addNumber=False)
                            self.packager.toOld(self.pipeliner.pipeData['publishPath'], publishFileName, self.pipeliner.assetNameList, self.pipeliner.pipeData['publishPath']+"/"+self.pipeliner.pipeData['s_old'])
                        # discord
                        if self.pipeliner.pipeData['b_discord']:
                            self.utils.setProgress(self.dpUIinst.lang['i226_exportFiles']+"... dpLog", addNumber=False)
                            messageText = self.pipeliner.pipeData["sceneName"]+"\n"+self.pipeliner.pipeData['publishPath']+"/**"+self.pipeliner.pipeData['publishFileName']+"**\n*"+self.pipeliner.pipeData["comments"]+"*"
                            result = self.packager.toDiscord(self.pipeliner.pipeData['publishedWebhook'], messageText)
                            if result: #error
                                print(self.dpUIinst.lang[result])

                    # publishing callback
                    if self.pipeliner.pipeData['s_callback']:
                        self.utils.setProgress("Callback...", addNumber=False)
                        if self.pipeliner.pipeData['callbackPath'] and self.pipeliner.pipeData['callbackFile']:
                            callbackResult = self.packager.toCallback(self.pipeliner.pipeData['callbackPath'], self.pipeliner.pipeData['callbackFile'], self.pipeliner.pipeData)
                            if callbackResult:
                                print("Callback result =", callbackResult)

                    # publisher log window
                    self.successPublishedWindow(publishFileName)
                    self.utils.setProgress(endIt=True)
                    self.utils.closeUI('dpPublisherWindow')
                    self.askUserChooseFile(publishFileName)

            else:
                mel.eval('warning \"'+self.dpUIinst.lang['v021_noFileName']+'\";')
        else:
            mel.eval('warning \"'+self.dpUIinst.lang['v022_noFilePath']+'\";')


    def abortPublishing(self, raison=None, *args):
        """ Stop the publishing process because we found an error somewhere.
            Reopen the rig file.
            Log error in a window.
            End progressWindow.
            Warning the raison of the error.
        """
        self.utils.setProgress(endIt=True)
        self.utils.closeUI('dpPublisherWindow')
        # reopen current file
        cmds.file(self.pipeliner.pipeData['sceneName'], open=True, force=True)
        # report the error in a log window
        if raison:
            self.dpUIinst.logger.infoWin('i019_log', 'i216_publish', raison, "left", 250, 150)
            mel.eval('warning \"'+raison+'\";')


    def askUserChooseFile(self, publishFileName, *args):
        """ Ask user witch file want to open:
            1 - WIP file
            2 - Published file
        """
        optWip = "1 - "+self.pipeliner.pipeData['shortName']
        optPub = "2 - "+publishFileName
        result = cmds.confirmDialog(title=self.publisherName, message=self.dpUIinst.lang['v098_askUserChooseFile'], button=[optWip, optPub], defaultButton=optPub, cancelButton=optPub, dismissString=optPub)
        if result == optWip:
            cmds.file(self.pipeliner.pipeData['sceneName'], open=True, force=True)


    def successPublishedWindow(self, publishedFile, *args):
        """ If everything works well we can call a success publishing window here.
        """
        self.utils.closeUI('dpSuccessPublishedWindow')
        self.utils.setProgress(endIt=True)
        # window
        winWidth  = 250
        winHeight = 130
        cmds.window('dpSuccessPublishedWindow', title=self.publisherName+" "+str(DP_PUBLISHER_VERSION), widthHeight=(winWidth, winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpSuccessPublishedWindow')
        # create UI layout and elements:
        succesLayout = cmds.columnLayout('succesLayout', adjustableColumn=True, columnOffset=("both", 10))
        cmds.separator(style="none", height=20, parent=succesLayout)
        cmds.text(label=self.dpUIinst.lang['v023_successPublished'], font='boldLabelFont', parent=succesLayout)
        cmds.separator(style="none", height=20, parent=succesLayout)
        cmds.text(label=publishedFile, parent=succesLayout)
        cmds.separator(style="none", height=20, parent=succesLayout)
        cmds.text(label=self.dpUIinst.lang['i018_thanks'], parent=succesLayout)
