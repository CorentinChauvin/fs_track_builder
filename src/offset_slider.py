"""
    Convenience class for defining sliders to modify the offsets on the initial
    pose
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
