# importing libraries:
from maya import cmds
import dpBaseControlClass
from importLib import reload
reload(dpBaseControlClass)

# global variables to this module:    
CLASS_NAME = "ZipperFlat"
TITLE = "m175_zipperFlat"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_zipperFlat.png"

dpZipperFlatVersion = 1.2

class ZipperFlat(dpBaseControlClass.ControlStartClass):
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
        self.cvPointList = [(-0.977*r, 0.158*r, 0), (-0.977*r, -0.135*r, 0), (-0.479*r, -0.135*r, 0), (-0.343*r, -0.248*r, 0), (-0.431*r, -0.341*r, 0),
                            (-0.398*r, -0.552*r, 0), (-0.246*r, -0.64*r, 0), (-0.107*r, -0.56*r, 0), (-0.0688*r, -0.332*r, 0), (-0.162*r, -0.252*r, 0),
                            (-0.0435*r, -0.135*r, 0), (0.268*r, -0.197*r, 0), (0.614*r, -0.328*r, 0), (0.786*r, -0.469*r, 0), (0.958*r, -0.26*r, 0),
                            (0.745*r, -0.107*r, 0), (0.268*r, -0.0149*r, 0), (-0.0267*r, 0, 0), (0.268*r, 0.0295*r, 0), (0.742*r, 0.0994*r, 0),
                            (0.975*r, 0.33*r, 0), (0.782*r, 0.487*r, 0), (0.613*r, 0.313*r, 0), (0.268*r, 0.196*r, 0), (-0.0587*r, 0.158*r, 0),
                            (-0.18*r, 0.267*r, 0), (-0.345*r, 0.267*r, 0), (-0.479*r, 0.158*r, 0), (-0.977*r, 0.158*r, 0)]
        self.cvKnotList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
        self.cvPeriodic = True #closed
    
    
    def getCubicPoints(self, *args):
        """ Get a list of cubic points for this kind of control curve.
            Set class object variables cvPointList, cvKnotList and cvPeriodic.
        """
        r = self.cvSize
        self.cvPointList = [(-0.977*r, 0.158*r, 0), (-0.977*r, -0.135*r, 0), (-0.977*r, -0.135*r, 0), (-0.479*r, -0.135*r, 0), (-0.343*r, -0.248*r, 0),
                            (-0.431*r, -0.341*r, 0), (-0.398*r, -0.552*r, 0), (-0.246*r, -0.64*r, 0), (-0.107*r, -0.56*r, 0), (-0.0688*r, -0.332*r, 0),
                            (-0.162*r, -0.252*r, 0), (-0.0435*r, -0.135*r, 0), (0.268*r, -0.197*r, 0), (0.614*r, -0.328*r, 0), (0.786*r, -0.469*r, 0),
                            (0.958*r, -0.26*r, 0), (0.745*r, -0.107*r, 0), (0.268*r, -0.0149*r, 0), (-0.0267*r, 0, 0), (0.268*r, 0.0295*r, 0),
                            (0.742*r, 0.0994*r, 0), (0.975*r, 0.33*r, 0), (0.782*r, 0.487*r, 0), (0.613*r, 0.313*r, 0), (0.268*r, 0.196*r, 0),
                            (-0.0587*r, 0.158*r, 0), (-0.18*r, 0.267*r, 0), (-0.345*r, 0.267*r, 0), (-0.479*r, 0.158*r, 0), (-0.977*r, 0.158*r, 0),
                            (-0.977*r, 0.158*r, 0), (-0.977*r, -0.135*r, 0), (-0.977*r, -0.135*r, 0)]
        self.cvKnotList = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
        self.cvPeriodic = True #closed