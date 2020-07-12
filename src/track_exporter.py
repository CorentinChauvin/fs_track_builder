"""
    Definition of a class for importing/exporting tracks
"""

import yaml
import tkinter as tk
from tkinter.filedialog import asksaveasfile, askopenfilename
from src.waypoint import Waypoint


class TrackExporter(object):
    """ Base class for the TrackBuilderGUI, handles importing/exporting tracks
    """

    def export_track(self, cones, waypoints, initial_pose):
        """ Exports the track as a YAML file

            @param cones:        Dictionary of cones coordinates (sorted by color)
            @param waypoints:    List of waypoints
            @param initial_pose: [x, y, yaw] -> initial pose of the car (m and radians)
        """
        f = asksaveasfile(
            mode="w",
            filetypes=(("YAML files", "*.yaml"), ("All files", "*.*"))
        )

        if f is None:
            return

        # Initial pose
        f.write("initial_pose:\n")
        f.write("  x: {:7.2f}  # x coordinate of the rear axle\n".format(initial_pose[0]))
        f.write("  y: {:7.2f}  # y coordinate of the rear axle\n".format(initial_pose[1]))
        f.write("  z: {:7.2f}  # yaw in radians\n".format(initial_pose[2]))

        # Cones
        f.write("\ncones:\n")

        for key in cones:
            color = key if key != 'orange' else 'big_orange'
            f.write("  {}: [\n".format(color))

            for cone in cones[key]:
                f.write("    [{:.2f}, {:.2f}],\n".format(cone.x, cone.y))

            f.write("  ]\n")

        # Waypoints
        f.write("\nwaypoints: [\n")

        for waypoint in waypoints:
            f.write("  [{:.2f}, {:.2f}],\n".format(waypoint.x, waypoint.y))

        f.write("]\n")
        f.close()

    def import_track(self, waypoint_radius):
        """ Imports the track from a YAML file

            @param waypoint_radius: Radius (in pixels) of the waypoint
            @return: List of waypoints
        """

        file_name = askopenfilename(
            defaultextension='yaml',
            filetypes=(("YAML files", "*.yaml"), ("All files", "*.*"))
        )

        try:
            f = open(file_name, 'r')
        except Exception:
            return []
        else:
            if f is None:
                return []

        data = yaml.load(f, Loader=yaml.FullLoader)
        f.close()

        waypoints = [
            Waypoint(
                data['waypoints'][k][0], data['waypoints'][k][1], waypoint_radius
            )
            for k in range(len(data['waypoints']))
        ]

        return waypoints
