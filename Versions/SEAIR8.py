import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# SEAIR Model function
def run_seair_model(params, initial_conditions, t_max):
    # Initial conditions
    S, E, A, I, Ri, Ra, Is, D, Va, Im = [initial_conditions[key] for key in initial_conditions]
    
    # Arrays to store results
    results = {"time": np.arange(t_max), "S": [], "E": [], "A": [], "I": [], "Ri": [], "Ra": [], "Is": [], "D": [], "Va": []}
    
    # Run simulation for t_max days
    for t in range(t_max):
        # Get parameters
        betaI, betaA, aE, iE, gammaI, gammaA, zigma, p_mild, p_severe, p_fatal = intervention_equations(S, E, A, I, t)
        
        # SEAIR differential equations (simplified)
        dSdt, dEdt, dIdt, dAdt, dRidt, dRadt, dIsdt, dDdt, dVadt = seair_model(S, E, A, I, Ri, Ra, Is, D, Va, Im, t, betaI, betaA, gammaI, gammaA, zigma, p_mild, p_severe, p_fatal)

        # Update values
        S += dSdt
        E += dEdt
        A += dAdt
        I += dIdt
        Ri += dRidt
        Ra += dRadt
        Is += dIsdt
        D += dDdt
        Va += dVadt
        
        # Store the results at each time step
        results["S"].append(S)
        results["E"].append(E)
        results["A"].append(A)
        results["I"].append(I)
        results["Ri"].append(Ri)
        results["Ra"].append(Ra)
        results["Is"].append(Is)
        results["D"].append(D)
        results["Va"].append(Va)

    return results

def intervention_equations(S, E, A, I, t):
    # Placeholder intervention effect (no interventions)
    betaI = RZero/2.9 #TI
    betaA = (RZero*0.35)/2.9 #TA
    aE = zigma*0.5
    iE = zigma*0.5
    gammaI = 0.2 #1/time of illness symptomatic
    gammaA = 0.1 #1/time of illness asymptomatic
    zigma = 5.2/3.6 # 1/time of common T_incubtion
    p_mild = 14-2.9 # recovery mild - time of total ill 
    p_severe = 0.2 # bimatihaii ke bastary mishan bimarestan
    p_fatal = 0.05
    return betaI, betaA, aE, iE, gammaI, gammaA, zigma, p_mild, p_severe, p_fatal

def seair_model(S, E, A, I, Ri, Ra, Is, D, Va, Im, t, betaI, betaA, gammaI, gammaA, zigma, p_mild, p_severe, p_fatal):
    # SEAIR differential equations (simplified version)
    dSdt = -betaI * S * I - betaA * A * S
    dEdt = betaI * S * I + betaA * A * S - zigma * E
    dIdt = zigma * E - gammaI * I
    dAdt = zigma * E - gammaA * A
    dRidt = gammaI * I - Ri
    dRadt = gammaA * A - Ra
    dIsdt = p_severe * gammaI * I - Is
    dDdt = p_fatal * gammaI * I - D
    dVadt = 0  # Vaccination is not modeled here for simplicity
    
    return dSdt, dEdt, dIdt, dAdt, dRidt, dRadt, dIsdt, dDdt, dVadt

def update_model():
    # Update parameters from sliders/entries
    for param in parameters:
        parameters[param] = param_sliders[param].get()

    # Update initial conditions
    for ic in initial_conditions:
        initial_conditions[ic] = float(ic_entries[ic].get())

    # Update total population
    N = float(total_population_entry.get())
    
    # Update t_max based on the slider value
    t_max = int(days_slider.get())
    
    # Run the model and plot in a new window
    results = run_seair_model(parameters, initial_conditions, t_max)
    create_new_window_and_plot(results)

def create_new_window_and_plot(results):
    # Create a new top-level window
    new_window = tk.Toplevel(root)
    new_window.title("SEAIR Model Plot")

    # Create a figure and axis for the plot
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot the results for each compartment
    ax.plot(results["time"], results["S"], label="Susceptible", color="blue")
    ax.plot(results["time"], results["E"], label="Exposed", color="orange")
    ax.plot(results["time"], results["A"], label="Asymptomatic", color="green")
    ax.plot(results["time"], results["I"], label="Infected", color="red")
    ax.plot(results["time"], results["Ri"], label="Recovered Mild", color="purple")
    ax.plot(results["time"], results["Ra"], label="Recovered Asymptomatic", color="cyan")
    ax.plot(results["time"], results["Is"], label="Severe Cases", color="brown")
    ax.plot(results["time"], results["D"], label="Deaths", color="black")
    ax.plot(results["time"], results["Va"], label="Vaccinated", color="magenta")

    # Set labels and title
    ax.set_xlabel("Time (Days)")
    ax.set_ylabel("Population")
    ax.set_title("SEAIR Model Simulation")

    # Show legend
    ax.legend()

    # Embed the plot in the new Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=new_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Define initial parameters and conditions
parameters = {
    "betta": 0.85,
    "epsilon": 0.50,
    "X": 0.75,
    "alpha": 0.52,
    "gamma": 0.40,
    "zetta": 0.03,
    "omega": 0.67,
    "delta": 0.018,
    "D_vaccin_rate": 0.01,
    "D_vaccin_effect": 70,
    "tetta": 0.02,
    "meu": 0.90,
    "etta": 0.1,
    "RZero": 2.5,  # Basic reproduction number
}

# Initial conditions for the simulation
initial_conditions = {
    "S0": 9000,
    "E0": 10000,
    "A0": 20000,
    "I0": 9000,
    "Ri0": 0,
    "Ra0": 0,
    "Is0": 0,
    "D0": 0,
    "Va0": 0,
    "Im0": 0
}

# Create Tkinter GUI
root = tk.Tk()
root.title("SEAIR Model Simulation")

# Create a canvas and a vertical scrollbar
canvas_frame = ttk.Frame(root)
canvas_frame.grid(row=0, column=0, padx=10, pady=10)

canvas = tk.Canvas(canvas_frame)
scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.config(yscrollcommand=scrollbar.set)

canvas.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")

# Parameter sliders and inputs
param_sliders = {}
for idx, (param, value) in enumerate(parameters.items()):
    label = ttk.Label(scrollable_frame, text=param)
    label.grid(row=idx, column=0, padx=10, pady=5)
    
    slider = tk.Scale(scrollable_frame, from_=0, to=5, orient="horizontal", resolution=0.01)
    slider.set(value)
    slider.grid(row=idx, column=1, padx=10, pady=5)
    param_sliders[param] = slider

# Initial conditions input fields
ic_entries = {}
for idx, (ic, value) in enumerate(initial_conditions.items()):
    label = ttk.Label(scrollable_frame, text=ic)
    label.grid(row=idx + len(parameters), column=0, padx=10, pady=5)
    
    entry = ttk.Entry(scrollable_frame)
    entry.grid(row=idx + len(parameters), column=1, padx=10, pady=5)
    entry.insert(0, value)
    ic_entries[ic] = entry

# Total population input field
total_population_entry = ttk.Entry(scrollable_frame)
total_population_entry.grid(row=len(parameters) + len(initial_conditions), column=0, padx=10, pady=5)
total_population_entry.insert(0, 10000)  # Default population size

# Simulation time slider
days_slider = tk.Scale(scrollable_frame, from_=1, to=200, orient="horizontal")
days_slider.set(100)
days_slider.grid(row=len(parameters) + len(initial_conditions) + 1, column=1, padx=10, pady=5)

# Run button
run_button = ttk.Button(scrollable_frame, text="Run Simulation", command=update_model)
run_button.grid(row=len(parameters) + len(initial_conditions) + 2, column=1, padx=10, pady=10)

# Start the Tkinter main loop
root.mainloop()
