import json
import os
import traceback

from .utils.google_fit_parsers import *
from producer import send_records_azure

from logging import getLogger

LOG = getLogger(__name__)

RECORD_PROCESSING = {
    'activity': google_activity_parser,
    'sleep': google_sleep_parser,
    'datastream': google_datastream_parser
}

SCHEMA_LOC = './avro'
SCHEMA_MAPPING = {
    'heartrate': 'fitbit_stream_schema.avsc',
    'activity': 'event_schema.avsc',
    'sleep': 'event_schema.avsc'
    }

TOPIC_MAPPING = {
    'heartrate': 'google_stream_heartrate',
    'activity': 'testhub-new',
    'sleep': 'testhub-new'
}

def send_records_to_personicle(personicle_user_id, records, stream_name, events_topic, limit = None):
    count = 0
    record_formatter = RECORD_PROCESSING[stream_name]
    
    formatted_records = []
    for record in records:
        formatted_record = record_formatter(record, personicle_user_id)
        # send formatted record to event hub
        # events_topic.add(json.dumps(formatted_record))
        formatted_records.append(formatted_record)
        # print(formatted_record)
        count += 1        

        if limit is not None and count <= limit:
            break
    # send data packet to data upload api instead of event hub
    # request_headers = {"accept": "application/json",
    #         "authorization": "Bearer {}".format(personicle_bearer_token)}
    # request_params = {}
    # request_data = {}
    # request_endpoint = os.environ.get("EVENT_WRITE_ENDPOINT")

    # response = requests.post(request_endpoint, headers=request_headers, data=formatted_records)
    # events_topic.set(json.dumps(formatted_records))
    try:
        send_records_azure.send_records_to_eventhub(None, formatted_records, os.environ['EVENTS_EVENTHUB_NAME'])
        return {"success": True, "number_of_records": count}
    except Exception as e:
        LOG.error(traceback.format_exc())
        return {"success": False, "error": e}
