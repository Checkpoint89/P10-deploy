#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

MIN_INTENT_SCORE = 0.5

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978

    APP_ID = os.getenv("APP_ID")
    APP_PASSWORD = os.getenv("APP_PASSWORD")
    LUIS_APP_ID = os.getenv("LUIS_APP_ID")
    LUIS_API_KEY = os.getenv("PREDICTION_KEY")
    LUIS_API_HOST_NAME = os.getenv("PREDICTION_ENDPOINT")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.getenv("APPINSIGHTS_INSTRUMENTATION_KEY")
    DB_ENDPOINT = os.getenv("DB_ENDPOINT")
    DB_KEY = os.getenv("DB_KEY")
    DB_NAME = os.getenv("DB_NAME")
    DB_CONTAINER_NAME = os.getenv("DB_CONTAINER_NAME")


    # print("APP_ID",APP_ID)
    # print("APP_PASSWORD",APP_PASSWORD)
    # print("LUIS_APP_ID",LUIS_APP_ID)
    # print("LUIS_API_KEY",LUIS_API_KEY)
    # print("LUIS_API_HOST_NAME",LUIS_API_HOST_NAME)
