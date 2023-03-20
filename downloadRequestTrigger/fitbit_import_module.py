import requests
from datetime import datetime, timedelta
import json
import os
import time 
import logging
from . import fitbit_upload
LOG = logging.getLogger(__name__)

FITBIT_ACTIVITIES_ENDPOINT = "/1/user/{user_id}/activities/list.json"
FITBIT_SLEEP_LOG_ENDPOINT = "/1.2/user/{user_id}/sleep/list.json"

def fitbit_activity_import(personicle_user_id, access_token, last_accessed_at, fitbit_user_id,events_topic):
    activities_api_endpoint = os.environ['FITBIT_API_ENDPOINT'] + FITBIT_ACTIVITIES_ENDPOINT.format(user_id=fitbit_user_id)
    LOG.info(f"fitbit activity import for user {personicle_user_id}")
    if last_accessed_at is None:
        query_parameters = {
            'beforeDate': datetime.date(datetime.utcnow()),
            'sort': 'desc',
            'offset': 0,
            'limit': 100
        }
    else:
        date = datetime.strptime(last_accessed_at, "%Y-%m-%d %H:%M:%S.%f").date()
        query_parameters = {
            'afterDate': date,
            'sort': 'asc',
            'offset': 0,
            'limit': 100
        }
    query_header = {
        "accept": "application/json",
        "authorization": "Bearer {}".format(access_token)
    }
    LOG.info("Requesting fitbit activities with query parameters: {}".format(query_parameters))

    activities_response = requests.get(activities_api_endpoint, headers=query_header, params=query_parameters)
    activities = json.loads(activities_response.content)
    LOG.info("Received payload: {}".format(json.dumps(activities, indent=2)))
    if 'activities' not in activities:
        LOG.error("Incorrect response received")
        return False, activities
    send_response = fitbit_upload.send_records_to_personicle(personicle_user_id, activities['activities'], 'activity')
    LOG.info(send_response)