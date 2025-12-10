#!/usr/bin/env python3
"""
Pomodoro Timer App
シンプルなポモドーロタイマー（25分作業 / 5分休憩）
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading


class PomodoroTimer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🍅 Pomodoro Timer")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        # Timer settings (seconds)
        self.work_time = 25 * 60      # 25分
        self.short_break = 5 * 60     # 5分
        self.long_break = 15 * 60     # 15分

        # State
        self.time_left = self.work_time
        self.is_running = False
        self.is_work_session = True
        self.sessions_completed = 0
        self.timer_thread = None

        self.setup_ui()

    def setup_ui(self):
        # Style
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Helvetica", 24, "bold"))
        style.configure("Timer.TLabel", font=("Helvetica", 72, "bold"))
        style.configure("Status.TLabel", font=("Helvetica", 14))
        style.configure("Big.TButton", font=("Helvetica", 14))

        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="🍅 Pomodoro Timer",
            style="Title.TLabel"
        )
        title_label.pack(pady=10)

        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="作業時間",
            style="Status.TLabel"
        )
        self.status_label.pack(pady=5)

        # Timer display
        self.timer_label = ttk.Label(
            main_frame,
            text="25:00",
            style="Timer.TLabel",
            foreground="#e74c3c"
        )
        self.timer_label.pack(pady=30)

        # Sessions counter
        self.sessions_label = ttk.Label(
            main_frame,
            text="完了セッション: 0",
            style="Status.TLabel"
        )
        self.sessions_label.pack(pady=5)

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=20)

        # Start/Pause button
        self.start_btn = ttk.Button(
            buttons_frame,
            text="▶ スタート",
            command=self.toggle_timer,
            style="Big.TButton",
            width=12
        )
        self.start_btn.grid(row=0, column=0, padx=5)

        # Reset button
        self.reset_btn = ttk.Button(
            buttons_frame,
            text="↺ リセット",
            command=self.reset_timer,
            style="Big.TButton",
            width=12
        )
        self.reset_btn.grid(row=0, column=1, padx=5)

        # Skip button
        self.skip_btn = ttk.Button(
            buttons_frame,
            text="⏭ スキップ",
            command=self.skip_session,
            style="Big.TButton",
            width=12
        )
        self.skip_btn.grid(row=0, column=2, padx=5)

        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="設定（分）", padding=10)
        settings_frame.pack(pady=20, fill=tk.X)

        # Work time setting
        ttk.Label(settings_frame, text="作業時間:").grid(row=0, column=0, padx=5)
        self.work_spinbox = ttk.Spinbox(
            settings_frame, from_=1, to=60, width=5,
            command=self.update_settings
        )
        self.work_spinbox.set(25)
        self.work_spinbox.grid(row=0, column=1, padx=5)

        # Short break setting
        ttk.Label(settings_frame, text="短い休憩:").grid(row=0, column=2, padx=5)
        self.short_spinbox = ttk.Spinbox(
            settings_frame, from_=1, to=30, width=5,
            command=self.update_settings
        )
        self.short_spinbox.set(5)
        self.short_spinbox.grid(row=0, column=3, padx=5)

        # Long break setting
        ttk.Label(settings_frame, text="長い休憩:").grid(row=1, column=0, padx=5, pady=5)
        self.long_spinbox = ttk.Spinbox(
            settings_frame, from_=1, to=60, width=5,
            command=self.update_settings
        )
        self.long_spinbox.set(15)
        self.long_spinbox.grid(row=1, column=1, padx=5, pady=5)

    def update_settings(self):
        """Update timer settings from spinboxes"""
        if not self.is_running:
            try:
                self.work_time = int(self.work_spinbox.get()) * 60
                self.short_break = int(self.short_spinbox.get()) * 60
                self.long_break = int(self.long_spinbox.get()) * 60
                if self.is_work_session:
                    self.time_left = self.work_time
                    self.update_display()
            except ValueError:
                pass

    def format_time(self, seconds):
        """Format seconds to MM:SS"""
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    def update_display(self):
        """Update the timer display"""
        self.timer_label.config(text=self.format_time(self.time_left))

        if self.is_work_session:
            self.timer_label.config(foreground="#e74c3c")  # Red for work
            self.status_label.config(text="🔴 作業時間")
        else:
            self.timer_label.config(foreground="#27ae60")  # Green for break
            if self.sessions_completed % 4 == 0 and self.sessions_completed > 0:
                self.status_label.config(text="🟢 長い休憩")
            else:
                self.status_label.config(text="🟢 休憩時間")

        self.sessions_label.config(text=f"完了セッション: {self.sessions_completed}")

    def toggle_timer(self):
        """Start or pause the timer"""
        if self.is_running:
            self.is_running = False
            self.start_btn.config(text="▶ スタート")
        else:
            self.is_running = True
            self.start_btn.config(text="⏸ 一時停止")
            self.run_timer()

    def run_timer(self):
        """Run the timer in a separate thread"""
        def countdown():
            while self.is_running and self.time_left > 0:
                time.sleep(1)
                if self.is_running:
                    self.time_left -= 1
                    self.root.after(0, self.update_display)

            if self.time_left == 0 and self.is_running:
                self.root.after(0, self.timer_finished)

        self.timer_thread = threading.Thread(target=countdown, daemon=True)
        self.timer_thread.start()

    def timer_finished(self):
        """Handle timer completion"""
        self.is_running = False
        self.start_btn.config(text="▶ スタート")

        if self.is_work_session:
            self.sessions_completed += 1
            if self.sessions_completed % 4 == 0:
                self.time_left = self.long_break
                messagebox.showinfo("🎉 お疲れさま！", "4セッション完了！\n長い休憩を取りましょう。")
            else:
                self.time_left = self.short_break
                messagebox.showinfo("✅ 完了", "作業セッション完了！\n短い休憩を取りましょう。")
            self.is_work_session = False
        else:
            self.time_left = self.work_time
            messagebox.showinfo("💪 準備OK", "休憩終了！\n次の作業セッションを始めましょう。")
            self.is_work_session = True

        self.update_display()

    def reset_timer(self):
        """Reset the current timer"""
        self.is_running = False
        self.start_btn.config(text="▶ スタート")

        if self.is_work_session:
            self.time_left = self.work_time
        else:
            if self.sessions_completed % 4 == 0 and self.sessions_completed > 0:
                self.time_left = self.long_break
            else:
                self.time_left = self.short_break

        self.update_display()

    def skip_session(self):
        """Skip to the next session"""
        self.is_running = False
        self.timer_finished()

    def run(self):
        """Start the application"""
        self.update_display()
        self.root.mainloop()


if __name__ == "__main__":
    app = PomodoroTimer()
    app.run()
