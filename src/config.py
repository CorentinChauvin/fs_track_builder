"""
    Constants definition
"""

##########################################
## Configurable constants
#
AREA_WIDTH = 40.0     # width (in meters) of the drawing area
CANVAS_WIDTH = 900    # width (in pixels) of the drawing area
CANVAS_HEIGHT = 700   # height (in pixels) of the drawing area
SCROLLABLE_CANVAS_WIDTH = 4 * CANVAS_WIDTH    # scrollable width (in pxls) of the drawing area
SCROLLABLE_CANVAS_HEIGHT = 4 * CANVAS_HEIGHT  # scrollable height (in pxls) of the drawing area
TRACK_WIDTH = 3.0     # track width in meters
WAYPOINTS_RADIUS = 5  # radius (in pixels) of the circle corresponding to a waypoint
CONE_RADIUS = 0.3     # radius (in meters) of the cones
DEFAULT_SPACING_CONES = 3.0   # defaut distance between each cones
DEFAULT_SPACING_ORANGE = 0.5  # default distance between orange cones
DEFAULT_GRID_SIZE = 1.0
INIT_OFFSET_X = -2.0   # initial offset for the starting pose (along longitudinal axis)
INIT_OFFSET_Y = 0.0    # initial offset for the starting pose (along lateral axis)
INIT_OFFSET_YAW = 0.0  # initial offset for the starting pose (yaw, in degrees)

##########################################
## Useful constants
#
ADD_STATE = 'add'        # Adding waypoints
DELETE_STATE = 'delete'  # Removing waypoints
