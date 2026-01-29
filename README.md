# Auto CE Amplifier Designer (Python)

## Overview

This project is a **Python-based automatic design system for common-emitter (CE) BJT amplifiers**. Given an input voltage, supply voltage, and optional target gain, the system:

1. **Calculates a suitable resistor network** (`R1`, `R2`, `RC`, `RE`) to bias the BJT in its **linear active region**.  
2. **Iteratively adjusts the component values** to meet design constraints (output swing, gain, and Q-point).  
3. **Simulates node voltages** of the circuit using a built-in **Modified Nodal Analysis (MNA)** solver.  
4. **Generates a SPICE netlist** compatible with Proteus or other SPICE simulators for further simulation or schematic generation.  

All of this is done **without requiring external circuit simulators**, making it a **standalone Python-based amplifier design tool**.

---

## What’s New / Unique

- **Automatic parameter selection:** Iteratively chooses resistor values to achieve the desired gain while keeping the transistor in the active region.  
- **Integrated DC simulation:** Uses a **custom MNA solver** to calculate node voltages for verification.  
- **SPICE netlist generation:** Automatically produces a **ready-to-run SPICE file**.  
- **Single-script self-contained solution:** Runs entirely in Python, requiring only **NumPy**.  
- **Adaptive gain control:** Target gain can be specified, or the system maximizes gain automatically within safe operating limits.

---

## Methods Used

### 1. BJT DC Operating Point Analysis

- Uses **Thevenin approximation** to calculate base voltage (`VB`) and base current (`IB`).  
- Calculates collector current (`IC`) and emitter voltage (`VE`) using standard BJT relations.  
- Determines transistor Q-point (`VCE`, `IC`) to ensure it remains in the **active region**.

### 2. Iterative Design Algorithm

- Starts with initial resistor guesses for `R1`, `R2`, `RC`, `RE`.  
- Iteratively adjusts resistors to satisfy:  
  - Transistor active region constraint  
  - Output swing limit (`Vout_peak < VCC - VE - margin`)  
  - Target voltage gain (if specified)  
  - Base voltage constraints  

- Converges to a solution that balances gain, biasing, and output swing.

### 3. Voltage Gain Calculation

- Small-signal gain estimated A_v = \frac{R_C}{R_E + r_e}

where \( r_e = \frac{0.026}{I_C} \) (thermal voltage approximation).  

### 4. Modified Nodal Analysis (MNA) Solver

- Constructs the **G-matrix** and **I-vector** for the circuit.  
- Stamps resistors and voltage sources into the MNA matrix.  
- Solves for **node voltages**, including base, collector, and emitter nodes.

### 5. SPICE Netlist Generation

- Generates a `.cir` file with:  
  - Supply voltage (`VCC`)  
  - Biasing resistors (`R1`, `R2`)  
  - Collector and emitter resistors (`RC`, `RE`)  
  - BJT model  
- Compatible with **Proteus SPICE** or any standard SPICE simulator.  
- Ready for **simulation or schematic generation** without manual editing.

---

## Getting Started

### Prerequisites

- Python 3.8+  
- NumPy

Install dependencies:

```bash
pip install numpy
```

## Clone the Repository

You can clone this repository to your local machine using Git:

```bash
git clone https://github.com/CharithaRanasinghe/auto-ce-amplifier-designer.git
cd auto-ce-amplifier-designer
