# 🖊️ PyEdit — Modern Code Editor

A lightweight, modern desktop code editor built entirely with Python.  
Supports syntax highlighting, multi-file tabs, line numbers, dark mode, and more — no Electron, no browser, just Python.

---

## ✨ Features

### 📁 Multi-Tab File Management
- Open multiple files at the same time, each in its own tab
- Tabs show a **● dot** when a file has unsaved changes
- Close individual tabs with the **✕** button — closing the last tab opens a fresh blank one
- Opening a file into a blank untitled tab reuses it instead of creating a duplicate
- Cycle between tabs with **Ctrl+Tab** / **Ctrl+Shift+Tab**

### 🎨 Syntax Highlighting
Automatic color-coded highlighting for:
| Language | Detection |
|---|---|
| Python | `.py` |
| HTML | `.html` |
| CSS | `.css` |
| JavaScript | `.js` |

Colors update live as you type. You can also manually switch the language from the toolbar dropdown at any time.

### 🔢 Line Numbers
- A VS Code-style gutter displays line numbers alongside your code
- Line numbers scroll in sync with the editor
- Font size matches the editor font automatically
- Gutter colors adapt to light and dark mode

### 💾 File Operations
| Action | Shortcut |
|---|---|
| New file (new tab) | `Ctrl+N` |
| Open file | `Ctrl+O` |
| Save | `Ctrl+S` |
| Save As | `Ctrl+Shift+S` |

### ✂️ Edit Operations
| Action | Shortcut |
|---|---|
| Copy | `Ctrl+C` |
| Paste | `Ctrl+V` |
| Cut | `Ctrl+X` |
| Select All | `Ctrl+A` |

### 🔍 Find Text
- Type any word or phrase in the find bar and click **Find**
- All matches are highlighted in **yellow** across the entire file

### 🌙 Dark Mode
- Toggle dark/light mode with the switch in the top-right corner
- The editor, tab bar, gutter, and all UI elements switch together

### 🔠 Font Size
- Choose from `10`, `12`, `14`, `16`, `18`, or `20` pt via the toolbar dropdown
- Font size updates instantly across the editor and line number gutter

---

## 🚀 Getting Started

### Requirements

- Python 3.8+
- The following packages:

```bash
pip install customtkinter pygments
```

### Run

```bash
python texteditor.py
```

---

## 🗂️ Project Structure

```
PyEdit/
│
├── texteditor.py      # Main application — all logic and UI
└── README.md
```

---

## 🛠️ Built With

| Library | Role |
|---|---|
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | Modern-styled UI widgets |
| [Pygments](https://pygments.org/) | Syntax tokenization and highlighting |
| `tkinter` (stdlib) | Core GUI framework, file dialogs, text widgets |
| `os` (stdlib) | File path handling |

---

## 📸 Interface Overview

```
┌─────────────────────────────────────────────────────────────┐
│  📄 New  📂 Open  💾 Save  Save As │ Copy Paste Cut Sel │ 14 │ Python │ ◐ Dark │
├─────────────────────────────────────────────────────────────┤
│  Find text…                                    [ Find ]     │
├──────────────────┬──────────────────────────────────────────┤
│  main.py ✕  +   │                                          │
├────┬─────────────┤   Code editor area                       │
│  1 │             │                                          │
│  2 │             │                                          │
│  3 │             │                                          │
└────┴─────────────┴──────────────────────────────────────────┘
```

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
