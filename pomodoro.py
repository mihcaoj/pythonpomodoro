import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk


class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("")
        self.root.geometry("380x260")

        # Disable window resizing, minimizing, and maximizing
        root.resizable(False, False)

        self.pomodoro_durations = [15, 25, 30, 45, 60, 90]  # List of durations
        self.break_durations = [5, 10, 15]  # List of break durations
        self.selected_duration = tk.StringVar(value=25)  # Default session duration
        self.selected_break_duration = tk.StringVar(value=5)  # Default break duration
        self.num_sessions = tk.StringVar(value=4)

        # Create a top-level menu accessible on the top right
        top_menu = tk.Menu(root)
        root.config(menu=top_menu)

        # Create a Duration submenu
        pomodoro_menu = tk.Menu(top_menu, tearoff=0)
        top_menu.add_cascade(label="Duration", menu=pomodoro_menu)

        # Add Pomodoro durations to the submenu
        for duration in self.pomodoro_durations:
            pomodoro_menu.add_radiobutton(
                label=f"{duration} minutes",
                variable=self.selected_duration,
                value=duration,
                command=self.reset_timer_on_duration_change,
            )

        # Create a Break Duration submenu
        break_menu = tk.Menu(top_menu, tearoff=0)
        top_menu.add_cascade(label="Break Duration", menu=break_menu)

        # Add break durations to the submenu
        for duration in self.break_durations:
            break_menu.add_radiobutton(
                label=f"{duration} minutes",
                variable=self.selected_break_duration,
                value=duration,
                command=self.reset_timer_on_duration_change,
            )

        # Create a Number of Sessions submenu
        num_sessions_menu = tk.Menu(top_menu, tearoff=0)
        top_menu.add_cascade(label="Number of Sessions", menu=num_sessions_menu)
        for sessions in range(1, 11):
            num_sessions_menu.add_radiobutton(label=str(sessions), variable=self.num_sessions, value=sessions)

        # Create a Reset submenu
        reset_menu = tk.Menu(top_menu, tearoff=0)
        top_menu.add_cascade(label="Reset", menu=reset_menu)

        # Add options to reset the timer or session count
        reset_menu.add_command(label="Reset Timer", command=self.reset_timer)
        reset_menu.add_command(label="Reset Session Count", command=self.reset_session_count)

        # Load and resize button images
        play_button_image = Image.open("/Users/jbono/Documents/py/progs/pomodoro_images/play_button.png")
        play_button_image = play_button_image.resize((50, 50), Image.LANCZOS)
        self.play_icon = ImageTk.PhotoImage(play_button_image)

        pause_button_image = Image.open("/Users/jbono/Documents/py/progs/pomodoro_images/pause_button.png")
        pause_button_image = pause_button_image.resize((50, 50), Image.LANCZOS)
        self.pause_icon = ImageTk.PhotoImage(pause_button_image)

        # Create a frame to contain the buttons and center them
        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.BOTTOM, pady=20)

        # Create the play button with the play icon
        self.play_button = tk.Button(
            button_frame,
            image=self.play_icon,
            command=self.toggle_timer,
            borderwidth=0,  # Remove the border
            highlightthickness=0,  # Remove the highlight border
        )

        self.play_button.pack(side=tk.LEFT, padx=20)

        self.session_count = 0  # Initialize the session count
        self.session_label = tk.Label(root, text=f"Sessions: {self.session_count}", font=("Sans Serif", 16))
        self.session_label.pack(side=tk.TOP, pady=20)  # Display session count at the top

        self.timer_label = tk.Label(root, text="", font=("Sans Serif", 70))
        self.timer_label.pack(pady=20, padx=(100, 100))  # Center the timer label

        self.time_left = 0
        self.is_running = False
        self.timer_id = None  # Store the timer ID
        self.paused_time = 0  # Store the remaining time when paused
        self.current_state = "session"  # Initial state is a session

        # Initialize the timer label with the default duration
        default_duration = int(self.selected_duration.get()) * 60
        mins, secs = divmod(default_duration, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        self.timer_label.config(text=time_str)

    def toggle_timer(self):
        if self.is_running:
            self.is_running = False
            self.play_button.config(image=self.play_icon)
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
        else:
            if self.time_left > 0:
                # Resume timer from the remaining time
                self.is_running = True
                self.play_button.config(image=self.pause_icon)
                self.run_timer(self.time_left)
            else:
                # Start a new timer with the selected duration or break duration
                self.is_running = True
                self.play_button.config(image=self.pause_icon)
                if self.paused_time > 0:
                    # The timer was paused due to duration change or break
                    self.run_timer(self.paused_time)
                    self.paused_time = 0
                else:
                    if self.current_state == "session":
                        # Start a session timer with the selected duration
                        self.run_timer(int(self.selected_duration.get()) * 60)
                    else:
                        # Start a break timer with the selected break duration
                        self.run_timer(int(self.selected_break_duration.get()) * 60)

    def reset_timer(self):
        self.is_running = False
        self.play_button.config(image=self.play_icon)
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.time_left = 0
        self.paused_time = 0
        default_duration = int(self.selected_duration.get()) * 60  # Get the default duration
        self.update_timer_label(default_duration)

    def reset_session_count(self):
        self.session_count = 0
        self.session_label.config(text=f"Sessions: {self.session_count}")

    def run_timer(self, seconds):
        if seconds <= 0:
            return

        mins, secs = divmod(seconds, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        self.timer_label.config(text=time_str)

        self.time_left = seconds
        self.timer_id = self.root.after(1000, self.update_timer)

    def update_timer(self):
        self.time_left -= 1
        if self.time_left > 0:
            mins, secs = divmod(self.time_left, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            self.timer_label.config(text=time_str)
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.is_running = False
            if self.current_state == "session":
                self.handle_session_end()
            else:
                self.handle_break_end()

    def handle_session_end(self):
        self.session_count += 1
        self.session_label.config(text=f"Sessions: {self.session_count}")
        messagebox.showinfo("Pomodoro Timer", "Pomodoro session ended. Time for a break!")

        # Switch to break state
        self.current_state = "break"
        self.selected_duration.set(25)  # Reset session duration to default
        self.play_button.config(image=self.play_icon)
        self.run_timer(int(self.selected_break_duration.get()) * 60)

    def handle_break_end(self):
        messagebox.showinfo("Pomodoro Timer", "Break ended. Let's start a new session!")

        # Switch to session state
        self.current_state = "session"
        self.play_button.config(image=self.play_icon)
        self.run_timer(int(self.selected_duration.get()) * 60)

    def update_timer_label(self, seconds):
        mins, secs = divmod(seconds, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        self.timer_label.config(text=time_str)

    def update_timer_label_on_duration_change(self):
        new_duration = int(self.selected_duration.get()) * 60
        self.update_timer_label(new_duration)

        if not self.is_running:
            # Update the timer label without starting the timer
            self.paused_time = 0
            self.update_timer_label(new_duration)

    def reset_timer_on_duration_change(self):
        new_duration = int(self.selected_duration.get()) * 60
        if self.is_running:
            # If the timer is running, pause it and store the remaining time
            self.is_running = False
            self.play_button.config(image=self.play_icon)
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
            self.paused_time = self.time_left
            self.run_timer(new_duration)
        else:
            self.paused_time = 0
            self.reset_timer()
            self.update_timer_label(new_duration)


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()
