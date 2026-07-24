from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import QObject, Signal, Slot
from calc import *
from math import *

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
        self.initCoil() # always default tab, needs to be updated manually

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
        match (self.frontend.tabs.currentIndex()):
            case 0:
                self.updateCoil()
            case 1:
                self.updateRod()
            case 2:
                self.updateWheel()

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

    ###                 ###
    #    Actuator tabs    #
    ###                 ###

    def tabChanged(self, value):
        """
        Active tab changed
        """
        match(value):
            case 0:
                self.initCoil()
            case 1:
                self.initRod()
            case 2:
                self.initWheel()

    ###                              ###
    #    Magnetotorquer Coil Sizing    #
    ###                              ###

    def initCoil(self):
        """
        Initialize all values needed for coil tab
        """
        self.coilVolt = self.frontend.coil_volt.value()
        self.coilDiameter = self.frontend.coil_diameter.value()/1000
        self.coilShape = self.frontend.coil_shape.currentText()
        self.coilTurns = self.frontend.coil_turns.value()
        self.coilMat = self.frontend.coil_mat.currentText()

        # weird order to avoid crashes (should maybe be changed to a try ... except)
        self.coilDipoleTarget = 2*self.total/self.minMag
        self.updateCoil()
        self.frontend.dipole_target.setValue(self.coilDipoleTarget) #this will trigger newDipoleTarget()


    @Slot(int)
    def newDipoleTarget(self, value):
        """
        User has supplied new Target Dipole Momen
        """
        self.coilDipoleTarget = value
        self.updateCoilPassFail() # save some processing power

    @Slot(int)
    def newCoilVolt(self, value):
        """
        User has supplied new Supply Voltage
        """
        self.coilVolt = value
        self.updateCoil()

    @Slot(int)
    def newCoilDiameter(self, value):
        """
        User has supplied new Wire Diameter
        """
        self.coilDiameter = value
        self.updateCoil()

    @Slot(str)
    def newCoilShape(self, value):
        """
        User has supplied new Coil Shape
        """
        self.coilShape = value
        self.updateCoil()

    @Slot(int)
    def newCoilTurns(self, value):
        """
        User has supplied new Number of Turns
        """
        self.coilTurns = value
        self.updateCoil()

    @Slot(str)
    def newCoilMat(self, value):
        """
        User has supplied new Wire Material
        """
        self.coilMat = value
        self.updateCoil()


    def updateCoil(self):
        """
        Calculate all the coil parameters and push to frontend
        """
        self.dipole, self.resistance, self.current, self.power, self.mass, self.turns, self.length = calcCoil(self.coilVolt, self.coilDiameter, self.coilShape, self.coilTurns, self.coilMat, self.form)

        self.frontend.dipole_label.setText(str(round(self.dipole, 3)))
        self.frontend.resistance_label.setText(str(round(self.resistance, 3)))
        self.frontend.current_label.setText(str(round(self.current, 3)))
        self.frontend.power_label.setText(str(round(self.power, 3)))
        self.frontend.mass_label.setText(str(round(self.mass, 3)))
        self.frontend.turns_label.setText(str(round(self.turns, 3)))
        self.frontend.length_label.setText(str(round(self.length, 3)))

        self.updateCoilPassFail()


    def updateCoilPassFail(self):
        """
        Calculate the coil pass/fail and push to frontend
        """
        default = Default()
        match (self.form):
            case "3U":
                satParams = default.threeU
            case "6U":
                satParams = default.sixU
            case "12U":
                satParams = default.twelveU
        if self.dipole >= self.coilDipoleTarget \
            and self.power <= satParams["max_avg_power"] \
            and self.mass <= satParams["max_mass"]:
            self.frontend.coil_status.setText("PASS")
            self.frontend.coil_status.setStyleSheet("background: green; color: white; padding: 6px;")
        else:
            self.frontend.coil_status.setText("FAIL")
            self.frontend.coil_status.setStyleSheet("background: red; color: white; padding: 6px;")


    ###                             ###
    #    Magnetotorquer Rod Sizing    #
    ###                             ###
    def initRod(self):
        """
        Initialize all values needed for rod tab
        """
        #TODO: take values from frontend
        self.rodVolt = 3
        self.rodWireDiameter = 0.15/1000
        self.rodCoreDiameter = 8/1000
        self.rodLength = 60/1000
        self.rodMaterial = "Mu-metal"
        self.rodLayers = 1

        # weird order to avoid crashes (should maybe be changed to a try ... except)
        self.rodDipoleTarget = 2*self.total/self.minMag
        self.updateRod()

    def updateRod(self):
        """
        Calculate all the rod parameters and push to frontend
        """
        self.dipole, self.resistance, self.current, self.power, self.mass, self.turns, self.mu_eff, self.N_d, self.maxTurns = calcRod(self.rodVolt, self.rodWireDiameter, self.rodCoreDiameter, self.rodLength, self.RodMaterial, self.rodLayers)

        # TODO: update frontend once frontend is able to be updated


    ###                         ###
    #    Reaction Wheel Sizing    #
    ###                         ###
    def initWheel(self):
        """
        Initialize all values needed for wheel tab
        """
        #TODO: take values from frontend
        self.wheelAngle = math.radians(30)
        self.wheelTime = 90
        self.wheelslewAxis = "x"
        self.wheelShape = "Solid Disk"
        self.wheelOuterRadius = 30/1000
        self.wheelInnerRadius = 20/1000
        self.wheelThiccness = 10/1000
        self.wheelMaterial = "Aluminium"
        self.wheelMaxSpeed = (6000*math.tau)/60
        self.wheelInterval = 1

        self.updateWheel()

    def updateWheel(self):
        self.torque, self.mass, self.maxAngularMomentum = calcWheel(self.wheelAngle, self.wheelTime, self.wheelSlewAxis, self.wheelShape, self.wheelOuterRadius, self.wheelInnerRadius, self.wheelThiccness, self.wheelMaterial, self.wheelMaxSpeed, self.wheelInterval, self.form)

