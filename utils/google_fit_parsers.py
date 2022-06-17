from datetime import datetime
# import pytz
import json
import logging


LOG = logging.getLogger(__name__)

# TO DO: Add a unit conversion module for data streams

def google_activity_parser(raw_event, personicle_user_id):
    """
    Format an activity received from google fit API to personicle event schema
    """
    new_event_record = {}
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=None)
    new_event_record['individual_id'] = personicle_user_id
    # timestamp format 2021-11-25T09:27:30.000-08:00
    new_event_record['start_time'] = str(datetime.utcfromtimestamp(int(raw_event['startTimeMillis'])/1000.0))
    duration = int(raw_event['endTimeMillis']) - int(raw_event['startTimeMillis'])
    new_event_record['end_time'] = str(datetime.utcfromtimestamp(int(raw_event['endTimeMillis'])/1000.0))

    new_event_record['event_name'] = raw_event['name']
    new_event_record['source'] = 'google-fit'
    new_event_record['parameters'] = json.dumps({
        "duration": duration,
        "source_device": raw_event['application']
    })
    return new_event_record

def google_sleep_parser(raw_event, personicle_user_id):
    pass

def google_datastream_parser(raw_records, stream_name, stream_info, personicle_user_id):
    """
    Convert datasets received from google fit rest API to personicle data stream schema
    raw_event: Messags received from the google fit rest API, format shown below
    stream_name: personicle data type for the data stream
    personicle_user_id: id for the user in the personicle ecosystem

    Input record format: 
        {
        "minStartTimeNs": "1614841219654238976",
        "maxEndTimeNs": "1646377219654239000",
        "dataSourceId": "derived:com.google.active_minutes:com.google.android.fit:OnePlus:ONE A2003:c0a93253:top_level",
        "point": [
            {
            "startTimeNanos": "1624605660000000000",
            "endTimeNanos": "1624605720000000000",
            "dataTypeName": "com.google.active_minutes",
            "originDataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps",
            "value": [
                {
                "intVal": 1,
                "mapVal": []
                }
            ],
            "modifiedTimeMillis": "1624606705659"
            }
        ]
        }
    Output record format:
        {
            "streamName":<personicle stream name>,
            "individual_id":<personicle individual id>,
            "source":<source application>,
            "confidence":<float 0-1, optional>,
            "unit":<string, optional>,
            "dataPoints": [
                {
                    "timestamp":<timestamp of data point>,
                    "value": <data point value>
                }
            ]
        }
    """
    return_message = {
        "streamName": stream_name,
        "individual_id": personicle_user_id,
        "source": "google-fit",
        "unit": stream_info['Unit'],
        "dataPoints": []
    }

    LOG.info("Initial message template: {}".format(json.dumps(return_message, indent=2)))
    data_points = raw_records.get('point', [])
    if len(data_points) == 0:
        return None

    for point in data_points:
        return_message['dataPoints'].append({
            "timestamp": str(datetime.fromtimestamp(int(point['endTimeNanos'])/10**9)),# point['endTimeNanos'],
            "value": _datapoint_formatter(point['value'][0], stream_info['ValueType'])
        })
    return return_message
    

def _datapoint_formatter(value, value_type: str):
    if "integer" in value_type.lower():
        return int(value['intVal'] if value.get('intVal', None) is not None else value.get('fpVal', None))
    elif "numeric" in value_type.lower():
        return float(value['intVal'] if value.get('intVal', None) is not None else value.get('fpVal', None))


def google_interval_datastream_parser(raw_records, stream_name, stream_info, personicle_user_id):
    """
    Convert datasets received from google fit rest API to personicle data stream schema
    raw_event: Messags received from the google fit rest API, format shown below
    stream_name: personicle data type for the data stream
    personicle_user_id: id for the user in the personicle ecosystem

    Input record format:
        {
        "minStartTimeNs": "1614841219654238976",
        "maxEndTimeNs": "1646377219654239000",
        "dataSourceId": "derived:com.google.active_minutes:com.google.android.fit:OnePlus:ONE A2003:c0a93253:top_level",
        "point": [
            {
            "startTimeNanos": "1624605660000000000",
            "endTimeNanos": "1624605720000000000",
            "dataTypeName": "com.google.active_minutes",
            "originDataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps",
            "value": [
                {
                "intVal": 1,
                "mapVal": []
                }
            ],
            "modifiedTimeMillis": "1624606705659"
            }
        ]
        }
    Output record format:
        {
            "streamName":<personicle stream name>,
            "individual_id":<personicle individual id>,
            "source":<source application>,
            "confidence":<float 0-1, optional>,
            "unit":<string, optional>,
            "dataPoints": [
                {
                    "timestamp":<timestamp of data point>,
                    "value": <data point value>
                }
            ]
        }
    """
    return_message = {
        "streamName": stream_name,
        "individual_id": personicle_user_id,
        "source": "google-fit",
        "unit": stream_info['Unit'],
        "dataPoints": []
    }

    LOG.info("Initial message template: {}".format(json.dumps(return_message, indent=2)))
    data_points = raw_records.get('point', [])
    if len(data_points) == 0:
        return None

    for point in data_points:
        return_message['dataPoints'].append({
            #"timestamp": str(datetime.fromtimestamp(int(point['endTimeNanos'])/10**9)),# point['endTimeNanos'],
            "starttime": str(datetime.fromtimestamp(int(point['startTimeNanos']) / 10 ** 9))
            "endtime": str(datetime.fromtimestamp(int(point['endTimeNanos']) / 10 ** 9))
            "value": _datapoint_formatter(point['value'][0], stream_info['ValueType'])
        })
    return return_message

