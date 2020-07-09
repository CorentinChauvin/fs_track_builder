#!/usr/bin/env python
"""
    Graphical interface to build a Formula Student track

    Corentin Chauvin-Hameau - 2020
"""

##########################################
## Imports
#
import tkinter as tk
from src.config import *
from src.utils import pxl_to_m, m_to_pxl, Point
from src.waypoint import Waypoint
from src.track_builder import TrackBuilder

##########################################
## Class TrackBuilderGUI
#
class TrackBuilderGUI(tk.Frame, TrackBuilder):
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

        # Update and draw the center line
        center_points = self.compute_center_points(self.waypoints, self.close_loop)
        if center_points == []:
            return
        self.canvas.create_line(center_points, smooth=True, fill='blue', width=1, dash=(5, 10))

        # Update and draw sides
        left_points, right_points = self.compute_side_points(TRACK_WIDTH)
        if left_points == [] or right_points == []:
            return
        self.canvas.create_line(left_points, smooth=True, fill='green', width=1.5)
        self.canvas.create_line(right_points, smooth=True, fill='green', width=1.5)

        # Update and draw cones
        left_cones, right_cones = self.compute_cones(self.cones_inter_distance)
        if left_cones == [] or right_cones == []:
            return
        radius = m_to_pxl(CONE_RADIUS)

        for cone in left_cones:
            x = m_to_pxl(cone.x)
            y = m_to_pxl(cone.y)
            self.canvas.create_oval([x-radius, y-radius, x+radius, y+radius], fill='yellow')

        for cone in right_cones:
            x = m_to_pxl(cone.x)
            y = m_to_pxl(cone.y)
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
            self.waypoints.append(Waypoint(x, y, WAYPOINTS_RADIUS))
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


if __name__ == "__main__":
    display = TrackBuilderGUI()
    display.mainloop()
