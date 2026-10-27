import numpy as np
import matplotlib.pyplot as plt

from rocketcea.cea_obj import CEA_Obj, add_new_fuel


# ============================================================
# CUSTOM ABS FUEL CARD
# ============================================================

ABS_CARD = """
fuel C3.85H4.85N0.43(S)  C 3.85  H 4.85  N 0.43  wt%=100
h,cal=-14.96894578  t(k)=298.15  rho.g/cc=1.07
"""

add_new_fuel("ABS_CUSTOM", ABS_CARD)


# ============================================================
# SETTINGS
# ============================================================

# Constant oxidizer-to-fuel ratio
OF = 7.0

# Chamber pressure range, psia
PC_MIN = 100.0
PC_MAX = 1000.0
PC_POINTS = 200

PRESSURES = np.linspace(
    PC_MIN,
    PC_MAX,
    PC_POINTS
)


# ============================================================
# CREATE CEA OBJECT
# ============================================================

cea = CEA_Obj(
    oxName="N2O",
    fuelName="ABS_CUSTOM"
)


# ============================================================
# CALCULATE CHAMBER DENSITY
# ============================================================

densities = []

for Pc in PRESSURES:

    try:

        rho_chamber, rho_throat, rho_exit = cea.get_Densities(
            Pc=Pc,
            MR=OF
        )

        densities.append(rho_chamber)

    except Exception as e:

        print(f"Pc = {Pc:.1f} psi failed: {e}")
        densities.append(np.nan)


# ============================================================
# CONVERT lbm/ft³ → kg/m³
# ============================================================

densities = np.array(densities)

densities *= 16.0184634


# ============================================================
# PLOT
# ============================================================

plt.figure(figsize=(9, 6))

plt.plot(
    PRESSURES,
    densities,
    linewidth=2
)

plt.xlabel("Chamber Pressure (psia)")
plt.ylabel("Chamber Density (kg/m³)")

plt.title(
    f"ABS + N₂O Chamber Density vs Pressure\n"
    f"O/F = {OF}"
)

plt.grid(True, alpha=0.3)

plt.tight_layout()

plt.show()