# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
import os
from ..Modules.Library import dpUtils
from . import dpPipeliner
from . import dpPackager
from importlib import reload
reload(dpPipeliner)
reload(dpPackager)


DPPUBLISHER_VERSION = 1.1


class Publisher(object):
    def __init__(self, dpUIinst, ui=True, verbose=True):
        """ Initialize the module class loading variables.
        """
        # defining variables:
        self.dpUIinst = dpUIinst
        self.langDic = dpUIinst.langDic
        self.langName = dpUIinst.langName
        self.ui = ui
        self.verbose = verbose
        self.publisherName = self.langDic[self.langName]['m046_publisher']
        self.currentAssetName = None
        self.shortAssetName = None
        self.pipeliner = dpPipeliner.Pipeliner()
        self.packager = dpPackager.Packager()


    def getFileTypeByExtension(self, fileName, *args):
        """ Return the file type based in the extension of the given file name.
        """
        ext = fileName[-2:]
        if ext == "mb":
            return "mayaBinary"
        return "mayaAscii"
    

    def userSaveThisScene(self, *args):
        """ Open a confirmDialog to user save or save as this file.
            Return the saved file path or False if canceled.
        """
        shortName = cmds.file(query=True, sceneName=True, shortName=True)
        saveName = self.langDic[self.langName]['i222_save']
        saveAsName = self.langDic[self.langName]['i223_saveAs']
        cancelName = self.langDic[self.langName]['i132_cancel']
        confirmResult = cmds.confirmDialog(title=self.publisherName, message=self.langDic[self.langName]['i201_saveScene'], button=[saveName, saveAsName, cancelName], defaultButton=saveName, cancelButton=cancelName, dismissString=cancelName)
        if confirmResult == cancelName:
            return False
        else:
            if not shortName or confirmResult == saveAsName: #untitled or saveAs
                newName = cmds.fileDialog2(fileFilter="Maya ASCII (*.ma);;Maya Binary (*.mb);;", fileMode=0, dialogStyle=2)
                if newName:
                    ext = self.getFileTypeByExtension(newName[0])
                    cmds.file(rename=newName[0])
                    return cmds.file(save=True, type=ext)
                else:
                    return False
            else: #save
                cmds.file(rename=cmds.file(query=True, sceneName=True))
                ext = cmds.file(type=True, query=True)[0]
                return cmds.file(save=True, type=ext)


    def mainUI(self, *args):
        """ This is the main method to load the Publisher UI.
        """
        self.ui = True
        dpUtils.closeUI('dpSuccessPublishedWindow')
        dpUtils.closeUI('dpPublisherWindow')
        savedScene = self.pipeliner.checkSavedScene()
        if not savedScene:
            savedScene = self.userSaveThisScene()
        if savedScene:
            # window
            publisher_winWidth  = 450
            publisher_winHeight = 200
            cmds.window('dpPublisherWindow', title=self.publisherName+" "+str(DPPUBLISHER_VERSION), widthHeight=(publisher_winWidth, publisher_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
            cmds.showWindow('dpPublisherWindow')
            # create UI layout and elements:
            publisherLayout = cmds.columnLayout('publisherLayout', adjustableColumn=True, columnOffset=("both", 10))
            cmds.separator(style="none", height=20, parent=publisherLayout)
            # fields
            self.filePathFBG = cmds.textFieldButtonGrp('filePathFBG', label=self.langDic[self.langName]['i220_filePath'], text='', buttonLabel=self.langDic[self.langName]['i187_load'], buttonCommand=self.userLoadFilePath, adjustableColumn=2, changeCommand=self.editPublishPath, parent=publisherLayout)
            self.fileNameTFG = cmds.textFieldGrp('fileNameTFG', label=self.langDic[self.langName]['i221_fileName'], text='', adjustableColumn=2, editable=True, parent=publisherLayout)
            self.commentTFG = cmds.textFieldGrp('commentTFG', label=self.langDic[self.langName]['i219_comments'], text='', adjustableColumn=2, editable=True, parent=publisherLayout)
            self.verifyValidatorsCB = cmds.checkBox("verifyValidatorsCB", label=self.langDic[self.langName]['i217_verifyChecked'], align="left", height=20, value=True, parent=publisherLayout)
            # buttons
            publisherBPLayout = cmds.paneLayout('publisherBPLayout', configuration='vertical3', paneSize=[(1, 20, 20), (2, 20, 20), (3, 50, 20)], parent=publisherLayout)
            cmds.button(label="Pipeliner", command=partial(self.pipeliner.mainUI, self.dpUIinst), parent=publisherBPLayout)
            cmds.button('diagnoseBT', label=self.langDic[self.langName]['i224_diagnose'], command=partial(self.runDiagnosing), height=30, backgroundColor=(0.5, 0.5, 0.5), parent=publisherBPLayout)
            cmds.button('publishBT', label=self.langDic[self.langName]['i216_publish'], command=partial(self.runPublishing, self.ui, self.verbose), height=30, backgroundColor=(0.75, 0.75, 0.75), parent=publisherBPLayout)

            # workaround to load pipeliner data correctly
            # TODO find a way to load without UI
            self.pipeliner.mainUI(self.dpUIinst)
            dpUtils.closeUI('dpPipelinerWindow')
            self.setPublishFilePath()


    def editPublishPath(self, *args):
        """ Set the current publish path as the entered text in the textField.
        """
        self.pipeliner.pipeData['publishPath'] = cmds.textFieldButtonGrp(self.filePathFBG, query=True, text=True)


    def checkPipelineAssetNameFolder(self, *args):
        """ Compare the sceneName with the father folder name to define if we use the assetName as a default pipeline setup.
            Return the shortName of the asset if found.
            Otherwise return False
        """
        self.currentAssetName = cmds.file(query=True, sceneName=True)
        self.shortAssetName = cmds.file(query=True, sceneName=True, shortName=True)
        if "_" in self.shortAssetName:
            self.shortAssetName = self.shortAssetName[:self.shortAssetName.find("_")]
        for ext in [".ma", ".mb"]:
            if self.shortAssetName.endswith(ext):
                self.shortAssetName = self.shortAssetName[:-3]
        folderAssetName = self.currentAssetName[:self.currentAssetName.rfind("/")]
        folderAssetName = folderAssetName[folderAssetName.rfind("/")+1:]
        if folderAssetName == self.shortAssetName:
            return self.shortAssetName
        return False


    def defineFileVersion(self, assetNameList, *args):
        """ Return the max number plus one of a versioned files list.
        """
        if assetNameList:
            numberList = []
            for item in assetNameList:
                numberList.append(int(item[:item.rfind(".")].split(self.pipeliner.pipeData['s_middle'])[1]))
            return max(numberList)+1


    def setPublishFilePath(self, filePath=None, *args):
        """ Set the publish file path and return it.
        """
        if not filePath:
            # try to load a pipeline structure to get the filePath to set it up
            filePath = self.pipeliner.loadPublishPath()
        if filePath:
            try:
                cmds.textFieldButtonGrp(self.filePathFBG, edit=True, text=str(filePath))
                cmds.textFieldGrp(self.fileNameTFG, edit=True, text=str(self.getPipeFileName(filePath)))
                self.pipeliner.pipeData['publishPath'] = filePath
            except:
                pass
        return filePath


    def userLoadFilePath(self, *args):
        """ Ask user to load a file path.
        """
        dialogResult = cmds.fileDialog2(fileFilter="Maya Files (*.ma *.mb);;", fileMode=3, dialogStyle=2, okCaption=self.langDic[self.langName]['i187_load'])
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


    def getPipeFileName(self, filePath, *args):
        """ Return the generated file name based on the pipeline publish folder.
            It's check the asset name and define the file version to save the published file.
        """
        self.assetNameList = []
        if os.path.exists(filePath):
            assetName = self.checkPipelineAssetNameFolder()
            if not assetName:
                assetName = self.shortAssetName
            publishVersion = 1 #starts the number versioning by one to have the first delivery file as _v001.
            fileNameList = next(os.walk(filePath))[2]
            if fileNameList:
                for fileName in fileNameList:
                    if assetName+self.pipeliner.pipeData['s_middle'] in fileName:
                        if not fileName in self.assetNameList:
                            self.assetNameList.append(fileName)
                if self.assetNameList:
                    publishVersion = self.defineFileVersion(self.assetNameList)
            if self.pipeliner.pipeData['b_capitalize']:
                assetName = assetName.capitalize()
            elif self.pipeliner.pipeData['b_lower']:
                assetName = assetName.lower()
            elif self.pipeliner.pipeData['b_upper']:
                assetName = assetName.upper()
            self.pipeliner.pipeData['assetName'] = assetName
            self.pipeliner.pipeData['rigVersion'] = self.getRigWIPVersion()
            self.pipeliner.pipeData['publishVersion'] = publishVersion
            fileName = self.pipeliner.pipeData['s_prefix']+assetName+self.pipeliner.pipeData['s_middle']+(str(publishVersion).zfill(int(self.pipeliner.pipeData['i_padding']))+self.pipeliner.pipeData['s_suffix'])
            return fileName
        else:
            return False
    

    def runCheckedValidators(self, verifyMode=True, stopIfFoundBlock=True, publishLog=None, *args):
        """ Run the verify of fix of checked validators.
        """
        toCheckValidatorList = self.dpUIinst.checkInInstanceList
        toCheckValidatorList.extend(self.dpUIinst.checkOutInstanceList)
        toCheckValidatorList.extend(self.dpUIinst.checkAddOnsInstanceList)
        if toCheckValidatorList:
            validationResultDataList = self.dpUIinst.runSelectedValidators(toCheckValidatorList, verifyMode, True, stopIfFoundBlock, publishLog)
            if validationResultDataList[1]: #found issue
                stoppedMessage = self.langDic[self.langName]['v020_publishStopped']+" "+toCheckValidatorList[validationResultDataList[2]].guideModuleName                    
                return stoppedMessage
        return False
        

    def runDiagnosing(self, *args):
        """ Check all active validators in the verify mode and return the result in a log window.
        """
        validatorsResult = self.runCheckedValidators() #verify mode
        if validatorsResult:
            mel.eval('warning \"'+validatorsResult+'\";')
            cmds.progressWindow(endProgress=True)
        else:
            validatorsResult = self.langDic[self.langName]['v007_allOk']
        self.dpUIinst.info('i019_log', 'i224_diagnose', validatorsResult, "left", 250, 150)


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
            maxProcess = 4
            progressAmount = 0
            cmds.progressWindow(title=self.publisherName, maxValue=maxProcess, progress=progressAmount, status='Starting...', isInterruptable=False)

            # check if there'a a file name to publish this scene
            publishFileName = self.getPipeFileName(self.pipeliner.pipeData['publishPath'])
            if fromUI:
                publishFileName = cmds.textFieldGrp(self.fileNameTFG, query=True, text=True)
            if publishFileName:
                # start logging
                publishLog = {}
                publishLog["Scene"] = self.pipeliner.pipeData['sceneName']
                if not publishFileName[-3:-1] == ".m":
                    publishFileName += ".m"+self.pipeliner.pipeData['sceneName'][-1]
                publishLog["Published"] = self.pipeliner.pipeData['publishPath']+"/"+publishFileName
                # comments
                publishLog["Comment"] = ""
                commentValue = comments
                if fromUI and not comments:
                    commentValue = cmds.textFieldGrp(self.commentTFG, query=True, text=True)
                if commentValue:
                    publishLog["Comment"] = commentValue
                
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
                    progressAmount += 1
                    cmds.progressWindow(title=self.publisherName, maxValue=maxProcess, progress=progressAmount, status='Storing data...', isInterruptable=False)
                    
                    # try to store data into All_Grp if it exists
                    self.pipeliner.pipeData['modelVersion'] = None
                    if not self.dpUIinst.checkIfNeedCreateAllGrp():
                        # published from file
                        if not cmds.objExists(self.dpUIinst.masterGrp+".publishedFromFile"):
                            cmds.addAttr(self.dpUIinst.masterGrp, longName="publishedFromFile", dataType="string")
                        cmds.setAttr(self.dpUIinst.masterGrp+".publishedFromFile", self.pipeliner.pipeData['sceneName'], type="string")
                        # coments
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

                    progressAmount += 1
                    cmds.progressWindow(edit=True, progress=progressAmount, status=self.langDic[self.langName]['i227_getImage'], isInterruptable=False)

                    # publishing file
                    # create folders to publish file if needed
                    if not os.path.exists(self.pipeliner.pipeData['publishPath']):
                        try:
                            os.makedirs(self.pipeliner.pipeData['publishPath'])
                        except:
                            self.abortPublishing(self.langDic[self.langName]['v022_noFilePath'])
                    
                    # mount folders
                    if self.pipeliner.pipeData['b_deliver']:
                        self.pipeliner.mountPackagePath()
                        if self.pipeliner.pipeData['toClientPath']:
                            # rigging preview image
                            if self.pipeliner.pipeData['b_imager']:
                                self.packager.imager(self.pipeliner.pipeData, builtVersion, self.pipeliner.today)
                    cmds.progressWindow(endProgress=True)
                    progressAmount += 1
                    cmds.progressWindow(title=self.publisherName, maxValue=maxProcess, progress=progressAmount, status=self.langDic[self.langName]['i225_savingFile'], isInterruptable=False)
                    
                    # save published file
                    cmds.file(rename=self.pipeliner.pipeData['publishPath']+"/"+publishFileName)
                    cmds.file(save=True, type=cmds.file(query=True, type=True)[0], prompt=False, force=True)

                    # organize old published files
                    if self.assetNameList:
                        self.pipeliner.makeDirIfNotExists(self.pipeliner.pipeData['publishPath']+"/"+self.pipeliner.pipeData['s_old'])
                        self.packager.toOld(self.pipeliner.pipeData['publishPath'], publishFileName, self.assetNameList, self.pipeliner.pipeData['publishPath']+"/"+self.pipeliner.pipeData['s_old'])

                    # packager
                    if self.pipeliner.pipeData['b_deliver']:
                        progressAmount += 1
                        cmds.progressWindow(edit=True, progress=progressAmount, status=self.langDic[self.langName]['i226_exportFiles'], isInterruptable=False)

                        if self.pipeliner.pipeData['toClientPath']:
                            # toClient
                            zipFile = self.packager.zipToClient(self.pipeliner.pipeData['publishPath'], publishFileName, self.pipeliner.pipeData['toClientPath'], self.pipeliner.today)
                            # dropbox
                            if zipFile:
                                if self.pipeliner.pipeData['dropboxPath']:
                                    self.packager.toDropbox(zipFile, self.pipeliner.pipeData['dropboxPath'])
                        # hist
                        if self.pipeliner.pipeData['historyPath']:
                            self.packager.toHistory(self.pipeliner.pipeData['scenePath'], self.pipeliner.pipeData['shortName'], self.pipeliner.pipeData['historyPath'])

                    # publisher log window
                    self.successPublishedWindow(publishFileName)
                dpUtils.closeUI('dpPublisherWindow')

            else:
                mel.eval('warning \"'+self.langDic[self.langName]['v021_noFileName']+'\";')
        else:
            mel.eval('warning \"'+self.langDic[self.langName]['v022_noFilePath']+'\";')


    def abortPublishing(self, raison=None, *args):
        """ Stop the publishing process because we found an error somewhere.
            Reopen the rig file.
            Log error in a window.
            End progressWindow.
            Warning the raison of the error.
        """
        # reopen current file
        cmds.file(self.pipeliner.pipeData['sceneName'], open=True, force=True)
        cmds.progressWindow(endProgress=True)
        # report the error in a log window
        if raison:
            self.dpUIinst.info('i019_log', 'i216_publish', raison, "left", 250, 150)
            mel.eval('warning \"'+raison+'\";')


    def successPublishedWindow(self, publishedFile, *args):
        """ If everything works well we can call a success publishing window here.
        """
        dpUtils.closeUI('dpSuccessPublishedWindow')
        cmds.progressWindow(endProgress=True)
        # window
        winWidth  = 250
        winHeight = 130
        cmds.window('dpSuccessPublishedWindow', title=self.publisherName+" "+str(DPPUBLISHER_VERSION), widthHeight=(winWidth, winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
        cmds.showWindow('dpSuccessPublishedWindow')
        # create UI layout and elements:
        succesLayout = cmds.columnLayout('succesLayout', adjustableColumn=True, columnOffset=("both", 10))
        cmds.separator(style="none", height=20, parent=succesLayout)
        cmds.text(label=self.langDic[self.langName]['v023_successPublished'], font='boldLabelFont', parent=succesLayout)
        cmds.separator(style="none", height=20, parent=succesLayout)
        cmds.text(label=publishedFile, parent=succesLayout)
        cmds.separator(style="none", height=20, parent=succesLayout)
        cmds.text(label=self.langDic[self.langName]['i018_thanks'], parent=succesLayout)
