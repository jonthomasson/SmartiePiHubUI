import time
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Rectangle
from kivy.graphics import Color
from kivy.utils import *
from kivy.uix.togglebutton import ToggleButton
from os.path import dirname, join
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty, BooleanProperty,\
    ListProperty, ObjectProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.boxlayout import BoxLayout
import sqlite3
from settings import settings_json


#initialize any default styles here
#Button.background_normal = ''
#Button.background_normal = 'images/button.png'
#Button.background_color = (.1, .1, .15)
#Button.border = (30,30,30,30)
Label.bold = True

db_file = 'data/smartiepi.db'

class PowerMenu(FloatLayout):
    def power_exit(self):
        print("exiting...")

    def power_shutdown(self):
        print("shutting down...")

    def power_restart(self):
        print("restarting...")

class SmartiePiHub(Widget):
    pass

class SystemHealth(BoxLayout):
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
        Clock.schedule_interval(self.update_clock, 1) #run once a second
        Clock.schedule_interval(self.update_system_health, 60) #run once a minute
        Clock.schedule_once(self.update_system_health,0)
        
        sm = hub.ids.sm
        screen = self.get_screen_file('Main')
        sm.add_widget(screen)
        sm.current = 'Main'
        return hub
    
    def build_config(self, config):
        config.setdefaults('SmartiePi', {
            'sendtextinfo': False,
            'sendtextwarning': False,
            'sendtextalert': False,
            'numberstotext': '',
            'sendemailinfo': False,
            'sendemailwarning': False,
            'sendemailalert': False,
            'emails': '',
            'enablewifi': False,
            'defaultvolume': 100
        })
    
    def build_settings(self, settings):
        settings.add_json_panel('SmartiePi', self.config, data=settings_json)
        
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

    def get_node_message_count(self, type):
        con = sqlite3.connect(db_file)
        cur = con.cursor()
        message_type = "m.IsWarn = 1" if type == "warning" else "m.IsAlert = 1"

        cur.execute("select count(*) from NodeMessages nm inner join Messages m on nm.MessageId = m.Id where {mtype}".\
        format(mtype=message_type))
        
        row = cur.fetchone()
        count = row[0]
        con.close()

        return count

    def update_system_health(self, dt):
        app= App.get_running_app()
        system_health = app.root.ids.system_health
        system_health_rv = system_health.ids.system_health_rv
        system_health_label = system_health.ids.system_health_label
        system_health_status = 'GOOD'
        system_health_message = ''
        system_health_color = '00ff00'
        rows = []
        #get list of current node messages

        #determine count of warning and alert messages
        count_warning = self.get_node_message_count('warning')
        count_alert = self.get_node_message_count('alert')

        if(count_warning > 3):
            count_warning = 3
        if(count_alert > 3):
            count_alert = 3
        if(count_alert > 0):
            count_warning = 3

        for x in range(0, 3):
            rows.append('00ff00')
        for x in range(0, count_warning):
            rows.append('ffff00')
        for x in range(0, 3 - count_warning):
            rows.append('222200')
        for x in range(0, count_alert):
            rows.append('ff0000')
        for x in range(0, 3 - count_alert):
            rows.append('220000')
        
        system_health_rv.data = [{'BgColor':"{}".format(BgColor)} for BgColor in rows]

        #update system_health label
        if(count_alert > 3):
            system_health_status = 'DEFCON 20'
        elif(count_alert == 2):
            system_health_status = 'CRITICAL'
        elif(count_alert == 1):
            system_health_status = 'VERY BAD'
        elif(count_warning == 3):
            system_health_status = 'SERIOUS'
        elif(count_warning == 2):
            system_health_status = 'NOT GOOD'
        elif(count_warning == 1):
            system_health_status = 'ELEVATED'

        if(count_alert > 0):
            system_health_color = 'ff0000'
        elif(count_warning > 0):
            system_health_color = 'ffff00'
        else:
            system_health_color = '00ff00'

        system_health_message = "SYSTEM HEALTH: [color={color}][b]{status}[/b][/color]".format(color = system_health_color, status = system_health_status)

        system_health_label.text = system_health_message

class SmartieActionBar(BoxLayout):
    pass

class VolumeControl(FloatLayout):
    

    def volume_value_changed(self, value):
        self.app= App.get_running_app()
        #get reference to action bar volume button
        toggle_volume = self.app.root.ids.toggle_volume
        #set appropriate text icon for action bar volume button
        if(value == 0):
            toggle_volume.text = u'\uf6a9' #volume-mute
        elif(value < 50):
            toggle_volume.text = u'\uf026' #volume-off
        elif(value < 150):
            toggle_volume.text = u'\uf027' #volume-down
        elif(value > 150):
            toggle_volume.text = u'\uf028' #volume-up

    def volume_touch_up(self):
        volume_slider = self.ids.volume_slider

        #update volume on raspi and play sample sound to test...
        print('setting raspi volume to ', volume_slider.value)

class BatteryStatus(FloatLayout):
    pass

class ActionBarToggleButton(ToggleButton):
    def show_volume_control(self):
        if(self.state == "normal"):
            volume_control = self.children[0]
            self.remove_widget(volume_control)
        else:
            volume_control = VolumeControl()
            volume_control.pos = [self.pos[0], self.height]
            volume_control.size = self.width, 250
            self.add_widget(volume_control)
    
    def show_battery_status(self):
        if(self.state == "normal"):
            battery_status = self.children[0]
            self.remove_widget(battery_status)
        else:
            battery_status = BatteryStatus()
            battery_status.pos = [self.pos[0], self.height]
            self.add_widget(battery_status)

    def toggle_wifi(self):
        if(self.state == 'down'):
            print("enable wifi")
        else:
            print("disable wifi")

    def show_power_menu(self):
        if(self.state == 'normal'):
            power_menu = self.children[0]
            self.remove_widget(power_menu)
        else:
            power_menu = PowerMenu()
            power_menu.pos = [self.pos[0], self.height]
            self.add_widget(power_menu)
    


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
       

    
        
    
class SystemHealthView(RecycleDataViewBehavior, Label):
    BgColor = StringProperty()

    def get_color(self, bg_color):
        #print(bg_color)
        if(bg_color != ''):
            return get_color_from_hex(bg_color)
        else:
            return get_color_from_hex('ffffff')

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