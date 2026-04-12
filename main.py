import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


window = tk.Tk()
window.title(" Data Visualization Dashboard")
window.geometry("1200x800")


data = None
selected_columns = []  
entry_fields = {}  
saved_file_path = None  


def create_scrollable_frame(parent):
    container = ttk.Frame(parent)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    container.pack(fill="both", expand=True)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return scrollable_frame

scrollable_frame = create_scrollable_frame(window)


def upload_and_save_csv():
    global data, saved_file_path
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        try:
            data = pd.read_csv(file_path)
            saved_file_path = file_path
            print("CSV file loaded: " + saved_file_path)
            create_column_checkboxes()
            create_entry_fields()
            display_data_table()
        except Exception as e:
            print("Failed to upload or save file: " + str(e))


def create_column_checkboxes():
    global selected_columns
    for widget in column_frame.winfo_children():
        widget.destroy()

    selected_columns.clear()
    ttk.Label(column_frame, text="Select Columns for Plotting:").pack()
    for col in data.columns:
        var = tk.BooleanVar()
        checkbox = ttk.Checkbutton(column_frame, text=col, variable=var)
        checkbox.pack(anchor="w")
        selected_columns.append((col, var))


def create_entry_fields():
    global entry_fields
    for widget in entry_frame.winfo_children():
        widget.destroy()

    entry_fields.clear()
    ttk.Label(entry_frame, text="Add New Row:").pack(pady=5)
    for col in data.columns:
        ttk.Label(entry_frame, text=col).pack()
        entry = ttk.Entry(entry_frame)
        entry.pack()
        entry_fields[col] = entry

    ttk.Button(entry_frame, text="Add Row", command=add_row).pack(pady=10)
    

def add_row():
    global data
    if data is None:
        print("Please load a dataset first.")
        return

    new_row = {col: entry.get() for col, entry in entry_fields.items()}
    try:
        new_row_df = pd.DataFrame([new_row])
        data = pd.concat([data, new_row_df], ignore_index=True)
        data.to_csv(saved_file_path, index=False)
        print("Row added and saved to the main CSV file!")
        create_column_checkboxes()
        display_data_table()
    except Exception as e:
        print("Failed to add row: " + str(e))


def delete_selected_row():
    global data
    if data is None:
        print("Please load a dataset first.")
        return

    selected_item = table.selection()
    if not selected_item:
        print("Please select a row to delete.")
        return

    row_index = table.index(selected_item[0])
    try:
        data = data.drop(index=row_index).reset_index(drop=True)
        data.to_csv(saved_file_path, index=False)
        print("Row deleted and CSV file updated!")
        display_data_table()
    except Exception as e:
        print("Failed to delete row: " + str(e))


def display_data_table():
    global data
    if data is None:
        print("Please load a dataset first.")
        return

    for widget in table_frame.winfo_children():
        widget.destroy()

    global table
    table = ttk.Treeview(table_frame, columns=data.columns.tolist(), show="headings", height=15)
    for col in data.columns:
        table.heading(col, text=col)
        table.column(col, anchor="center")

    for i, row in data.iterrows():
        table.insert("", "end", values=row.tolist())

    table.pack(fill="both", expand=True)

    ttk.Button(table_frame, text="Delete Selected Row", command=delete_selected_row).pack(pady=10)


def validate_numeric_columns(selected_cols):
    global data
    numeric_cols = []
    for col in selected_cols:
        try:
            data[col] = pd.to_numeric(data[col], errors="coerce")
            numeric_cols.append(col)
        except Exception as e:
            pass
    return numeric_cols


def plot_data():
    global data
    if data is None:
        print("Please load a dataset first.")
        return

    selected_cols = [col for col, var in selected_columns if var.get()]
    if not selected_cols:
        print("Please select at least one column to plot.")
        return

    selected_cols = validate_numeric_columns(selected_cols)
    if not selected_cols:
        print("No numeric columns selected for plotting.")
        return

    chart_type_selected = chart_type_var.get()
    chart_title = title_var.get()

    fig, ax = plt.subplots(figsize=(8, 5))
    if chart_type_selected == "Bar Chart":
        for col in selected_cols:
            ax.bar(data.index, data[col], label=col)
    elif chart_type_selected == "Line Chart":
        for col in selected_cols:
            ax.plot(data.index, data[col], label=col)
    elif chart_type_selected == "Scatter Plot":
        if len(selected_cols) < 2:
            print("Scatter plot requires at least 2 columns.")
            return
        ax.scatter(data[selected_cols[0]], data[selected_cols[1]], label=f"{selected_cols[0]} vs {selected_cols[1]}")
    elif chart_type_selected == "Histogram":
        ax.hist([data[col] for col in selected_cols], bins=20, label=selected_cols, alpha=0.7)

    ax.set_title(chart_title)
    ax.legend()

    plot_window = tk.Toplevel(window)
    plot_window.title("Generated Plot")
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack()


column_frame = ttk.Frame(scrollable_frame)
column_frame.pack(side="left", fill="both", expand=True, padx=10)


entry_frame = ttk.Frame(scrollable_frame)
entry_frame.pack(side="left", fill="both", expand=True, padx=10)


table_frame = ttk.Frame(scrollable_frame)
table_frame.pack(fill="both", expand=True, pady=10)


ttk.Button(scrollable_frame, text="Upload and Save CSV File", command=upload_and_save_csv).pack(pady=10)


chart_type_var = tk.StringVar(value="Bar Chart")
ttk.Label(scrollable_frame, text="Select Chart Type:").pack()
ttk.OptionMenu(scrollable_frame, chart_type_var, "Bar Chart", "Line Chart", "Scatter Plot", "Histogram").pack()

title_var = tk.StringVar(value="Chart Title")
ttk.Label(scrollable_frame, text="Chart Title:").pack()
ttk.Entry(scrollable_frame, textvariable=title_var).pack()

ttk.Button(scrollable_frame, text="Generate Plot", command=plot_data).pack(pady=10)


window.mainloop()
