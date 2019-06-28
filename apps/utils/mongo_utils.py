from pymongo import MongoClient
import pandas as pd
from sanic.log import logger
from config import *
from bson.objectid import ObjectId
import copy
import json


async def save_csv_to_mongo(config, csv_file, config_id): 
    client = MongoClient(config.MONGO_HOST, config.MONGO_PORT)
    db=client.exago

    if config_id:
        logger.info('CREATING MONGO COLLECTION')
        logger.info(config_id)
        reports = db[config_id]
    else:
        reports = db.report
    x = reports.delete_many({}) #delete all previous documents
    logger.info("{} documents to be updated".format(x.deleted_count))
    df = pd.read_csv(csv_file, low_memory=False) #csv file which you want to import
    df = df.where((pd.notnull(df)), None) # changa NaN value for None (null in mongo)
    records_ = df.to_dict(orient = 'records')
    result = reports.insert_many(records_)

async def save_to_mongo(config, data, collection):
    client = MongoClient(config.MONGO_HOST, config.MONGO_PORT)
    db=client.exago
    my_collection = db[collection]
    my_collection_id = my_collection.insert_one(data).inserted_id
    return str(my_collection_id)

async def get_from_mongo(config, collection, value_match, key_match='_id'):
    client = MongoClient(config.MONGO_HOST, config.MONGO_PORT)
    db=client.exago
    my_collection = db[collection]

    if key_match == '_id':
        for x in my_collection.find({ key_match : ObjectId(value_match)}):
            result = x

        result[key_match] = str(result[key_match])
    else:
        for x in my_collection.find({ key_match : value_match}):
            result = x

    return result

