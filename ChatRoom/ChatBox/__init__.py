from otree.api import *
from os import environ
from openai import OpenAI


# openAI chat gpt key 
client = OpenAI(api_key=environ.get('CHATGPT_KEY'))
import random
import json
from datetime import datetime

author = "Yuhao"
doc = """
a chatGPT ChatBox for oTree
"""
# --------------------------------Constants-----------------------------------# 
class C(BaseConstants):
    NAME_IN_URL = 'chatGPT'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    # chatGPT vars

    ## temperature (range 0 - 2)
    ## this sets the bot's creativity in responses, with higher values being more creative
    ## https://platform.openai.com/docs/api-reference/completions#completions/create-temperature
    TEMP = 1

    ## model
    ## this is which gpt model to use, which have different prices and ability
    ## https://platform.openai.com/docs/models
    MODEL = "gpt-4o"

    PROMPT = """　"""

# --------------------------------Constants END-----------------------------------# 

class Subsession(BaseSubsession):
    num_Chat = models.IntegerField(initial=0)

            
def creating_session(subsession: Subsession):
    #set prompts  
    players = subsession.get_players()
    for p in players:
        p.msg = json.dumps([{"role": "system", "content": C.PROMPT}])



       
class Group(BaseGroup):
    pass


class Player(BasePlayer):
    
    # chat condition and data log
    condition = models.StringField(blank=True)
    chatLog = models.LongStringField(blank=True)

    # input data for gpt
    msg = models.LongStringField(blank=True)



# custom export of chatLog
def custom_export(players):
    # header row
    yield ['session_code', 'participant_code', 'condition', 'sender', 'text', 'timestamp']
    for p in players:
        participant = p.participant
        session = p.session

        # expand chatLog
        log = p.field_maybe_none('chatLog')
        if log:    
            json_log = json.loads(log)
            print(json_log)
            for r in json_log:
                sndr = r['sender']
                txt = r['text']
                time = r['timestamp']
                yield [session.code, participant.code, p.condition, sndr, txt, time]



# function to run messages
def runGPT(inputMessage):
    completion = client.chat.completions.create(model = C.MODEL, 
    messages = inputMessage, 
    temperature = C.TEMP)
    return completion.choices[0].message.content

# --------------------------------PAGES-----------------------------------# 


class AIChat(Page):
    form_model = 'player'
    form_fields = ['chatLog']

    @staticmethod
    def live_method(player: Player, data):

        # load msg
        messages = json.loads(player.msg)

        # functions for retrieving text from openAI
        if 'text' in data:
            # grab text that participant inputs and format for chatgpt
            text = data['text']
            inputMsg = {'role': 'user', 'content': text}


            # append messages and run chat gpt function
            messages.append(inputMsg)
            output = runGPT(messages)
            
            # also append messages with bot message
            botMsg = {'role': 'assistant', 'content': output}
            messages.append(botMsg)

            # write appended messages to database
            player.msg = json.dumps(messages)

            return {player.id_in_group: output}  
        else: 
            pass

    @staticmethod
    def before_next_page(player, timeout_happened):
        return {
        }




page_sequence = [ AIChat,
]