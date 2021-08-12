import requests
import json
import random

from os.path import join, abspath, dirname

from mycroft.audio import wait_while_speaking
from mycroft.skills.core import intent_handler

from mycroft_bus_client.message import Message
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill
from ovos_workshop.frameworks.playback import CPSMatchType, CPSPlayback, \
    CPSMatchConfidence
from ovos_utils.parse import fuzzy_match, MatchStrategy, match_one


class ContesSkill(OVOSCommonPlaybackSkill):
    def __init__(self):
        contes_path = join(dirname(abspath(__file__)), "contes.json")
        with open(contes_path) as f:
            self.contes = json.load(f)
        super().__init__()
        self.supported_media = [CPSMatchType.GENERIC,
                                CPSMatchType.VISUAL_STORY,
                                CPSMatchType.AUDIO,
                                CPSMatchType.VIDEO,
                                CPSMatchType.AUDIOBOOK]
        self.skill_icon = join(dirname(__file__), "ui", "logo.png")

    @intent_handler("explica.intent")
    def handle_conte_intent(self, message):
        query = message.data["utterance"]
        titols = list(self.contes.keys())
        titol, _ = match_one(query, titols,
                             strategy=MatchStrategy.TOKEN_SET_RATIO)
        self.reprodueix(titol)

    @intent_handler("aleatori.intent")
    def handle_conte_intent(self, message):
        titol = random.choice(list(self.contes.keys()))
        self.reprodueix(titol)
        
    def reprodueix(self, titol):
        url = self.contes[titol]
        self.speak_dialog("intro", data={"nom": titol})
        wait_while_speaking()
        # ovos common play metadata
        track_data =  {
                "title": titol,
                "match_confidence": CPSMatchConfidence.EXACT,
                "media_type":  CPSMatchType.VISUAL_STORY,
                "uri": url,
                "playback": CPSPlayback.GUI,
                "image": join(dirname(__file__), "ui", "logo.png"),
                "bg_image": join(dirname(__file__), "ui", "bg.png"),
                "skill_id": self.skill_id,
                "skill_icon": self.skill_icon,
                "skill_logo": self.skill_icon  # backwards compat
            }
        # audio only if GUI not available
        disambiguation = [track_data, {
                "title": titol + " (audio)",
                "match_confidence": CPSMatchConfidence.HIGH,
                "media_type":  CPSMatchType.AUDIOBOOK,
                "uri": url,
                "playback": CPSPlayback.AUDIO,
                "image": join(dirname(__file__), "ui", "logo.png"),
                "bg_image": join(dirname(__file__), "ui", "bg.png"),
                "skill_id": self.skill_id,
                "skill_icon": self.skill_icon,
                "skill_logo": self.skill_icon  # backwards compat
            }]
        self.play_media(track_data, disambiguation)

    # common play
    def CPS_search(self, phrase, media_type=CPSMatchType.GENERIC):
        """Analyze phrase to see if it is a play-able phrase with this skill.

        Arguments:
            phrase (str): User phrase uttered after "Play", e.g. "some music"
            media_type (CPSMatchType): requested CPSMatchType to search for

        Returns:
            search_results (list): list of dictionaries with result entries
            {
                "match_confidence": CPSMatchConfidence.HIGH,
                "media_type":  CPSMatchType.MUSIC,
                "uri": "https://audioservice.or.gui.will.play.this",
                "playback": CPSPlayback.GUI,
                "image": "http://optional.audioservice.jpg",
                "bg_image": "http://optional.audioservice.background.jpg"
            }
        """
        # match the request media_type
        base_score = 0
        if media_type == CPSMatchType.AUDIO:
            base_score += 15
        elif media_type == CPSMatchType.AUDIOBOOK:
            base_score += 25

        if self.lang != "ca-es":
            base_score = -20

        matches = []
        for titol in self.contes.keys():
            score = base_score
            # this will give score of 100 if query is included in title
            score += 100 * fuzzy_match(phrase.lower(), titol.lower(),
                strategy=MatchStrategy.TOKEN_SET_RATIO)
            matches.append({
                "title": titol,
                "match_confidence": score,
                "media_type":  CPSMatchType.VISUAL_STORY,
                "uri": self.contes[titol],
                "playback": CPSPlayback.GUI,
                "image": join(dirname(__file__), "ui", "logo.png"),
                "bg_image": join(dirname(__file__), "ui", "bg.png"),
                "skill_id": self.skill_id,
                "skill_icon": self.skill_icon,
                "skill_logo": self.skill_icon  # backwards compat
            })
            matches.append({
                "title": titol + " (audio)",
                "match_confidence": score - 10,
                "media_type":  CPSMatchType.AUDIOBOOK,
                "uri": self.contes[titol],
                "playback": CPSPlayback.AUDIO,
                "image": join(dirname(__file__), "ui", "logo.png"),
                "bg_image": join(dirname(__file__), "ui", "bg.png"),
                "skill_id": self.skill_id,
                "skill_icon": self.skill_icon,
                "skill_logo": self.skill_icon  # backwards compat
            })
        return matches

def create_skill():
    return ContesSkill()