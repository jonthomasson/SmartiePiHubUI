from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.clock import Clock
import sqlite3
from screens.shared.system import SmartiePiScreen, db_file
from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior

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

        self.parent.parent.parent.parent.parent.parent.bind_node_messages(0)

    def view_node_message(self, screen_name, node_message_id):
        self.app=App.get_running_app()
        
        sm = self.app.root.ids.sm
        sm.transition.direction = 'left'
        self.app.node_message_id = node_message_id
        self.app.load_screen(screen_name)

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

        main_view_info = self.ids.tab_info.content.children[0]
        main_view_warn = self.ids.tab_warnings.content.children[0]
        main_view_alert = self.ids.tab_alerts.content.children[0]
            
        main_view_info.data = [{'Node':"{}".format(Node), 'Message':"{}".format(Message), 'TimeStamp':"{}".format(TimeStamp), 'NodeMessageId':"{}".format(NodeMessageId), 'ScreenName':"{}".format(ScreenName)} for Node, Message, TimeStamp, NodeMessageId, ScreenName, IsInfo, IsWarn, IsAlert in rows_info]
        main_view_warn.data = [{'Node':"{}".format(Node), 'Message':"{}".format(Message), 'TimeStamp':"{}".format(TimeStamp), 'NodeMessageId':"{}".format(NodeMessageId), 'ScreenName':"{}".format(ScreenName)} for Node, Message, TimeStamp, NodeMessageId, ScreenName, IsInfo, IsWarn, IsAlert in rows_warn]
        main_view_alert.data = [{'Node':"{}".format(Node), 'Message':"{}".format(Message), 'TimeStamp':"{}".format(TimeStamp), 'NodeMessageId':"{}".format(NodeMessageId), 'ScreenName':"{}".format(ScreenName)} for Node, Message, TimeStamp, NodeMessageId, ScreenName, IsInfo, IsWarn, IsAlert in rows_alert]

class MainRecycleView(RecycleView):
    pass

    #def __init__(self, **kwargs):
    #    super(MainRecycleView, self).__init__(**kwargs)
        
    #    self.bind_node_messages()



       
