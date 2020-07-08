#!/usr/bin/env python
"""
    Graphical interface to build a Formula Student track

    Corentin Chauvin-Hameau - 2020
"""

import tkinter as tk

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
WAYPOINTS_RADIUS = 5

ADD_STATE = 'add'        # Adding waypoints
DELETE_STATE = 'delete'  # Removing waypoints


class Waypoint(object):
    """
    """
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.is_hovered = False  # whether the mouse is over the waypoint

        self.left   = self.x - WAYPOINTS_RADIUS  # bounding box coordinates
        self.right  = self.x + WAYPOINTS_RADIUS
        self.top    = self.y - WAYPOINTS_RADIUS
        self.bottom = self.y + WAYPOINTS_RADIUS

    def is_colliding(self, x, y):
        """ Checks whether a given point is within the waypoint
        """
        return x >= self.left and x <= self.right \
            and y >= self.top and y <= self.bottom

    def draw(self, canvas):
        """ Draws the waypoint on a given canvas
        """
        bounding_box = (self.left, self.top, self.right, self.bottom)
        canvas.create_oval(bounding_box, fill='red')

    def update_hovering(self, x, y):
        """ Updates whether the mouse is hovering the waypoint given mouse coordinates

            @ return: Whether the hovering state has changed
        """
        if self.is_colliding(x, y):
            if not self.is_hovered:
                self.is_hovered = True

                radius = 1.5 * WAYPOINTS_RADIUS
                self.left   = self.x - radius
                self.right  = self.x + radius
                self.top    = self.y - radius
                self.bottom = self.y + radius

                return True

        else:
            if self.is_hovered:
                self.is_hovered = False

                self.left   = self.x - WAYPOINTS_RADIUS
                self.right  = self.x + WAYPOINTS_RADIUS
                self.top    = self.y - WAYPOINTS_RADIUS
                self.bottom = self.y + WAYPOINTS_RADIUS

                return True

        return False

    def __repr__(self):
        return self._display()

    def __str__(self):
        return self._display()

    def _display(self):
        """ Displays its coordinates
        """
        return "({}, {})".format(self.x, self.y)


class TrackBuilder(tk.Frame):
    """
    """
    def __init__(self, parent=None):
        tk.Frame.__init__(self, parent)

        # Initialise the widgets
        self.pack(fill=tk.BOTH, expand=True)

        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill=tk.BOTH, expand=True)

        self.add_button = tk.Button(self.top_frame, text="Add", command=self._add_button_cb)
        self.add_button.pack(side=tk.LEFT)
        self.delete_button = tk.Button(self.top_frame, text="Delete", command=self._delete_button_cb)
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
        self.is_dragging = False  # Whether a waypoint is being dragged (ie moved)
        self.waypoints = []

    def _update_window(self):
        """ Draw all the objects in the window again
        """
        self.canvas.delete(tk.ALL)

        for wp in self.waypoints:
            wp.draw(self.canvas)

    def _mouse_motion_cb(self, event):
        """
        """
        redraw = False  # whether the window needs to be drawn again

        if not self.is_dragging:
            for wp in self.waypoints:
                redraw = wp.update_hovering(event.x, event.y) or redraw

        if redraw:
            self._update_window()

    def _left_click_cb(self, event):
        """
        """
        if self.action_state == ADD_STATE:
            # Check that it doesn't collid with an already existing waypoint
            for wp in self.waypoints:
                if wp.is_colliding(event.x, event.y):
                    return

            # If not, add a new waypoint
            self.waypoints.append(Waypoint(event.x, event.y))
            self._update_window()

        if self.action_state == DELETE_STATE:
            for i, wp in enumerate(self.waypoints):
                if wp.is_colliding(event.x, event.y):
                    del self.waypoints[i]
                    break

            self._update_window()

    def _left_release_cb(self, event):
        """
        """
        pass

    def _add_button_cb(self):
        """
        """
        self.action_state = ADD_STATE

    def _delete_button_cb(self):
        """
        """
        self.action_state = DELETE_STATE


if __name__ == "__main__":
    display = TrackBuilder()
    display.mainloop()
