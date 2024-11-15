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
    "betta": 1,
    "epsilon": 0.8,
    "X": 0.75,
    "alpha": 0.5,
    "gamma": 0.3,
    "zetta": 0.03,
    "omega": 0.95,
    "delta": 0.018,
    "D_vaccin_rate": 0,
    "D_vaccin_effect": 0,
    "tetta": 0,
    "meu": 0,
    "etta": 0
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

# Update parameters for the SEAIR model
parameters.update({
    "D_incubation": 5.2,  # زمان دوره کمون
    # "transfer_rate": 0.5,  # نسبت انتقال
    "D_asymptomatic": 2.9,  # طول دوره بیماری افراد بدون علامت
    "D_symptomatic": 7.0,  # طول دوره بیماری افراد با علامت
    # t infictios
    "hospitalization_duration":28.6,  # مدت زمان بستری در بیمارستان
    "D_mortality": 32,  # زمان از پایان دوره کمون تا مرگ
    "D_recovery_mild": 11.1,  # زمان بهبودی برای موارد خفیف
    "vaccination_day": 0,  # روز اعمال واکسیناسیون
    "natural_mortality_rate": 0,  # Example natural mortality rate
    "birth_rate": 0  # نرخ متولدین
})

# Add Persian translations for new parameters
parameter_translations.update({
    "D_incubation": "زمان انتقال (طول دوره کمون)",
    # "transfer_rate": "نسبت انتقال",
    "D_asymptomatic": "طول دوره بیماری افراد بدون علامت",
    "D_symptomatic": "طول دوره بیماری افراد با علامت",
    "hospitalization_duration": "مدت زمان بستری در بیمارستان",
    "D_mortality": "زمان از پایان دوره کمون تا مرگ",
    "D_recovery_mild": "زمان بهبودی برای موارد خفیف",
    "vaccination_day": "روز اعمال واکسیناسیون",
    "natural_mortality_rate": "نرخ مرگ و میر طبیعی",
    "birth_rate": "نرخ متولدین"
})



# Default initial conditions
initial_conditions = {
    "S0": 7000000,
    "E0": 1,
    "A0": 1,
    "I0": 0,
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
    
    # Update the new parameters
    for param in parameters:
        if param not in ["natural_mortality_rate","hospitalization_duration","D_mortality","D_recovery_mild","vaccination_day","birth_rate",    
            "D_symptomatic","D_asymptomatic","D_incubation","meu", "etta","tetta","D_vaccin_effect","D_vaccin_rate","delta","zetta","X","betta", "epsilon", "omega", "alpha", "gamma"]:  # These are handled separately
            parameters[param] = float(ic_entries[param].get())  # Update from the input fields

    # Recalculate R0
    R0_value = calculate_R0()
    R0_label.config(text=f"Basic Reproduction Number (R0): {R0_value:.2f}")
    
    # Update t_max based on the slider value
    t_max = int(days_slider.get())
    
    # Run the model and plot the results
    run_and_plot_model()




default_R0 = 2.2
def calculate_R0():
    # Extracting the parameters
    beta = parameters["betta"]
    epsilon = parameters["epsilon"]
    omega = parameters["omega"]
    alpha = parameters["alpha"]
    gamma = parameters["gamma"]
    
    # Calculate R0
    R0 = (beta * (1 + epsilon * omega)) / (alpha + gamma)
    
    return R0

# Example usage:
R0_value = calculate_R0()
# print(f"Basic Reproduction Number (R0): {R0_value}")

def update_R0_value():
    """ Update R0 based on user inputs or default value. """
    global default_R0
    
    if advanced_r0_var.get() == 0:  # If advanced settings are not checked
        default_R0 = float(r0_entry.get())  # Use the default R0 value entered by the user
    else:  # If advanced settings are checked, calculate R0 based on parameters
        # Get user inputs for the parameters
        beta = float(betta_entry.get())
        epsilon = float(epsilon_entry.get())
        omega = float(omega_entry.get())
        alpha = float(alpha_entry.get())
        gamma = float(gamma_entry.get())
        
        # Set the parameters for the calculation
        parameters["betta"] = beta
        parameters["epsilon"] = epsilon
        parameters["omega"] = omega
        parameters["alpha"] = alpha
        parameters["gamma"] = gamma
        
        # Recalculate R0 based on user inputs
        default_R0 = (beta * (1 + epsilon * omega)) / (alpha + gamma)
    
    # Update the R0 label to show the calculated value
    R0_label.config(text=f"Basic Reproduction Number (R0): {default_R0:.2f}")

def toggle_advanced_settings():
    """ Toggle visibility of advanced R0 settings based on checkbox state. """
    if advanced_r0_var.get() == 1:  # If checkbox is checked, show advanced settings
        advanced_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
    else:  # If unchecked, hide advanced settings
        advanced_frame.grid_forget()

def seair_model(S, E, A, I, Ri, Ra, Is, D, Va, Im, t, RZero, sigma, natural_mortality_rate):
    betaI = RZero / 2.9
    betaA = (RZero * 0.35) / 2.9
    aE = sigma * 0.4
    iE = sigma * 0.6
    gammaI = 1 / 2.9
    gammaA = 1 / 2.9
    p_mild = 14 - 2.9
    p_severe = 0.2
    p_fatal = 0
    birth_rate = 0

    # Differential equations
    ds = (-betaI * I * S) - (S * parameters["D_vaccin_rate"] * (parameters["D_vaccin_effect"] / 100)) - (natural_mortality_rate * S) + (parameters["birth_rate"] * S)
    de = (betaI * I * S) + (betaA * A * S) - (aE * E) - (natural_mortality_rate * E)
    da = (aE * E) - (gammaA * A) - (natural_mortality_rate * A)
    di = (iE * E) - (gammaI * I) - (natural_mortality_rate * I)
    dRi = (gammaI * I) - (natural_mortality_rate * Ri)
    dRa = (gammaA * A) - (natural_mortality_rate * Ra)
    dIs = (p_severe * I) - (p_fatal * I) - (natural_mortality_rate * Is)
    dD = p_fatal * I
    dVa = parameters["birth_rate"] * S
    dIm = 0

    return ds, de, da, di, dRi, dRa, dIs, dD, dVa, dIm

def euler_method(S0, E0, A0, I0, Ri0, Ra0, Is0, D0, Va0, Im0, t, dt, RZero, sigma, natural_mortality_rate=0, momentum_factor=0.1):
    # Initial values
    S, E, A, I, Ri, Ra, Is, D, Va, Im = [S0], [E0], [A0], [I0], [Ri0], [Ra0], [Is0], [D0], [Va0], [Im0]
    
    # Momentum values for each compartment (initialize to 0)
    momentum_S, momentum_E, momentum_A, momentum_I, momentum_Ri, momentum_Ra, momentum_Is, momentum_D, momentum_Va, momentum_Im = [0]*10
    
    for i in range(1, len(t)):
        ds, de, da, di, dRi, dRa, dIs, dD, dVa, dIm = seair_model(
            S[-1], E[-1], A[-1], I[-1], Ri[-1], Ra[-1], Is[-1], D[-1], Va[-1], Im[-1], t[i], RZero, sigma, natural_mortality_rate
        )

        # Apply momentum to each compartment update
        S_new = max(S[-1] + ds * dt + momentum_S, 0)
        E_new = max(E[-1] + de * dt + momentum_E, 0)
        A_new = max(A[-1] + da * dt + momentum_A, 0)
        I_new = max(I[-1] + di * dt + momentum_I, 0)
        Ri_new = max(Ri[-1] + dRi * dt + momentum_Ri, 0)
        Ra_new = max(Ra[-1] + dRa * dt + momentum_Ra, 0)
        Is_new = max(Is[-1] + dIs * dt + momentum_Is, 0)
        D_new = max(D[-1] + dD * dt + momentum_D, 0)
        Va_new = max(Va[-1] + dVa * dt + momentum_Va, 0)
        Im_new = max(Im[-1] + dIm * dt + momentum_Im, 0)
        
        # Update momentum based on the change in the state
        momentum_S = momentum_factor * (S_new - S[-1])
        momentum_E = momentum_factor * (E_new - E[-1])
        momentum_A = momentum_factor * (A_new - A[-1])
        momentum_I = momentum_factor * (I_new - I[-1])
        momentum_Ri = momentum_factor * (Ri_new - Ri[-1])
        momentum_Ra = momentum_factor * (Ra_new - Ra[-1])
        momentum_Is = momentum_factor * (Is_new - Is[-1])
        momentum_D = momentum_factor * (D_new - D[-1])
        momentum_Va = momentum_factor * (Va_new - Va[-1])
        momentum_Im = momentum_factor * (Im_new - Im[-1])
        
        # Scale the values if total population exceeds N
        total_population = S_new + E_new + A_new + I_new + Ri_new + Ra_new + Is_new + D_new + Va_new + Im_new
        if total_population > N:
            scale_factor = N / total_population
            S_new *= scale_factor
            E_new *= scale_factor
            A_new *= scale_factor
            I_new *= scale_factor
            Ri_new *= scale_factor
            Ra_new *= scale_factor
            Is_new *= scale_factor
            D_new *= scale_factor
            Va_new *= scale_factor
            Im_new *= scale_factor

        # Append the new values
        S.append(S_new)
        E.append(E_new)
        A.append(A_new)
        I.append(I_new)
        Ri.append(Ri_new)
        Ra.append(Ra_new)
        Is.append(Is_new)
        D.append(D_new)
        Va.append(Va_new)
        Im.append(Im_new)

    return S, E, A, I, Ri, Ra, Is, D, Va, Im




def run_and_plot_model():
    global S, E, A, I, Ri, Ra, Is, D, Va, Im, t
    dt = 1
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

    RZero = 2.5
    sigma = 5.2 / 3.6
    natural_mortality_rate = 0  # Set a default value for natural mortality rate

    S, E, A, I, Ri, Ra, Is, D, Va, Im = euler_method(S0, E0, A0, I0, Ri0, Ra0, Is0, D0, Va0, Im0, t, dt, RZero, sigma, natural_mortality_rate, momentum_factor=0.8)


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
    # Ensure non-negative values before exporting to Excel
    rounded_S = np.round(np.maximum(S, 0)).astype(int)
    rounded_E = np.round(np.maximum(E, 0)).astype(int)
    rounded_A = np.round(np.maximum(A, 0)).astype(int)
    rounded_I = np.round(np.maximum(I, 0)).astype(int)
    rounded_Ri = np.round(np.maximum(Ri, 0)).astype(int)
    rounded_Ra = np.round(np.maximum(Ra, 0)).astype(int)
    rounded_Is = np.round(np.maximum(Is, 0)).astype(int)
    rounded_D = np.round(np.maximum(D, 0)).astype(int)
    rounded_Va = np.round(np.maximum(Va, 0)).astype(int)
    rounded_Im = np.round(np.maximum(Im, 0)).astype(int)

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


# Create main root window
root = tk.Tk()
root.title("SEAIR مدل")

# تنظیم فونت پیش‌فرض
default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(family="B Nazanin", size=12)

# Create a canvas for scrolling
canvas = tk.Canvas(root)
canvas.pack(side="left", fill="both", expand=True)

# Create a vertical scrollbar linked to the canvas
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

# Create a frame within the canvas which will be scrolled
scrollable_frame = ttk.Frame(canvas)

# Configure canvas to scroll the frame
canvas.configure(yscrollcommand=scrollbar.set)

# Add the frame to the canvas window
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# Update scrollbar and frame size when the content inside the frame changes
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
scrollable_frame.bind("<Configure>", on_frame_configure)

# Main Frame
main_frame = ttk.Frame(scrollable_frame)
main_frame.pack(pady=10, ipadx=55, ipady=10, expand=True)

# Parameter Frame
param_frame = ttk.LabelFrame(main_frame, text="بروزرسانی پارامترها")
param_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
param_sliders = {}

# Define two lists for splitting the parameters
first_column_params = ["X", "zetta", "omega"]
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
days_slider.set(365)  # مقدار پیش‌فرض
days_slider.grid(row=len(first_column_params) + len(second_column_params), column=1, padx=10, pady=5)

# Quarantine Slider
quarantine_slider_label = ttk.Label(param_frame, text="درصد قرنطینه:")
quarantine_slider_label.grid(row=len(first_column_params) + len(second_column_params) + 1, column=0, padx=10, pady=5)

quarantine_slider = tk.Scale(param_frame, from_=0, to=100, orient=tk.HORIZONTAL)
quarantine_slider.set(0)  # مقدار پیش‌فرض
quarantine_slider.grid(row=len(first_column_params) + len(second_column_params) + 1, column=1, padx=10, pady=5)

# Add initial R0 entry field
R0_label = ttk.Label(param_frame, text="Basic Reproduction Number (R0):")
R0_label.grid(row=len(first_column_params) + len(second_column_params) + 2, column=0, padx=10, pady=5)

r0_entry = ttk.Entry(param_frame)
r0_entry.grid(row=len(first_column_params) + len(second_column_params) + 2, column=1, padx=10, pady=5)
r0_entry.insert(0, str(calculate_R0()))  # Insert default R0 value

# Create advanced R0 settings checkbox and move it to the second column (end)
advanced_r0_var = tk.IntVar()
advanced_r0_checkbox = ttk.Checkbutton(param_frame, text="تنظیمات پیشرفته R0", variable=advanced_r0_var, command=toggle_advanced_settings)
advanced_r0_checkbox.grid(row=len(first_column_params) + len(second_column_params) + 3, column=0, columnspan=2, padx=10, pady=5)

# Create advanced R0 settings frame (initially hidden)
advanced_frame = ttk.Frame(param_frame)

# Add the advanced R0 settings fields (but no β, 𝜖, 𝜔, 𝛼 in the main frame)
ttk.Label(advanced_frame, text="Transmission Rate (β):").grid(row=0, column=0, padx=10, pady=5)
betta_entry = ttk.Entry(advanced_frame)
betta_entry.grid(row=0, column=1, padx=10, pady=5)
betta_entry.insert(0, str(parameters["betta"]))  # Default value

ttk.Label(advanced_frame, text="Relative Infectivity (𝜖):").grid(row=1, column=0, padx=10, pady=5)
epsilon_entry = ttk.Entry(advanced_frame)
epsilon_entry.grid(row=1, column=1, padx=10, pady=5)
epsilon_entry.insert(0, str(parameters["epsilon"]))  # Default value

ttk.Label(advanced_frame, text="Symptomatic Fraction (𝜔):").grid(row=2, column=0, padx=10, pady=5)
omega_entry = ttk.Entry(advanced_frame)
omega_entry.grid(row=2, column=1, padx=10, pady=5)
omega_entry.insert(0, str(parameters["omega"]))  # Default value

ttk.Label(advanced_frame, text="Rate of Progression (𝛼):").grid(row=3, column=0, padx=10, pady=5)
alpha_entry = ttk.Entry(advanced_frame)
alpha_entry.grid(row=3, column=1, padx=10, pady=5)
alpha_entry.insert(0, str(parameters["alpha"]))  # Default value

ttk.Label(advanced_frame, text="Recovery Rate (𝛾):").grid(row=4, column=0, padx=10, pady=5)
gamma_entry = ttk.Entry(advanced_frame)
gamma_entry.grid(row=4, column=1, padx=10, pady=5)
gamma_entry.insert(0, str(parameters["gamma"]))  # Default value

# Add Update button to calculate and update R0
update_R0_button = ttk.Button(param_frame, text="بروزرسانی R0", command=update_R0_value)
update_R0_button.grid(row=len(first_column_params) + len(second_column_params) + 4, column=0, columnspan=2, pady=10)

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

# Assuming 'N' is the total population value from the user (stored after user input)
total_population_value = N  # Replace 'N' with the actual value you have from the user

# Instead of using an entry field, display the value of 'جمعیت کل' (Total Population)
total_population_label = ttk.Label(init_cond_frame, text=f"جمعیت کل: {total_population_value}")
total_population_label.grid(row=len(initial_conditions), column=0, padx=10, pady=5)

# Add entry fields for the new parameters
new_param_frame = ttk.LabelFrame(main_frame, text="بروزرسانی پارامترهای جدید")
new_param_frame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

# Define and create input fields for new parameters
new_params = [
    ("D_incubation", "زمان دوره کمون"),
    # ("transfer_rate", "نسبت انتقال"),
    ("D_asymptomatic", "طول دوره بیماری افراد بدون علامت"),
    ("D_symptomatic", "طول دوره بیماری افراد با علامت"),
    ("natural_mortality_rate", "نرخ مرگ و میر طبیعی")
]

for idx, (param, label) in enumerate(new_params):
    param_label = ttk.Label(new_param_frame, text=label)
    param_label.grid(row=idx, column=0, padx=10, pady=5)
    param_entry = ttk.Entry(new_param_frame)
    param_entry.grid(row=idx, column=1, padx=10, pady=5)
    param_entry.insert(0, parameters[param])  # Default value

# Button Frame
button_frame = ttk.Frame(main_frame)
button_frame.grid(row=2, column=0, columnspan=2, pady=10)

param_update_button = ttk.Button(button_frame, text="بروزرسانی و نمایش نمودار", command=update_model)
param_update_button.grid(row=0, column=0, padx=10)

output_button = ttk.Button(button_frame, text="خروجی به اکسل", command=export_to_excel)
output_button.grid(row=0, column=1, padx=10)

t_max = int(days_slider.get())
    
    # Run the model and plot the results
run_and_plot_model()
