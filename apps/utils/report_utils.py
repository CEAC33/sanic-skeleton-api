# External dependencies
from sanic.response import text, json
from sanic.log import logger
from sanic import response as sanic_response
import asyncio
import copy
import time
import subprocess
import socket
import time
from sanic_openapi import doc

import logging
logging.basicConfig(filename='logs.txt',level=logging.WARNING)

# Internal dependencies
from apps.utils.aio_utils import get
from apps.utils.datetime_utils import change_datetime_format, get_current_date, change_date_format
from apps.utils.format_utils import change_to_int_format, list_to_comma_separated_string
from apps.utils.connection_utils import check_connection
from apps.utils.dict_utils import nested_set, nested_get, nested_get_format, nested_append
from apps.utils.csv_utils import create_general_csv, create_permission_csv, delete_all_csv
from apps.utils.mongo_utils import save_csv_to_mongo
from apps.es_report.es_querys import *
# from config import *

# dictionary to store the result of the report
result = {}

# FUNCTIONS TO PROCESS DATA

async def generate_report_synchronous(config, csv_name, config_id=None):
    es_connection = await check_connection(config)

    if es_connection == 'down':
        return json({'error': 'Elasticsearch is not available'})

    # removing previous CSV
    await delete_all_csv()

    # Extracting Agreement Fields
    for fw in config.FW_LIST:
        await nested_append(config.AGREEMENT_LIST_QUERY, config.AGREEMENT_LIST_QUERY_FW_KEY, {"match": {"agreement_framework.raw": fw}})
    logger.info('AGREEMENT_LIST_QUERY')    
    logger.info(config.AGREEMENT_LIST_QUERY) 
    response = await gather_get(config.ES_URL.format(doc_type='agreement_index'), config.AGREEMENT_LIST_QUERY, 'agreement', config)

    # Extracting Tag Fields
    for fw in config.FW_LIST:
        await nested_append(config.TAG_LIST_QUERY, config.TAG_LIST_QUERY_FW_KEY, {"match": {"tag_framework": fw}})
    for tag in config.TAG_LIST:
        await nested_append(config.TAG_LIST_QUERY, config.TAG_LIST_QUERY_TAG_KEY, {"match": {"tag_name": tag}})

    logger.info('TAG_LIST_QUERY')    
    logger.info(config.TAG_LIST_QUERY) 
    response = await gather_get(config.ES_URL.format(doc_type='tag_index'), config.TAG_LIST_QUERY, 'tag', config)

    logger.info('\n\n\nSEARCH FINISHED! B|')

    # creating CSV
    logger.info('\n\n\nCREATING CSV ...')
    await create_permission_csv(result, 'permission_'+csv_name, 'utf-8', config.CSV_HEADERS, config)
    await create_general_csv(result, csv_name, 'utf-8', config.CSV_HEADERS, config)
    
    logger.info('\n\n\n CSV for today created and saved, now you can download it in /es_report/download_report')

    # saving to mongo
    await save_csv_to_mongo('permission_'+csv_name, config, config_id)
    logger.info('\n\n\n Data sent and saved in Mongo!')

    
    return json({'result':'success', 'size': len(result)})

async def get_agreement_fields_from_response(res, config):
    if res:
        if res.get("hits"):
            for element in res['hits']['hits']:

                agreement_id = element["_id"]
                data = element['_source']

                # logger.info('AGREEMENT agreement_id:')
                # logger.info(agreement_id)

                # getting agreement fields requested in the config
                for key in config.AGREEMENT_ES_KEYS.keys():
                    try:
                        result[agreement_id][key] = await nested_get_format(data, config.AGREEMENT_ES_KEYS, key, config)
                    except KeyError:
                        result[agreement_id] = {key: ""}
                        result[agreement_id][key] = await nested_get_format(data, config.AGREEMENT_ES_KEYS, key, config)
                    # logger.info(result[agreement_id][key])

                # getting agreement permissions requested in the config
                for key in config.PERMISSION_ES_KEYS.keys():
                    # print('INSIDE PERMISSIONS')
                    tmp = await nested_get_format(data, config.PERMISSION_ES_KEYS, key, config)
                    permission_format = ""
                    for element in tmp:
                        permission_format = permission_format+'[{}]'.format(element)
                    # print(permission_format)
                    result[agreement_id][key] = permission_format
                    # logger.info(result[agreement_id][key])
                # logger.info('---------------------------------------------------------------')

async def get_tag_fields_from_response(res, config):
    if res:
        if res.get("hits"):
            for element in res['hits']['hits']:
                agreement_id = element["_parent"]
                data = element['_source']
                # logger.info('TAG '+data.get("tag_name")+' agreement_id:')
                # logger.info(agreement_id)
                try:
                    key = data.get("tag_name")
                    result[agreement_id][key] = await nested_get_format(data, config.TAG_LIST, key, config)
                except KeyError:
                    "This tag is not included in the requested agreements"
                # logger.info('---------------------------------------------------------------')

async def gather_get(url, query, doc_type, config):  
    # logger.info('INSIDE gather_get')
    # logger.info(url)
    # logger.info(query)
    response = await get(url, query)
    # logger.info(response)
    try:
        scroll_id = response.get('_scroll_id')
    except Exception as e:
        logger.error(e)
        logger.info('RETRYING')
        await gather_get(url, query, doc_type, config)
        return
    result_info = True
    # logger.info(response)
    retry_count = 0
    while result_info:
        # logger.info('DEBUGGING SCROLL:')
        # logger.info(response)
        # logger.info(scroll_id)
        # logger.info(config.SCROLL_ES_URL)
        # logger.info(config.SCROLL_ES_ALIVE)
        if doc_type == 'agreement':
            await get_agreement_fields_from_response(response, config) 
        if doc_type == 'tag':
            await get_tag_fields_from_response(response, config)
        response = await get(config.SCROLL_ES_URL, {"scroll":config.SCROLL_ES_ALIVE, "scroll_id":scroll_id})
        
        try:
            if not response['hits']['hits']: #or len(result) > 500:
                result_info = False
                logger.info('Scroll for {} finished'.format(scroll_id))
        except (KeyError, TypeError) as e: # ES capacity is full, waiting to retry
            logger.error(e)
            logger.info('result size: {}'.format(len(result)))
            if retry_count > 50:
                result_info = False
            time.sleep(3)
            logger.info('RESPONSE: {}'.format(response))
            logger.info('RETRYING SCROLL')

            retry_count = retry_count + 1

async def batch_of_get_requests(url, json_list, doc_type):  
    # logger.info('INSIDE batch_of_get_requests')
    # logger.info(json_list)
    await asyncio.gather(
        *[gather_get(url, json, doc_type) for json in json_list]
    )


#--------------------------------------------------------------

# TODO:FIND A WAY THAT ES CAN HANDLE THIS WAY TO GENERATE THE REPORT (ASYNCHRONOUS)

# async def generate_report_asynchronous(request):
#     es_connection = await check_connection()

#     if es_connection == 'down':
#         return json({'error': 'Elasticsearch is not available'})

#     # removing previous CSV
#     await delete_all_csv()

#     # Extracting Agreement Fields

#     agreement_query_list = []

#     for fw in FW_LIST:
#         await nested_set(AGREEMENT_QUERY, AGREEMENT_QUERY_FW_KEY, fw)
#         agreement_query_list.append(copy.deepcopy(AGREEMENT_QUERY))
        
#     response = await batch_of_get_requests(ES_URL.format(doc_type='agreement_index'), agreement_query_list, 'agreement')

#     # Extracting Tag Fields

#     tag_query_list = []

#     for fw in FW_LIST:
#         await nested_set(TAG_QUERY, TAG_QUERY_FW_KEY, fw)
#         for tag in TAG_LIST:
#             await nested_set(TAG_QUERY, TAG_QUERY_TAG_KEY, tag)
#             tag_query_list.append(copy.deepcopy(TAG_QUERY))

#     response = await batch_of_get_requests(ES_URL.format(doc_type='tag_index'), tag_query_list, 'tag')

#     logger.info('\n\n\nSEARCH FINISHED! B|')

#     # creating CSV
#     logger.info('\n\n\nCREATING CSV ...')
#     csv_name = 'DXC - Power BI report {}-{}-{}.csv'.format(now.year, now.month, now.day)
#     await create_permission_csv(result, 'permission_'+csv_name, 'utf-8', CSV_FIELDS)
#     await create_general_csv(result, csv_name, 'utf-8', CSV_FIELDS)
    
#     logger.info('\n\n\n CSV for today created and saved, now you can download it in /es_report/download_report')
    
#     #saving to mongo
#     await save_csv_to_mongo(csv_name)
#     logger.info('\n\n\n Data sent and saved in Mongo!')

#     logger.info({'result':'success', 'size': len(result))
#     return json({'result':'success', 'size': len(result)})