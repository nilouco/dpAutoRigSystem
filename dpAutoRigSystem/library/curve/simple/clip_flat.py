# importing libraries:
from ...base import curve

# global variables to this module:    
CLASS_NAME = "ClipFlat"
TITLE = "m107_clipFlat"
DESCRIPTION = "m099_cvControlDesc"



class ClipFlat(curve.BaseCurve):
    def __init__(self, ar):
        curve.BaseCurve.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, None)
    
    
    def cvMain(self, useUI, cvID=None, cvName=CLASS_NAME+'_Ctrl', cvSize=1.0, cvDegree=1, cvDirection='+Y', cvRot=(0, 0, 0), cvAction=1, dpGuide=False, *args):
        """ The principal method to call all other methods in order to build the cvControl curve.
            Return the result: new control curve or the destination list depending of action.
        """
        return self.cvCreate(useUI, cvID, cvName, cvSize, cvDegree, cvDirection, cvRot, cvAction, dpGuide)
        
    
    
    def getLinearPoints(self):
        """ Get a list of linear points for this kind of control curve.
            Set class object variables cvPointList, cvKnotList and cvPeriodic.
        """
        r = self.cvSize
        self.cvPointList = [(0, 0, 0), (0, 0.198*r, 0), (0, 0.405*r, 0), (0, 0.495*r, 0), (0.198*r, 0.617*r, 0),
                            (0.198*r, 0.9*r, 0), (0, r, 0), (-0.198*r, 0.9*r, 0), (-0.198*r, 0.617*r, 0), (0, 0.495*r, 0)]
        self.cvKnotList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.cvPeriodic = False #open
    
    
    def getCubicPoints(self):
        """ Get a list of cubic points for this kind of control curve.
            Set class object variables cvPointList, cvKnotList and cvPeriodic.
        """
        r = self.cvSize
        self.cvPointList = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0.198*r, 0), (0, 0.405*r, 0),
                            (0, 0.495*r, 0), (0, 0.495*r, 0), (0, 0.495*r, 0), (0.198*r, 0.617*r, 0), (0.198*r, 0.9*r, 0),
                            (0, r, 0), (-0.198*r, 0.9*r, 0), (-0.198*r, 0.617*r, 0), (0, 0.495*r, 0), (0, 0.495*r, 0),
                            (0, 0.495*r, 0)]
        self.cvKnotList = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
        self.cvPeriodic = False #open