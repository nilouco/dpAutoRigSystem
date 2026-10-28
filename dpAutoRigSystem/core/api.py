class API:
    def __init__(self, ar):
        self.ar = ar


    def guide(self, module, name=None, t=(0, 0, 0), r=(0, 0, 0), s=(1, 1, 1), size=1, radius=2, end=1.3, mirror=None, flip=1, deformed=0, indSkin=0, annot=1, parent=None, progress=False):
        if name:
            return self.ar.maker.set_new_guide(module, name, t, r, s, size, radius, end, mirror, flip, deformed, indSkin, annot, parent, progress)
        return self.ar.maker.create_raw_guide(module)


    def template(self, name):
        template = self.ar.config.get_instance(name, [self.ar.data.template_folder])
        if template:
            template.build_template()


    def tool(self, name):
        tool = self.ar.config.get_instance(name, [self.ar.data.tools_folder])
        if tool:
            tool.build_tool()
            return tool


    def curve(self, name, ui=False):
        curve = self.ar.config.get_instance(name, [self.ar.data.curve_simple_folder, self.ar.data.curve_combined_folder])
        if curve:
            curve.cv_main(use_ui=ui)
            return curve


    def validate(self, name):
        """ Getter validate instance.
        """
        for item in self.ar.config.get_validator_instances():
            if item.name == name:
                return item


    def validate_checked(self, verify=True):
        """ If verify is False, then it'll run the fix mode.
        """
        self.ar.publisher.run_checked_validators(first_mode=verify)


    def publish(self, comments="API"):
        self.ar.publisher.run_publishing(comments=comments)


    def publish_batch(self, assets, comments="Batch - API"):
        for asset in assets:
            self.ar.pipeliner.load_asset(file=asset)
            self.ar.publisher.run_publishing(comments=comments)


    def rebuild(self, name):
        """ Getter rebuild instance.
        """
        for item in self.ar.config.get_rebuilder_instances():
            if item.name == name:
                return item


    def rebuilder_split_data(self):
        self.ar.ui_manager.run_selected_actions(self.ar.config.get_rebuilder_instances(), True, True, action_type='r000_rebuilder')


    def rebuilder_rebuild(self):
        self.ar.ui_manager.run_selected_actions(self.ar.config.get_rebuilder_instances(), False, True, action_type='r000_rebuilder')


    def rig_all(self):
        self.ar.filler.fill_created_guides()
        self.ar.maker.rig_all()


    def skin_it(self, geos, joints, mode=None):
        """ mode:
                - Add
                - Remove
                - None = create a new skinCluster
        """
        self.ar.skin.run_skinning(geos, joints, mode)


    def copy_skin(self, source, destinations):
        items = [source]
        items.extend(destinations)
        self.ar.skin.copy_skin_from_one_source(items)
