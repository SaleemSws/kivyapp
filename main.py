from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    NumericProperty,
    StringProperty,
    ListProperty,
    ObjectProperty,
    BoundedNumericProperty,
)
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.core.audio import SoundLoader
from kivy.animation import Animation
from kivy.resources import resource_add_path
from kivy.uix.video import Video
from kivy.uix.floatlayout import FloatLayout
import os
import json
from datetime import datetime, timedelta
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
import random
from kivy.uix.image import Image


WORK_MOTIVATIONS = [
    "Great job staying focused!",
    "You're making progress!",
    "One step closer to your goals!",
    "Consistency is key!",
    "Productivity champion!",
    "Keep crushing your tasks!",
    "Your hard work pays off!",
]

BREAK_MOTIVATIONS = [
    "Well-deserved break!",
    "Rest and recharge!",
    "Self-care is important!",
    "Mental health matters!",
    "Relaxation boosts productivity!",
    "Take a moment to breathe!",
    "You've earned this break!",
]

ICONS = {
    "WORK": ["trophy.png", "rocket.png", "target.png", "success.png"],
    "BREAK": ["relax.png", "meditation.png", "coffee.png", "refresh.png"],
}


def get_random_motivation(mode):
    if mode == "WORK":
        return random.choice(WORK_MOTIVATIONS)
    return random.choice(BREAK_MOTIVATIONS)


def get_random_icon(mode):
    return random.choice(ICONS[mode])


class PomodoroHistory:
    def __init__(self, filename="pomodoro_history.json"):
        self.filename = filename
        self.history = self.load_history()

    def load_history(self):
        """Load history from JSON file or create a new one if it doesn't exist."""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r") as f:
                    history = json.load(f)

                    # Add default values if not present
                    if "current_progress" not in history:
                        history["current_progress"] = {
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "minutes_completed": 0,
                            "last_updated": datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        }

                    return history
            else:
                return {
                    "daily_records": [],
                    "total_work_time": 0,
                    "total_break_time": 0,
                    "current_progress": {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "minutes_completed": 0,
                        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    },
                }
        except (json.JSONDecodeError, IOError):
            return {
                "daily_records": [],
                "total_work_time": 0,
                "total_break_time": 0,
                "current_progress": {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "minutes_completed": 0,
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
            }

    def update_current_progress(self, minutes_completed):
        """Update current progress"""
        today = datetime.now().strftime("%Y-%m-%d")

        # Check if it's the same day
        if self.history["current_progress"]["date"] != today:
            # Reset if it's a new day
            self.history["current_progress"] = {
                "date": today,
                "minutes_completed": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        # Update minutes completed
        self.history["current_progress"]["minutes_completed"] = minutes_completed
        self.history["current_progress"]["last_updated"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        self.save_history()

    def get_current_progress(self):
        """Get current progress"""
        today = datetime.now().strftime("%Y-%m-%d")

        # Check if it's the same day
        if self.history["current_progress"]["date"] != today:
            # Reset if it's a new day
            return 0

        return self.history["current_progress"]["minutes_completed"]

    def record_session(self, mode, duration):
        """Record a completed Pomodoro session."""
        today = datetime.now().strftime("%Y-%m-%d")

        # Find today's record or create a new one
        today_record = next(
            (
                record
                for record in self.history["daily_records"]
                if record["date"] == today
            ),
            None,
        )

        if not today_record:
            today_record = {"date": today, "work_time": 0, "break_time": 0}
            self.history["daily_records"].append(today_record)

        # Update the record based on mode
        if mode == "WORK":
            today_record["work_time"] += duration
            self.history["total_work_time"] += duration
        else:
            today_record["break_time"] += duration
            self.history["total_break_time"] += duration

        # Remove old records (keep last 30 days)
        self.prune_old_records()

        self.save_history()

    def prune_old_records(self):
        """Remove records older than 30 days."""
        thirty_days_ago = datetime.now() - timedelta(days=30)
        self.history["daily_records"] = [
            record
            for record in self.history["daily_records"]
            if datetime.strptime(record["date"], "%Y-%m-%d") >= thirty_days_ago
        ]

    def get_daily_summary(self, days=7):
        """Get summary of work time for the last specified number of days."""
        today = datetime.now()
        summary = []

        for i in range(days):
            check_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            day_record = next(
                (
                    record
                    for record in self.history["daily_records"]
                    if record["date"] == check_date
                ),
                None,
            )

            summary.append(
                {
                    "date": check_date,
                    "work_time": day_record["work_time"] if day_record else 0,
                    "break_time": day_record["break_time"] if day_record else 0,
                }
            )

        return summary

    def save_history(self):
        """Save history to JSON file."""
        try:
            with open(self.filename, "w") as f:
                json.dump(self.history, f, indent=4)
        except IOError:
            print("Could not save history file")

    def get_total_time_stats(self):
        """Get total work and break time across all records."""
        return {
            "total_work_time": self.history["total_work_time"],
            "total_break_time": self.history["total_break_time"],
        }


class VideoBackground(Video):
    volume = BoundedNumericProperty(0, min=0, max=1)

    def __init__(self, **kwargs):
        super(VideoBackground, self).__init__(**kwargs)
        self.state = "play"
        self.options = {"eos": "loop"}
        self.allow_stretch = True
        self.keep_ratio = False
        self.volume = 0


class PomodoroRoot(FloatLayout):
    video_widget = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PomodoroRoot, self).__init__(**kwargs)
        self.video_widget = VideoBackground(source="background.mp4")
        self.add_widget(self.video_widget)
        self.pomodoro = Pomodoro()
        self.add_widget(self.pomodoro)

    def increase_volume(self):
        self.video_widget.volume = min(1.0, self.video_widget.volume + 0.1)

    def decrease_volume(self):
        self.video_widget.volume = max(0.0, self.video_widget.volume - 0.1)

    def toggle_mute(self):
        if self.video_widget.volume > 0:
            self._previous_volume = self.video_widget.volume
            self.video_widget.volume = 0
        else:
            self.video_widget.volume = getattr(self, "_previous_volume", 0.5)


class TimesUpPopup(Popup):
    def __init__(self, mode, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.8, 0.5)
        self.auto_dismiss = False

        # Get random motivation and icon
        motivation = get_random_motivation(mode)
        icon = get_random_icon(mode)

        # Set properties to be used in the KV file
        self.ids.motivation_label.text = motivation
        self.ids.icon_image.source = icon
        self.ids.motivation_label.color = (
            (0.2, 0.8, 0.2, 1) if mode == "WORK" else (0.2, 0.2, 0.8, 1)
        )


class Pomodoro(BoxLayout):
    time = NumericProperty(25 * 60)
    break_time = NumericProperty(5 * 60)
    mode = StringProperty("WORK")
    work_duration = NumericProperty(25)
    break_duration = NumericProperty(5)
    daily_goal_hours = NumericProperty(4)
    minutes_completed = NumericProperty(0)
    progress_color = ListProperty([0.3, 0.6, 1, 1])
    is_running = False

    def __init__(self, **kwargs):
        super(Pomodoro, self).__init__(**kwargs)
        self.load_sounds()

        # Initialize history tracking
        self.history_tracker = PomodoroHistory()

        # Start with current progress from history
        self.minutes_completed = self.history_tracker.get_current_progress()
        self.update_progress_bar()

        # New properties to track session details
        self.current_session_duration = 0
        self.last_update_time = 0

    def load_sounds(self):
        sound_file = "alert.mp3"
        try:
            self.timer_sound = SoundLoader.load(sound_file)
        except:
            print("Could not load sound file")
            self.timer_sound = None

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.last_update_time = 0  # Reset tracking for this session
            self.current_session_duration = 0
            Clock.schedule_interval(self.update_time, 1)

    def stop_timer(self):
        if self.is_running:
            self.is_running = False
            Clock.unschedule(self.update_time)

    def reset_timer(self):
        self.stop_timer()
        if self.mode == "WORK":
            self.time = self.work_duration * 60
        else:
            self.time = self.break_duration * 60

    def switch_mode(self):
        # Record the current session before switching
        if self.current_session_duration > 0:
            session_duration = self.current_session_duration // 60
            if self.mode == "WORK":
                self.history_tracker.record_session("WORK", session_duration)
            else:
                self.history_tracker.record_session("BREAK", session_duration)

        # Existing switch mode logic
        self.stop_timer()
        if self.mode == "WORK":
            completed_time = self.work_duration - (self.time // 60)
            if completed_time > 0:
                self.animate_progress_update(completed_time)
            self.mode = "BREAK"
            self.time = self.break_duration * 60
        else:
            self.mode = "WORK"
            self.time = self.work_duration * 60

        # Reset session tracking
        self.current_session_duration = 0

    def update_progress_bar(self):
        progress = min(self.minutes_completed / (self.daily_goal_hours * 60), 1.0) * 100

        if progress < 30:
            self.progress_color = [0.3, 0.6 + (progress / 30 * 0.3), 1, 1]
        elif progress < 70:
            ratio = (progress - 30) / 40
            self.progress_color = [0.3 - (ratio * 0.2), 0.9, 1 - (ratio * 0.5), 1]
        else:
            ratio = (progress - 70) / 30
            self.progress_color = [0.1, 0.9 + (ratio * 0.1), 0.5 - (ratio * 0.3), 1]

    def animate_progress_update(self, completed_minutes):
        # Add new progress
        target_minutes = min(
            self.minutes_completed + completed_minutes, self.daily_goal_hours * 60
        )

        # Save current progress
        self.history_tracker.update_current_progress(target_minutes)

        # Original animation
        anim = Animation(
            minutes_completed=target_minutes, duration=0.5, transition="out_bounce"
        )
        anim.start(self)
        Clock.schedule_once(lambda dt: self.update_progress_bar(), 0.5)

    def update_time(self, dt):
        if self.time > 0:
            self.time -= 1
            self.current_session_duration += 1
        else:
            self.stop_timer()
            self.play_alert()

            # Create and open the popup
            popup = TimesUpPopup(mode=self.mode)
            popup.open()

            # Record the completed session
            if self.mode == "WORK":
                self.animate_progress_update(self.work_duration)
                self.history_tracker.record_session("WORK", self.work_duration)
            else:
                self.history_tracker.record_session("BREAK", self.break_duration)

            print("Time's up!")

    def play_alert(self):
        if self.timer_sound:
            self.timer_sound.play()

    def set_work_duration(self, duration_text):
        try:
            duration = int(duration_text)
            if 1 <= duration <= 120:
                self.work_duration = duration
                if self.mode == "WORK":
                    self.time = duration * 60
        except ValueError:
            pass

    def set_break_duration(self, duration_text):
        try:
            duration = int(duration_text)
            if 1 <= duration <= 30:
                self.break_duration = duration
                if self.mode == "BREAK":
                    self.time = duration * 60
        except ValueError:
            pass

    def set_daily_goal(self, goal_text):
        try:
            goal = int(goal_text)
            if 1 <= goal <= 24:
                self.daily_goal_hours = goal
        except ValueError:
            pass

    def reset_daily_progress(self):
        anim = Animation(minutes_completed=0, duration=0.5, transition="in_out_cubic")
        anim.start(self)
        # Also reset the stored progress in history
        self.history_tracker.update_current_progress(0)

    def get_history_summary(self):
        """
        Get a summary of recent history for displaying in the app.

        Returns:
        dict: A dictionary with recent history details
        """
        daily_summary = self.history_tracker.get_daily_summary()
        total_stats = self.history_tracker.get_total_time_stats()

        return {
            "daily_summary": daily_summary,
            "total_work_time": total_stats["total_work_time"],
            "total_break_time": total_stats["total_break_time"],
        }


class PomodoroApp(App):
    def build(self):
        return PomodoroRoot()


if __name__ == "__main__":
    PomodoroApp().run()
