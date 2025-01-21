# from kivy.app import App
# from kivy.uix.boxlayout import BoxLayout
# from kivy.properties import NumericProperty, StringProperty
# from kivy.clock import Clock
# from kivy.uix.textinput import TextInput
# from kivy.core.audio import SoundLoader
# from kivy.resources import resource_add_path
# import os


# class Pomodoro(BoxLayout):
#     time = NumericProperty(25 * 60)  # 25 minutes for work
#     break_time = NumericProperty(5 * 60)  # 5 minutes for break
#     mode = StringProperty("WORK")  # Current mode (WORK/BREAK)
#     work_duration = NumericProperty(25)  # Default work duration in minutes
#     break_duration = NumericProperty(5)  # Default break duration in minutes
#     is_running = False

#     def __init__(self, **kwargs):
#         super(Pomodoro, self).__init__(**kwargs)
#         # Load the sound file
#         self.load_sounds()

#     def load_sounds(self):
#         # Try to load the sound file
#         sound_file = "alert.mp3"  # You'll need to provide this sound file
#         try:
#             self.timer_sound = SoundLoader.load(sound_file)
#         except:
#             print("Could not load sound file")
#             self.timer_sound = None

#     def start_timer(self):
#         if not self.is_running:
#             self.is_running = True
#             Clock.schedule_interval(self.update_time, 1)

#     def stop_timer(self):
#         if self.is_running:
#             self.is_running = False
#             Clock.unschedule(self.update_time)

#     def reset_timer(self):
#         self.stop_timer()
#         if self.mode == "WORK":
#             self.time = self.work_duration * 60
#         else:
#             self.time = self.break_duration * 60

#     def switch_mode(self):
#         self.stop_timer()
#         if self.mode == "WORK":
#             self.mode = "BREAK"
#             self.time = self.break_duration * 60
#         else:
#             self.mode = "WORK"
#             self.time = self.work_duration * 60

#     def update_time(self, dt):
#         if self.time > 0:
#             self.time -= 1
#         else:
#             self.stop_timer()
#             self.play_alert()
#             print("Time's up!")

#     def play_alert(self):
#         if self.timer_sound:
#             self.timer_sound.play()

#     def set_work_duration(self, duration_text):
#         try:
#             duration = int(duration_text)
#             if 1 <= duration <= 120:  # Limit between 1 and 120 minutes
#                 self.work_duration = duration
#                 if self.mode == "WORK":
#                     self.time = duration * 60
#         except ValueError:
#             pass

#     def set_break_duration(self, duration_text):
#         try:
#             duration = int(duration_text)
#             if 1 <= duration <= 30:  # Limit between 1 and 30 minutes
#                 self.break_duration = duration
#                 if self.mode == "BREAK":
#                     self.time = duration * 60
#         except ValueError:
#             pass


# class PomodoroApp(App):
#     def build(self):
#         return Pomodoro()


# if __name__ == "__main__":
#     PomodoroApp().run()
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.core.audio import SoundLoader
from kivy.resources import resource_add_path
import os


class Pomodoro(BoxLayout):
    time = NumericProperty(25 * 60)  # 25 minutes for work
    break_time = NumericProperty(5 * 60)  # 5 minutes for break
    mode = StringProperty("WORK")  # Current mode (WORK/BREAK)
    work_duration = NumericProperty(25)  # Default work duration in minutes
    break_duration = NumericProperty(5)  # Default break duration in minutes
    daily_goal_hours = NumericProperty(4)  # Default daily goal in hours
    minutes_completed = NumericProperty(0)  # Minutes completed today
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
            # Add completed work time to daily progress
            self.minutes_completed += self.work_duration - (self.time // 60)
            self.mode = "BREAK"
            self.time = self.break_duration * 60
        else:
            self.mode = "WORK"
            self.time = self.work_duration * 60

    def update_time(self, dt):
        if self.time > 0:
            self.time -= 1
        else:
            self.stop_timer()
            self.play_alert()
            if self.mode == "WORK":
                # Add completed work session to daily progress
                self.minutes_completed += self.work_duration
            print("Time's up!")

    def play_alert(self):
        if self.timer_sound:
            self.timer_sound.play()

    def set_work_duration(self, duration_text):
        try:
            duration = int(duration_text)
            if 1 <= duration <= 120:  # Limit between 1 and 120 minutes
                self.work_duration = duration
                if self.mode == "WORK":
                    self.time = duration * 60
        except ValueError:
            pass

    def set_break_duration(self, duration_text):
        try:
            duration = int(duration_text)
            if 1 <= duration <= 30:  # Limit between 1 and 30 minutes
                self.break_duration = duration
                if self.mode == "BREAK":
                    self.time = duration * 60
        except ValueError:
            pass

    def set_daily_goal(self, goal_text):
        try:
            goal = int(goal_text)
            if 1 <= goal <= 24:  # Limit between 1 and 24 hours
                self.daily_goal_hours = goal
        except ValueError:
            pass

    def reset_daily_progress(self):
        self.minutes_completed = 0


class PomodoroApp(App):
    def build(self):
        return Pomodoro()


if __name__ == "__main__":
    PomodoroApp().run()
