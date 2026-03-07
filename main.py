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
        self.success_color = "#4ec9b0" # Green for feedback

        # Window State & Config
        self.config_file = os.path.join(os.path.dirname(__file__), "config.json")
        self.config = self.load_config()

        self.side = self.config.get("side", "Right")
        self.expanded_size = 300
        self.collapsed_size = 10
        self.is_expanded = True
        self.pin_var = tk.BooleanVar(value=False)
        self.collapse_job = None
        self.tooltip_win = None

        self.snippets_file = os.path.join(os.path.dirname(__file__), "snippets.json")
        self.custom_snippets = self.load_custom_snippets()

        # All snippets by tab for search in content
        self.all_snippets = {}

        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.configure(bg=self.bg_color)

        self.root.bind("<Enter>", self.on_enter)
        self.root.bind("<Leave>", self.on_leave)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.content_frame = tk.Frame(root, bg=self.bg_color)
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(3, weight=1)

        header_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)

        tk.Label(header_frame, text="CodeSidebar", font=("Segoe UI", 14, "bold"),
                 bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, padx=10, sticky="w")

        tk.Button(header_frame, text="✕", command=root.quit, bg=self.bg_color, fg=self.fg_color,
                  relief="flat", font=("Segoe UI", 10)).grid(row=0, column=1, padx=5, sticky="e")

        controls_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=2)

        tk.Checkbutton(controls_frame, text="Pin", variable=self.pin_var,
                       bg=self.bg_color, fg=self.fg_color,
                       selectcolor=self.btn_color, activebackground=self.bg_color,
                       activeforeground=self.fg_color, font=("Segoe UI", 8)).pack(side="left")

        self.side_var = tk.StringVar(value=self.side)
        side_menu = ttk.Combobox(controls_frame, textvariable=self.side_var, values=["Left", "Right", "Top", "Bottom"],
                                 width=7, state="readonly", font=("Segoe UI", 8))
        side_menu.pack(side="left", padx=5)
        side_menu.bind("<<ComboboxSelected>>", self.change_side)

        tk.Button(controls_frame, text="+ Add", command=self.open_add_snippet_window,
                  bg=self.accent_color, fg=self.fg_color, relief="flat", padx=5,
                  font=("Segoe UI", 8, "bold")).pack(side="right")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_snippets)
        search_entry = tk.Entry(self.content_frame, textvariable=self.search_var, bg=self.btn_color,
                                fg=self.fg_color, insertbackground="white", borderwidth=0)
        search_entry.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.btn_color, foreground=self.fg_color, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", self.accent_color)])

        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.grid(row=3, column=0, sticky="nsew", padx=2, pady=(5, 0))

        self.tab_frames = {} # tab_name -> scroll_frame
        self.buttons = []    # (btn, label, code, tab_name)
        self.create_tab("HTML", self.get_html_snippets())
        self.create_tab("JS", self.get_js_snippets())
        self.create_tab("CSS", self.get_css_snippets())
        self.create_tab("Python", self.get_python_snippets())
        self.create_tab("SQL", self.get_sql_snippets())
        self.create_tab("TS", self.get_ts_snippets())
        self.create_tab("Custom", self.custom_snippets)

        self.vignette = tk.Frame(root, bg=self.accent_color)
        self.update_geometry()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f: return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showwarning("Config Error", f"Could not load config:\n{e}")
                return {}
        return {}

    def save_config(self):
        self.config["side"] = self.side
        with open(self.config_file, 'w') as f: json.dump(self.config, f)

    def change_side(self, event):
        self.side = self.side_var.get()
        self.save_config()
        # Redraw snippets for new layout orientation
        for tab_name, frame in self.tab_frames.items():
            for widget in frame.winfo_children(): widget.destroy()
        self.buttons = []
        self.render_snippets(self.tab_frames["HTML"], self.get_html_snippets(), "HTML")
        self.render_snippets(self.tab_frames["JS"], self.get_js_snippets(), "JS")
        self.render_snippets(self.tab_frames["CSS"], self.get_css_snippets(), "CSS")
        self.render_snippets(self.tab_frames["Python"], self.get_python_snippets(), "Python")
        self.render_snippets(self.tab_frames["SQL"], self.get_sql_snippets(), "SQL")
        self.render_snippets(self.tab_frames["TS"], self.get_ts_snippets(), "TS")
        self.render_snippets(self.tab_frames["Custom"], self.custom_snippets, "Custom")
        self.update_geometry()

    def update_geometry(self, collapsed=False):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        size = self.collapsed_size if collapsed else self.expanded_size
        if self.side == "Right": geom = f"{size}x700+{sw - size}+50"
        elif self.side == "Left": geom = f"{size}x700+0+50"
        elif self.side == "Top": geom = f"{sw}x{size}+0+0"
        elif self.side == "Bottom": geom = f"{sw}x{size}+0+{sh - size}"
        self.root.geometry(geom)

    def on_enter(self, event):
        if self.collapse_job: self.root.after_cancel(self.collapse_job); self.collapse_job = None
        if not self.is_expanded: self.expand()

    def on_leave(self, event):
        if not self.pin_var.get(): self.collapse_job = self.root.after(500, self.collapse)

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
        was_pinned = self.pin_var.get(); self.pin_var.set(True)
        add_win = tk.Toplevel(self.root)
        add_win.title("Add Snippet")
        add_win.geometry("350x300")
        add_win.configure(bg=self.bg_color)
        add_win.attributes('-topmost', True)
        def on_close(): self.pin_var.set(was_pinned); add_win.destroy(); self.on_leave(None)
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
        
        # Adjust scroll content width based on orientation
        canvas_width = 1200 if self.side in ["Top", "Bottom"] else 280
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=canvas_width) 
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tab_frames[name] = scroll_frame
        self.render_snippets(scroll_frame, snippets, name)
        return scroll_frame

    def render_snippets(self, parent, snippets, tab_name=""):
        self.all_snippets[tab_name] = snippets
        if self.side in ["Top", "Bottom"]:
            cols = 4
            for i, (label, code) in enumerate(snippets):
                btn = tk.Button(parent, text=label, command=lambda c=code: self.paste_snippet(c),
                                bg=self.btn_color, fg=self.fg_color, relief="flat",
                                padx=10, pady=8, anchor="w", font=("Segoe UI", 10))
                btn.grid(row=i // cols, column=i % cols, sticky="ew", padx=5, pady=5)
                parent.grid_columnconfigure(i % cols, weight=1)
                btn.bind("<Enter>", lambda e, c=code: self.show_tooltip(e, c))
                btn.bind("<Leave>", lambda e: self.hide_tooltip())
                if tab_name == "Custom":
                    btn.bind("<Button-3>", lambda e, l=label, c=code, b=btn: self.show_context_menu(e, l, c, b))
                self.buttons.append((btn, label, code, tab_name))
        else:
            for label, code in snippets:
                btn = tk.Button(parent, text=label, command=lambda c=code: self.paste_snippet(c),
                                bg=self.btn_color, fg=self.fg_color, relief="flat",
                                padx=10, pady=8, anchor="w", font=("Segoe UI", 10))
                btn.pack(fill="x", pady=1, padx=2)
                btn.bind("<Enter>", lambda e, c=code: self.show_tooltip(e, c))
                btn.bind("<Leave>", lambda e: self.hide_tooltip())
                if tab_name == "Custom":
                    btn.bind("<Button-3>", lambda e, l=label, c=code, b=btn: self.show_context_menu(e, l, c, b))
                self.buttons.append((btn, label, code, tab_name))

    def filter_snippets(self, *args):
        query = self.search_var.get().lower()
        for btn, label, code, tab_name in self.buttons:
            match = query in label.lower() or query in code.lower()
            if match:
                if self.side in ["Top", "Bottom"]: btn.grid()
                else: btn.pack(fill="x", pady=1, padx=2)
            else:
                if self.side in ["Top", "Bottom"]: btn.grid_remove()
                else: btn.pack_forget()

    def paste_snippet(self, text):
        try:
            pyperclip.copy(text)
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.15)
            pyautogui.hotkey('ctrl', 'v')
            self.show_feedback("Pasted!")
        except Exception as e:
            self.show_feedback(f"Error: {e}", error=True)

    def show_feedback(self, msg, error=False):
        color = "#f44747" if error else self.success_color
        feedback = tk.Toplevel(self.root)
        feedback.overrideredirect(True)
        feedback.attributes('-topmost', True)
        x = self.root.winfo_x() + self.root.winfo_width() // 2 - 60
        y = self.root.winfo_y() + self.root.winfo_height() - 40
        feedback.geometry(f"120x28+{x}+{y}")
        tk.Label(feedback, text=msg, bg=color, fg="white", font=("Segoe UI", 9, "bold")).pack(expand=True, fill="both")
        feedback.after(800, feedback.destroy)

    def show_tooltip(self, event, code):
        self.hide_tooltip()
        x = event.widget.winfo_rootx() - 250
        y = event.widget.winfo_rooty()
        if x < 0:
            x = event.widget.winfo_rootx() + event.widget.winfo_width() + 5
        self.tooltip_win = tk.Toplevel(self.root)
        self.tooltip_win.overrideredirect(True)
        self.tooltip_win.attributes('-topmost', True)
        preview = code[:300] + ("..." if len(code) > 300 else "")
        self.tooltip_win.geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_win, text=preview, justify="left", bg="#2d2d2d", fg="#d4d4d4",
                         font=("Consolas", 9), padx=8, pady=6, wraplength=240, relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self):
        if self.tooltip_win:
            self.tooltip_win.destroy()
            self.tooltip_win = None

    def show_context_menu(self, event, label, code, btn):
        menu = tk.Menu(self.root, tearoff=0, bg=self.btn_color, fg=self.fg_color,
                       activebackground=self.accent_color, activeforeground=self.fg_color)
        menu.add_command(label="Edit", command=lambda: self.edit_snippet(label, code))
        menu.add_command(label="Delete", command=lambda: self.delete_snippet(label, btn))
        menu.tk_popup(event.x_root, event.y_root)

    def edit_snippet(self, old_name, old_code):
        was_pinned = self.pin_var.get(); self.pin_var.set(True)
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Snippet")
        edit_win.geometry("350x300")
        edit_win.configure(bg=self.bg_color)
        edit_win.attributes('-topmost', True)
        def on_close(): self.pin_var.set(was_pinned); edit_win.destroy(); self.on_leave(None)
        edit_win.protocol("WM_DELETE_WINDOW", on_close)
        tk.Label(edit_win, text="Name:", bg=self.bg_color, fg=self.fg_color).pack(pady=(15, 2), padx=15, anchor="w")
        name_entry = tk.Entry(edit_win, bg=self.btn_color, fg=self.fg_color, borderwidth=0, insertbackground="white")
        name_entry.pack(fill="x", padx=15, pady=5)
        name_entry.insert(0, old_name)
        tk.Label(edit_win, text="Code:", bg=self.bg_color, fg=self.fg_color).pack(pady=(10, 2), padx=15, anchor="w")
        code_text = tk.Text(edit_win, bg=self.btn_color, fg=self.fg_color, borderwidth=0, height=6, font=("Consolas", 10), insertbackground="white")
        code_text.pack(fill="both", padx=15, pady=5, expand=True)
        code_text.insert("1.0", old_code)
        def save_edit():
            new_name = name_entry.get().strip()
            new_code = code_text.get("1.0", tk.END).strip()
            if not new_name or not new_code: return
            for i, (n, c) in enumerate(self.custom_snippets):
                if n == old_name and c == old_code:
                    self.custom_snippets[i] = (new_name, new_code)
                    break
            self._save_and_refresh_custom()
            on_close()
        tk.Button(edit_win, text="Save", command=save_edit,
                  bg=self.accent_color, fg=self.fg_color, relief="flat", pady=8, font=("Segoe UI", 10, "bold")).pack(fill="x", padx=15, pady=15)

    def delete_snippet(self, label, btn):
        if not messagebox.askyesno("Delete Snippet", f"Delete '{label}'?"): return
        self.custom_snippets = [(n, c) for n, c in self.custom_snippets if n != label]
        self._save_and_refresh_custom()

    def _save_and_refresh_custom(self):
        try:
            with open(self.snippets_file, 'w') as f: json.dump(self.custom_snippets, f)
        except IOError as e:
            messagebox.showerror("Save Error", f"Could not save snippets:\n{e}")
            return
        # Refresh custom tab
        parent = self.tab_frames["Custom"]
        for widget in parent.winfo_children(): widget.destroy()
        self.buttons = [(b, l, c, t) for b, l, c, t in self.buttons if t != "Custom"]
        self.render_snippets(parent, self.custom_snippets, "Custom")

    def load_custom_snippets(self):
        if os.path.exists(self.snippets_file):
            try:
                with open(self.snippets_file, 'r') as f: return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showwarning("Snippets Error", f"Could not load snippets:\n{e}")
                return []
        return []

    def save_new_snippet(self, name, code, window, close_callback):
        if not name or not code: return
        self.custom_snippets.append((name, code))
        self._save_and_refresh_custom()
        close_callback()

    def get_html_snippets(self):
        return [("Boilerplate", "<!DOCTYPE html>\n<html>\n<head>\n<title></title>\n</head>\n<body>\n\n</body>\n</html>"), ("Div Container", '<div class="container">\n\n</div>'), ("Flex Row", '<div style="display: flex; flex-direction: row;">\n\n</div>'), ("Input Field", '<input type="text" placeholder="">'), ("Submit Button", '<button type="submit">Submit</button>'), ("Image Link", '<img src="" alt="">'), ("List (UL)", "<ul>\n  <li></li>\n</ul>"), ("Table", "<table>\n  <tr><td></td></tr>\n</table>"), ("Form", '<form>\n  <input type="text">\n  <button>Go</button>\n</form>'), ("Style Tag", "<style>\n\n</style>"), ("Script Tag", "<script>\n\n</script>")]
    def get_js_snippets(self):
        return [("Console Log", "console.log();"), ("Async Func", "async function name() {\n  try {\n    \n  } catch (err) {}\n}"), ("Arrow Func", "const name = () => {\n  \n};"), ("Event Listener", 'addEventListener("click", (e) => {});'), ("Map Array", "const newArr = arr.map(item => item);"), ("Fetch API", "const res = await fetch(url);\nconst data = await res.json();"), ("Local Storage Set", "localStorage.setItem('key', JSON.stringify(data));"), ("JSON Parse", "JSON.parse(data);"), ("Query Selector", "document.querySelector('');"), ("Set Timeout", "setTimeout(() => {}, 1000);"), ("React Component", "const App = () => {\n  return <div></div>;\n};")]
    def get_css_snippets(self):
        return [("Flex Center", "display: flex;\njustify-content: center;\nalign-items: center;"), ("Grid Layout", "display: grid;\ngrid-template-columns: repeat(3, 1fr);"), ("Box Shadow", "box-shadow: 0 4px 6px rgba(0,0,0,0.1);"), ("Reset CSS", "* {\n  margin: 0;\n  padding: 0;\n  box-sizing: border-box;\n}"), ("Responsive Query", "@media (max-width: 768px) {\n\n}"), ("Transition", "transition: all 0.3s ease;"), ("Border Radius", "border-radius: 8px;"), ("Hover State", "&:hover {\n  opacity: 0.8;\n}")]

    def get_python_snippets(self):
        return [
            ("Main Block", 'if __name__ == "__main__":\n    main()'),
            ("Function", "def func_name(param):\n    pass"),
            ("Class", "class MyClass:\n    def __init__(self):\n        pass"),
            ("List Comprehension", "[x for x in iterable if condition]"),
            ("Try/Except", "try:\n    pass\nexcept Exception as e:\n    print(e)"),
            ("With Open", 'with open("file.txt", "r") as f:\n    data = f.read()'),
            ("Lambda", "fn = lambda x: x"),
            ("Dict Comprehension", "{k: v for k, v in iterable}"),
            ("Decorator", "def decorator(func):\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs)\n    return wrapper"),
            ("Dataclass", "from dataclasses import dataclass\n\n@dataclass\nclass Item:\n    name: str\n    value: int = 0"),
        ]

    def get_sql_snippets(self):
        return [
            ("SELECT", "SELECT * FROM table_name WHERE condition;"),
            ("INSERT", "INSERT INTO table_name (col1, col2) VALUES (val1, val2);"),
            ("UPDATE", "UPDATE table_name SET col1 = val1 WHERE condition;"),
            ("DELETE", "DELETE FROM table_name WHERE condition;"),
            ("CREATE TABLE", "CREATE TABLE table_name (\n  id INT PRIMARY KEY,\n  name VARCHAR(255)\n);"),
            ("JOIN", "SELECT a.*, b.*\nFROM table_a a\nINNER JOIN table_b b ON a.id = b.a_id;"),
            ("GROUP BY", "SELECT col, COUNT(*)\nFROM table_name\nGROUP BY col\nHAVING COUNT(*) > 1;"),
            ("Subquery", "SELECT * FROM table_name\nWHERE col IN (SELECT col FROM other_table);"),
        ]

    def get_ts_snippets(self):
        return [
            ("Interface", "interface IName {\n  key: string;\n  value: number;\n}"),
            ("Type Alias", "type Name = {\n  key: string;\n  value: number;\n};"),
            ("Enum", "enum Status {\n  Active = 'ACTIVE',\n  Inactive = 'INACTIVE',\n}"),
            ("Generic Func", "function identity<T>(arg: T): T {\n  return arg;\n}"),
            ("Optional Props", "interface Props {\n  required: string;\n  optional?: number;\n}"),
            ("React FC", "const Component: React.FC<Props> = ({ prop }) => {\n  return <div>{prop}</div>;\n};"),
            ("useState", "const [state, setState] = useState<Type>(initial);"),
            ("useEffect", "useEffect(() => {\n  // effect\n  return () => {\n    // cleanup\n  };\n}, [deps]);"),
        ]

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeSidebar(root)
    root.mainloop()
