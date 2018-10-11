from time import time
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
    current_title = StringProperty()
    time = NumericProperty(0)
    
    def build(self):
        self.title = 'Smartie Pi Hub'
        return SmartiePiHub()

if __name__ == '__main__':
    SmartiePiApp().run()