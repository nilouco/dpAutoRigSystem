# importing libraries:
from maya import cmds
from maya import mel
from urllib import request
from importlib import reload
import json
import zipfile
import shutil
import os
import sys
import subprocess
import platform

RIGPREVIEW = "Rigging Preview"
CAMERA = "persp"
CAM_ROTX = -10
CAM_ROTY = 30
CAM_ROTZ = 0
CTRL_LAYER = "Ctrl_Lyr"
PREVIEW_WIDTH = 1024
PREVIEW_HEIGHT = 720



class Packager(object):
    def __init__(self, ar) -> None:
        self.ar = ar
        self.callback = None
    
    
    def create_zip_to_client(self, file_path, file_name, destination_folder, date=None):
        """ Create a zipped file with given file_path and file_name replacing the extention (.ma or .mb) to .zip
            Add date at the end of the file if it's given.
            Write the zip file in the destination_folder.
            Returns the zipFilePathName.
        """
        if date:
            zip_name = file_name[:-3]+"_"+date+".zip"
        else:
            zip_name = file_name[:-3]+".zip"
        zip = zipfile.ZipFile(destination_folder+"/"+zip_name, "w", zipfile.ZIP_DEFLATED)
        zip.write(filename=file_path+"/"+file_name, arcname=file_name)
        zip.close()
        return destination_folder+"/"+zip_name
        

    def frame_camera_to_publish(self, cam=CAMERA, rot_x=CAM_ROTX, rot_y=CAM_ROTY, rot_z=CAM_ROTZ, focus_it=None):
        """ Prepare the given camera to frame correctly the viewport to publish.
        """
        # set up rotation
        cmds.setAttr(cam+".rotateX", rot_x)
        cmds.setAttr(cam+".rotateY", rot_y)
        cmds.setAttr(cam+".rotateZ", rot_z)
        # frame all
        cmds.viewFit(allObjects=True)
        position = cmds.xform(cam, query=True, translation=True, worldSpace=True)
        if not focus_it:
            focus_it = self.ar.utils.get_node_by_message("renderGrp")
        if focus_it:
            # frame render group
            cmds.select(focus_it)
            cmds.viewFit()
            focus_position = cmds.xform(cam, query=True, translation=True, worldSpace=True)
            # get average
            position = [(position[0]+focus_position[0])/2, (position[1]+focus_position[1])/2, (position[2]+focus_position[2])/2]
        cmds.select(clear=True)
        cmds.refresh(force=True)
        cmds.camera(cam, edit=True, position=[position[0], position[1], position[2]], rotation=[rot_x, rot_y, 0])
        
        
    def get_display_rgb_colors(self, search_item):
        """ Return the RGB values listed for the given search_item from displayRGBColor Maya command.
        """
        for item in cmds.displayRGBColor(list=True):
            if search_item+' ' in item:
                values = item[:-1].split(" ")
                values = values[1:]
                values = [float(x) for x in values]
                return values

    
    def imager(self, pipe_data, version, date, rig_preview=RIGPREVIEW, cam=CAMERA, width_res=PREVIEW_WIDTH, height_res=PREVIEW_HEIGHT):
        """ Save a rigging preview screenShot file with the given informations.
            Returns the image preview path.
        """
        mel.eval('setNamedPanelLayout "Single Perspective View"; updateToolbox();')

        # store current user settings
        current_grid = cmds.grid(toggle=True, query=True)
        current_display_gradient = cmds.displayPref(displayGradient=True, query=True)
        current_hud_labels = cmds.displayColor('headsUpDisplayLabels', query=True, dormant=True)
        current_hud_values = cmds.displayColor('headsUpDisplayValues', query=True, dormant=True)
        current_bg_colors = self.get_display_rgb_colors('background')
        current_bg_top_colors = self.get_display_rgb_colors('backgroundTop')
        current_bg_bottom_colors = self.get_display_rgb_colors('backgroundBottom')
        current_remember_window = cmds.windowPref(query=True, enableAll=True)
        
        # save huds to hide:
        h = 0
        current_hud_visibilities = []
        huds = cmds.headsUpDisplay(listHeadsUpDisplays=True)
        for item in huds:
            current_hud_visibilities.append(cmds.headsUpDisplay(item, query=True, visible=True))
            cmds.headsUpDisplay(item, edit=True, visible=False)
            if cmds.headsUpDisplay(item, query=True, section=True) == 0:
                h += 1
        cam_vis_attributes = []
        cam_attributes = ["displayGateMask", "displayResolution", "displayFilmGate", "displayFieldChart", "displaySafeAction", "displaySafeTitle", "displayFilmPivot", "displayFilmOrigin", "depthOfField"]
        for attr in cam_attributes:
            cam_vis_attributes.append(cmds.getAttr(cam+"."+attr)) #current camera vis attr
            cmds.setAttr(cam+"."+attr, False)
        current_cam_overscan = cmds.getAttr(cam+".overscan")
        cmds.setAttr(cam+".overscan", 1.0)
        current_cam_aspect_ratio = cmds.camera(cam, query=True, aspectRatio=True)
        cmds.camera(cam, edit=True, aspectRatio=0.8)
        current_ctrl_layer_display = False
        if cmds.objExists(CTRL_LAYER):
            current_ctrl_layer_display = cmds.getAttr(CTRL_LAYER+".hideOnPlayback")
            cmds.setAttr(CTRL_LAYER+".hideOnPlayback", 0)

        # set up custom display settings
        cmds.grid(toggle=False)
        cmds.displayPref(displayGradient=pipe_data['b_i_degrade'])
        cmds.displayColor('headsUpDisplayLabels', 1, dormant=True) #black
        cmds.displayColor('headsUpDisplayValues', 1, dormant=True) #black
        cmds.displayRGBColor('background', 0.631, 0.631, 0.631)
        cmds.displayRGBColor('backgroundTop', 0.731, 0.731, 0.731)
        cmds.displayRGBColor('backgroundBottom', 0.42, 0.42, 0.42)

        # file information messages
        cmds.headsUpDisplay('HudRigPreviewTxt'+str(h+1), section=0, block=(h+1), labelFontSize="large", allowOverlap=True, label="")
        cmds.headsUpDisplay('HudRigPreviewTxt'+str(h+2), section=0, block=(h+2), labelFontSize="large", allowOverlap=True, label=rig_preview)
        b = h+3
        if pipe_data['b_i_maya']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label=cmds.about(installedVersion=True)) #Maya version
            b += 1
        if pipe_data['b_i_version']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label="dpAutoRigSystem "+version)
            b += 1
        if pipe_data['b_i_studio']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label=pipe_data['f_studio'])
            b += 1
        if pipe_data['b_i_project']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label=pipe_data['f_project'])
            b += 1
        if pipe_data['b_i_asset']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label=pipe_data['assetName'])
            b += 1
        if pipe_data['b_i_model']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label="Model "+str(pipe_data['modelVersion']).zfill(int(pipe_data['i_padding'])))
            b += 1
        if pipe_data['b_i_wip']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label="Rig "+str(pipe_data['rigVersion']).zfill(int(pipe_data['i_padding'])))
            b += 1
        if pipe_data['b_i_publish']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label="Publish "+str(pipe_data['publishVersion']).zfill(int(pipe_data['i_padding'])))
            b += 1
        if pipe_data['b_i_date']:
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(b), section=0, block=b, labelFontSize="large", allowOverlap=True, label=date)
            b += 1
            
        # create a new persp viewport window to get the image from it
        cmds.windowPref(enableAll=False) #to avoid open window with the wrong size
        self.ar.utils.close_ui('imager_win')
        cmds.window('imager_win', width=width_res, height=height_res, menuBarVisible=False, titleBar=True, visible=True, sizeable=False)
        cmds.paneLayout(parent='imager_win')
        imager_panel = cmds.modelPanel(menuBarVisible=False, label='imager_panel') #keep this variable to avoid find panel issue
        cmds.modelEditor(imager_panel, edit=True, displayAppearance='smoothShaded', allObjects=True)
        bar_layout = cmds.modelPanel(imager_panel, query=True, barLayout=True)
        cmds.frameLayout(bar_layout, edit=True, collapse=True)
        cmds.showWindow('imager_win')
        self.editor = cmds.modelPanel(imager_panel, query=True, modelEditor=True)
        cmds.modelEditor(self.editor, edit=True, activeView=True)
        cmds.setFocus(self.editor)

        # focus camera to frame the rig
        self.frame_camera_to_publish(cam)

        # take the screenShot
        current_frame = int(cmds.currentTime(query=True))
        destination_folder = pipe_data['toClientPath']
        if not destination_folder.endswith("/"):
            destination_folder += "/"
        export_path = "{}{}_{}.jpg".format(destination_folder, pipe_data['assetName'], rig_preview.replace(" ", ""))
        # playblast to make an image
        cmds.playblast(frame=current_frame, viewer=False, format="image", compression="jpg", showOrnaments=True, completeFilename=export_path, widthHeight=[width_res, height_res], percent=100, forceOverwrite=False, quality=100, editorPanelName=imager_panel)
        # clean up the UI
        cmds.deleteUI(imager_panel, panel=True)
        self.ar.utils.close_ui('imager_win')
        # back scene preferences to stored status
        cmds.camera(cam, edit=True, aspectRatio=1.5)
        cmds.grid(toggle=current_grid)
        cmds.displayPref(displayGradient=current_display_gradient)
        cmds.displayColor('headsUpDisplayLabels', current_hud_labels, dormant=True)
        cmds.displayColor('headsUpDisplayValues', current_hud_values, dormant=True)
        cmds.displayRGBColor('background', current_bg_colors[0], current_bg_colors[1], current_bg_colors[2])
        cmds.displayRGBColor('backgroundTop', current_bg_top_colors[0], current_bg_top_colors[1], current_bg_top_colors[2])
        cmds.displayRGBColor('backgroundBottom', current_bg_bottom_colors[0], current_bg_bottom_colors[1], current_bg_bottom_colors[2])
        cmds.windowPref(enableAll=current_remember_window)
        # Unhide huds
        for i in range(len(huds)):
            cmds.headsUpDisplay(huds[i], edit=True, visible=current_hud_visibilities[i])
        # remove hud texts
        for n in range((h+1), b):
            cmds.headsUpDisplay('HudRigPreviewTxt'+str(n), remove=True)
        for c in range(len(cam_attributes)):
            cmds.setAttr(cam+"."+cam_attributes[c], cam_vis_attributes[c])
        cmds.setAttr(cam+".overscan", current_cam_overscan)
        cmds.camera(cam, edit=True, aspectRatio=current_cam_aspect_ratio)
        if current_ctrl_layer_display:
            cmds.setAttr(CTRL_LAYER+".hideOnPlayback", current_ctrl_layer_display)
        # force persp viewport to show file as default view options
        active_editor = cmds.playblast(activeEditor=True)
        cmds.modelEditor(active_editor, edit=True, displayAppearance='smoothShaded', xray=False, wireframeOnShaded=False, occlusionCulling=False, shadows=False, polymeshes=True, pivots=False, nurbsCurves=True, jointXray=False, displayTextures=False, useDefaultMaterial=False, activeComponentsXray=False)
        return export_path


    def to_history(self, scene_path, file_shortname, destination_folder):
        """ List all Maya scene files in the given scene_path.
            Put all found Maya scene file into the given destination_folder, except the current given file_shortname.
        """
        scenes = []
        folder_content_obj = os.scandir(scene_path)
        for entry in folder_content_obj :
            if entry.is_file():
                if not entry.name == file_shortname:
                    scenes.append(entry.name)
        if scenes:
            for item in scenes:
                self.remove_existing_archived(destination_folder, item)
                shutil.move(scene_path+"/"+item, destination_folder)
        try: #to avoid have an issue when copying file to a non default pipeline asset name folder
            shutil.copy2(scene_path+"/"+file_shortname, destination_folder)
        except:
            pass

    
    def to_dropbox(self, file, to_path):
        """ Just copy the zipped file to the destination path.
            TODO: Returns Dropbox's download link
        """        
        if file and to_path:
            shutil.copy2(file, to_path)

            # WIP
            #if host:
                #dropLink = "https://dl.dropboxusercontent.com/u/"+str(host)+file[file.rfind("/"):]+"?dl=1"
                #return dropLink


    def to_old(self, source_folder, publish_filename, asset_names, destination_folder):
        """ Move all old publish files to the dpOld folder.
        """
        for item in asset_names:
            if not item == publish_filename:
                self.remove_existing_archived(destination_folder, item)
                shutil.move(source_folder+"/"+item, destination_folder)


    def remove_existing_archived(self, file_path, file_name):
        """ Delete existing same achived version in dpOld if it exists to avoid naming conflict when copying.
        """
        if os.path.isfile(file_path+"/"+file_name):
            os.remove(file_path+"/"+file_name)

    
    def to_discord(self, webhook, message_text):
        """ This method will send the given message text string to the Discord webhook.
        """
        if webhook and message_text:
            message_dic = {"content": message_text}
            message_data = json.dumps(message_dic).encode("utf8")
            try:
                req = request.Request(webhook, message_data, {"content-type": "application/json"})
                req.add_header("user-agent", "dpAR Discord Webhook")
                request.urlopen(req)
            except:
                return 'i088_internetFail'
        else:
            return 'i279_didntSend'


    def to_callback(self, callback_path, callback_file, data=None):
        """ Just eval the Python callback object.
            Call main method.
            Returns its result.
        """
        if not callback_path in sys.path:
           sys.path.append(callback_path)
        try:
            if not self.callback:
                #import publish_callback
                callback = __import__(callback_file, globals(), locals(), [], 0)
                #if self.ar.dev:
                reload(callback)
                self.callback = callback.Callback()
            return self.callback.main(data)
        except:
            pass


    def open_folder(self, path, *args):
        """ Just open a folder in exporer, finder, etc if it exists.
        """
        if os.path.exists(path):
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin": #Mac
                subprocess.Popen(['open', path])
            else: #Unix, Linux
                subprocess.Popen(['xdg-open', path])
        #
        #TODO
        # Move it to utils?
