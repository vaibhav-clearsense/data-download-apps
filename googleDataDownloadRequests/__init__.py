import logging
import json
import traceback
import azure.functions as func
import requests
import os
from utils.google_fit_parsers import google_datastream_parser
from producer.send_datastreams_to_azure import datastream_producer
GOOGLE_FIT_DATA_SET = "https://www.googleapis.com/fitness/v1/users/me/dataSources/{dataSourceId}/datasets/{datasetId}"

def main(msg: func.QueueMessage, datastreamTopic: func.Out[str], datastreamTaskQueue: func.Out[str]) -> None:
    """
    Request format:
    query_parameters: JSON
    access_token
    datasource
    dataset_id
    personicle_data_type
    personicle_user_id
    """
    logging.info('Python queue trigger function processed a queue item: %s',
                 msg.get_body().decode('utf-8'))
    request_message = json.loads(msg.get_body().decode('utf-8'))

    query_parameters = request_message['query_parameters']
    datasource = request_message['datasource']
    dataset_id = request_message['dataset_id']
    personicle_data_type = request_message['personicle_data_type']
    personicle_user_id = request_message['personicle_user_id']

    total_data_points=0

    query_header = {
            "accept": "application/json",
            "authorization": "Bearer {}".format(request_message['access_token'])
        }

    logging.info("Requesting google-fit data {} for Time range {}".format(datasource, dataset_id))
    next_page = True

    while next_page:
        dataset_response = requests.get(GOOGLE_FIT_DATA_SET.format(dataSourceId=datasource, datasetId=dataset_id), 
                                    headers=query_header, params=query_parameters)
        dataset = json.loads(dataset_response.content)

        # if the API call throws an error
        if 'error' in dataset.keys():
            logging.error(dataset['error'])
            return

        if 'point' not in dataset.keys():
            logging.error("Unknown response received: {}".format(dataset))
            return

        logging.info("Number of data points: {}".format(len(dataset['point'])))
        if len(dataset['point']) == 0:
            logging.info("No data received")
            return

        logging.info("Received payload (first 10 data points): {}".format(json.dumps(dataset['point'][:min(10, len(dataset['point']))], indent=2)))

        # find personicle data dictionary for the dataset
        
        stream_information = requests.get(os.environ.get("VALIDATION_ENDPOINT")+"/match-data-dictionary", params={
            "data_type": "datastream",
            "stream_name": personicle_data_type
        }, verify=False)
        
        # personicle_data_description = find_datastream(personicle_data_type)
        if stream_information.status_code != requests.codes.ok:
            logging.warn("Data type {} not present in personicle data dictionary".format(personicle_data_type))
            logging.warn(stream_information.text)
            return 
        logging.info(stream_information.text)
        personicle_data_description = json.loads(stream_information.text)

        # format the records to match the avro schema
        formatted_records = google_datastream_parser(dataset, personicle_data_type, personicle_data_description, personicle_user_id)
        logging.debug("Formatted records: {}".format(json.dumps(formatted_records, indent=2)))
        logging.info("Validating records against schema object: {}".format(json.dumps(personicle_data_description, indent=2)))
        # validate if the data points match the avro schema
        if formatted_records is None:
            logging.info("Total data points added for source {}: {}".format(datasource, total_data_points))
            return 
            
        validated_records = requests.post(os.environ.get("VALIDATION_ENDPOINT")+"/validate-data-packet", params={
            "data_type": "datastream",
        }, json=formatted_records, verify=False)
        logging.info("Received response from validation server: {}".format(validated_records.text))
        # validation_response = json.loads(validated_records.text)
        # validate_datastream_schema(formatted_records, personicle_data_description['base_schema'])
        if validated_records.status_code != requests.codes.ok or (not json.loads(validated_records.text).get("schema_check", False)):
            logging.info("Total data points added for source {}: {}".format(datasource, total_data_points))
            logging.error("formatted records do not match the specified schema: {} \nRecords: {}".format(personicle_data_description["base_schema"], json.dumps(formatted_records, indent=2)))
            return 

        # send data to write api
        try:

            # datastreamTopic.set(json.dumps(formatted_records))
            # datastream_topic.add(json.dumps(formatted_records))
            # send_data_response = requests.post(os.environ.get("DATASTREAM_WRITE_ENDPOINT"), params={}, data=formatted_records, headers={})
            datastream_producer(formatted_records)
        except Exception as e:
            logging.info("Total data points added for source {}: {}".format(datasource, total_data_points))
            logging.error(traceback.format_exc())
            return

        total_data_points += len(dataset['point'])

        # get next page token
        next_page_token = dataset.get('nextPageToken', None)
        if next_page_token:
            logging.info("Next page token found")
            query_parameters = {
                "nextPageToken": next_page_token
            }
            # if there is a next page token then generate another request
            # datastreamTaskQueue.set(json.dumps({
            #     "query_parameters": {
            #         "nextPageToken": next_page_token
            #     },
            #     "access_token": request_message['access_token'],
            #     "datasource": datasource,
            #     "dataset_id": dataset_id,
            #     "personicle_data_type": personicle_data_type,
            #     "personicle_user_id": personicle_user_id
            # }))
        else: 
            next_page = False

    return
