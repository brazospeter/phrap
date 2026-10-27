from phrap.modules.ccsv import load
from phrap.modules.curve import Curve

file1_name = "new_horizon_v1.3.6.csv"
file2_name = "new_horizon_v1.3.4.csv"

switch_file_names = False

if switch_file_names:
    file1_name, file2_name = file2_name, file1_name

load(file1_name).cplot("Time (s)", "Thrust (N)", load(file2_name))
#load(file1_name).cplot("Time (s)", "Helical Ratio", load(file2_name))
#load(file1_name).cplot("Time (s)", "Radial Blowing Amplification", load(file2_name))
load(file1_name).plot2("Time (s)", "Ambient Pressure (atm)", "Exit Pressure (atm)")
#load(file1_name).plot2("Time (s)", "Pressure Drop (PSI)", "Critical Pressure (PSI)")
#load(file1_name).plot2("Time (s)", "Tank Pressure (PSI)", "Chamber Pressure (PSI)")
#load(file1_name).plot2("Time (s)", "Skin Friction Amplification","Radial Blowing Amplification")
#load(file1_name).plot("Time (s)", "MFR Injector (kg/s)")
load(file1_name).plot("Time (s)", "O/F Ratio")
load(file1_name).plot("Time (s)", "Chamber Pressure (PSI)")