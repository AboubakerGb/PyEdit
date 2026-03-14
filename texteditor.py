import customtkinter as ctk
from tkinter import filedialog, Text, Frame
from pygments import lex
from pygments.lexers import PythonLexer, HtmlLexer, CssLexer, JavascriptLexer
from pygments.token import Token
import os

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Modern Code Editor")
app.geometry("1000x620")

font_size = 14
is_dark_mode = False

# ─────────────────────────────────────────────
#  Tab data model
#  Each tab is a dict:
#  {
#    "id":        int
#    "title":     str
#    "filepath":  str | None
#    "language":  str
#    "modified":  bool
#    "frame":     CTkFrame   – the editor container
#    "textbox":   CTkTextbox
#    "linenums":  Text        – gutter widget
#  }
# ─────────────────────────────────────────────

tabs = []
active_tab_id = None
_tab_id_counter = 0


def _next_id():
    global _tab_id_counter
    _tab_id_counter += 1
    return _tab_id_counter


def get_tab(tab_id=None):
    tid = tab_id if tab_id is not None else active_tab_id
    for t in tabs:
        if t["id"] == tid:
            return t
    return None


def get_textbox():
    t = get_tab()
    return t["textbox"] if t else None


# ─────────────────────────────────────────────
#  Syntax highlighting
# ─────────────────────────────────────────────

def highlight_syntax(tab=None, event=None):
    if tab is None:
        tab = get_tab()
    if tab is None:
        return

    tb   = tab["textbox"]
    lang = tab["language"]
    code = tb.get("1.0", "end-1c")

    if lang == "Python":
        lexer = PythonLexer()
    elif lang == "HTML":
        lexer = HtmlLexer()
    elif lang == "CSS":
        lexer = CssLexer()
    else:
        lexer = JavascriptLexer()

    for tag in ("keyword", "string", "comment"):
        tb.tag_remove(tag, "1.0", "end")

    index = "1.0"
    for token, content in lex(code, lexer):
        end_index = f"{index}+{len(content)}c"
        if token in Token.Keyword:
            tb.tag_add("keyword", index, end_index)
        elif token in Token.String:
            tb.tag_add("string",  index, end_index)
        elif token in Token.Comment:
            tb.tag_add("comment", index, end_index)
        index = end_index

    tb.tag_config("keyword", foreground="#ff7b72")
    tb.tag_config("string",  foreground="#a5d6ff")
    tb.tag_config("comment", foreground="#8b949e")

    update_line_numbers(tab)


# ─────────────────────────────────────────────
#  Line numbers
# ─────────────────────────────────────────────

def update_line_numbers(tab=None, event=None):
    if tab is None:
        tab = get_tab()
    if tab is None:
        return

    tb    = tab["textbox"]
    ln    = tab["linenums"]
    total = int(tb.index("end-1c").split(".")[0])

    ln.config(state="normal")
    ln.delete("1.0", "end")
    ln.insert("1.0", "\n".join(str(i) for i in range(1, total + 1)))
    ln.config(state="disabled")
    ln.yview_moveto(tb.yview()[0])


def on_scroll(tab, event=None):
    tab["linenums"].yview_moveto(tab["textbox"].yview()[0])


# ─────────────────────────────────────────────
#  Language helpers
# ─────────────────────────────────────────────

def detect_language(path):
    if path.endswith(".py"):   return "Python"
    if path.endswith(".html"): return "HTML"
    if path.endswith(".css"):  return "CSS"
    if path.endswith(".js"):   return "JavaScript"
    return "Python"


def change_language(choice):
    tab = get_tab()
    if tab:
        tab["language"] = choice
        highlight_syntax(tab)


# ─────────────────────────────────────────────
#  Tab bar rendering
# ─────────────────────────────────────────────

def refresh_tab_bar():
    for widget in tab_bar.winfo_children():
        widget.destroy()

    for t in tabs:
        tid       = t["id"]
        is_active = tid == active_tab_id
        label     = ("● " if t["modified"] else "") + t["title"]

        fg   = ("#1f6aa5" if not is_dark_mode else "#4da6ff") if is_active else ("gray30" if not is_dark_mode else "gray70")
        bg   = ("white"   if not is_dark_mode else "#2b2b2b") if is_active else ("#d0d0d0" if not is_dark_mode else "#3a3a3a")
        bord = ("#1f6aa5" if not is_dark_mode else "#4da6ff") if is_active else None

        ctk.CTkButton(
            tab_bar,
            text=label,
            width=130,
            height=28,
            corner_radius=6,
            border_width=2 if is_active else 0,
            border_color=bord if bord else ("#1f6aa5" if not is_dark_mode else "#4da6ff"),
            fg_color=bg,
            text_color=fg,
            hover_color="#dce8f5" if not is_dark_mode else "#3a3a3a",
            command=lambda i=tid: switch_tab(i),
            anchor="w",
        ).pack(side="left", padx=(3, 0), pady=2)

        ctk.CTkButton(
            tab_bar,
            text="✕",
            width=22,
            height=22,
            corner_radius=4,
            fg_color=("#d0d0d0" if not is_dark_mode else "#3a3a3a"),
            text_color="gray50" if not is_dark_mode else "gray60",
            hover_color="#ffcccc" if not is_dark_mode else "#5a2020",
            command=lambda i=tid: close_tab(i),
        ).pack(side="left", padx=(0, 4), pady=2)

    # "+" button
    ctk.CTkButton(
        tab_bar,
        text="+",
        width=28,
        height=28,
        corner_radius=6,
        fg_color=("#d0d0d0" if not is_dark_mode else "#3a3a3a"),
        text_color="gray40" if not is_dark_mode else "gray70",
        hover_color="#dce8f5" if not is_dark_mode else "#3a3a3a",
        command=lambda: new_tab(),
    ).pack(side="left", padx=4, pady=2)


# ─────────────────────────────────────────────
#  Tab lifecycle
# ─────────────────────────────────────────────

def build_editor_widgets(parent):
    ln_bg = "#2b2b2b" if is_dark_mode else "#f0f0f0"
    ln_fg = "#858585" if is_dark_mode else "#888888"

    linenums = Text(
        parent,
        width=4,
        padx=6,
        pady=4,
        font=("Consolas", font_size),
        bg=ln_bg,
        fg=ln_fg,
        bd=0,
        state="disabled",
        cursor="arrow",
        takefocus=0,
        selectbackground=ln_bg,
        inactiveselectbackground=ln_bg,
    )
    linenums.pack(side="left", fill="y")

    ctk.CTkFrame(parent, width=1).pack(side="left", fill="y")   # separator

    textbox = ctk.CTkTextbox(parent, font=("Consolas", font_size))
    textbox.pack(side="left", fill="both", expand=True)

    return linenums, textbox


def new_tab(title="Untitled", filepath=None, content="", language="Python"):
    global active_tab_id

    tid   = _next_id()
    frame = ctk.CTkFrame(editor_area)
    frame.pack(fill="both", expand=True)

    linenums, textbox = build_editor_widgets(frame)

    tab = {
        "id":       tid,
        "title":    title,
        "filepath": filepath,
        "language": language,
        "modified": False,
        "frame":    frame,
        "textbox":  textbox,
        "linenums": linenums,
    }
    tabs.append(tab)

    if content:
        textbox.insert("1.0", content)

    # Bind per-tab events
    textbox.bind("<KeyRelease>", lambda e, t=tab: _on_key(t, e))
    textbox.bind("<MouseWheel>", lambda e, t=tab: on_scroll(t, e))
    textbox.bind("<Button-4>",   lambda e, t=tab: on_scroll(t, e))
    textbox.bind("<Button-5>",   lambda e, t=tab: on_scroll(t, e))

    switch_tab(tid)
    return tab


def _on_key(tab, event=None):
    tab["modified"] = True
    highlight_syntax(tab, event)
    refresh_tab_bar()


def switch_tab(tab_id):
    global active_tab_id

    for t in tabs:
        t["frame"].pack_forget()

    active_tab_id = tab_id
    tab = get_tab(tab_id)

    if tab:
        tab["frame"].pack(fill="both", expand=True)
        update_line_numbers(tab)
        lang_menu.set(tab["language"])
        suffix = " ●" if tab["modified"] else ""
        app.title(f"Modern Code Editor — {tab['title']}{suffix}")

    refresh_tab_bar()


def close_tab(tab_id):
    global active_tab_id

    tab = get_tab(tab_id)
    if not tab:
        return

    tab["frame"].destroy()
    tabs.remove(tab)

    if not tabs:
        new_tab()
        return

    if active_tab_id == tab_id:
        switch_tab(tabs[-1]["id"])
    else:
        refresh_tab_bar()


# ─────────────────────────────────────────────
#  File operations
# ─────────────────────────────────────────────

def new_file():
    new_tab()


def open_file():
    path = filedialog.askopenfilename(
        filetypes=[("Code Files", "*.py *.html *.css *.js *.txt"), ("All Files", "*.*")]
    )
    if not path:
        return

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    title    = os.path.basename(path)
    language = detect_language(path)

    # Reuse a blank untitled tab instead of spawning a new one
    current = get_tab()
    if current and not current["modified"] and current["title"] == "Untitled" \
            and current["textbox"].get("1.0", "end-1c") == "":
        current["title"]    = title
        current["filepath"] = path
        current["language"] = language
        current["modified"] = False
        current["textbox"].delete("1.0", "end")
        current["textbox"].insert("1.0", content)
        highlight_syntax(current)
        update_line_numbers(current)
        lang_menu.set(language)
        app.title(f"Modern Code Editor — {title}")
        refresh_tab_bar()
    else:
        t = new_tab(title=title, filepath=path, content=content, language=language)
        highlight_syntax(t)
        t["modified"] = False
        refresh_tab_bar()


def save_file():
    tab = get_tab()
    if not tab:
        return
    if tab["filepath"]:
        _write_file(tab, tab["filepath"])
    else:
        save_as()


def save_as():
    tab = get_tab()
    if not tab:
        return
    path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"),
                   ("HTML Files", "*.html"), ("All Files", "*.*")]
    )
    if path:
        tab["filepath"] = path
        tab["title"]    = os.path.basename(path)
        tab["language"] = detect_language(path)
        _write_file(tab, path)
        lang_menu.set(tab["language"])


def _write_file(tab, path):
    content = tab["textbox"].get("1.0", "end-1c")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    tab["modified"] = False
    app.title(f"Modern Code Editor — {tab['title']}")
    refresh_tab_bar()


# ─────────────────────────────────────────────
#  Edit operations
# ─────────────────────────────────────────────

def copy_text():
    tb = get_textbox()
    if not tb: return
    try:
        app.clipboard_clear()
        app.clipboard_append(tb.selection_get())
    except:
        pass


def paste_text():
    tb = get_textbox()
    if not tb: return
    try:
        tb.insert("insert", app.clipboard_get())
        _on_key(get_tab())
    except:
        pass


def cut_text():
    copy_text()
    tb = get_textbox()
    if not tb: return
    try:
        tb.delete("sel.first", "sel.last")
        _on_key(get_tab())
    except:
        pass


def select_all():
    tb = get_textbox()
    if tb:
        tb.tag_add("sel", "1.0", "end")


# ─────────────────────────────────────────────
#  Font size
# ─────────────────────────────────────────────

def change_font_size(size):
    global font_size
    font_size = int(size)
    for t in tabs:
        t["textbox"].configure(font=("Consolas", font_size))
        t["linenums"].config(font=("Consolas", font_size))
        update_line_numbers(t)


# ─────────────────────────────────────────────
#  Dark mode
# ─────────────────────────────────────────────

def toggle_mode():
    global is_dark_mode
    is_dark_mode = mode_switch.get() == 1
    ctk.set_appearance_mode("dark" if is_dark_mode else "light")
    ln_bg = "#2b2b2b" if is_dark_mode else "#f0f0f0"
    ln_fg = "#858585" if is_dark_mode else "#888888"
    for t in tabs:
        t["linenums"].config(bg=ln_bg, fg=ln_fg,
                             selectbackground=ln_bg,
                             inactiveselectbackground=ln_bg)
    refresh_tab_bar()


# ─────────────────────────────────────────────
#  Find
# ─────────────────────────────────────────────

def find_text():
    tb = get_textbox()
    if not tb: return
    tb.tag_remove("found", "1.0", "end")
    search = find_entry.get()
    if not search: return
    start = "1.0"
    while True:
        pos = tb.search(search, start, stopindex="end")
        if not pos: break
        end = f"{pos}+{len(search)}c"
        tb.tag_add("found", pos, end)
        start = end
    tb.tag_config("found", background="yellow", foreground="black")


# ─────────────────────────────────────────────
#  UI layout
# ─────────────────────────────────────────────

# Toolbar
toolbar = ctk.CTkFrame(app)
toolbar.pack(fill="x", padx=10, pady=(6, 2))

ctk.CTkButton(toolbar, text="📄 New",    command=new_file,   width=75).pack(side="left", padx=3)
ctk.CTkButton(toolbar, text="📂 Open",   command=open_file,  width=75).pack(side="left", padx=3)
ctk.CTkButton(toolbar, text="💾 Save",   command=save_file,  width=75).pack(side="left", padx=3)
ctk.CTkButton(toolbar, text="Save As",  command=save_as,    width=75).pack(side="left", padx=3)
ctk.CTkButton(toolbar, text="Copy",     command=copy_text,  width=65).pack(side="left", padx=3)
ctk.CTkButton(toolbar, text="Paste",    command=paste_text, width=65).pack(side="left", padx=3)
ctk.CTkButton(toolbar, text="Cut",      command=cut_text,   width=55).pack(side="left", padx=3)
ctk.CTkButton(toolbar, text="Select All", command=select_all, width=85).pack(side="left", padx=3)

font_menu = ctk.CTkOptionMenu(toolbar, values=["10","12","14","16","18","20"],
                               command=change_font_size, width=75)
font_menu.set("14")
font_menu.pack(side="left", padx=6)

lang_menu = ctk.CTkOptionMenu(toolbar, values=["Python","HTML","CSS","JavaScript"],
                               command=change_language, width=115)
lang_menu.set("Python")
lang_menu.pack(side="left", padx=6)

mode_switch = ctk.CTkSwitch(toolbar, text="Dark Mode", command=toggle_mode)
mode_switch.pack(side="right", padx=10)

# Find bar
find_frame = ctk.CTkFrame(app)
find_frame.pack(fill="x", padx=10, pady=2)

find_entry = ctk.CTkEntry(find_frame, placeholder_text="Find text…")
find_entry.pack(side="left", padx=5, fill="x", expand=True)
ctk.CTkButton(find_frame, text="Find", command=find_text, width=75).pack(side="left", padx=5)

# Tab bar
tab_bar = ctk.CTkFrame(app, height=38)
tab_bar.pack(fill="x", padx=10, pady=(4, 0))
tab_bar.pack_propagate(False)

# Editor area
editor_area = ctk.CTkFrame(app)
editor_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))

# ─────────────────────────────────────────────
#  Keyboard shortcuts
# ─────────────────────────────────────────────

app.bind("<Control-n>", lambda e: new_file())
app.bind("<Control-o>", lambda e: open_file())
app.bind("<Control-s>", lambda e: save_file())
app.bind("<Control-S>", lambda e: save_as())
app.bind("<Control-c>", lambda e: copy_text())
app.bind("<Control-v>", lambda e: paste_text())
app.bind("<Control-x>", lambda e: cut_text())
app.bind("<Control-a>", lambda e: select_all())


def next_tab(e=None):
    if not tabs: return
    idx = next((i for i, t in enumerate(tabs) if t["id"] == active_tab_id), 0)
    switch_tab(tabs[(idx + 1) % len(tabs)]["id"])


def prev_tab(e=None):
    if not tabs: return
    idx = next((i for i, t in enumerate(tabs) if t["id"] == active_tab_id), 0)
    switch_tab(tabs[(idx - 1) % len(tabs)]["id"])


app.bind("<Control-Tab>",       next_tab)
app.bind("<Control-Shift-Tab>", prev_tab)

# ─────────────────────────────────────────────
#  Bootstrap
# ─────────────────────────────────────────────

new_tab()   # open one blank tab on startup

app.mainloop()