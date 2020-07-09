"""
    Definition of useful functions and classes
"""

from src.config import AREA_WIDTH, CANVAS_WIDTH

##########################################
## Conversion functions
#
PXL_TO_M = float(AREA_WIDTH) / CANVAS_WIDTH
M_TO_PXL = CANVAS_WIDTH / float(AREA_WIDTH)

def pxl_to_m(x):
    """ Converts a length in pixels to a length in meters
    """
    return float(x) * PXL_TO_M

def m_to_pxl(x):
    """ Converts a length in meters to a length in pixels
    """
    return int(x * M_TO_PXL)

##########################################
## Point class
#
class Point(object):
    def __init__(self, x, y):
        self.x = x  # spatial coordinates (in meters)
        self.y = y
