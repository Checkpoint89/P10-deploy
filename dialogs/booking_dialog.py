# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core.conversation_state import ConversationState
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, UserState, BotTelemetryClient, NullTelemetryClient
from botbuilder.schema import InputHints

from datatypes_date_time.timex import Timex

from data_model import ConState

from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog


class BookingDialog(CancelAndHelpDialog):

    def __init__(
        self,
        dialog_id: str = None,
        user_state: UserState = None,
        con_state: ConversationState = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient):
        super(BookingDialog, self).__init__(
            dialog_id or BookingDialog.__name__,
            telemetry_client,
        )

        self.telemetry_client = telemetry_client

        if user_state is None:
            raise Exception("[BookingDialogBot]: Missing parameter. user_state is required")
        if con_state is None:
            raise Exception("[BookingDialogBot]: Missing parameter. con_state is required")

        self.user_state = user_state
        self.user_prop = self.user_state.create_property("user_state")

        self.con_state = con_state
        self.con_prop = self.con_state.create_property("con_state")

        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = telemetry_client
        self.add_dialog(text_prompt)

        confirm_prompt = ConfirmPrompt(ConfirmPrompt.__name__)
        confirm_prompt.telemetry_client = telemetry_client
        self.add_dialog(confirm_prompt)

        dateresolverdialog = DateResolverDialog(DateResolverDialog.__name__)
        dateresolverdialog.telemetry_client = telemetry_client
        self.add_dialog(dateresolverdialog)

        waterfall_dialog = WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.destination_step,
                    self.origin_step,
                    self.travel_start_date_step,
                    self.travel_end_date_step,
                    self.budget_step,
                    self.confirm_step,
                    self.final_step,
                ],
            )
        waterfall_dialog.telemetry_client = telemetry_client
        self.add_dialog(waterfall_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__

    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a destination city has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """

        booking_details = step_context.options

        if booking_details.destination is None:
            message_text = "Where would you like to travel to?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )

            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )

        return await step_context.next(booking_details.destination)

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        If an origin city has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        try:
            booking_details.destination = step_context.context.turn_state['destination']
            if booking_details.destination is None:
                booking_details.destination = step_context.result
        except KeyError:
            booking_details.destination = step_context.result

        if booking_details.origin is None:
            message_text = "From what city will you be travelling?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(booking_details.origin)

    async def travel_start_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a travel start date has not been provided, prompt for one.
        This will use the DATE_RESOLVER_DIALOG.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        try:
            booking_details.origin = step_context.context.turn_state['origin']
            if booking_details.origin is None:
                booking_details.origin = step_context.result
        except KeyError:
            booking_details.origin = step_context.result

        if not booking_details.travel_start_date or self.is_ambiguous(
            booking_details.travel_start_date
        ):
            return await step_context.begin_dialog(
                DateResolverDialog.__name__,
                {'date':booking_details.travel_start_date, 'direction': 'in'},
            )
        return await step_context.next(booking_details.travel_start_date)

    async def travel_end_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a travel end date has not been provided, prompt for one.
        This will use the DATE_RESOLVER_DIALOG.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.travel_start_date = step_context.result
        if not booking_details.travel_end_date or self.is_ambiguous(
            booking_details.travel_end_date
        ):
            return await step_context.begin_dialog(
                DateResolverDialog.__name__,
                {'date':booking_details.travel_end_date, 'direction': 'back'},
            )
        return await step_context.next(booking_details.travel_end_date)

    async def budget_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        If an budget has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.travel_end_date = step_context.result
        if booking_details.budget is None:
            message_text = "What is  your maximum budget for this trip ?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(booking_details.budget)

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        Confirm the information the user has provided.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        try:
            booking_details.budget = step_context.context.turn_state['budget']
            if booking_details.budget is None:
                booking_details.budget = step_context.result
        except KeyError:
            booking_details.budget = step_context.result

        message_text = (
            f"Please confirm: I have you traveling to { booking_details.destination }"
            f"\nfrom { booking_details.origin } on { booking_details.travel_start_date}."
            f"\nYour flight back is schedules on { booking_details.travel_end_date}."
            f"\nYou want to spend less than: { booking_details.budget}."
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Complete the interaction and end the dialog.
        :param step_context:
        :return DialogTurnResult:
        """

        if step_context.result:
            booking_details = step_context.options
            self.telemetry_client.track_trace("Success")
            return await step_context.end_dialog(booking_details)

        self.telemetry_client.track_trace("Failed")
        step_context.context.turn_state['failed'] = True
        return await step_context.end_dialog()


    def is_ambiguous(self, timex: str) -> bool:
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
