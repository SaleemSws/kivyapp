from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.core.audio import SoundLoader
from kivy.animation import Animation
from kivy.resources import resource_add_path
import os


class CustomProgressBar(BoxLayout):
    value = NumericProperty(0)
    max = NumericProperty(100)
    progress_color = ListProperty([0.3, 0.6, 1, 1])  # เริ่มต้นด้วยสีฟ้า

    def on_value(self, instance, value):
        # คำนวณสีตามความคืบหน้า
        progress_ratio = value / self.max if self.max > 0 else 0
        if progress_ratio < 0.5:
            # ไล่จากสีฟ้าไปสีเขียวอ่อน
            self.progress_color = [
                0.3,
                0.6 + (progress_ratio * 0.8),
                1 - (progress_ratio * 0.5),
                1,
            ]
        else:
            # ไล่จากสีเขียวอ่อนไปสีเขียวเข้ม
            self.progress_color = [0.3, 1, 0.5 - ((progress_ratio - 0.5) * 0.5), 1]


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
            # เพิ่มเวลาที่ทำเสร็จและแสดงเอฟเฟกต์
            completed_time = self.work_duration - (self.time // 60)
            if completed_time > 0:
                self.animate_progress_update(completed_time)
            self.mode = "BREAK"
            self.time = self.break_duration * 60
        else:
            self.mode = "WORK"
            self.time = self.work_duration * 60

    def animate_progress_update(self, completed_minutes):
        # สร้างแอนิเมชันสำหรับการอัพเดตความคืบหน้า
        target_minutes = self.minutes_completed + completed_minutes
        anim = Animation(
            minutes_completed=target_minutes, duration=0.5, transition="out_bounce"
        )
        anim.start(self)

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
        return Pomodoro()


if __name__ == "__main__":
    PomodoroApp().run()
