"""
"""

from math import sqrt
import numpy as np
from scipy.interpolate import splprep, splev
from src.utils import m_to_pxl, Point


class TrackBuilder(object):
    """ Base class for the TrackBuilderGUI, handles all computations
    """

    def __init__(self):
        self.center_pts_x = []  # coordinates of the center points of the track
        self.center_pts_y = []
        self.center_n_x = []    # coordinates of the normals to the center points
        self.center_n_y = []
        self.left_points = []   # interpolated points of the sides of the track
        self.right_points = []

        self.left_cones = []  # cones position
        self.right_cones = []

    def compute_center_points(self, waypoints, close_loop):
        """ Interpolates track center points between the waypoints

            @param waypoints:  List of waypoints
            @param close_loop: Whether to close the loop
            @return: List of pixel coordinates ready to draw the center line
                [x1, y1, x2, y2, ...]
        """
        pt_x, pt_y, n_x, n_y = self._get_spline_points(self.waypoints, self.close_loop)
        self.center_pts_x = pt_x
        self.center_pts_y = pt_y
        self.center_n_x = n_x
        self.center_n_y = n_y

        points_list = []

        for k in range(len(pt_x)):
            points_list.append(m_to_pxl(pt_x[k]))
            points_list.append(m_to_pxl(pt_y[k]))

        return points_list

    def compute_side_points(self, track_width):
        """ Interpolates points on the two sides of the track

            @param track_width: Width (in meters) of the track
            @return: [left_points_list, right_points_list] -> ready to draw
                lists of points for the two sides
        """
        left_points_list = []     # pixel coordinates for drawing
        right_points_list = []
        self.left_points = []  # waypoints coordinates for cones sampling
        self.right_points = []

        for k in range(len(self.center_pts_x)):
            x = self.center_pts_x[k] + 0.5 * track_width * self.center_n_x[k]
            y = self.center_pts_y[k] + 0.5 * track_width * self.center_n_y[k]
            left_points_list.append(m_to_pxl(x))
            left_points_list.append(m_to_pxl(y))
            self.left_points.append(Point(x, y))

            x = self.center_pts_x[k] - 0.5 * track_width * self.center_n_x[k]
            y = self.center_pts_y[k] - 0.5 * track_width * self.center_n_y[k]
            right_points_list.append(m_to_pxl(x))
            right_points_list.append(m_to_pxl(y))
            self.right_points.append(Point(x, y))

        return left_points_list, right_points_list

    def compute_cones(self, inter_distance):
        """ Compute the position of the cones on the two sides

            @param inter_distance: Distance (in meters) between two consecutive cones
            @return: List of cones position (in meters)
        """
        left_cones_x, left_cones_y, _, _ = self._get_spline_points(self.left_points, False, inter_distance)
        right_cones_x, right_cones_y, _, _ = self._get_spline_points(self.right_points, False, inter_distance)

        self.left_cones = [
            Point(left_cones_x[k], left_cones_y[k])
            for k in range(len(left_cones_x))
        ]
        self.right_cones = [
            Point(right_cones_x[k], right_cones_y[k])
            for k in range(len(right_cones_x))
        ]

        return self.left_cones, self.right_cones

    def _get_spline_points(self, points, periodical, inter_distance=0.0):
        """
            Interpolates a list of points

            @param points:  List of points to interpolate between
            @param periodical: Whether the spline should be periodical
            @param inter_distance: Distance between interpolated points (0.0 for a dense interpolation)
            @return: [pt_x, pt_y, n_x, n_y]
                - pt_x, pt_y -> interpolated spatial coordinates
                - d_x, d_y -> normals to the interpolated points (of unit length)
        """
        if len(points) < 2:
            return [], [], [], []

        # Parse the input points
        wp_x = []
        wp_y = []

        for wp in points:
            wp_x.append(wp.x)
            wp_y.append(wp.y)

        if periodical:
            wp_x.append(points[0].x)
            wp_y.append(points[0].y)

        wp_x = np.array(wp_x)
        wp_y = np.array(wp_y)

        # Create a spline from the waypoints
        if (len(wp_x) == 2):
            spline, _ = splprep([wp_x, wp_y], u=None, s=0.0, per=periodical, k=1)  # straight line
        elif (len(wp_x) == 3):
            spline, _ = splprep([wp_x, wp_y], u=None, s=0.0, per=periodical, k=2)  # degree 2
        else:
            spline, _ = splprep([wp_x, wp_y], u=None, s=0.0, per=periodical)

        # Determine number of interpolated points
        if inter_distance <= 0.0:
            n = 10 * len(points)
        else:
            # Estimate total length of the spline
            length = 0.0
            for k in range(len(points)-1):
                length += sqrt((wp_x[k+1]-wp_x[k])**2 + (wp_y[k+1]-wp_y[k])**2)
            n = int(length / inter_distance)

            if n == 0:
                return [], [], [], []

        # Interpolate the spline
        interval = np.linspace(0, 1, n)
        pt_x, pt_y = splev(interval, spline, der=0)

        # Get the normals
        d_x, d_y = splev(interval, spline, der=1)  # derivatives
        n_x = []
        n_y = []
        for k in range(len(d_x)):
            norm = sqrt(d_x[k]**2 + d_y[k]**2)
            n_x.append(d_y[k] / norm)
            n_y.append(-d_x[k] / norm)

        return list(pt_x), list(pt_y), n_x, n_y

    def snap_coord_to_grid(self, x, y, grid_size):
        """ Snaps spatial coordinates to a grid
        """
        x -= x % grid_size
        y -= y % grid_size
        return x, y