from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window
import json

from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
# Adding LLM memory ability
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts.prompt import PromptTemplate


# For combat
import random
model='llama2:7b-chat-q5_K_M'
# model= 'gemma:7b'
# model='mistral'
llm = Ollama(model=model,callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
# llm.temperature=0.6
llm.num_predict=800 # To prevent the LLM from generating infinitely



template="""The following conversation is between me who is the player and dungeon master which is you. The dungeon master tells story with a wonderful descriptive language, create stories creatively and build a exciting world for user. Each response of dungeon master will contain a session of adventure and at the end ask the player what he will do next
Current Conversation:
{history}
Player: {input}
Dungeon Master:"""
PROMPT=PromptTemplate(input_variables=["history","input"],template=template)

template_header="""
"YOU ARE AN AI DUNGEON MASTER FOR RPG-TEXT GAME. YOUR MISSION IS TO CRAFT STORYLINE FOR ME, THE PLAYER.
The story is set within a character's mind.
FOLLOW UPDATED GUIDELINES. 
INTEGRATE ANY PREVIOUS DECISIONS OR EVENTS FROM OUR ADVENTURES. 
USE REALISTIC TONE, STAY AWAY FROM SENTIMENTS LIKE "RENEWED HOPE FOR FUTURE" OR "READY TO FACE WHATEVER CHALLENGES".
DO NOT CREATE SENTENCES THAT FEELS LIKE ENDING OF A STORY.
TAKE SLOW STEPS, DO NOT JUMP IN STORY.
ASK PLAYER WHAT THEY WANT TO DO IN DECISIONS or CONVERSATIONS.
IN COMBATS, DO NOT FINISH THE COMBAT RIGHT AWAY, ASK PLAYER WHAT HE WANTS TO DO
"""

template_main="""
            Current Conversation:
            {history}
            Player: {input}
            AI:"""

conversation=ConversationChain(
    prompt=PROMPT,
    llm=llm,
    verbose=False,
    memory=ConversationBufferWindowMemory(human_prefix="Player",ai_prefix='AI'),
)


class Character:
    def __init__(self, name, ch_class, **stats):
        self.name = name 
        self.ch_class=ch_class
        self.stats = {}
        # Unpack stats into dict
        for stat, value in stats.items():
            self.stats[stat] = value

        # Calculate health and mana based on stats
        self.health = self.stats["vitality"] * 10   
        self.mana = self.stats["intelligence"] * 10

        # Allow for additional stats to be added
        self.extra_stats = {}  

        self.power=0

    def power_char(self):
        for stat, value in self.stats.items():
            self.power+=value

    def update_stat(self, stat_name, value):
        if stat_name in ['vitality', 'strength', 'agility','intelligence']:
            setattr(self, stat_name, value)
        # else:
        #     self.extra_stats[stat_name] = value

    def take_damage(self, amount):
        self.health -= amount
        self.health = max(self.health, 0)  # Ensure health doesn't go below 0

    def display_stats(self):
        stats = f"{self.name} \n\nHealth: {self.health} \n\nMana: {self.mana}" 
        for stat, value in self.stats.items():
            stats += f"\n\n{stat.capitalize()}: {value}"
        for stat, value in self.extra_stats.items():
            stats += f"\n\n{stat.capitalize()}: {value}"
        return stats


    def to_json(self):
        # Convert the character object to JSON string
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str):
        # Create a character object from a JSON string
        data = json.loads(json_str)
        char = cls(data['name'], data['health'], data['strength'], data['agility'], data['intelligence'])
        # char.extra_stats = data.get('extra_stats', {})
        return char

class StatsDistributionScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.character = Character("Player",
                                   "class",
                                    vitality=10, 
                                    strength=10,
                                    agility=10,
                                    intelligence=10)
        self.remaining_points = 10
        
        self.layout = BoxLayout(orientation='vertical')

        
        
        # Add name input
        self.name_input = TextInput(text="Input your Character's Name")
        self.layout.add_widget(self.name_input)

        self.class_input = TextInput(text="Input your Combat Class")
        self.layout.add_widget(self.class_input)

        # Labels to show remaining points
        self.points_label = Label(text="Remaining points: "+str(self.remaining_points))
        self.layout.add_widget(self.points_label)

        # Stat Labels
        self.add_stat_input("vitality")
        self.add_stat_input("strength")
        self.add_stat_input("agility")
        self.add_stat_input("intelligence")

        # Done button
        done_button = Button(text="Done")
        done_button.bind(on_press=self.done)
        self.layout.add_widget(done_button)

        self.add_widget(self.layout)
        
    def add_stat_input(self, stat_name):

        """
        Binds plus and minus buttons to increase/decrease the stat, 
        and saves a reference to the stat's label in the character's stats dict.
        """
        input = Label(text="10")
        plus = Button(text="+")
        minus = Button(text="-")

        plus.bind(on_press=lambda instance: self.update_stat(stat_name, instance))
        minus.bind(on_press=lambda instance: self.update_stat(stat_name, instance))
        
        self.layout.add_widget(Label(text=stat_name.capitalize()))
        hlayout = BoxLayout(orientation='horizontal')
        hlayout.add_widget(input)
        hlayout.add_widget(plus) 
        hlayout.add_widget(minus)
        self.layout.add_widget(hlayout)

        # Add input to dict to reference later
        self.character.stats[stat_name] = input



    # Update stat method
    def update_stat(self, stat_name, instance):
        input = self.character.stats[stat_name]
        if instance.text == "+":
            # Increment logic
            input.text = str(int(input.text) + 1)
            self.remaining_points -= 1
        else:
            # Decrement logic
            input.text = str(int(input.text) - 1)
            self.remaining_points += 1
        # Update points label
        self.points_label.text = "Remaining points: " + str(self.remaining_points)


    def done(self, instance):
        # Get stat values from text inputs
        vitality = int(self.character.stats['vitality'].text)
        strength = int(self.character.stats['strength'].text)
        agility = int(self.character.stats['agility'].text)
        intelligence = int(self.character.stats['intelligence'].text)
        character_name=self.name_input.text
        character_class=self.class_input.text
        # Validate stat totals
        if self.remaining_points < 0:
            # Show error
            error_popup = Popup(title='Invalid Stats', 
                      content=Label(text='Stats are invalid. Please adjust.'),
                      size_hint=(None, None), size=(400, 200))

            error_popup.open()
            return

        # # Create and initialize the character
        # self.character=Character(name=character_name, ch_class=character_class, vitality=vitality, strength=strength, agility=agility, intelligence=intelligence)
        self.character=Character(name=character_name, ch_class=character_class, vitality=vitality, strength=strength, agility=agility, intelligence=intelligence)
        stats_screen = self.manager.get_screen('stats')
        game_screen = self.manager.get_screen('game')
        # game_screen.character = Character(name=character_name, ch_class=character_class, vitality=vitality, strength=strength, agility=agility, intelligence=intelligence)
        game_screen.character = stats_screen.character
        # self.current = 'game'
        # Switch to game screen
        self.manager.current = 'game'



# Define your screens
class MenuScreen(Screen):
    pass

class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        # This label will display the stats; updated dynamically when the screen is entered
        self.stats_label = Label()
        self.layout.add_widget(self.stats_label)
        self.add_widget(self.layout)
    
    def on_touch_down(self, touch):
        # Override to go back to the GameScreen when anywhere on the screen is touched
        self.manager.current = 'game'
    
    def on_pre_enter(self):
        # Before entering the screen, update stats from the character in GameScreen
        game_screen = self.manager.get_screen('game')
        self.stats_label.text = game_screen.character.display_stats()


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.i=0
        self.combat_init=0
        self.dice=0
        self.combat_round=0
        self.combat_result=None
        #self.character = Character("Arthur", 10, 10, 10, 10)  # Instantiate Character
        # self.character = Character("Player","Class",vitality=10,intelligence=10)
        top_button_layout = BoxLayout(size_hint=(1, None), height="40dp", pos_hint={"top": 1})
        # Create the buttons
        self.toggle_stats_button = Button(text="Character Details", size_hint=(0.33, None), height="40dp") 
        self.map_button = Button(text="Map", size_hint=(0.33, None), height="40dp")
        self.story_button = Button(text="Story", size_hint=(0.33, None), height="40dp")
        # Add buttons to top BoxLayout
        top_button_layout.add_widget(self.toggle_stats_button)
        top_button_layout.add_widget(self.map_button)
        top_button_layout.add_widget(self.story_button)
        
        # Shows the stats
        self.toggle_stats_button.bind(on_press=self.toggle_stats_display)

        # Position and size adjustments for the story and input areas
        self.story_area = TextInput(
            text="Welcome to the adventure!", 
            readonly=True, 
            size_hint=(1, 0.7), 
            pos_hint={"top": 0.9, "x": 0}
        )
        self.input_area = TextInput(
            hint_text="Your action...", 
            size_hint=(1, 0.1), 
            pos_hint={"y": 0.1, "x": 0}
        )
        continue_button = Button(
            text="Continue", 
            size_hint=(1, 0.1), 
            pos_hint={"y": 0, "x": 0}
        )
        continue_button.bind(on_press=self.process_input)

        # Add widgets to the layout
        self.layout.add_widget(self.story_area)
        self.layout.add_widget(self.input_area)
        self.layout.add_widget(continue_button)
        # Add top button layout 
        self.layout.add_widget(top_button_layout) 
        self.add_widget(self.layout)
    
    def init_character(self):
        game_screen = self.manager.get_screen('game')
        self.character=game_screen.character
        print(self.character.name)
        print(self.character.ch_class)

    def toggle_stats_display(self, instance):
        # Navigate to the StatsScreen
        self.manager.current = 'statsinfo'

    
    def prompt_on_type(self,prompt_type):
        # if self.i==1 and self.combat_init==0:
        """
        prompt_on_type handles different prompt types and updates the prompt template accordingly.
        
        It checks for different conditions like whether it's the start of the journey, 
        in combat or not, combat round etc. and updates the prompt template string accordingly.
        
        The updated template is then used to generate a new PromptTemplate object which is set as the prompt.
        """  
        if prompt_type=="start" and self.i==0:
            template_str=f"""
            Player Information:
            Name: {self.character.name}
            Combat Class: {self.character.ch_class}
            UPDATED GUIDELINES:
            This is the START OF JOURNEY, DO NOT INITIALIZE COMBAT,
            JUST CREATE A THE BEGINNING OF THE NEW JOURNEY.
            DO NOT MAKE MOVES OR CREATE ANSWERS INSTEAD OF PLAYER.
            """
            self.i=1       
            
            template= template_header+template_str + template_main
            PROMPT=PromptTemplate(input_variables=["history","input"],template=template)
            conversation.prompt=PROMPT
            
        if prompt_type=="journal" and self.combat_init==0:
            template_str=f"""
            Player Information:
            Name: {self.character.name}
            Combat Class: {self.character.ch_class}
            UPDATED GUIDELINES:
            CONTINUE CREATING CREATIVE ENVIRONMENT, KEEP THE STORY GOING ON, DO NOT CREATE BIG STEPS AND TAKE SLOWER
            NARRATIVE, DO NOT INITIALIZE A COMBAT
            DO NOT MAKE MOVES OR CREATE ANSWERS INSTEAD OF PLAYER.
            """
            template= template_header+template_str + template_main
            PROMPT=PromptTemplate(input_variables=["history","input"],template=template)
            self.combat_system()
            self.i+=1
            conversation.prompt=PROMPT
                
        if prompt_type=="journal" and self.combat_init==1 and self.combat_round>=1:
            if self.dice>2:
                self.combat_result="Player wins"
                self.combat_init=0
            elif self.dice<=2:
                self.combat_result="PLAYER LOSES, MUST CHOOSE A MEANS OF ESCAPE, ASK HOW HE WANTS TO ESCAPE"
            print(self.combat_round)
            print(self.combat_round>=1)
            print(f"The result of incoming battle: {self.combat_result}")
            template_str=f"""
            Player Information:
            Player's name: {self.character.name}
            Combat Class: {self.character.ch_class}
            Incoming information:
            YOU WILL CONTINUE THE PREVIOUS BATTLE,
            THE RESULT OF INCOMING BATTLE: {str(self.combat_result).upper}
            ACCORDING TO THE RESULT OF THE INCOMING BATTLE AND PLAYERS REPLY, CREATE STORY
            DO NOT MAKE MOVES OR CREATE ANSWERS INSTEAD OF PLAYER.
            """
            template= template_header+template_str + template_main
            PROMPT=PromptTemplate(input_variables=["history","input"],template=template)
            self.combat_round=0
            self.combat_init=0
            conversation.prompt=PROMPT

        if prompt_type=="journal" and self.combat_init==1 and self.combat_round==0:
            template_str=f"""
            Player Information:
            Name: {self.character.name}
            Combat Class: {self.character.ch_class}
            UPDATED GUIDELINES:
            INITIALIZE A COMBAT, CREATE A HOSTILE ENVIROMENT AND DRAG PLAYER TO COMBAT, INFORM THE PLAYER ON THE ENEMY, ASK WHAT WILL THE PLAYER DO IN HIS NEXT STEP
            DO NOT MAKE MOVES OR CREATE ANSWERS INSTEAD OF PLAYER.
            """
            template= template_header+template_str + template_main
            PROMPT=PromptTemplate(input_variables=["history","input"],template=template)
            self.combat_round=1
            conversation.prompt=PROMPT

        

    def process_input(self, instance):
        # Concatenate the new input with the conversation history
        # response = self.llm.invoke(self.input_area.text)
        if self.i==0:
            self.init_character()
            self.prompt_on_type("start")
        else:
            self.prompt_on_type("journal")
        response= conversation.invoke(self.input_area.text)
        response_text = response['response']
        
        # For now, just display the input text in the story area
        self.story_area.text += f"\n\nPlayer: {self.input_area.text}"
        self.story_area.text += f"\n\n {response_text}"
        self.input_area.text = "" # Clear input area
    
    def combat_system(self):
        # generate random number from 0 to 1:
        random_num = random.random()
        
        # If the random number is equal to zero...
        if random_num>=0.6:
            self.combat_round=0
            self.combat_init=1
            self.dice=random.randint(1,6)
        else:
            self.combat_init=0
        print(f"Generated random number is: {random_num}")
        print(f"Combat state is: {self.combat_init}")
        
        

        

class SettingsScreen(Screen):
    pass

# Define the screen manager
class MyScreenManager(ScreenManager):
    pass

# Load the KV design language
kv = Builder.load_string("""
<MyScreenManager>:
    MenuScreen:
    StatsScreen:
    StatsDistributionScreen: 
    GameScreen:
    SettingsScreen:

<MenuScreen>:
    name: 'menu'
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: 'Start Game'
            on_press: root.manager.current = 'stats'
        Button:
            text: 'Settings'
            # Settings functionality can be added here
        Button:
            text: 'Exit'
            on_press: app.stop()

<GameScreen>:
    name: 'game'

<SettingsScreen>:
    name: 'settings'
                         
<StatsScreen>:
    name: 'statsinfo'

<StatsDistributionScreen>:
    name: 'stats'
                 

""")

class MyApp(App):
    def build(self):
        return MyScreenManager()

if __name__ == '__main__':
    MyApp().run()
