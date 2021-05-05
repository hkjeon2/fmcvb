# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.types import DomainDict
from fuzzywuzzy import process
import pathlib

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

        return [SlotSet("sports_venue", None), SlotSet("sports_venue_selected", None)]

class ActionClearSportsCategory(Action):

    def name(self) -> Text:
        return "action_clear_sports_category"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet("sports_category", None), SlotSet("sports_category_spelled_correctly", None),
            SlotSet("sports_category_match", None)]

sports_categories = pathlib.Path("db/sports_category.txt").read_text().split("\n")
sports_venues = pathlib.Path("db/sports_venues.txt").read_text().split("\n")

class ValidateSportsCategoryFrom(FormValidationAction):
    def name(self) -> Text:
        return "validate_sports_category_form"
    
    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Optional[List[Text]]:
        sports_category = tracker.slots.get("sports_category")
        sports_category_match = tracker.slots.get("sports_category_match")
        # last_entity_sports_category = next(tracker.get_latest_entity_values("sports_category"), None)
        # intent = tracker.get_intent_of_latest_message()
        required_slots = slots_mapped_in_domain

        if sports_category:
            if sports_category.lower() != sports_category_match:
                required_slots = ["sports_category_spelled_correctly"] + slots_mapped_in_domain
        # print(sports_category, sports_category_match, required_slots)

        return required_slots
    
    async def extract_sports_category_spelled_correctly(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        intent = tracker.get_intent_of_latest_message()
        text_of_last_user_message = tracker.latest_message.get("text")
        # print(f"intent: {intent}, text_of_last_user_message: {text_of_last_user_message}")
        # print(intent == "affirm")
        return {"sports_category_spelled_correctly": intent == "affirm"}

    def validate_sports_category_spelled_correctly(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if tracker.get_slot("sports_category_spelled_correctly"):
            return {"sports_category": tracker.get_slot("sports_category"), "sports_category_spelled_correctly": True}
        return {"sports_category": None, "sports_category_spelled_correctly": None}
        
    def validate_sports_category(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        top_match = process.extractOne(slot_value, sports_categories)
        return {"sports_category": slot_value, "sports_category_match": top_match[0]}

class ValidateSportsVenueForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_sports_venue_form"
    
    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Optional[List[Text]]:
        return slots_mapped_in_domain
    
    def validate_sports_venue_selected(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        
        top_match = process.extractOne(slot_value, sports_venues)
        if top_match[1] == 100:
            return {"sports_venue": slot_value, "sports_venue_selected": slot_value}
        else:
            dispatcher.utter_message(template="utter_please_rephrase")
            return {"sports_venue_selected": None}
        
    def validate_sports_venue(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        top_match = process.extractOne(slot_value, sports_venues)
        if top_match[1] == 100:
            return {"sports_venue": slot_value, "sports_venue_selected": slot_value}
        else:
            buttons = []
            for found, score in process.extract(slot_value, sports_venues, limit=5):
                if score >= 70:
                    buttons.append(
                        {"title": found, "payload": found}
                    )
            if buttons:
                dispatcher.utter_message(text="Please select a venue", buttons=buttons)
                return {"sports_venue": slot_value}
            else:
                dispatcher.utter_message(template="utter_please_rephrase")
                return {"sports_venue": None}
