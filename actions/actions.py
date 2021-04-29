# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []

class ActionGetHotelsUrl(Action):

    def name(self) -> Text:
        return "action_get_hotels_url"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sports_venue = tracker.get_slot("sports_venue")
        if sports_venue:
            sports_venue_replaced = sports_venue.replace(" ", "+")
            msg = f"Please click the following [hotels near {sports_venue}](https://www.google.com/maps/search/hotels+near+{sports_venue_replaced},+fargo)"
        else:
            msg = f"Sorry, we could not find {sports_venue}"

        dispatcher.utter_message(text=msg)

        return [SlotSet("sports_venue", None)]

class ActionClearSportsCategory(Action):

    def name(self) -> Text:
        return "action_clear_sports_category"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet("sports_category", None)]
