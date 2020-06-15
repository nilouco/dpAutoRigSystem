# importing libraries:
import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import dpAutoRigSystem.Modules.Library.dpControls as dpControls
import dpAutoRigSystem.Modules.Library.dpUtils as utils

# global variables to this module:
CLASS_NAME = "FacialControl"
TITLE = "m085_facialCtrl"
DESCRIPTION = "m086_facialCtrlDesc"
ICON = "/Icons/dp_facialCtrl.png"


HEAD_BSNAME = "Head_Recept_BS"
BODY_BSNAME = "Body_Recept_BS"
BROW_TGTLIST = ["BrowFrown", "BrowSad", "BrowDown", "BrowUp"]
EYELID_TGTLIST = [None, None, "EyelidsClose", "EyelidsOpen"]
MOUTH_TGTLIST = ["MouthNarrow", "MouthWide", "MouthSad", "MouthSmile"]
LIPS_TGTLIST = ["Pucker", "LipsOpen", "LipsDown", "LipsUp"]
SNEER_TGTLIST = ["R_Sneer", "L_Sneer", None, None]
GRIMACE_TGTLIST = ["R_Grimace", "L_Grimace", None, None]
FACE_TGTLIST = ["L_Puff", "R_Puff", "AAA", "OOO", "UUU", "FFF", "MMM"]
TYPE_BS = "typeBS"
TYPE_JOINTS = "typeJoints"
MIDDLE = "Middle"
SIDED = "Sided"

DPFC_VERSION = "1.8"


class FacialControl():
    def __init__(self, dpUIinst, langDic, langName, presetDic, presetName, *args, **kwargs):
        # defining variables:
        self.dpUIinst = dpUIinst
        self.langDic = langDic
        self.langName = langName
        self.presetDic = presetDic
        self.presetName = presetName
        self.ctrls = dpControls.ControlClass(self.dpUIinst, self.presetDic, self.presetName)
        self.facialCtrlsGrp = self.langDic[self.langName]["c059_facial"]+"_Ctrls_Grp"
        self.headCtrl = self.dpGetHeadCtrl()
        self.jntTargetList = []
        self.RmVNumber = 0
        # redefining Tweaks variables:
        self.dpInitTweaksVariables()
        # call main function:
        self.dpFacialControlUI(self)
        # load fields:
        self.userType = TYPE_BS
        self.bsNode = None
        if cmds.objExists(BODY_BSNAME):
            self.dpLoadBSTgtList(BODY_BSNAME)
        elif cmds.objExists(HEAD_BSNAME):
            self.dpLoadBSTgtList(HEAD_BSNAME)
        self.dpLoadJointNode(self.tweaksNameList)
        # declaring gaming dictionary:
        self.dpInitTweaksDic()
    
    
    def dpInitTweaksVariables(self, *args):
        # part names:
        mainName = self.langDic[self.langName]['c058_main']
        tweaksName = self.langDic[self.langName]['m081_tweaks']
        middleName = self.langDic[self.langName]['c029_middle']
        eyebrowName = self.langDic[self.langName]['c041_eyebrow']
        cornerName = self.langDic[self.langName]['c043_corner']
        upperName = self.langDic[self.langName]['c044_upper']
        lowerName = self.langDic[self.langName]['c045_lower']
        lipName = self.langDic[self.langName]['c039_lip']
        squintName = self.langDic[self.langName]['c054_squint']
        cheekName = self.langDic[self.langName]['c055_cheek']
        # eyebrows names:
        self.eyebrowMiddleName = tweaksName+"_"+middleName+"_"+eyebrowName
        self.eyebrowName1 = tweaksName+"_"+eyebrowName+"_01"
        self.eyebrowName2 = tweaksName+"_"+eyebrowName+"_02"
        self.eyebrowName3 = tweaksName+"_"+eyebrowName+"_03"
        # squints names:
        self.squintName1 = tweaksName+"_"+squintName+"_01"
        self.squintName2 = tweaksName+"_"+squintName+"_02"
        self.squintName3 = tweaksName+"_"+squintName+"_03"
        # cheeks names:
        self.cheekName1 = tweaksName+"_"+cheekName+"_01"
        # lip names:
        self.upperLipMiddleName = tweaksName+"_"+upperName+"_"+lipName+"_00"
        self.upperLipName1 = tweaksName+"_"+upperName+"_"+lipName+"_01"
        self.upperLipName2 = tweaksName+"_"+upperName+"_"+lipName+"_02"
        self.lowerLipMiddleName = tweaksName+"_"+lowerName+"_"+lipName+"_00"
        self.lowerLipName1 = tweaksName+"_"+lowerName+"_"+lipName+"_01"
        self.lowerLipName2 = tweaksName+"_"+lowerName+"_"+lipName+"_02"
        self.lipCornerName = tweaksName+"_"+cornerName+"_"+lipName
        # list:
        self.tweaksNameList = [self.eyebrowMiddleName, self.eyebrowName1, self.eyebrowName2, self.eyebrowName3, \
                                self.squintName1, self.squintName2, self.squintName3, \
                                self.cheekName1, \
                                self.upperLipMiddleName, self.upperLipName1, self.upperLipName2, self.lowerLipMiddleName, self.lowerLipName1, self.lowerLipName2, self.lipCornerName]
        
    
    def dpInitTweaksDic(self, *args):
        self.tweaksDic = {
                            "BrowFrown" : {
                                            MIDDLE : {
                                                        self.eyebrowMiddleName : {
                                                                                    "ty" : [0, -1.2],
                                                                                    "tz" : [0, 0.5]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.eyebrowName1 : {
                                                                                "tx" : [0, -1.8],
                                                                                "ty" : [0, -2.5],
                                                                                "tz" : [0, 0.8],
                                                                                "rz" : [0, 15.5]
                                                                                },
                                                        self.eyebrowName2 : {
                                                                                "tx" : [0, -0.8],
                                                                                "ty" : [0, 0.68],
                                                                                "tz" : [0, 0.2],
                                                                                "rz" : [0, 9.1]
                                                                                },
                                                        self.eyebrowName3 : {
                                                                                "tx" : [0, 0.2],
                                                                                "ty" : [0, 0.54]
                                                                                }
                                                    }
                                          },
                            "BrowSad" : {
                                            MIDDLE : {
                                                        self.eyebrowMiddleName : {
                                                                                    "ty" : [0, 0.8],
                                                                                    "tz" : [0, 0.2]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.eyebrowName1 : {
                                                                                "tx" : [0, -2.0],
                                                                                "ty" : [0, 3.0],
                                                                                "tz" : [0, 0.4],
                                                                                "rz" : [0, -9.3]
                                                                                },
                                                        self.eyebrowName2 : {
                                                                                "tx" : [0, -0.96],
                                                                                "ty" : [0, 0.06],
                                                                                "tz" : [0, 0.16]
                                                                                },
                                                        self.eyebrowName3 : {
                                                                                "ty" : [0, -0.5]
                                                                                }
                                                    }
                                         },
                            "BrowDown" : {
                                            MIDDLE : {
                                                        self.eyebrowMiddleName : {
                                                                                    "ty" : [0, -0.4],
                                                                                    "tz" : [0, 0.4]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.eyebrowName1 : {
                                                                                "ty" : [0, -1.76],
                                                                                "tz" : [0, 0.76]
                                                                                },
                                                        self.eyebrowName2 : {
                                                                                "ty" : [0, -2.52],
                                                                                "tz" : [0, 1.08]
                                                                                },
                                                        self.eyebrowName3 : {
                                                                                "ty" : [0, -1.76],
                                                                                "tz" : [0, 0.76]
                                                                                }
                                                    }
                                         },
                            "BrowUp" : {
                                            MIDDLE : {
                                                        self.eyebrowMiddleName : {
                                                                                    "ty" : [0, 1.0],
                                                                                    "tz" : [0, -0.3]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.eyebrowName1 : {
                                                                                "ty" : [0, 4.0],
                                                                                "tz" : [0, -0.6]
                                                                                },
                                                        self.eyebrowName2 : {
                                                                                "ty" : [0, 4.0],
                                                                                "tz" : [0, -0.6]
                                                                                },
                                                        self.eyebrowName3 : {
                                                                                "ty" : [0, 4.0],
                                                                                "tz" : [0, -0.6]
                                                                                }
                                                    }
                                         },
                            "MouthNarrow" : {
                                            SIDED : {
                                                        self.upperLipName1 : {
                                                                                "tx" : [0, -1.42],
                                                                                "tz" : [0, 0.26]
                                                                                },
                                                        self.upperLipName2 : {
                                                                                "tx" : [0, -3.28],
                                                                                "tz" : [0, 0.16]
                                                                                },
                                                        self.lowerLipName1 : {
                                                                                "tx" : [0, -1.42],
                                                                                "tz" : [0, 0.26]
                                                                                },
                                                        self.lowerLipName2 : {
                                                                                "tx" : [0, -3.28],
                                                                                "tz" : [0, 0.16]
                                                                                },
                                                        self.lipCornerName : {
                                                                                "tx" : [0, -4.56],
                                                                                "tz" : [0, 0.02]
                                                                                }
                                                    }
                                         },
                            "MouthWide" : {
                                            SIDED : {
                                                        self.upperLipName1 : {
                                                                                "tx" : [0, 2.72],
                                                                                "tz" : [0, -0.24]
                                                                                },
                                                        self.upperLipName2 : {
                                                                                "tx" : [0, 4.56],
                                                                                "tz" : [0, -0.84]
                                                                                },
                                                        self.lowerLipName1 : {
                                                                                "tx" : [0, 2.72],
                                                                                "tz" : [0, -0.24]
                                                                                },
                                                        self.lowerLipName2 : {
                                                                                "tx" : [0, 4.56],
                                                                                "tz" : [0, -0.84]
                                                                                },
                                                        self.lipCornerName : {
                                                                                "tx" : [0, 6.62],
                                                                                "tz" : [0, -1.58]
                                                                                },
                                                        self.cheekName1 :    {
                                                                                "tx" : [0, 2.26],
                                                                                "tz" : [0, -1.18]
                                                                             }
                                                    }
                                         },
                            "MouthSad" : {
                                            SIDED : {
                                                        self.upperLipName1 : {
                                                                                "ty" : [0, -0.96],
                                                                                "rz" : [0, -7.6]
                                                                                },
                                                        self.upperLipName2 : {
                                                                                "ty" : [0, -1.62],
                                                                                "tz" : [0, 0.3],
                                                                                "rz" : [0, -16.1]
                                                                                },
                                                        self.lowerLipName1 : {
                                                                                "ty" : [0, -0.96],
                                                                                "rz" : [0, -7.6]
                                                                                },
                                                        self.lowerLipName2 : {
                                                                                "ty" : [0, -1.62],
                                                                                "tz" : [0, 0.3],
                                                                                "rz" : [0, -16.1]
                                                                                },
                                                        self.lipCornerName : {
                                                                                "ty" : [0, -3.5],
                                                                                "tz" : [0, 0.44],
                                                                                "rz" : [0, -30.0]
                                                                                }
                                                    }
                                         },
                            "MouthSmile" : {
                                            SIDED : {
                                                        self.upperLipName1 : {
                                                                                "ty" : [0, 0.52],
                                                                                "rz" : [0, 5.0]
                                                                                },
                                                        self.upperLipName2 : {
                                                                                "ty" : [0, 1.5],
                                                                                "tz" : [0, -0.26],
                                                                                "rz" : [0, 18.0]
                                                                                },
                                                        self.lowerLipName1 : {
                                                                                "ty" : [0, 0.52],
                                                                                "rz" : [0, 5.0]
                                                                                },
                                                        self.lowerLipName2 : {
                                                                                "ty" : [0, 1.5],
                                                                                "tz" : [0, -0.26],
                                                                                "rz" : [0, 18.0]
                                                                                },
                                                        self.lipCornerName : {
                                                                                "ty" : [0, 3.9],
                                                                                "tz" : [0, -0.62],
                                                                                "rz" : [0, 37.0]
                                                                                },
                                                        self.squintName1 : {
                                                                                "tx" : [0, -0.18],
                                                                                "ty" : [0, 0.26]
                                                                                },
                                                        self.squintName2 : {
                                                                                "ty" : [0, 0.74]
                                                                                },
                                                        self.squintName3 : {
                                                                                "tx" : [0, 0.16],
                                                                                "ty" : [0, 0.16],
                                                                                "tz" : [0, -0.46]
                                                                                }
                                                    }
                                         },
                            "Pucker" : {
                                            MIDDLE : {
                                                        self.upperLipMiddleName : {
                                                                                    "tz" : [0, 0.92]
                                                                                    },
                                                        self.lowerLipMiddleName : {
                                                                                    "tz" : [0, 0.92]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.upperLipName1 : {
                                                                                "tx" : [0, -1.96],
                                                                                "tz" : [0, 0.94]
                                                                                },
                                                        self.upperLipName2 : {
                                                                                "tx" : [0, -4.2],
                                                                                "tz" : [0, 0.14]
                                                                                },
                                                        self.lowerLipName1 : {
                                                                                "tx" : [0, -1.96],
                                                                                "tz" : [0, 0.94]
                                                                                },
                                                        self.lowerLipName2 : {
                                                                                "tx" : [0, -4.2],
                                                                                "tz" : [0, 0.14]
                                                                                },
                                                        self.lipCornerName : {
                                                                                "tx" : [0, -5.84],
                                                                                "tz" : [0, 1.82]
                                                                                }
                                                    }
                                            
                                       }, 
                            "LipsOpen" : {
                                            MIDDLE : {
                                                        self.upperLipMiddleName : {
                                                                                    "ty" : [0, 1.66]
                                                                                    },
                                                        self.lowerLipMiddleName : {
                                                                                    "ty" : [0, -1.66]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.upperLipName1 : {
                                                                                "ty" : [0, 1.66]
                                                                                },
                                                        self.upperLipName2 : {
                                                                                "ty" : [0, 1.12],
                                                                                "rz" : [0, -8.0]
                                                                                },
                                                        self.lowerLipName1 : {
                                                                                "ty" : [0, -1.66]
                                                                                },
                                                        self.lowerLipName2 : {
                                                                                "ty" : [0, -1.12],
                                                                                "rz" : [0, 8.0]
                                                                                }
                                                    }
                                            
                                          },
                            "LipsDown" : {
                                            MIDDLE : {
                                                        self.upperLipMiddleName : {
                                                                                    "ty" : [0, -3.12]
                                                                                    },
                                                        self.lowerLipMiddleName : {
                                                                                    "ty" : [0, -3.12]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.upperLipName1 : {
                                                                                "ty" : [0, -3.12]
                                                                                },
                                                        self.upperLipName2 : {
                                                                                "ty" : [0, -3.12]
                                                                                },
                                                        self.lowerLipName1 : {
                                                                                "ty" : [0, -3.12]
                                                                                },
                                                        self.lowerLipName2 : {
                                                                                "ty" : [0, -3.12]
                                                                                },
                                                        self.lipCornerName : {
                                                                                "ty" : [0, -2.88]
                                                                                }
                                                    }
                                            
                                          },
                            "LipsUp" : {
                                            MIDDLE : {
                                                        self.upperLipMiddleName : {
                                                                                    "ty" : [0, 3.12]
                                                                                    },
                                                        self.lowerLipMiddleName : {
                                                                                    "ty" : [0, 3.12]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.upperLipName1 : {
                                                                                "ty" : [0, 3.12]
                                                                                },
                                                        self.upperLipName2 : {
                                                                                "ty" : [0, 3.12]
                                                                                },
                                                        self.lowerLipName1 : {
                                                                                "ty" : [0, 3.12]
                                                                                },
                                                        self.lowerLipName2 : {
                                                                                "ty" : [0, 3.12]
                                                                                },
                                                        self.lipCornerName : {
                                                                                "ty" : [0, 2.88]
                                                                                }
                                                    }
                                            
                                          },
                            "L_Sneer" : {
                                            MIDDLE : {
                                                        self.upperLipMiddleName : {
                                                                                    "ty" : [0, 0.14]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.upperLipName1 : {
                                                                                "tx" : [0, 0.44],
                                                                                "ty" : [0, 1.1]
                                                                                },
                                                        self.upperLipName2 : {
                                                                                "tx" : [0, 0.82],
                                                                                "ty" : [0, 1.84],
                                                                                "rz" : [0, -10.0]
                                                                                },
                                                        self.squintName1 : {
                                                                                "tx" : [0, 0.16],
                                                                                "ty" : [0, 0.34]
                                                                                },
                                                        self.squintName2 : {
                                                                                "tx" : [0, 0.16],
                                                                                "ty" : [0, 0.4]
                                                                                }
                                                    }
                                            
                                          },
                            "R_Sneer" : {
                                            MIDDLE : {
                                                        self.upperLipMiddleName : {
                                                                                    "ty" : [0, 0.14]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.upperLipName1 : {
                                                                                "tx" : [0, 0.44],
                                                                                "ty" : [0, 1.1]
                                                                                },
                                                        self.upperLipName2 : {
                                                                                "tx" : [0, 0.82],
                                                                                "ty" : [0, 1.84],
                                                                                "rz" : [0, -10.0]
                                                                                },
                                                        self.squintName1 : {
                                                                                "tx" : [0, 0.16],
                                                                                "ty" : [0, 0.34]
                                                                                },
                                                        self.squintName2 : {
                                                                                "tx" : [0, 0.16],
                                                                                "ty" : [0, 0.4]
                                                                                }
                                                    }
                                            
                                          },
                            "L_Grimace" : {
                                            MIDDLE : {
                                                        self.lowerLipMiddleName : {
                                                                                    "ty" : [0, -0.14]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.lowerLipName1 : {
                                                                                "tx" : [0, 0.44],
                                                                                "ty" : [0, -1.1]
                                                                                },
                                                        self.lowerLipName2 : {
                                                                                "tx" : [0, 0.82],
                                                                                "ty" : [0, -1.84],
                                                                                "rz" : [0, 10.0]
                                                                                }
                                                    }
                                          },
                            "R_Grimace" : {
                                            MIDDLE : {
                                                        self.lowerLipMiddleName : {
                                                                                    "ty" : [0, -0.14]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.lowerLipName1 : {
                                                                                "tx" : [0, 0.44],
                                                                                "ty" : [0, -1.1]
                                                                                },
                                                        self.lowerLipName2 : {
                                                                                "tx" : [0, 0.82],
                                                                                "ty" : [0, -1.84],
                                                                                "rz" : [0, 10.0]
                                                                                }
                                                    }
                                          },
                            "L_Puff" : {
                                            SIDED : {
                                                        self.cheekName1 : {
                                                                                "tx" : [0, 3.7],
                                                                                "tz" : [0, 3.22],
                                                                                "sx" : [1, 2],
                                                                                "sy" : [1, 2],
                                                                                "sz" : [1, 2]
                                                                                }
                                                    }
                                          },
                            "R_Puff" : {
                                            SIDED : {
                                                        self.cheekName1 : {
                                                                                "tx" : [0, 3.7],
                                                                                "tz" : [0, 3.22],
                                                                                "sx" : [1, 2],
                                                                                "sy" : [1, 2],
                                                                                "sz" : [1, 2]
                                                                                }
                                                    }
                                          },
                            "AAA" : {
                                            MIDDLE : {
                                                        self.upperLipMiddleName : {
                                                                                    "ty" : [0, 0.34]
                                                                                    },
                                                        self.lowerLipMiddleName : {
                                                                                    "ty" : [0, -1.66]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.upperLipName1 : {
                                                                                "ty" : [0, 0.34]
                                                                                },
                                                        self.upperLipName2 : {
                                                                                "ty" : [0, 0.34],
                                                                                "rz" : [0, -3.0]
                                                                                },
                                                        self.lowerLipName1 : {
                                                                                "ty" : [0, -1.66]
                                                                                },
                                                        self.lowerLipName2 : {
                                                                                "ty" : [0, -1.06],
                                                                                "rz" : [0, 7.0]
                                                                                }
                                                    }
                                          },
                            "OOO" : {
                                            MIDDLE : {
                                                        self.upperLipMiddleName : {
                                                                                    "ty" : [0, 2.0],
                                                                                    "tz" : [0, 1.46]
                                                                                    },
                                                        self.lowerLipMiddleName : {
                                                                                    "ty" : [0, -2.0],
                                                                                    "tz" : [0, 1.46]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.upperLipName1 : {
                                                                                "tx" : [0, -1.74],
                                                                                "ty" : [0, 2.2],
                                                                                "tz" : [0, 1.14],
                                                                                "rz" : [0, -10.0]
                                                                                },
                                                        self.upperLipName2 : {
                                                                                "tx" : [0, -3.74],
                                                                                "ty" : [0, 0.98],
                                                                                "tz" : [0, 0.84],
                                                                                "rz" : [0, -35.0]
                                                                                },
                                                        self.lowerLipName1 : {
                                                                                "tx" : [0, -1.56],
                                                                                "ty" : [0, -2.4],
                                                                                "tz" : [0, 1.14],
                                                                                "rz" : [0, 13.0]
                                                                                },
                                                        self.lowerLipName2 : {
                                                                                "tx" : [0, -3.0],
                                                                                "ty" : [0, -1.98],
                                                                                "tz" : [0, 0.84],
                                                                                "rz" : [0, 36.0]
                                                                                },
                                                        self.lipCornerName : {
                                                                                "tx" : [0, -4.54],
                                                                                "ty" : [0, -0.5],
                                                                                "tz" : [0, 0.3]
                                                                                }
                                                    }
                                          },
                            "UUU" : {
                                            MIDDLE : {
                                                        self.upperLipMiddleName : {
                                                                                    "ty" : [0, 1.52],
                                                                                    "tz" : [0, 1.3]
                                                                                    },
                                                        self.lowerLipMiddleName : {
                                                                                    "ty" : [0, -1.06],
                                                                                    "tz" : [0, 1.3]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.upperLipName1 : {
                                                                                "tx" : [0, -2.06],
                                                                                "ty" : [0, 1.0],
                                                                                "tz" : [0, 1.1],
                                                                                "rz" : [0, -32.0]
                                                                                },
                                                        self.upperLipName2 : {
                                                                                "tx" : [0, -4.66],
                                                                                "ty" : [0, 0.06],
                                                                                "tz" : [0, 0.68],
                                                                                "rz" : [0, -64.0]
                                                                                },
                                                        self.lowerLipName1 : {
                                                                                "tx" : [0, -2.06],
                                                                                "ty" : [0, -1.06],
                                                                                "tz" : [0, 1.1],
                                                                                "rz" : [0, 25.0]
                                                                                },
                                                        self.lowerLipName2 : {
                                                                                "tx" : [0, -4.56],
                                                                                "ty" : [0, -0.8],
                                                                                "tz" : [0, 0.68],
                                                                                "rz" : [0, 54.0]
                                                                                },
                                                        self.lipCornerName : {
                                                                                "tx" : [0, -6.98],
                                                                                "ty" : [0, -0.54],
                                                                                "tz" : [0, 0.36]
                                                                                }
                                                    }
                                          },
                            "FFF" : {
                                            MIDDLE : {
                                                        self.upperLipMiddleName : {
                                                                                    "ty" : [0, 0.42],
                                                                                    "tz" : [0, 1.3],
                                                                                    "rx" : [0, -12.0]
                                                                                    },
                                                        self.lowerLipMiddleName : {
                                                                                    "ty" : [0, 1.5],
                                                                                    "tz" : [0, -0.42],
                                                                                    "rx" : [0, -22.0]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.upperLipName1 : {
                                                                                "ty" : [0, 0.42],
                                                                                "tz" : [0, 1.3],
                                                                                "rx" : [0, -12.0]
                                                                                },
                                                        self.upperLipName2 : {
                                                                                "ty" : [0, 0.12],
                                                                                "tz" : [0, 0.46],
                                                                                "rx" : [0, -7.7]
                                                                                },
                                                        self.lowerLipName1 : {
                                                                                "ty" : [0, 0.92],
                                                                                "tz" : [0, -0.42],
                                                                                "rx" : [0, -22.0]
                                                                                },
                                                        self.lowerLipName2 : {
                                                                                "ty" : [0, 0.64],
                                                                                "tz" : [0, -0.44],
                                                                                "rx" : [0, -14.0]
                                                                                }
                                                    }
                                          },
                            "MMM" : {
                                            MIDDLE : {
                                                        self.upperLipMiddleName : {
                                                                                    "ty" : [0, -0.94],
                                                                                    "tz" : [0, -0.68],
                                                                                    "rx" : [0, 28.0]
                                                                                    },
                                                        self.lowerLipMiddleName : {
                                                                                    "ty" : [0, 1.3],
                                                                                    "tz" : [0, -0.68],
                                                                                    "rx" : [0, -32.0]
                                                                                    }
                                                      },
                                            SIDED : {
                                                        self.upperLipName1 : {
                                                                                "ty" : [0, -0.28],
                                                                                "tz" : [0, -0.68],
                                                                                "rx" : [0, 28.0]
                                                                                },
                                                        self.upperLipName2 : {
                                                                                "tz" : [0, -0.34],
                                                                                "rx" : [0, 13.0]
                                                                                },
                                                        self.lowerLipName1 : {
                                                                                "ty" : [0, 0.72],
                                                                                "tz" : [0, -0.68],
                                                                                "rx" : [0, -32.0]
                                                                                },
                                                        self.lowerLipName2 : {
                                                                                "ty" : [0, 0.22],
                                                                                "tz" : [0, -0.34],
                                                                                "rx" : [0, -23.0]
                                                                                }
                                                    }
                                          }
                         }
    
    
    def dpGetHeadCtrl(self, *args):
        """ Find and return the headCtrl if it exists in the scene.
        """
        headCtrlList = self.ctrls.getControlNodeById("id_023_HeadHead")
        if headCtrlList:
            return headCtrlList[0]
    
    
    def dpCloseFacialControlWin(self, *args):
        """ Close facial control window if it exists.
        """
        if cmds.window('dpFacialControlWindow', query=True, exists=True):
            cmds.deleteUI('dpFacialControlWindow', window=True)
    
    
    def dpFacialControlUI(self, *args):
        """ Create a window in order to load the original model and targets to be mirrored.
        """
        # creating targetMirrorUI Window:
        self.dpCloseFacialControlWin()
        
        facialCtrl_winWidth  = 380
        facialCtrl_winHeight = 450
        dpFacialControlWin = cmds.window('dpFacialControlWindow', title=self.langDic[self.langName]["m085_facialCtrl"]+" "+DPFC_VERSION, widthHeight=(facialCtrl_winWidth, facialCtrl_winHeight), menuBar=False, sizeable=True, minimizeButton=False, maximizeButton=False, menuBarVisible=False, titleBar=True)

        # creating layout:
        facialCtrlLayout = cmds.columnLayout('facialCtrlLayout', columnOffset=("left", 10))
        cmds.text(label=self.langDic[self.langName]["m139_facialCtrlsAttr"], height=30, parent=facialCtrlLayout)
        
        doubleCBLayout = cmds.rowColumnLayout('doubleCBLayout', numberOfColumns=2, columnWidth=[(1, 70), (2, 300)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 20)], parent=facialCtrlLayout)
        
        self.browCB = cmds.checkBox('browCB', label=self.langDic[self.langName]["c060_brow"], value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(BROW_TGTLIST), parent=doubleCBLayout)
        
        self.eyelidCB = cmds.checkBox('eyelidCB', label=self.langDic[self.langName]["c042_eyelid"], value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(EYELID_TGTLIST[2:]), parent=doubleCBLayout)
        
        self.mouthCB = cmds.checkBox('mouthCB', label=self.langDic[self.langName]["c061_mouth"], value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(MOUTH_TGTLIST), parent=doubleCBLayout)
        
        self.lipsCB = cmds.checkBox('lipsCB', label=self.langDic[self.langName]["c062_lips"], value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(LIPS_TGTLIST), parent=doubleCBLayout)
        
        self.sneerCB = cmds.checkBox('sneerCB', label=self.langDic[self.langName]["c063_sneer"], value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(SNEER_TGTLIST[:2]), parent=doubleCBLayout)
        
        self.grimaceCB = cmds.checkBox('grimaceCB', label=self.langDic[self.langName]["c064_grimace"], value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(GRIMACE_TGTLIST[:2]), parent=doubleCBLayout)
        
        self.faceCB = cmds.checkBox('faceCB', label=self.langDic[self.langName]["c065_face"], value=1, parent=doubleCBLayout)
        cmds.text(label=', '.join(FACE_TGTLIST), parent=doubleCBLayout)
        
        cmds.separator(height=20, style="in", horizontal=True, parent=facialCtrlLayout)
        
        # radio buttons (blendShapes/joints):
        cmds.text("typeText", label=self.langDic[self.langName]["i182_facialMessage"], height=30, parent=facialCtrlLayout)
        typeCollectionLayout = cmds.columnLayout('typeCollectionLayout', columnOffset=('left', 10), width=310, parent=facialCtrlLayout)
        self.typeCollection = cmds.radioCollection('typeCollection', parent=typeCollectionLayout)
        cmds.radioButton( label=self.langDic[self.langName]['i180_indSkinAnim'], annotation=TYPE_BS, onCommand=self.dpChangeType )
        cmds.radioButton( label=self.langDic[self.langName]['i181_jointGame'], annotation=TYPE_JOINTS, onCommand=self.dpChangeType )
        cmds.separator(height=20, style="in", horizontal=True, parent=typeCollectionLayout)
        
        # BlendShapes UI:
        self.bsLayout = cmds.frameLayout("bsLayout", label=self.langDic[self.langName]["m170_blendShapes"], collapsable=True, collapse=True, enable=False, parent=facialCtrlLayout)
        self.connectCB = cmds.checkBox("connectCB", label=self.langDic[self.langName]["m140_tryConnectFacial"], value=1, height=30, changeCommand=self.dpChangeConnectCB, parent=self.bsLayout)
        doubleLayout = cmds.rowColumnLayout('doubleLayout', numberOfColumns=2, columnWidth=[(1, 120), (2, 180)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 20)], parent=self.bsLayout)
        self.loadBSButton = cmds.button("loadBSButton", label=self.langDic[self.langName]["m141_loadBlendShape"]+" >", annotation=self.langDic[self.langName]["m174_loadBSDesc"], backgroundColor=(0.6, 0.6, 1.0), width=120, command=self.dpLoadBSNode, parent=doubleLayout)
        self.bsNodeTextField = cmds.textField('bsNodeTextField', width=160, text='', editable=False, parent=doubleLayout)
        bsTgtListFoundLayout = cmds.columnLayout('bsTgtListFoundLayout', columnOffset=('left', 10), width=310, rowSpacing=4, parent=self.bsLayout)
        self.bsTgtListTxt = cmds.text("bsTgtListTxt", label=self.langDic[self.langName]["m170_blendShapes"]+" "+self.langDic[self.langName]["m142_targetListFound"], height=30, parent=bsTgtListFoundLayout)
        self.bsTargetScrollList = cmds.textScrollList('bsTargetScrollList', width=290, height=100, enable=True, parent=bsTgtListFoundLayout)
        cmds.text(label='', parent=bsTgtListFoundLayout)
        
        # Joints UI:
        self.jointsLayout = cmds.frameLayout("jointsLayout", label=self.langDic[self.langName]["m171_joints"], collapsable=True, collapse=True, enable=False, parent=facialCtrlLayout)
        cmds.text(self.langDic[self.langName]["m172_loadJointCtrl"], height=30, parent=self.jointsLayout)
        doubleJointsLayout = cmds.rowColumnLayout('doubleJointsLayout', numberOfColumns=2, columnWidth=[(1, 120), (2, 180)], columnAlign=[(1, 'left'), (2, 'left')], columnAttach=[(1, 'left', 10), (2, 'left', 20)], parent=self.jointsLayout)
        self.loadJointButton = cmds.button("loadJointButton", label=self.langDic[self.langName]["m173_retargetSelected"], annotation=self.langDic[self.langName]["m175_retargetSelDesc"], backgroundColor=(1.0, 0.6, 0.6), width=120, command=self.dpRetargetJointNode, parent=doubleJointsLayout)
        jntTgtListFoundLayout = cmds.columnLayout('jntTgtListFoundLayout', columnOffset=('left', 10), width=310, rowSpacing=4, parent=self.jointsLayout)
        self.jntTgtListTxt = cmds.text("jntTgtListTxt", label=self.langDic[self.langName]["m171_joints"]+" "+self.langDic[self.langName]["m142_targetListFound"], height=30, parent=jntTgtListFoundLayout)
        self.jntTargetScrollList = cmds.textScrollList('jntTargetScrollList', width=290, height=100, enable=True, parent=jntTgtListFoundLayout)
        
        cmds.separator(height=20, style="in", horizontal=True, parent=facialCtrlLayout)
        cmds.button(label=self.langDic[self.langName]["m143_createSelected"], annotation="Create selected facial controls.", width=290, backgroundColor=(0.6, 1.0, 0.6), command=self.dpSelectedCtrls, parent=facialCtrlLayout)
        cmds.button(label=self.langDic[self.langName]["m144_createDefaltPackage"], annotation="Create default facial controls package.", width=290, backgroundColor=(1.0, 1.0, 0.6), command=self.dpCreateDefaultPackage, parent=facialCtrlLayout)
        
        # call facialControlUI Window:
        cmds.showWindow(dpFacialControlWin)
    
    
    def dpChangeConnectCB(self, *args):
        """ Set values enable or disable when the user change the connect check box.
        """
        # get
        cbValue = cmds.checkBox(self.connectCB, query=True, value=True)
        # set
        cmds.button(self.loadBSButton, edit=True, enable=cbValue)
        cmds.textField(self.bsNodeTextField, edit=True, text="", enable=cbValue)
        cmds.text(self.bsTgtListTxt, edit=True, enable=cbValue)
        cmds.textScrollList(self.bsTargetScrollList, edit=True, removeAll=True, enable=cbValue)
    
    
    def dpGetUserType(self, *args):
        connectBS = False
        connectJnt = False
        if self.userType == TYPE_BS:
            connectBS = cmds.checkBox(self.connectCB, query=True, value=True)
        else:
            connectJnt = True
        return [connectBS, connectJnt]
    
    
    def dpChangeType(self, *args):
        """ Get and return the user selected type of controls.
            Change interface to be more clear.
        """
        typeSelectedRadioButton = cmds.radioCollection(self.typeCollection, query=True, select=True)
        self.userType = cmds.radioButton(typeSelectedRadioButton, query=True, annotation=True)
        if self.userType == TYPE_BS:
            cmds.frameLayout(self.bsLayout, edit=True, enable=True, collapse=False)
            cmds.frameLayout(self.jointsLayout, edit=True, enable=False, collapse=True)
            cmds.checkBox(self.eyelidCB, edit=True, enable=True)
        elif self.userType == TYPE_JOINTS:
            cmds.frameLayout(self.bsLayout, edit=True, enable=False, collapse=True)
            cmds.frameLayout(self.jointsLayout, edit=True, enable=True, collapse=False)
            cmds.checkBox(self.eyelidCB, edit=True, enable=False)
        
    
    def dpCreateDefaultPackage(self, *args):
        """ Function to create a package of facial controls we use as default.
        """
        connectBS, connectJnt = self.dpGetUserType()
        # creating controls:
        lBrowCtrl, lBrowCtrlGrp = self.dpCreateFacialCtrl("L", self.langDic[self.langName]["c060_brow"], "id_046_FacialBrow", BROW_TGTLIST, (0, 0, 0), False, False, True, True, False, connectBS, connectJnt, "red")
        rBrowCtrl, rBrowCtrlGrp = self.dpCreateFacialCtrl("R", self.langDic[self.langName]["c060_brow"], "id_046_FacialBrow", BROW_TGTLIST, (0, 0, 0), False, False, True, True, False, connectBS, connectJnt, "blue")
        if self.userType == TYPE_BS:
            lEyelidCtrl, lEyelidCtrlGrp = self.dpCreateFacialCtrl("L", self.langDic[self.langName]["c042_eyelid"], "id_047_FacialEyelid", EYELID_TGTLIST, (0, 0, 90), True, False, False, True, False, connectBS, connectJnt, "red")
            rEyelidCtrl, rEyelidCtrlGrp = self.dpCreateFacialCtrl("R", self.langDic[self.langName]["c042_eyelid"], "id_047_FacialEyelid", EYELID_TGTLIST, (0, 0, 90), True, False, False, True, False, connectBS, connectJnt, "blue")
        lMouthCtrl, lMouthCtrlGrp = self.dpCreateFacialCtrl("L", self.langDic[self.langName]["c061_mouth"], "id_048_FacialMouth", MOUTH_TGTLIST, (0, 0, -90), False, False, False, False, False, connectBS, connectJnt, "red")
        rMouthCtrl, rMouthCtrlGrp = self.dpCreateFacialCtrl("R", self.langDic[self.langName]["c061_mouth"], "id_048_FacialMouth", MOUTH_TGTLIST, (0, 0, -90), False, False, False, False, False, connectBS, connectJnt, "blue")
        lipsCtrl, lipsCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c062_lips"], "id_049_FacialLips", LIPS_TGTLIST, (0, 0, 0), False, False, True, True, False, connectBS, connectJnt, "yellow")
        sneerCtrl, sneerCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c063_sneer"], "id_050_FacialSneer", SNEER_TGTLIST, (0, 0, 0), False, False, True, True, False, connectBS, connectJnt, "cyan", True)
        grimaceCtrl, grimaceCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c064_grimace"], "id_051_FacialGrimace", GRIMACE_TGTLIST, (0, 0, 0), False, False, True, True, False, connectBS, connectJnt, "cyan", True)
        faceCtrl, faceCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c065_face"], "id_052_FacialFace", FACE_TGTLIST, (0, 0, 0), True, True, True, True, True, connectBS, connectJnt, "cyan")
        
        # placing control groups:
        if lBrowCtrlGrp:
            cmds.setAttr(lBrowCtrlGrp+".translateX", 4)
            cmds.setAttr(lBrowCtrlGrp+".translateY", 12)
            cmds.setAttr(lBrowCtrlGrp+".translateZ", 13)
        if rBrowCtrlGrp:
            cmds.setAttr(rBrowCtrlGrp+".rotateY", 180)
            cmds.setAttr(rBrowCtrlGrp+".translateX", -4)
            cmds.setAttr(rBrowCtrlGrp+".translateY", 12)
            cmds.setAttr(rBrowCtrlGrp+".translateZ", 13)
        if lMouthCtrlGrp:
            cmds.setAttr(lMouthCtrlGrp+".translateX", 3)
            cmds.setAttr(lMouthCtrlGrp+".translateY", 1.5)
            cmds.setAttr(lMouthCtrlGrp+".translateZ", 13)
        if rMouthCtrlGrp:
            cmds.setAttr(rMouthCtrlGrp+".rotateY", 180)
            cmds.setAttr(rMouthCtrlGrp+".translateX", -3)
            cmds.setAttr(rMouthCtrlGrp+".translateY", 1.5)
            cmds.setAttr(rMouthCtrlGrp+".translateZ", 13)
        if lipsCtrlGrp:
            cmds.setAttr(lipsCtrlGrp+".translateY", 1.5)
            cmds.setAttr(lipsCtrlGrp+".translateZ", 13)
        if sneerCtrlGrp:
            cmds.setAttr(sneerCtrlGrp+".translateY", 2.5)
            cmds.setAttr(sneerCtrlGrp+".translateZ", 13)
        if grimaceCtrlGrp:
            cmds.setAttr(grimaceCtrlGrp+".rotateX", 180)
            cmds.setAttr(grimaceCtrlGrp+".translateY", 0.5)
            cmds.setAttr(grimaceCtrlGrp+".translateZ", 13)
        if faceCtrlGrp:
            cmds.setAttr(faceCtrlGrp+".translateX", 10)
            cmds.setAttr(faceCtrlGrp+".translateY", 2)
        
        if self.userType == TYPE_BS:
            if lEyelidCtrlGrp:
                cmds.setAttr(lEyelidCtrlGrp+".translateX", 2)
                cmds.setAttr(lEyelidCtrlGrp+".translateY", 10)
                cmds.setAttr(lEyelidCtrlGrp+".translateZ", 13)
            if rEyelidCtrlGrp:
                cmds.setAttr(rEyelidCtrlGrp+".translateX", -2)
                cmds.setAttr(rEyelidCtrlGrp+".translateY", 10)
                cmds.setAttr(rEyelidCtrlGrp+".translateZ", 13)
        
        # integrating to dpAutoRigSystem:
        if self.headCtrl:
            if cmds.objExists(self.headCtrl):
                cmds.parent(self.facialCtrlsGrp, self.headCtrl, absolute=True)
                cmds.setAttr(self.facialCtrlsGrp+".tx", 0)
                cmds.setAttr(self.facialCtrlsGrp+".ty", 0)
                cmds.setAttr(self.facialCtrlsGrp+".tz", 0)
    
        # closes window:
        self.dpCloseFacialControlWin()
        
    
    def dpSelectedCtrls(self, *args):
        """ Function to create selected facial controls checkboxes.
        """
        connectBS, connectJnt = self.dpGetUserType()
        
        if cmds.checkBox(self.browCB, query=True, value=True):
            lBrowCtrl, lBrowCtrlGrp = self.dpCreateFacialCtrl("L", self.langDic[self.langName]["c060_brow"], "id_046_FacialBrow", BROW_TGTLIST, (0, 0, 0), False, False, True, True, False, connectBS, connectJnt, "red")
            rBrowCtrl, rBrowCtrlGrp = self.dpCreateFacialCtrl("R", self.langDic[self.langName]["c060_brow"], "id_046_FacialBrow", BROW_TGTLIST, (0, 0, 0), False, False, True, True, False, connectBS, connectJnt, "blue")
            if rBrowCtrlGrp:
                cmds.setAttr(rBrowCtrlGrp+".rotateY", 180)
        if cmds.checkBox(self.eyelidCB, query=True, enable=True):
            if cmds.checkBox(self.eyelidCB, query=True, value=True):
                lEyelidCtrl, lEyelidCtrlGrp = self.dpCreateFacialCtrl("L", self.langDic[self.langName]["c042_eyelid"], "id_047_FacialEyelid", EYELID_TGTLIST, (0, 0, 90), True, False, False, True, False, connectBS, connectJnt, "red")
                rEyelidCtrl, rEyelidCtrlGrp = self.dpCreateFacialCtrl("R", self.langDic[self.langName]["c042_eyelid"], "id_047_FacialEyelid", EYELID_TGTLIST, (0, 0, 90), True, False, False, True, False, connectBS, connectJnt, "blue")
        if cmds.checkBox(self.mouthCB, query=True, value=True):
            lMouthCtrl, lMouthCtrlGrp = self.dpCreateFacialCtrl("L", self.langDic[self.langName]["c061_mouth"], "id_048_FacialMouth", MOUTH_TGTLIST, (0, 0, -90), False, False, False, False, False, connectBS, connectJnt, "red")
            rMouthCtrl, rMouthCtrlGrp = self.dpCreateFacialCtrl("R", self.langDic[self.langName]["c061_mouth"], "id_048_FacialMouth", MOUTH_TGTLIST, (0, 0, -90), False, False, False, False, False, connectBS, connectJnt, "blue")
            if rMouthCtrlGrp:
                cmds.setAttr(rMouthCtrlGrp+".rotateY", 180)
        if cmds.checkBox(self.lipsCB, query=True, value=True):
            lipsCtrl, lipsCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c062_lips"], "id_049_FacialLips", LIPS_TGTLIST, (0, 0, 0), False, False, True, True, False, connectBS, connectJnt, "yellow")
        if cmds.checkBox(self.sneerCB, query=True, value=True):
            sneerCtrl, sneerCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c063_sneer"], "id_050_FacialSneer", SNEER_TGTLIST, (0, 0, 0), False, False, True, True, False, connectBS, connectJnt, "cyan", True)
        if cmds.checkBox(self.grimaceCB, query=True, value=True):
            grimaceCtrl, grimaceCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c064_grimace"], "id_051_FacialGrimace", GRIMACE_TGTLIST, (0, 0, 0), False, False, True, True, False, connectBS, connectJnt, "cyan", True)
            if grimaceCtrlGrp:
                cmds.setAttr(grimaceCtrlGrp+".rotateX", 180)
        if cmds.checkBox(self.faceCB, query=True, value=True):
            faceCtrl, faceCtrlGrp = self.dpCreateFacialCtrl(None, self.langDic[self.langName]["c065_face"], "id_052_FacialFace", FACE_TGTLIST, (0, 0, 0), True, True, True, True, True, connectBS, connectJnt, "cyan")
        
    
    def dpCreateFacialCtrl(self, side, ctrlName, cvCtrl, attrList, rotVector=(0, 0, 0), lockX=False, lockY=False, limitX=True, limitY=True, directConnection=False, connectBS=True, connectJnt=False, color='yellow', addTranslateY=False, *args):
        """ Important function to receive called parameters and create the specific asked control.
            Convention:
                transfList = ["tx", "tx", "ty", "ty"]
                axisDirectionList = [-1, 1, -1, 1] # neg, pos, neg, pos
            Returns the created Facial control and its zeroOut group.
        """
        # force limits when working on facial joints:
        if connectJnt:
            limitX = True
            limitY = True
        
        # declaring variables:
        fCtrl = None
        fCtrlGrp = None
        
        transfList = ["tx", "tx", "ty", "ty"]
        # naming:
        if not side == None:
            ctrlName = side+"_"+ctrlName
        fCtrlName = ctrlName+"_Ctrl"
        # skip if already there is this ctrl object:
        if cmds.objExists(fCtrlName):
            return None, None
        else:
            if self.userType == TYPE_BS:
                if connectBS and self.bsNode:
                    # validating blendShape node:
                    if cmds.objectType(self.bsNode) == "blendShape":
                        aliasList = cmds.aliasAttr(self.bsNode, query=True)
            # create control calling dpControls function:
            fCtrl = self.ctrls.cvControl(cvCtrl, fCtrlName, d=0, rot=rotVector)
            
            # ctrl zeroOut grp and color:
            fCtrlGrp = cmds.duplicate(fCtrl, name=fCtrl+'_Grp')[0]
            allChildrenList = cmds.listRelatives(fCtrlGrp, allDescendents=True, children=True, fullPath=True)
            if allChildrenList:
                cmds.delete(allChildrenList)
            cmds.parent(fCtrl, fCtrlGrp, absolute=True)
            self.ctrls.colorShape([fCtrl], color)
            # lock or limit XY axis:
            if lockX:
                cmds.setAttr(fCtrl+".tx", lock=True, keyable=False)
            else:
                # add calibrate attributes:
                cmds.addAttr(fCtrl, longName="calibrateTX", attributeType="float", defaultValue=1, minValue=0.001)
                if limitX:
                    cmds.transformLimits(fCtrl, enableTranslationX=(1, 1))
                    self.dpLimitTranslate(fCtrl, ctrlName, "X")
            if lockY:
                cmds.setAttr(fCtrl+".ty", lock=True, keyable=False)
            else:
                cmds.addAttr(fCtrl, longName="calibrateTY", attributeType="float", defaultValue=1, minValue=0.001)
                if limitY:
                    cmds.transformLimits(fCtrl, enableTranslationY=(1, 1))
                    self.dpLimitTranslate(fCtrl, ctrlName, "Y")
            self.ctrls.setLockHide([fCtrl], ['tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
            # start work with custom attributes
            if attrList:
                for a, attr in enumerate(attrList):
                    if not attr == None:
                        if directConnection:
                            cmds.addAttr(fCtrl, longName=attr, attributeType="float", defaultValue=0, minValue=0, maxValue=1)
                            cmds.setAttr(fCtrl+"."+attr, keyable=True)
                        else:
                            cmds.addAttr(fCtrl, longName=attr, attributeType="float", defaultValue=0)
                            calibrateMD = cmds.createNode("multiplyDivide", name=ctrlName+"_"+attr+"_Calibrate_MD")
                            clp = cmds.createNode("clamp", name=ctrlName+"_"+attr+"_Clp")
                            invMD = cmds.createNode("multiplyDivide", name=ctrlName+"_"+attr+"_Invert_MD")
                            if a == 0 or a == 2: #negative
                                cmds.setAttr(clp+".minR", -1000)
                                cmds.setAttr(invMD+".input2X", -1)
                            else: #positive
                                cmds.setAttr(clp+".maxR", 1000)
                            # connect nodes:
                            cmds.connectAttr(fCtrl+"."+transfList[a], calibrateMD+".input1X", force=True)
                            if a == 0 or a == 1: # -x or +x
                                cmds.connectAttr(fCtrl+".calibrateTX", calibrateMD+".input2X", force=True)
                            else: # -y or +y
                                cmds.connectAttr(fCtrl+".calibrateTY", calibrateMD+".input2X", force=True)
                            if addTranslateY: #useful for Sneer and Grimace
                                integrateTYPMA = cmds.createNode("plusMinusAverage", name=ctrlName+"_"+attr+"_TY_PMA")
                                cmds.connectAttr(calibrateMD+".outputX", integrateTYPMA+".input1D[0]", force=True)
                                cmds.connectAttr(fCtrl+".translateY", integrateTYPMA+".input1D[1]", force=True)
                                cmds.connectAttr(integrateTYPMA+".output1D", clp+".input.inputR", force=True)
                                if "R_" in attr: #hack to set operation as substract in PMA node for Right side
                                    cmds.setAttr(integrateTYPMA+".operation", 2)
                                cmds.setAttr(fCtrl+".calibrateTY", lock=True)
                            else:
                                cmds.connectAttr(calibrateMD+".outputX", clp+".input.inputR", force=True)
                            cmds.connectAttr(clp+".outputR", invMD+".input1X", force=True)
                            cmds.connectAttr(invMD+".outputX", fCtrl+"."+attr, force=True)
                            cmds.setAttr(fCtrl+"."+attr, lock=True)
                        
                        if self.userType == TYPE_BS:
                            # try to connect attributes into blendShape node:
                            if connectBS and self.bsNode:
                                addedSide = False
                                storedAttr = attr
                                for i, alias in enumerate(aliasList):
                                    if not side == None and not addedSide:
                                        attr = side+"_"+attr
                                        addedSide = True
                                    if attr in alias:
                                        try:
                                            cmds.connectAttr(fCtrl+"."+attr, self.bsNode+"."+alias, force=True)
                                        except:
                                            try:
                                                cmds.connectAttr(fCtrl+"."+storedAttr, self.bsNode+"."+alias, force=True)
                                            except:
                                                pass
                        else:
                            if connectJnt:
                                sidedNodeList = None
                                try:
                                    sidedNodeList = self.tweaksDic[attr]
                                except:
                                    pass
                                if sidedNodeList:
                                    for sidedNode in sidedNodeList:
                                        toNodeList = None
                                        try:
                                            toNodeList = self.tweaksDic[attr][sidedNode]
                                        except:
                                            pass
                                        if toNodeList:
                                            for toNodeBaseName in toNodeList:
                                                toNode = None
                                                toNodeSided = toNodeBaseName
                                                addedSide = False
                                                toNodeTargedList = []
                                                for jntTarget in self.jntTargetList:
                                                    toNodeSided = toNodeBaseName
                                                    if sidedNode == SIDED:
                                                        if not addedSide:
                                                            if not side == None:
                                                                # check prefix:
                                                                if jntTarget[1] == "_":
                                                                    if side == jntTarget[0]:
                                                                        toNodeSided = side+"_"+toNodeBaseName
                                                                        if jntTarget.startswith(toNodeSided):    
                                                                            toNode = jntTarget
                                                                            addedSide = True
                                                            elif toNodeSided in jntTarget:
                                                                if attr[1] == "_":
                                                                    if attr[0] == jntTarget[0]:
                                                                        toNode = jntTarget
                                                                        addedSide = True
                                                                else:
                                                                    toNodeTargedList.append(jntTarget)
                                                                    toNode = jntTarget
                                                    elif jntTarget.startswith(toNodeSided):
                                                        if cmds.objExists(jntTarget):
                                                            toNode = jntTarget
                                                if toNode:
                                                    if not toNodeTargedList:
                                                        toNodeTargedList.append(toNode)
                                                    for toNode in toNodeTargedList:
                                                        if cmds.objExists(toNode):
                                                            sizeFactor = self.dpGetSizeFactor(toNode)
                                                            if not sizeFactor:
                                                                sizeFactor = 1
                                                            toAttrList = self.tweaksDic[attr][sidedNode][toNodeBaseName]
                                                            for toAttr in toAttrList:
                                                                oMin = self.tweaksDic[attr][sidedNode][toNodeBaseName][toAttr][0]
                                                                oMax = self.tweaksDic[attr][sidedNode][toNodeBaseName][toAttr][1]
                                                                self.dpCreateRemapNode(fCtrl, attr, toNodeBaseName, toNode, toAttr, self.RmVNumber, sizeFactor, oMin, oMax)
                                                                self.RmVNumber = self.RmVNumber+1
            
            # parenting the hierarchy:
            if not cmds.objExists(self.facialCtrlsGrp):
                cmds.group(name=self.facialCtrlsGrp, empty=True)
            cmds.parent(fCtrlGrp, self.facialCtrlsGrp)
        
        cmds.select(self.facialCtrlsGrp)
        return fCtrl, fCtrlGrp
    
    
    def dpLimitTranslate(self, fCtrl, ctrlName, axis, *args):
        """ Create a hyperbolic setup to limit min and max value for translation of the control.
            Resuming it's just divide 1 by the calibrate value.
        """
        hyperboleTLimitMD = cmds.createNode("multiplyDivide", name=ctrlName+"_LimitT"+axis+"_MD")
        hyperboleInvMD = cmds.createNode("multiplyDivide", name=ctrlName+"_LimitT"+axis+"_Inv_MD")
        cmds.setAttr(hyperboleTLimitMD+".input1X", 1)
        cmds.setAttr(hyperboleTLimitMD+".operation", 2)
        cmds.setAttr(hyperboleInvMD+".input2X", -1)
        cmds.connectAttr(fCtrl+".calibrateT"+axis, hyperboleTLimitMD+".input2X", force=True)
        cmds.connectAttr(hyperboleTLimitMD+".outputX", fCtrl+".maxTransLimit.maxTrans"+axis+"Limit", force=True)
        cmds.connectAttr(hyperboleTLimitMD+".outputX", hyperboleInvMD+".input1X", force=True)
        cmds.connectAttr(hyperboleInvMD+".outputX", fCtrl+".minTransLimit.minTrans"+axis+"Limit", force=True)
    
    
    def dpLoadBSNode(self, *args):
        """ Load selected object as blendShapeNode
        """
        selectedList = cmds.ls(selection=True)
        if selectedList:
            if cmds.objectType(selectedList[0]) == "blendShape":
                cmds.textField(self.bsNodeTextField, edit=True, text=selectedList[0])
                self.dpLoadBSTgtList(selectedList[0])
                self.bsNode = selectedList[0]
            elif cmds.objectType(selectedList[0]) == "transform":
                meshList = cmds.listRelatives(selectedList[0], children=True, shapes=True, noIntermediate=True, type="mesh")
                if meshList:
                    bsNodeList = cmds.listConnections(meshList[0], type="blendShape")
                    if bsNodeList:
                        self.dpLoadBSTgtList(bsNodeList[0])
                        self.bsNode = bsNodeList[0]
                    else:
                        mel.eval("warning \""+self.langDic[self.langName]["e018_selectBlendShape"]+"\";")
                else:
                    mel.eval("warning \""+self.langDic[self.langName]["e018_selectBlendShape"]+"\";")
            else:
                mel.eval("warning \""+self.langDic[self.langName]["e018_selectBlendShape"]+"\";")
        else:
            mel.eval("warning \""+self.langDic[self.langName]["e018_selectBlendShape"]+"\";")
    
    
    def dpLoadBSTgtList(self, bsNodeName, *args):
        """ Add target list found in the blendShape node to target textScroll list
        """
        if cmds.objExists(bsNodeName):
            if cmds.objectType(bsNodeName) == "blendShape":
                tgtList = cmds.blendShape(bsNodeName, query=True, target=True)
                if tgtList:
                    cmds.textScrollList(self.bsTargetScrollList, edit=True, removeAll=True)
                    cmds.textScrollList(self.bsTargetScrollList, edit=True, append=tgtList)
                    cmds.textField(self.bsNodeTextField, edit=True, text=bsNodeName)
                    self.bsNode = bsNodeName
    
    
    def dpRetargetJointNode(self, *args):
        print "yes yes thanks... wip"
    
    
    def dpLoadJointNode(self, itemList, *args):
        leftPrefix = self.langDic[self.langName]["p002_left"]+"_"
        rightPrefix = self.langDic[self.langName]["p003_right"]+"_"
        offsetSuffix = "_Ctrl_Offset_Grp"
        for item in itemList:
            centerName = item+offsetSuffix
            leftName   = leftPrefix+item+offsetSuffix
            rightName  = rightPrefix+item+offsetSuffix
            if cmds.objExists(centerName):
                self.dpLoadJointTgtList(centerName)
            if cmds.objExists(leftName):
                self.dpLoadJointTgtList(leftName)
            if cmds.objExists(rightName):
                self.dpLoadJointTgtList(rightName)
    
    
    def dpLoadJointTgtList(self, item, *args):
        # get current list
        currentList = cmds.textScrollList(self.jntTargetScrollList, query=True, allItems=True)
        if currentList:
            # clear current list
            cmds.textScrollList(self.jntTargetScrollList, edit=True, removeAll=True)
            # avoid repeated items
            if not item in currentList:
                currentList.append(item)
            # refresh textScrollList
            cmds.textScrollList(self.jntTargetScrollList, edit=True, append=currentList)
        else:
            # add selected items in the empyt target scroll list
            cmds.textScrollList(self.jntTargetScrollList, edit=True, append=item)
        self.jntTargetList = cmds.textScrollList(self.jntTargetScrollList, query=True, allItems=True)
    
    
    def dpCreateRemapNode(self, fromNode, fromAttr, toNodeBaseName, toNode, toAttr, number, sizeFactor, oMin=0, oMax=1, iMin=0, iMax=1, *args):
        fromNodeName = utils.extractSuffix(fromNode)
        remap = cmds.createNode("remapValue", name=fromNodeName+"_"+fromAttr+"_"+str(number).zfill(2)+"_"+toAttr.upper()+"_RmV")
        outMaxAttr = toNodeBaseName+"_"+str(number).zfill(2)+"_"+toAttr.upper()
        if "t" in toAttr:
            if not cmds.objExists(fromNode+".sizeFactor"):
                cmds.addAttr(fromNode, longName="sizeFactor", attributeType="float", defaultValue=sizeFactor, keyable=False)
            cmds.addAttr(fromNode, longName=outMaxAttr, attributeType="float", defaultValue=oMax, keyable=False)
            md = cmds.createNode("multiplyDivide", name=fromNodeName+"_"+fromAttr+"_"+str(number).zfill(2)+"_"+toAttr.upper()+"_SizeFactor_MD")
            cmds.connectAttr(fromNode+"."+outMaxAttr, md+".input1X", force=True)
            cmds.connectAttr(fromNode+".sizeFactor", md+".input2X", force=True)
            cmds.connectAttr(md+".outputX", remap+".outputMax", force=True)
        else:
            cmds.addAttr(fromNode, longName=outMaxAttr, attributeType="float", defaultValue=oMax, keyable=False)
            cmds.connectAttr(fromNode+"."+outMaxAttr, remap+".outputMax", force=True)
        cmds.setAttr(remap+".inputMin", iMin)
        cmds.setAttr(remap+".inputMax", iMax)
        cmds.setAttr(remap+".outputMin", oMin)
        cmds.connectAttr(fromNode+"."+fromAttr, remap+".inputValue", force=True)
        # check if there's an input connection and create a plusMinusAverage if we don't have one to connect in:
        connectedList = cmds.listConnections(toNode+"."+toAttr, destination=False, source=True, plugs=False)
        if connectedList:
            if cmds.objectType(connectedList[0]) == "plusMinusAverage":
                inputList = cmds.listConnections(connectedList[0]+".input1D", destination=False, source=True, plugs=False)
                cmds.connectAttr(remap+".outValue", connectedList[0]+".input1D["+str(len(inputList))+"]", force=True)
            else:
                if cmds.objectType(connectedList[0]) == "unitConversion":
                    connectedAttr = cmds.listConnections(connectedList[0]+".input", destination=False, source=True, plugs=True)[0]
                else:
                    connectedAttr = cmds.listConnections(toNode+"."+toAttr, destination=False, source=True, plugs=True)[0]
                pma = cmds.createNode("plusMinusAverage", name=toNode+"_"+toAttr.upper()+"_PMA")
                cmds.connectAttr(connectedAttr, pma+".input1D[0]", force=True)
                cmds.connectAttr(remap+".outValue", pma+".input1D[1]", force=True)
                cmds.connectAttr(pma+".output1D", toNode+"."+toAttr, force=True)
        else:
            cmds.connectAttr(remap+".outValue", toNode+"."+toAttr, force=True)
    

    def dpGetSizeFactor(self, toNode, *args):
        childrenList = cmds.listRelatives(toNode, children=True, type="transform")
        if childrenList:
            for child in childrenList:
                if cmds.objExists(child+".dpControl"):
                    if cmds.getAttr(child+".dpControl") == 1:
                        if cmds.objExists(child+".size"):
                            sizeValue = cmds.getAttr(child+".size")
                            return sizeValue