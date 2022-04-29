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
    )

async def main(mytimer: func.TimerRequest, datastreamTaskQueue: func.Out[List[str]]) -> None:
    await database.connect()
    # connect_str = os.environ['personicle_STORAGE']
    # queue_client = QueueClient.from_connection_string(connect_str, os.environ["DOWNLOAD_REQUEST_QUEUE"])

    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    query = select(users).where(users.c.last_accessed_at < (datetime.datetime.utcnow() - datetime.timedelta(hours=1))) 
    rows = await database.fetch_all(query)
    fetch_data_for = []
    for r in rows:
        data= {}
        data["individual_id"] = tuple(r.values())[1]
        data["service_name"] = tuple(r.values())[2]
        data["service_access_token"] = tuple(r.values())[3]
        data["last_accessed_at"] = str(tuple(r.values())[8])
        fetch_data_for.append(json.dumps(data))

    json_object = fetch_data_for

    logging.info("Adding data: {}".format(json_object))
    # queue_client.send_message(json_object)
    datastreamTaskQueue.set(json_object)

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    await database.disconnect()
