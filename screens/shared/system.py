from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty
from kivy.app import App

db_file = 'data/smartiepi.db'

class SmartiePiScreen(Screen):
    app= App.get_running_app()
    fullscreen = BooleanProperty(False)