from dataclasses import dataclass, field


@dataclass
class Data:
    prefix: str = ''
    degree: str = ''

    dp_auto_rig_path: str = ''
    dp_auto_rig_filename: str = 'dpAutoRig.py'
    workspace_control_name: str = 'dpAutoRigSystemWC'

    language_default: str = 'english'
    validator_default: str = 'all_check_outs'
    curve_default: str = 'default'
    degree_default: str = 'preset_0'
    template_default: str = 'v001_template'
    
    language_option_var: str = 'dpAutoRigLastLanguage'
    validator_option_var: str = 'dpAutoRigLastValidatorPreset'
    curve_option_var: str = 'dpAutoRigLastCurvePreset'
    degree_option_var: str = 'dpAutoRigLastCurveDegree'
    colorize_curve_option_var: str = 'dpAutoRigLastColorizeCurve'
    supplementary_attr_option_var: str = 'dpAutoRigLastSupplementaryAttr'
    display_joint_option_var: str = 'dpAutoRigLastDisplayJoint'
    display_sub_shape_option_var: str = 'dpAutoRigLastDisplaySubShape'
    display_temp_grp_option_var: str = 'dpAutoRigLastDisplayTempGrp'
    compose_all_option_var: str = 'dpAutoRigLastComposeAll'
    default_render_layer_option_var: str = 'dpAutoRigLastDefaultRenderLayer'

    check_update_option_var: str = 'dpAutoRigAutoCheckUpdate'
    check_update_last_option_var: str = 'dpAutoRigLastDateAutoCheckUpdate'
    terms_cond_option_var: str = 'dpAutoRigAgreeTermsCond'
    terms_cond_last_option_var: str = 'dpAutoRigLastDateAgreeTermsCond'
    
    rig_type_biped: str = 'biped'
    rig_type_quadruped: str = 'quadruped'

    master_name: str = 'All_Grp'
    base_name: str = 'dpAR_'
    eye_name: str = 'Eye'
    head_name: str = 'Head'
    spine_name: str = 'Spine'
    limb_name: str = 'Limb'
    foot_name: str = 'Foot'
    finger_name: str = 'Finger'
    arm_name: str = 'Arm'
    leg_name: str = 'Leg'
    single_name: str = 'Single'
    wheel_name: str = 'Wheel'
    steering_name: str = 'Steering'
    suspension_name: str = 'Suspension'
    nose_name: str = 'Nose'
    chain_name: str = 'Chain'
    guide_base_name: str = 'Guide_Base'
    
    plus_info_win_name: str = 'plus_info_win'
    color_override_win_name: str = 'color_override_win'
    info_win_name: str = 'info_win'
    new_asset_win_name: str = 'new_asset_win'
    replace_data_win_name: str = 'replace_data_win'
    select_asset_win_name: str = 'select_asset_win'
    save_version_win_name: str = 'save_version_win'
    terms_cond_win_name: str = 'terms_cond_win'
    update_win_name: str = 'update_win'
    donate_win_name: str = 'donate_win'
    copy_paste_attr_win_name: str = 'copy_paste_attr_win'
    correction_manager_win_name: str = 'correction_manager_win'
    custom_attr_win_name: str = 'custom_attr_win'
    custom_attr_add_win_name: str = 'custom_attr_add_win'
    custom_attr_remove_win_name: str = 'custom_attr_remove_win'
    custom_attr_id_win_name: str = 'custom_attr_id_win'
    facial_connection_win_name: str = 'facial_connection_win'
    joint_display_win_name: str = 'joint_display_win'
    motion_capture_win_name: str = 'motion_capture_win'
    one_skeleton_win_name: str = 'one_skeleton_win'
    pipeliner_win_name: str = 'pipeliner_win'
    select_asset_checkbox_win_name: str = 'select_asset_checkbox_win'
    publisher_win_name: str = 'publisher_win'
    success_published_win_name: str = 'success_published_win'
    renamer_win_name: str = 'renamer_win'
    reorder_attr_win_name: str = 'reorder_attr_win'
    rivet_win_name: str = 'rivet_win'
    target_mirror_win_name: str = 'target_mirror_win'
    update_guides_win_name: str = 'update_guides_win'
    update_summary_win_name: str = 'update_summary_win'
    value_editor_win_name: str = 'value_editor_win'
    zipper_win_name: str = 'zipper_win'
    
    icons_folder: str = 'icons'
    tools_folder: str = 'library.tool'
    language_folder: str = 'library.language'
    pipeline_folder: str = 'library.pipeline'
    standard_folder: str = 'library.standard'
    template_folder: str = 'library.template'
    curve_simple_folder: str = 'library.curve.simple'
    curve_combined_folder: str = 'library.curve.combined'
    curve_preset_folder: str = 'library.preset.curve'
    facial_preset_folder: str = 'library.preset.facial'
    checkin_folder: str = 'library.validate.checkin'
    checkout_folder: str = 'library.validate.checkout'
    prepare_anim_folder: str = 'library.validate.prepare_anim'
    validate_preset_folder: str = 'library.preset.validate'
    start_folder: str = 'library.rebuild.start'
    source_folder: str = 'library.rebuild.source'
    setup_folder: str = 'library.rebuild.setup'
    deforming_folder: str = 'library.rebuild.deforming'
    custom_folder: str = 'library.rebuild.custom'
    checkaddon_folder: str = ""
    checkfinishing_folder: str = ""
    
    guide_base_attr: str = 'guideBase'
    master_attr: str = 'masterGrp'
    module_namespace_attr: str = 'moduleNamespace'
    module_instance_info_attr: str = 'moduleInstanceInfo'
    joint_end_attr: str = 'JEnd'
    
    raw_url: str = 'https://raw.githubusercontent.com/nilouco/dpAutoRigSystem/master/dpAutoRigSystem/dpAutoRig.py'
    github_url: str = 'https://github.com/nilouco/dpAutoRigSystem'
    master_url: str = 'https://github.com/nilouco/dpAutoRigSystem/zipball/master/'
    whats_changed_url: str = 'https://github.com/nilouco/dpAutoRigSystem/commits/master'
    donate_url: str = 'https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=nilouco%40gmail.com&item_name=Support+dpAutoRigSystem+and+Tutorials+by+Danilo+Pinheiro+%28nilouco%29&currency_code='
    location_url: str = 'https://ipinfo.io/json'
    wiki_url: str = 'https://github.com/nilouco/dpAutoRigSystem/wiki/'
    discord_url: str = 'https://discord.com/api/webhooks'
    version_url: str = 'https://github.com/nilouco/dpAutoRigSystem/raw/refs/heads/master/dpAutoRigSystem/version.py'
    
    temp_grp: str = 'dpAR_Temp_Grp'
    guide_mirror_grp: str = 'dpAR_GuideMirror_Grp'
    dp_data: str = 'dpData'
    dp_log: str = 'dpLog'
    dp_id: str = 'dpID'

    ui_state: bool = False
    verbose: bool = False
    loaded_path: bool = False
    rebuilding: bool = False
    modules_collapse_status: bool = False
    rebuilders_collapse_status: bool = True
    collapse_edit_sel_mod: bool = False
    first_time_open: bool = False
    
    degree_option: int = 0
    colorize_curve: int = 1
    display_joint: int = 1
    display_sub_shape: int = 1
    display_temp_grp: int = 0
    supplementary_attr: int = 1
    compose_all: int = 1
    default_render_layer: int = 1
    agree_terms: int = 1
    auto_check_update: int = 1
    select_change_job_id: int = 0

    transform_attrs: list = field(default_factory=lambda: ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ', 'visibility'])
    rebuilder_layouts: list = field(default_factory=lambda: ['rebuilder_start_fl', 'rebuilder_source_fl', 'rebuilder_setup_fl', 'rebuilder_deforming_fl', 'rebuilder_custom_fl'])
    drivenkey_types: list = field(default_factory=lambda: ['animCurveUA', 'animCurveUL', 'animCurveUT', 'animCurveUU'])
    axes: list = field(default_factory=lambda: ['X', 'Y', 'Z'])
    degrees: list = field(default_factory=lambda: ['preset_0', 'linear_1', 'cubic_3'])
    booleans: list = field(default_factory=lambda: [0, 1])
    facial_brow_targets: list = field(default_factory=lambda: ['BrowFrown', 'BrowSad', 'BrowDown', 'BrowUp'])
    facial_eyelid_targets: list = field(default_factory=lambda: [None, None, 'EyelidsClose', 'EyelidsOpen'])
    facial_mouth_targets: list = field(default_factory=lambda: ['MouthNarrow', 'MouthWide', 'MouthSad', 'MouthSmile'])
    facial_lips_targets: list = field(default_factory=lambda: ['R_LipsSide', 'L_LipsSide', 'LipsDown', 'LipsUp', 'LipsBack', 'LipsFront'])
    facial_sneer_targets: list = field(default_factory=lambda: ['R_Sneer', 'L_Sneer', None, None, 'UpperLipBack', 'UpperLipFront'])
    facial_grimace_targets: list = field(default_factory=lambda: ['R_Grimace', 'L_Grimace', None, None, 'LowerLipBack', 'LowerLipFront'])
    facial_face_targets: list = field(default_factory=lambda: ['L_Puff', 'R_Puff', 'Pucker', 'SoftSmile', 'BigSmile', 'AAA', 'OOO', 'UUU', 'FFF', 'MMM'])
    mirror_menus: list = field(default_factory=lambda: ['off', 'X', 'Y', 'Z', 'XY', 'XZ', 'YZ', 'XYZ'])
    directions: list = field(default_factory=lambda: ['+X', '-X', '+Y', '-Y', '+Z', '-Z'])
    axis_orders: list = field(default_factory=lambda: ['XYZ', 'YZX', 'ZXY', 'XZY', 'YXZ', 'ZYX'])
    facial_connect_types: list = field(default_factory=lambda: ['bsType', 'jointsType'])
    interpolations: list = field(default_factory=lambda: ['Linear', 'Smooth', 'Spline'])
    
    to_ids: list = field(default_factory=list)
    
    lib_instances: list = field(default_factory=list)
    guide_instances: list = field(default_factory=list)

    lib: dict = field(default_factory=dict)
    lang: dict = field(default_factory=dict)
    lang_preset_data: dict = field(default_factory=dict)
    curve_preset: dict = field(default_factory=dict)
    curve_preset_data: dict = field(default_factory=dict)
    validator_preset: dict = field(default_factory=dict)
    validator_preset_data: dict = field(default_factory=dict)


    #
    # TODO: WIP = to delete after dev:
    #
    #raw_url: str = 'https://raw.githubusercontent.com/nilouco/dpAutoRigSystem/699-dev-mode-reload/dpAutoRigSystem/dpAutoRig.py'
    #master_url: str = 'https://github.com/nilouco/dpAutoRigSystem/zipball/699-dev-mode-reload/'
    #version_url: str = 'https://github.com/nilouco/dpAutoRigSystem/raw/refs/heads/699-dev-mode-reload/dpAutoRigSystem/version.py'