# importing libraries:
from maya import cmds
from ....library.base import action

# global variables to this module:
CLASS_NAME = "Proxy"
TITLE = "m230_proxy"
DESCRIPTION = "m231_proxyDesc"
WIKI = "07-‐-Validator#-proxy-creator"

PROXIED = "dpProxied"
NO_PROXY = "dpDoNotProxyIt"



class Proxy(action.BaseAction):
    def __init__(self, ar):
        action.BaseAction.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, WIKI)
        self.repeated_names = []
    

    def run_action(self, first_mode=True, inputs=None, *args):
        """ Main method to process this validator instructions.
            It's in verify mode by default.
            If first_mode parameter is False, it'll run in fix mode.
            Returns dataLog with the validation result as:
                - checked_items = node list of checked items
                - found_issues = True if an issue was found, False if there isn't an issue for the checked node
                - good_results = True if well done, False if we got an error
                - messages = reported text
        """
        # starting
        self.first_mode = first_mode
        self.cleanup_to_start()

        # ---
        # --- validator code --- beginning
        if not cmds.file(query=True, reference=True):
            self.skinclusters = []
            proxy_grp = None
            if inputs:
                proxy_grp = inputs[0]
            else:
                proxy_grp = self.ar.utils.get_node_by_message("proxyGrp")
                if not proxy_grp:
                    if cmds.objExists("Proxy_Grp"):
                        proxy_grp = "Proxy_Grp"
            if proxy_grp:
                if not PROXIED in cmds.listAttr(proxy_grp):
                    meshes = cmds.listRelatives(proxy_grp, children=True, allDescendents=True, type="mesh")
                    if not meshes:
                        render_grp = self.ar.utils.get_node_by_message("renderGrp")
                        if not render_grp:
                            if cmds.objExists("Render_Grp"):
                                render_grp = "Render_Grp"
                        if render_grp:
                            meshes = cmds.listRelatives(render_grp, children=True, allDescendents=True, fullPath=True, type="mesh")
                    if meshes:
                        # find meshes to generate proxy
                        to_proxy_items = []
                        for mesh in meshes:
                            if len(cmds.ls(mesh)) == 1:
                                mesh_transforms = cmds.listRelatives(mesh, parent=True, fullPath=True, type="transform")
                                if mesh_transforms:
                                    if not mesh_transforms[0] in to_proxy_items:
                                        if not NO_PROXY in cmds.listAttr(mesh_transforms):
                                            if not PROXIED in cmds.listAttr(mesh_transforms):
                                                to_proxy_items.append(mesh_transforms[0])
                        if to_proxy_items:
                            self.ar.utils.set_progress(max=len(to_proxy_items), add_one=False, add_number=False)
                            self.checked_items.append(proxy_grp)
                            self.found_issues.append(True)
                            if self.first_mode:
                                self.good_results.append(False)
                            else: #fix
                                try:
                                    for source_transform in to_proxy_items:
                                        source_shortname = self.ar.utils.get_short_name(source_transform)
                                        self.ar.utils.set_progress(self.ar.data.lang[self.title]+": "+source_shortname)
                                        self.create_proxy(source_transform, source_shortname, proxy_grp)
                                    self.proxy_integration(proxy_grp)
                                    self.good_results.append(True)
                                    self.messages.append(self.ar.data.lang['v004_fixed']+": "+proxy_grp)
                                except:
                                    self.good_results.append(False)
                                    self.messages.append(self.ar.data.lang['v005_cantFix']+": "+proxy_grp)
                        else:
                            self.found_issues.append(False)
                            self.good_results.append(True)
                    else:
                        self.not_found_node(proxy_grp)
                else:
                    self.not_found_node(proxy_grp)
            else:
                self.not_found_node(proxy_grp)
        else:
            self.fail_io(self.ar.data.lang['r072_noReferenceAllowed'])
        # --- validator code --- end
        # ---
        
        # finishing
        self.update_action_buttons()
        self.report_log()
        self.end_progress()
        return self.log_data


    def create_proxy(self, source, shortname, grp):
        """ Creates a proxy setup from the given source transform and put it into the given grp group.
        """
        try:
            input_deformers = cmds.findDeformers(source)
        except:
            return
        skincluster_node = None
        if input_deformers:
            for deformer_node in input_deformers:
                if cmds.objectType(deformer_node) == "skinCluster":
                    skincluster_node = deformer_node
                    break
        if skincluster_node:
            self.skinclusters.append(skincluster_node)
            weigthed_influences = cmds.skinCluster(skincluster_node, query=True, weightedInfluence=True)
            if weigthed_influences:
                # get data and store it into a data
                index_joint_data = {}
                source_faces = cmds.ls(source+".f[*]", flatten=True, long=True)
                for i, idx in enumerate(source_faces):
                    percents = cmds.skinPercent(skincluster_node, source+".f["+str(i)+"]", ignoreBelow=0.1, transform=None, query=True)
                    if percents:
                        index_joint_data[i] = percents[0]
                        if not len(percents) == 1:
                            joint_values = []
                            for item in percents:
                                joint_values.append(cmds.skinPercent(skincluster_node, source+".f["+str(i)+"]", ignoreBelow=0.1, transform=item, query=True))
                            index_joint_data[i] = percents[joint_values.index(max(joint_values))]
                for jnt in weigthed_influences:
                    node_faces = []
                    skinned_faces = []
                    # data analisis
                    for j in list(index_joint_data.keys()):
                        if index_joint_data[j] == jnt:
                            skinned_faces.append(j)
                    if skinned_faces:
                        # filter lists
                        faces = [w.replace(source+".f[", "") for w in source_faces]
                        faces = [int(w.replace("]", "")) for w in faces]
                        if faces:
                            for v in reversed(skinned_faces):
                                faces.pop(v)
                        if faces:
                            for n in faces:
                                node_faces.append(source+".f["+str(n)+"]")
                        # create proxy geometry
                        dup = cmds.duplicate(source, name=shortname+"_"+str(self.repeated_names.count(shortname)).zfill(2)+"_"+jnt+"_Pxy")[0]
                        self.repeated_names.append(shortname)
                        self.ar.utils.remove_user_defined_attr(dup)
                        self.ar.utils.delete_orig_shape(dup)
                        self.ar.utils.remove_from_sets(dup)
                        if node_faces:
                            dup_faces = [w.replace(source, dup) for w in node_faces]
                            cmds.delete(dup_faces)
                        self.ar.ctrls.set_lock_hide([dup], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], l=False)
                        cmds.xform(dup, pivots=cmds.xform(jnt, worldSpace=True, rotatePivot=True, query=True))
                        cmds.parent(dup, jnt)
                        cmds.scriptEditorInfo(suppressWarnings=True)
                        cmds.makeIdentity(dup, apply=True, translate=True, rotate=True, scale=True)
                        cmds.scriptEditorInfo(suppressWarnings=False)
                        self.check_reverse_normal(dup, jnt)
                        cmds.connectAttr(jnt+".worldMatrix", dup+".offsetParentMatrix", force=True)
                        cmds.parent(dup, grp)
                        self.ar.utils.set_attr_values([dup], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'], [0, 0, 0, 0, 0, 0, 1, 1, 1])
                        self.ar.ctrls.set_lock_hide([dup], ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'])
                        draw_override_items = cmds.listConnections(dup+".drawOverride", source=True, destination=False, plugs=True)
                        if draw_override_items:
                            # remove from display layer
                            cmds.disconnectAttr(draw_override_items[0], dup+".drawOverride")
                        cmds.setAttr(dup+".overrideEnabled", 1)
                        cmds.setAttr(dup+".overrideDisplayType", 2) #reference
                        self.reconnect_visibility(source, dup)
            cmds.addAttr(source, longName=PROXIED, attributeType="bool", defaultValue=1)
        source_parent = cmds.listRelatives(source, parent=True, fullPath=True, type="transform")
        if source_parent:
            if source_parent[0] == grp:
                cmds.delete(source)


    def proxy_integration(self, grp):
        """ Add attributes, connect to deformer nodeState if possible to disable them in order to get performance.
        """
        if not PROXIED in cmds.listAttr(grp):
            cmds.addAttr(grp, longName=PROXIED, attributeType="bool", defaultValue=1)
        option_ctrl = self.ar.utils.get_node_by_message("optionCtrl")
        if option_ctrl:
            # prepare option_ctrl to deformers connections
            cmds.setAttr(option_ctrl+".proxy", channelBox=True)
            cmds.addAttr(option_ctrl, longName="proxyRevOutput", attributeType="bool")
            proxy_rev = cmds.createNode("reverse", name="Proxy_Rev")
            cmds.connectAttr(option_ctrl+".proxy", proxy_rev+".inputX", force=True)
            cmds.connectAttr(proxy_rev+".outputX", option_ctrl+".proxyRevOutput", force=True)
            deformers = self.skinclusters
            defs = ["blendShape", "wrap", "ffd", "wire", "shrinkWrap", "sculpt", "morph"]
            for deform in defs:
                deformers.extend(cmds.ls(type=deform) or [])
            if deformers:
                for deform_node in deformers:
                    try:
                        cmds.connectAttr(option_ctrl+".proxy", deform_node+".nodeState") #don't force it please
                    except:
                        pass #maybe it already has a connection from another node
            # hide controllers and meshes
            self.connect_proxy_vis(option_ctrl, "mesh")
            self.connect_proxy_vis(option_ctrl, "tweaks")
            self.connect_proxy_vis(option_ctrl, "Tweaks") #fixed camelCase for earlier rig versions v4.03.32
            self.connect_proxy_vis(option_ctrl, suffix="Facial_Ctrls_Grp")
            self.connect_proxy_vis(option_ctrl, suffix="Deformer_Ctrl_Grp")
        self.ar.ctrls.color_shape([grp], [1, 0.5, 0.5], outliner=True) #red


    def connect_proxy_vis(self, ctrl, attr=None, suffix=None):
        """ Create a reverseNode to plug it to the inverse visibility proxy option to the matching nodes.
        """
        if attr or suffix:
            if attr:
                if attr in cmds.listAttr(ctrl):
                    connections = cmds.listConnections(ctrl+"."+attr, source=False, destination=True, plugs=True) #list before connect on it
                    vis_md = cmds.createNode("multiplyDivide", name="Proxy_"+(attr[0].upper()+attr[1:])+"_Vis_MD")
                    cmds.connectAttr(ctrl+".proxyRevOutput", vis_md+".input1X", force=True)
                    cmds.connectAttr(ctrl+"."+attr, vis_md+".input2X", force=True)
                    if connections:
                        for plug_dest in connections:
                            cmds.connectAttr(vis_md+".outputX", plug_dest, force=True)
            else:
                suffix_items = cmds.ls("*"+suffix, selection=False)
                if suffix_items:
                    for item in suffix_items:
                        cmds.connectAttr(ctrl+".proxyRevOutput", item+".visibility", force=True)


    def reconnect_visibility(self, sourceMesh, proxyMesh):
        """ Check if there's sourceMesh visibility connection then connect the new proxyMesh visibility too, if so.
        """
        vis_connections = cmds.listConnections(sourceMesh+".visibility", source=True, destination=False, plugs=True)
        if vis_connections:
            cmds.connectAttr(vis_connections[0], proxyMesh+".visibility", force=True)


    def check_reverse_normal(self, dup, jnt):
        """ Verify if there're negative scale joint attributes and reverse the normal mesh if true.
        """
        for axis in ['sx', 'sy', 'sz']:
            if cmds.getAttr(jnt+'.'+axis) < 0:
                cmds.polyNormal(dup, normalMode=0, userNormalMode=0, constructionHistory=False)
                break
