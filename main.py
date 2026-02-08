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
        
        # Window State
        self.expanded_width = 300
        self.collapsed_width = 10
        self.is_expanded = True
        self.pin_var = tk.BooleanVar(value=False)
        self.collapse_job = None
        
        # Path for custom snippets
        self.snippets_file = os.path.join(os.path.dirname(__file__), "snippets.json")
        self.custom_snippets = self.load_custom_snippets()
        
        # Position window at top right
        screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.x_pos = screen_width - self.expanded_width
        
        self.root.geometry(f"{self.expanded_width}x700+{self.x_pos}+50")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True) # Remove title bar for cleaner "vignette" look
        self.root.configure(bg=self.bg_color)
        
        # Events
        self.root.bind("<Enter>", self.on_enter)
        self.root.bind("<Leave>", self.on_leave)

        # Layout - Ensure row 3 (notebook) expands
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(3, weight=1)

        # --- Content Frame (To hide when collapsed) ---
        self.content_frame = tk.Frame(root, bg=self.bg_color)
        self.content_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(3, weight=1)

        # --- Header ---
        header_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        header_frame.grid_columnconfigure(0, weight=1)

        tk.Label(header_frame, text="CodeSidebar", font=("Segoe UI", 16, "bold"), 
                 bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, padx=10)

        # --- Controls (Pin & Add) ---
        controls_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=2)
        
        tk.Checkbutton(controls_frame, text="Pin Open", variable=self.pin_var,
                       bg=self.bg_color, fg=self.fg_color,
                       selectcolor=self.btn_color, activebackground=self.bg_color,
                       activeforeground=self.fg_color, font=("Segoe UI", 9)).pack(side="left")

        tk.Button(controls_frame, text="+ Add Snippet", command=self.open_add_snippet_window,
                  bg=self.accent_color, fg=self.fg_color, relief="flat", padx=8,
                  font=("Segoe UI", 9, "bold")).pack(side="right")
        
        # Close Button (since we removed title bar)
        tk.Button(header_frame, text="✕", command=root.quit, bg=self.bg_color, fg=self.fg_color,
                  relief="flat", font=("Segoe UI", 10)).grid(row=0, column=1, padx=5, sticky="e")


        # --- Search Bar ---
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_snippets)
        search_entry = tk.Entry(self.content_frame, textvariable=self.search_var, bg=self.btn_color, 
                                fg=self.fg_color, insertbackground="white", borderwidth=0)
        search_entry.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        # --- Tabs (Notebook) ---
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

        # Visual indicator for collapsed state
        self.vignette = tk.Frame(root, bg=self.accent_color, width=self.collapsed_width)
        # It sits behind content, brought to front when collapsed

    def on_enter(self, event):
        if self.collapse_job:
            self.root.after_cancel(self.collapse_job)
            self.collapse_job = None
        
        if not self.is_expanded:
            self.expand()

    def on_leave(self, event):
        # Don't collapse if pinned or if opening a dialog/toplevel
        if not self.pin_var.get():
            # Add small delay to prevent flickering
            self.collapse_job = self.root.after(500, self.collapse)

    def expand(self):
        self.root.geometry(f"{self.expanded_width}x700+{self.root.winfo_screenwidth() - self.expanded_width}+50")
        self.content_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.vignette.grid_forget()
        self.is_expanded = True

    def collapse(self):
        # Check if mouse is really outside (sometimes Leave fires on child widgets)
        x, y = self.root.winfo_pointerxy()
        widget_under_mouse = self.root.winfo_containing(x, y)
        if widget_under_mouse is not None and str(widget_under_mouse).startswith(str(self.root)):
             return

        self.root.geometry(f"{self.collapsed_width}x700+{self.root.winfo_screenwidth() - self.collapsed_width}+50")
        self.content_frame.grid_forget()
        self.vignette.grid(row=0, column=0, sticky="nsew")
        self.is_expanded = False

    def open_add_snippet_window(self):
        # Pin temporarily while adding
        was_pinned = self.pin_var.get()
        self.pin_var.set(True)
        
        add_win = tk.Toplevel(self.root)
        add_win.title("Add New Snippet")
        add_win.geometry("350x300")
        add_win.configure(bg=self.bg_color)
        add_win.attributes('-topmost', True)
        
        # Restore pin state when closed
        def on_close():
            self.pin_var.set(was_pinned)
            add_win.destroy()
            self.on_leave(None) # Trigger check to collapse

        add_win.protocol("WM_DELETE_WINDOW", on_close)
        
        tk.Label(add_win, text="Snippet Name:", bg=self.bg_color, fg=self.fg_color).pack(pady=(15, 2), padx=15, anchor="w")
        name_entry = tk.Entry(add_win, bg=self.btn_color, fg=self.fg_color, borderwidth=0, insertbackground="white")
        name_entry.pack(fill="x", padx=15, pady=5)

        tk.Label(add_win, text="Code Content:", bg=self.bg_color, fg=self.fg_color).pack(pady=(10, 2), padx=15, anchor="w")
        code_text = tk.Text(add_win, bg=self.btn_color, fg=self.fg_color, borderwidth=0, height=6, font=("Consolas", 10), insertbackground="white")
        code_text.pack(fill="both", padx=15, pady=5, expand=True)

        save_btn = tk.Button(add_win, text="Save Snippet", 
                             command=lambda: self.save_new_snippet(name_entry.get().strip(), code_text.get("1.0", tk.END).strip(), add_win, on_close),
                             bg=self.accent_color, fg=self.fg_color, relief="flat", pady=8, font=("Segoe UI", 10, "bold"))
        save_btn.pack(fill="x", padx=15, pady=15)

    def create_tab(self, name, snippets):
        frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text=name)
        
        # Scrollable area
        canvas = tk.Canvas(frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.bg_color)
        
        # Ensure scroll_frame fills the canvas width
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
            if query in label.lower():
                btn.pack(fill="x", pady=1, padx=2)
            else:
                btn.pack_forget()

    def paste_snippet(self, text):
        try:
            pyperclip.copy(text)
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.15)
            pyautogui.hotkey('ctrl', 'v')
        except:
            pass

    def load_custom_snippets(self):
        if os.path.exists(self.snippets_file):
            try:
                with open(self.snippets_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_new_snippet(self, name, code, window, close_callback):
        if not name or not code:
            messagebox.showwarning("Warning", "Please provide both a name and code.", parent=window)
            return

        self.custom_snippets.append((name, code))
        
        try:
            with open(self.snippets_file, 'w') as f:
                json.dump(self.custom_snippets, f)
            
            # Add to UI immediately
            btn = tk.Button(self.custom_tab_frame, text=name, command=lambda c=code: self.paste_snippet(c),
                            bg=self.btn_color, fg=self.fg_color, relief="flat", 
                            padx=10, pady=8, anchor="w", font=("Segoe UI", 10))
            btn.pack(fill="x", pady=1, padx=2)
            self.buttons.append((btn, name))
            
            close_callback()
            messagebox.showinfo("Success", f"Snippet '{name}' added!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save snippet: {e}", parent=window)

    def get_html_snippets(self):
        return [
            ("Boilerplate", "<!DOCTYPE html>\n<html>\n<head>\n<title></title>\n</head>\n<body>\n\n</body>\n</html>"),
            ("Div Container", '<div class="container">\n\n</div>'),
            ("Flex Row", '<div style="display: flex; flex-direction: row;">\n\n</div>'),
            ("Input Field", '<input type="text" placeholder="">'),
            ("Submit Button", '<button type="submit">Submit</button>'),
            ("Image Link", '<img src="" alt="">'),
            ("List (UL)", "<ul>\n  <li></li>\n</ul>"),
            ("Table", "<table>\n  <tr><td></td></tr>\n</table>"),
            ("Form", '<form>\n  <input type="text">\n  <button>Go</button>\n</form>'),
            ("Style Tag", "<style>\n\n</style>"),
            ("Script Tag", "<script>\n\n</script>"),
        ]

    def get_js_snippets(self):
        return [
            ("Console Log", "console.log();"),
            ("Async Func", "async function name() {\n  try {\n    \n  } catch (err) {}\n}"),
            ("Arrow Func", "const name = () => {\n  \n};"),
            ("Event Listener", 'addEventListener("click", (e) => {});'),
            ("Map Array", "const newArr = arr.map(item => item);"),
            ("Fetch API", "const res = await fetch(url);\nconst data = await res.json();"),
            ("Local Storage Set", "localStorage.setItem('key', JSON.stringify(data));"),
            ("JSON Parse", "JSON.parse(data);"),
            ("Query Selector", "document.querySelector('');"),
            ("Set Timeout", "setTimeout(() => {}, 1000);"),
            ("React Component", "const App = () => {\n  return <div></div>;\n};"),
        ]

    def get_css_snippets(self):
        return [
            ("Flex Center", "display: flex;\njustify-content: center;\nalign-items: center;"),
            ("Grid Layout", "display: grid;\ngrid-template-columns: repeat(3, 1fr);"),
            ("Box Shadow", "box-shadow: 0 4px 6px rgba(0,0,0,0.1);"),
            ("Reset CSS", "* {\n  margin: 0;\n  padding: 0;\n  box-sizing: border-box;\n}"),
            ("Responsive Query", "@media (max-width: 768px) {\n\n}"),
            ("Transition", "transition: all 0.3s ease;"),
            ("Border Radius", "border-radius: 8px;"),
            ("Hover State", "&:hover {\n  opacity: 0.8;\n}"),
        ]

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeSidebar(root)
    root.mainloop()
