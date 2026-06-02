class Default:
    def __init__(self):
        self.threeU = {
            "x" : 100,
            "y" : 100,
            "z" : 340,
            "mass" : 4,
            "Ixx" : 0.040,
            "Iyy" : 0.040,
            "Izz" : 0.007,
            "max_mass" : 0.3,
            "max_peak_power" : 3,
            "max_avg_power" : 1.5 
        }
        self.sixU = {
            "x" : 100,
            "y" : 226,
            "z" : 340,
            "mass" : 8,
            "Ixx" : 0.090,
            "Iyy" : 0.090,
            "Izz" : 0.020,
            "max_mass" : 0.6,
            "max_peak_power" : 6,
            "max_avg_power" : 3
        }
        self.twelveU = {
            "x" : 240,
            "y" : 226,
            "z" : 340,
            "mass" : 12,
            "Ixx" : 0.160,
            "Iyy" : 0.160,
            "Izz" : 0.080,
            "max_mass" : 1.2,
            "max_peak_power" : 15,
            "max_avg_power" : 8
        }
        self.coil = {
            "m_target" : 1,
            "v_supply" : 3.3,
            "d_w" : 0.2,
            "shape" : "Square",
            "n" : 1000,
            "material" : "Copper"
        }
        self.rod = {
            "m_target" : 1,
            "v_supply" : 3.3,
            "d_w" : 0.15,
            "d_r" : 8,
            "l_r" : 60,
            "material" : "Mu-metal",
            "layers" : 1
        }
        self.wheel = {
            "theta" : 30,
            "t_slew" : 90,
            "axis" : "x",
            "shape" : "Solid disk",
            "r_w" : 30,
            "r_i" : 20,
            "t_w" : 10,
            "material" : "Aluminium",
            "omega_max" : 6000,
            "t_desat" : 1
        }
default = Default()