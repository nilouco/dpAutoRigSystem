# importing libraries:
from maya import cmds
import zipfile
import shutil
import os
import time


DPPACKAGER_VERSION = 1.0


RIGPREVIEW = "Rigging preview"
CAMERA = "persp"
CAM_ROTX = -10
CAM_ROTY = 30

class Packager(object):
    def __init__(self, *args):
        """ 
        """
        # define variables
        print("loaded Packager here, merci...")


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
        


    def frameCameraToPublish(self, cam=CAMERA, rotX=CAM_ROTX, rotY=CAM_ROTY, focusGrp=None, *args):
        """ Prepare the given camera to frame correctly the viewport to publish.
        """
        # set up rotation
        cmds.setAttr(cam+".rotateX", rotX)
        cmds.setAttr(cam+".rotateY", rotY)
        # frame all
        cmds.viewFit(allObjects=True)
        posList = cmds.xform(cam, query=True, translation=True, worldSpace=True)
        if focusGrp:
            # frame render group
            cmds.select(focusGrp)
            cmds.viewFit()
            focusPosList = cmds.xform(cam, query=True, translation=True, worldSpace=True)
            # get average
            posList = [(posList[0]+focusPosList[0])/2, (posList[1]+focusPosList[1])/2, (posList[2]+focusPosList[2])/2]
        cmds.select(clear=True)
        cmds.camera(cam, edit=True, position=[posList[0], posList[1], posList[2]], rotation=[rotX, rotY, 0], aspectRatio=0.8)



    
    
    def imager(self, dpARVersion, studioName, projectName, assetName, modelVersion, rigVersion, publishVersion, destinationFolder, date, padding=3, rigPreview=RIGPREVIEW, cam=CAMERA, rotX=CAM_ROTX, rotY=CAM_ROTY, *args):
        """
        """
        # WIP
        # getting text data
        #
        #
        print ("Carreto's photo!")

        if dpARVersion:
            print("dpARVersion ===", dpARVersion)

        if studioName:
            print("Studio ===", studioName)

        if projectName:
            print("ProjectName ===", projectName)

        if assetName:
            print("AssetName ===", assetName)

        if modelVersion:
            print("ModelVersion ===", str(modelVersion).zfill(int(padding)))

        if rigVersion:
            print("RigVersion ===", str(rigVersion).zfill(int(padding)))

        if publishVersion:
            print("publishVersion ===", str(publishVersion).zfill(int(padding)))

        if destinationFolder:
            print("destinationFolder ===", destinationFolder)

        if date:
            print("date ===", date)

        print("rigPreview ===", rigPreview)


        
        



        return
        # WIP
        #
        ###
    #
    #   THANKS to:
    #       gfxhacks.com
    #
    #   Based on:
    #       https://gist.github.com/gfxhacks/f3e750f416f94952d7c9894ed8f78a71
    #   
    #   This module will capture and save a scene preview based on the active viewport. It will also input text about the file ready to publish.
    #	It uses playblast feature
    #
    ###

    
        # camera view
        
        

        # frameAll and store translations
        # get Render_Grp
        # check if there're children
        # if yes
        #       focus and store translations
        #       sum frameAll
        #       divide by 2
        # use result as translation position of the persp camera or another new camera in the modelPanel
        # 
        # rotation is arbitrary
        #   use constants variables to story it
        #       RX = -10
        #       RY = 30
        # 
        #cmds.camera("persp", edit=True, position=[15, 16, 27], rotation=[-10, 30, 0], aspectRatio=0.8)
        #
        # get screenShot
        #
        # back aspectRatio to default = 1.5

        # = enquadramento
        #aspectRatio = float ??? = 0.8
        # 
        # 

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
