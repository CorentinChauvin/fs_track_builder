#!/usr/bin/python3
"""
    Graphical interface to build a Formula Student track

    Corentin Chauvin-Hameau - 2020
"""

##########################################
## Imports
#
from math import cos, sin, radians
import tkinter as tk
from tkinter import ttk
from src.config import *
from src.utils import DistanceConverter, Point
from src.waypoint import Waypoint
from src.track_builder import TrackBuilder
from src.track_exporter import TrackExporter
from src.sliders import OffsetSlider, BasicSlider

##########################################
## Class TrackBuilderGUI
#
class TrackBuilderGUI(tk.Frame, TrackBuilder, TrackExporter, DistanceConverter):
    """
    """
    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)
        TrackBuilder.__init__(self)
        TrackExporter.__init__(self)
        DistanceConverter.__init__(self)

        self.winfo_toplevel().title("Track builder")

        # Initialise diverse variables
        self.action_state = ADD_STATE
        self.waypoints = []
        self.is_dragging = False    # Whether a waypoint is being dragged (ie moved)
        self.dragged_wp_idx = None  # Index of the dragged waypoint
        self.close_loop = False     # Whether to close the loop
        self.cones_spacing = DEFAULT_SPACING_CONES
        self.orange_spacing = DEFAULT_SPACING_ORANGE
        self.snap_grid = False  # whether to snap waypoint moving/adding to grid
        self.grid_size = DEFAULT_GRID_SIZE
        self.initial_pose = [0.0, 0.0, 0.0]
        self.initial_pose_offset = {}
        self.initial_pose_offset['x'] = INIT_OFFSET_X
        self.initial_pose_offset['y'] = INIT_OFFSET_Y
        self.initial_pose_offset['yaw'] = radians(INIT_OFFSET_YAW)
        self.turning_radius = DEFAULT_TURNING_RADIUS  # Maximum turning radius (in m)

        # Initialise window
        self.pack(fill=tk.BOTH, expand=True)
        self.top_frame1 = tk.Frame(self)
        self.top_frame1.pack(fill=tk.X, expand=False)
        self.top_frame2 = tk.Frame(self)
        self.top_frame2.pack(fill=tk.X, expand=False)
        self.top_frame3 = tk.Frame(self)
        self.top_frame3.pack(fill=tk.X, expand=False)

        # First row of widgets (left)
        add_button = tk.Button(self.top_frame1, text="Add/Move", command=self._add_button_cb)
        add_button.pack(side=tk.LEFT)

        delete_button = tk.Button(self.top_frame1, text="Delete", command=self._delete_button_cb)
        delete_button.pack(side=tk.LEFT)

        separator = ttk.Separator(self.top_frame1, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill="y", padx=5)

        delete_last_button = tk.Button(self.top_frame1, text="Delete last cone", command=self._delete_last_button_cb)
        delete_last_button.pack(side=tk.LEFT)

        clear_button = tk.Button(self.top_frame1, text="Clear", command=self._clear_button_cb)
        clear_button.pack(side=tk.LEFT)

        separator = ttk.Separator(self.top_frame1, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill="y", padx=5)

        zoom_out_button = tk.Button(self.top_frame1, text="Zoom out", command=self._zoom_out_button_cb)
        zoom_out_button.pack(side=tk.LEFT)

        zoom_in_button = tk.Button(self.top_frame1, text="Zoom in", command=self._zoom_in_button_cb)
        zoom_in_button.pack(side=tk.LEFT)

        # First row of widgets (right)
        export_button = tk.Button(self.top_frame1, text="Export", command=self._export_button_cb)
        export_button.pack(side=tk.RIGHT)

        import_button = tk.Button(self.top_frame1, text="Import", command=self._import_button_cb)
        import_button.pack(side=tk.RIGHT)

        # Second row of widgets
        self.snap_grid_var = tk.IntVar()
        snap_grid_check = tk.Checkbutton(self.top_frame2, text=" Snap to grid", variable=self.snap_grid_var)
        snap_grid_check.pack(side=tk.LEFT)
        self.snap_grid_var.trace('w', self._snap_grid_cb)

        self.close_loop_var = tk.IntVar()
        close_loop_check = tk.Checkbutton(self.top_frame2, text=" Close loop", variable=self.close_loop_var)
        close_loop_check.pack(side=tk.LEFT)
        self.close_loop_var.trace('w', self._close_loop_cb)

        separator = ttk.Separator(self.top_frame2, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill="y", padx=5)

        self.orange_spacing_var = tk.StringVar()
        self.orange_spacing_var.set(str(DEFAULT_SPACING_ORANGE))
        self.orange_spacing_var.trace(
            "w", lambda name, index, mode,
            sv=self.orange_spacing_var:
                self._orange_spacing_cb(self.orange_spacing_var)
        )
        spacing_orange_lbl = tk.Label(self.top_frame2, text="Orange cones spacing (m):")
        spacing_orange_lbl.pack(side=tk.LEFT)
        spacing_orange_field = tk.Entry(self.top_frame2, width=4, textvariable=self.orange_spacing_var)
        spacing_orange_field.pack(side=tk.LEFT)

        self.spacing_var = tk.StringVar()
        self.spacing_var.set(str(DEFAULT_SPACING_CONES))
        self.spacing_var.trace(
            "w", lambda name, index, mode,
            sv=self.spacing_var: self._cones_spacing_cb(self.spacing_var)
        )
        spacing_lbl = tk.Label(self.top_frame2, text="Cones spacing (m):")
        spacing_lbl.pack(side=tk.LEFT)
        spacing_field = tk.Entry(self.top_frame2, width=4, textvariable=self.spacing_var)
        spacing_field.pack(side=tk.LEFT)

        random_spacing_lbl = tk.Label(self.top_frame2, text="Randomisation of cones spacing (m):")
        random_spacing_lbl.pack(side=tk.LEFT)
        self.random_spacing_slider = BasicSlider(0.0, [0.0, 1.0], 0.01, self, self.top_frame2)

        # Third row of widgets
        self.turning_radius_var = tk.StringVar()
        self.turning_radius_var.set(str(DEFAULT_TURNING_RADIUS))
        self.turning_radius_var.trace(
            "w", lambda name, index, mode,
            sv=self.turning_radius_var: self._turning_radius_var(self.turning_radius_var)
        )

        radius_lbl = tk.Label(self.top_frame3, text="Max turning radius (m):")
        radius_lbl.pack(side=tk.LEFT)
        radius_field = tk.Entry(self.top_frame3, width=4, textvariable=self.turning_radius_var)
        radius_field.pack(side=tk.LEFT)

        separator = ttk.Separator(self.top_frame3, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, fill="y", padx=5)

        offset_lbl = tk.Label(self.top_frame3, text="Offset on the initial pose (m and °):")
        offset_lbl.pack(side=tk.LEFT)
        self.slider_x = OffsetSlider('x', [-3.0, 3.0], self)
        self.slider_y = OffsetSlider('y', [-1.5, 1.5], self)
        self.slider_yaw = OffsetSlider('yaw', [-90, 90], self)

        # Canvas (and its scrollbars)
        self.canvas = tk.Canvas(self, background="white")
        self.canvas.config(width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        sc_w = SCROLLABLE_CANVAS_WIDTH / 2.0
        sc_h = SCROLLABLE_CANVAS_HEIGHT / 2.0
        self.canvas.config(scrollregion=(-sc_w, -sc_h, sc_w, sc_h))

        self.x_scrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.x_scrollbar.config(command=self.canvas.xview)
        self.y_scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.y_scrollbar.config(command=self.canvas.yview)

        self.canvas.config(xscrollcommand=self.x_scrollbar.set, yscrollcommand=self.y_scrollbar.set)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Declare window events
        self.canvas.bind("<Motion>", self._mouse_motion_cb)
        self.canvas.bind("<Button-1>", self._left_click_cb)
        self.canvas.bind("<ButtonRelease-1>", self._left_release_cb)
        self.canvas.bind("<Control-Button-1>", self._ctrl_left_click_cb)
        self.canvas.bind("<Button-4>", self._mouse_scroll_up_cb)
        self.canvas.bind("<Button-5>", self._mouse_scroll_down_cb)
        self.canvas.bind("<Shift-Button-4>", self._mouse_scroll_left_cb)
        self.canvas.bind("<Shift-Button-5>", self._mouse_scroll_right_cb)
        self.canvas.focus_set()  # give focus to the canvas so that it captures key events

    def update_window(self):
        """ Draw all the objects in the window again
        """
        self.canvas.delete(tk.ALL)

        # Draw the waypoints
        for wp in self.waypoints:
            self.canvas.create_oval(wp.get_bounding_box(), fill='red')

        # Update and draw the center line
        center_points, curvatures = self.compute_center_points(self.waypoints, self.close_loop)
        if center_points == []:
            self.cones = {}
            return
        self._draw_center_line(center_points, curvatures)

        # Update and draw sides
        left_points, right_points = self.compute_side_points(TRACK_WIDTH)
        if left_points == [] or right_points == []:
            self.cones = {}
            return
        self.canvas.create_line(left_points, smooth=True, fill='green', width=1.5)
        self.canvas.create_line(right_points, smooth=True, fill='green', width=1.5)

        # Update and draw cones
        cones_spacing_randomisation = self.random_spacing_slider.get_value()
        cones = self.compute_cones(
            self.cones_spacing, cones_spacing_randomisation,
            self.orange_spacing, self.close_loop
        )
        radius = self.m_to_pxl(CONE_RADIUS)

        for color in self.cones:
            for cone in cones[color]:
                x = self.m_to_pxl(cone.x)
                y = self.m_to_pxl(cone.y)
                self.canvas.create_oval([x-radius, y-radius, x+radius, y+radius], fill=color)

        # Update and draw starting position
        self.initial_pose = self.compute_start_pose(self.waypoints, self.initial_pose_offset)
        x1 = self.m_to_pxl(self.initial_pose[0])
        y1 = self.m_to_pxl(self.initial_pose[1])
        x2 = x1 + 20*cos(self.initial_pose[2])
        y2 = y1 + 20*sin(self.initial_pose[2])
        self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, arrowshape="8 10 5", width=5, fill="red")

    def _draw_center_line(self, center_points, curvatures):
        """ Draw the center line

            @param center_points: List of pixel coordinates ready to draw the center line
                                  [x1, y1, x2, y2, ...]
            @param curvatures:    Curvatures at each point
        """
        for k in range(len(curvatures)-1):
            points = center_points[2*k:2*(k+2)]
            max_curvature = 1.0 / self.turning_radius

            if abs(curvatures[k]) > max_curvature:
                self.canvas.create_line(points, smooth=True, fill='red', width=2)
            else:
                self.canvas.create_line(points, smooth=True, fill='blue', width=1, dash=(5, 10))


    def _mouse_motion_cb(self, event):
        """ Callback for any motion of the mouse

            Moves waypoint if it is being dragged.
        """
        self.canvas.focus_set()  # give focus to the canvas so that it captures key events

        offset_x = (self.x_scrollbar.get()[0] - 0.5) * SCROLLABLE_CANVAS_WIDTH
        offset_y = (self.y_scrollbar.get()[0] - 0.5) * SCROLLABLE_CANVAS_HEIGHT
        pxl_x = event.x + offset_x  # cursor position (in pxl)
        pxl_y = event.y + offset_y

        redraw = False  # whether the window needs to be drawn again

        if not self.is_dragging:
            for wp in self.waypoints:
                redraw = wp.update_hovering(pxl_x, pxl_y) or redraw
        else:
            x = self.pxl_to_m(pxl_x)
            y = self.pxl_to_m(pxl_y)

            if self.snap_grid or (event.state == 276):
                x, y = self.snap_coord_to_grid(x, y, self.grid_size)

            # Check whether it would collides with another waypoint
            collision = False
            for i, wp in enumerate(self.waypoints):
                if i != self.dragged_wp_idx and wp.is_colliding(self.m_to_pxl(x), self.m_to_pxl(y)):
                    collision = True
                    break
            if not collision:
                self.waypoints[self.dragged_wp_idx].update_position(x, y)
                redraw = True

        if redraw:
            self.update_window()

    def _left_click_cb(self, event):
        """ Callback for the left click

            Adds, deletes or moves waypoints, depending on the action state
        """
        offset_x = (self.x_scrollbar.get()[0] - 0.5) * SCROLLABLE_CANVAS_WIDTH
        offset_y = (self.y_scrollbar.get()[0] - 0.5) * SCROLLABLE_CANVAS_HEIGHT
        pxl_x = event.x + offset_x  # cursor position (in pxl)
        pxl_y = event.y + offset_y

        if self.action_state == ADD_STATE:
            x = self.pxl_to_m(pxl_x)  # cursor position (in m)
            y = self.pxl_to_m(pxl_y)

            # Check whether it collides with an already existing waypoint
            for i, wp in enumerate(self.waypoints):
                if wp.is_colliding(pxl_x, pxl_y):
                    self.is_dragging = True
                    self.dragged_wp_idx = i
                    return

            # Snaps to grid if necessary, and check that the snapped position is
            # not already taken
            if self.snap_grid:
                x, y = self.snap_coord_to_grid(x, y, self.grid_size)
                pxl_x = self.m_to_pxl(x)
                pxl_y = self.m_to_pxl(y)

                for i, wp in enumerate(self.waypoints):
                    if wp.is_colliding(pxl_x, pxl_y):
                        return

            # If not, add a new waypoint
            self.waypoints.append(Waypoint(x, y, WAYPOINTS_RADIUS))
            self.update_window()

        elif self.action_state == DELETE_STATE:
            for i, wp in enumerate(self.waypoints):
                if wp.is_colliding(pxl_x, pxl_y):
                    del self.waypoints[i]
                    break

            self.update_window()

    def _left_release_cb(self, event):
        self.is_dragging = False

    def _ctrl_left_click_cb(self, event):
        self._left_click_cb(event)

    def _mouse_scroll_up_cb(self, event):
        self.canvas.yview_scroll(-1, "units")

    def _mouse_scroll_down_cb(self, event):
        self.canvas.yview_scroll(1, "units")

    def _mouse_scroll_left_cb(self, event):
        self.canvas.xview_scroll(-1, "units")

    def _mouse_scroll_right_cb(self, event):
        self.canvas.xview_scroll(1, "units")

    def _add_button_cb(self):
        self.action_state = ADD_STATE

    def _delete_button_cb(self):
        self.action_state = DELETE_STATE

    def _delete_last_button_cb(self):
        if self.waypoints != []:
            del self.waypoints[-1]
            self.update_window()

    def _clear_button_cb(self):
        self.waypoints = []
        self.update_window()

    def _zoom_out_button_cb(self):
        DistanceConverter.zoom_out()
        for p in self.waypoints:
            p.update_pxl_position()
        self.update_window()

    def _zoom_in_button_cb(self):
        DistanceConverter.zoom_in()
        for p in self.waypoints:
            p.update_pxl_position()
        self.update_window()

    def _export_button_cb(self):
        self.export_track(self.cones, self.waypoints, self.initial_pose)

    def _import_button_cb(self):
        new_waypoints = self.import_track(WAYPOINTS_RADIUS)

        if new_waypoints != []:
            self.waypoints = new_waypoints
            self.update_window()

    def _close_loop_cb(self, a, b, c):
        self.close_loop = self.close_loop_var.get()
        self.update_window()

    def _snap_grid_cb(self, a, b, c):
        self.snap_grid = self.snap_grid_var.get()

    def _cones_spacing_cb(self, string_var):
        try:
            self.cones_spacing = float(string_var.get())
            self.update_window()
        except ValueError:  # catch wrong inputs
            pass

    def _orange_spacing_cb(self, string_var):
        try:
            self.orange_spacing = float(string_var.get())
            self.update_window()
        except ValueError:  # catch wrong inputs
            pass

    def _turning_radius_var(self, string_var):
        try:
            self.turning_radius = float(string_var.get())

            if self.turning_radius == 0.0:
                self.turning_radius = 1.0

            self.update_window()
        except ValueError:  # catch wrong inputs
            pass


if __name__ == "__main__":
    display = TrackBuilderGUI()
    display.mainloop()
