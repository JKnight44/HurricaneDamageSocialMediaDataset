import os
import tkinter as tk
from tkinter import filedialog, ttk
from ultralytics import YOLO
import threading
import sys
import io

# Persistent storage for hyperparameters
persistent_sub_vars = {}

def train_model():
    # Create a new window for progress as a modal subwindow
    progress_window = tk.Toplevel(root)
    progress_window.title("Training Progress")
    progress_window.geometry("600x400")

    # Make progress_window modal
    progress_window.transient(root)
    progress_window.grab_set()

    progress_label = tk.Label(progress_window, text="Initializing training...")
    progress_label.pack(pady=10)

    progress_bar = ttk.Progressbar(progress_window, orient="horizontal", length=500, mode="determinate")
    progress_bar.pack(pady=10)

    # Terminal-like text box
    terminal_frame = tk.Frame(progress_window)
    terminal_frame.pack(fill='both', expand=True, padx=10, pady=10)

    terminal_text = tk.Text(terminal_frame, wrap='word', height=10, bg='black', fg='white')
    terminal_text.pack(side='left', fill='both', expand=True)

    terminal_scroll = tk.Scrollbar(terminal_frame, command=terminal_text.yview)
    terminal_scroll.pack(side='right', fill='y')
    terminal_text.config(yscrollcommand=terminal_scroll.set)

    # Redirect stdout to the terminal window
    class StdoutRedirector(io.StringIO):
        def write(self, s):
            terminal_text.insert(tk.END, s)
            terminal_text.see(tk.END)
            super().write(s)

    sys.stdout = StdoutRedirector()

    def run_training():
        # Set the model
        os.chdir("models")
        model = YOLO(model_var.get())

        # Set the datasets
        selected_dataset_name = dataset_var.get()
        selected_dataset_path = dataset_paths.get(selected_dataset_name, "Path not found")

        # Dynamically create custom hyperparameters
        custom_hyp = {}
        custom_epochs = None
        custom_batch = None

        for var_name, (check_var, entry_var) in persistent_sub_vars.items():
            if var_name.lower() == "epochs":
                try:
                    custom_epochs = int(entry_var.get())
                except ValueError:
                    custom_epochs = entry_var.get()
            elif var_name.lower() == "batch":
                try:
                    custom_batch = int(entry_var.get())
                except ValueError:
                    custom_batch = entry_var.get()
            elif check_var.get():
                try:
                    custom_hyp[var_name] = float(entry_var.get())
                except ValueError:
                    custom_hyp[var_name] = entry_var.get()

        if custom_epochs is None:
            custom_epochs = 100
        if custom_batch is None:
            custom_batch = 16

        progress_bar["maximum"] = custom_epochs

        # Training with progress update
        model.train(data=f"../{selected_dataset_path}/{selected_dataset_name}.yaml",
                    epochs=custom_batch,
                    batch=custom_batch,
                    **custom_hyp)

        # Update after training completion
        progress_bar["value"] = custom_epochs
        progress_label.config(text="Training Complete!")

        def close_progress():
            sys.stdout = sys.__stdout__  # Restore stdout
            progress_window.destroy()
            os.chdir("..")

        tk.Button(progress_window, text="Close", command=close_progress).pack(pady=10)

    # Run training in a separate thread to keep GUI responsive
    threading.Thread(target=run_training, daemon=True).start()

def extra_function():
    print("Extra button clicked!")

def open_subwindow():
    sub_window = tk.Toplevel(root)
    sub_window.title("Hyperparameters")
    sub_window.geometry("300x200")

    # Position subwindow in the middle of the main window
    root.update_idletasks()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    root_x = root.winfo_x()
    root_y = root.winfo_y()

    sub_width = 300
    sub_height = 400

    x = root_x + (root_width // 2) - (sub_width // 2)
    y = root_y + (root_height // 2) - (sub_height // 2)
    sub_window.geometry(f"{sub_width}x{sub_height}+{x}+{y}")

    tk.Label(sub_window, text="Hyperparameters").pack(pady=10)

    def update_entry_state():
        for name, (check_var, entry_var) in persistent_sub_vars.items():
            if name.lower() in ["epochs", "batch"]:
                check_var.set(True)
            entry = entry_widgets[name]
            if check_var.get():
                entry.config(state='normal')
            else:
                entry.config(state='disabled')

    # Read hyperparameters from file if not already loaded
    if not persistent_sub_vars:
        try:
            with open("hyperparameters.txt", "r") as file:
                lines = file.readlines()

            for line in lines:
                if ":" in line:
                    var_name, default_val = line.strip().split(":")

                    check_var = tk.BooleanVar()
                    # Ensure 'epochs' and 'batch' start as checked
                    if var_name.lower() in ["epochs", "batch"]:
                        check_var.set(True)
                    else:
                        check_var.set(False)
                    entry_var = tk.StringVar(value=default_val)
                    persistent_sub_vars[var_name] = (check_var, entry_var)

        except FileNotFoundError:
            tk.Label(sub_window, text="hyperparameters.txt not found.").pack(pady=10)

    # Create UI elements from persistent data
    entry_widgets = {}
    for var_name, (check_var, entry_var) in persistent_sub_vars.items():
        frame = tk.Frame(sub_window)
        frame.pack(pady=5, fill='x')

        check = tk.Checkbutton(frame, text=var_name, variable=check_var,
                               command=update_entry_state)
        check.pack(side='left')

        entry = tk.Entry(frame, width=20, textvariable=entry_var)
        entry.pack(side='left', padx=5)

        if var_name.lower() in ["epochs", "batch"] or check_var.get():
            entry.config(state='normal')
        else:
            entry.config(state='disabled')

        entry_widgets[var_name] = entry

    tk.Button(sub_window, text="Close", command=sub_window.destroy).pack(pady=10)

    # Make the subwindow modal
    sub_window.transient(root)
    sub_window.grab_set()
    root.wait_window(sub_window)

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        save_dir_var.set(directory)

# MAIN

if __name__ == '__main__':
    # Define consts
    HOME_DIR = ".."
    DATASET_DIR = f"{HOME_DIR}/Datasets"

    # Create main window
    root = tk.Tk()
    root.title("Yolo Model Trainer")
    root.geometry("400x400")

    # Dropdown Menu for Models
    tk.Label(root, text="Select a pretrained model to train:").pack(pady=5)

    # Loop over the 'models' directory and list model names
    model_dir = "models"
    models = [f for f in os.listdir(model_dir) if os.path.isfile(os.path.join(model_dir, f))]

    model_var = tk.StringVar(value=models[0] if models else "No models found")
    model = tk.OptionMenu(root, model_var, *models)
    model.pack()

    # Dropdown Menu for Datasets
    tk.Label(root, text="Choose a dataset to train the model on:").pack(pady=5)

    datasets = []
    dataset_paths = {}
    for dir_name in [f"{DATASET_DIR}/Core", f"{DATASET_DIR}/SocialMedia"]:
        if os.path.isdir(dir_name):
            for f in os.listdir(dir_name):
                dataset_path = os.path.join(dir_name, f)
                if os.path.isdir(dataset_path):
                    datasets.append(f)
                    dataset_paths[f] = dataset_path

    dataset_var = tk.StringVar(value=datasets[0] if datasets else "No datasets found")
    dataset_dropdown = tk.OptionMenu(root, dataset_var, *datasets)
    dataset_dropdown.pack()

    # Open Hyperparameters window
    tk.Button(root, text="Change Hyperparameter Window", command=open_subwindow).pack(pady=10)

    # Directory Selection
    tk.Label(root, text="Select a directory to save to:").pack(pady=5)
    save_dir_var = tk.StringVar()

    dir_frame = tk.Frame(root)
    dir_frame.pack(pady=5)

    save_dir_entry = tk.Entry(dir_frame, textvariable=save_dir_var, width=40)
    save_dir_entry.pack(side='left')

    tk.Button(dir_frame, text="Browse", command=select_directory).pack(side='left', padx=5)

    # Buttons for Train and Extra Function
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="Train Model", command=train_model).pack(side='left', padx=10)
    tk.Button(button_frame, text="Extra Button", command=extra_function).pack(side='left', padx=10)

    # Run the GUI loop
    root.mainloop()