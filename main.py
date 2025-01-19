from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock


class Pomodoro(BoxLayout):
    time = NumericProperty(25 * 60)  # 25 minutes for work
    break_time = NumericProperty(5 * 60)  # 5 minutes for break
    mode = StringProperty("WORK")  # Current mode (WORK/BREAK)
    is_running = False

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
            self.time = 25 * 60
        else:
            self.time = 5 * 60

    def switch_mode(self):
        self.stop_timer()
        if self.mode == "WORK":
            self.mode = "BREAK"
            self.time = self.break_time
        else:
            self.mode = "WORK"
            self.time = 25 * 60

    def update_time(self, dt):
        if self.time > 0:
            self.time -= 1
        else:
            self.stop_timer()
            print("Time's up!")


class PomodoroApp(App):
    def build(self):
        return Pomodoro()


if __name__ == "__main__":
    PomodoroApp().run()
