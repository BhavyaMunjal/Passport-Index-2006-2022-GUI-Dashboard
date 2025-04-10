import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors
from PIL import Image, ImageTk

# Load Data
df = pd.read_csv("henleypassportindex1.csv")
df['YEAR'] = df['YEAR'].astype(int)
df['RANK'] = pd.to_numeric(df['RANK'], errors='coerce')
df['ACCESS TO COUNTRIES'] = pd.to_numeric(df['ACCESS TO COUNTRIES'], errors='coerce')

# Add dummy data if missing
if df[(df['COUNTRY'] == 'India') & (df['YEAR'] == 2007)].empty:
    df = pd.concat([df, pd.DataFrame([{'COUNTRY': 'India', 'YEAR': 2007, 'RANK': 70, 'ACCESS TO COUNTRIES': 45}])], ignore_index=True)

if df[(df['COUNTRY'] == 'India') & (df['YEAR'] == 2009)].empty:
    df = pd.concat([df, pd.DataFrame([{'COUNTRY': 'India', 'YEAR': 2009, 'RANK': 65, 'ACCESS TO COUNTRIES': 48}])], ignore_index=True)

# Main Window
root = tk.Tk()
root.title("Henley Passport Index Dashboard")
root.geometry("1300x1100")

# Load and set background image
bg_image = Image.open("background.jpg")  # Ensure this file is in the same folder
bg_image = bg_image.resize((1300, 1100), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)
background_label = tk.Label(root, image=bg_photo)
background_label.image = bg_photo  # Avoid garbage collection
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Content Frame
main_content = tk.Frame(root, bg="white")
main_content.place(relx=0, rely=0, relwidth=1, relheight=1)

# Filters Frame
filters_frame = tk.Frame(main_content, bg="white")
filters_frame.pack(pady=5)

# Country Filter
tk.Label(filters_frame, text="Select Country:", bg="white").grid(row=0, column=0, padx=10)
country_var = tk.StringVar()
country_menu = ttk.Combobox(filters_frame, textvariable=country_var, values=sorted(df['COUNTRY'].unique()), width=20)
country_menu.grid(row=0, column=1)

# Year Filter
tk.Label(filters_frame, text="Select Year:", bg="white").grid(row=0, column=2, padx=10)
year_var = tk.StringVar()
year_menu = ttk.Combobox(filters_frame, textvariable=year_var, values=sorted(df['YEAR'].unique()), width=20)
year_menu.grid(row=0, column=3)

# Reset Button
def reset_filters():
    country_var.set(df['COUNTRY'].iloc[0])
    year_var.set(str(df['YEAR'].max()))
    update_graphs()

reset_button = tk.Button(filters_frame, text="Reset", command=reset_filters)
reset_button.grid(row=0, column=4, padx=10)

# Matplotlib Figure
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))
fig.tight_layout(pad=5)
canvas = FigureCanvasTkAgg(fig, master=main_content)
canvas.get_tk_widget().pack()

# Outcome Texts
outcome_main_frame = tk.Frame(main_content, bg="white")
outcome_main_frame.pack(pady=5, fill="x")

line_outcome = tk.Label(outcome_main_frame, text="", font=("Arial", 10), wraplength=300, justify="center", bg="white")
line_outcome.pack(side="left", expand=True, padx=10)

bar_outcome = tk.Label(outcome_main_frame, text="", font=("Arial", 10), wraplength=300, justify="center", bg="white")
bar_outcome.pack(side="left", expand=True, padx=10)

pie_outcome = tk.Label(outcome_main_frame, text="", font=("Arial", 10), wraplength=300, justify="center", bg="white")
pie_outcome.pack(side="left", expand=True, padx=10)

colors = plt.cm.tab10.colors

# Update all graphs
def update_graphs(*args):
    update_line_chart()
    update_bar_chart()
    update_pie_chart()
    canvas.draw()

# Line Chart
def update_line_chart():
    ax1.clear()
    country = country_var.get()
    year = int(year_var.get())
    data = df[(df['COUNTRY'] == country) & (df['YEAR'] <= year)].sort_values(by='YEAR')
    ax1.plot(data['YEAR'], data['RANK'], marker='o', color=colors[0], label=country)
    ax1.set_title(f"{country} Rank till {year}")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Rank")
    ax1.invert_yaxis()
    ax1.grid(True)
    ax1.legend()

    if not data.empty:
        line_outcome.config(text=f"{country}'s rank changed from {int(data['RANK'].iloc[0])} ({int(data['YEAR'].iloc[0])}) to {int(data['RANK'].iloc[-1])} ({int(data['YEAR'].iloc[-1])}).")

    cursor = mplcursors.cursor(ax1.lines, hover=True)
    @cursor.connect("add")
    def on_add(sel):
        sel.annotation.set_text(f"Year: {int(data.iloc[sel.index]['YEAR'])}\nRank: {int(data.iloc[sel.index]['RANK'])}")

# Bar Chart
def update_bar_chart():
    ax2.clear()
    country = country_var.get()
    year = int(year_var.get())
    data = df[(df['COUNTRY'] == country) & (df['YEAR'] <= year)].sort_values(by='YEAR')

    bar_colors = [colors[(y - data['YEAR'].min()) // 5 % len(colors)] for y in data['YEAR']]
    bars = ax2.bar(data['YEAR'], data['ACCESS TO COUNTRIES'], color=bar_colors)
    ax2.set_title(f"{country} Access Till {year}")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Visa-Free Access")
    ax2.grid(True)

    if not data.empty:
        bar_outcome.config(text=f"{country}'s access grew from {int(data['ACCESS TO COUNTRIES'].iloc[0])} to {int(data['ACCESS TO COUNTRIES'].iloc[-1])}.")

    cursor = mplcursors.cursor(bars, hover=True)
    @cursor.connect("add")
    def on_add(sel):
        sel.annotation.set_text(f"Year: {int(data['YEAR'].iloc[sel.index])}\nAccess: {int(data['ACCESS TO COUNTRIES'].iloc[sel.index])}")

# Pie Chart
def update_pie_chart():
    ax3.clear()
    country = country_var.get()
    year = int(year_var.get())
    filtered = df[(df['COUNTRY'] == country) & (df['YEAR'] == year)]

    if not filtered.empty:
        access = int(filtered['ACCESS TO COUNTRIES'].values[0])
        total_countries = 199
        no_access = total_countries - access
        wedges, _, _ = ax3.pie([access, no_access], labels=["Visa-Free Access", "Visa Required"], autopct='%1.1f%%', colors=['#1f77b4', '#ff7f0e'], startangle=90)
        ax3.set_title(f"{country} Visa Access in {year}")
        pie_outcome.config(text=f"In {year}, {access} visa-free and {no_access} required for {country}.")

        cursor = mplcursors.cursor(wedges, hover=True)
        @cursor.connect("add")
        def on_add(sel):
            sel.annotation.set_text(f"{['Visa-Free', 'Visa Required'][sel.index]}: {access if sel.index == 0 else no_access}")
    else:
        pie_outcome.config(text="No data available.")

# Default Setup
country_var.set(df['COUNTRY'].iloc[0])
year_var.set(str(df['YEAR'].max()))
update_graphs()

# Bind Comboboxes
country_menu.bind("<<ComboboxSelected>>", update_graphs)
year_menu.bind("<<ComboboxSelected>>", update_graphs)

# Launch
root.mainloop()
