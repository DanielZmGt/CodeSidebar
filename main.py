import tkinter as tk
from tkinter import ttk
import pyperclip
import pyautogui
import time

class CodeSidebar:
    def __init__(self, root):
        self.root = root
        self.root.title("CodeSidebar")
        
        # --- UI Styling & Colors ---
        self.bg_color = "#1e1e1e"      # VS Code dark gray
        self.fg_color = "#ffffff"      # White text
        self.accent_color = "#007acc"  # VS Code blue
        self.btn_color = "#333333"     # Darker gray for buttons
        
        # Position window at top right
        screen_width = self.root.winfo_screenwidth()
        self.root.geometry(f"300x750+{screen_width - 320}+50")
        self.root.attributes('-topmost', True)
        self.root.configure(bg=self.bg_color)
        
        # Layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        # --- Header ---
        tk.Label(root, text="CodeSidebar", font=("Segoe UI", 16, "bold"), 
                 bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, pady=10)

        # --- Search Bar ---
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_snippets)
        search_entry = tk.Entry(root, textvariable=self.search_var, bg=self.btn_color, 
                                fg=self.fg_color, insertbackground="white", borderwidth=0)
        search_entry.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        
        # --- Tabs (Notebook) ---
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.btn_color, foreground=self.fg_color, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", self.accent_color)])
        
        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        self.buttons = []
        self.create_tab("HTML", self.get_html_snippets())
        self.create_tab("JS", self.get_js_snippets())
        self.create_tab("CSS", self.get_css_snippets())

    def create_tab(self, name, snippets):
        frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text=name)
        
        # Scrollable area
        canvas = tk.Canvas(frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.bg_color)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=260)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for label, code in snippets:
            btn = tk.Button(scroll_frame, text=label, command=lambda c=code: self.paste_snippet(c),
                            bg=self.btn_color, fg=self.fg_color, relief="flat", 
                            padx=10, pady=5, anchor="w", font=("Segoe UI", 10))
            btn.pack(fill="x", pady=2, padx=5)
            self.buttons.append((btn, label))

    def filter_snippets(self, *args):
        query = self.search_var.get().lower()
        for btn, label in self.buttons:
            if query in label.lower():
                btn.pack(fill="x", pady=2, padx=5)
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
