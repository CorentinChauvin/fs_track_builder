"""
    Definition of useful functions and classes
"""

from src.config import AREA_WIDTH, CANVAS_WIDTH

##########################################
## Distance conversion class
#
class DistanceConverter(object):
    """ Converts pixels to meters, and vice versa
    """
    # Static variables
    zoom_ratio = 1.0

    def __init__(self):
        self.pxl_to_m_ = float(AREA_WIDTH) / CANVAS_WIDTH
        self.m_to_pxl_ = CANVAS_WIDTH / float(AREA_WIDTH)

    def pxl_to_m(self, x):
        """ Converts a length in pixels to a length in meters
        """
        return float(x) * self.pxl_to_m_ / DistanceConverter.zoom_ratio

    def m_to_pxl(self, x):
        """ Converts a length in meters to a length in pixels
        """
        return int(x * self.m_to_pxl_ * DistanceConverter.zoom_ratio)

    @staticmethod
    def zoom_in():
        DistanceConverter.zoom_ratio += 0.2

        if DistanceConverter.zoom_ratio > 2.0:
            DistanceConverter.zoom_ratio = 2.0

    @staticmethod
    def zoom_out():
        DistanceConverter.zoom_ratio -= 0.2

        if DistanceConverter.zoom_ratio < 0.4:
            DistanceConverter.zoom_ratio = 0.4


##########################################
## Point class
#
class Point(object):
    def __init__(self, x, y):
        self.x = x  # spatial coordinates (in meters)
        self.y = y
