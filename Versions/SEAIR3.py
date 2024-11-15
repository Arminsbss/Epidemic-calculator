import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo

# پارامترهای مدل SEAIR (مقادیر پیش‌فرض)
parameters = {
    "betta": 0.85,
    "epsilon": 0.50,
    "X": 0.75,
    "alpha": 0.52,
    "gamma": 0.40,
    "zetta": 0.03,
    "omega": 0.67,
    "delta": 0.018,

# Vaccination Parameters
    "D_vaccin_rate" : 0.01,  # Default vaccination rate, user-defined
    "D_vaccin_effect" : 70,  # Default vaccination effect percentage, user-defined (0 to 100)
    "tetta": 0.02,
    "meu": 0.90,
    "neu": 0.0001,
    "etta": 0.1
}

# شرایط اولیه (مقادیر پیش‌فرض)
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

def update_parameters():
    for param in parameters:
        parameters[param] = param_sliders[param].get()
    run_and_plot_model()

def update_initial_conditions():
    for ic in initial_conditions:
        initial_conditions[ic] = float(ic_entries[ic].get())
    run_and_plot_model()

def seair_model(S, E, A, I, Ri, Ra, Is, D, Va, Im, t):
    lambda_ = parameters["betta"] * (I + parameters["epsilon"] * A + parameters["X"] * Is) / N
    dSdt = -lambda_ * S + parameters["neu"] * N - parameters["neu"] * S * Va
    dEdt = lambda_ * S - parameters["alpha"] * parameters["omega"] * E - parameters["alpha"] * (1 - parameters["omega"]) * E
    dAdt = parameters["alpha"] * (1 - parameters["omega"]) * E - parameters["gamma"] * A
    dIdt = parameters["alpha"] * parameters["omega"] * E - (parameters["delta"] + parameters["tetta"]) * I
    dRidt = parameters["gamma"] * (1 - parameters["zetta"]) * I - parameters["etta"] * Ri
    dRadt = parameters["gamma"] * (1 - parameters["zetta"]) * A
    dIsdt = parameters["tetta"] * I
    dDdt = parameters["delta"] * I
    dVadt = parameters["D_vaccin_rate"] * S
    dImdt = parameters["etta"] * Ri
    return dSdt, dEdt, dAdt, dIdt, dRidt, dRadt, dIsdt, dDdt, dVadt, dImdt

def euler_method(S0, E0, A0, I0, Ri0, Ra0, Is0, D0, Va0, Im0, t, dt):
    S, E, A, I, Ri, Ra, Is, D, Va, Im = [S0], [E0], [A0], [I0], [Ri0], [Ra0], [Is0], [D0], [Va0], [Im0]
    for i in range(1, len(t)):
        dSdt, dEdt, dAdt, dIdt, dRidt, dRadt, dIsdt, dDdt, dVadt, dImdt = seair_model(S[-1], E[-1], A[-1], I[-1], Ri[-1], Ra[-1], Is[-1], D[-1], Va[-1], Im[-1], t[i])
        S.append(S[-1] + dSdt * dt)
        E.append(E[-1] + dEdt * dt)
        A.append(A[-1] + dAdt * dt)
        I.append(I[-1] + dIdt * dt)
        Ri.append(Ri[-1] + dRidt * dt)
        Ra.append(Ra[-1] + dRadt * dt)
        Is.append(Is[-1] + dIsdt * dt)
        D.append(D[-1] + dDdt * dt)
        Va.append(Va[-1] + dVadt * dt)
        Im.append(Im[-1] + dImdt * dt)
    return np.array(S), np.array(E), np.array(A), np.array(I), np.array(Ri), np.array(Ra), np.array(Is), np.array(D), np.array(Va), np.array(Im)

def run_and_plot_model():
    global S, E, A, I, Ri, Ra, Is, D, Va, Im, N, t
    N = sum(initial_conditions.values())
    t_max = 80
    dt = 1
    t = np.arange(0, t_max, dt)
    
    S, E, A, I, Ri, Ra, Is, D, Va, Im = euler_method(initial_conditions["S0"], initial_conditions["E0"], initial_conditions["A0"], initial_conditions["I0"], initial_conditions["Ri0"], initial_conditions["Ra0"], initial_conditions["Is0"], initial_conditions["D0"], initial_conditions["Va0"], initial_conditions["Im0"], t, dt)
    plt.figure(figsize=(10, 6))
    plt.plot(t, S, label='Susceptible')
    plt.plot(t, E, label='Exposed')
    plt.plot(t, A, label='Asymptomatic')
    plt.plot(t, I, label='Infectious')
    plt.plot(t, Ri, label='Recovered (Symptomatic)')
    plt.plot(t, Ra, label='Recovered (Asymptomatic)')
    plt.plot(t, Is, label='Isolated')
    plt.plot(t, D, label='Deceased')
    plt.plot(t, Va, label='Vaccinated')
    plt.plot(t, Im, label='Immune')
    plt.xlabel('Time (days)')
    plt.ylabel('Population')
    plt.title('SEAIR Model for H2N2 Influenza')
    plt.legend()
    plt.grid(True)
    plt.show()

def export_to_excel():
    data = {
        "Time (days)": t,
        "Susceptible": S,
        "Exposed": E,
        "Asymptomatic": A,
        "Infectious": I,
        "Recovered (Symptomatic)": Ri,
        "Recovered (Asymptomatic)": Ra,
        "Isolated": Is,
        "Deceased": D,
        "Vaccinated": Va,
        "Immune": Im
    }
    df = pd.DataFrame(data)
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        wb = Workbook()
        ws = wb.active

        for r in dataframe_to_rows(df, index=False, header=True):
            ws.append(r)

        tab = Table(displayName="SEAIRData", ref=f"A1:K{len(df)+1}")

        style = TableStyleInfo(
            name="TableStyleMedium9",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=True
        )
        tab.tableStyleInfo = style
        ws.add_table(tab)

        wb.save(file_path)
        messagebox.showinfo("ذخیره شد", "داده‌ها با موفقیت ذخیره شدند.")

root = tk.Tk()
root.title("SEAIR مدل")
notebook = ttk.Notebook(root)
notebook.pack(pady=10, ipadx=55, ipady= 10 , expand=True)

# Minimum and maximum values for each parameter
parameter_ranges = {
    "betta": (0.0, 0.7),    # Transmission rate
    "epsilon": (0.0, 0.8),  # Relative infectiousness of asymptomatic individuals
    "X": (0.0, 0.5),        # Relative infectiousness of isolated individuals
    "alpha": (0.0, 0.5),    # Rate at which exposed individuals become infectious
    "gamma": (0.0, 0.5),    # Recovery rate
    "zetta": (0.0, 0.05),   # Proportion of symptomatic cases
    "omega": (0.0, 0.8),    # Proportion of cases that become symptomatic
    "delta": (0.0, 0.05),   # Disease-induced death rate
    "tetta": (0.0, 0.2),    # Rate of isolation for symptomatic individuals
    "meu": (0.0, 0.95),     # Vaccine efficacy
    "neu": (0.0, 0.005),    # Vaccination rate
    "etta": (0.0, 0.01),     # Rate of loss of immunity
    "D_vaccin_rate" : (0,0.5),  # Default vaccination rate, user-defined
    "D_vaccin_effect" : (0,95)  # Default vaccination effect percentage, user-defined (0 to 100)
}

param_frame = ttk.Frame(notebook)
param_frame.pack(fill='both', expand=True)
param_sliders = {}
for idx, (param, value) in enumerate(parameters.items()):
    label = ttk.Label(param_frame, text=param)
    label.grid(row=idx, column=0, padx=10, pady=5)
    
    min_val, max_val = parameter_ranges[param]
    slider = tk.Scale(param_frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL, resolution=0.01)
    slider.set(value)
   
    slider.grid(row=idx, column=1, padx=10, pady=5)
    param_sliders[param] = slider

param_update_button = ttk.Button(param_frame, text="بروزرسانی و نمایش نمودار", command=update_parameters)
param_update_button.grid(row=len(parameters), column=0, columnspan=2, pady=10)

init_cond_frame = ttk.Frame(notebook)
init_cond_frame.pack(fill='both', expand=True)
ic_entries = {}
for idx, (ic, value) in enumerate(initial_conditions.items()):
    label = ttk.Label(init_cond_frame, text=ic)
    label.grid(row=idx, column=0, padx=10, pady=5)
    entry = ttk.Entry(init_cond_frame)
    entry.grid(row=idx, column=1, padx=10, pady=5)
    entry.insert(0, value)
    ic_entries[ic] = entry

ic_update_button = ttk.Button(init_cond_frame, text="بروزرسانی و نمایش نمودار", command=update_initial_conditions)
ic_update_button.grid(row=len(initial_conditions), column=0, columnspan=2, pady=10)

output_frame = ttk.Frame(notebook)
output_frame.pack(fill='both', expand=True)
output_button = ttk.Button(output_frame, text="خروجی به اکسل", command=export_to_excel)
output_button.pack(pady=10)

notebook.add(param_frame, text="پارامترها")
notebook.add(init_cond_frame, text="شرایط اولیه")
notebook.add(output_frame, text="خروجی")

run_and_plot_model()

root.mainloop()
