import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime
import threading
import time
import random
import requests
from pathlib import Path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class GrindForgeApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("GrindForge — Pomodoro")
        self.root.geometry("1400x900")
        self.root.minsize(800, 600)
        
        # Data storage
        self.data_dir = Path.home() / ".grindforge"
        self.data_dir.mkdir(exist_ok=True)
        
        self.TASKS_KEY = 'gf_tasks_v2.json'
        self.STATS_KEY = 'gf_stats_v2.json'
        self.QUOTES_KEY = 'gf_quotes_v1.json'
        self.JOURNAL_KEY = 'gf_journal_v1.json'
        
        # App state
        self.is_running = False
        self.timer_thread = None
        self.is_work_mode = True
        self.time_left = 25 * 60
        self.stats = {"completed_seconds": 0, "sessions_completed": 0, "last_date": ""}
        
        self.quotes = [
            "Focus is a skill - practice it daily.",
            "You don't have to be perfect, just persistent.",
            "Small progress each day adds up to big results.",
            "Work in silence, let success make the noise.",
            "One task at a time. Win the moment."
        ]
        
        self.setup_ui()
        self.load_all_data()
        self.update_timer_display()
        self.update_mode_label()
        self.update_buttons()
        
    def setup_ui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        # Dashboard grid
        self.dashboard_frame = ctk.CTkFrame(
            self.main_frame, 
            fg_color="rgba(4,6,10,0.85)",
            corner_radius=14,
            border_width=1,
            border_color="rgba(78,205,196,0.15)"
        )
        self.dashboard_frame.pack(fill="both", expand=True)
        
        # Header
        self.create_header()
        
        # Sidebar
        self.create_sidebar()
        
        # Timer section
        self.create_timer_section()
        
        # Todo section
        self.create_todo_section()
        
        # End day overlay
        self.create_end_day_overlay()
        
    def create_header(self):
        header_frame = ctk.CTkFrame(
            self.dashboard_frame,
            fg_color="rgba(4,6,10,0.85)",
            corner_radius=14,
            border_width=1,
            border_color="rgba(78,205,196,0.15)"
        )
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12,12), rowconfigure=0)
        
        # Logo and brand
        brand_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        brand_frame.pack(side="left", fill="x", expand=True, padx=(20,0), pady=20)
        
        logo_label = ctk.CTkLabel(
            brand_frame,
            text="🔥",
            font=ctk.CTkFont(size=44, weight="bold"),
            text_color="#4ecdc4"
        )
        logo_label.pack(side="left", padx=(0,12))
        
        brand_container = ctk.CTkFrame(brand_frame, fg_color="transparent")
        brand_container.pack(side="left", fill="x", expand=True)
        
        self.brand_title = ctk.CTkLabel(
            brand_container,
            text="GrindForge",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#4ecdc4"
        )
        self.brand_title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            brand_container,
            text="Pomodoro Productivity Dashboard",
            font=ctk.CTkFont(size=13),
            text_color="#9adbd4"
        )
        subtitle.pack(anchor="w")
        
        # Creator credit
        creator_btn = ctk.CTkButton(
            header_frame,
            text="Creator – Shaurya Chauhan",
            fg_color="rgba(57,255,20,0.12)",
            text_color="#39FF14",
            border_width=1,
            border_color="rgba(57,255,20,0.3)",
            corner_radius=6,
            font=ctk.CTkFont(size=12, weight="medium"),
            height=32,
            command=lambda: messagebox.showinfo("About", "GrindForge by Shaurya Chauhan\nPython Desktop App")
        )
        creator_btn.pack(side="right", padx=20, pady=20)
    
    def create_sidebar(self):
        sidebar_frame = ctk.CTkFrame(
            self.dashboard_frame,
            fg_color="transparent",
            corner_radius=0
        )
        sidebar_frame.grid(row=1, column=0, sticky="nsew", padx=(12,6), pady=(0,12))
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_columnconfigure(1, weight=3)
        self.dashboard_frame.grid_rowconfigure(1, weight=1)
        self.dashboard_frame.grid_rowconfigure(2, weight=1)
        
        # Date and stats box
        date_box = ctk.CTkFrame(
            sidebar_frame,
            fg_color="rgba(4,6,10,0.85)",
            corner_radius=14,
            border_width=1
        )
        date_box.pack(fill="x", padx=12, pady=(0,12))
        
        self.datetime_label = ctk.CTkLabel(
            date_box,
            text="Loading...",
            font=ctk.CTkFont(size=15),
            anchor="center"
        )
        self.datetime_label.pack(pady=(16,10))
        
        stats_frame = ctk.CTkFrame(date_box, fg_color="transparent")
        stats_frame.pack(pady=5)
        
        self.hours_label = ctk.CTkLabel(
            stats_frame,
            text="Hours: 0.00",
            font=ctk.CTkFont(size=13),
            fg_color="rgba(255,255,255,0.08)",
            corner_radius=10,
            padx=12,
            pady=7
        )
        self.hours_label.pack(side="left", padx=(0,10))
        
        self.sessions_label = ctk.CTkLabel(
            stats_frame,
            text="Sessions: 0",
            font=ctk.CTkFont(size=13),
            fg_color="rgba(255,255,255,0.08)",
            corner_radius=10,
            padx=12,
            pady=7
        )
        self.sessions_label.pack(side="left")
        
        # Quotes section
        quotes_frame = ctk.CTkFrame(
            sidebar_frame,
            fg_color="rgba(4,6,10,0.85)",
            corner_radius=14,
            border_width=1
        )
        quotes_frame.pack(fill="x", padx=12, pady=(0,12))
        
        ctk.CTkLabel(
            quotes_frame,
            text="Quote",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(pady=(16,10), anchor="w", padx=16)
        
        self.quote_label = ctk.CTkLabel(
            quotes_frame,
            text='"Stay focused - distractions are the enemy of progress."',
            font=ctk.CTkFont(size=14),
            wraplength=280,
            justify="center"
        )
        self.quote_label.pack(pady=(0,16), padx=16)
        
        quote_btn_frame = ctk.CTkFrame(quotes_frame, fg_color="transparent")
        quote_btn_frame.pack(pady=5, padx=16)
        
        self.new_quote_btn = ctk.CTkButton(
            quote_btn_frame,
            text="New Quote",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=32,
            command=self.new_quote
        )
        self.new_quote_btn.pack(side="left", fill="x", expand=True, padx=(0,8))
        
        self.save_quote_btn = ctk.CTkButton(
            quote_btn_frame,
            text="Save",
            fg_color="#2b3dff",
            text_color="white",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=32,
            command=self.save_quote
        )
        self.save_quote_btn.pack(side="left", fill="x", expand=True)
        
        # Journal
        journal_frame = ctk.CTkFrame(quotes_frame, fg_color="transparent")
        journal_frame.pack(fill="x", padx=16, pady=(16,12))
        
        ctk.CTkLabel(
            journal_frame,
            text="Daily Journal",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w")
        
        self.journal_text = ctk.CTkTextbox(
            journal_frame,
            height=100,
            corner_radius=10,
            fg_color="rgba(255,255,255,0.06)",
            border_width=1,
            border_color="rgba(78,205,196,0.22)"
        )
        self.journal_text.pack(fill="x", pady=(8,12))
        
        self.save_journal_btn = ctk.CTkButton(
            journal_frame,
            text="Save Journal",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=32,
            command=self.save_journal
        )
        self.save_journal_btn.pack(fill="x")
        
        # End day button
        self.end_day_btn = ctk.CTkButton(
            sidebar_frame,
            text="🌙 End Day",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=48,
            fg_color="#4ecdc4",
            text_color="#042726",
            hover_color="#6ef0c9",
            command=self.end_day,
            corner_radius=10
        )
        self.end_day_btn.pack(fill="x", padx=12, pady=(0,12))
    
    def create_timer_section(self):
        self.timer_frame = ctk.CTkFrame(
            self.dashboard_frame,
            fg_color="rgba(4,6,10,0.85)",
            corner_radius=14,
            border_width=1,
            border_color="rgba(78,205,196,0.15)"
        )
        self.timer_frame.grid(row=1, column=1, sticky="nsew", padx=(6,12), pady=(0,12))
        
        ctk.CTkLabel(
            self.timer_frame,
            text="Pomodoro Timer",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(24,12))
        
        self.timer_display = ctk.CTkLabel(
            self.timer_frame,
            text="25:00",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="#4ecdc4"
        )
        self.timer_display.pack(pady=(0,20))
        
        # Timer controls
        controls_frame = ctk.CTkFrame(self.timer_frame, fg_color="transparent")
        controls_frame.pack(pady=10)
        
        self.start_btn = ctk.CTkButton(
            controls_frame,
            text="Start",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="#4ecdc4",
            text_color="#042726",
            command=self.start_timer
        )
        self.start_btn.pack(side="left", padx=(0,10))
        
        self.pause_btn = ctk.CTkButton(
            controls_frame,
            text="Pause",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="#4ecdc4",
            text_color="#042726",
            state="disabled",
            command=self.pause_timer
        )
        self.pause_btn.pack(side="left", padx=(0,10))
        
        self.reset_btn = ctk.CTkButton(
            controls_frame,
            text="Reset",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="#4ecdc4",
            text_color="#042726",
            command=self.reset_timer
        )
        self.reset_btn.pack(side="left")
        
        # Settings
        settings_frame = ctk.CTkFrame(self.timer_frame, fg_color="transparent")
        settings_frame.pack(pady=20)
        
        work_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        work_frame.pack(side="left", padx=20)
        ctk.CTkLabel(work_frame, text="Work", font=ctk.CTkFont(size=13)).pack()
        self.work_time_input = ctk.CTkEntry(
            work_frame,
            width=80,
            height=36,
            font=ctk.CTkFont(size=15, weight="bold"),
            justify="center",
            fg_color="rgba(255,255,255,0.08)"
        )
        self.work_time_input.insert(0, "25")
        self.work_time_input.pack(pady=(5,0))
        
        break_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        break_frame.pack(side="left", padx=20)
        ctk.CTkLabel(break_frame, text="Break", font=ctk.CTkFont(size=13)).pack()
        self.break_time_input = ctk.CTkEntry(
            break_frame,
            width=80,
            height=36,
            font=ctk.CTkFont(size=15, weight="bold"),
            justify="center",
            fg_color="rgba(255,255,255,0.08)"
        )
        self.break_time_input.insert(0, "5")
        self.break_time_input.pack(pady=(5,0))
        
        # Progress row
        progress_frame = ctk.CTkFrame(self.timer_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=20, pady=20)
        
        self.mode_label = ctk.CTkLabel(
            progress_frame,
            text="Mode: Work",
            font=ctk.CTkFont(size=13),
            text_color="#9adbd4"
        )
        self.mode_label.pack(side="left")
        
        self.session_label = ctk.CTkLabel(
            progress_frame,
            text="Completed: 0",
            font=ctk.CTkFont(size=13),
            text_color="#9adbd4"
        )
        self.session_label.pack(side="right")
    
    def create_todo_section(self):
        self.todo_frame = ctk.CTkScrollableFrame(
            self.dashboard_frame,
            fg_color="rgba(0,0,0,0.55)",
            corner_radius=14,
            border_width=1,
            border_color="rgba(78,205,196,0.15)"
        )
        self.todo_frame.grid(row=2, column=1, sticky="nsew", padx=(6,12), pady=(12,12))
        
        title_label = ctk.CTkLabel(
            self.todo_frame,
            text="To-Do List ✨",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20,16))
        
        # Todo input
        input_frame = ctk.CTkFrame(self.todo_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=5)
        
        self.todo_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Write a task...",
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="rgba(255,255,255,0.08)"
        )
        self.todo_input.pack(side="left", fill="x", expand=True, padx=(0,10))
        
        self.add_task_btn = ctk.CTkButton(
            input_frame,
            text="Add Task",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="#4ecdc4",
            text_color="#042726",
            command=self.add_task
        )
        self.add_task_btn.pack(side="right", fill="x", padx=0, width=120)
        
        self.todo_listbox = ctk.CTkScrollableFrame(
            self.todo_frame,
            fg_color="transparent",
            scrollbar_button_color="#4ecdc4",
            scrollbar_button_hover_color="#6ef0c9"
        )
        self.todo_listbox.pack(fill="both", expand=True, padx=20, pady=(0,20))
    
    def create_end_day_overlay(self):
        self.overlay = ctk.CTkToplevel(self.root)
        self.overlay.geometry("400x500")
        self.overlay.transient(self.root)
        self.overlay.grab_set()
        self.overlay.attributes("-alpha", 0.0)
        self.overlay.attributes("-topmost", True)
        
        overlay_frame = ctk.CTkFrame(
            self.overlay,
            fg_color="rgba(3,6,18,0.95)",
            corner_radius=18
        )
        overlay_frame.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Center content
        content_frame = ctk.CTkFrame(
            overlay_frame,
            fg_color="rgba(8,10,20,0.98)",
            corner_radius=18,
            border_width=1,
            border_color="rgba(78,205,196,0.4)"
        )
        content_frame.pack(expand=True)
        
        ctk.CTkLabel(
            content_frame,
            text="✓",
            font=ctk.CTkFont(size=38, weight="bold"),
            text_color="#4ecdc4"
        ).pack(pady=(40,20))
        
        ctk.CTkLabel(
            content_frame,
            text="Day Complete",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(0,6))
        
        ctk.CTkLabel(
            content_frame,
            text="Here is what you achieved today:",
            font=ctk.CTkFont(size=14),
            text_color="#9adbd4"
        ).pack(pady=(0,20))
        
        self.summary_label = ctk.CTkLabel(
            content_frame,
            text="",
            font=ctk.CTkFont(size=16, family="monospace"),
            wraplength=340,
            justify="center"
        )
        self.summary_label.pack(pady=(0,20))
    
    def load_all_data(self):
        self.load_stats()
        self.load_quotes()
        self.load_journal()
        self.load_todos()
        self.update_datetime()
    
    def get_data_path(self, key):
        return self.data_dir / key
    
    def get_today_date(self):
        return datetime.now().strftime("%Y-%m-%d")
    
    def update_datetime(self):
        now = datetime.now()
        formatter = now.strftime("%A, %B %d, %I:%M %p")
        self.datetime_label.configure(text=formatter)
        self.root.after(1000, self.update_datetime)
    
    def load_stats(self):
        try:
            stats_path = self.get_data_path(self.STATS_KEY)
            if stats_path.exists():
                with open(stats_path, 'r') as f:
                    stats = json.load(f)
                    if stats.get("last_date") == self.get_today_date():
                        self.stats = stats
        except:
            pass
        self.update_stats_display()
    
    def save_stats(self):
        try:
            stats_path = self.get_data_path(self.STATS_KEY)
            with open(stats_path, 'w') as f:
                json.dump(self.stats, f)
            self.update_stats_display()
        except:
            pass
    
    def update_stats_display(self):
        hours = (self.stats["completed_seconds"] / 3600)
        self.hours_label.configure(text=f"Hours: {hours:.2f}")
        self.sessions_label.configure(text=f"Sessions: {self.stats['sessions_completed']}")
        self.session_label.configure(text=f"Completed: {self.stats['sessions_completed']}")
    
    def update_timer_display(self):
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.timer_display.configure(text=time_str)
    
    def update_mode_label(self):
        mode = "Work" if self.is_work_mode else "Break"
        self.mode_label.configure(text=f"Mode: {mode}")
    
    def update_buttons(self):
        self.start_btn.configure(state="disabled" if self.is_running else "normal")
        self.pause_btn.configure(state="normal" if self.is_running else "disabled")
    
    def start_timer(self):
        if self.is_running:
            return
        self.is_running = True
        self.update_buttons()
        self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
        self.timer_thread.start()
    
    def pause_timer(self):
        self.is_running = False
        self.update_buttons()
    
    def reset_timer(self):
        self.pause_timer()
        self.is_work_mode = True
        self.time_left = int(self.work_time_input.get()) * 60
        self.update_mode_label()
        self.update_timer_display()
    
    def timer_loop(self):
        while self.is_running and self.time_left > 0:
            time.sleep(1)
            if self.is_running:
                self.time_left -= 1
                self.root.after(0, self.update_timer_display)
        
        if self.time_left <= 0:
            self.root.after(0, self.timer_complete)
    
    def timer_complete(self):
        self.pause_timer()
        if self.is_work_mode:
            work_minutes = int(self.work_time_input.get())
            self.stats["completed_seconds"] += work_minutes * 60
            self.stats["sessions_completed"] += 1
            self.stats["last_date"] = self.get_today_date()
            self.save_stats()
            # Play sound (simple beep)
            self.root.bell()
            self.is_work_mode = False
            self.time_left = int(self.break_time_input.get()) * 60
        else:
            self.root.bell()
            self.is_work_mode = True
            self.time_left = int(self.work_time_input.get()) * 60
        
        self.update_mode_label()
        self.update_timer_display()
    
    def new_quote(self):
        quote = random.choice(self.quotes)
        self.quote_label.configure(text=f'"{quote}"')
    
    def save_quote(self):
        quote = tk.simpledialog.askstring("New Quote", "Add a new quote:")
        if quote and quote.strip():
            self.quotes.insert(0, quote.strip())
            self.save_quotes()
            self.new_quote()
    
    def load_quotes(self):
        try:
            quotes_path = self.get_data_path(self.QUOTES_KEY)
            if quotes_path.exists():
                with open(quotes_path, 'r') as f:
                    self.quotes = json.load(f)
        except:
            pass
    
    def save_quotes(self):
        try:
            quotes_path = self.get_data_path(self.QUOTES_KEY)
            with open(quotes_path, 'w') as f:
                json.dump(self.quotes, f)
        except:
            pass
    
    def load_journal(self):
        try:
            journal_path = self.get_data_path(self.JOURNAL_KEY)
            if journal_path.exists():
                with open(journal_path, 'r') as f:
                    self.journal_text.insert("0.0", f.read())
        except:
            pass
    
    def save_journal(self):
        try:
            journal_path = self.get_data_path(self.JOURNAL_KEY)
            with open(journal_path, 'w') as f:
                f.write(self.journal_text.get("0.0", "end").strip())
            self.save_journal_btn.configure(text="Saved ✔")
            self.root.after(1200, lambda: self.save_journal_btn.configure(text="Save Journal"))
        except:
            messagebox.showerror("Error", "Failed to save journal.")
    
    def load_todos(self):
        try:
            tasks_path = self.get_data_path(self.TASKS_KEY)
            if tasks_path.exists():
                with open(tasks_path, 'r') as f:
                    tasks = json.load(f)
                    self.render_todos(tasks)
        except:
            self.render_todos([])
    
    def save_todos(self, tasks):
        try:
            tasks_path = self.get_data_path(self.TASKS_KEY)
            with open(tasks_path, 'w') as f:
                json.dump(tasks, f)
        except:
            pass
    
    def add_task(self):
        text = self.todo_input.get().strip()
        if not text:
            return
        
        tasks = self.get_todos()
        tasks.append({
            "id": str(time.time()),
            "text": text,
            "done": False,
            "created_at": time.time()
        })
        self.save_todos(tasks)
        self.todo_input.delete(0, "end")
        self.render_todos(tasks)
    
    def get_todos(self):
        try:
            tasks_path = self.get_data_path(self.TASKS_KEY)
            if tasks_path.exists():
                with open(tasks_path, 'r') as f:
                    return json.load(f)
            return []
        except:
            return []
    
    def render_todos(self, tasks):
        # Clear existing
        for widget in self.todo_listbox.winfo_children():
            widget.destroy()
        
        incomplete = [t for t in tasks if not t["done"]]
        complete = [t for t in tasks if t["done"]]
        
        for task in incomplete + complete:
            task_frame = ctk.CTkFrame(
                self.todo_listbox,
                fg_color="rgba(255,255,255,0.05)",
                border_width=1,
                border_color="rgba(255,255,255,0.06)",
                corner_radius=10,
                height=50
            )
            task_frame.pack(fill="x", padx=8, pady=4)
            task_frame.pack_propagate(False)
            
            # Left section
            left_frame = ctk.CTkFrame(task_frame, fg_color="transparent")
            left_frame.pack(side="left", fill="x", expand=True, padx=12, pady=8)
            
            checkbox = ctk.CTkButton(
                left_frame,
                text="✓" if task["done"] else "",
                width=32,
                height=32,
                fg_color="transparent" if not task["done"] else "#6ef0c9",
                border_width=2 if not task["done"] else 0,
                border_color="rgba(255,255,255,0.12)",
                text_color="#042726" if task["done"] else "transparent",
                font=ctk.CTkFont(size=14, weight="bold"),
                command=lambda t=task: self.toggle_task(t["id"])
            )
            checkbox.pack(side="left", padx=(0,12))
            
            desc_label = ctk.CTkLabel(
                left_frame,
                text=task["done"] and "line-through" or task["text"],
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            desc_label.pack(side="left", fill="x", expand=True)
            
            meta_label = ctk.CTkLabel(
                left_frame,
                text="Completed" if task["done"] else "Quest",
                font=ctk.CTkFont(size=12),
                text_color="#9adbd4"
            )
            meta_label.pack(side="right")
            
            # Delete button
            del_btn = ctk.CTkButton(
                task_frame,
                text="✕",
                width=32,
                height=32,
                fg_color="#ff5a5a",
                hover_color="#ff7272",
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda t=task: self.delete_task(t["id"])
            )
            del_btn.pack(side="right", padx=12, pady=8)
    
    def toggle_task(self, task_id):
        tasks = self.get_todos()
        for task in tasks:
            if task["id"] == task_id:
                task["done"] = not task["done"]
                break
        self.save_todos(tasks)
        self.render_todos(tasks)
    
    def delete_task(self, task_id):
        tasks = self.get_todos()
        tasks = [t for t in tasks if t["id"] != task_id]
        self.save_todos(tasks)
        self.render_todos(tasks)
    
    def end_day(self):
        hours = (self.stats["completed_seconds"] / 3600)
        sessions = self.stats["sessions_completed"]
        summary = f"Today you completed {sessions} session{'s' if sessions != 1 else ''}\nand studied {hours:.2f} hour{'s' if hours != 1.0 else ''}."
        
        self.summary_label.configure(text=summary)
        self.overlay.attributes("-alpha", 1.0)
        self.overlay.deiconify()
        self.overlay.lift()
    
    def close_end_day(self):
        self.overlay.attributes("-alpha", 0.0)
        self.overlay.withdraw()
    
    def run(self):
        # Bind events
        self.work_time_input.bind("<KeyRelease>", lambda e: self.update_work_time())
        self.break_time_input.bind("<KeyRelease>", lambda e: self.update_break_time())
        self.todo_input.bind("<Return>", lambda e: self.add_task())
        self.overlay.bind("<Escape>", lambda e: self.close_end_day())
        self.overlay.protocol("WM_DELETE_WINDOW", self.close_end_day)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def update_work_time(self):
        if not self.is_running and self.is_work_mode:
            self.time_left = int(self.work_time_input.get()) * 60
            self.update_timer_display()
    
    def update_break_time(self):
        if not self.is_running and not self.is_work_mode:
            self.time_left = int(self.break_time_input.get()) * 60
            self.update_timer_display()
    
    def on_closing(self):
        self.save_journal()
        self.save_stats()
        self.root.destroy()

if __name__ == "__main__":
    app = GrindForgeApp()
    app.run()
