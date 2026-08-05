# importing libraries:
from ...base import curve

# global variables to this module:    
CLASS_NAME = "Character"
TITLE = "m125_character"
DESCRIPTION = "m099_cvControlDesc"



class Character(curve.BaseCurve):
    def __init__(self, ar):
        curve.BaseCurve.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, None)
    
    
    def cvMain(self, use_ui, cv_id=None, cv_name=CLASS_NAME+'_Ctrl', cv_size=1.0, cv_degree=1, cv_direction='+Y', cv_rot=(0, 0, 0), cv_action=1, guide=False, *args):
        """ The principal method to call all other methods in order to build the cvControl curve.
            Return the result: new control curve or the destination list depending of action.
        """
        return self.cv_create(use_ui, cv_id, cv_name, cv_size, cv_degree, cv_direction, cv_rot, cv_action, guide)
        
    
    
    def getLinearPoints(self):
        """ Get a list of linear points for this kind of control curve.
            Set class object variables cv_points, cvKnotList and cv_periodic.
        """
        r = self.cv_size
        self.cv_points = [(0, r, 0), (0.1*r, r, 0), (0.19*r, 0.82*r, 0), (0.1*r, 0.7*r, 0), (0.04*r, 0.66*r, 0), 
                            (0.04*r, 0.57*r, 0), (0.24*r, 0.545*r, 0), (0.38*r, 0.55*r, 0), (0.46*r, 0.6*r, 0), (0.58*r, 0.55*r, 0), 
                            (0.525*r, 0.46*r, 0), (0.4*r, 0.5*r, 0), (0.24*r, 0.49*r, 0), (0.16*r, 0.45*r, 0), (0.11*r, 0.3*r, 0), 
                            (0.15*r, 0.17*r, 0), (0.17*r, 0.05*r, 0), (0.3*r, 0.037*r, 0), (0.315*r, 0, 0), (0.1*r, 0, 0),
                            (0.073*r, 0.15*r, 0), (0, 0.225*r, 0), (-0.073*r, 0.15*r, 0), (-0.1*r, 0, 0), (-0.315*r, 0, 0), 
                            (-0.3*r, 0.037*r, 0), (-0.17*r, 0.05*r, 0), (-0.15*r, 0.17*r, 0), (-0.11*r, 0.3*r, 0), (-0.16*r, 0.45*r, 0), 
                            (-0.24*r, 0.49*r, 0), (-0.4*r, 0.5*r, 0), (-0.525*r, 0.46*r, 0), (-0.58*r, 0.55*r, 0), (-0.46*r, 0.6*r, 0), 
                            (-0.38*r, 0.55*r, 0), (-0.24*r, 0.545*r, 0), (-0.04*r, 0.57*r, 0), (-0.04*r, 0.66*r, 0), (-0.1*r, 0.7*r, 0),
                            (-0.19*r, 0.82*r, 0), (-0.1*r, r, 0), (0, r, 0)]
        self.cv_knots = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                            26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]
        self.cv_periodic = True #close
    
    
    def getCubicPoints(self):
        """ Get a list of cubic points for this kind of control curve.
            Set class object variables cv_points, cvKnotList and cv_periodic.
        """
        r = self.cv_size
        self.cv_points = [(0, r, 0), (0.1*r, r, 0), (0.19*r, 0.82*r, 0), (0.1*r, 0.7*r, 0), (0.04*r, 0.66*r, 0), 
                            (0.04*r, 0.57*r, 0), (0.24*r, 0.545*r, 0), (0.38*r, 0.55*r, 0), (0.46*r, 0.6*r, 0), (0.58*r, 0.55*r, 0), 
                            (0.525*r, 0.46*r, 0), (0.4*r, 0.5*r, 0), (0.24*r, 0.49*r, 0), (0.16*r, 0.45*r, 0), (0.11*r, 0.3*r, 0), 
                            (0.15*r, 0.17*r, 0), (0.17*r, 0.05*r, 0), (0.3*r, 0.037*r, 0), (0.315*r, 0, 0), (0.1*r, 0, 0),
                            (0.073*r, 0.15*r, 0), (0, 0.225*r, 0), (-0.073*r, 0.15*r, 0), (-0.1*r, 0, 0), (-0.315*r, 0, 0), 
                            (-0.3*r, 0.037*r, 0), (-0.17*r, 0.05*r, 0), (-0.15*r, 0.17*r, 0), (-0.11*r, 0.3*r, 0), (-0.16*r, 0.45*r, 0), 
                            (-0.24*r, 0.49*r, 0), (-0.4*r, 0.5*r, 0), (-0.525*r, 0.46*r, 0), (-0.58*r, 0.55*r, 0), (-0.46*r, 0.6*r, 0), 
                            (-0.38*r, 0.55*r, 0), (-0.24*r, 0.545*r, 0), (-0.04*r, 0.57*r, 0), (-0.04*r, 0.66*r, 0), (-0.1*r, 0.7*r, 0),
                            (-0.19*r, 0.82*r, 0), (-0.1*r, r, 0), (0, r, 0), (0.1*r, r, 0), (0.19*r, 0.82*r, 0)]
        self.cv_knots = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                            26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45]
        self.cv_periodic = True #close