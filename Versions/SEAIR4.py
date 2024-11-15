import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo


from matplotlib import rc
from bidi.algorithm import get_display
import arabic_reshaper

import tkinter.font as tkFont




# Default parameters for the SEAIR model
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
    "neu": 0.0001,
    "etta": 0.1
}

# Default initial conditions
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

def update_population():
    total_population = sum(float(ic_entries[ic].get()) for ic in initial_conditions)
    total_population_label.config(text=f"کل جمعیت: {np.round(total_population).astype(int)}")

def update_model():
    # Update parameters
    for param in parameters:
        parameters[param] = param_sliders[param].get()

    # Update initial conditions
    for ic in initial_conditions:
        initial_conditions[ic] = float(ic_entries[ic].get())
    
    # Update population display
    update_population()
    
    # Run the model and plot
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



def reshape_arabic(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

def run_and_plot_model():
    global S, E, A, I, Ri, Ra, Is, D, Va, Im, N, t
    N = sum(initial_conditions.values())
    t_max = 80
    dt = 1
    t = np.arange(0, t_max, dt)
    
    S, E, A, I, Ri, Ra, Is, D, Va, Im = euler_method(
        initial_conditions["S0"], initial_conditions["E0"], initial_conditions["A0"],
        initial_conditions["I0"], initial_conditions["Ri0"], initial_conditions["Ra0"],
        initial_conditions["Is0"], initial_conditions["D0"], initial_conditions["Va0"],
        initial_conditions["Im0"], t, dt)

    # تنظیم فونت فارسی
    rc('font', family='B Nazanin',size=16)  # یا فونت دیگری که از آن استفاده می‌کنید
    plt.figure(figsize=(10, 6))

    plt.plot(t, S, label=reshape_arabic('مستعد'))
    plt.plot(t, E, label=reshape_arabic('در معرض'))
    plt.plot(t, A, label=reshape_arabic('بی‌علامت'))
    plt.plot(t, I, label=reshape_arabic('مبتلا'))
    plt.plot(t, Ri, label=reshape_arabic('بهبودیافته (علامت‌دار)'))
    plt.plot(t, Ra, label=reshape_arabic('بهبودیافته (بی‌علامت)'))
    plt.plot(t, Is, label=reshape_arabic('ایزوله'))
    plt.plot(t, D, label=reshape_arabic('فوت‌شده'))
    plt.plot(t, Va, label=reshape_arabic('واکسینه شده'))
    plt.plot(t, Im, label=reshape_arabic('ایمن'))

    plt.xlabel(reshape_arabic('زمان (روزها)'))
    plt.ylabel(reshape_arabic('جمعیت'))
    plt.title(reshape_arabic('نمودار بیماری مدلسازی شده'))
    plt.legend(loc='best', prop={'size': 10})  # موقعیت و اندازه لیجند
    plt.grid(True)
    
    plt.show()



def export_to_excel():
    # Round the values to the nearest whole number
    rounded_S = np.round(S).astype(int)
    rounded_E = np.round(E).astype(int)
    rounded_A = np.round(A).astype(int)
    rounded_I = np.round(I).astype(int)
    rounded_Ri = np.round(Ri).astype(int)
    rounded_Ra = np.round(Ra).astype(int)
    rounded_Is = np.round(Is).astype(int)
    rounded_D = np.round(D).astype(int)
    rounded_Va = np.round(Va).astype(int)
    rounded_Im = np.round(Im).astype(int)

    data = {
        "Time (days)": t,
        "Susceptible": rounded_S,
        "Exposed": rounded_E,
        "Asymptomatic": rounded_A,
        "Infectious": rounded_I,
        "Recovered (Symptomatic)": rounded_Ri,
        "Recovered (Asymptomatic)": rounded_Ra,
        "Isolated": rounded_Is,
        "Deceased": rounded_D,
        "Vaccinated": rounded_Va,
        "Immune": rounded_Im
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

# تنظیم فونت پیش‌فرض
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(family="B Nazanin", size=12)  # یا هر فونت دیگری که می‌خواهید

# Main Frame
main_frame = ttk.Frame(root)
main_frame.pack(pady=10, ipadx=55, ipady=10, expand=True)

# Parameter Frame
param_frame = ttk.LabelFrame(main_frame, text="بروزرسانی پارامترها")
param_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
param_sliders = {}

# Define two lists for splitting the parameters
first_column_params = ["betta", "epsilon", "X", "alpha", "gamma", "zetta", "omega"]
second_column_params = ["delta", "D_vaccin_rate", "D_vaccin_effect", "tetta", "meu", "neu", "etta"]

# Fill the first column
for idx, param in enumerate(first_column_params):
    value = parameters[param]
    label = ttk.Label(param_frame, text=param)
    label.grid(row=idx, column=0, padx=10, pady=5)
    
    slider = tk.Scale(param_frame, from_=0, to=1, orient=tk.HORIZONTAL, resolution=0.01)
    slider.set(value)
    slider.grid(row=idx, column=1, padx=10, pady=5)
    param_sliders[param] = slider

# Fill the second column
for idx, param in enumerate(second_column_params):
    value = parameters[param]
    label = ttk.Label(param_frame, text=param)
    label.grid(row=idx, column=2, padx=10, pady=5)  # Column index 2 for the second column
    
    slider = tk.Scale(param_frame, from_=0, to=1, orient=tk.HORIZONTAL, resolution=0.01)
    slider.set(value)
    slider.grid(row=idx, column=3, padx=10, pady=5)  # Column index 3 for the second column
    param_sliders[param] = slider

# Initial Conditions Frame
init_cond_frame = ttk.LabelFrame(main_frame, text="بروزرسانی شرایط اولیه")
init_cond_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
ic_entries = {}
for idx, (ic, value) in enumerate(initial_conditions.items()):
    label = ttk.Label(init_cond_frame, text=ic)
    label.grid(row=idx, column=0, padx=10, pady=5)
    entry = ttk.Entry(init_cond_frame)
    entry.grid(row=idx, column=1, padx=10, pady=5)
    entry.insert(0, value)  # Ensure all initial values are shown
    ic_entries[ic] = entry

    # Add trace to update population on change
    entry_var = tk.StringVar(value=value)
    entry.config(textvariable=entry_var)
    entry_var.trace_add("write", lambda *args: update_population())

# Total Population Label
total_population_label = ttk.Label(main_frame, text=f"کل جمعیت: {sum(initial_conditions.values())}")
total_population_label.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')

# Buttons
button_frame = ttk.Frame(main_frame)
button_frame.grid(row=2, column=0, columnspan=2, pady=10)
param_update_button = ttk.Button(button_frame, text="بروزرسانی و نمایش نمودار", command=update_model)
param_update_button.grid(row=0, column=0, padx=10)

output_button = ttk.Button(button_frame, text="خروجی به اکسل", command=export_to_excel)
output_button.grid(row=0, column=1, padx=10)

# Initial plot
run_and_plot_model()

root.mainloop()


