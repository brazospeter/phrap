from .modules.units import *

temperature = c(69)
ambient_pressure = 0.99 * atm

card_str = """
        fuel C3.85H4.85N0.43(S)  C 3.85   H 4.85   N 0.43     wt%=100
        h,cal=-14.96894578     t(k)=""" + str(temperature + 273.15) + """  rho.g/cc=1.07
        """