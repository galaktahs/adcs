# calc stands for calculator
# everyone knows that
import math

g_EarthRadius = 6378
g_Mu = 398000
g_B0 = 3.12*10**-5

def calcOrbit(altitude, inclination):
        """
        Calculate the environment for the given orbit
        """
        period = math.tau*math.sqrt((altitude+g_EarthRadius)**3/g_Mu)
        velocity = math.tau*(altitude+g_EarthRadius)/period
        if 400 >= altitude:
            density = (8.25711*10**-9)*0.9811**altitude
        else:
            density = (3.5*10**-7)*0.97188**altitude
        minMag = g_B0*(g_EarthRadius/(altitude+g_EarthRadius))**3
        if 90 >= inclination:
            maxMag = minMag + minMag*(math.sqrt(3)-1)*(inclination/90)
        else:
            maxMag = minMag + (minMag*(math.sqrt(3)-1))*(180-inclination)/90

        return (period, velocity, density, minMag, maxMag)
