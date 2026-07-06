from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QComboBox, QTabWidget, QSplitter,
    QFormLayout, QSpinBox, QDoubleSpinBox, QGridLayout
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from properties import default
from backend import Backend


class MplCanvas(FigureCanvas):
    def __init__(self):
        self.figure = Figure(figsize=(5, 3))
        self.ax = self.figure.add_subplot(111)
        super().__init__(self.figure)

        self.ax.set_title("Placeholder Plot")
        self.ax.text(
            0.5, 0.5,
            "Backend will update this plot",
            ha="center",
            va="center",
            transform=self.ax.transAxes
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ADCS Actuator Sizing Tool (GUI Shell)")
        self.resize(1400, 850)
        self.backend = Backend(self)

        splitter = QSplitter(Qt.Horizontal)

        splitter.addWidget(self.create_left_panel())
        splitter.addWidget(self.create_tabs())

        splitter.setSizes([350, 1000])

        self.setCentralWidget(splitter)

    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)

        cubesat_group = QGroupBox("CubeSat Configuration")
        cubesat_layout = QFormLayout()

        self.form_factor_combo = QComboBox()
        self.form_factor_combo.addItems(["3U", "6U", "12U"])

        cubesat_layout.addRow("Form Factor:", self.form_factor_combo)
        cubesat_group.setLayout(cubesat_layout)

        orbit_group = QGroupBox("Orbit Parameters")
        orbit_layout = QFormLayout()
        
        #ALtitude
        self.orbit_combo = QSpinBox()
        self.orbit_combo.setRange(300, 800)
        self.orbit_combo.valueChanged.connect(self.backend.newAlt)

        #Inclination
        self.inclination = QDoubleSpinBox()
        self.inclination.setRange(0, 98)
        self.inclination.setDecimals(1)
        self.inclination.valueChanged.connect(self.backend.newInclination)

        orbit_layout.addRow("Orbit Altitude (km):", self.orbit_combo)
        orbit_layout.addRow("Inclination (degrees):", self.inclination)
        orbit_group.setLayout(orbit_layout)


        orbital_group = QGroupBox("Orbital Summary")
        orbital_layout = QFormLayout()

        #TODO add connection to the back end math
        self.period_label = QLabel(str(round(self.backend.period/60, 3)))
        self.velocity_label = QLabel(str(round(self.backend.velocity, 3)))
        self.density_label = QLabel(str(format(self.backend.density, ".2e")))
        self.min_mag_label = QLabel(str(format(self.backend.minMag, ".2e")))
        self.max_mag_label = QLabel(str(format(self.backend.maxMag, ".2e")))

        orbital_layout.addRow("Period Time (min):", self.period_label)
        orbital_layout.addRow("Velocity (km/s):", self.velocity_label)
        orbital_layout.addRow("Atmospheric Density (kg/m^3):", self.density_label)
        orbital_layout.addRow("Minimum Magnetic field (T):", self.min_mag_label)
        orbital_layout.addRow("Maximum Magnetic field (T):", self.max_mag_label)

        orbital_group.setLayout(orbital_layout)


        disturbance_group = QGroupBox("Disturbance Budget")
        disturbance_layout = QVBoxLayout()

        #Check if this is a bar chart
        self.disturbance_canvas = MplCanvas()
        disturbance_layout.addWidget(self.disturbance_canvas)

        disturbance_group.setLayout(disturbance_layout)

        summary_group = QGroupBox("Disturbance Summary")
        summary_layout = QFormLayout()

        self.gg_label = QLabel("--")
        self.drag_label = QLabel("--")
        self.srp_label = QLabel("--")
        self.mag_label = QLabel("--")
        self.expul_label = QLabel("0")
        self.total_label = QLabel("--")

        summary_layout.addRow("Gravity Gradient:", self.gg_label)
        summary_layout.addRow("Drag:", self.drag_label)
        summary_layout.addRow("Solar Pressure:", self.srp_label)
        summary_layout.addRow("Magnetic:", self.mag_label)
        summary_layout.addRow("Propulsion (Assumed): ", self.expul_label)
        summary_layout.addRow("Total:", self.total_label)

        summary_group.setLayout(summary_layout)

        layout.addWidget(cubesat_group)
        layout.addWidget(orbit_group)
        layout.addWidget(orbital_group)
        layout.addWidget(disturbance_group)
        layout.addWidget(summary_group)
        layout.addStretch()

        return panel

    def create_tabs(self):
        tabs = QTabWidget()

        tabs.addTab(self.create_coil_tab(), "Magnetorquer Coil")
        tabs.addTab(self.create_rod_tab(), "Magnetorquer Rod")
        tabs.addTab(self.create_wheel_tab(), "Reaction Wheel")

        return tabs

    def create_coil_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        top = QHBoxLayout()

        inputs = QGroupBox("Inputs")
        inputs_layout = QFormLayout()

        self.dipole_taget = QDoubleSpinBox()
        self.dipole_taget.setRange(0.01, 10)
        self.dipole_taget.setDecimals(2)
        self.dipole_taget.setValue(default.coil["m_target"])
        #INSERT SET VALUE BASED ON ORBIT

        self.coil_volt = QDoubleSpinBox()
        self.coil_volt.setRange(1.8, 12)
        self.coil_volt.setDecimals(2)
        self.coil_volt.setValue(default.coil["v_supply"])

        self.coil_diameter = QDoubleSpinBox()
        self.coil_diameter.setRange(0.05, 1.0)
        self.coil_diameter.setDecimals(2)
        self.coil_diameter.setValue(default.coil["d_w"])

        self.coil_shape = QComboBox()
        self.coil_shape.addItems(["Square", "Rectangular", "Circular"])
        #self.coil_shape.setValue(default.coil["shape"])

        self.coil_turns = QSpinBox()
        self.coil_turns.setRange(1, 2000)
        self.coil_turns.setValue(default.coil["n"])
        #INSERT FUNCTION TO GET REASONABLE SET VALUE


        self.coil_mat = QComboBox()
        self.coil_mat.addItems(["Copper", "Aluminium"])
        #self.coil_mat.setValue(default.coil["material"])


        inputs_layout.addRow("Target Dipole Moment:", self.dipole_taget)
        inputs_layout.addRow("Supply Voltage:", self.coil_volt)
        inputs_layout.addRow("Wire Diameter", self.coil_diameter)
        inputs_layout.addRow("Coil Shape", self.coil_shape)
        inputs_layout.addRow("Number of Turns:", self.coil_turns)
        inputs_layout.addRow("Wire Material:", self.coil_mat)

        inputs.setLayout(inputs_layout)

        outputs = QGroupBox("Outputs")
        outputs_layout = QFormLayout()


        #TODO Add the values to connect here
        outputs_layout.addRow("Achieved Moment:", QLabel("--"))
        outputs_layout.addRow("Coil Resistance (Ohm):", QLabel("--"))
        outputs_layout.addRow("Operating Curren (A):", QLabel("--"))
        outputs_layout.addRow("Power Consumption (W):", QLabel("--"))
        outputs_layout.addRow("Coil Mass:", QLabel("--"))
        outputs_layout.addRow("Number of Turns:", QLabel(self.coil_turns))
        outputs_layout.addRow("Total Wire Lenght:", QLabel("--"))
        #TODO Add graph

        self.coil_status = QLabel("PASS")
        self.coil_status.setAlignment(Qt.AlignCenter)
        self.coil_status.setStyleSheet(
            "background: green; color: white; padding: 6px;"
        )

        outputs_layout.addRow("Status:", self.coil_status)

        outputs.setLayout(outputs_layout)

        top.addWidget(inputs)
        top.addWidget(outputs)

        layout.addLayout(top)

        self.coil_canvas = MplCanvas()
        layout.addWidget(self.coil_canvas)

        return tab

    def create_rod_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        top = QHBoxLayout()

        inputs = QGroupBox("Inputs")
        inputs_layout = QFormLayout()

        self.rod_turns = QSpinBox()
        self.rod_turns.setRange(1, 10000)

        self.rod_current = QDoubleSpinBox()
        self.rod_current.setRange(0, 20)

        self.core_length = QDoubleSpinBox()
        self.core_length.setRange(0, 1)

        self.mu_r = QDoubleSpinBox()
        self.mu_r.setRange(1, 100000)

        inputs_layout.addRow("Turns:", self.rod_turns)
        inputs_layout.addRow("Current (A):", self.rod_current)
        inputs_layout.addRow("Core Length (m):", self.core_length)
        inputs_layout.addRow("Relative Permeability:", self.mu_r)

        inputs.setLayout(inputs_layout)

        outputs = QGroupBox("Outputs")
        outputs_layout = QFormLayout()

        outputs_layout.addRow("Moment:", QLabel("--"))
        outputs_layout.addRow("Torque:", QLabel("--"))
        outputs_layout.addRow("Mass:", QLabel("--"))
        outputs_layout.addRow("Power:", QLabel("--"))

        self.rod_status = QLabel("PASS")
        self.rod_status.setAlignment(Qt.AlignCenter)
        self.rod_status.setStyleSheet(
            "background: green; color: white; padding: 6px;"
        )

        outputs_layout.addRow("Status:", self.rod_status)

        outputs.setLayout(outputs_layout)

        top.addWidget(inputs)
        top.addWidget(outputs)

        layout.addLayout(top)

        self.rod_canvas = MplCanvas()
        layout.addWidget(self.rod_canvas)

        return tab

    def create_wheel_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        top = QHBoxLayout()

        inputs = QGroupBox("Inputs")
        inputs_layout = QFormLayout()

        self.wheel_radius = QDoubleSpinBox()
        self.wheel_radius.setRange(0, 1)

        self.wheel_mass = QDoubleSpinBox()
        self.wheel_mass.setRange(0, 20)

        self.max_rpm = QSpinBox()
        self.max_rpm.setRange(0, 50000)

        self.slew_angle = QDoubleSpinBox()
        self.slew_angle.setRange(0, 360)

        self.slew_time = QDoubleSpinBox()
        self.slew_time.setRange(0.1, 10000)

        inputs_layout.addRow("Wheel Radius (m):", self.wheel_radius)
        inputs_layout.addRow("Wheel Mass (kg):", self.wheel_mass)
        inputs_layout.addRow("Max RPM:", self.max_rpm)
        inputs_layout.addRow("Slew Angle (deg):", self.slew_angle)
        inputs_layout.addRow("Slew Time (s):", self.slew_time)

        inputs.setLayout(inputs_layout)

        outputs = QGroupBox("Outputs")
        outputs_layout = QFormLayout()

        outputs_layout.addRow("Wheel Inertia:", QLabel("--"))
        outputs_layout.addRow("Stored Momentum:", QLabel("--"))
        outputs_layout.addRow("Available Torque:", QLabel("--"))
        outputs_layout.addRow("Required Torque:", QLabel("--"))
        outputs_layout.addRow("Margin:", QLabel("--"))

        self.wheel_status = QLabel("PASS")
        self.wheel_status.setAlignment(Qt.AlignCenter)
        self.wheel_status.setStyleSheet(
            "background: green; color: white; padding: 6px;"
        )

        outputs_layout.addRow("Status:", self.wheel_status)

        outputs.setLayout(outputs_layout)

        top.addWidget(inputs)
        top.addWidget(outputs)

        layout.addLayout(top)

        self.wheel_canvas = MplCanvas()
        layout.addWidget(self.wheel_canvas)

        return tab


if __name__ == "__main__":
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()
