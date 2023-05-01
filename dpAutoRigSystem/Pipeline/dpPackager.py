# importing libraries:
from maya import cmds
from maya import mel
from ..Modules.Library import dpUtils
from urllib import request
import json
import zipfile
import shutil
import os


DPPACKAGER_VERSION = 1.4


RIGPREVIEW = "Rigging Preview"
CAMERA = "persp"
CAM_ROTX = -10
CAM_ROTY = 30
CTRL_LAYER = "Ctrl_Lyr"

class Packager(object):

    def zipToClient(self, filePath, fileName, destinationFolder, date=None, *args):
        """ Create a zipped file with given filePath and fileName replacing the extention (.ma or .mb) to .zip
            Add date at the end of the file if it's given.
            Write the zip file in the destinationFolder.
            Returns the zipFilePathName.
        """
        if date:
            zipName = fileName[:-3]+"_"+date+".zip"
        else:
            zipName = fileName[:-3]+".zip"
        zip = zipfile.ZipFile(destinationFolder+"/"+zipName, "w", zipfile.ZIP_DEFLATED)
        zip.write(filename=filePath+"/"+fileName, arcname=fileName)
        zip.close()
        return destinationFolder+"/"+zipName
        

    def frameCameraToPublish(self, cam=CAMERA, rotX=CAM_ROTX, rotY=CAM_ROTY, focusIt=None, *args):
        """ Prepare the given camera to frame correctly the viewport to publish.
        """
        mel.eval('setNamedPanelLayout "Single Perspective View"; updateToolbox(); findNewCurrentModelView;')
        # set up rotation
        cmds.setAttr(cam+".rotateX", rotX)
        cmds.setAttr(cam+".rotateY", rotY)
        # frame all
        cmds.viewFit(allObjects=True)
        posList = cmds.xform(cam, query=True, translation=True, worldSpace=True)
        if not focusIt:
            focusIt = dpUtils.getNodeByMessage("renderGrp")
        if focusIt:
            # frame render group
            cmds.select(focusIt)
            cmds.viewFit()
            focusPosList = cmds.xform(cam, query=True, translation=True, worldSpace=True)
            # get average
            posList = [(posList[0]+focusPosList[0])/2, (posList[1]+focusPosList[1])/2, (posList[2]+focusPosList[2])/2]
        cmds.select(clear=True)
        cmds.refresh(force=True)
        cmds.camera(cam, edit=True, position=[posList[0], posList[1], posList[2]], rotation=[rotX, rotY, 0])
        
        
    def getDisplayRGBColorList(self, searchItem, *args):
        """ Return the RGB values listed for the given searchItem from displayRGBColor Maya command.
        """
        displayRGBColorList = cmds.displayRGBColor(list=True)
        for item in displayRGBColorList:
            if searchItem+' ' in item:
                valuesList = item[:-1].split(" ")
                valuesList = valuesList[1:]
                valuesList = [float(x) for x in valuesList]
                return valuesList

    
    def imager(self, pipeData, dpARVersion, date, rigPreview=RIGPREVIEW, cam=CAMERA, *args):
        """ Save a rigging preview screenShot file with the given informations.
            Thanks Caio Hidaka for the help in this code!
        """
        mayaVersion = cmds.about(installedVersion=True)
        # store current user settings
        currentGrid = cmds.grid(toggle=True, query=True)
        currentDisplayGradient = cmds.displayPref(displayGradient=True, query=True)
        currentHUDLabels = cmds.displayColor('headsUpDisplayLabels', query=True, dormant=True)
        currentHUDValues = cmds.displayColor('headsUpDisplayValues', query=True, dormant=True)
        currentBGColorList = self.getDisplayRGBColorList('background')
        currentBGTopColorList = self.getDisplayRGBColorList('backgroundTop')
        currentBGBottomColorList = self.getDisplayRGBColorList('backgroundBottom')
        
        # save hudList to hide:
        currentHUDVisList = []
        hudList = cmds.headsUpDisplay(listHeadsUpDisplays=True)
        for item in hudList:
            currentHUDVis = cmds.headsUpDisplay(item, query=True, visible=True)
            currentHUDVisList.append(currentHUDVis)
            cmds.headsUpDisplay(item, edit=True, visible=False)
        camAttrVisList = []
        camAttrList = ["displayGateMask", "displayResolution", "displayFilmGate", "displayFieldChart", "displaySafeAction", "displaySafeTitle", "displayFilmPivot", "displayFilmOrigin", "depthOfField"]
        for attr in camAttrList:
            currentCamAttrVis = cmds.getAttr(cam+"."+attr)
            camAttrVisList.append(currentCamAttrVis)
            cmds.setAttr(cam+"."+attr, False)
        currentCamOverscan = cmds.getAttr(cam+".overscan")
        cmds.setAttr(cam+".overscan", 1.0)
        currentCamAspectRatio = cmds.camera(cam, query=True, aspectRatio=True)
        cmds.camera(cam, edit=True, aspectRatio=0.8)
        currentCtrlLyrDisplay = False
        if cmds.objExists(CTRL_LAYER):
            currentCtrlLyrDisplay = cmds.getAttr(CTRL_LAYER+".hideOnPlayback")
            cmds.setAttr(CTRL_LAYER+".hideOnPlayback", 0)

        # set up custom display settings
        cmds.grid(toggle=False)
        cmds.displayPref(displayGradient=pipeData['b_i_degrade'])
        cmds.displayColor('headsUpDisplayLabels', 1, dormant=True) #black
        cmds.displayColor('headsUpDisplayValues', 1, dormant=True) #black
        cmds.displayRGBColor('background', 0.631, 0.631, 0.631)
        cmds.displayRGBColor('backgroundTop', 0.731, 0.731, 0.731)
        cmds.displayRGBColor('backgroundBottom', 0.42, 0.42, 0.42)

        # file information messages
        cmds.headsUpDisplay('HudRigPreviewTxt10', section=0, block=10, labelFontSize="large", allowOverlap=True, label="") #starting by 10 to avoid default Maya's HUD already existing
        cmds.headsUpDisplay('HudRigPreviewTxt11', section=0, block=11, labelFontSize="large", allowOverlap=True, label=rigPreview)
        b = 12
        if pipeData['b_i_maya']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label=mayaVersion)
            b += 1
        if pipeData['b_i_version']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label="dpAutoRigSystem "+dpARVersion)
            b += 1
        if pipeData['b_i_studio']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label=pipeData['f_studio'])
            b += 1
        if pipeData['b_i_project']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label=pipeData['f_project'])
            b += 1
        if pipeData['b_i_asset']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label=pipeData['assetName'])
            b += 1
        if pipeData['b_i_model']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label="Model "+str(pipeData['modelVersion']).zfill(int(pipeData['i_padding'])))
            b += 1
        if pipeData['b_i_wip']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label="Rig "+str(pipeData['rigVersion']).zfill(int(pipeData['i_padding'])))
            b += 1
        if pipeData['b_i_publish']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label="Publish "+str(pipeData['publishVersion']).zfill(int(pipeData['i_padding'])))
            b += 1
        if pipeData['b_i_date']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label=date)
            b += 1
            
        # create a new persp viewport window to get the image from it
        dpUtils.closeUI("dpImagerWindow")
        dpImagerWindow = cmds.window('dpImagerWindow', width=720, height=720, menuBarVisible=False, titleBar=True, visible=True)
        cmds.paneLayout(parent=dpImagerWindow)
        dpImagerPanel = cmds.modelPanel(menuBarVisible=False, label='dpImagerPanel')
        cmds.modelEditor(dpImagerPanel, edit=True, displayAppearance='smoothShaded')
        barLayout = cmds.modelPanel(dpImagerPanel, query=True, barLayout=True)
        cmds.frameLayout(barLayout, edit=True, collapse=True)
        cmds.showWindow(dpImagerWindow)
        editor = cmds.modelPanel(dpImagerPanel, query=True, modelEditor=True)
        cmds.modelEditor(editor, edit=True, activeView=True)
        #cmds.refresh(force=True)

        # focus camera to frame the rig
        self.frameCameraToPublish(cam)
        
        # take the screenShot
        width = 0
        height = 0
        currentFrame = int(cmds.currentTime(query=True))
        destinationFolder = pipeData['toClientPath']
        if not destinationFolder.endswith("/"):
            destinationFolder += "/"
        exportPath = "{}{}_{}.jpg".format(destinationFolder, pipeData['assetName'], rigPreview.replace(" ", ""))
        # playblast to make an image
        cmds.playblast(frame=currentFrame, viewer=False, format="image", compression="jpg", showOrnaments=True, completeFilename=exportPath, widthHeight=[width, height], percent=100, forceOverwrite=False, quality=100, editorPanelName=dpImagerPanel)
        # clean up the UI
        cmds.deleteUI(dpImagerPanel, panel=True)
        dpUtils.closeUI("dpImagerWindow")
        
        # back scene preferences to stored status
        cmds.camera(cam, edit=True, aspectRatio=1.5)
        cmds.grid(toggle=currentGrid)
        cmds.displayPref(displayGradient=currentDisplayGradient)
        cmds.displayColor('headsUpDisplayLabels', currentHUDLabels, dormant=True)
        cmds.displayColor('headsUpDisplayValues', currentHUDValues, dormant=True)
        cmds.displayRGBColor('background', currentBGColorList[0], currentBGColorList[1], currentBGColorList[2])
        cmds.displayRGBColor('backgroundTop', currentBGTopColorList[0], currentBGTopColorList[1], currentBGTopColorList[2])
        cmds.displayRGBColor('backgroundBottom', currentBGBottomColorList[0], currentBGBottomColorList[1], currentBGBottomColorList[2])
        # Unhide hudList
        for i in range(len(hudList)):
            cmds.headsUpDisplay(hudList[i], edit=True, visible=currentHUDVisList[i])
        # remove hud texts
        for n in range(10, b):
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(n), remove=True)
        for c in range(len(camAttrList)):
            cmds.setAttr(cam+"."+camAttrList[c], camAttrVisList[c])
        cmds.setAttr(cam+".overscan", currentCamOverscan)
        cmds.camera(cam, edit=True, aspectRatio=currentCamAspectRatio)
        if currentCtrlLyrDisplay:
            cmds.setAttr(CTRL_LAYER+".hideOnPlayback", currentCtrlLyrDisplay)
        # force persp viewport to show file as default view options
        activeEditor = cmds.playblast(activeEditor=True)
        cmds.modelEditor(activeEditor, edit=True, displayAppearance='smoothShaded', xray=False, wireframeOnShaded=False, occlusionCulling=False, shadows=False, polymeshes=True, pivots=False, nurbsCurves=True, jointXray=False, displayTextures=False, useDefaultMaterial=False, activeComponentsXray=False)


    def toHistory(self, scenePath, fileShortName, destinationFolder, *args):
        """ List all Maya scene files in the given scenePath.
            Put all found Maya scene file into the given destinationFolder, except the current given fileShortName.
        """
        sceneList = []
        folderContentObj = os.scandir(scenePath)
        for entry in folderContentObj :
            if entry.is_file():
                if not entry.name == fileShortName:
                    sceneList.append(entry.name)
        if sceneList:
            for item in sceneList:
                self.removeExistingArchived(destinationFolder, item)
                shutil.move(scenePath+"/"+item, destinationFolder)

    
    def toDropbox(self, file, toPath, *args):
        """ Just copy the zipped file to the destination path.
            TODO: Returns Dropbox's download link
        """        
        if file and toPath:
            shutil.copy2(file, toPath)

            # WIP
            #if host:
                #dropLink = "https://dl.dropboxusercontent.com/u/"+str(host)+file[file.rfind("/"):]+"?dl=1"
                #return dropLink


    def toOld(self, sourceFolder, publishFilename, assetNameList, destinationFolder, *args):
        """ Move all old publish files to the dpOld folder.
        """
        for item in assetNameList:
            if not item == publishFilename:
                self.removeExistingArchived(destinationFolder, item)
                shutil.move(sourceFolder+"/"+item, destinationFolder)


    def removeExistingArchived(self, filePath, fileName, *args):
        """ Delete existing same achived version in dpOld if it exists to avoid naming conflict when copying.
        """
        if os.path.isfile(filePath+"/"+fileName):
            os.remove(filePath+"/"+fileName)

    
    def toDiscord(self, webhook, messageText, *args):
        """
        """
        print("sending message to discord here...", webhook, messageText)

        #WIP
        if webhook and messageText:
            messageDic = {"content": messageText}
            messageData = json.dumps(messageDic).encode("utf8")
            try:
                req = request.Request(webhook, messageData, {"content-type": "application/json"})
                req.add_header("user-agent", "dpAR Discord Webhook")
                f = request.urlopen(req)
                print(f)
            except:
                print("no internet connection or fail request")
        else:
            print("no webhook or data to send to Discord")