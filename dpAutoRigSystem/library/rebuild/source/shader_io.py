# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "ShaderIO"
TITLE = "r008_shaderIO"
DESCRIPTION = "r009_shaderIODesc"
WIKI = "10-‐-Rebuilder#-shader"



class ShaderIO(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.set_action_type("r000_rebuilder")
        self.io_folder = "s_shaderIO"
        self.start_name = "dpShader"
        self.maya_default_shader = "openPBRSurface"
    

    def run_action(self, first_mode=True, inputs=None, *args):
        """ Main method to process this validator instructions.
            It's in export mode by default.
            If first_mode parameter is False, it'll run in import mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start(True)
        
        # ---
        # --- rebuilder code --- beginning
        if not cmds.file(query=True, reference=True):
            if self.ar.pipeliner.check_asset_context():
                self.io_path = self.get_io_path(self.io_folder)
                if self.io_path:
                    self.custom_attributes = ["aiKdInd", "azimuthalWidthG", "azimuthalShiftG", "intensityG", "longitudinalWidthTRT", "longitudinalShiftTRT", "intensityTRT", 
                                            "longitudinalWidthR", "longitudinalShiftR", "intensityR", "longitudinalWidthTT", "intensityTT", "longitudinalShiftTT", "azimuthalWidthTT",
                                            "longitudinalWidthTT", "angle", "spreadX", "spreadY", "fresnelRefractiveIndex", "specularShift", "scatter", "scatterPower", 
                                            "tubeDirection", "highlightSize", "roughness", "refractions", "refractiveIndex", "refractionLimit", "reflectionLimit", "reflectivity",
                                            "specularRollOff", "eccentricity", "diffuse", "cosinePower", "base", "diffuseRoughness", "metalness", "specular", "specularRoughness",
                                            "specularIOR", "specularAnisotropy", "specularRotation", "transmission", "transmissionDepth", "transmissionScatterAnisotropy", 
                                            "transmissionDispersion", "transmissionExtraRoughness", "subsurface", "subsurfaceScale", "subsurfaceAnisotropy", "coat", "coatRoughness", 
                                            "coatIOR", "coatAnisotropy", "coatRotation", "coatAffectColor", "coatAffectRoughness", "sheen", "sheenRoughness", "emission", "thinFilmThickness",
                                            "thinFilmIOR", "thinWalled",
                                            "baseWeight", "baseDiffuseRoughness", "baseMetalness", "specularWeight", "specularRoughnessAnisotropy", "transmissionWeight",
                                            "transmissionDispersionScale", "transmissionDispersionAbbeNumber", "subsurfaceWeight", "subsurfaceScatterAnisotropy", "fuzzWeight",
                                            "fuzzRoughness", "coatWeight", "coatRoughnessAnisotropy", "coatDarkening", "thinFilmWeight", "emissionLuminance", "geometryThinWalled"]
                    self.vector_colors = ["outColor", "outTransparency", "outGlowColor", "outMatteOpacity", "colorTT", "colorTRT", "tipColorD", "rootColorD", "whiteness", "reflectedColor",
                                            "specularColor", "transmissionColor", "transmissionScatter", "subsurfaceColor", "coatColor", "sheenColor", "emissionColor",
                                            "ambientColor", "incandescence", "baseColor", "fuzzColor"]
                    self.changed_types = ["subsurfaceRadius", "subsurfaceRadiusScale"]
                    if self.first_mode: #export
                        shaders = None
                        if inputs:
                            shaders = inputs
                        else:
                            shaders = self.get_used_materials()
                        if shaders:
                            self.export_json_file(self.get_shader_data(shaders))
                        else:
                            self.maybe_done_io("Shading")
                    else: #import
                        shader_data = self.import_latest_json_file(self.get_exported_items())
                        if shader_data:
                            try:
                                self.import_shader(shader_data)
                            except Exception as e:
                                self.fail_io(self.ar.data.lang['r032_notImportedData']+": "+str(e))
                        else:
                            self.maybe_done_io(self.ar.data.lang['r007_notExportedData'])
                else:
                    self.fail_io(self.ar.data.lang['r010_notFoundPath'])
            else:
                self.fail_io(self.ar.data.lang['r027_noAssetContext'])
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- rebuilder code --- end
        # ---

        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        self.refresh_view()
        return self.log_data


    def get_shader_data(self, shaders):
        """ Return shader data dictionary to export.
        """
        shader_data = {}
        self.ar.ui_manager.set_progress(max=len(shaders), add_one=False, add_number=False)
        for shader in shaders:
            self.ar.ui_manager.set_progress(self.ar.data.lang[self.title]+": "+shader)
            file_node = None
            texture = None
            color = None
            cmds.hyperShade(objects=shader)
            assigned_items = cmds.ls(selection=True)
            if assigned_items:
                # color
                color_attr = "color"
                if not color_attr in cmds.listAttr(shader): #support standardShader
                    color_attr = "baseColor"
                if color_attr in cmds.listAttr(shader):
                    shader_connections = cmds.listConnections(shader+"."+color_attr, destination=False, source=True)
                    if shader_connections:
                        file_node = shader_connections[0]
                        texture = cmds.getAttr(file_node+".fileTextureName")
                    else:
                        color = cmds.getAttr(shader+"."+color_attr)[0]
                # transparency
                transparency_attr = "transparency"
                if not transparency_attr in cmds.listAttr(shader): #support standardShader
                    transparency_attr = "opacity"
                    if not transparency_attr in cmds.listAttr(shader): #support openPBRShader
                        transparency_attr = "geometryOpacity"
                        if not transparency_attr in cmds.listAttr(shader): #support surfaceShader
                            transparency_attr = "outTransparency"
                            transparency = cmds.getAttr(shader+"."+transparency_attr)[0]
                        else:
                            transparency = cmds.getAttr(shader+"."+transparency_attr)
                    else:
                        transparency = cmds.getAttr(shader+"."+transparency_attr)[0]
                else:
                    transparency = cmds.getAttr(shader+"."+transparency_attr)[0]
                # data dictionary to export
                shader_data[shader] = {"assigned"        : assigned_items,
                                    "color"            : color,
                                    "colorAttr"        : color_attr,
                                    "fileNode"         : file_node,
                                    "material"         : cmds.objectType(shader),
                                    "texture"          : texture,
                                    "transparency"     : transparency,
                                    "transparencyAttr" : transparency_attr
                                    }
                # custom shader attributes
                for attr in self.custom_attributes:
                    if attr in cmds.listAttr(shader):
                        shader_data[shader][attr] = cmds.getAttr(shader+"."+attr)
                # custom vector color attributes
                for attr in self.vector_colors:
                    if attr in cmds.listAttr(shader):
                        shader_data[shader][attr] = cmds.getAttr(shader+"."+attr)[0]
                # changed type shader attributes
                for attr in self.changed_types:
                    if attr in cmds.listAttr(shader):
                        shader_data[shader][attr] = cmds.getAttr(shader+"."+attr)
            cmds.select(clear=True)
        return shader_data


    def import_shader(self, shader_data):
        """ Import the shaders from given shader dictionary.
        """
        not_found_meshs = []
        # rebuild shaders
        for item in shader_data.keys():
            if not cmds.objExists(item):
                shader = cmds.shadingNode(shader_data[item]['material'], asShader=True, name=item)
                if shader_data[item]['fileNode']:
                    file_node = cmds.shadingNode("file", asTexture=True, isColorManaged=True, name=shader_data[item]['file_node'])
                    cmds.connectAttr(file_node+".outColor", shader+"."+shader_data[item]['colorAttr'], force=True)
                    cmds.setAttr(file_node+".fileTextureName", shader_data[item]['texture'], type="string")
                else:
                    colors = shader_data[item]['color']
                    cmds.setAttr(shader+"."+shader_data[item]['colorAttr'], colors[0], colors[1], colors[2], type="double3")
                transparencies = shader_data[item]['transparency']
                if shader_data[item]['transparencyAttr'] == "geometryOpacity": #support OpenPBRShader
                    cmds.setAttr(shader+"."+shader_data[item]['transparencyAttr'], transparencies)
                else:
                    cmds.setAttr(shader+"."+shader_data[item]['transparencyAttr'], transparencies[0], transparencies[1], transparencies[2], type="double3")
                for attr in self.custom_attributes:
                    if attr in cmds.listAttr(shader) and shader_data[item][attr]:
                        cmds.setAttr(shader+"."+attr, shader_data[item][attr])
                for attr in self.vector_colors:
                    if attr in cmds.listAttr(shader) and shader_data[item][attr]:
                        cmds.setAttr(shader+"."+attr, shader_data[item][attr][0], shader_data[item][attr][1], shader_data[item][attr][2], type="double3")
                for attr in self.changed_types: #exception to conform Maya2024 standardSurface and Maya2026 openPBRshader - float or vector attribute types
                    if attr in cmds.listAttr(shader) and shader_data[item][attr]:
                        try:
                            cmds.setAttr(shader+"."+attr, shader_data[item][attr])
                        except:
                            cmds.setAttr(shader+"."+attr, shader_data[item][attr][0][0], shader_data[item][attr][0][1], shader_data[item][attr][0][2], type="double3")
            # apply shader to meshes
            for mesh in shader_data[item]['assigned']:
                if cmds.objExists(mesh):
                    if cmds.about(version=True) >= "2024": #Maya version
                        cmds.hyperShade(assign=item, geometries=mesh)
                    else:
                        cmds.select(mesh)
                        cmds.hyperShade(assign=item)
                else:
                    not_found_meshs.append(mesh)
        cmds.select(clear=True)
        if not_found_meshs:
            self.fail_io(self.ar.data.lang['r011_notFoundMesh']+", ".join(not_found_meshs))
        else:
            self.well_done_io(self.latest_data_file)
