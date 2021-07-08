# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.component_dialog import ComponentDialog
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, UserState, turn_context
from botbuilder.schema import InputHints

from datatypes_date_time.timex import Timex

from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog

# import sys
# sys.path.append(r"D:\Data\Google Drive\Openclassrooms\P10\07 core_bot")
from booking_details import BookingDetails

class ValidationDialog(ComponentDialog):

    def __init__(self, dialog_id: str = None, user_state: UserState = None):

        super(ValidationDialog, self).__init__(ValidationDialog.__name__)

        if user_state is None:
            raise Exception("[TestDialog]: Missing parameter. user_state is required")

        self.user_state = user_state
        self.user_prop = self.user_state.create_property("user_state")

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(DateResolverDialog(DateResolverDialog.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.final_step,
                ],
            )
        )
        self.initial_dialog_id = WaterfallDialog.__name__

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Complete the interaction and end the dialog.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options
        # message_text = f"{booking_details.destination}"
        # prompt_message = MessageFactory.text(
        #         message_text, message_text, InputHints.expecting_input
        #     )
        # return await step_context.prompt(
        #         TextPrompt.__name__, PromptOptions(prompt=prompt_message)
        #     )

        return await step_context.end_dialog(booking_details)
