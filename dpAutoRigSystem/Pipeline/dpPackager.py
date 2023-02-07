# importing libraries:
from maya import cmds
from maya import mel
import zipfile
import shutil
import os
import time


DPPACKAGER_VERSION = 1.0


RIGPREVIEW = "Rigging Preview"
CAMERA = "persp"
CAM_ROTX = -10
CAM_ROTY = 30

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
        if focusIt:
            # frame render group
            cmds.select(focusIt)
            cmds.viewFit()
            focusPosList = cmds.xform(cam, query=True, translation=True, worldSpace=True)
            # get average
            posList = [(posList[0]+focusPosList[0])/2, (posList[1]+focusPosList[1])/2, (posList[2]+focusPosList[2])/2]
        cmds.select(clear=True)
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

    
    def imager(self, destinationFolder, dpARVersion=None, studioName=None, projectName=None, assetName=None, modelVersion=None, rigVersion=None, publishVersion=None, date=None, padding=3, rigPreview=RIGPREVIEW, cam=CAMERA, *args):
        """ Save a rigging preview screenShot file with the given informations.
            Thanks Caio Hidaka for the help in this code!
        """
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

        # set up custom display settings
        cmds.grid(toggle=False)
        cmds.displayPref(displayGradient=True)
        cmds.displayColor('headsUpDisplayLabels', 1, dormant=True) #black
        cmds.displayColor('headsUpDisplayValues', 1, dormant=True) #black
        cmds.displayRGBColor('background', 0.631, 0.631, 0.631)
        cmds.displayRGBColor('backgroundTop', 0.8, 0.782, 0.76)
        cmds.displayRGBColor('backgroundBottom', 0.45, 0.42975, 0.405)

        # file information messages
        cmds.headsUpDisplay('HudRigPreviewTxt0', section=1, block=0, labelFontSize="large", allowOverlap=True, label="")
        cmds.headsUpDisplay('HudRigPreviewTxt1', section=1, block=1, labelFontSize="large", allowOverlap=True, label=rigPreview)
        b = 2
        if dpARVersion:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=1, block=b, labelFontSize="large", allowOverlap=True, label="dpAutoRigSystem v"+dpARVersion)
            b += 1
        if studioName:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=1, block=b, labelFontSize="large", allowOverlap=True, label=studioName)
            b += 1
        if projectName:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=1, block=b, labelFontSize="large", allowOverlap=True, label=projectName)
            b += 1
        if assetName:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=1, block=b, labelFontSize="large", allowOverlap=True, label=assetName)
            b += 1
        if modelVersion:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=1, block=b, labelFontSize="large", allowOverlap=True, label="Model "+str(modelVersion).zfill(int(padding)))
            b += 1
        if rigVersion:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=1, block=b, labelFontSize="large", allowOverlap=True, label="Rig "+str(rigVersion).zfill(int(padding)))
            b += 1
        if publishVersion:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=1, block=b, labelFontSize="large", allowOverlap=True, label="Publish "+str(publishVersion).zfill(int(padding)))
            b += 1
        if date:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=1, block=b, labelFontSize="large", allowOverlap=True, label=date)
            b += 1
            
        


        
        
        

        

        panel = cmds.playblast(activeEditor=True)
        print("panel =", panel)
        if "|" in panel:
            panel = panel[panel.rfind("|")+1:]
        camera = cmds.modelPanel(panel, query=True, camera=True)





        print("camera", camera)
        



        # center panel on screen
        imagerWindow = cmds.window(width=960, height=720, menuBarVisible=False, titleBar=True, visible=True)
        cmds.paneLayout(parent=imagerWindow)
        panel = cmds.modelPanel(menuBarVisible=False, label='dpImager')
        cmds.modelEditor(panel, edit=True, displayAppearance='smoothShaded')
        bar_layout = cmds.modelPanel(panel, q=True, barLayout=True)
        cmds.frameLayout(bar_layout, edit=True, collapse=True)
        cmds.showWindow(imagerWindow)
        editor = cmds.modelPanel(panel, query=True, modelEditor=True)
        cmds.modelEditor(editor, edit=True, activeView=True)
        cmds.refresh(force=True)

#        try:
#            yield panel
#        finally:
#            # Delete the panel to fix memory leak (about 5 mb per capture)
#            cmds.deleteUI(panel, panel=True)
#            cmds.deleteUI(window)




        return
        
        # check film gate - viewport
        #
        # get screenShot
        #
        # get active viewport panel
        #panel = cmds.playblast(activeEditor=True)
        # take the screenShot
        currentFrame = int(cmds.currentTime(query=True))

        width = 576
        height = 720
        if not destinationFolder.endswith("/"):
            destinationFolder += "/"
        exportPath = "{}{}_{}.jpg".format(destinationFolder, assetName, rigPreview.replace(" ", ""))

        cmds.playblast(frame=currentFrame, viewer=False, format="image", compression="jpg", showOrnaments=True, completeFilename=exportPath, widthHeight=[width, height], percent=100, forceOverwrite=False, quality=100)


        
        
        
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
        for n in range(b):
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(n), remove=True)
        for c in range(len(camAttrList)):
            cmds.setAttr(cam+"."+camAttrList[c], camAttrVisList[c])
        cmds.setAttr(cam+".overscan", currentCamOverscan)
        cmds.camera(cam, edit=True, aspectRatio=currentCamAspectRatio)

#        cmds.deleteUI(panel, panel=True)
#        cmds.deleteUI(imagerWindow)
        return


        # set screenshot dimensions:
        width = 960
        height = 960
        
        # get active viewport panel:
#        panel = cmds.getPanel(withFocus=True)
        panel = cmds.playblast(activeEditor=True)
        
        # throw error if active panel is not a viewport:
#        if "modelPanel" not in cmds.getPanel(typeOf=panel):
#        	cmds.confirmDialog(title='Error!', message='Please select a viewport panel first.', button=['Ok'], defaultButton='Ok', dismissString='No')	
#        	raise RuntimeError('Error: Please select a viewport panel, then try again.')
    
        # get the version of the file:
        fileNameAll = cmds.file(query=True, sceneName=True, shortName=True)
        fileName = fileNameAll.split(".ma")[0]
        if fileName.find("rig") == 0:
            fileName = fileName.split("rig_")[1]
            assetName = fileName.split("_")[0]
            if assetName.find("_")!= -1:
                assetName = assetName.split("_")[1]
            versionNumber = fileName.split("_")[1]
        elif fileName.rfind("_rig_") != -1:
            versionNumber = fileName.split("_rig_")[1]
            assetName = fileName.split("_rig_")[0]
            if assetName.find("_")!= -1:
                assetName = assetName.split("_")[1]
        else:
            assetName = fileName.rsplit("_")[0]
            versionNumber = fileName.rsplit("_")[-1]
        
        # get project name:
        pipelineDrive = "R:/"
        filePath = cmds.file(query=True, sceneName=True)
        if pipelineDrive in filePath:
            studioName = filePath.split(pipelineDrive)[1]
            studioName = studioName[:studioName.find("/")]
            studioPath = pipelineDrive+studioName
            projectName = filePath.split(studioPath+"/")[1]
            projectName = projectName[:projectName.find("/")]
        else:
            projectName = "projectName"
            
    
        # set new path where previews will be saved to:
        path = filePath.split(fileNameAll)[0]+"dpData/"
    
        # get name of current camera:
        cam = cmds.modelEditor(panel, query=True, camera=True)
        
        # get current timestamp:
        currentTime = time.localtime()
        currentDate = time.strftime("%Y-%m-%d", currentTime)
    
        # construct full path:
        rigPreviewTxt = "RigPreview"
        fullPath = "{}{}_{}.jpg".format(path, assetName, rigPreviewTxt)
        
        # Create path if it doesn't exist:
        if not os.path.exists(path):
            os.makedirs(path)
        
        # Save hudList to hide:
        hudList = cmds.headsUpDisplay(lh=True)
        hudVisList = []
        for item in hudList:
            hudVis = cmds.headsUpDisplay(item, query=True, vis=True)
            hudVisList.append(hudVis)
            cmds.headsUpDisplay(item, edit=True, vis=False)
            
        # File Informations message:
        cmds.headsUpDisplay('HudRigPreviewTxt0', section=1, block=0, labelFontSize="large", allowOverlap=True, label="")
        cmds.headsUpDisplay('HudRigPreviewTxt1', section=1, block=1, labelFontSize="large", allowOverlap=True, label=projectName)
        cmds.headsUpDisplay('HudRigPreviewTxt2', section=1, block=2, labelFontSize="large", allowOverlap=True, label=assetName)
        cmds.headsUpDisplay('HudRigPreviewTxt3', section=1, block=3, labelFontSize="large", allowOverlap=True, label=versionNumber)
        cmds.headsUpDisplay('HudRigPreviewTxt4', section=1, block=4, labelFontSize="large", allowOverlap=True, label=rigPreviewTxt)
        cmds.headsUpDisplay('HudRigPreviewTxt5', section=1, block=5, labelFontSize="large", allowOverlap=True, label=currentDate)
    
        # run playblast for current viewport:
        curFrame = int(cmds.currentTime(query=True))
        cmds.playblast(fr=curFrame, showOrnaments=True, v=False, fmt="image", c="jpg", orn=False, cf=fullPath, wh=[width,height], p=100, fo=False, qlt=100)
        
        # Unhide hudList:
        for idx in range(len(hudList)):
            cmds.headsUpDisplay(hudList[idx], edit=True, vis=hudVisList[idx])
    
        # log path to console for reference:
        print("Image preview saved as: " + fullPath)

        cmds.headsUpDisplay('HudRigPreviewTxt0', remove=True)
        cmds.headsUpDisplay('HudRigPreviewTxt1', remove=True)
        cmds.headsUpDisplay('HudRigPreviewTxt2', remove=True)
        cmds.headsUpDisplay('HudRigPreviewTxt3', remove=True)
        cmds.headsUpDisplay('HudRigPreviewTxt4', remove=True)
        cmds.headsUpDisplay('HudRigPreviewTxt5', remove=True)







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
                shutil.move(sourceFolder+"/"+item, destinationFolder)
