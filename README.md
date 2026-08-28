# 📝 To-Do List Desktop App

A desktop To-Do List application built with **Python**, **Tkinter**, and **JSON** file storage. Built as part of a Python internship project to practice GUI programming, CRUD operations, event handling, and file-based data persistence.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)


---

## 📸 Overview

The app provides a dashboard-style interface for managing daily tasks — add, edit, filter, search, and track completion progress, all backed by a local `tasks.json` file so nothing is lost between sessions.

---

## ✨ Features

| Feature | Description |
|---|---|
| ➕ **Add / Edit Task** | Create tasks with a description, priority, due date, and category |
| 🔄 **Mark Complete / Pending** | One button that toggles status and relabels itself based on the selected task |
| 🗑️ **Delete Selected** | Remove a single task with a confirmation prompt |
| 🧹 **Clear Completed** | Bulk-remove every completed task in one click |
| ⚠️ **Delete All** | Wipe the entire list, with a confirmation dialog |
| 🔍 **Search** | Live search across task titles and categories |
| 🗂️ **Filters** | Sidebar filters for All / Active / Completed / High Priority tasks |
| 📊 **Stats Dashboard** | Live counters for Total, Completed, Active tasks, and % Progress |
| 📅 **Smart Due Dates** | Auto-filled with today's date; uses a calendar picker if `tkcalendar` is installed |
| 🏷️ **Smart Categories** | Dropdown remembers every category you've typed, plus common presets |
| 💾 **Auto-Save / Auto-Load** | Every change is saved to `tasks.json` instantly; tasks reload automatically on startup |
| ✅ **Input Validation** | Blocks empty task titles and invalid date formats before saving |

---

## 🖥️ Tech Stack

- **Language:** Python 3
- **GUI:** Tkinter / ttk
- **Storage:** JSON (`tasks.json`)
- **Optional:** [`tkcalendar`](https://pypi.org/project/tkcalendar/) for a calendar-picker date field

---

## 📂 Project Structure

```
To-Do-List-App/
├── todo_app.py         # Main application (UI + data logic)
├── tasks.json          # Task data (auto-created and auto-updated)
├── requirements.txt    # Optional dependency (tkcalendar)
├── .gitignore
└── README.md            # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or later
- Tkinter (bundled with most standard Python installations on Windows/macOS)

### Installation

1. Clone or download this repository.
2. *(Optional but recommended)* Install `tkcalendar` for the calendar-picker date field:
   ```bash
   pip install -r requirements.txt
   ```
   If skipped, the app still works — the due date field auto-fills with today's date and includes a **Today** reset button instead of a calendar popup.

### Run the App

```bash
python todo_app.py
```

The app will automatically create `tasks.json` in the same folder on first launch.

---

## 🗃️ Data Model

Each task is stored in `tasks.json` as an object with the following fields:

```json
{
  "id": 1,
  "title": "Finish Python internship task",
  "priority": "High",
  "due_date": "2026-08-30",
  "category": "University",
  "status": "Pending"
}
```

| Field | Type | Notes |
|---|---|---|
| `id` | integer | Unique, auto-incremented |
| `title` | string | The task description |
| `priority` | string | `Low`, `Medium`, or `High` |
| `due_date` | string | `YYYY-MM-DD` format |
| `category` | string | Free text; suggestions are remembered automatically |
| `status` | string | `Pending` or `Completed` |

---

## 🎨 Design

The interface uses a warm, professional theme:

- **Header:** Dark navy (`#1B2A3A`) banner with a gold/orange accent line (`#D98E28`)
- **Background:** Cream (`#F5EFE6`)
- **Buttons:** Color-coded by action — green (Add/Complete), blue (Update), red (Delete), tan (Clear), navy (destructive bulk actions)
- **Task Table:** Alternating row stripes, color-coded priority text, and a soft green tint for completed tasks

---

## 🧠 What This Project Demonstrates

- Designing multi-panel GUIs with Tkinter (`ttk.Treeview`, `ttk.Combobox`, `ttk.Progressbar`)
- Implementing full CRUD operations against a JSON data store
- Handling button, selection, and keystroke events
- Structuring code with a clear separation between data logic (`TaskManager`) and UI logic (`TodoApp`)
- Defensive file handling (missing/corrupted JSON recovery, backward-compatible data loading)
- Basic input validation and user-confirmation flows for destructive actions

---

## 🔮 Possible Future Improvements

- Task reminders / due-date notifications
- Drag-and-drop task reordering
- Export tasks to CSV or PDF
- Dark mode toggle
- Multi-user task lists

---

## 📄 License

This project is open for educational and personal use.
