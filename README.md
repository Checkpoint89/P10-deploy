Deploy Repo

app.py: web application code  
app_test.py: defines the test classes
adapter_with_error_handler.py: adapter class instantiated in app.py  
booking_details.py: defines a data structure for the flight details (origin, destination, ...)  
flight_booking_recognizer.py: defines the class that call LUIS and expose its response  
middleware1.py: defines the middlewares  
config.py: set-up the credentials from environment variables  
requirements.txt: librairies required 

Code managing the bot (that is the 'Adaptater' in the MS Bot Framework)  
  bots/dialog_and_welcome_bot.py  
  bots/dialog_bot.py  
  bots/validation_bot.py  

Code defining the structures used to manage the conversation state   
  data_model/states.py  

Code managing the various dialogs  
  dialogs/booking_dialog.py: defines the booking dialog class which implements the waterfall dialog getting all required information to book a flight  
  dialogs/cancel_and_help_dialog.py: defines a superclass for other dialog classes implementing cancel and help features  
  dialogs/date_resolver_dialog.py: defines the class for date management  
  dialogs/main_dialog.py: defines a class used as the main orchestrator of the dialogs  
  dialogs/validation_dialog.py  

Helpers  
  helpers/dialog_helper.py  
  helpers/luis_helper.py  