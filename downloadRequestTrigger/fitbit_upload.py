import json
import os
import traceback
from downloadRequestTrigger.utils.fitbit_parsers import fitbit_activity_parser, fitbit_sleep_parser, format_heartrate
from producer import send_records_azure
from logging import getLogger
import logging
LOG = logging.getLogger(__name__)

RECORD_PROCESSING = {
    'heartrate': format_heartrate,
    'activity': fitbit_activity_parser ,
    'sleep': fitbit_sleep_parser
}

SCHEMA_LOC = './avro'
SCHEMA_MAPPING = {
    'heartrate': 'fitbit_stream_schema.avsc',
    'activity': 'event_schema.avsc',
    'sleep': 'event_schema.avsc'
}

TOPIC_MAPPING = {
    'heartrate': 'fitbit_stream_heartrate',
    'activity': 'testhub-new',
    'sleep': 'testhub-new'
}

def send_records_to_personicle(personicle_user_id, records, stream_name, limit = None):
    count = 0
    record_formatter = RECORD_PROCESSING[stream_name]
    schema = SCHEMA_MAPPING[stream_name]
    topic = TOPIC_MAPPING[stream_name]
    formatted_records = []
    for record in records:
        formatted_record = record_formatter(record, personicle_user_id)
        if type(formatted_record) is dict:
            formatted_records.append(formatted_record)
        elif type(formatted_record) is list:
            formatted_records.extend(formatted_record)
        else:
            LOG.error("Record not processed correctly for stream {}, record data: {} \n formatted record: {}".format(stream_name, json.dumps(record, indent=2), json.dumps(formatted_record, indent=2)))
            
        count += 1

        if limit is not None and count <= limit:
            break

    try:
        send_records_azure.send_records_to_eventhub(None, formatted_records, os.environ['EVENTS_EVENTHUB_NAME'])
        return {"success": True, "number_of_records": count}
    except Exception as e:
        LOG.error(traceback.format_exc())
        return {"success": False, "error": e}

