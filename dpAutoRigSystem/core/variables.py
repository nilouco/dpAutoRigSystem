from dataclasses import dataclass, field

@dataclass
class Data:
    prefix: str = ""
    degree: str = ""

    dp_auto_rig_path: str = ""
    dp_auto_rig_filename: str = "dpAutoRig.py"
    workspace_control_name: str = "dpAutoRigSystemWC"

    language_default: str = "English"
    validator_default: str = "AllCheckOuts"
    curve_default: str = "Default"
    degree_default: str = "Preset_0"
    
    language_option_var: str = "dpAutoRigLastLanguage"
    validator_option_var: str = "dpAutoRigLastValidatorPreset"
    curve_option_var: str = "dpAutoRigLastCurvePreset"
    degree_option_var: str = "dpAutoRigLastCurveDegree"
    colorize_curve_option_var: str = "dpAutoRigLastColorizeCurve"
    supplementary_attr_option_var: str = "dpAutoRigLastSupplementaryAttr"
    display_joint_option_var: str = "dpAutoRigLastDisplayJoint"
    display_temp_grp_option_var: str = "dpAutoRigLastDisplayTempGrp"
    integrate_all_option_var: str = "dpAutoRigLastIntegrateAll"
    default_render_layer_option_var: str = "dpAutoRigLastDefaultRenderLayer"

    check_update_option_var: str = "dpAutoRigAutoCheckUpdate"
    check_update_last_option_var: str = "dpAutoRigLastDateAutoCheckUpdate"
    terms_cond_option_var: str = "dpAutoRigAgreeTermsCond"
    terms_cond_last_option_var: str = "dpAutoRigLastDateAgreeTermsCond"
    
    rig_type_biped: str = "biped"
    rig_type_quadruped: str = "quadruped"
    rig_type_default: str = "unknown" #support old guide system TODO: check using...

    base_name: str = "dpAR_"
    eye_name: str = "Eye"
    head_name: str = "Head"
    spine_name: str = "Spine"
    limb_name: str = "Limb"
    foot_name: str = "Foot"
    finger_name: str = "Finger"
    arm_name: str = "Arm"
    leg_name: str = "Leg"
    single_name: str = "Single"
    wheel_name: str = "Wheel"
    steering_name: str = "Steering"
    suspension_name: str = "Suspension"
    nose_name: str = "Nose"
    chain_name: str = "Chain"
    guide_base_name: str = "Guide_Base"
    plus_info_win_name: str = "dpPlusInfoWindow"
    color_override_win_name: str = "dpColorOverrideWindow"
    
    icons_folder: str = "Icons"
    tools_folder: str = "Tools"
    language_folder: str = "Languages"
    pipeline_folder: str = "Pipeline"
    standard_folder: str = "Modules.Standard"
    integrated_folder: str = "Modules.Integrated"
    template_folder: str = "library.template"
    curve_simple_folder: str = "Modules.Curves.Simple"
    curve_combined_folder: str = "Modules.Curves.Combined"
    curve_preset_folder: str = "Modules.Curves.Presets"
#    validator_folder: str = "Pipeline.Validator"
    checkin_folder: str = "Pipeline.Validator.CheckIn"
    checkout_folder: str = "Pipeline.Validator.CheckOut"
    validator_preset_folder: str = "Pipeline.Validator.Presets"
#    rebuilder_folder: str = "Pipeline.Rebuilder"
    start_folder: str = "Pipeline.Rebuilder.Start"
    source_folder: str = "Pipeline.Rebuilder.Source"
    setup_folder: str = "Pipeline.Rebuilder.Setup"
    deforming_folder: str = "Pipeline.Rebuilder.Deforming"
    custom_folder: str = "Pipeline.Rebuilder.Custom"
    checkaddon_folder: str = ""
    checkfinishing_folder: str = ""
    
    guide_base_attr: str = "guideBase"
    master_attr: str = "masterGrp"
    module_namespace_attr: str = "moduleNamespace"
    module_instance_info_attr: str = "moduleInstanceInfo"
    joint_end_attr: str = "JEnd"
    
    raw_url: str = "https://raw.githubusercontent.com/nilouco/dpAutoRigSystem/master/dpAutoRigSystem/dpAutoRig.py"
    github_url: str = "https://github.com/nilouco/dpAutoRigSystem"
    master_url: str = "https://github.com/nilouco/dpAutoRigSystem/zipball/master/"
    whats_changed_url: str = "https://github.com/nilouco/dpAutoRigSystem/commits/master"
    donate_url: str = "https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=nilouco%40gmail.com&item_name=Support+dpAutoRigSystem+and+Tutorials+by+Danilo+Pinheiro+%28nilouco%29&currency_code="
    location_url: str = "https://ipinfo.io/json"
    wiki_url: str = "https://github.com/nilouco/dpAutoRigSystem/wiki/"
    discord_url: str = "https://discord.com/api/webhooks"
    
    # TODO: change it to get raw file from master branch:
    #version_url: str = "https://github.com/nilouco/dpAutoRigSystem/raw/refs/heads/master/dpAutoRigSystem/version.py"
    version_url: str = "https://github.com/nilouco/dpAutoRigSystem/raw/refs/heads/699-dev-mode-reload/dpAutoRigSystem/version.py"
    
    temp_grp: str = "dpAR_Temp_Grp"
    guide_mirror_grp: str = "dpAR_GuideMirror_Grp"
    dp_data: str = "dpData"
    dp_log: str = "dpLog"
    dp_id: str = "dpID"

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
    supplementary_attr: int = 1
    display_temp_grp: int = 0
    integrate_all: int = 1
    default_render_layer: int = 1
    agree_terms: int = 1
    auto_check_update: int = 1
    select_change_job_id: int = 0

    transform_attrs: list = field(default_factory=lambda: ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ", "visibility"])
    rebuilder_layouts: list = field(default_factory=lambda: ["rebuilder_start_fl", "rebuilder_source_fl", "rebuilder_setup_fl", "rebuilder_deforming_fl", "rebuilder_custom_fl"])
    axis: list = field(default_factory=lambda: ["X", "Y", "Z"])
    degrees: list = field(default_factory=lambda: ['Preset_0', 'Linear_1', 'Cubic_3'])
    booleans: list = field(default_factory=lambda: [0, 1])
    
    to_ids: list = field(default_factory=list)
    
    created_guides: list = field(default_factory=list)
    lib_modules: list = field(default_factory=list)
    lib_instances: list = field(default_factory=list)
    standard_instances: list = field(default_factory=list)
    template_instances: list = field(default_factory=list)
    curve_simple_instances: list = field(default_factory=list)
    curve_combined_instances: list = field(default_factory=list)
    tools_instances: list = field(default_factory=list)
#    checkin_instances: list = field(default_factory=list)
#    checkout_instances: list = field(default_factory=list)
#    checkaddon_instances: list = field(default_factory=list)
#    checkfinishing_instances: list = field(default_factory=list)
#    rebuilder_instances: list = field(default_factory=list)
    start_instances: list = field(default_factory=list)
    source_instances: list = field(default_factory=list)
    setup_instances: list = field(default_factory=list)
    deforming_instances: list = field(default_factory=list)
    custom_instances: list = field(default_factory=list)

    lib: dict = field(default_factory=dict)
    lang: dict = field(default_factory=dict)
    lang_preset_data: dict = field(default_factory=dict)
    curve_preset: dict = field(default_factory=dict)
    curve_preset_data: dict = field(default_factory=dict)
    validator_preset: dict = field(default_factory=dict)
    validator_preset_data: dict = field(default_factory=dict)


    #
    # WIP = to delete after dev:
    #
    #raw_url: str = "https://raw.githubusercontent.com/nilouco/dpAutoRigSystem/699-dev-mode-reload/dpAutoRigSystem/dpAutoRig.py"
    #master_url: str = "https://github.com/nilouco/dpAutoRigSystem/zipball/699-dev-mode-reload/"
    #version_url: str = "https://github.com/nilouco/dpAutoRigSystem/raw/refs/heads/699-dev-mode-reload/dpAutoRigSystem/version.py"