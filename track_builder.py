#!/usr/bin/env python
"""
    Graphical interface to build a Formula Student track

    Corentin Chauvin-Hameau - 2020
"""

from math import sqrt
import numpy as np
from scipy.interpolate import splprep, splev
import tkinter as tk

##########################################
## Configurable constants
#
AREA_WIDTH = 40.0     # width (in meters) of the drawing area
CANVAS_WIDTH = 800    # width (in pixels) of the drawing area
CANVAS_HEIGHT = 600   # height (in pixels) of the drawing area
TRACK_WIDTH = 3.0     # track width in meters
WAYPOINTS_RADIUS = 5  # radius (in pixels) of the circle corresponding to a waypoint
CONE_RADIUS = 0.3     # radius (in meters) of the cones
DEFAULT_INTER_DISTANCE_CONES = 3.0  # defaut distance between each cones

##########################################
## Useful constants and functions
#
ADD_STATE = 'add'        # Adding waypoints
DELETE_STATE = 'delete'  # Removing waypoints
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
## Class Waypoint
#
class Waypoint(object):
    """
    """
    def __init__(self, x=0.0, y=0.0):
        self.x = x  # spatial coordinates (in meters)
        self.y = y
        self.pxl_x = m_to_pxl(x)  # canvas coordinates (in pixels)
        self.pxl_y = m_to_pxl(y)
        self.is_hovered = False  # whether the mouse is over the waypoint

        self.radius = WAYPOINTS_RADIUS
        self.left   = self.pxl_x - self.radius  # bounding box coordinates
        self.right  = self.pxl_x + self.radius
        self.top    = self.pxl_y - self.radius
        self.bottom = self.pxl_y + self.radius

    def is_colliding(self, x, y):
        """ Checks whether a given canvas point is within the waypoint
        """
        return x >= self.left and x <= self.right \
            and y >= self.top and y <= self.bottom

    def get_bounding_box(self):
        """ Returns the waypoint bounding box
        """
        return (self.left, self.top, self.right, self.bottom)

    def update_hovering(self, x, y):
        """ Updates whether the mouse is hovering the waypoint given mouse coordinates

            @return: Whether the hovering state has changed
        """
        if self.is_colliding(x, y):
            if not self.is_hovered:
                self.is_hovered = True
                self.radius = 1.5 * WAYPOINTS_RADIUS
                self._update_bounding_box()

                return True
        else:
            if self.is_hovered:
                self.is_hovered = False
                self.radius = WAYPOINTS_RADIUS
                self._update_bounding_box()

                return True

        return False

    def update_position(self, x, y):
        """ Updates the position of the waypoint given its spatial position
        """
        self.x = x
        self.y = y
        self.pxl_x = m_to_pxl(x)
        self.pxl_y = m_to_pxl(y)
        self._update_bounding_box()

    def _update_bounding_box(self):
        """ Updates the bounding box of the waypoint
        """
        self.left   = self.pxl_x - self.radius
        self.right  = self.pxl_x + self.radius
        self.top    = self.pxl_y - self.radius
        self.bottom = self.pxl_y + self.radius

    def __repr__(self):
        return self._display()

    def __str__(self):
        return self._display()

    def _display(self):
        """ Displays its coordinates
        """
        return "({}, {})".format(self.x, self.y)


##########################################
## Class TrackBuilder
#
class TrackBuilder(tk.Frame):
    """
    """
    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)

        self.pack(fill=tk.BOTH, expand=True)
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill=tk.BOTH, expand=True)

        # Left widgets
        self.add_button = tk.Button(self.top_frame, text="Add/Move", command=self._add_button_cb)
        self.add_button.pack(side=tk.LEFT)

        self.delete_button = tk.Button(self.top_frame, text="Delete", command=self._delete_button_cb)
        self.delete_button.pack(side=tk.LEFT)

        self.delete_last_button = tk.Button(self.top_frame, text="Delete last cone", command=self._delete_last_button_cb)
        self.delete_last_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(self.top_frame, text="Clear", command=self._clear_button_cb)
        self.clear_button.pack(side=tk.LEFT)

        # Right widgets (need to be added in reverse order)
        self.close_loop_text = tk.StringVar()
        self.close_loop_text.set('Close loop')
        self.close_loop_button = tk.Button(self.top_frame, textvariable=self.close_loop_text, command=self._close_loop_button_cb)
        self.close_loop_button.pack(side=tk.RIGHT)

        self.inter_distance_var = tk.StringVar()
        self.inter_distance_var.set(str(DEFAULT_INTER_DISTANCE_CONES))
        self.inter_distance_var.trace(
            "w", lambda name, index, mode,
            sv=self.inter_distance_var: self._cones_inter_distance_cb(self.inter_distance_var)
        )
        self.inter_distance_field = tk.Entry(self.top_frame, width=4, textvariable=self.inter_distance_var)
        self.inter_distance_field.pack(side=tk.RIGHT)

        self.inter_distance_lbl = tk.Label(self.top_frame, text="Cones inter distance (m):")
        self.inter_distance_lbl.pack(side=tk.RIGHT)

        # Canvas
        self.canvas = tk.Canvas(self)
        self.canvas.config(width=CANVAS_WIDTH, height=CANVAS_HEIGHT, background="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Declare window events
        self.canvas.bind("<Motion>", self._mouse_motion_cb)
        self.canvas.bind("<Button-1>", self._left_click_cb)
        self.canvas.bind("<ButtonRelease-1>", self._left_release_cb)

        # Initialise other variables
        self.action_state = ADD_STATE
        self.waypoints = []
        self.is_dragging = False    # Whether a waypoint is being dragged (ie moved)
        self.dragged_wp_idx = None  # Index of the dragged waypoint
        self.close_loop = False     # Whether to close the loop
        self.cones_inter_distance = DEFAULT_INTER_DISTANCE_CONES

    def _update_window(self):
        """ Draw all the objects in the window again
        """
        self.canvas.delete(tk.ALL)

        # Draw the waypoints
        for wp in self.waypoints:
            self.canvas.create_oval(wp.get_bounding_box(), fill='red')

        # Draw the center line
        pt_x, pt_y, n_x, n_y = self._get_spline_points(self.waypoints, self.close_loop)

        if pt_x == []:
            return

        point_list = []

        for k in range(len(pt_x)):
            point_list.append(m_to_pxl(pt_x[k]))
            point_list.append(m_to_pxl(pt_y[k]))

        self.canvas.create_line(point_list, smooth=True, fill='blue', width=1, dash=(5, 10))

        # Draw one side
        left_points = []     # pixel coordinates for drawing
        right_points = []
        left_waypoints = []  # waypoints coordinates for cones sampling
        right_waypoints = []

        for k in range(len(pt_x)):
            x = pt_x[k] + 0.5 * TRACK_WIDTH * n_x[k]
            y = pt_y[k] + 0.5 * TRACK_WIDTH * n_y[k]
            left_points.append(m_to_pxl(x))
            left_points.append(m_to_pxl(y))
            left_waypoints.append(Waypoint(x, y))

            x = pt_x[k] - 0.5 * TRACK_WIDTH * n_x[k]
            y = pt_y[k] - 0.5 * TRACK_WIDTH * n_y[k]
            right_points.append(m_to_pxl(x))
            right_points.append(m_to_pxl(y))
            right_waypoints.append(Waypoint(x, y))

        self.canvas.create_line(left_points, smooth=True, fill='green', width=1.5)
        self.canvas.create_line(right_points, smooth=True, fill='green', width=1.5)

        # Sample cones
        left_cones_x, left_cones_y, _, _ = self._get_spline_points(left_waypoints, False, self.cones_inter_distance)
        right_cones_x, right_cones_y, _, _ = self._get_spline_points(right_waypoints, False, self.cones_inter_distance)
        radius = m_to_pxl(CONE_RADIUS)

        if left_cones_x == [] or right_cones_x == []:
            return

        for k in range(len(left_cones_x)):
            x = m_to_pxl(left_cones_x[k])
            y = m_to_pxl(left_cones_y[k])
            self.canvas.create_oval([x-radius, y-radius, x+radius, y+radius], fill='yellow')

        for k in range(len(right_cones_x)):
            x = m_to_pxl(right_cones_x[k])
            y = m_to_pxl(right_cones_y[k])
            self.canvas.create_oval([x-radius, y-radius, x+radius, y+radius], fill='blue')


    def _mouse_motion_cb(self, event):
        """
        """
        redraw = False  # whether the window needs to be drawn again
        x = pxl_to_m(event.x)
        y = pxl_to_m(event.y)

        if not self.is_dragging:
            for wp in self.waypoints:
                redraw = wp.update_hovering(event.x, event.y) or redraw
        else:
            self.waypoints[self.dragged_wp_idx].update_position(x, y)
            redraw = True

        if redraw:
            self._update_window()

    def _left_click_cb(self, event):
        """
        """
        x = pxl_to_m(event.x)
        y = pxl_to_m(event.y)

        if self.action_state == ADD_STATE:
            # Check whether it collides with an already existing waypoint
            for i, wp in enumerate(self.waypoints):
                if wp.is_colliding(event.x, event.y):
                    self.is_dragging = True
                    self.dragged_wp_idx = i
                    return

            # If not, add a new waypoint
            self.waypoints.append(Waypoint(x, y))
            self._update_window()

        elif self.action_state == DELETE_STATE:
            for i, wp in enumerate(self.waypoints):
                if wp.is_colliding(event.x, event.y):
                    del self.waypoints[i]
                    break

            self._update_window()

    def _left_release_cb(self, event):
        """
        """
        self.is_dragging = False

    def _add_button_cb(self):
        self.action_state = ADD_STATE

    def _delete_button_cb(self):
        self.action_state = DELETE_STATE

    def _delete_last_button_cb(self):
        if self.waypoints != []:
            del self.waypoints[-1]
            self._update_window()

    def _clear_button_cb(self):
        self.waypoints = []
        self._update_window()

    def _close_loop_button_cb(self):
        if self.close_loop:
            self.close_loop = False
            self.close_loop_text.set("Close loop")
        else:
            self.close_loop = True
            self.close_loop_text.set("Open loop")

        self._update_window()

    def _cones_inter_distance_cb(self, string_var):
        try:
            self.cones_inter_distance = float(string_var.get())
            self._update_window()
        except ValueError:  # catch wrong inputs
            pass

    def _get_spline_points(self, waypoints, periodical, inter_distance=0.0):
        """
            Interpolates a list of waypoints

            @param waypoints:  List of waypoints to interpolate between
            @param periodical: Whether the spline should be periodical
            @param inter_distance: Distance between interpolated points (0.0 for a dense interpolation)
            @return: [pt_x, pt_y, n_x, n_y]
                - pt_x, pt_y -> interpolated spatial coordinates
                - d_x, d_y -> normals to the interpolated points (of unit length)
        """
        if len(waypoints) < 2:
            return [], [], [], []

        # Parse the input waypoints
        wp_x = []
        wp_y = []

        for wp in waypoints:
            wp_x.append(wp.x)
            wp_y.append(wp.y)

        if periodical:
            wp_x.append(waypoints[0].x)
            wp_y.append(waypoints[0].y)

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
            n = 10 * len(waypoints)
        else:
            # Estimate total length of the spline
            length = 0.0
            for k in range(len(waypoints)-1):
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


if __name__ == "__main__":
    display = TrackBuilder()
    display.mainloop()
