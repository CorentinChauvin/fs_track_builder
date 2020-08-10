"""
    Convenience classes for defining some sliders
"""

from math import radians
import tkinter as tk


class OffsetSlider(object):
    """ Sliders for changing the initial pose offsets
    """
    def __init__(self, key, bounds, gui):
        """ @param key: 'x', 'y', or 'yaw'
            @param bounds: [min, max] -> bounds on the offset
            @param gui: reference to the TrackBuilderGUI instance
        """
        self.gui = gui
        self.key = key

        self.offset_var = tk.DoubleVar()
        self.offset_var.set(gui.initial_pose_offset[key])
        self.offset_var.trace(
            "w", lambda name, index, mode,
            sv=self.offset_var:
                self._offset_cb(self.offset_var)
        )
        resolution = 1 if key == 'yaw' else 0.1
        offset_scale = tk.Scale(
            gui.top_frame3, from_=bounds[0], to=bounds[1], resolution=resolution,
            orient=tk.HORIZONTAL, variable=self.offset_var)
        offset_scale.pack(side=tk.LEFT)

    def _offset_cb(self, var):
        value = self.offset_var.get()
        if self.key == 'yaw':
            value = radians(value)

        self.gui.initial_pose_offset[self.key] = value
        self.gui.update_window()


class BasicSlider(object):
    """ Basic slider storing one double value
    """
    def __init__(self, default_value, bounds, resolution, gui, frame):
        """ @param default_value: default value of the slider
            @param bounds: [min, max] -> bounds on the offset
            @param resolution: resolution of the slider
            @param gui: reference to the TrackBuilderGUI instance
            @param frame: tk frame in which add the slider
        """
        self.gui = gui
        self.var = tk.DoubleVar()
        self.var.set(default_value)

        self.var.trace(
            "w", lambda name, index, mode,
            sv=self.var: self._callback(self.var)
        )
        scale = tk.Scale(
            frame, from_=bounds[0], to=bounds[1], resolution=resolution,
            orient=tk.HORIZONTAL, variable=self.var)
        scale.pack(side=tk.LEFT)

    def _callback(self, var):
        self.gui.update_window()

    def get_value(self):
        return self.var.get()
