import requests
import json
from typing import Dict
import time
from datetime import datetime

from django.http import JsonResponse
from django.utils import timezone
from api.loggers import AuthenticationApiLogger
from pymongo import MongoClient
from bson import ObjectId

from dotenv import load_dotenv
import os

load_dotenv()


class GetDevAccess:

    def __init__(self, username, password):
        response = GetDevAccess.jamshid_dev_login(username, password)
        self.access_token = response["access_token"]
        self.dev_user_id = response["_id"]["$oid"]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        logout_url = "https://logout.api.jamshid.app/logout?user_id=" + self.dev_user_id
        headers = {
            "token": "Bearer " + self.access_token
        }
        requests.post(logout_url, headers=headers)
        # print(exc_type, exc_value, exc_tb, sep="\n")

    @staticmethod
    def jamshid_dev_login(username: str, password: str) -> Dict:
        login_url = "https://api.mafia.jamshid.app/auth/login"
        payload = dict(username=username, pwd=password)
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        response = requests.post(login_url, headers=headers, data=json.dumps(payload))
        data = json.loads(response.text)
        return data["data"]

    @staticmethod
    def recursive_search(user_data, user_id):
        if user_data['_id']['$oid'] == user_id:
            return user_data

    @classmethod
    def get_object_by_id(cls, json_data_list, user_id):

        for json_data in json_data_list:
            result = cls.recursive_search(json_data, user_id)
            if result:
                return result
        return None

    @classmethod
    def get_user_data(cls, self, user_id: str) -> Dict:
        get_all_users_url = "https://api.mafia.jamshid.app/auth/user/get/all/"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.access_token
        }
        response = requests.post(get_all_users_url, headers=headers)
        data = json.loads(response.text)
        user_ids = [user['_id']['$oid'] for user in data["data"]]
        if user_id in user_ids:
            return cls.get_object_by_id(data["data"], user_id)


def get_user_data(user_id: str) -> Dict:
    with GetDevAccess("dev", "dev@1234%") as root:
        return root.get_user_data(root, user_id=user_id)


def check_authentication_api(request, token):
    _, received_token = token.split()
    api_endpoint = 'https://api.mafia.jamshid.app/auth/check-token/'
    headers = {'Authorization': f'Bearer {received_token}'}
    response = JsonResponse
    try:
        response = requests.post(api_endpoint, headers=headers)

        # print(f'response => {str(response)}')
        print(f'response.data => {json.loads(response.text)}')
        # print(f'response.data => {type(json.loads(response.text))}')

        # response_json = response.json()
        response_json = json.loads(response.text)
        if response_json["status"] == 200 or response_json["status"] == 201:
            user_id = request.data.get("user_id")
            if user_id is None:
                user_id = request.query_params.get("user_id")
            AuthenticationApiLogger.info(
                f'successfully authenticated request for user {user_id}')
            return True
        elif response_json["status"] == 500:
            AuthenticationApiLogger.warning(
                f'Unauthorized access to api.mafia.jamshid.app/auth/check-token for user {request.query_params.get("user_id")}')
            return False
    except Exception as err:
        AuthenticationApiLogger.exception(f"Exception occurred: {err}")
        return False


def calculate_commission(event_start_time: int):
    time_difference_hour = (event_start_time - int(timezone.now().timestamp())) / 60 / 60
    if time_difference_hour <= 1:
        return 40, time_difference_hour
    elif 1 <= time_difference_hour <= 5:
        return 80, time_difference_hour
    else:
        return 95, time_difference_hour


def update_mongo(event_id, user_id):
    MONGO_CONNECT = os.environ.get("MONGO_CONNECT")
    mongo_client = MongoClient(MONGO_CONNECT)
    database = mongo_client['conse']
    collection = database["events"]
    event_id = ObjectId(event_id)
    player_id = ObjectId(user_id)
    event_query = {'_id': event_id}

    event = collection.find_one(event_query)
    if event:
        # Find the index of the user in the players array
        player_index = next((index for index, player in enumerate(event['players']) if player['_id'] == player_id),
                            None)
        if player_index is not None:
            # Remove the user from the players array
            del event['players'][player_index]

            # Update the event document
            collection.update_one({'_id': event_id}, {'$set': {'players': event['players']}})

            print(f"User with _id {user_id} removed from event with _id {event_id}")
        else:
            print(f"User with _id {user_id} not found in event with _id {event_id}")
    else:
        print(f"Event with _id {event_id} not found")

        # Close the connection when done
    mongo_client.close()
