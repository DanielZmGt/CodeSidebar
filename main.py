import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import pyautogui
import time
import json
import os

class CodeSidebar:
    def __init__(self, root):
        self.root = root
        self.root.title("CodeSidebar")
        
        # --- UI Styling & Colors ---
        self.bg_color = "#1e1e1e"      # VS Code dark gray
        self.fg_color = "#ffffff"      # White text
        self.accent_color = "#007acc"  # VS Code blue
        self.btn_color = "#333333"     # Darker gray for buttons
        
        # Window State & Config
        self.config_file = os.path.join(os.path.dirname(__file__), "config.json")
        self.config = self.load_config()
        
        self.side = self.config.get("side", "Right") # Left, Right, Top, Bottom
        self.expanded_size = 300
        self.collapsed_size = 10
        self.is_expanded = True
        self.pin_var = tk.BooleanVar(value=False)
        self.collapse_job = None
        
        # Path for custom snippets
        self.snippets_file = os.path.join(os.path.dirname(__file__), "snippets.json")
        self.custom_snippets = self.load_custom_snippets()
        
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.configure(bg=self.bg_color)
        
        # Events
        self.root.bind("<Enter>", self.on_enter)
        self.root.bind("<Leave>", self.on_leave)

        # Main Layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # --- Content Frame ---
        self.content_frame = tk.Frame(root, bg=self.bg_color)
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(3, weight=1)

        # --- Header & Close ---
        header_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)

        tk.Label(header_frame, text="CodeSidebar", font=("Segoe UI", 14, "bold"), 
                 bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, padx=10, sticky="w")
        
        tk.Button(header_frame, text="✕", command=root.quit, bg=self.bg_color, fg=self.fg_color,
                  relief="flat", font=("Segoe UI", 10)).grid(row=0, column=1, padx=5, sticky="e")

        # --- Controls (Pin, Side, Add) ---
        controls_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=2)
        
        tk.Checkbutton(controls_frame, text="Pin", variable=self.pin_var,
                       bg=self.bg_color, fg=self.fg_color,
                       selectcolor=self.btn_color, activebackground=self.bg_color,
                       activeforeground=self.fg_color, font=("Segoe UI", 8)).pack(side="left")

        # Side Selection
        self.side_var = tk.StringVar(value=self.side)
        side_menu = ttk.Combobox(controls_frame, textvariable=self.side_var, values=["Left", "Right", "Top", "Bottom"], 
                                 width=7, state="readonly", font=("Segoe UI", 8))
        side_menu.pack(side="left", padx=5)
        side_menu.bind("<<ComboboxSelected>>", self.change_side)

        tk.Button(controls_frame, text="+ Add", command=self.open_add_snippet_window,
                  bg=self.accent_color, fg=self.fg_color, relief="flat", padx=5,
                  font=("Segoe UI", 8, "bold")).pack(side="right")

        # --- Search Bar ---
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_snippets)
        search_entry = tk.Entry(self.content_frame, textvariable=self.search_var, bg=self.btn_color, 
                                fg=self.fg_color, insertbackground="white", borderwidth=0)
        search_entry.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        # --- Tabs ---
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.btn_color, foreground=self.fg_color, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", self.accent_color)])
        
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.grid(row=3, column=0, sticky="nsew", padx=2, pady=(5, 0))
        
        self.buttons = []
        self.create_tab("HTML", self.get_html_snippets())
        self.create_tab("JS", self.get_js_snippets())
        self.create_tab("CSS", self.get_css_snippets())
        self.custom_tab_frame = self.create_tab("Custom", self.custom_snippets)

        # Visual indicator
        self.vignette = tk.Frame(root, bg=self.accent_color)
        
        # Initial position
        self.update_geometry()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except: return {}
        return {}

    def save_config(self):
        self.config["side"] = self.side
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

    def change_side(self, event):
        self.side = self.side_var.get()
        self.save_config()
        self.update_geometry()

    def update_geometry(self, collapsed=False):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        
        size = self.collapsed_size if collapsed else self.expanded_size
        
        if self.side == "Right":
            geom = f"{size}x700+{sw - size}+50"
        elif self.side == "Left":
            geom = f"{size}x700+0+50"
        elif self.side == "Top":
            geom = f"{sw}x{size}+0+0"
        elif self.side == "Bottom":
            geom = f"{sw}x{size}+0+{sh - size}"
            
        self.root.geometry(geom)

    def on_enter(self, event):
        if self.collapse_job:
            self.root.after_cancel(self.collapse_job)
            self.collapse_job = None
        if not self.is_expanded:
            self.expand()

    def on_leave(self, event):
        if not self.pin_var.get():
            self.collapse_job = self.root.after(500, self.collapse)

    def expand(self):
        self.update_geometry(collapsed=False)
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.vignette.grid_forget()
        self.is_expanded = True

    def collapse(self):
        x, y = self.root.winfo_pointerxy()
        widget = self.root.winfo_containing(x, y)
        if widget and str(widget).startswith(str(self.root)): return

        self.update_geometry(collapsed=True)
        self.content_frame.grid_forget()
        self.vignette.grid(row=0, column=0, sticky="nsew")
        self.is_expanded = False

    def open_add_snippet_window(self):
        was_pinned = self.pin_var.get()
        self.pin_var.set(True)
        add_win = tk.Toplevel(self.root)
        add_win.title("Add Snippet")
        add_win.geometry("350x300")
        add_win.configure(bg=self.bg_color)
        add_win.attributes('-topmost', True)
        
        def on_close():
            self.pin_var.set(was_pinned)
            add_win.destroy()
            self.on_leave(None)

        add_win.protocol("WM_DELETE_WINDOW", on_close)
        tk.Label(add_win, text="Name:", bg=self.bg_color, fg=self.fg_color).pack(pady=(15, 2), padx=15, anchor="w")
        name_entry = tk.Entry(add_win, bg=self.btn_color, fg=self.fg_color, borderwidth=0, insertbackground="white")
        name_entry.pack(fill="x", padx=15, pady=5)
        tk.Label(add_win, text="Code:", bg=self.bg_color, fg=self.fg_color).pack(pady=(10, 2), padx=15, anchor="w")
        code_text = tk.Text(add_win, bg=self.btn_color, fg=self.fg_color, borderwidth=0, height=6, font=("Consolas", 10), insertbackground="white")
        code_text.pack(fill="both", padx=15, pady=5, expand=True)
        tk.Button(add_win, text="Save", command=lambda: self.save_new_snippet(name_entry.get().strip(), code_text.get("1.0", tk.END).strip(), add_win, on_close),
                  bg=self.accent_color, fg=self.fg_color, relief="flat", pady=8, font=("Segoe UI", 10, "bold")).pack(fill="x", padx=15, pady=15)

    def create_tab(self, name, snippets):
        frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text=name)
        canvas = tk.Canvas(frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.bg_color)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=280) 
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.render_snippets(scroll_frame, snippets)
        return scroll_frame

    def render_snippets(self, parent, snippets):
        for label, code in snippets:
            btn = tk.Button(parent, text=label, command=lambda c=code: self.paste_snippet(c),
                            bg=self.btn_color, fg=self.fg_color, relief="flat", 
                            padx=10, pady=8, anchor="w", font=("Segoe UI", 10))
            btn.pack(fill="x", pady=1, padx=2)
            self.buttons.append((btn, label))

    def filter_snippets(self, *args):
        query = self.search_var.get().lower()
        for btn, label in self.buttons:
            if query in label.lower(): btn.pack(fill="x", pady=1, padx=2)
            else: btn.pack_forget()

    def paste_snippet(self, text):
        try:
            pyperclip.copy(text)
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.15)
            pyautogui.hotkey('ctrl', 'v')
        except: pass

    def load_custom_snippets(self):
        if os.path.exists(self.snippets_file):
            try:
                with open(self.snippets_file, 'r') as f: return json.load(f)
            except: return []
        return []

    def save_new_snippet(self, name, code, window, close_callback):
        if not name or not code: return
        self.custom_snippets.append((name, code))
        try:
            with open(self.snippets_file, 'w') as f: json.dump(self.custom_snippets, f)
            btn = tk.Button(self.custom_tab_frame, text=name, command=lambda c=code: self.paste_snippet(c),
                            bg=self.btn_color, fg=self.fg_color, relief="flat", padx=10, pady=8, anchor="w", font=("Segoe UI", 10))
            btn.pack(fill="x", pady=1, padx=2)
            self.buttons.append((btn, name))
            close_callback()
        except: pass

    def get_html_snippets(self):
        return [("Boilerplate", "<!DOCTYPE html>\n<html>\n<head>\n<title></title>\n</head>\n<body>\n\n</body>\n</html>"), ("Div", '<div class="container">\n\n</div>'), ("Flex Row", '<div style="display: flex;">\n\n</div>')]

    def get_js_snippets(self):
        return [("Console Log", "console.log();"), ("Async Func", "async function name() {\n\n}"), ("Arrow Func", "const name = () => {\n\n};")]

    def get_css_snippets(self):
        return [("Flex Center", "display: flex;\njustify-content: center;\nalign-items: center;"), ("Grid", "display: grid;\ngrid-template-columns: repeat(3, 1fr);")]

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeSidebar(root)
    root.mainloop()