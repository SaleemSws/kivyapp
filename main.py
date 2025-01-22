from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    NumericProperty,
    StringProperty,
    ListProperty,
    ObjectProperty,
)
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.core.audio import SoundLoader
from kivy.animation import Animation
from kivy.resources import resource_add_path
from kivy.uix.video import Video
from kivy.uix.floatlayout import FloatLayout
import os


class VideoBackground(Video):
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
        self.video_widget = VideoBackground(
            source="background.mp4"
        )  # Replace with your video file
        self.add_widget(self.video_widget)
        # Add the main Pomodoro interface on top
        self.pomodoro = Pomodoro()
        self.add_widget(self.pomodoro)


class CustomProgressBar(BoxLayout):
    value = NumericProperty(0)
    max = NumericProperty(100)
    progress_color = ListProperty([0.3, 0.6, 1, 1])  # Start with blue

    def on_value(self, instance, value):
        # Ensure progress doesn't exceed 100%
        progress_ratio = min(value / self.max, 1.0) if self.max > 0 else 0

        if progress_ratio < 0.3:
            # Blue to light blue (0-30%)
            self.progress_color = [0.3, 0.6 + (progress_ratio * 1.0), 1, 1]
        elif progress_ratio < 0.7:
            # Light blue to light green (30-70%)
            ratio = (progress_ratio - 0.3) / 0.4
            self.progress_color = [0.3 - (ratio * 0.2), 0.9, 1 - (ratio * 0.5), 1]
        else:
            # Light green to vibrant green (70-100%)
            ratio = (progress_ratio - 0.7) / 0.3
            self.progress_color = [0.1, 0.9 + (ratio * 0.1), 0.5 - (ratio * 0.3), 1]


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

    def update_progress_bar(self):
        # Calculate progress percentage with maximum cap at 100%
        progress = min(self.minutes_completed / (self.daily_goal_hours * 60), 1.0) * 100

        # Update progress color based on completion
        if progress < 30:
            self.progress_color = [0.3, 0.6 + (progress / 30 * 0.3), 1, 1]
        elif progress < 70:
            ratio = (progress - 30) / 40
            self.progress_color = [0.3 - (ratio * 0.2), 0.9, 1 - (ratio * 0.5), 1]
        else:
            ratio = (progress - 70) / 30
            self.progress_color = [0.1, 0.9 + (ratio * 0.1), 0.5 - (ratio * 0.3), 1]

    def animate_progress_update(self, completed_minutes):
        # Cap the progress at the daily goal
        target_minutes = min(
            self.minutes_completed + completed_minutes, self.daily_goal_hours * 60
        )
        anim = Animation(
            minutes_completed=target_minutes, duration=0.5, transition="out_bounce"
        )
        anim.start(self)
        Clock.schedule_once(lambda dt: self.update_progress_bar(), 0.5)

    def update_time(self, dt):
        if self.time > 0:
            self.time -= 1
        else:
            self.stop_timer()
            self.play_alert()
            if self.mode == "WORK":
                self.animate_progress_update(self.work_duration)
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


class PomodoroApp(App):
    def build(self):
        return PomodoroRoot()


if __name__ == "__main__":
    PomodoroApp().run()
