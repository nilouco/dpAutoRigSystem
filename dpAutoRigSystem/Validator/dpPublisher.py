# importing libraries:
from maya import cmds
from maya import mel
from functools import partial
from os import walk
from ..Modules.Library import dpUtils


DPPUBLISHER_VERSION = 1.0

RIG_V = "_rig_v"

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
        self.rigV = RIG_V
        self.publisherName = self.langDic[self.langName]['m046_publisher']
        self.currentAssetName = None
        self.shortAssetName = None


    def mainUI(self, *args):
        """ This is the main method to load the Publisher UI.
        """
        
        #WIP
        self.ui = True
        self.closeUI()
        savedScene = self.checkSavedScene()
        if savedScene:
            self.checkPipelineAssetName()
            

            # window
            publisher_winWidth  = 380
            publisher_winHeight = 300
            cmds.window('dpPublisherWindow', title=self.publisherName+" "+str(DPPUBLISHER_VERSION), widthHeight=(publisher_winWidth, publisher_winHeight), menuBar=False, sizeable=True, minimizeButton=True, maximizeButton=False)
            cmds.showWindow('dpPublisherWindow')
            # create UI layout and elements:
            publisherLayout = cmds.columnLayout('publisherLayout', adjustableColumn=True, columnOffset=("both", 10))
            cmds.separator(style="none", parent=publisherLayout)
            

            publisherLayoutA = cmds.rowColumnLayout('publisherLayoutA', numberOfColumns=2, columnWidth=[(1, 100), (2, 280)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'both', 5), (2, 'both', 5)], rowSpacing=[(1, 5), (2, 5), (3, 5)], parent=publisherLayout)
            cmds.text('commentTxt', label=self.langDic[self.langName]['i219_comments'], align='right', parent=publisherLayoutA)
            self.commentTF = cmds.textField('commentTF', editable=True, parent=publisherLayoutA)
            
            #cmds.text('')
            self.filePathFBG = cmds.textFieldButtonGrp('filePathFBG', label=self.langDic[self.langName]['i220_filePath'], text='', buttonLabel=self.langDic[self.langName]['i187_load'], buttonCommand=self.loadFilePath, adjustableColumn=2, parent=publisherLayout)
            self.fileNameTFG = cmds.textFieldGrp('fileNameTFG', label=self.langDic[self.langName]['i221_fileName'], text='', adjustableColumn=2, parent=publisherLayout)

            #cmds.text('filePathTxt', label=self.langDic[self.langName]['i220_filePath'], align='right', parent=publisherLayoutA)
            #self.filePathTF = cmds.textField('filePathTF', editable=True, parent=publisherLayoutA)

            self.publishBT = cmds.button('publishBT', label=self.langDic[self.langName]['i216_publish'], command=partial(self.runPublishing, self.ui, self.verbose), backgroundColor=(0.75, 0.75, 0.75), parent=publisherLayout)
            cmds.text("infoTxt", label=self.langDic[self.langName]['i217_publishDesc'], align="center", height=20, parent=publisherLayout)
            
            cmds.separator(style='none', height=10, width=100, parent=publisherLayout)
            
            
            self.setFilePath()
            self.setFileName()

            # file path
            # file name
            # version
            # ignore validation checkBox
            # diagnose?
            # verbose = see log (none, simple or complete)
            # fromUI ?


    def checkSavedScene(self, *args):
        """ Check if the current scene is saved to return True.
            If not saved, try to save or save as it.
            Otherwise return False.
        """
        modifiedScene = cmds.file(query=True, modified=True)
        if modifiedScene:
            saveName = self.langDic[self.langName]['i222_save']
            saveAsName = self.langDic[self.langName]['i223_saveAs']
            cancelName = self.langDic[self.langName]['i132_cancel']
            confirmResult = cmds.confirmDialog( title=self.publisherName, message=self.langDic[self.langName]['i201_saveScene'], button=[saveName, saveAsName, cancelName], defaultButton=saveName, cancelButton=cancelName, dismissString=cancelName )
            if confirmResult == cancelName:
                return False
            else:
                if confirmResult == saveName:
                    return cmds.file(save=True)
                else:
                    newName = cmds.fileDialog2(fileFilter="Maya Files (*.ma *.mb);;", fileMode=0, dialogStyle=2)
                    if newName:
                        cmds.file(rename=newName[0])
                        return cmds.file(save=True)
                    else:
                        return False
        return True


    def checkPipelineAssetName(self, *args):
        """
        """
        self.currentAssetName = cmds.file(query=True, sceneName=True)
        shortName = cmds.file(query=True, sceneName=True, shortName=True)
        self.shortAssetName = shortName[:shortName.find("_")]
        folderAssetName = self.currentAssetName[:self.currentAssetName.rfind("/")]
        folderAssetName = folderAssetName[folderAssetName.rfind("/")+1:]
        print("self.currentAssetName =", self.currentAssetName)
        print("shortName =", shortName)
        print("shortAssetName =", self.shortAssetName)
        print("folderAssetName = ", folderAssetName)
        if folderAssetName == self.shortAssetName:
            print("YESSSS")
            
            return self.shortAssetName
        else:
            print("NOOOOOOOOOO")
            return False


    def defineFileVersion(self, assetNameList, *args):
        """
        """
        if assetNameList:
            numberList = []
            for item in assetNameList:
                print("item =", item)
                numberList.append(int(item[:item.rfind(".")].split(self.rigV)[1]))
            print("numberList =", numberList)
            return max(numberList)+1



    def setFilePath(self, filePath=None, *args):
        """
        """
        print("setting filePath here merci...")
        if not filePath:
            # try to load a pipeline structure to get the filePath to set
            print("trying to find pipe path here.....")
        if filePath:
            #try:
            cmds.textFieldButtonGrp(self.filePathFBG, edit=True, text=str(filePath))
            self.setFileName(filePath)
            #except:
            #    pass


    def setFileName(self, filePath=None, *args):
        """
        """
        print("setting file name here, teinquil")
        if not filePath:
            filePath = self.getPipeFilePath()

        if filePath:
            fileName = self.getPipeFileName(filePath)
            cmds.textFieldGrp(self.fileNameTFG, edit=True, text=str(fileName))


    def loadFilePath(self, *args):
        """
        """
        print("loading filePath here....")
        dialogResult = cmds.fileDialog2(fileFilter="Maya Files (*.ma *.mb);;", fileMode=3, dialogStyle=2, okCaption=self.langDic[self.langName]['i187_load'])
        print("dialogResult = ", dialogResult)
        if dialogResult:
            self.setFilePath(dialogResult[0])


    def getPipeFilePath(self, *args):
        """
        """
        print("loading file path from pipeline here... we are the champions my friend")
        studioName, studioPath = self.dpUIinst.getPipelineStudioName(self.dpUIinst.pipelineDrive)
        print("studioName and Path =", studioName, studioPath)


    def getPipeFileName(self, filePath, *args):
        """
        """
        assetNameList = []
        print("geting pipe file name mi amigo...")
        if filePath:
            print("FILE PATH HERE:", filePath)
            fileNameList = next(walk(filePath))[2]
            print("fileNameList =", fileNameList)
            if fileNameList:
                lastAssetVersion = 0
                assetName = self.checkPipelineAssetName()
                print("assetName =", assetName)
                if not assetName:
                    assetName = self.shortAssetName
                for fileName in fileNameList:
                    if assetName+"_" in fileName:
                        if not fileName in assetNameList:
                            assetNameList.append(fileName)
                if assetNameList:
                    print(assetNameList)
                    fileVersion = self.defineFileVersion(assetNameList)
                    print("fileVersion ===", fileVersion)



    def closeUI(self, *args):
        """ Delete existing Publisher window if it exists.
        """
        if cmds.window('dpPublisherWindow', query=True, exists=True):
            cmds.deleteUI('dpPublisherWindow', window=True)
    

    def runPublishing(self, fromUI, verbose, comments=False, *args):
        """ Start the publishing process running the checked validators.
        """
        foundIssue = False
        toCheckValidatorList = [self.dpUIinst.checkInInstanceList, self.dpUIinst.checkOutInstanceList, self.dpUIinst.checkAddOnsInstanceList]
        for validatorList in toCheckValidatorList:
            if validatorList:
                validationResultDataList = self.dpUIinst.runSelectedValidators(validatorList, True, False, True)
                if validationResultDataList[1]: #found issue
                    stoppedMessage = self.langDic[self.langName]['v020_publishStopped']+" "+validatorList[validationResultDataList[2]].guideModuleName
                    mel.eval('warning \"'+stoppedMessage+'\";')
                    cmds.progressWindow(endProgress=True)
                    foundIssue = True
                    break
        if not foundIssue:
            print ("good, merci")
            

            # comments
            commentValue = comments
            if not comments and fromUI:
                commentValue = cmds.textField(self.commentTF, query=True, text=True)
            print("commentValue =", commentValue)


            # 



        # TODO result window = log here


        self.closeUI()
