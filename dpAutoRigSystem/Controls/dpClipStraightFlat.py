# importing libraries:
from . import dpBaseControlClass

# global variables to this module:    
CLASS_NAME = "ClipStraightFlat"
TITLE = "m108_clipStraightFlat"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_clipStraightFlat.png"

DP_CLIPSTRAIGHTFLAT_VERSION = 1.3


class ClipStraightFlat(dpBaseControlClass.ControlStartClass):
    def __init__(self, *args, **kwargs):
        #Add the needed parameter to the kwargs dict to be able to maintain the parameter order
        kwargs["CLASS_NAME"] = CLASS_NAME
        kwargs["TITLE"] = TITLE
        kwargs["DESCRIPTION"] = DESCRIPTION
        kwargs["ICON"] = ICON
        dpBaseControlClass.ControlStartClass.__init__(self, *args, **kwargs)
    
    
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
        self.cvPointList = [(0, 0, 0), (0, 0.198*r, 0), (0, 0.405*r, 0), (0, 0.495*r, 0), (0.198*r, 0.617*r, 0),
                            (0.198*r, 0.9*r, 0), (0, 0.9*r, 0), (-0.198*r, 0.9*r, 0), (-0.198*r, 0.617*r, 0), (0, 0.495*r, 0)]
        self.cvKnotList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.cvPeriodic = False #open
    
    
    def getCubicPoints(self, *args):
        """ Get a list of cubic points for this kind of control curve.
            Set class object variables cvPointList, cvKnotList and cvPeriodic.
        """
        r = self.cvSize
        self.cvPointList = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0.198*r, 0), (0, 0.405*r, 0),
                            (0, 0.495*r, 0), (0, 0.495*r, 0), (0, 0.495*r, 0), (0.198*r, 0.617*r, 0), (0.198*r, 0.9*r, 0),
                            (0, 0.9*r, 0), (-0.198*r, 0.9*r, 0), (-0.198*r, 0.617*r, 0), (0, 0.495*r, 0), (0, 0.495*r, 0),
                            (0, 0.495*r, 0)]
        self.cvKnotList = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        self.cvPeriodic = False #open