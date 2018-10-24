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
from kivy.uix.boxlayout import BoxLayout
import sqlite3



db_file = 'smartiepi.db'

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
        
        self.bind_node_messages()

    def bind_node_messages(self):
        con = sqlite3.connect(db_file)
        cur = con.cursor()

        app= App.get_running_app()
        cur.execute("select n.Name as Node, m.Message, nm.TimeStamp, nm.Id as NodeMessageId from NodeMessages nm inner join Messages m on nm.MessageId = m.Id inner join Nodes n on n.Id = nm.NodeId order by nm.id desc")
        
        rows = cur.fetchall()
        con.close()
        #using try block instead of hasattr for attribute checking here because most of the time this will not fail
        try:
            app.root.ids.main_view.data = [{'Node':"{}".format(Node), 'Message':"{}".format(Message), 'TimeStamp':"{}".format(TimeStamp), 'NodeMessageId':"{}".format(NodeMessageId)} for Node, Message, TimeStamp, NodeMessageId in rows]
        except AttributeError:
            self.data = [{'Node':"{}".format(Node), 'Message':"{}".format(Message), 'TimeStamp':"{}".format(TimeStamp), 'NodeMessageId':"{}".format(NodeMessageId)} for Node, Message, TimeStamp, NodeMessageId in rows]

class MessageView(RecycleDataViewBehavior, BoxLayout):
    
    Node = StringProperty("")
    Message = StringProperty("")
    TimeStamp = StringProperty("")
    NodeMessageId = StringProperty("")

    index = None

    def delete_node_message(self,node_message_id):
        print(node_message_id)
        con = sqlite3.connect(db_file)
        cur = con.cursor()

        app= App.get_running_app()
        cur.execute("delete from nodemessages where id = {id}".\
        format(id=node_message_id))
        
        con.commit()
        con.close()

        self.parent.parent.bind_node_messages()

        

    def view_node_message(self,data):
        print(data)


if __name__ == '__main__':
    SmartiePiApp().run()