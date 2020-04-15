# importing libraries:
import maya.cmds as cmds
import dpBaseControlClass as BaseControl
reload(BaseControl)

# global variables to this module:    
CLASS_NAME = "SteeringShape"
TITLE = "m161_steeringShape"
DESCRIPTION = "m099_cvControlDesc"
ICON = "/Icons/dp_steeringShape.png"

dpSteeringShapeVersion = 1.0

class SteeringShape(BaseControl.ControlStartClass):
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
        self.cvPointList = [(0, 0.256*r, 0), (0.189*r, 0.187*r, 0), (0.251*r, 0.004*r, 0), (0.192*r, -0.192*r, 0), (0, -0.266*r, 0), 
                            (-0.192*r, -0.192*r, 0), (-0.251*r, 0.004*r, 0), (-0.189*r, 0.187*r, 0), (0, 0.256*r, 0), (0, 0.388*r, 0), 
                            (-0.268*r, 0.331*r, 0), (-0.462*r, 0.164*r, 0), (-0.631*r, 0.1*r, 0), (-0.725*r, 0.1*r, 0), (-0.711*r, 0.215*r, 0), 
                            (-0.596*r, 0.542*r, 0), (-0.38*r, 0.752*r, 0), (-0.087*r, 0.87*r, 0), (0, 0.875*r, 0), (0, 0.991*r, 0), 
                            (-0.122*r, 0.978*r, 0), (-0.427*r, 0.859*r, 0), (-0.688*r, 0.614*r, 0), (-0.821*r, 0.247*r, 0), (-0.85*r, 0.004*r, 0), 
                            (-0.82*r, -0.117*r, 0), (-0.694*r, -0.349*r, 0), (-0.443*r, -0.569*r, 0), (-0.186*r, -0.638*r, 0), (0, -0.652*r, 0), 
                            (0, -0.545*r, 0), (-0.145*r, -0.526*r, 0), (-0.385*r, -0.469*r, 0), (-0.586*r, -0.267*r, 0), (-0.671*r, -0.135*r, 0), 
                            (-0.553*r, -0.129*r, 0), (-0.388*r, -0.146*r, 0), (-0.292*r, -0.29*r, 0), (-0.093*r, -0.382*r, 0), (0, -0.39*r, 0), 
                            (0.093*r, -0.382*r, 0), (0.292*r, -0.29*r, 0), (0.388*r, -0.146*r, 0), (0.553*r, -0.129*r, 0), (0.671*r, -0.135*r, 0), 
                            (0.586*r, -0.267*r, 0), (0.385*r, -0.469*r, 0), (0.145*r, -0.526*r, 0), (0, -0.545*r, 0), (0, -0.652*r, 0), 
                            (0.186*r, -0.638*r, 0), (0.443*r, -0.569*r, 0), (0.694*r, -0.349*r, 0), (0.82*r, -0.117*r, 0), (0.85*r, 0.004*r, 0), 
                            (0.821*r, 0.247*r, 0), (0.688*r, 0.614*r, 0), (0.427*r, 0.859*r, 0), (0.122*r, 0.978*r, 0), (0, 0.991*r, 0), 
                            (0, 0.875*r, 0), (0.087*r, 0.87*r, 0), (0.38*r, 0.752*r, 0), (0.596*r, 0.542*r, 0), (0.711*r, 0.215*r, 0), 
                            (0.725*r, 0.1*r, 0), (0.631*r, 0.1*r, 0), (0.462*r, 0.164*r, 0), (0.268*r, 0.331*r, 0), (0, 0.388*r, 0), 
                            (0, 0.256*r, 0)]
        self.cvKnotList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                            30, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
                            61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]
        self.cvPeriodic = True #closed
    
    
    def getCubicPoints(self, *args):
        """ Get a list of cubic points for this kind of control curve.
            Set class object variables cvPointList, cvKnotList and cvPeriodic.
        """
        r = self.cvSize
        self.cvPointList = [(0, 0.256*r, 0), (0, 0.256*r, 0), (0.189*r, 0.187*r, 0), (0.251*r, 0.004*r, 0), (0.192*r, -0.192*r, 0), 
                            (0, -0.266*r, 0), (-0.192*r, -0.192*r, 0), (-0.251*r, 0.004*r, 0), (-0.189*r, 0.187*r, 0), (0, 0.256*r, 0), 
                            (0, 0.256*r, 0), (0, 0.377*r, 0), (0, 0.377*r, 0), (-0.268*r, 0.331*r, 0), (-0.462*r, 0.164*r, 0), 
                            (-0.631*r, 0.1*r, 0), (-0.725*r, 0.1*r, 0), (-0.711*r, 0.259*r, 0), (-0.596*r, 0.542*r, 0), (-0.38*r, 0.752*r, 0), 
                            (-0.087*r, 0.87*r, 0), (0, 0.869*r, 0), (0, 0.869*r, 0), (0, 0.985*r, 0), (0, 0.985*r, 0), (-0.122*r, 0.978*r, 0), 
                            (-0.427*r, 0.859*r, 0), (-0.688*r, 0.614*r, 0), (-0.821*r, 0.291*r, 0), (-0.85*r, 0.03*r, 0), (-0.82*r, -0.122*r, 0), 
                            (-0.694*r, -0.376*r, 0), (-0.443*r, -0.575*r, 0), (-0.186*r, -0.639*r, 0), (0, -0.653*r, 0), (0, -0.653*r, 0), 
                            (0, -0.546*r, 0), (0, -0.546*r, 0), (-0.145*r, -0.527*r, 0), (-0.385*r, -0.475*r, 0), (-0.586*r, -0.294*r, 0), 
                            (-0.671*r, -0.135*r, 0), (-0.553*r, -0.129*r, 0), (-0.388*r, -0.146*r, 0), (-0.292*r, -0.29*r, 0), (-0.093*r, -0.382*r, 0), 
                            (0, -0.39*r, 0), (0.093*r, -0.382*r, 0), (0.292*r, -0.29*r, 0), (0.388*r, -0.146*r, 0), (0.553*r, -0.129*r, 0), 
                            (0.671*r, -0.135*r, 0), (0.586*r, -0.294*r, 0), (0.385*r, -0.475*r, 0), (0.145*r, -0.527*r, 0), (0, -0.546*r, 0), 
                            (0, -0.546*r, 0), (0, -0.653*r, 0), (0, -0.653*r, 0), (0.186*r, -0.639*r, 0), (0.443*r, -0.575*r, 0), 
                            (0.694*r, -0.376*r, 0), (0.82*r, -0.122*r, 0), (0.85*r, 0.03*r, 0), (0.821*r, 0.291*r, 0), (0.688*r, 0.614*r, 0), 
                            (0.427*r, 0.859*r, 0), (0.122*r, 0.978*r, 0), (0, 0.985*r, 0), (0, 0.985*r, 0), (0, 0.869*r, 0), 
                            (0, 0.869*r, 0), (0.087*r, 0.87*r, 0), (0.38*r, 0.752*r, 0), (0.596*r, 0.542*r, 0), (0.711*r, 0.259*r, 0), 
                            (0.725*r, 0.1*r, 0), (0.631*r, 0.1*r, 0), (0.462*r, 0.164*r, 0), (0.268*r, 0.331*r, 0), (0, 0.377*r, 0), 
                            (0, 0.377*r, 0), (0, 0.256*r, 0), (0, 0.256*r, 0), (0.189*r, 0.187*r, 0)]
        self.cvKnotList = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
                            30, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
                            61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85]
        self.cvPeriodic = True #closed