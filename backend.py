from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import QObject, Signal, Slot
from calc import *

class Backend(QObject):
    """
    Backend class, holding all the values in the UI, using calc to calcuate, and then pushing to the frontend
    """
    def __init__(self, frontend):
        self.frontend = frontend
        self.altitude = 300
        self.inclination = 0

        self.updateOrbit()

    @Slot(int)
    def newAlt(self, value):
        """
        User has supplied a new altitude value
        """
        self.altitude = value
        self.updateOrbit()

    @Slot(int)
    def newInclination(self, value):
        """
        User has supplied a new inclination value
        """
        self.inclination = value
        self.updateOrbit()

    def updateOrbit(self):
        """
        Update orbital summary and push to frontend
        """
        self.period, self.velocity, self.density, self.minMag, self.maxMag = calcOrbit(self.altitude, self.inclination)

        try:
            self.frontend.period_label.setText(str(round(self.period/60, 3)))
            self.frontend.velocity_label.setText(str(round(self.velocity, 3)))
            self.frontend.density_label.setText(str(format(self.density, ".2e")))
            self.frontend.min_mag_label.setText(str(format(self.minMag, ".2e")))
            self.frontend.max_mag_label.setText(str(format(self.maxMag, ".2e")))
        except AttributeError:
            pass
