import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Parameters (same as in your original model)
RZero = 2.5
D_infectious = 5
D_asymptomatic = 7
D_incubation = 14
D_recovery_mild = 14
D_hospital_lag = 7
D_recovery_severe = 21
D_death = 10
P_SEVERE = 0.15
CFR = 0.02
InterventionTime = 20
duration = 30
InterventionAmt = 0.7

# Initial conditions
N = 7000  # total population
I0 = 1  # initial infected
R0 = 0  # initial recovered
E0 = 1  # initial exposed
A0 = 0  # initial asymptomatic
Mild0 = 0
Severe0 = 0
Severe_H0 = 0
Fatal0 = 0
R_Mild0 = 0
R_Severe0 = 0
R_Fatal0 = 0

initial_conditions = [N - I0 - E0, E0, I0, A0, Mild0, Severe0, Severe_H0, Fatal0, R_Mild0, R_Severe0, R_Fatal0]

# Time step and parameters
interpolation_steps = 40
dt = 0.05 / interpolation_steps
steps = 110 * interpolation_steps

# Runge-Kutta 4th order method for integration
def rk4(f, y, t, dt):
    k1 = f(t, y)
    k2 = f(t + dt/2, y + dt*k1/2)
    k3 = f(t + dt/2, y + dt*k2/2)
    k4 = f(t + dt, y + dt*k3)
    return y + dt/6 * (k1 + 2*k2 + 2*k3 + k4)

# SEIR model with complications
def seir_model(t, y):
    S, E, I, A, Mild, Severe, Severe_H, Fatal, R_Mild, R_Severe, R_Fatal = y
    
    # Dynamic beta values for interventions
    if InterventionTime <= t < InterventionTime + duration:
        beta = (InterventionAmt) * RZero / D_infectious
    elif t >= InterventionTime + duration:
        beta = 0.5 * RZero / D_infectious
    else:
        beta = RZero / D_infectious
        
    # Other parameters
    zigma = 1 / D_incubation
    aE = zigma * 0.5
    iE = zigma * 0.5
    gammaI = 1 / D_infectious
    gammaA = 1 / D_asymptomatic
    p_mild = 1 - P_SEVERE - CFR
    p_severe = P_SEVERE
    p_fatal = CFR

    # Differential equations
    dS = -beta * I * S - beta * A * S
    dE = beta * I * S + beta * A * S - zigma * E
    dI = iE * E - gammaI * I
    dA = aE * E - gammaA * A
    dMild = p_mild * gammaI * I + p_mild * gammaA * A - (1 / D_recovery_mild) * Mild
    dSevere = p_severe * gammaI * I + p_severe * gammaA * A - (1 / D_hospital_lag) * Severe
    dSevere_H = (1 / D_hospital_lag) * Severe - (1 / D_recovery_severe) * Severe_H
    dFatal = p_fatal * gammaI * I + p_fatal * gammaA * A
    dR_Mild = (1 / D_recovery_mild) * Mild
    dR_Severe = (1 / D_recovery_severe) * Severe_H
    dR_Fatal = (1 / D_death) * Fatal

    return np.array([dS, dE, dI, dA, dMild, dSevere, dSevere_H, dFatal, dR_Mild, dR_Severe, dR_Fatal])

# Simulation loop
def simulate():
    y = np.array(initial_conditions)
    t = 0
    results = []
    times = []  # To store the time points
    while t < steps * dt:
        results.append(y)
        times.append(t)
        y = rk4(seir_model, y, t, dt)
        t += dt
    
    return np.array(results), np.array(times)

# Running the simulation
results, times = simulate()

# Extract results for plotting
S, E, I, A, Mild, Severe, Severe_H, Fatal, R_Mild, R_Severe, R_Fatal = results.T

# Plot setup
fig, ax = plt.subplots(figsize=(12, 8))

# Initial plot
line_E, = ax.plot([], [], label="Exposed (E)", color='orange')
line_I, = ax.plot([], [], label="Infectious (I)", color='red')
line_Severe_H, = ax.plot([], [], label="Severe (Hospitalized)", color='purple')
line_Fatal, = ax.plot([], [], label="Fatalities (Fatal)", color='black')

ax.set_xlim(0, np.max(times))
ax.set_ylim(0, np.max(S))  # Set initial y-axis limit
ax.set_xlabel("Time (days)")
ax.set_ylabel("Population")
ax.set_title("SEIR Model with RK4 Integration")
ax.legend()
ax.grid(True)

# Animation update function
def update(frame):
    line_E.set_data(times[:frame], E[:frame])
    line_I.set_data(times[:frame], I[:frame])
    line_Severe_H.set_data(times[:frame], Severe_H[:frame])
    line_Fatal.set_data(times[:frame], Fatal[:frame])
    return line_E, line_I, line_Severe_H, line_Fatal

# Creating animation
ani = FuncAnimation(fig, update, frames=len(times), interval=dt*1000, blit=True)

# Show the animation
plt.show()
