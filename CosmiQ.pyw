import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import importlib.metadata
import sys
import time

# List of vital libraries (mark these as crucial)
vital_libraries = [
    'tkinter',
    'subprocess',
    'importlib.metadata',
    'setuptools',
]

# Function to check if a library is installed
def is_library_installed(lib_name):
    try:
        importlib.metadata.distribution(lib_name)
        return True
    except importlib.metadata.PackageNotFoundError:
        return False

# Function to install a library
def install_library(lib_name, output_text):
    if is_library_installed(lib_name):
        output_text.set(f"{lib_name} is already installed.")
    else:
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "install", lib_name], capture_output=True, text=True)
            if result.returncode == 0:
                output_text.set(f"Installation of {lib_name} successful.")
            else:
                output_text.set(f"{lib_name} does not exist.")
        except Exception as e:
            output_text.set(f"Error installing {lib_name}: {e}")

# Function to show loading screen
def show_loading_screen(message):
    loading_screen = tk.Tk()
    loading_screen.title("Loading")
    loading_screen.geometry("300x100")
    loading_label = tk.Label(loading_screen, text=message)
    loading_label.pack(expand=True)
    loading_screen.update_idletasks()  # Ensure the loading screen is displayed
    time.sleep(1)  # Keep the loading screen visible for at least 1 second
    return loading_screen

# Function to hide loading screen
def hide_loading_screen(loading_screen):
    loading_screen.destroy()

# Function to refresh the list of installed libraries
def refresh_library_list():
    for widget in library_listbox.winfo_children():
        widget.destroy()

    installed_libraries = [dist.metadata['Name'] for dist in importlib.metadata.distributions()]
    
    for lib in installed_libraries:
        var = tk.BooleanVar()
        cb = tk.Checkbutton(library_listbox, text=f"{lib} {'*' if lib in vital_libraries else ''}", variable=var, command=update_buttons_state)
        cb.var = var
        library_checkboxes[cb] = lib
        cb.pack(anchor='w')

    update_buttons_state()

# Function to handle library actions (uninstall, reinstall, update)
def handle_library_action(action):
    selected_libraries = [lib for cb, lib in library_checkboxes.items() if cb.var.get()]

    if action == 'uninstall':
        for lib in selected_libraries:
            if lib in vital_libraries:
                messagebox.showerror("Error", f"{lib} is a vital library and cannot be uninstalled.")
                return
        
        loading_screen = show_loading_screen("Uninstalling libraries...")
        for lib in selected_libraries:
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", lib])
        refresh_library_list()
        hide_loading_screen(loading_screen)
        messagebox.showinfo("Info", "Selected libraries have been uninstalled.")

    elif action in ['reinstall', 'update']:
        loading_screen = show_loading_screen(f"{action.capitalize()}ing libraries...")
        for lib in selected_libraries:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade" if action == 'update' else "--force-reinstall", lib])
        refresh_library_list()
        hide_loading_screen(loading_screen)
        messagebox.showinfo("Info", f"Selected libraries have been {action}ed.")

# Function to open the add library window
def open_add_library_window():
    add_window = tk.Toplevel(root)
    add_window.title("Add Library")
    add_window.geometry("400x200")

    label = tk.Label(add_window, text="Library Name:")
    label.pack(pady=10)

    lib_name_entry = tk.Entry(add_window, width=40)
    lib_name_entry.pack(pady=10)

    output_text = tk.StringVar()
    output_label = tk.Label(add_window, textvariable=output_text)
    output_label.pack(pady=10)

    def install_and_update():
        lib_name = lib_name_entry.get().strip()
        if lib_name:
            output_text.set(f"Installing {lib_name}...")
            add_window.update()
            install_library(lib_name, output_text)
            lib_name_entry.delete(0, tk.END)
            refresh_library_list()

    install_button = tk.Button(add_window, text="Install", command=install_and_update)
    install_button.pack(pady=10)

# Function to handle mouse wheel scrolling
def on_mouse_wheel(event):
    canvas.yview_scroll(-1 * (event.delta // 120), "units")

# Function to update the state of the buttons based on checkbox selection
def update_buttons_state():
    selected = any(cb.var.get() for cb in library_checkboxes.keys())
    uninstall_button.config(state=tk.NORMAL if selected else tk.DISABLED)
    reinstall_button.config(state=tk.NORMAL if selected else tk.DISABLED)
    update_button.config(state=tk.NORMAL if selected else tk.DISABLED)

# Main application
root = tk.Tk()
root.withdraw()  # Hide the main window initially

# Show loading screen initially
loading_screen = show_loading_screen("Initializing...")

# Set up the main window
root.deiconify()  # Show the main window
root.title("CosmiQ")
root.geometry("500x720")

# Create a frame for the library listbox and scrollbar
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(main_frame)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

scrollable_frame = ttk.Frame(canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

library_listbox = scrollable_frame

# Bind mouse wheel event to scrollable frame
library_listbox.bind_all("<MouseWheel>", on_mouse_wheel)

library_checkboxes = {}

# Buttons frame
button_frame = tk.Frame(root)
button_frame.pack(fill=tk.X, pady=5)

uninstall_button = tk.Button(button_frame, text="Uninstall Selected", command=lambda: handle_library_action('uninstall'), state=tk.DISABLED)
uninstall_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

reinstall_button = tk.Button(button_frame, text="Reinstall Selected", command=lambda: handle_library_action('reinstall'), state=tk.DISABLED)
reinstall_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

update_button = tk.Button(button_frame, text="Update Selected", command=lambda: handle_library_action('update'), state=tk.DISABLED)
update_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

add_library_button = tk.Button(button_frame, text="Add Library", command=open_add_library_window)
add_library_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

# Refresh the library list on startup
refresh_library_list()

# Hide the loading screen after initialization
hide_loading_screen(loading_screen)

# Run the application
root.mainloop()
