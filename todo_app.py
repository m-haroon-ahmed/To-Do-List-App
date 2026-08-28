"""
To-Do List Desktop Application
Python Internship Project No. 3
Built with Python Tkinter + JSON file storage.

"""

import json
import os
import tkinter as tk
from datetime import date, datetime
from tkinter import ttk, messagebox

try:
    from tkcalendar import DateEntry
    TKCALENDAR_AVAILABLE = True
except ImportError:
    TKCALENDAR_AVAILABLE = False

# ----------------------------------------------------------------------
# Theme constants
# ----------------------------------------------------------------------
COLOR_BG = "#F5EFE6"           # cream background (main content area)
COLOR_SIDEBAR = "#EFE6D8"      # slightly deeper cream for sidebar
COLOR_HEADER = "#1B2A3A"       # dark navy
COLOR_ACCENT = "#D98E28"       # orange/gold accent
COLOR_CARD = "#FFFFFF"         # white cards
COLOR_CARD_BORDER = "#E1D7C4"

COLOR_ADD = "#4C8C4A"          # green
COLOR_UPDATE = "#3E6B99"       # blue
COLOR_DELETE = "#A6453B"       # red/maroon
COLOR_CLEAR = "#9C9280"        # tan/gray
COLOR_COMPLETE = "#D98E28"     # orange/gold
COLOR_DELETE_ALL = "#1B2A3A"   # dark navy

COLOR_ROW_ALT = "#F0E8DA"      # light cream stripe
COLOR_ROW_WHITE = "#FFFFFF"
COLOR_TEXT_LABEL = "#7A6F5E"   # muted gray-brown
COLOR_TEXT_DARK = "#2B2B2B"
COLOR_WHITE = "#FFFFFF"

COLOR_PRIORITY_HIGH = "#A6453B"
COLOR_PRIORITY_MEDIUM = "#D98E28"
COLOR_PRIORITY_LOW = "#4C8C4A"

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SECTION = ("Segoe UI", 12, "bold")
FONT_LABEL = ("Segoe UI", 10)
FONT_SMALL_LABEL = ("Segoe UI", 8, "bold")
FONT_STAT_LABEL = ("Segoe UI", 10, "bold")
FONT_ENTRY = ("Segoe UI", 10)
FONT_BUTTON = ("Segoe UI", 10, "bold")
FONT_HEADER_ROW = ("Segoe UI", 10, "bold")
FONT_ROW = ("Segoe UI", 10)
FONT_STAT_NUMBER = ("Segoe UI", 20, "bold")
FONT_SIDEBAR_ITEM = ("Segoe UI", 10)

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")

STATUS_OPTIONS = ["Pending", "Completed"]
PRIORITY_OPTIONS = ["Low", "Medium", "High"]
FILTER_OPTIONS = ["All", "Active", "Completed", "High Priority"]
POPULAR_CATEGORIES = [
    "Personal", "Work", "Shopping", "Health", "Finance", "Education",
    "Home", "Travel", "Errands",
]


# ----------------------------------------------------------------------
# Data layer
# ----------------------------------------------------------------------
class TaskManager:
    """Handles loading, saving, and CRUD operations for tasks."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.tasks = []
        self.next_id = 1
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from the JSON file. Create an empty file if missing/corrupted."""
        if not os.path.exists(self.filepath):
            self.tasks = []
            self.save_tasks()
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                raw = json.loads(content) if content else []
        except (json.JSONDecodeError, OSError):
            raw = []

        # Normalize each task so older tasks.json files (without priority/
        # due_date/category) still load cleanly.
        self.tasks = []
        for t in raw:
            self.tasks.append({
                "id": t.get("id"),
                "title": t.get("title", ""),
                "priority": t.get("priority", "Medium"),
                "due_date": t.get("due_date", ""),
                "category": t.get("category", ""),
                "status": t.get("status", "Pending"),
            })

        if self.tasks:
            self.next_id = max(task["id"] for task in self.tasks) + 1
        else:
            self.next_id = 1

        if raw and any(t.get("priority") is None for t in raw):
            # File was in the older format; re-save it in the new format.
            self.save_tasks()

    def save_tasks(self):
        """Write the current task list to the JSON file."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, indent=2)
            return True
        except OSError as e:
            messagebox.showerror("Save Error", f"Could not save tasks:\n{e}")
            return False

    def add_task(self, title, priority, due_date, category, status="Pending"):
        task = {
            "id": self.next_id,
            "title": title,
            "priority": priority,
            "due_date": due_date,
            "category": category,
            "status": status,
        }
        self.tasks.append(task)
        self.next_id += 1
        self.save_tasks()
        return task

    def update_task(self, task_id, title, priority, due_date, category, status):
        for task in self.tasks:
            if task["id"] == task_id:
                task["title"] = title
                task["priority"] = priority
                task["due_date"] = due_date
                task["category"] = category
                task["status"] = status
                self.save_tasks()
                return True
        return False

    def delete_task(self, task_id):
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        if len(self.tasks) != before:
            self.save_tasks()
            return True
        return False

    def delete_all(self):
        self.tasks = []
        self.save_tasks()

    def clear_completed(self):
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t["status"] != "Completed"]
        if len(self.tasks) != before:
            self.save_tasks()
        return before - len(self.tasks)

    def toggle_complete(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = (
                    "Pending" if task["status"] == "Completed" else "Completed"
                )
                self.save_tasks()
                return task["status"]
        return None

    def get_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def filtered(self, filter_name):
        if filter_name == "Active":
            return [t for t in self.tasks if t["status"] != "Completed"]
        if filter_name == "Completed":
            return [t for t in self.tasks if t["status"] == "Completed"]
        if filter_name == "High Priority":
            return [t for t in self.tasks if t["priority"] == "High"]
        return list(self.tasks)

    def search(self, keyword, base_list=None):
        keyword = keyword.lower().strip()
        source = base_list if base_list is not None else self.tasks
        if not keyword:
            return source
        return [
            t for t in source
            if keyword in t["title"].lower()
            or keyword in t.get("category", "").lower()
        ]

    def stats(self):
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["status"] == "Completed")
        active = total - completed
        progress = int(round((completed / total) * 100)) if total else 0
        return {
            "total": total,
            "completed": completed,
            "active": active,
            "progress": progress,
        }


# ----------------------------------------------------------------------
# UI layer
# ----------------------------------------------------------------------
class TodoApp:
    def __init__(self, root):
        self.root = root
        self.manager = TaskManager(DATA_FILE)
        self.category_options = self._load_category_options()
        self.selected_task_id = None
        self.active_filter = "All"

        self._configure_window()
        self._configure_style()
        self._build_header()

        body = tk.Frame(self.root, bg=COLOR_BG)
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)
        content = tk.Frame(body, bg=COLOR_BG)
        content.pack(side="left", fill="both", expand=True)

        self._build_stat_cards(content)
        self._build_task_form(content)
        self._build_action_buttons(content)
        self._build_task_table(content)

        self.refresh_all()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def _configure_window(self):
        self.root.title("To-Do List")
        self.root.geometry("1180x760")
        self.root.minsize(1000, 680)
        self.root.configure(bg=COLOR_BG)

    def _configure_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background=COLOR_ROW_WHITE,
            fieldbackground=COLOR_ROW_WHITE,
            foreground=COLOR_TEXT_DARK,
            rowheight=30,
            font=FONT_ROW,
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=COLOR_HEADER,
            foreground=COLOR_WHITE,
            font=FONT_HEADER_ROW,
            relief="flat",
        )
        style.map("Treeview.Heading", background=[("active", COLOR_HEADER)])
        style.map(
            "Treeview",
            background=[("selected", COLOR_UPDATE)],
            foreground=[("selected", COLOR_WHITE)],
        )

        style.configure("TCombobox", font=FONT_ENTRY)

        style.configure(
            "Progress.Horizontal.TProgressbar",
            troughcolor=COLOR_CARD_BORDER,
            background=COLOR_ACCENT,
            thickness=10,
        )

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    def _build_header(self):
        header = tk.Frame(self.root, bg=COLOR_HEADER, height=68)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="\u2713  To-Do List",
            bg=COLOR_HEADER,
            fg=COLOR_WHITE,
            font=FONT_TITLE,
        )
        title.pack(side="left", padx=25)

        search_frame = tk.Frame(header, bg=COLOR_WHITE)
        search_frame.pack(side="right", padx=25, pady=17)

        tk.Label(search_frame, text="\U0001F50D", bg=COLOR_WHITE, font=("Segoe UI", 10)).pack(
            side="left", padx=(8, 0)
        )
        self.search_entry = tk.Entry(
            search_frame, font=FONT_ENTRY, relief="flat", bd=0, width=28
        )
        self.search_entry.pack(side="left", ipady=6, padx=6)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_table())

        accent = tk.Frame(self.root, bg=COLOR_ACCENT, height=3)
        accent.pack(fill="x")

    # ------------------------------------------------------------------
    # Sidebar
    # ------------------------------------------------------------------
    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=COLOR_SIDEBAR, width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="TASK FILTERS", bg=COLOR_SIDEBAR, fg=COLOR_TEXT_LABEL,
            font=FONT_SMALL_LABEL,
        ).pack(anchor="w", padx=20, pady=(25, 10))

        self.filter_buttons = {}
        for name in FILTER_OPTIONS:
            btn = tk.Label(
                sidebar,
                text=name,
                bg=COLOR_SIDEBAR,
                fg=COLOR_TEXT_DARK,
                font=FONT_SIDEBAR_ITEM,
                anchor="w",
                padx=20,
                pady=10,
                cursor="hand2",
            )
            btn.pack(fill="x")
            btn.bind("<Button-1>", lambda e, n=name: self.set_filter(n))
            self.filter_buttons[name] = btn

        # Progress panel pinned near the bottom of the sidebar
        progress_card = tk.Frame(sidebar, bg=COLOR_CARD, highlightbackground=COLOR_CARD_BORDER,
                                  highlightthickness=1)
        progress_card.pack(side="bottom", fill="x", padx=15, pady=20)

        tk.Label(
            progress_card, text="YOUR PROGRESS", bg=COLOR_CARD, fg=COLOR_UPDATE,
            font=FONT_SMALL_LABEL,
        ).pack(anchor="w", padx=15, pady=(15, 8))

        self.progress_bar = ttk.Progressbar(
            progress_card, style="Progress.Horizontal.TProgressbar",
            orient="horizontal", mode="determinate", length=160,
        )
        self.progress_bar.pack(padx=15, pady=(0, 8))

        self.progress_label = tk.Label(
            progress_card, text="0 of 0 completed (0%)", bg=COLOR_CARD,
            fg=COLOR_TEXT_LABEL, font=("Segoe UI", 9),
        )
        self.progress_label.pack(anchor="w", padx=15, pady=(0, 15))

    def set_filter(self, name):
        self.active_filter = name
        for fname, btn in self.filter_buttons.items():
            if fname == name:
                btn.configure(bg=COLOR_UPDATE, fg=COLOR_WHITE)
            else:
                btn.configure(bg=COLOR_SIDEBAR, fg=COLOR_TEXT_DARK)
        self.refresh_table()

    # ------------------------------------------------------------------
    # Stat cards
    # ------------------------------------------------------------------
    def _build_stat_cards(self, parent):
        row = tk.Frame(parent, bg=COLOR_BG)
        row.pack(fill="x", padx=25, pady=(20, 15))

        self.stat_labels = {}
        cards = [
            ("total", "TOTAL TASKS", COLOR_UPDATE),
            ("completed", "COMPLETED", COLOR_ADD),
            ("active", "ACTIVE", COLOR_ACCENT),
            ("progress", "PROGRESS", COLOR_HEADER),
        ]
        for key, label, color in cards:
            card = tk.Frame(row, bg=COLOR_CARD, highlightbackground=COLOR_CARD_BORDER,
                             highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=(0 if key == "total" else 10, 0))

            inner = tk.Frame(card, bg=COLOR_CARD)
            inner.pack(fill="both", padx=18, pady=16)

            tk.Label(inner, text=label, bg=COLOR_CARD, fg=COLOR_TEXT_LABEL,
                     font=FONT_STAT_LABEL).pack(anchor="w")

            stat_row = tk.Frame(inner, bg=COLOR_CARD)
            stat_row.pack(anchor="w", pady=(6, 0))
            tk.Frame(stat_row, bg=color, width=4, height=26).pack(side="left", padx=(0, 8))
            value_lbl = tk.Label(stat_row, text="0", bg=COLOR_CARD, fg=color,
                                  font=FONT_STAT_NUMBER)
            value_lbl.pack(side="left")
            self.stat_labels[key] = value_lbl

    # ------------------------------------------------------------------
    # Add / Edit task form
    # ------------------------------------------------------------------
    def _load_category_options(self):
        options = list(POPULAR_CATEGORIES)
        known = {category.casefold() for category in options}
        for task in self.manager.tasks:
            category = task.get("category", "").strip()
            if category and category.casefold() not in known:
                options.append(category)
                known.add(category.casefold())
        return options

    def _remember_category(self, category):
        if category and category.casefold() not in {
            option.casefold() for option in self.category_options
        }:
            self.category_options.append(category)
            self.category_combo.configure(values=self.category_options)

    def _build_task_form(self, parent):
        card = tk.Frame(parent, bg=COLOR_CARD, highlightbackground=COLOR_CARD_BORDER,
                         highlightthickness=1)
        card.pack(fill="x", padx=25, pady=(0, 15))

        inner = tk.Frame(card, bg=COLOR_CARD)
        inner.pack(fill="x", padx=20, pady=18)

        tk.Label(inner, text="ADD / EDIT TASK", bg=COLOR_CARD, fg=COLOR_HEADER,
                 font=FONT_SECTION).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))

        inner.columnconfigure(0, weight=3)
        inner.columnconfigure(1, weight=1)
        inner.columnconfigure(2, weight=1)
        inner.columnconfigure(3, weight=1)

        # Row 1: Task description + Priority
        tk.Label(inner, text="Task description", bg=COLOR_CARD, fg=COLOR_TEXT_LABEL,
                 font=FONT_LABEL).grid(row=1, column=0, sticky="w")
        tk.Label(inner, text="Priority", bg=COLOR_CARD, fg=COLOR_TEXT_LABEL,
                 font=FONT_LABEL).grid(row=1, column=1, sticky="w", padx=(15, 0))

        self.task_entry = tk.Entry(inner, font=FONT_ENTRY, relief="solid", bd=1)
        self.task_entry.grid(row=2, column=0, sticky="ew", ipady=6, pady=(2, 12))

        self.priority_var = tk.StringVar(value=PRIORITY_OPTIONS[1])
        self.priority_combo = ttk.Combobox(
            inner, textvariable=self.priority_var, values=PRIORITY_OPTIONS,
            state="readonly", font=FONT_ENTRY,
        )
        self.priority_combo.grid(row=2, column=1, sticky="ew", ipady=3, padx=(15, 0), pady=(2, 12))

        # Row 2: Due date + Category + Save button
        tk.Label(inner, text="Due date", bg=COLOR_CARD, fg=COLOR_TEXT_LABEL,
                 font=FONT_LABEL).grid(row=3, column=0, sticky="w")
        tk.Label(inner, text="Category", bg=COLOR_CARD, fg=COLOR_TEXT_LABEL,
                 font=FONT_LABEL).grid(row=3, column=1, sticky="w", padx=(15, 0))

        due_date_frame = tk.Frame(inner, bg=COLOR_CARD)
        due_date_frame.grid(row=4, column=0, sticky="ew", pady=(2, 0))

        if TKCALENDAR_AVAILABLE:
            # Real calendar-picker field.
            self.due_date_widget = DateEntry(
                due_date_frame, font=FONT_ENTRY, date_pattern="yyyy-mm-dd",
                background=COLOR_UPDATE, foreground=COLOR_WHITE,
                borderwidth=1, width=16,
            )
            self.due_date_widget.pack(side="left", ipady=3)
        else:
            # Fallback: plain entry, auto-filled with today's date, plus a
            # "Today" button so the user rarely has to type a date by hand.
            self.due_date_entry = tk.Entry(
                due_date_frame, font=FONT_ENTRY, relief="solid", bd=1
            )
            self.due_date_entry.pack(side="left", fill="x", expand=True, ipady=6)
            self.due_date_entry.insert(0, date.today().isoformat())

            self._make_button(
                due_date_frame, "Today", COLOR_CLEAR, self._set_due_date_today, outline=True
            ).pack(side="left", padx=(6, 0))

        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            inner, textvariable=self.category_var, values=self.category_options,
            state="normal", font=FONT_ENTRY,
        )
        self.category_combo.grid(row=4, column=1, sticky="ew", ipady=3, padx=(15, 0), pady=(2, 0))

        self.save_btn = self._make_button(inner, "\u270E  Save Task", COLOR_UPDATE, self.save_task)
        self.save_btn.grid(row=4, column=3, sticky="e", pady=(2, 0))

    def _get_due_date(self):
        if TKCALENDAR_AVAILABLE:
            return self.due_date_widget.get()
        return self.due_date_entry.get().strip()

    def _set_due_date(self, value):
        """Set the due-date field. Passing an empty value resets it to today."""
        if TKCALENDAR_AVAILABLE:
            try:
                if value:
                    self.due_date_widget.set_date(
                        datetime.strptime(value, "%Y-%m-%d").date()
                    )
                else:
                    self.due_date_widget.set_date(date.today())
            except ValueError:
                self.due_date_widget.set_date(date.today())
        else:
            self.due_date_entry.delete(0, tk.END)
            self.due_date_entry.insert(0, value if value else date.today().isoformat())

    def _set_due_date_today(self):
        self._set_due_date("")

    # ------------------------------------------------------------------
    # Action buttons
    # ------------------------------------------------------------------
    def _make_button(self, parent, text, bg, command, outline=False):
        if outline:
            btn = tk.Button(
                parent, text=text, bg=COLOR_CARD, fg=COLOR_TEXT_DARK,
                font=FONT_BUTTON, relief="solid", bd=1,
                padx=14, pady=8, cursor="hand2", command=command,
                highlightbackground=COLOR_CARD_BORDER,
            )
        else:
            btn = tk.Button(
                parent, text=text, bg=bg, fg=COLOR_WHITE, font=FONT_BUTTON,
                relief="flat", bd=0, padx=14, pady=8,
                activebackground=bg, activeforeground=COLOR_WHITE,
                cursor="hand2", command=command,
            )
        return btn

    def _build_action_buttons(self, parent):
        row = tk.Frame(parent, bg=COLOR_BG)
        row.pack(fill="x", padx=25, pady=(0, 12))

        self._make_button(row, "\u2713 Change Status", COLOR_ADD, self.toggle_complete).pack(
            side="left", padx=(0, 8)
        )
        self._make_button(row, "\U0001F5D1 Delete Selected", COLOR_DELETE, self.delete_selected).pack(
            side="left", padx=8
        )
        self._make_button(row, "Clear Completed", COLOR_CLEAR, self.clear_completed).pack(
            side="left", padx=8
        )
        self._make_button(row, "\u26A0 Delete All", COLOR_DELETE_ALL, self.delete_all_tasks).pack(
            side="left", padx=8
        )

    # ------------------------------------------------------------------
    # Task table
    # ------------------------------------------------------------------
    def _build_task_table(self, parent):
        container = tk.Frame(parent, bg=COLOR_BG)
        container.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        columns = ("task", "priority", "due_date", "category", "status")
        self.tree = ttk.Treeview(
            container, columns=columns, show="headings", selectmode="browse"
        )
        headings = {
            "task": ("Task", 320, "w"),
            "priority": ("Priority", 100, "center"),
            "due_date": ("Due Date", 110, "center"),
            "category": ("Category", 130, "center"),
            "status": ("Status", 110, "center"),
        }
        for col, (text, width, anchor) in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor)

        self.tree.tag_configure("oddrow", background=COLOR_ROW_ALT)
        self.tree.tag_configure("evenrow", background=COLOR_ROW_WHITE)
        self.tree.tag_configure("completed", background="#E4EFE0")
        self.tree.tag_configure("priority_high", foreground=COLOR_PRIORITY_HIGH)
        self.tree.tag_configure("priority_medium", foreground=COLOR_PRIORITY_MEDIUM)
        self.tree.tag_configure("priority_low", foreground=COLOR_PRIORITY_LOW)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    # ------------------------------------------------------------------
    # Refresh / render
    # ------------------------------------------------------------------
    def refresh_all(self):
        self.refresh_table()
        self.refresh_stats()

    def _visible_tasks(self):
        base = self.manager.filtered(self.active_filter)
        keyword = self.search_entry.get()
        return self.manager.search(keyword, base_list=base)

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for i, task in enumerate(self._visible_tasks()):
            tags = ["oddrow" if i % 2 else "evenrow"]
            if task["status"] == "Completed":
                tags.append("completed")
                status_text = "\u2713 Done"
            else:
                status_text = "\u25CB Pending"

            priority = task.get("priority", "Medium")
            if priority == "High":
                tags.append("priority_high")
            elif priority == "Low":
                tags.append("priority_low")
            else:
                tags.append("priority_medium")

            self.tree.insert(
                "", "end",
                iid=str(task["id"]),
                values=(
                    task["title"], priority, task.get("due_date", ""),
                    task.get("category", ""), status_text,
                ),
                tags=tuple(tags),
            )
        self.refresh_stats()

    def refresh_stats(self):
        stats = self.manager.stats()
        self.stat_labels["total"].config(text=str(stats["total"]))
        self.stat_labels["completed"].config(text=str(stats["completed"]))
        self.stat_labels["active"].config(text=str(stats["active"]))
        self.stat_labels["progress"].config(text=f"{stats['progress']}%")

        self.progress_bar["value"] = stats["progress"]
        self.progress_label.config(
            text=f"{stats['completed']} of {stats['total']} completed ({stats['progress']}%)"
        )

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def on_row_select(self, event=None):
        selection = self.tree.selection()
        if not selection:
            self.selected_task_id = None
            return
        task_id = int(selection[0])
        task = self.manager.get_task(task_id)
        if task:
            self.selected_task_id = task_id
            self.task_entry.delete(0, tk.END)
            self.task_entry.insert(0, task["title"])
            self.priority_var.set(task.get("priority", "Medium"))
            self._set_due_date(task.get("due_date", ""))
            self.category_var.set(task.get("category", ""))
            self.save_btn.config(text="\u270E  Update Task")

    def clear_form(self):
        self.task_entry.delete(0, tk.END)
        self.priority_var.set(PRIORITY_OPTIONS[1])
        self._set_due_date("")
        self.category_var.set("")
        self.selected_task_id = None
        self.save_btn.config(text="\u270E  Save Task")
        self.tree.selection_remove(self.tree.selection())

    def save_task(self):
        title = self.task_entry.get().strip()
        if not title:
            messagebox.showwarning("Input Required", "Please enter a task description.")
            return

        due_date = self._get_due_date()
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning(
                    "Invalid Date", "Please use the YYYY-MM-DD date format."
                )
                return
        category = self.category_var.get().strip()
        priority = self.priority_var.get()
        self._remember_category(category)

        if self.selected_task_id is not None:
            task = self.manager.get_task(self.selected_task_id)
            status = task["status"] if task else "Pending"
            self.manager.update_task(
                self.selected_task_id, title, priority, due_date, category, status
            )
        else:
            self.manager.add_task(title, priority, due_date, category)

        self.clear_form()
        self.refresh_all()

    def toggle_complete(self):
        if self.selected_task_id is None:
            messagebox.showwarning("No Selection", "Please select a task to toggle.")
            return
        task_id = self.selected_task_id
        self.manager.toggle_complete(task_id)
        self.refresh_all()
        # Keep the same task selected (if still visible under the active
        # filter/search) so the button can be clicked again to toggle back.
        if self.tree.exists(str(task_id)):
            self.tree.selection_set(str(task_id))
            self.selected_task_id = task_id
        else:
            self.selected_task_id = None

    def delete_selected(self):
        if self.selected_task_id is None:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return
        if messagebox.askyesno("Confirm Delete", "Delete the selected task?"):
            self.manager.delete_task(self.selected_task_id)
            self.clear_form()
            self.refresh_all()

    def clear_completed(self):
        stats = self.manager.stats()
        if stats["completed"] == 0:
            messagebox.showinfo("Nothing to Clear", "There are no completed tasks.")
            return
        if messagebox.askyesno("Confirm Clear", f"Remove all {stats['completed']} completed task(s)?"):
            self.manager.clear_completed()
            self.clear_form()
            self.refresh_all()

    def delete_all_tasks(self):
        if not self.manager.tasks:
            messagebox.showinfo("Nothing to Delete", "There are no tasks to delete.")
            return
        if messagebox.askyesno("Confirm Delete All", "Delete ALL tasks? This cannot be undone."):
            self.manager.delete_all()
            self.clear_form()
            self.refresh_all()

    def on_close(self):
        self.manager.save_tasks()
        self.root.destroy()


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
def main():
    root = tk.Tk()
    app = TodoApp(root)
    app.set_filter("All")
    root.mainloop()


if __name__ == "__main__":
    main()