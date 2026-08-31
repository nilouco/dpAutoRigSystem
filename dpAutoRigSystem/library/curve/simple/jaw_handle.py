# importing libraries:
from ...base import curve

# global variables to this module:    
CLASS_NAME = "JawHandle"
TITLE = "m132_jawHandle"
DESCRIPTION = "m099_cvControlDesc"



class JawHandle(curve.BaseCurve):
    def __init__(self, ar):
        curve.BaseCurve.__init__(self, ar, CLASS_NAME, TITLE, DESCRIPTION, None)
    
    
    def cv_main(self, use_ui, cv_id=None, cv_name=CLASS_NAME+'_Ctrl', cv_size=1.0, cv_degree=1, cv_direction='+Y', cv_rot=(0, 0, 0), cv_action=1, guide=False):
        """ The principal method to call all other methods in order to build the create_controller curve.
            Return the result: new control curve or the destination list depending of action.
        """
        return self.cv_create(use_ui, cv_id, cv_name, cv_size, cv_degree, cv_direction, cv_rot, cv_action, guide)
        
    
    def get_linear_points(self):
        """ Get a list of linear points for this kind of control curve.
            Set class object variables cv_points, cvKnotList and cv_periodic.
        """
        r = self.cv_size
        self.cv_points = [(-0.728*r, 0, -0.229*r), (-0.646*r, 0, 0.015*r), (-0.534*r, 0, 0.257*r), (-0.462*r, 0, 0.434*r), (-0.343*r, 0, 0.733*r),
                            (-0.191*r, 0.0, 0.759*r), (0, 0, 0.759*r), (0.191*r, 0, 0.759*r), (0.343*r, 0, 0.733*r), (0.462*r, 0, 0.434*r), 
                            (0.527*r, 0, 0.257*r), (0.658*r, 0, 0.015*r), (0.749*r, 0, -0.292*r), (0.855*r, 0.018*r, -0.606*r), (0.913*r, 0.030*r, -0.920*r), 
                            (1.036*r, 0.455*r, -0.879*r), (0.945*r, 0.311*r, -0.577*r), (0.818*r, 0.139*r, -0.335*r), (0.753*r, 0.114*r, 0.017*r), (0.449*r, 0.124*r, 0.657*r),
                            (0.335*r, 0.206*r, 0.726*r), (0.322*r, 0.552*r, 0.848*r), (0, 0.591*r, 0.87*r), (-0.322*r, 0.552*r, 0.848*r), (-0.335*r, 0.206*r, 0.726*r), 
                            (-0.449*r, 0.124*r, 0.657*r), (-0.753*r, 0.114*r, 0.017*r), (-0.8181*r, 0.139*r, -0.335*r), (-0.945*r, 0.311*r, -0.577*r), (-1.031*r, 0.452*r, -0.895*r),
                            (-0.921*r, 0.030*r, -0.883*r), (-0.824*r, 0.018*r, -0.519*r), (-0.728*r, 0, -0.229*r)]
        self.cv_knots = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                            26, 27, 28, 29, 30, 31, 32, 33]
        self.cv_periodic = True #closed
    
    
    def get_cubic_points(self):
        """ Get a list of cubic points for this kind of control curve.
            Set class object variables cv_points, cvKnotList and cv_periodic.
        """
        r = self.cv_size
        self.cv_points = [(-0.728*r, 0, -0.229*r), (-0.646*r, 0, 0.015*r), (-0.534*r, 0, 0.257*r), (-0.462*r, 0, 0.434*r), (-0.343*r, 0, 0.733*r),
                            (-0.191*r, 0.0, 0.759*r), (0, 0, 0.759*r), (0.191*r, 0, 0.759*r), (0.343*r, 0, 0.733*r), (0.462*r, 0, 0.434*r), 
                            (0.527*r, 0, 0.257*r), (0.658*r, 0, 0.015*r), (0.749*r, 0, -0.292*r), (0.855*r, 0.018*r, -0.606*r), (0.913*r, 0.030*r, -0.920*r), 
                            (1.036*r, 0.455*r, -0.879*r), (0.945*r, 0.311*r, -0.577*r), (0.818*r, 0.139*r, -0.335*r), (0.753*r, 0.114*r, 0.017*r), (0.449*r, 0.124*r, 0.657*r),
                            (0.335*r, 0.206*r, 0.726*r), (0.322*r, 0.552*r, 0.848*r), (0, 0.591*r, 0.87*r), (-0.322*r, 0.552*r, 0.848*r), (-0.335*r, 0.206*r, 0.726*r), 
                            (-0.449*r, 0.124*r, 0.657*r), (-0.753*r, 0.114*r, 0.017*r), (-0.8181*r, 0.139*r, -0.335*r), (-0.945*r, 0.311*r, -0.577*r), (-1.031*r, 0.452*r, -0.895*r),
                            (-0.921*r, 0.030*r, -0.883*r), (-0.824*r, 0.018*r, -0.519*r), (-0.728*r, 0, -0.229*r), (-0.646*r, 0, 0.015*r), (-0.534*r, 0, 0.257*r)]
        self.cv_knots = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                            26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
        self.cv_periodic = True #closed
