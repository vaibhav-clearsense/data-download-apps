import logging
import json
import traceback
from typing import List
import azure.functions as func

from downloadRequestTrigger.fitbit_import_module import fitbit_activity_import, fitbit_sleep_import
from .google_fit_import_module import google_fit_sessions_import, google_fit_dataset_import, google_fit_sleep_stages


def main(msg: func.QueueMessage, eventsTopic: func.Out[List[str]], datastreamTaskQueue: func.Out[List[str]]) -> None:
    """
    message format: {"individual_id" : <personicle_user_id>, 
                    "service_name": <external service name>, "service_access_token": <access token>,
                    "last_accesed_at" : <timestamp for last successful data download request>}
    """
    request_message = json.loads(msg.get_body().decode('utf-8'))
    logging.basicConfig(level=logging.WARNING, str='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
    logging.info('Python queue trigger function processed a queue item: %s',
                 request_message)
    try:
        required_args = ["individual_id", "service_name", "service_access_token", "last_accessed_at"]
        assert all([x in request_message for x in required_args]), "missing parameter in the request {}".format(json.dumps(required_args))
        if request_message['service_name'] == 'google-fit':
            events_response = google_fit_sessions_import(request_message["individual_id"], 
                    request_message["service_access_token"], request_message['last_accessed_at'], eventsTopic)
            logging.info("Processed event request")
            logging.info(str(events_response))
            datasets_response = google_fit_dataset_import(request_message["individual_id"], request_message["service_access_token"], request_message['last_accessed_at'], datastreamTaskQueue)
            logging.info("Processed datastream request")
            logging.info(str(datasets_response))
            sleep_stages_response = google_fit_sleep_stages(request_message["individual_id"], 
                    request_message["service_access_token"], request_message['last_accessed_at'], eventsTopic)
        if request_message['service_name'] == 'fitbit':
            # need to pass fitbit user id (external user id) in the queue message
            print("fitbit event download request trigger")
            print(request_message)
            fitbit_activity_response  = fitbit_activity_import(request_message["individual_id"], 
                request_message["service_access_token"], request_message['last_accessed_at'], request_message['fitbit_user_id'])
            fitbit_sleep_response = fitbit_sleep_import(request_message["individual_id"], 
                request_message["service_access_token"], request_message['last_accessed_at'], request_message['fitbit_user_id'])
            logging.info("Processed fitbit activity request")


    except AssertionError as e:
        logging.error("Missing parameter in data download request")
        logging.error(e)
        
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc())
