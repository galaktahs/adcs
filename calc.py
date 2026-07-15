# calc stands for calculator
# everyone knows that
import math
from properties import Default

g_EarthRadius = 6378
g_Mu = 398000
g_B0 = 3.12*10**-5
g_coilMat = {
    "Copper":{"density":8935, "resistivity":16.78*10**-9},
    "Aluminium":{"density":2699, "resistivity":26.5*10**-9}

}
g_rodMat = {
    "Mu-metal":{"density":8747, "mu_r" = 20000}, # CarTech HyMu 800
    "Permalloy":{"density":8250, "mu_r" = 8000}, #ATI Moly Permalloy
    "Ferrite":{"density":5000, "mu_r" = 1000}, #Eclipse magnetic ferrite magnets typ. value
}
def calcOrbit(altitude, inclination):
    """
    Calculate the environment for the given orbit
    """
    period = math.tau*math.sqrt((altitude+g_EarthRadius)**3/g_Mu)
    velocity = math.tau*(altitude+g_EarthRadius)/period
    angVelocity = math.tau/period
    if 400 >= altitude:
        density = (8.25711*10**-9)*0.9811**altitude
    else:
        density = (3.5*10**-7)*0.97188**altitude
    minMag = g_B0*((g_EarthRadius/(altitude+g_EarthRadius))**3)
    if 90 >= inclination:
        maxMag = minMag + minMag*(math.sqrt(3)-1)*(inclination/90)
    else:
        maxMag = minMag + (minMag*(math.sqrt(3)-1))*(180-inclination)/90

    return (period, velocity, density, minMag, maxMag, angVelocity)

def calcDisturbance(velocity, angVelocity, density, maxMag, form):
    """
    Calculate the disturbances for a given situation
    """
    default = Default()
    match (form):
        case "3U":
            satParams = default.threeU
            satParams["m_res"] = 0.01 #TODO: Should be user editable
        case "6U":
            satParams = default.sixU
            satParams["m_res"] = 0.05
        case "12U":
            satParams = default.twelveU
            satParams["m_res"] = 0.1
    maxAngle = 15
    C_p = 2
    rcp = 0.05 # TODO: Should be user editable
    I_s = 1361
    K = 0.6
    c = 29979458
    
    gg = (3/2)*angVelocity**2*abs(satParams["Izz"]-satParams["Ixx"])*math.sin(2*math.radians(15))
    drag = 1/2*density*(velocity*1000)**2*satParams["x"]/1000*satParams["y"]/1000*2*0.05*satParams["z"]/1000
    srp = (1 + K)*(I_s/c)*(satParams["x"]*satParams["y"]*satParams["z"])/(min(min(satParams["x"], satParams["y"]), satParams["z"])*1000**2)*0.05*satParams["z"]/1000
    mag = satParams["m_res"]*maxMag

    return (gg, drag, srp, mag)

def calcCoil(voltage, diameter, shape, turns, mat, form):
    """
    calculate parameters for a specified coil
    """
    default = Default()
    match (form):
        case "3U":
            satParams = default.threeU
        case "6U":
            satParams = default.sixU
        case "12U":
            satParams = default.twelveU

    match(shape):
        case "Square":
            area = (min(satParams["x"], satParams["y"])/1000)**2
            perimeter = (min(satParams["x"], satParams["y"])/1000)*4
        case "Rectangular":
            area = satParams["x"]/1000 * satParams["y"]/1000
            perimeter = 2*satParams["x"]/1000 + 2*satParams["y"]/1000
        case "Circular":
            area = math.pi*(min(satParams["x"], satParams["y"])/2000)**2
            perimeter = math.pi*(min(satParams["x"], satParams["y"])/1000)
        case _:
            print(shape)
    resistance = g_coilMat[mat]["resistivity"]*(turns*perimeter*4)/(math.pi*diameter**2)
    current = voltage/resistance
    moment = turns*current*area
    power = (voltage**2)/resistance
    mass = turns*perimeter*math.pi*diameter**2*g_coilMat[mat]["density"]/4
    length = turns*perimeter

    return (moment, resistance, current, power, mass, turns, length)


def calcRod(voltage, rodWireDiameter, rodCoreDiameter, rodLength, rodMat, rodLayers)
    """
    calculate parameters for a specific rod
    """

    maxTurns = rodLength/rodWireDiameter
    turns = maxTurns*rodLayers

    resistance = g_coilMat["copper"]["resistivity"]*(turns*rodCoreDiameter*math.pi*4)/(math.pi*rodWireDiameter**2)
    current = voltage/resistance
    power = (voltage**2)/resistance
    rodRadius = rodCoreDiameter/2
    N_d = (4*(math.log(rodLength/rodRadius)-1))/((rodLength/rodRadius)**2-4*math.log(rodLength/rodRadius))
    mu_eff = 1+((g_rodMat[rodMat]["mu_r"]-1)/(1+(g_rodMat[rodMat]["mu_r"]-1)*N_d)
    dipole = math.pi*rodRadius*turns*current*mu_eff


    return (dipole, resistance, current, power, mass, turns, mu_eff, N_d, maxTurns)
