import time
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from os.path import dirname, join
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import NumericProperty, StringProperty, BooleanProperty,\
    ListProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
import sqlite3


con = sqlite3.connect('smartiepi.db')
cur = con.cursor()


class SmartiePiHub(Widget):
    pass

class SmartiePiScreen(Screen):
    app= App.get_running_app()
    fullscreen = BooleanProperty(False)

class SmartiePiApp(App):
    index = NumericProperty(-1)
    current_title = StringProperty()
    screen_names = ListProperty([])
    rows = ListProperty([("NodeId","MessageId","TimeStamp")])

    def build(self):
        hub = SmartiePiHub()
        self.title = 'SmartiePi Hub'
        Clock.schedule_interval(self.update_clock, 1 / 60.)
        sm = hub.ids.sm
        self.screens = {}
        self.available_screens = sorted([
            'Main'])
        self.screen_names = self.available_screens
        curdir = dirname(__file__)
        self.available_screens = [join(curdir, 'screens',
            '{}.kv'.format(fn).lower()) for fn in self.available_screens]
        sm.switch_to(self.load_screen(0), direction='left') #load main screen
        return hub

    def go_screen(self, idx):
        self.index = idx
        self.root.ids.sm.switch_to(self.load_screen(idx), direction='left')
        
    def load_screen(self, index):
        if index in self.screens:
            return self.screens[index]
        screen = Builder.load_file(self.available_screens[index])
        self.screens[index] = screen
        return screen

    def update_clock(self, dt):
        self.root.ids.date_and_time.text = time.strftime("%I:%M %p\n%m/%d/%Y")

class MainRecycleView(RecycleView):
    def __init__(self, **kwargs):
        super(MainRecycleView, self).__init__(**kwargs)

        cur.execute("SELECT NodeId, MessageId, TimeStamp FROM NodeMessages ORDER by Id DESC")
        #self.rows = cur.fetchall()

        self.data = [{'text':"NodeId:{} MessageId:{} TimeStamp:{}".format(NodeId,MessageId,TimeStamp)} for NodeId,MessageId,TimeStamp in cur.fetchall()]
        #print(self.data)
        

if __name__ == '__main__':
    SmartiePiApp().run()