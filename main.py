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
    node_message_id = StringProperty()

    def build(self):
        self.app=App.get_running_app()
        hub = SmartiePiHub()
        self.title = 'SmartiePi Hub'
        Clock.schedule_interval(self.update_clock, 1 / 60.)
        sm = hub.ids.sm
        screen = self.get_screen_file('Main')
        sm.add_widget(screen)
        sm.current = 'Main'
        return hub
        
    def load_screen(self, screen_name):
        app= App.get_running_app()
        sm = app.root.ids.sm

        if sm.has_screen(screen_name):
            sm.current = screen_name
        else:
            screen = self.get_screen_file(screen_name)
            sm.add_widget(screen)
            sm.current = screen_name

    def get_screen_file(self, screen_name):
        con = sqlite3.connect(db_file)
        cur = con.cursor()
        curdir = dirname(__file__)

        cur.execute("select FileName from Screens where Name = '{Name}'".\
        format(Name=screen_name))
        file_name = cur.fetchone()
        con.close()
        
        screen = Builder.load_file("{}{}\\{}".format(curdir,'screens', file_name[0]))
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
        cur.execute("select n.Name as Node, m.Message, nm.TimeStamp, nm.Id as NodeMessageId, s.Name as ScreenName from NodeMessages nm inner join Messages m on nm.MessageId = m.Id inner join Nodes n on n.Id = nm.NodeId inner join Screens s on m.ScreenId = s.Id order by nm.id desc")
        
        rows = cur.fetchall()
        con.close()
        #using try block instead of hasattr for attribute checking here because most of the time this will not fail
        try:
            app.root.ids.main_view.data = [{'Node':"{}".format(Node), 'Message':"{}".format(Message), 'TimeStamp':"{}".format(TimeStamp), 'NodeMessageId':"{}".format(NodeMessageId), 'ScreenName':"{}".format(ScreenName)} for Node, Message, TimeStamp, NodeMessageId, ScreenName in rows]
        except AttributeError:
            self.data = [{'Node':"{}".format(Node), 'Message':"{}".format(Message), 'TimeStamp':"{}".format(TimeStamp), 'NodeMessageId':"{}".format(NodeMessageId), 'ScreenName':"{}".format(ScreenName)} for Node, Message, TimeStamp, NodeMessageId, ScreenName in rows]

class MessageDefaultScreen(SmartiePiScreen):
    
    def on_enter(self):
        print("got to on_enter")
        
class MessageDefault(BoxLayout):
    node_message_id = StringProperty()
    node_name = StringProperty()
    node_message = StringProperty()
    node_type = StringProperty()
    node_description = StringProperty()
    time_stamp = StringProperty()

    def __init__(self, **kwargs):
        super(MessageDefault, self).__init__(**kwargs)
        print("message default init")
        #get current node_message_id
        self.app=App.get_running_app()
        self.node_message_id = self.app.node_message_id

        con = sqlite3.connect(db_file)
        cur = con.cursor()

        app= App.get_running_app()
        cur.execute("select n.Name as Node, m.Message, n.Type, n.Description, nm.TimeStamp  from NodeMessages nm inner join Messages m on nm.MessageId = m.Id inner join Nodes n on n.Id = nm.NodeId inner join Screens s on m.ScreenId = s.Id where nm.Id = {id}".\
        format(id=self.node_message_id))
        
        row = cur.fetchone()
        self.node_name = row[0]
        self.node_message = row[1]
        #self.node_type = row[2]
        self.node_description = row[3]
        self.time_stamp = row[4]

        con.close()

    def back_to_messages(self):
        self.app=App.get_running_app()
        
        
        sm = self.app.root.ids.sm
        sm.transition.direction = 'right'
        sm.current = 'Main'
        
    

class MessageView(RecycleDataViewBehavior, BoxLayout):
    
    Node = StringProperty("")
    Message = StringProperty("")
    TimeStamp = StringProperty("")
    NodeMessageId = StringProperty("")
    ScreenName = StringProperty("")

    index = None

    def delete_node_message(self,node_message_id):
        con = sqlite3.connect(db_file)
        cur = con.cursor()

        app= App.get_running_app()
        cur.execute("delete from nodemessages where id = {id}".\
        format(id=node_message_id))
        
        con.commit()
        con.close()

        self.parent.parent.bind_node_messages()

        

    def view_node_message(self, screen_name, node_message_id):
        self.app=App.get_running_app()
        
        sm = self.app.root.ids.sm
        sm.transition.direction = 'left'
        self.app.node_message_id = node_message_id
        self.app.load_screen(screen_name)



if __name__ == '__main__':
    SmartiePiApp().run()