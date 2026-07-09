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
        self.form = "3U"

    def update(self):
        """
        Force update with existing values
        used for the weird init
        """
        self.updateOrbit()

    ###                              ###
    #    ORBITAL PARAMETER HANDLING    #
    ###                              ###

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

    @Slot(str)
    def newForm(self, value):
        """
        User has supplied a new form factor
        """
        self.form = value
        self.updateDisturbance()

    def updateOrbit(self):
        """
        Update orbital summary and push to frontend
        """
        self.period, self.velocity, self.density, self.minMag, self.maxMag, self.angVelocity = calcOrbit(self.altitude, self.inclination)

        self.frontend.period_label.setText(str(round(self.period/60, 3)))
        self.frontend.velocity_label.setText(str(round(self.velocity, 3)))
        self.frontend.density_label.setText(str(format(self.density, ".2e")))
        self.frontend.min_mag_label.setText(str(format(self.minMag, ".2e")))
        self.frontend.max_mag_label.setText(str(format(self.maxMag, ".2e")))

        self.updateDisturbance()

    def updateDisturbance(self):
        """
        Update disturbance summary and push to frontend
        """
        self.gg, self.drag, self.srp, self.mag = calcDisturbance(self.velocity, self.angVelocity, self.density, self.maxMag, self.form)
        self.total = self.gg+self.drag+self.srp+self.mag

        self.frontend.gg_label.setText(str(format(self.gg, ".2e")))
        self.frontend.drag_label.setText(str(format(self.drag, ".2e")))
        self.frontend.srp_label.setText(str(format(self.srp, ".2e")))
        self.frontend.mag_label.setText(str(format(self.mag, ".2e")))
        self.frontend.total_label.setText(str(format(self.total, ".2e")))

        self.frontend.disturbance_canvas.ax.clear()
        self.frontend.disturbance_canvas.ax.set_title("Disturbance comparison")
        self.frontend.disturbance_canvas.ax.bar(["Gravity", "Drag", "Solar", "Magnetic"], [self.gg, self.drag, self.srp, self.mag])
        self.frontend.disturbance_canvas.draw()
