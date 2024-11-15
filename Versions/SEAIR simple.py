import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Parameters
RZero = 2.5
D_infectious = 5
D_asymptomatic = 7
D_incubation = 14
D_recovery_mild = 14
D_hospital_lag = 7
D_recovery_severe = 21
D_death = 10
D_natural_death = 1 / (70 * 365)
P_SEVERE = 0.15
CFR = 0.02
InterventionTime = 20
duration = 30
InterventionAmt = 0.7
D_vaccin_rate = 0
D_vaccin_effect = 0
D_incoming_popul = 0
D_born_popul = 0
day_of_vaccine = 50

# Initial conditions
initial_conditions = {
    "S": 7000, "E": 1, "I": 0, "A": 0, "Mild": 0, "Severe": 0,
    "Severe_H": 0, "Fatal": 0, "R_Mild": 0, "R_Severe": 0, "R_Fatal": 0
}
total_population = sum(initial_conditions.values())
initial_values = list(initial_conditions.values())

# Differential equations
def model(t, y):
    S, E, I, A, Mild, Severe, Severe_H, Fatal, R_Mild, R_Severe, R_Fatal = y

    # Dynamic beta values
    if InterventionTime <= t < InterventionTime + duration:
        betaI = (InterventionAmt) * RZero / D_infectious
        betaA = (InterventionAmt) * (0.35 * RZero) / D_asymptomatic
    elif t >= InterventionTime + duration:
        betaI = 0.5 * RZero / D_infectious
        betaA = 0.5 * (0.35 * RZero) / D_asymptomatic
    else:
        betaI = RZero / D_infectious
        betaA = (0.35 * RZero) / D_asymptomatic

    # Other parameters
    zigma = 1 / D_incubation
    aE = zigma * 0.5
    iE = zigma * 0.5
    gammaI = 1 / D_infectious
    gammaA = 1 / D_asymptomatic
    p_mild = 1 - P_SEVERE - CFR
    p_severe = P_SEVERE
    p_fatal = CFR

    # Equations
    dS = -betaI * I * S - betaA * A * S - D_natural_death * S
    if t >= day_of_vaccine:
        dS -= S * D_vaccin_rate * (D_vaccin_effect / 100)
    dS += D_incoming_popul * S + D_born_popul * S

    dE = betaI * I * S + betaA * A * S - zigma * E - D_natural_death * E
    dI = iE * E - gammaI * I - D_natural_death * I
    dA = aE * E - gammaA * A - D_natural_death * A
    dMild = p_mild * gammaI * I + p_mild * gammaA * A - (1 / D_recovery_mild) * Mild - D_natural_death * Mild
    dSevere = p_severe * gammaI * I + p_severe * gammaA * A - (1 / D_hospital_lag) * Severe - D_natural_death * Severe
    dSevere_H = (1 / D_hospital_lag) * Severe - (1 / D_recovery_severe) * Severe_H - D_natural_death * Severe_H
    dFatal = p_fatal * gammaI * I + p_fatal * gammaA * A - D_natural_death * Fatal  # Only increase Fatality
    dR_Mild = (1 / D_recovery_mild) * Mild
    dR_Severe = (1 / D_recovery_severe) * Severe_H
    dR_Fatal = (1 / D_death) * Fatal

    return [dS, dE, dI, dA, dMild, dSevere, dSevere_H, dFatal, dR_Mild, dR_Severe, dR_Fatal]

# Time range
t_span = (0, 100)
t_eval = np.linspace(*t_span, 100)

# Solve the model
solution = solve_ivp(model, t_span, initial_values, t_eval=t_eval, method='LSODA')

# Extract results
results = solution.y

# Plot results
compartments_to_plot = ["E", "A", "I", "Severe_H", "Fatal"]
compartment_indices = [list(initial_conditions.keys()).index(c) for c in compartments_to_plot]

plt.figure(figsize=(12, 8))
for i, compartment in enumerate(compartments_to_plot):
    plt.plot(t_eval, results[compartment_indices[i]], label=compartment)
plt.xlabel("Time (days)")
plt.ylabel("Population")
plt.title("Selected SEAIR Model Compartments")
plt.legend()
plt.grid()
plt.show()
