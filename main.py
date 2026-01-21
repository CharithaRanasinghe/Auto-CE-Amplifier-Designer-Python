import numpy as np

class BJT:
    def __init__(self, beta=100, Vbe=0.7, Vce_sat=0.2):
        self.beta = beta
        self.Vbe = Vbe
        self.Vce_sat = Vce_sat

def dc_op(VCC, R1, R2, RC, RE, bjt):
    Vth = VCC * R2 / (R1 + R2)
    Rth = (R1 * R2) / (R1 + R2)
    IB = (Vth - bjt.Vbe) / (Rth + (bjt.beta + 1) * RE)
    IC = bjt.beta * IB
    IE = IC + IB
    VE = IE * RE
    VC = VCC - IC * RC
    VCE = VC - VE
    return {"IB": IB, "IC": IC, "IE": IE, "VC": VC, "VE": VE, "VCE": VCE}

def voltage_gain(RC, RE, IC=None):
    re = 0.026 / IC if IC else 0
    return RC / (RE + re)

def is_active(op, bjt):
    return op["VCE"] > bjt.Vce_sat + 0.1 and op["IC"] > 0

class MNASystem:
    def __init__(self, nodes, vsrc_count):
        self.N = nodes
        self.M = vsrc_count
        self.size = self.N + self.M
        self.G = np.zeros((self.size, self.size))
        self.I = np.zeros(self.size)

    def stamp_resistor(self, n1, n2, R):
        g = 1 / R
        if n1 != 0:
            self.G[n1-1, n1-1] += g
        if n2 != 0:
            self.G[n2-1, n2-1] += g
        if n1 != 0 and n2 != 0:
            self.G[n1-1, n2-1] -= g
            self.G[n2-1, n1-1] -= g

    def stamp_voltage(self, n1, n2, V, index):
        row = self.N + index
        if n1 != 0:
            self.G[row, n1-1] = 1
            self.G[n1-1, row] = 1
        if n2 != 0:
            self.G[row, n2-1] = -1
            self.G[n2-1, row] = -1
        self.I[row] = V

def design_ce_amplifier(Vin_peak, VCC=12, target_gain=None):
    bjt = BJT(beta=100)
    max_possible_gain = (VCC / 2) / Vin_peak
    if target_gain is None or target_gain > max_possible_gain:
        if target_gain:
            print(f"Warning: Target gain too high for Vin and VCC. Reducing to {max_possible_gain:.2f}")
        target_gain = max_possible_gain

    R1, R2 = 10_000, 2_000
    RC, RE = 4_700, 470

    for _ in range(1000):
        op = dc_op(VCC, R1, R2, RC, RE, bjt)
        Av = voltage_gain(RC, RE, op["IC"])
        Vout_peak = Vin_peak * Av

        if not is_active(op, bjt):
            RC += max(50, RC*0.05)
            R2 = max(100, R2 - 50)
            continue

        if Vout_peak > (VCC - op["VE"] - 0.5):
            RE += max(20, RE*0.05)
            continue

        if target_gain and abs(Av - target_gain) > 0.05:
            if Av > target_gain:
                RE += max(10, RE*0.02)
            else:
                RE = max(10, RE - max(10, RE*0.02))
            continue

        VB = VCC * R2 / (R1 + R2)
        if VB > VCC / 2:
            R2 = max(100, R2 - 50)
            continue

        return {"R1": R1, "R2": R2, "RC": RC, "RE": RE, "Av": Av, "Qpoint": op}

    raise Exception("Could not converge. Try different Vin/VCC or initial guesses.")

def simulate_ce(design, VCC):
    nodes = 3
    vsrc_count = 1
    mna = MNASystem(nodes, vsrc_count)

    mna.stamp_resistor(1, 2, design["R1"])
    mna.stamp_resistor(2, 0, design["R2"])
    mna.stamp_resistor(1, 3, design["RC"])
    mna.stamp_resistor(3, 0, design["RE"])
    mna.stamp_voltage(1, 0, VCC, 0)

    x = np.linalg.solve(mna.G, mna.I)
    node_voltages = {f"Node {i+1}": x[i] for i in range(nodes)}
    node_voltages["Vout (Collector)"] = x[2]  # Node3
    return node_voltages

def write_proteus_netlist(design, VCC, filename="ce_amp.cir"):
    with open(filename, "w") as f:
        f.write("* Auto-generated CE Amplifier for Proteus\n")
        f.write(f"VCC 1 0 DC {VCC}\n")
        f.write(f"R1 1 2 {design['R1']}\n")
        f.write(f"R2 2 0 {design['R2']}\n")
        f.write(f"RC 1 3 {design['RC']}\n")
        f.write(f"RE 3 0 {design['RE']}\n")
        f.write("Q1 3 2 0 NPN\n")
        f.write(".model NPN NPN(IS=1e-14 BF=100 VAF=100)\n")
        f.write(".dc VCC 12 12 1\n")
        f.write(".end\n")
    print(f"Netlist written to {filename}")

if __name__ == "__main__":
    Vin = float(input("Enter input peak voltage (V): "))
    VCC = float(input("Enter VCC (V): "))
    target_gain_input = float(input("Enter desired gain (0 for auto): ") or 0)
    target_gain = target_gain_input if target_gain_input > 0 else None

    design = design_ce_amplifier(Vin, VCC, target_gain)
    print("\n--- Designed CE Amplifier ---")
    for k, v in design.items():
        if k != "Qpoint":
            print(f"{k}: {v}")
    print("Q-point:", {k: f"{v:.3f}" for k, v in design["Qpoint"].items()})

    node_voltages = simulate_ce(design, VCC)
    print("\n--- Node Voltages ---")
    for k, v in node_voltages.items():
        print(f"{k}: {v:.3f} V")

    write_proteus_netlist(design, VCC)
