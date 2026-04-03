#import libraries
from maya import cmds
from importlib import reload



class Maker(object):
    def __init__(self, ar):
        self.ar = ar


    def create_raw_guide(self, module, *args):
        #
        # TODO: review after rename modules without dp
        #
        if not module.startswith("dp"):
            module = "dp"+module

        mod = self.import_module(module, self.ar.data.standard_folder)
        return [mod, mod.build_raw_guide()]


    def import_module(self, module, folder):
        path = f"{self.ar.utils.findEnv('PYTHONPATH', 'dpAutoRigSystem')}.{folder.replace('/', '.')}"
        imported_module = __import__(path+"."+module, {}, {}, [module])
        if self.ar.dev:
            reload(imported_module)
        return getattr(imported_module, imported_module.CLASS_NAME)(self.ar)
    

    def set_new_guide(self, module, name, t=(0, 0, 0), r=(0, 0, 0), s=(1, 1, 1), size=1, radius=2, end=1.3, mirror=None, flip=1, deformed=0, indSkin=0, annot=1, annot_pos=None, parent=None, progress=True):
        """ Creates a new standard guide, set the given values and returns a list with the imported module and the created guide.
        """
        if progress:
            self.ar.utils.setProgress(self.ar.data.lang['m094_doing']+name)
            cmds.refresh()
        mod, guide = self.create_raw_guide(module)
        mod.editGuideModuleName(name)
        cmds.setAttr(mod.radiusCtrl+".translateX", radius)
        cmds.setAttr(mod.cvEndJoint+".translateZ", end)
        cmds.setAttr(guide+".translateX", t[0])
        cmds.setAttr(guide+".translateY", t[1])
        cmds.setAttr(guide+".translateZ", t[2])
        cmds.setAttr(guide+".rotateX", r[0])
        cmds.setAttr(guide+".rotateY", r[1])
        cmds.setAttr(guide+".rotateZ", r[2])
        cmds.setAttr(guide+".scaleX", s[0])
        cmds.setAttr(guide+".scaleY", s[1])
        cmds.setAttr(guide+".scaleZ", s[2])
        cmds.setAttr(guide+".shapeSize", size)
        if mirror:
            mod.changeMirror(mirror)
            cmds.setAttr(guide+".flip", flip)
        if deformed:
            cmds.setAttr(guide+".deformedBy", deformed)
        if indSkin:
            cmds.setAttr(guide+".indirectSkin", indSkin)
        cmds.setAttr(guide+".displayAnnotation", annot)
        cmds.setAttr(guide+"_Ant.visibility", annot)
        if annot_pos:
            cmds.setAttr(mod.annotation+".translateX", annot_pos[0])
            cmds.setAttr(mod.annotation+".translateY", annot_pos[1])
            cmds.setAttr(mod.annotation+".translateZ", annot_pos[2])
        else:
            cmds.setAttr(mod.annotation+".translateX", 0)
            cmds.setAttr(mod.annotation+".translateY", radius)
            cmds.setAttr(mod.annotation+".translateZ", 0)
        if parent:
            cmds.parent(guide, parent, absolute=True)
        return [mod, guide]
