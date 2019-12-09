# importing libraries:
import maya.cmds as cmds
import dpBaseControlClass as BaseControl
reload(BaseControl)

# global variables to this module:    
CLASS_NAME = "Character"
TITLE = "m125_character"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_character.png"

dpCharacterVersion = 1.1

class Character(BaseControl.ControlStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        BaseControl.ControlStartClass.__init__(self, *args, **kwargs)
    
    
    def cvMain(self, useUI, cvID=None, cvName=CLASS_NAME+'_Ctrl', cvSize=1.0, cvDegree=1, cvDirection='+Y', cvRot=(0, 0, 0), cvAction=1, dpGuide=False, *args):
        """ The principal method to call all other methods in order to build the cvControl curve.
            Return the result: new control curve or the destination list depending of action.
        """
        result = self.cvCreate(useUI, cvID, cvName, cvSize, cvDegree, cvDirection, cvRot, cvAction, dpGuide)
        return result
    
    
    def getLinearPoints(self, *args):
        """ Get a list of linear points for this kind of control curve.
            Set class object variables cvPointList, cvKnotList and cvPeriodic.
        """
        r = self.cvSize
        self.cvPointList = [(0, r, 0), (0.1*r, r, 0), (0.19*r, 0.82*r, 0), (0.1*r, 0.7*r, 0), (0.04*r, 0.66*r, 0), 
                            (0.04*r, 0.57*r, 0), (0.24*r, 0.545*r, 0), (0.38*r, 0.55*r, 0), (0.46*r, 0.6*r, 0), (0.58*r, 0.55*r, 0), 
                            (0.525*r, 0.46*r, 0), (0.4*r, 0.5*r, 0), (0.24*r, 0.49*r, 0), (0.16*r, 0.45*r, 0), (0.11*r, 0.3*r, 0), 
                            (0.15*r, 0.17*r, 0), (0.17*r, 0.05*r, 0), (0.3*r, 0.037*r, 0), (0.315*r, 0, 0), (0.1*r, 0, 0),
                            (0.073*r, 0.15*r, 0), (0, 0.225*r, 0), (-0.073*r, 0.15*r, 0), (-0.1*r, 0, 0), (-0.315*r, 0, 0), 
                            (-0.3*r, 0.037*r, 0), (-0.17*r, 0.05*r, 0), (-0.15*r, 0.17*r, 0), (-0.11*r, 0.3*r, 0), (-0.16*r, 0.45*r, 0), 
                            (-0.24*r, 0.49*r, 0), (-0.4*r, 0.5*r, 0), (-0.525*r, 0.46*r, 0), (-0.58*r, 0.55*r, 0), (-0.46*r, 0.6*r, 0), 
                            (-0.38*r, 0.55*r, 0), (-0.24*r, 0.545*r, 0), (-0.04*r, 0.57*r, 0), (-0.04*r, 0.66*r, 0), (-0.1*r, 0.7*r, 0),
                            (-0.19*r, 0.82*r, 0), (-0.1*r, r, 0), (0, r, 0)]
        self.cvKnotList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                            26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]
        self.cvPeriodic = True #close
    
    
    def getCubicPoints(self, *args):
        """ Get a list of cubic points for this kind of control curve.
            Set class object variables cvPointList, cvKnotList and cvPeriodic.
        """
        r = self.cvSize
        self.cvPointList = [(0, r, 0), (0.1*r, r, 0), (0.19*r, 0.82*r, 0), (0.1*r, 0.7*r, 0), (0.04*r, 0.66*r, 0), 
                            (0.04*r, 0.57*r, 0), (0.24*r, 0.545*r, 0), (0.38*r, 0.55*r, 0), (0.46*r, 0.6*r, 0), (0.58*r, 0.55*r, 0), 
                            (0.525*r, 0.46*r, 0), (0.4*r, 0.5*r, 0), (0.24*r, 0.49*r, 0), (0.16*r, 0.45*r, 0), (0.11*r, 0.3*r, 0), 
                            (0.15*r, 0.17*r, 0), (0.17*r, 0.05*r, 0), (0.3*r, 0.037*r, 0), (0.315*r, 0, 0), (0.1*r, 0, 0),
                            (0.073*r, 0.15*r, 0), (0, 0.225*r, 0), (-0.073*r, 0.15*r, 0), (-0.1*r, 0, 0), (-0.315*r, 0, 0), 
                            (-0.3*r, 0.037*r, 0), (-0.17*r, 0.05*r, 0), (-0.15*r, 0.17*r, 0), (-0.11*r, 0.3*r, 0), (-0.16*r, 0.45*r, 0), 
                            (-0.24*r, 0.49*r, 0), (-0.4*r, 0.5*r, 0), (-0.525*r, 0.46*r, 0), (-0.58*r, 0.55*r, 0), (-0.46*r, 0.6*r, 0), 
                            (-0.38*r, 0.55*r, 0), (-0.24*r, 0.545*r, 0), (-0.04*r, 0.57*r, 0), (-0.04*r, 0.66*r, 0), (-0.1*r, 0.7*r, 0),
                            (-0.19*r, 0.82*r, 0), (-0.1*r, r, 0), (0, r, 0), (0.1*r, r, 0), (0.19*r, 0.82*r, 0)]
        self.cvKnotList = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                            26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]
        self.cvPeriodic = True #close