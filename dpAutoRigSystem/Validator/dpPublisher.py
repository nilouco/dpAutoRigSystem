# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
import os
from ..Modules.Library import dpUtils
from . import dpPipeliner
from importlib import reload
reload(dpPipeliner)


DPPUBLISHER_VERSION = 1.0


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
                newName = cmds.fileDialog2(fileFilter="Maya Files (*.ma *.mb);;", fileMode=0, dialogStyle=2)
                if newName:
                    cmds.file(rename=newName[0])
                    return cmds.file(save=True)
                else:
                    return False
            else: #save
                return cmds.file(save=True)


    def mainUI(self, *args):
        """ This is the main method to load the Publisher UI.
        """

        #self.pipeliner.getPipelineData()
        #WIP


        self.ui = True
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

            # TODO back to verifyValidatorsCB to value = True
            #self.verifyValidatorsCB = cmds.checkBox("verifyValidatorsCB", label=self.langDic[self.langName]['i217_verifyChecked'], align="left", height=20, value=True, parent=publisherLayout)
            self.verifyValidatorsCB = cmds.checkBox("verifyValidatorsCB", label=self.langDic[self.langName]['i217_verifyChecked'], align="left", height=40, value=False, parent=publisherLayout)

            # buttons
            publisherBPLayout = cmds.paneLayout('publisherBPLayout', configuration='vertical2', paneSize=[1, 20, 3], parent=publisherLayout)
            cmds.button(label="Pipeliner", command=partial(self.pipeliner.mainUI, self.dpUIinst), parent=publisherBPLayout)
            self.publishBT = cmds.button('publishBT', label=self.langDic[self.langName]['i216_publish'], command=partial(self.runPublishing, self.ui, self.verbose), height=30, backgroundColor=(0.75, 0.75, 0.75), parent=publisherBPLayout)
            
            # workaround to load pipeliner data correctly
            # TODO find a way to load without UI
            self.pipeliner.mainUI(self.dpUIinst)
            dpUtils.closeUI('dpPipelinerWindow')
            
            
            self.setPublishFilePath()
           

            # TODO
            #
            # 
            #
            # ignore validation checkBox
            # diagnose?
            # verbose = see log (none, simple or complete)
            # fromUI ?
            # pipe to find folders like: Publish, ToClient, etc
            # log window
            # 


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
        """ Return the latest number of a versioned files list.
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


    def getPipeFileName(self, filePath, *args):
        """ Return the generated file name based on the pipeline publish folder.
            It's check the asset name and define the file version to save the published file.
        """
        if os.path.exists(filePath):
            assetName = self.checkPipelineAssetNameFolder()
            if not assetName:
                assetName = self.shortAssetName
            fileVersion = 0
            fileNameList = next(os.walk(filePath))[2]
            if fileNameList:
                assetNameList = []
                for fileName in fileNameList:
                    if assetName in fileName:
                        if not fileName in assetNameList:
                            assetNameList.append(fileName)
                if assetNameList:
                    fileVersion = self.defineFileVersion(assetNameList)
            if self.pipeliner.pipeData['b_capitalize']:
                assetName = assetName.capitalize()
            elif self.pipeliner.pipeData['b_lower']:
                assetName = assetName.lower()
            elif self.pipeliner.pipeData['b_upper']:
                assetName = assetName.upper()
            fileName = self.pipeliner.pipeData['s_prefix']+assetName+self.pipeliner.pipeData['s_middle']+(str(fileVersion).zfill(int(self.pipeliner.pipeData['i_padding']))+self.pipeliner.pipeData['s_suffix'])
            return fileName
        else:
            return False
    

    def verifyCheckedValidators(self, *args):
        """ Run the verify of checked validators.
        """
        toCheckValidatorList = [self.dpUIinst.checkInInstanceList, self.dpUIinst.checkOutInstanceList, self.dpUIinst.checkAddOnsInstanceList]
        for validatorList in toCheckValidatorList:
            if validatorList:
                validationResultDataList = self.dpUIinst.runSelectedValidators(validatorList, True, False, True)
                if validationResultDataList[1]: #found issue
                    stoppedMessage = self.langDic[self.langName]['v020_publishStopped']+" "+validatorList[validationResultDataList[2]].guideModuleName                    
                    return stoppedMessage
        return False
        



    def runPublishing(self, fromUI, verifyValidator=False, comments=False, *args):
        """ Start the publishing process


            TODO need to describe the publishing process here...
        """

        #WIP
        #save a temp file
        # run validators
        #save a publishedFile
        #delete the temp file



        validatorsResult = False
        if fromUI:
            if cmds.checkBox(self.verifyValidatorsCB, query=True, value=True):
                validatorsResult = self.verifyCheckedValidators()
        elif verifyValidator:
            # TODO: find a way to verify validators without UI
            print("TODO: find a way to verify validators without UI")
        
        if validatorsResult:
            mel.eval('warning \"'+validatorsResult+'\";')
            cmds.progressWindow(endProgress=True)
            # TODO report stopped message here
            # open source file
            # delete temp file

        else:
            # comments
            commentValue = comments
            if fromUI and not comments:
                commentValue = cmds.textFieldGrp(self.commentTFG, query=True, text=True)
            print("commentValue =", commentValue)
            
            # TODO add commentValue to LOG
            

            #WIP 



            if self.pipeliner.pipeData['publishPath']:
                # check if there'a a file name to publish this scene
                publishFileName = self.getPipeFileName(self.pipeliner.pipeData['publishPath'])
                if fromUI:
                    publishFileName = cmds.textFieldGrp(self.fileNameTFG, query=True, text=True)
                if publishFileName:
                    # try to store data into All_Grp if it exists
                    if not self.dpUIinst.checkIfNeedCreateAllGrp():
                        # published from file
                        if not cmds.objExists(self.dpUIinst.masterGrp+".publishedFromFile"):
                            cmds.addAttr(self.dpUIinst.masterGrp, longName="publishedFromFile", dataType="string")
                        cmds.setAttr(self.dpUIinst.masterGrp+".publishedFromFile", self.pipeliner.pipeData['sceneName'], type="string")
                        # model version
                        shortName = cmds.file(query=True, sceneName=True, shortName=True)
                        if self.pipeliner.pipeData['s_model'] in shortName:
                            modelVersion = shortName[shortName.find(self.pipeliner.pipeData['s_model'])+len(self.pipeliner.pipeData['s_model']):]
                            modelVersion = int(modelVersion[:modelVersion.find("_")])
                            if not cmds.objExists(self.dpUIinst.masterGrp+".modelVersion"):
                                cmds.addAttr(self.dpUIinst.masterGrp, longName="modelVersion", attributeType="long")
                            cmds.setAttr(self.dpUIinst.masterGrp+".modelVersion", modelVersion)


                    # create folders to publish file if needed
                    if not os.path.exists(self.pipeliner.pipeData['publishPath']):
                        os.makedirs(self.pipeliner.pipeData['publishPath'])
                
                

                
                     
                    # save published file
                    cmds.file(rename=self.pipeliner.pipeData['publishPath']+"/"+publishFileName)
                    cmds.file(save=True, type=cmds.file(query=True, type=True)[0], prompt=False, force=True)

                

                
                else:
                    print("There isn't a publish file name to save the file, sorry.")
            else:
                print("There isn't a publishing path to save the file, sorry.")

            # WIP
            # review path from user (test desk)
            # call dpImager
            # pass all old wip files to Hist folder
            #
            # TODO result window = log here
            # TODO run everything (Publisher and Pipeliner) without UI
            #
            # after all, ask to open the source file or keep in published file ???


        dpUtils.closeUI('dpPublisherWindow')
