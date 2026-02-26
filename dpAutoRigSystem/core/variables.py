from dataclasses import dataclass, field

@dataclass
class Data:
    language_default: str = "English"
    controller_default: str = "Default"
    validator_default: str = "AllCheckOuts"
    
    language_option_var: str = "dpAutoRigLastLanguage"
    controller_option_var: str = "dpAutoRigLastControllerPreset"
    validator_option_var: str = "dpAutoRigLastValidatorPreset"
    degree_option_var: str = "dpAutoRigLastDegreeOption"
    
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
    
    tools_folder: str = "Tools"
    language_folder: str = "Languages"
    standard_folder: str = "Modules/Standard"
    integrated_folder: str = "Modules/Integrated"
    curves_simple_folder: str = "Modules/Curves/Simple"
    curves_combined_folder: str = "Modules/Curves/Combined"
    curves_presets_folder: str = "Modules/Curves/Presets"
    validator_folder: str = "Pipeline/Validator"
    checkin_folder: str = "Pipeline/Validator/CheckIn"
    checkout_folder: str = "Pipeline/Validator/CheckOut"
    validator_presets_folder: str = "Pipeline/Validator/Presets"
    rebuilder_folder: str = "Pipeline/Rebuilder"
    start_folder: str = "Pipeline/Rebuilder/Start"
    source_folder: str = "Pipeline/Rebuilder/Source"
    setup_folder: str = "Pipeline/Rebuilder/Setup"
    deforming_folder: str = "Pipeline/Rebuilder/Deforming"
    custom_folder: str = "Pipeline/Rebuilder/Custom"
    
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
    
    temp_grp: str = "dpAR_Temp_Grp"
    guide_mirror_grp: str = "dpAR_GuideMirror_Grp"
    dp_data: str = "dpData"
    dp_log: str = "dpLog"
    dp_id: str = "dpID"

    loaded_path: bool = False
    loaded_standard: bool = False
    loaded_integrated: bool = False
    loaded_curve_shape: bool = False
    loaded_combined: bool = False
    loaded_tools: bool = False
    loaded_checkin: bool = False
    loaded_checkout: bool = False
    loaded_addon: bool = False
    loaded_finishing: bool = False
    loaded_rebuilder: bool = False
    loaded_start: bool = False
    loaded_source: bool = False
    loaded_setup: bool = False
    loaded_deforming: bool = False
    loaded_custom: bool = False
    rebuilding: bool = False
    modules_collapse_status: bool = False
    rebuilders_collapse_status: bool = False
    collapse_edit_sel_mod: bool = False

    degree_option: int = 0
    auto_check_update: int = 1
    agree_terms: int = 1

    transform_attrs: list = field(default_factory=lambda: ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ", "visibility"])
    rebuilder_layouts: list = field(default_factory=lambda: ["rebuilder_start_fl", "rebuilder_source_fl", "rebuilder_setup_fl", "rebuilder_deforming_fl", "rebuilder_custom_fl"])
    axis: list = field(default_factory=lambda: ["X", "Y", "Z"])
    to_ids: list = field(default_factory=list)
    control_instances: list = field(default_factory=list)
    checkin_instances: list = field(default_factory=list)
    checkout_instances: list = field(default_factory=list)
    checkaddon_instances: list = field(default_factory=list)
    checkfinishing_instances: list = field(default_factory=list)
    rebuilder_instances: list = field(default_factory=list)