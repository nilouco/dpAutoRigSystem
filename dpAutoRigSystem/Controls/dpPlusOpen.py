# importing libraries:
from maya import cmds
from . import dpBaseControlClass
from importlib import reload
reload(dpBaseControlClass)

# global variables to this module:    
CLASS_NAME = "PlusOpen"
TITLE = "m207_plusOpen"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_plusOpen.png"

dpPlusVersion = 1.2

class PlusOpen(dpBaseControlClass.ControlStartClass):
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
        self.cvPointList = [(-0.33*r, -r, 0), (-0.53*r, -0.53*r, 0), (-r, -0.33*r, 0), (-r, 0.33*r, 0), (-0.53*r, 0.53*r, 0),
                            (-0.33*r, r, 0), (0.33*r, r, 0), (0.53*r, 0.53*r, 0), (r, 0.33*r, 0), (r, -0.33*r, 0), (0.53*r, -0.53*r, 0),
                            (0.33*r, -r, 0), (-0.33*r, -r, 0)]
        self.cvKnotList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        self.cvPeriodic = True #closed

        # curve -d 1 -p (-0.33*r, -r, 0), (-0.53*r, -0.53*r, 0), (-r, -0.33*r, 0), (-r, 0.33*r, 0), (-0.53*r, 0.53*r, 0), (-0.33*r, r, 0), (0.33*r, r, 0), (0.53*r, 0.53*r, 0), (r, 0.33*r, 0), (r, -0.33*r, 0), (0.53*r, -0.53*r, 0), (0.33*r, -r, 0), (-0.33*r, -r, 0)
    
        # curve -d 3 -p -0.531401 -0.531401 0 -p -0.715483 -0.518453 0 -p -1.083649 -0.492557 0 -p -1.134002 0.521628 0 -p -0.380341 0.386046 0 -p -0.533037 1.122593 0 -p 0.532488 1.123581 0 -p 0.383084 0.383084 0 -p 1.123581 0.532488 0 -p 1.122593 -0.533037 0 -p 0.386046 -0.380341 0 -p 0.521628 -1.134002 0 -p -0.492557 -1.083649 0 -p -0.518453 -0.715483 0 -p -0.531401 -0.531401 0 -k 0 -k 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 12 -k 12 ;

    
    def getCubicPoints(self, *args):
        """ Get a list of cubic points for this kind of control curve.
            Set class object variables cvPointList, cvKnotList and cvPeriodic.
        """
        r = self.cvSize
        self.cvPointList = [(-r, 0.33*r, 0), (-0.9*r, 0.33*r, 0), (-0.43*r, 0.33*r, 0), (-0.33*r, 0.33*r, 0), (-0.33*r, 0.43*r, 0), 
                            (-0.33*r, 0.9*r, 0), (-0.33*r, r, 0), (-0.23*r, r, 0), (0.23*r, r, 0), (0.33*r, r, 0), 
                            (0.33*r, 0.9*r, 0), (0.33*r, 0.43*r, 0), (0.33*r, 0.33*r, 0), (0.43*r, 0.33*r, 0), (0.9*r, 0.33*r, 0), 
                            (r, 0.33*r, 0), (r, 0.23*r, 0), (r, -0.23*r, 0), (r, -0.23*r, 0), (r, -0.33*r, 0), 
                            (0.9*r, -0.33*r, 0), (0.43*r, -0.33*r, 0), (0.33*r, -0.33*r, 0), (0.33*r, -0.43*r, 0), (0.33*r, -0.9*r, 0),
                            (0.33*r, -r, 0), (0.23*r, -r, 0), (-0.23*r, -r, 0), (-0.33*r, -r, 0), (-0.33*r, -0.9*r, 0), 
                            (-0.33*r, -0.43*r, 0), (-0.33*r, -0.33*r, 0), (-0.43*r, -0.33*r, 0), (-0.9*r, -0.33*r, 0), (-r, -0.33*r, 0),
                            (-r, -0.23*r, 0), (-r, 0.23*r, 0), (-r, 0.33*r, 0), (-0.9*r, 0.33*r, 0), (-0.43*r, 0.33*r, 0)]
        self.cvKnotList = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                            26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
        self.cvPeriodic = True #closed