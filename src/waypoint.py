"""
    Definition of a class to handle movable waypoints
"""

from src.utils import pxl_to_m, m_to_pxl, Point


class Waypoint(Point):
    """ Handles movable waypoint GUI behaviour
    """
    def __init__(self, x=0.0, y=0.0, radius=1.0):
        super().__init__(x, y)    # spatial coordinates (in meters)
        self.pxl_x = m_to_pxl(x)  # canvas coordinates (in pixels)
        self.pxl_y = m_to_pxl(y)
        self.is_hovered = False  # whether the mouse is over the waypoint

        self.base_radius = radius
        self.radius = radius  # will change when the waypoint is being hovered
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
                self.radius = 1.5 * self.base_radius
                self._update_bounding_box()

                return True
        else:
            if self.is_hovered:
                self.is_hovered = False
                self.radius = self.base_radius
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
