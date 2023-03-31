import requests
from datetime import datetime, timedelta
import json
import os
import time 

import logging
from . import google_fit_upload

from utils.google_fit_datasets import get_data_sources, get_dataset_for_datasource
from utils.google_fit_data_mapping import DATA_DICTIONARY

LOG = logging.getLogger(__name__)
SLEEP_ACTIVITY = 72
GOOGLE_FIT_SESSIONS_ENDPOINT = "https://www.googleapis.com/fitness/v1/users/me/sessions"
GOOGLE_FIT_SLEEP_SESSIONS_ENDPOINT = "https://www.googleapis.com/fitness/v1/users/me/sessions?activityType=72"

def google_fit_sessions_import(personicle_user_id, access_token, last_accessed_at, events_topic):
    """
    Get all sleep events and related data from google fit REST api
    Google fit sleep get endpoint: https://www.googleapis.com/fitness/v1/users/me/sessions?startTime=2019-12-05T00:00.000Z&endTime=2019-12-17T23:59:59.999Z&activityType=72
    """
    # google_fit_sleep_endpoint = GOOGLE_FIT_SESSIONS_ENDPOINT.format(activity_type=SLEEP_ACTIVITY)
    if last_accessed_at is None:
        start_time = None
        end_time = datetime.utcnow()
    else:
        start_time = datetime.strptime(last_accessed_at, "%Y-%m-%d %H:%M:%S.%f")
        end_time = None
    count_sessions = 0
    repeat_token = None
    call_api = True
    request_status = False
    while call_api:
        # end_time = start_time + SESSIONS_DATE_OFFSET
        query_parameters = {}
        if start_time:
            query_parameters['startTime'] = start_time.strftime("%Y-%m-%dT%H:%M:%S%zZ")
        if end_time:
            query_parameters['endTime'] = end_time.strftime("%Y-%m-%dT%H:%M:%S%zZ")
        if repeat_token:
            query_parameters['pageToken'] = repeat_token

        query_header = {
            "accept": "application/json",
            "authorization": "Bearer {}".format(access_token)
        }

        LOG.info("Requesting google-fit data for user {} from {} to {}".format(personicle_user_id, start_time, end_time))
    
        activities_response = requests.get(GOOGLE_FIT_SESSIONS_ENDPOINT, headers=query_header, params=query_parameters)
        activities = json.loads(activities_response.content)
        if 'session' not in activities:
            LOG.error("Unexpected response from API")
            LOG.error(json.dumps(activities, indent=2))
            break

        LOG.info("Number of sessions: {}".format(len(activities['session'])))
        LOG.info("Received payload (first 5 events): {}".format(json.dumps(activities['session'][:min(5, len(activities['session']))], indent=2)))

        # SEND DATA TO KAFKA 
        if len(activities['session']) > 0:
            # provide request parameters and data
            request_status=True
            send_response = google_fit_upload.send_records_to_personicle(personicle_user_id, activities['session'], 'activity', events_topic)
            LOG.info(send_response)

        call_api = activities.get('hasMoreData', False)
        repeat_token = activities.get('nextPageToken', None)

        # start_time = end_time
        count_sessions += len(activities['session'])
    LOG.info("Number of sessions sent : {}".format(count_sessions))
    return request_status, count_sessions

def google_fit_dataset_import(personicle_user_id, access_token, last_accessed_at, datastream_queue):
    """
    Get all datasets for the current user
    First need to list all data sources for the user
    Then download the datasets for each data source
    """
    datasources_list = get_data_sources(access_token)
    resp = {}
    data_requests = []
    if last_accessed_at is None:
        end_time = time.time_ns()
        start_time = int(end_time - timedelta(days=365).total_seconds()*1000000000)
    else:
        last_accessed_at = datetime.strptime(last_accessed_at, "%Y-%m-%d %H:%M:%S.%f")
        start_time = int(last_accessed_at.timestamp())*1000000000 + 1
        end_time = time.time_ns()
    # sending requests for 10 days' worth of data at a time
    window_start = start_time
    while window_start < end_time:
        # uncomment the second part of next line for sending data requests for fixed periods (e.g., 10 days)
        window_end = end_time #int(min(end_time, window_start+timedelta(days=10).total_seconds()*1000000000))
        dataset_id = "{}-{}".format(window_start, window_end)

        for source in datasources_list:
            # get the data type from source
            data_type = source['dataType']['name']
            dataset_name = source['dataStreamId']
            
            # map the data type to a table
            if data_type not in DATA_DICTIONARY.keys():
                LOG.warning("Google type {} not in google fit data dictionary".format(data_type))
                continue
            personicle_mapping = DATA_DICTIONARY[data_type]

            # get the data for the source
            # define the time range for the dataset id
            # send request for this in the tsak queue

            data_requests.append(json.dumps({
                "query_parameters": {
                    
                },
                "access_token": access_token,
                "datasource": dataset_name,
                "dataset_id": dataset_id,
                "personicle_data_type": personicle_mapping,
                "personicle_user_id": personicle_user_id,
                "google_datatype": data_type
            }))
            resp[personicle_mapping] = True
            # number_of_datapoints_added = get_dataset_for_datasource(access_token, dataset_name, dataset_id, personicle_mapping, personicle_user_id, datastream_topic)
            # resp[personicle_mapping] = resp.get(personicle_mapping, 0) + number_of_datapoints_added
        datastream_queue.set(data_requests)
        window_start = window_end+1
    return resp

def google_fit_sleep_stages(personicle_user_id, access_token, last_accessed_at, events_topic):
    # if last_accessed_at is None:
    #     start_time_millis = "0"
    #     end_time_millis = str(int(time.time() * 1000))
    # else:
    #     start_time = datetime.strptime(last_accessed_at, "%Y-%m-%d %H:%M:%S.%f")
    #     # start_time_millis = int(start_time.timestamp() * 1000)
    #     start_time_millis = 1675329954000
    #     end_time_millis = str(int(time.time() * 1000))
    with open('utils/google_fit_sleep_stages.json', 'r') as file:
        sleep_stages = json.load(file)
        
    if last_accessed_at is None:
        start_time = None
        end_time = datetime.utcnow()
    else:
        start_time = datetime.strptime(last_accessed_at, "%Y-%m-%d %H:%M:%S.%f")
        end_time = None
    count_sessions = 0
    repeat_token = None
    call_api = True
    request_status = False
    while call_api:
        # end_time = start_time + SESSIONS_DATE_OFFSET
        query_parameters = {}
        # if start_time:
        # query_parameters['startTime'] = start_time_millis   
        # if end_time:
        # query_parameters['endTime'] = end_time_millis
        if start_time:
            query_parameters['startTime'] = start_time.strftime("%Y-%m-%dT%H:%M:%S%zZ")
        if end_time:
            query_parameters['endTime'] = end_time.strftime("%Y-%m-%dT%H:%M:%S%zZ")
        if repeat_token:
            query_parameters['pageToken'] = repeat_token
        query_parameters['activityType'] = 72   

        query_header = {
            "accept": "application/json",
            "authorization": "Bearer {}".format(access_token)
        }

        LOG.info("Requesting google-fit sleep data for user {} from {} to {}".format(personicle_user_id, start_time, end_time))
    
        activities_response = requests.get(GOOGLE_FIT_SESSIONS_ENDPOINT, headers=query_header, params=query_parameters)
        activities = json.loads(activities_response.content)
        if 'session' not in activities:
            LOG.error("Unexpected response from API")
            LOG.error(json.dumps(activities, indent=2))
            break

        LOG.info("Number of sessions: {}".format(len(activities['session'])))
        LOG.info("Received payload (first 5 events): {}".format(json.dumps(activities['session'][:min(5, len(activities['session']))], indent=2)))
        response_data = activities_response.json()
        sessions = response_data.get("session", [])
        data_source_type = "derived"
        data_type = "com.google.sleep.segment"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(access_token)
        }
        records = []

        for session in sessions:
             if session.get("activityType") == 72:
                 start_time_millis = session.get("startTimeMillis")
                 end_time_millis = session.get("endTimeMillis")
                 LOG.info(session)
                 # request sleep stages for this session here
                #  url = "https://www.googleapis.com/fitness/v1/users/me/dataSources/" + data_source_type + ":" + data_type + "/datasets/" + str(start_time_millis) + "-" + str(end_time_millis)
                 url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
                #  params = {
                #     "startTimeMillis": start_time_millis,
                #     "endTimeMillis": end_time_millis,
                #     "aggregateBy": "com.google.sleep.segment.sleep_class",
                #     "bucketByTime": "300s"
                #  }
                 request_body = {
                        "aggregateBy": [
                            {
                            "dataTypeName": "com.google.sleep.segment"
                            }
                        ],
                        "endTimeMillis": end_time_millis,
                        "startTimeMillis": start_time_millis
                        }
                 response = requests.post(url, headers=headers, data=json.dumps(request_body))
                 
                 LOG.info(response.json())
                 if response.status_code != requests.codes.ok:
                     LOG.error(f"Request failed with error {response.status_code} and message {response.text}")
                     break
                 response_data = response.json()
                 if "bucket" in response.json():
                     for bucket in response.json()["bucket"]:
                         start_time_for_sleep_stage = int(bucket["startTimeMillis"])
                         end_time_for_sleep_stage = int(bucket["endTimeMillis"])
                         LOG.info(f"sleep session start_time: {start_time_millis}, sleep session end_time: {end_time_millis}")
                         if "dataset" in bucket:
                              for dataset in bucket["dataset"]:
                                  if "point" in dataset:
                                       for point in dataset["point"]:
                                            sleep_stage = point["value"][0]["intVal"]
                                            new_record = {}
                                            new_record['individual_id'] = personicle_user_id
                                            new_record['startTimeMillis'] = start_time_for_sleep_stage
                                            new_record['endTimeMillis'] = end_time_for_sleep_stage
                                            new_record['name'] = sleep_stages[f'{sleep_stage}']
                                            new_record['application'] = session['application']
                                            records.append(new_record)
                                            LOG.info(f"Sleep stage: {sleep_stage}, Start time: {start_time_for_sleep_stage}, End time: {end_time_for_sleep_stage}")
                #  sleep_stages = response_data.get("bucket", []) 
                #  for stage in sleep_stages:
                #     sleep_datasets = stage.get("dataset")
        #             start_time_millis = stage.get("startTimeMillis")
        #             end_time_millis = stage.get("endTimeMillis")
        #             duration_millis = stage.get("durationMillis")
        #             print(f"Sleep session start time: {start_time_millis}")
        #             print(f"Sleep session end time: {end_time_millis}")
        #             print(f"Sleep stage: {sleep_class}")
        #             print(f"Stage duration: {duration_millis} milliseconds")
        # # SEND DATA TO KAFKA 
        # if len(activities['session']) > 0:
        #     # provide request parameters and data
        #     request_status=True
        #     LOG.info(send_response)
        send_response = google_fit_upload.send_records_to_personicle(personicle_user_id, records, 'activity', events_topic)

        call_api = activities.get('hasMoreData', False)
        repeat_token = activities.get('nextPageToken', None)

        # start_time = end_time
        count_sessions += len(activities['session'])
    LOG.info("Number of sessions sent : {}".format(count_sessions))
    return request_status, count_sessions
    

