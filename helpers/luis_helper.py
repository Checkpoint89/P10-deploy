# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from recognizers_date_time import recognize_datetime
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext, intent_score

from booking_details import BookingDetails


class Intent(Enum):
    BOOK_FLIGHT = "inform"
    CANCEL = "Cancel"
    GET_WEATHER = "GetWeather"
    NONE_INTENT = "None"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object, object):
        """
        Returns an object with pre-formatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None
        score = None


        def get_entities(luis_result, entities):
            entities_set = {'or_city', 'dst_city', 'str_date', 'end_date', 'budget'}
            mapping = {
                'or_city': 'origin', 'dst_city': 'destination',
                'str_date': 'travel_start_date', 'end_date': 'travel_end_date',
                'budget': 'budget'
            }
            entities_result = luis_result.entities['$instance']
            for entity in entities_set:
                if entity in entities_result:
                    result = entities_result[entity][0]['text']
                    if entity in ['str_date', 'dst_date']:
                        date_recognizer = recognize_datetime(result, 'english-us')
                        if date_recognizer:
                            formatted_result = date_recognizer[0].resolution['values'][0]['value']
                            setattr(entities,mapping[entity],formatted_result)
                        else:
                            setattr(entities,mapping[entity],result)
                    else:
                        setattr(entities,mapping[entity],result)
            return()

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)
            
            if recognizer_result.intents:
                intent = sorted(recognizer_result.intents,key=recognizer_result.intents.get,reverse=True,)[:1][0]
                score = recognizer_result.intents.get(intent).score
            else:
                intent =  None
                score = None

            result = BookingDetails()
            get_entities(recognizer_result, result)

        except Exception as err:
            print(err)

        try:
            print(f"\n-------------[luis_helper.py] text: {turn_context.activity.text}----")
            print(f"\n-------------[luis_helper.py] intent: {intent} score: {score}----")
            print(f"\n-------------[luis_helper.py] result: {vars(result)}-------------")
        except TypeError as err:
            print(f"\n-------------[luis_helper.py] result: {err}-------------")

        return intent, score, result

