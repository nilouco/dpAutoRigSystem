# importing libraries:
from maya import cmds
from . import dpBaseControlClass
from importlib import reload
reload(dpBaseControlClass)

# global variables to this module:    
CLASS_NAME = "PinSide"
TITLE = "m209_pinSide"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_pinSide.png"

DP_PINSIDE_VERSION = 1.1

class PinSide(dpBaseControlClass.ControlStartClass):
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
        self.cvPointList = [(0, 0, 0), (0, 0.429*r, 0), (-0.205*r, 0.499*r, 0), (-0.291*r, 0.696*r, 0), (-0.235*r, 0.898*r, 0), 
                            (0, 1.016*r, 0), (0.235*r, 0.898*r, 0), (0.292*r, 0.696*r, 0), (0.205*r, 0.499*r, 0), (0, 0.429*r, 0), 
                            (0, 0, 0), (0, -0.425*r, 0), (-0.208*r, -0.497*r, 0), (-0.296*r, -0.697*r, 0), (-0.238*r, -0.901*r, 0), 
                            (0, -1.02*r, 0), (0.238*r, -0.901*r, 0), (0.297*r, -0.697*r, 0), (0.208*r, -0.497*r, 0), (0, -0.425*r, 0), 
                            (0, 0, 0)]
        self.cvKnotList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
        self.cvPeriodic = True #closed
    
    
    def getCubicPoints(self, *args):
        """ Get a list of cubic points for this kind of control curve.
            Set class object variables cvPointList, cvKnotList and cvPeriodic.
        """
        r = self.cvSize
        self.cvPointList = [(0, 0, 0), (0, 0.429*r, 0), (0, 0.429*r, 0), (-0.205*r, 0.499*r, 0), (-0.291*r, 0.696*r, 0),
                            (-0.235*r, 0.898*r, 0), (0, 1.016*r, 0), (0.235*r, 0.898*r, 0), (0.292*r, 0.696*r, 0), (0.205*r, 0.499*r, 0), 
                            (0, 0.429*r, 0), (0, 0.429*r, 0), (0, 0, 0), (0, 0, 0), (0, -0.425*r, 0), (0, -0.425*r, 0), 
                            (-0.208*r, -0.497*r, 0), (-0.296*r, -0.697*r, 0), (-0.238*r, -0.901*r, 0), (0, -1.02*r, 0), (0.238*r, -0.901*r, 0),
                            (0.297*r, -0.697*r, 0), (0.208*r, -0.497*r, 0), (0, -0.425*r, 0), (0, -0.425*r, 0), (0, 0, 0), 
                            (0, 0, 0), (0, 0.429*r, 0), (0, 0.429*r, 0)]
        self.cvKnotList = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
        self.cvPeriodic = True #closed