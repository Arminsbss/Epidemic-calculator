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

def reshape_arabic(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

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
    "etta": 0.1
}
# Persian translations for parameter names
parameter_translations = {
    "betta": "نرخ انتقال",
    "epsilon": "عفونت نسبی موارد بدون علامت",
    "X": "عفونت نسبی موارد منفرد علامت دار",
    "alpha": "نرخ پیشرفت از کلاس در معرض",
    "gamma": "میزان پیشرفت به کلاس بازیابی شده",
    "zetta": "میزان مرگ و میر موردي",
    "omega": "نسبت موارد مواجهه شده که علامت دار می شوند",
    "delta": "میزان پیشرفت تا مرگ در میان طبقه عفونی علامت دار",
    "D_vaccin_rate": "نرخ واکسیناسیون",
    "D_vaccin_effect": "تاثیر واکسیناسیون",
    "tetta": "میزان جداسازي",
    "meu": "اثربخشی درمان",
    "etta": "نرخ مهاجرت بین شهرها و مناطق",
    "quarantine": "درصد قرنطینه"
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

# Total population
N = sum(initial_conditions.values())

def update_model():
    global t_max, N
    # Update parameters
    for param in parameters:
        parameters[param] = param_sliders[param].get()

    # Update initial conditions
    for ic in initial_conditions:
        initial_conditions[ic] = float(ic_entries[ic].get())

    # Update total population
    N = float(total_population_entry.get())
    
    # Update t_max based on the slider value
    t_max = int(days_slider.get())
    
    # Run the model and plot
    run_and_plot_model()

def seair_model(S, E, A, I, Ri, Ra, Is, D, Va, Im, t):
    quarantine_percentage = quarantine_slider.get() / 100
    effective_population = N * (1 - quarantine_percentage)

    lambda_ = parameters["betta"] * (I + parameters["epsilon"] * A + parameters["X"] * Is) / effective_population
    dSdt = -lambda_ * S
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
    return S, E, A, I, Ri, Ra, Is, D, Va, Im

def run_and_plot_model():
    global S, E, A, I, Ri, Ra, Is, D, Va, Im, t
    dt = 0.1
    t = np.arange(0, t_max + dt, dt)

    S0 = initial_conditions["S0"]
    E0 = initial_conditions["E0"]
    A0 = initial_conditions["A0"]
    I0 = initial_conditions["I0"]
    Ri0 = initial_conditions["Ri0"]
    Ra0 = initial_conditions["Ra0"]
    Is0 = initial_conditions["Is0"]
    D0 = initial_conditions["D0"]
    Va0 = initial_conditions["Va0"]
    Im0 = initial_conditions["Im0"]

    S, E, A, I, Ri, Ra, Is, D, Va, Im = euler_method(S0, E0, A0, I0, Ri0, Ra0, Is0, D0, Va0, Im0, t, dt)

    # Plotting results
    plt.figure(figsize=(10, 6))
    plt.plot(t, S, label=reshape_arabic('آسیب پذیر'))
    plt.plot(t, E, label=reshape_arabic('در معرض'))
    plt.plot(t, A, label=reshape_arabic('بدون علامت'))
    plt.plot(t, I, label=reshape_arabic('عفونی'))
    plt.plot(t, Ri, label=reshape_arabic('بهبودیافته (علامت‌دار)'))
    plt.plot(t, Ra, label=reshape_arabic('بهبودیافته (بدون علامت)'))
    plt.plot(t, Is, label=reshape_arabic('جداسازی شده'))
    plt.plot(t, D, label=reshape_arabic('درگذشته'))
    plt.plot(t, Va, label=reshape_arabic('واکسینه شده'))
    plt.plot(t, Im, label=reshape_arabic('ایمن'))

    plt.title(reshape_arabic('نمودار مدل SEAIR'))
    plt.xlabel(reshape_arabic('زمان (روزها)'))
    plt.ylabel(reshape_arabic('تعداد افراد'))
    plt.legend()
    plt.grid()
    plt.show()

def export_to_excel():
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
default_font.configure(family="B Nazanin", size=12)

# Main Frame
main_frame = ttk.Frame(root)
main_frame.pack(pady=10, ipadx=55, ipady=10, expand=True)

# Parameter Frame
param_frame = ttk.LabelFrame(main_frame, text="بروزرسانی پارامترها")
param_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
param_sliders = {}

# Define two lists for splitting the parameters
first_column_params = ["betta", "epsilon", "X", "alpha", "gamma", "zetta", "omega"]
second_column_params = ["delta", "D_vaccin_rate", "D_vaccin_effect", "tetta", "meu", "etta"]

# Fill the first column
for idx, param in enumerate(first_column_params):
    value = parameters[param]
    label = ttk.Label(param_frame, text=parameter_translations[param])
    label.grid(row=idx, column=0, padx=10, pady=5)
    
    slider = tk.Scale(param_frame, from_=0, to=1, orient=tk.HORIZONTAL, resolution=0.01)
    slider.set(value)
    slider.grid(row=idx, column=1, padx=10, pady=5)
    param_sliders[param] = slider

# Fill the second column
for idx, param in enumerate(second_column_params):
    value = parameters[param]
    label = ttk.Label(param_frame, text=parameter_translations[param])
    label.grid(row=idx, column=2, padx=10, pady=5)
    
    slider = tk.Scale(param_frame, from_=0, to=1, orient=tk.HORIZONTAL, resolution=0.01)
    slider.set(value)
    slider.grid(row=idx, column=3, padx=10, pady=5)
    param_sliders[param] = slider

# Days Simulation Slider
days_slider_label = ttk.Label(param_frame, text="تعداد روزهای شبیه‌سازی:")
days_slider_label.grid(row=len(first_column_params) + len(second_column_params), column=0, padx=10, pady=5)

days_slider = tk.Scale(param_frame, from_=10, to=365, orient=tk.HORIZONTAL)
days_slider.set(80)  # مقدار پیش‌فرض
days_slider.grid(row=len(first_column_params) + len(second_column_params), column=1, padx=10, pady=5)

# Quarantine Slider
quarantine_slider_label = ttk.Label(param_frame, text="درصد قرنطینه:")
quarantine_slider_label.grid(row=len(first_column_params) + len(second_column_params) + 1, column=0, padx=10, pady=5)

quarantine_slider = tk.Scale(param_frame, from_=0, to=100, orient=tk.HORIZONTAL)
quarantine_slider.set(0)  # مقدار پیش‌فرض
quarantine_slider.grid(row=len(first_column_params) + len(second_column_params) + 1, column=1, padx=10, pady=5)

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

# Total Population Entry
total_population_label = ttk.Label(init_cond_frame, text="جمعیت کل:")
total_population_label.grid(row=len(initial_conditions), column=0, padx=10, pady=5)

total_population_entry = ttk.Entry(init_cond_frame)
total_population_entry.grid(row=len(initial_conditions), column=1, padx=10, pady=5)
total_population_entry.insert(0, str(N))  # مقدار پیش‌فرض

# Buttons
button_frame = ttk.Frame(main_frame)
button_frame.grid(row=2, column=0, columnspan=2, pady=10)
param_update_button = ttk.Button(button_frame, text="بروزرسانی و نمایش نمودار", command=update_model)
param_update_button.grid(row=0, column=0, padx=10)

output_button = ttk.Button(button_frame, text="خروجی به اکسل", command=export_to_excel)
output_button.grid(row=0, column=1, padx=10)

# Initial plot
t_max = 80  # مقدار پیش‌فرض برای t_max
run_and_plot_model()

root.mainloop()
