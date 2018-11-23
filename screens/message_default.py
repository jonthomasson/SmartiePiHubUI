from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.clock import Clock
import sqlite3
from screens.shared.system import SmartiePiScreen, db_file
from kivy.app import App

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