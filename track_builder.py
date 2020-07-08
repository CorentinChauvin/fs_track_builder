#!/usr/bin/env python
"""
    Graphical interface to build a Formula Student track

    Corentin Chauvin-Hameau - 2020
"""

import numpy as np
from scipy.interpolate import splprep, splev
import tkinter as tk

##########################################
## Configurable constants
#
AREA_WIDTH = 40.0     # width (in meters) of the drawing area
CANVAS_WIDTH = 800    # width (in pixels) of the drawing area
CANVAS_HEIGHT = 600   # height (in pixels) of the drawing area
WAYPOINTS_RADIUS = 5  # radius (in pixels) of the circle corresponding to a waypoint

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

        # Initialise the widgets
        self.pack(fill=tk.BOTH, expand=True)

        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill=tk.BOTH, expand=True)

        self.add_button = tk.Button(self.top_frame, text="Add/Move", command=self._add_button_cb)
        self.add_button.pack(side=tk.LEFT)
        self.delete_button = tk.Button(self.top_frame, text="Delete", command=self._delete_button_cb)
        self.delete_button.pack(side=tk.LEFT)

        self.close_loop_text = tk.StringVar()
        self.close_loop_text.set('Close loop')
        self.delete_button = tk.Button(self.top_frame, textvariable=self.close_loop_text, command=self._close_loop_button_cb)
        self.delete_button.pack(side=tk.LEFT)

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

    def _update_window(self):
        """ Draw all the objects in the window again
        """
        self.canvas.delete(tk.ALL)

        # Draw the waypoints
        for wp in self.waypoints:
            self.canvas.create_oval(wp.get_bounding_box(), fill='red')

        # Draw the center line
        spline_x, spline_y = self._get_spline_points(self.waypoints, self.close_loop)

        if spline_x != []:
            point_list = []

            for k in range(len(spline_x)):
                point_list.append(m_to_pxl(spline_x[k]))
                point_list.append(m_to_pxl(spline_y[k]))

            self.canvas.create_line(point_list, smooth=True, fill='blue', width=2)

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

    def _close_loop_button_cb(self):
        if self.close_loop:
            self.close_loop = False
            self.close_loop_text.set("Close loop")
        else:
            self.close_loop = True
            self.close_loop_text.set("Open loop")

        self._update_window()

    def _get_spline_points(self, waypoints, periodical):
        """
            Interpolates a list of waypoints

            @param periodical: Whether the spline should be periodical
            @return: [pt_x, pt_y, d_x, d_y] -> interpolated spatial coordinates
        """
        if len(waypoints) < 2:
            return [], []

        # Create a spline from the waypoints
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

        if (len(wp_x) == 2):
            spline, _ = splprep([wp_x, wp_y], u=None, s=0.0, per=periodical, k=1)  # straight line
        elif (len(wp_x) == 3):
            spline, _ = splprep([wp_x, wp_y], u=None, s=0.0, per=periodical, k=2)  # degree 2
        else:
            spline, _ = splprep([wp_x, wp_y], u=None, s=0.0, per=periodical )

        # Interpolate the spline
        interval = np.linspace(0, 1, 10 * len(waypoints))
        spline_x, spline_y = splev(interval, spline, der=0)

        return list(spline_x), list(spline_y)


if __name__ == "__main__":
    display = TrackBuilder()
    display.mainloop()
