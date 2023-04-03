from asyncio import current_task
import datetime
import logging
from typing import List
import databases
import azure.functions as func

# from configparser import ConfigParser
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import select
# from azure.storage.queue import QueueClient
import json
import os
import requests

DATABASE_URL = 'postgresql://{}:{}@{}/{}?sslmode={}'.format(os.environ['DB_CONFIG_USERNAME'], os.environ['DB_CONFIG_PASSWORD'],os.environ['DB_CONFIG_HOST'],os.environ['DB_CONFIG_NAME'], 'prefer')
engine = sqlalchemy.create_engine(
    DATABASE_URL, pool_size=3, max_overflow=0
)
Base = declarative_base(engine)

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


users = sqlalchemy.Table(
    os.environ["CREDENTIALS_TABLENAME"],
    metadata,
    sqlalchemy.Column("id", sqlalchemy.INT, primary_key=True),
    sqlalchemy.Column("userId", sqlalchemy.String, primary_key=True,nullable=False),
    sqlalchemy.Column("service", sqlalchemy.String,nullable=False),
    sqlalchemy.Column("access_token", sqlalchemy.String,nullable=False),
    sqlalchemy.Column("expires_in", sqlalchemy.INT,nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DATETIME,nullable=False, default=datetime.datetime.utcnow()),
    sqlalchemy.Column("external_user_id", sqlalchemy.String),
    sqlalchemy.Column("refresh_token", sqlalchemy.String),
    sqlalchemy.Column("last_accessed_at", sqlalchemy.DATETIME,nullable=True),
    sqlalchemy.Column("scope", sqlalchemy.String,nullable=True),
    sqlalchemy.Column("status", sqlalchemy.String,nullable=True),

    )

async def main(mytimer: func.TimerRequest, datastreamTaskQueue: func.Out[List[str]]) -> None:
    await database.connect()
    # connect_str = os.environ['personicle_STORAGE']
    # queue_client = QueueClient.from_connection_string(connect_str, os.environ["DOWNLOAD_REQUEST_QUEUE"])
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    # query = select(users).where( (users.c.last_accessed_at < (datetime.datetime.utcnow() - datetime.timedelta(hours=1) ) ) | (users.c.last_accessed_at == None ))
    query = select(users).where( (users.c.last_accessed_at < (datetime.datetime.utcnow() - datetime.timedelta(hours=1) ) ) | (users.c.last_accessed_at == None ))
    rows = await database.fetch_all(query)
   
    fetch_data_for = []
    for r in rows:
        data= {}
        if (tuple(r.values())[7]) == None : # no refresh token present, mark status as expired and continue
            if(str(tuple(r.values())[10]) != 'expired'):
                update_status_query = users.update().where(users.c.userId == str(tuple(r.values())[1])).values(status='expired')
                result = await database.execute(update_status_query)
            continue
        data["individual_id"] = tuple(r.values())[1]
        data["service_name"] = tuple(r.values())[2]
        data["service_access_token"] = tuple(r.values())[3]
        data["last_accessed_at"] = str(tuple(r.values())[8])
        data["refresh_token"] = str(tuple(r.values())[7])
        data["expires_in"] = (tuple(r.values())[4])
        data["status"] = str(tuple(r.values())[10])
        data['fitbit_user_id']  = str(tuple(r.values())[6])
        fetch_data_for.append(json.dumps(data))
   
    json_object = fetch_data_for

    data_to_be_fetched = []
    for user in json_object:
        user_object = json.loads(user)
        # print(user_object)
        #  last accessed at can be none
        new_access_token_required = True
        last_accessed_at = user_object['last_accessed_at']

        if last_accessed_at != 'None':
            expires_in = user_object['expires_in']

            last_accessed_at_datetime = datetime.datetime.strptime(str(last_accessed_at), '%Y-%m-%d %H:%M:%S.%f')
            expiration_datetime = last_accessed_at_datetime + datetime.timedelta(seconds=expires_in)
            logging.info(expiration_datetime)
            if expiration_datetime <  datetime.datetime.utcnow():
                logging.info("expired")
                new_access_token_required = True
                # we have refresh tokens, access token is expired
            else:
                # if token is valid but status is marked as expired, update status to connected
                if user_object['status'] == 'expired':
                    update_status_query = users.update().where(users.c.userId == str(user_object['individual_id'])).values(status='connected')
                    result = await database.execute(update_status_query)
                logging.info("access token is valid")
                new_access_token_required = False
        #  we have refresh tokens, but no last accessed time, so refetch access token 
        successfully_fetched_token = False
        if new_access_token_required and user_object['service_name'] == 'google-fit':
            response = await refresh_google_fit_token(user_object,last_accessed_at)
            if response:
             data_to_be_fetched.append(json.dumps(response))
             successfully_fetched_token = True

        if new_access_token_required and user_object['service_name'] == 'fitbit':
            response = await refresh_fitbit_token(user_object,last_accessed_at)
            if response:
                data_to_be_fetched.append(json.dumps(response))
                successfully_fetched_token = True

        # update last accessed at time for this user only if successfully fetched access token
        if successfully_fetched_token:
            current_time = datetime.datetime.strptime(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f'), '%Y-%m-%d %H:%M:%S.%f')
            update_last_accessed_at = users.update().where(users.c.userId == str(user_object['individual_id'])).where(users.c.service == user_object['service_name']).values(last_accessed_at=current_time)
            result = await database.execute(update_last_accessed_at)
    logging.info("Adding data: {}".format(data_to_be_fetched))

    if data_to_be_fetched: datastreamTaskQueue.set(data_to_be_fetched)
    
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    await database.disconnect()


async def refresh_fitbit_token(user_object, last_accessed_at):
    url = os.environ['FITBIT_TOKEN_URL']
    client_id = os.environ['FITBIT_CLIENT_ID']
    client_secret = os.environ['FITBIT_CLIENT_SECRET']
    refresh_token = user_object['refresh_token']
    response = requests.post(
        url,
        auth=(client_id, client_secret),
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
    )   
    # print("refresh fitbit token")
    # print(response.json())
    if response.status_code == 200:
        access_token = response.json()['access_token']
        refresh_token = response.json()['refresh_token']
        expires_in = response.json()['expires_in']
        user_object['service_access_token'] = access_token
        user_object['refresh_token'] = refresh_token
        user_object['last_accessed_at'] = None if last_accessed_at == 'None' else last_accessed_at
        # update status to connected, update refresh and access token. Refresh token needs to be updated as previous refresh token is marked invalid
        update_status_query = users.update().where(users.c.userId == str(user_object['individual_id'])).where(users.c.service == user_object['service_name']).values(status='connected', access_token=access_token, refresh_token=refresh_token, expires_in=expires_in)
        result = await database.execute(update_status_query)
        return user_object

async def refresh_google_fit_token(user_object, last_accessed_at):
    url = os.environ['TOKEN_URL']
    client_id = os.environ['GOOGLE_CLIENT_ID']
    client_secret = os.environ['GOOGLE_CLIENT_SECRET']
    refresh_token = user_object['refresh_token']

    response = requests.post(url, data={
    'grant_type': 'refresh_token',
    'refresh_token': refresh_token,
    'client_id': client_id,
    'client_secret': client_secret
    })
    # print(response.json())
    if response.status_code == 200:
        access_token = response.json()['access_token']
        user_object['service_access_token'] = access_token
        user_object['last_accessed_at'] = None if last_accessed_at == 'None' else last_accessed_at
        update_status_query = users.update().where(users.c.userId == str(user_object['individual_id'])).values(status='connected')
        result = await database.execute(update_status_query)
        return user_object
        data_to_be_fetched.append(json.dumps(user_object))
    else:
            update_status_query = users.update().where(users.c.userId == str(user_object['individual_id'])).values(status='expired')
            result = await database.execute(update_status_query)
            # logging.info('Error: ' + response.json()['error'])
            return False
