import aiounittest

from botbuilder.core import (
    ConversationState,
    UserState,
    MemoryStorage,
)

from botbuilder.azure import CosmosDbConfig, CosmosDbStorage
from botbuilder.core.adapters import TestAdapter
from botbuilder.testing.dialog_test_client import DialogTestClient

from config import DefaultConfig
from dialogs import MainDialog
from dialogs.booking_dialog import BookingDialog
from bots import ValidationBot
from flight_booking_recognizer import FlightBookingRecognizer
from booking_details import BookingDetails
from middleware1 import Middleware1

CONFIG = DefaultConfig()

# Create MemoryStorage, UserState and ConversationState
MEMORY = MemoryStorage()
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)

COMOS_DB_CONFIG = CosmosDbConfig(
    CONFIG.DB_ENDPOINT,CONFIG.DB_KEY,
    CONFIG.DB_NAME, CONFIG.DB_CONTAINER_NAME)
COSMOS_DB_STORAGE = CosmosDbStorage(COMOS_DB_CONFIG)

# Create dialogs and Bot
RECOGNIZER = FlightBookingRecognizer(CONFIG)
BOOKING_DIALOG = BookingDialog(user_state=USER_STATE, con_state=CONVERSATION_STATE)
DIALOG = MainDialog(RECOGNIZER, BOOKING_DIALOG)
BOT = ValidationBot(CONVERSATION_STATE, USER_STATE, DIALOG)

class BookingDialogTest(aiounittest.AsyncTestCase):
    async def test_booking_dialog(self):
        booking_details = BookingDetails()

        test_client = DialogTestClient('booking_test', BOOKING_DIALOG, booking_details)

        reply = await test_client.send_activity('hi')
        assert reply.text == 'Where would you like to travel to?'
        reply = await test_client.send_activity('Berlin')
        assert reply.text == 'From what city will you be travelling?'
        reply = await test_client.send_activity('Paris')
        assert reply.text == 'On what date would you like to travel in?'
        reply = await test_client.send_activity('mar 23')
        message = "I'm sorry, for best results,"\
            "please enter your travel date in " \
            "including the month, day and year."
        assert reply.text == message
        reply = await test_client.send_activity('mar 23 2021')
        assert reply.text == 'On what date would you like to travel back?'
        reply = await test_client.send_activity('apr 15 2021')
        assert reply.text == 'What is  your maximum budget for this trip ?'
        reply = await test_client.send_activity('$500')
        message = (
            "Please confirm: I have you traveling to Berlin"
            "\nfrom Paris on 2021-03-23."
            "\nYour flight back is schedules on 2021-04-15."
            "\nYou want to spend less than: $500."
            " (1) Yes or (2) No"
        )
        assert reply.text == message

class BookingDialogDetails(aiounittest.AsyncTestCase):
    async def test_booking_dialog_with_details(self):
        booking_details = BookingDetails()
        booking_details.destination = 'Berlin'
        booking_details.travel_start_date = '2021-03-23'

        test_client = DialogTestClient('booking_test', BOOKING_DIALOG, booking_details)

        reply = await test_client.send_activity('hi')
        assert reply.text == 'From what city will you be travelling?'
        reply = await test_client.send_activity('Paris')
        assert reply.text == 'On what date would you like to travel back?'
        reply = await test_client.send_activity('apr 15 2021')
        assert reply.text == 'What is  your maximum budget for this trip ?'
        reply = await test_client.send_activity('$500')
        message = (
            "Please confirm: I have you traveling to Berlin"
            "\nfrom Paris on 2021-03-23."
            "\nYour flight back is schedules on 2021-04-15."
            "\nYou want to spend less than: $500."
            " (1) Yes or (2) No"
        )
        assert reply.text == message

class BookingDialogDetailsMiddleWare(aiounittest.AsyncTestCase):
    async def test_booking_dialog_with_details(self):
        booking_details = BookingDetails()
        booking_details.destination = 'Berlin'
        booking_details.travel_start_date = '2021-03-23'

        luis_recognizer = FlightBookingRecognizer(CONFIG)

        test_client = DialogTestClient(
            'booking_test',
            BOOKING_DIALOG,
            booking_details,
            [Middleware1(luis_recognizer)],
            CONVERSATION_STATE,
        )

        reply = await test_client.send_activity('hi')
        assert reply.text == 'From what city will you be travelling?'
        reply = await test_client.send_activity('I will take off from Paris')
        assert reply.text == 'On what date would you like to travel back?'
        reply = await test_client.send_activity('Ideally, that should be apr 15 2021')
        assert reply.text == 'What is  your maximum budget for this trip ?'
        reply = await test_client.send_activity('$500')
        message = (
            "Please confirm: I have you traveling to Berlin"
            "\nfrom paris on 2021-03-23."
            "\nYour flight back is schedules on 2021-04-15."
            "\nYou want to spend less than: $ 500."
            " (1) Yes or (2) No"
        )
        assert reply.text == message