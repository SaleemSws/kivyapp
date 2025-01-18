from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.clock import Clock


class Pomodoro(BoxLayout):
    time = NumericProperty(25 * 60)  # ตั้งค่าเริ่มต้นเป็น 25 นาที (1500 วินาที)
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
