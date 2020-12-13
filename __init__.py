import requests
import json
import random

from os.path import join, abspath, dirname

from mycroft.audio import wait_while_speaking
from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
from mycroft.skills.core import intent_handler
from mycroft.util.parse import match_one

CONTES = json.load(open(join(dirname(abspath(__file__)), "contes.json"), "r", encoding="utf-8"))
TITOLS = list(CONTES.keys())

def find_mime(url):
    mime = "audio/mpeg"
    response = requests.Session().head(url, allow_redirects=True)
    if 200 <= response.status_code < 300:
        mime = response.headers["content-type"]
    return mime
    
class ContesSkill(CommonPlaySkill):
    def __init__(self):
        super().__init__()
    
    @intent_handler("explica.intent")
    def handle_conte_intent(self, message):
        query = message.data["utterance"]
        titol, _ = match_one(query, TITOLS)
        
        self.reprodueix(titol)


    @intent_handler("aleatori.intent")
    def handle_conte_intent(self, message):
        titol = random.choice(TITOLS)
        self.reprodueix(titol)
        
    def reprodueix(self, titol):
        url = CONTES[titol]
        self.speak_dialog("intro", data={"nom": titol})
        wait_while_speaking()
        self.CPS_play((url, find_mime(url)))
        
    def CPS_match_query_phrase(self, phrase):
        return (phrase, CPSMatchLevel.EXACT)
    
    def CPS_start(self, phrase, data):
        self.handle_conte_intent(phrase)

def create_skill():
    return ContesSkill()