from typing import Callable, Awaitable
from botbuilder.azure.cosmosdb_storage import CosmosDbStorage
from botbuilder.core import Middleware, TurnContext, MessageFactory
from botbuilder.core.conversation_state import ConversationState
from botbuilder.schema import ActivityTypes, InputHints

from flight_booking_recognizer import FlightBookingRecognizer
from data_model import ConState

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
                _, _, luis_result = await LuisHelper.execute_luis_query(
                    self._luis_recognizer,
                    turn_context
                )

                if luis_result is not None:
                    turn_context.turn_state['destination'] = luis_result.destination
                    turn_context.turn_state['origin'] = luis_result.origin
                    turn_context.turn_state['travel_start_date'] = luis_result.travel_start_date
                    turn_context.turn_state['travel_end_date'] = luis_result.travel_end_date
                    turn_context.turn_state['budget'] = luis_result.budget

            turn_context.turn_state['failed'] = False

            await next()

        if turn_context.activity.type == ActivityTypes.conversation_update:
            await next()


class Middleware2(Middleware):

    def __init__(self, constate: ConversationState, cosmosdb: CosmosDbStorage) -> None:
        self.constate = constate
        self.conprop = self.constate.create_property("constate")
        self.cosmosdb = cosmosdb

    async def on_turn(
        self,
        turn_context: TurnContext,
        next: Callable[[TurnContext],Awaitable]
    ):

        if turn_context.activity.type == ActivityTypes.message:

            conmode = await self.conprop.get(turn_context,ConState)
            conmode.conversation.append("[User]: " + turn_context.activity.text)

            async def send_activity_handler(new_context, activities, next_send):
                for activity in activities:
                    if activity.text is not None:
                        conmode.conversation.append("[Bot]: " + activity.text)
                await next_send()

            turn_context = turn_context.on_send_activities(send_activity_handler)

            await next()

            if turn_context.turn_state['failed']:
                print(f"\n-------------[middleware1.py =>] Failed ?: \
                    {turn_context.turn_state['failed']}")
                print(f"\n-------------[middleware1.py =>] conmode.conversation: \
                    {conmode.conversation}")

                activity_id = (turn_context
                    .get_conversation_reference(turn_context.activity)
                    .activity_id)
                activity_id_str = str(activity_id)

                collection_store = {activity_id_str: conmode.conversation}
                await self.cosmosdb.write(collection_store)


            await self.constate.save_changes(turn_context)

        if turn_context.activity.type == ActivityTypes.conversation_update:
            await next()
