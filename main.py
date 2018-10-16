import time
from kivy.app import App
from kivy.uix.widget import Widget
from os.path import dirname, join
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty,\
    ListProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen

class SmartiePiHub(Widget):
    pass

class SmartiePiApp(App):
    def build(self):
        hub = SmartiePiHub()
        self.title = 'SmartiePi Hub'
        Clock.schedule_interval(self.update_clock, 1 / 60.)
        return hub
        
    def update_clock(self, dt):
        self.root.ids.date_and_time.text = time.strftime("%I:%M %p\n%m/%d/%Y")
        

if __name__ == '__main__':
    SmartiePiApp().run()