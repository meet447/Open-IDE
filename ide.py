import os
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import re
import customtkinter as ctk

ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

# Set up the main window
root = ctk.CTk()
root.title("Open IDE")
root.geometry("800x600")
root.configure(bg="#1e1e1e")

# Create a ttk Notebook widget
notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# Create a frame for the code editor
code_frame = ctk.CTkFrame(notebook)
notebook.add(code_frame, text="Code Editor")

# Create a Text widget for code editing
code_editor = scrolledtext.ScrolledText(code_frame, bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4")
code_editor.pack(fill=tk.BOTH, expand=True)

# Configure tags for syntax highlighting
code_editor.tag_configure("keyword", foreground="#569CD6")
code_editor.tag_configure("comment", foreground="#57A64A")

# Create a frame for the file explorer
file_frame = ctk.CTkFrame(notebook)
notebook.add(file_frame, text="File Explorer")

# Create a Treeview widget for the file explorer
file_tree = ttk.Treeview(file_frame)
file_tree.pack(fill=tk.BOTH, expand=True)

# Set up the file tree columns
file_tree["columns"] = ("Type")
file_tree.column("#0", width=200, minwidth=200)
file_tree.column("Type", width=80, minwidth=80)

# Add headers to the file tree columns
file_tree.heading("#0", text="Name", anchor=tk.W)
file_tree.heading("Type", text="Type", anchor=tk.W)

# Create a frame for the variable window
variable_frame = ctk.CTkFrame(notebook)
notebook.add(variable_frame, text="Variables")

# Create a Treeview widget for displaying variables
variable_tree = ttk.Treeview(variable_frame)
variable_tree.pack(fill=tk.BOTH, expand=True)

# Set up the variable tree columns
variable_tree["columns"] = ("Value")
variable_tree.column("#0", width=200, minwidth=200)
variable_tree.column("Value", width=200, minwidth=200)

# Add headers to the variable tree columns
variable_tree.heading("#0", text="Variable", anchor=tk.W)
variable_tree.heading("Value", text="Value", anchor=tk.W)

# Function to populate the file tree
def populate_file_tree():
    current_directory = os.getcwd()
    file_tree.delete(*file_tree.get_children())
    items = os.listdir(current_directory)
    for item in items:
        item_path = os.path.join(current_directory, item)
        item_type = "folder" if os.path.isdir(item_path) else "file"
        item_id = file_tree.insert("", "end", text=item, values=(item_type))
        if item_type == "folder":
            populate_file_tree_helper(item_path, item_id)


def populate_file_tree_helper(path, parent=""):
    items = os.listdir(path)
    for item in items:
        item_path = os.path.join(path, item)
        item_type = "folder" if os.path.isdir(item_path) else "file"
        item_id = file_tree.insert(parent, "end", text=item, values=(item_type))
        if item_type == "folder":
            populate_file_tree_helper(item_path, item_id)


# Function to handle directory change
def change_directory():
    new_directory = filedialog.askdirectory()
    if new_directory:
        os.chdir(new_directory)
        populate_file_tree()


# Function to handle file saving
def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".py")
    if file_path:
        with open(file_path, "w") as file:
            file.write(code_editor.get("1.0", tk.END))
            tk.messagebox.showinfo("Save", "File saved successfully.")


# Function to handle file opening
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, "r") as file:
            code_editor.delete("1.0", tk.END)
            code_editor.insert(tk.END, file.read())


# Function to handle running the code
def run_code():
    code = code_editor.get("1.0", tk.END)
    code_output = run_python_code(code)
    output_window.delete("1.0", tk.END)
    if code_output is not None:
        if code_output.startswith("SyntaxError:") or code_output.startswith("IndentationError:"):
            messagebox.showerror("Error", code_output)
        else:
            output_window.insert(tk.END, code_output)
            notebook.select(output_frame)  # Redirect to the output window


def run_python_code(code):
    with open("temp_script.py", "w") as file:
        file.write(code)
    try:
        result = subprocess.run(["python", "temp_script.py"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return result.stderr
    except Exception as e:
        return str(e)
    finally:
        os.remove("temp_script.py")


# Function to handle opening files from the file explorer
def open_file_from_explorer(event):
    selected_item = file_tree.selection()
    if selected_item:
        item_path = file_tree.item(selected_item)["text"]
        if os.path.isfile(item_path):
            with open(item_path, "r") as file:
                code_editor.delete("1.0", tk.END)
                code_editor.insert(tk.END, file.read())
            notebook.select(code_frame)  # Redirect to the code editor window


# Bind double-click event to open_file_from_explorer function
file_tree.bind("<Double-1>", open_file_from_explorer)

# Create a frame for the app bar
app_bar_frame = ctk.CTkFrame(root)
app_bar_frame.pack(fill=tk.X)

# Create a button to change directory
change_dir_button = ctk.CTkButton(app_bar_frame, text="Change Directory", command=change_directory)
change_dir_button.pack(side=tk.LEFT, padx=10, pady=5)

# Create a button to save file
save_button = ctk.CTkButton(app_bar_frame, text="Save", command=save_file)
save_button.pack(side=tk.LEFT, padx=10, pady=5)

# Create a button to open file
open_button = ctk.CTkButton(app_bar_frame, text="Open", command=open_file)
open_button.pack(side=tk.LEFT, padx=10, pady=5)

# Create a button to run code
run_button = ctk.CTkButton(app_bar_frame, text="Run", command=run_code)
run_button.pack(side=tk.LEFT, padx=10, pady=5)

# Create a frame for the output window
output_frame = ctk.CTkFrame(notebook)
notebook.add(output_frame, text="Output")

# Create a Text widget for displaying output
output_window = scrolledtext.ScrolledText(output_frame, bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4")
output_window.pack(fill=tk.BOTH, expand=True)

# Predefined list of keywords for autocomplete
keywords = [
    "if", "else", "for", "while", "def", "class", "import", "from", "return", "print",
    "and", "or", "not", "in", "is", "pass", "break", "continue", "try", "except",
    "finally", "raise", "assert", "with", "global", "nonlocal", "True", "False"
]


# Create a Completion class for autocomplete suggestions
class Completion:
    def __init__(self, start, suggestions):
        self.start = start
        self.suggestions = suggestions


# Create a list of Completion objects for autocomplete
completions = [Completion(keyword, [keyword]) for keyword in keywords]


# Function to handle autocomplete
def autocomplete(event):
    current_line = code_editor.get("insert linestart", "insert")
    current_word = re.search(r"\w*$", current_line).group(0)
    if current_word:
        suggestions = [completion.suggestions[0] for completion in completions if
                       completion.start.startswith(current_word)]
        if suggestions:
            unique_suggestions = list(set(suggestions))
            unique_suggestions.sort()
            code_editor.delete("insert - {} chars".format(len(current_word)), "insert")
            code_editor.insert("insert", unique_suggestions[0])


# Bind key press event to autocomplete function
code_editor.bind("<Shift_L>", autocomplete)


# Function to handle changing text size
def change_text_size():
    text_size = size_var.get()
    code_editor.configure(font=("Courier", text_size))


# Create a label for text size
size_label = ctk.CTkLabel(app_bar_frame, text="Text Size:")
size_label.pack(side=tk.LEFT, padx=10, pady=5)

# Create a variable to store text size
size_var = ctk.IntVar(value=16)

# Create a spinbox for text size
size_spinbox = tk.Spinbox(app_bar_frame, from_=8, to=24, increment=2, textvariable=size_var, width=4,
                          command=change_text_size)
size_spinbox.pack(side=tk.LEFT, padx=0, pady=5)


def apply_syntax_highlighting(event):
    # Remove previous tags
    code_editor.tag_remove("keyword", "1.0", tk.END)
    code_editor.tag_remove("comment", "1.0", tk.END)

    # Get the current code content
    code = code_editor.get("1.0", tk.END)

    # Define the list of keywords
    keywords = [
        "if", "else", "for", "while", "def", "class", "import", "from", "return", "print",
        "and", "or", "not", "in", "is", "pass", "break", "continue", "try", "except",
        "finally", "raise", "assert", "with", "global", "nonlocal"
    ]
    # Apply syntax highlighting to keywords
    for keyword in keywords:
        start = "1.0"
        while True:
            start = code_editor.search(keyword, start, stopindex=tk.END)
            if not start:
                break
            end = f"{start}+{len(keyword)}c"
            code_editor.tag_add("keyword", start, end)
            start = end

    # Apply syntax highlighting to comments (using '#' as an example)
    start = "1.0"
    while True:
        start = code_editor.search("#", start, stopindex=tk.END)
        if not start:
            break
        end = code_editor.search("\n", start, stopindex=tk.END)
        if not end:
            end = ctk.END
        code_editor.tag_add("comment", start, end)
        start = end


# Bind key release event to apply_syntax_highlighting function
code_editor.bind("<KeyRelease>", apply_syntax_highlighting)


def handle_enter(event):
    current_line = code_editor.get("insert linestart", "insert")
    if current_line.endswith(":"):
        code_editor.insert("insert", "\n    ")  # Insert a new line with indentation
        return "break"  # Prevent the default behavior of Enter key press


def retrieve_variables():
    code = code_editor.get("1.0", tk.END)

    # Create a new local scope for executing the code
    local_vars = {}
    global_vars = {}

    try:
        exec(code, global_vars, local_vars)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

    # Clear existing items from the variable tree
    variable_tree.delete(*variable_tree.get_children())

    # Populate the variable tree with variables and their values
    for name, value in local_vars.items():
        if not name.startswith("__") and not callable(value):
            variable_tree.insert("", tk.END, text=name, values=(repr(value),))


# Create a button to retrieve variables
retrieve_variables_button = ctk.CTkButton(app_bar_frame, text="Retrieve Variables", command=retrieve_variables)
retrieve_variables_button.pack(side=tk.LEFT, padx=10, pady=5)



# Bind Enter key press event to handle_enter function
code_editor.bind("<Return>", handle_enter)

# Run the Tkinter event loop
root.mainloop()
