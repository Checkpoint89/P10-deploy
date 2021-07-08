from typing import Callable, Awaitable
from botbuilder.core import Middleware, TurnContext, MessageFactory
from botbuilder.schema import ActivityTypes, InputHints

from flight_booking_recognizer import FlightBookingRecognizer

from helpers import LuisHelper

class Middleware1(Middleware):

    def __init__(self, luis_recognizer: FlightBookingRecognizer) -> None:
        self._luis_recognizer = luis_recognizer

    async def on_turn(
        self,
        turn_context: TurnContext,
        next: Callable[[TurnContext],Awaitable]
    ):
        if turn_context.activity.type == ActivityTypes.message:

            if not self._luis_recognizer.is_configured:
                await turn_context.send_activity(
                    MessageFactory.text(
                        "NOTE: LUIS is not configured. "\
                        "To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and " \
                        "'LuisAPIHostName' to the appsettings.json file.",
                        input_hint=InputHints.ignoring_input,
                    )
                )
            else:
                # Call LUIS and gather any potential booking details.
                # (Note the TurnContext has the response to the prompt.)
                _, luis_result = await LuisHelper.execute_luis_query(
                    self._luis_recognizer,
                    turn_context
                )

                if luis_result is not None:
                    turn_context.turn_state['destination'] = luis_result.destination
                    turn_context.turn_state['origin'] = luis_result.origin
                    turn_context.turn_state['travel_start_date'] = luis_result.travel_start_date
                    turn_context.turn_state['travel_end_date'] = luis_result.travel_end_date
                    turn_context.turn_state['budget'] = luis_result.budget

            await next()

        if turn_context.activity.type == ActivityTypes.conversation_update:
            await next()
