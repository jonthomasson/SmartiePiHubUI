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


#initialize any default styles here
#Button.background_normal = ''
#Button.background_normal = 'images/button.png'
#Button.background_color = (.1, .1, .15)
#Button.border = (30,30,30,30)

db_file = 'data/smartiepi.db'

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

class MainScreen(SmartiePiScreen):
    
    def on_enter(self):
        Clock.schedule_once(self.bind_node_messages,0)

    def bind_node_messages(self, dt):
        con = sqlite3.connect(db_file)
        cur = con.cursor()

        app= App.get_running_app()
        cur.execute("select n.Name as Node, m.Message, nm.TimeStamp, nm.Id as NodeMessageId, s.Name as ScreenName, m.IsInfo, m.IsWarn, m.IsAlert from NodeMessages nm inner join Messages m on nm.MessageId = m.Id inner join Nodes n on n.Id = nm.NodeId inner join Screens s on m.ScreenId = s.Id order by nm.id desc")
        
        rows = cur.fetchall()
        con.close()
        rows_info = []
        rows_warn = []
        rows_alert = []

        
        #using try block instead of hasattr for attribute checking here because most of the time this will not fail
        try:
            main_view_info = self.ids.main_view_info
            main_view_warn = self.ids.main_view_warn
            main_view_alert = self.ids.main_view_alert

        except AttributeError:
            main_view_info = app.root.ids.main_view_info
            main_view_warn = app.root.ids.main_view_warn
            main_view_alert = app.root.ids.main_view_alert

        for row in rows:
            if row[5] == 1:
                #info row
                rows_info.append(row)
            if row[6] == 1:
                #warn row
                rows_warn.append(row)
            if row[7] == 1:
                #alert row
                rows_alert.append(row)

            
        main_view_info.data = [{'Node':"{}".format(Node), 'Message':"{}".format(Message), 'TimeStamp':"{}".format(TimeStamp), 'NodeMessageId':"{}".format(NodeMessageId), 'ScreenName':"{}".format(ScreenName)} for Node, Message, TimeStamp, NodeMessageId, ScreenName, IsInfo, IsWarn, IsAlert in rows_info]
        main_view_warn.data = [{'Node':"{}".format(Node), 'Message':"{}".format(Message), 'TimeStamp':"{}".format(TimeStamp), 'NodeMessageId':"{}".format(NodeMessageId), 'ScreenName':"{}".format(ScreenName)} for Node, Message, TimeStamp, NodeMessageId, ScreenName, IsInfo, IsWarn, IsAlert in rows_warn]
        main_view_alert.data = [{'Node':"{}".format(Node), 'Message':"{}".format(Message), 'TimeStamp':"{}".format(TimeStamp), 'NodeMessageId':"{}".format(NodeMessageId), 'ScreenName':"{}".format(ScreenName)} for Node, Message, TimeStamp, NodeMessageId, ScreenName, IsInfo, IsWarn, IsAlert in rows_alert]


class MainRecycleView(RecycleView):
    pass
    

    #def __init__(self, **kwargs):
    #    super(MainRecycleView, self).__init__(**kwargs)
        
    #    self.bind_node_messages()


class MessageDefaultScreen(SmartiePiScreen):
    node_message_id = StringProperty()
    node_name = StringProperty()
    node_message = StringProperty()
    node_type = StringProperty()
    node_description = StringProperty()
    time_stamp = StringProperty()

    def on_enter(self):
        Clock.schedule_once(self.bind_node_message,0)
        #print("got to message default on_enter")

    def bind_node_message(self, dt):
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

class MessageDefault(BoxLayout):
    

    def __init__(self, **kwargs):
        super(MessageDefault, self).__init__(**kwargs)
       

    
        
    

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

        #app.root.ids.main_screen.bind_node_messages()
        self.parent.parent.parent.parent.parent.parent.bind_node_messages(0)

        

    def view_node_message(self, screen_name, node_message_id):
        self.app=App.get_running_app()
        
        sm = self.app.root.ids.sm
        sm.transition.direction = 'left'
        self.app.node_message_id = node_message_id
        self.app.load_screen(screen_name)



if __name__ == '__main__':
    SmartiePiApp().run()