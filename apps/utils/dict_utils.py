from sanic.log import logger
import copy
import json

from apps.utils.datetime_utils import change_datetime_format, get_current_date, change_date_format
from apps.utils.format_utils import change_to_int_format, list_to_comma_separated_string

class ndict(dict):
    def __getitem__(self, key):
        if key in self: return self.get(key)
        return self.setdefault(key, ndict())

async def nested_get(d, key_list):
    tmp = ndict(d)
    for key in key_list:
        try:
            tmp = tmp[key]
        except (IndexError, TypeError): # list index out of range, empty list
            tmp = ""
    return tmp

async def nested_get_format(d, keys_dictionary, key, config):
    if type(keys_dictionary) == dict: 
        key_list = keys_dictionary[key]
    elif type(keys_dictionary) == list: 
        key_list = ["tag_value"]

    tmp = await nested_get(d, key_list)

    # handling multiple values inside a field
    if 0 in key_list:
        iterable_keys = key_list
        final_result = []
        iterable_result = None
        while iterable_result != {}:
            iterable_result = await nested_get(d, iterable_keys)
            if iterable_result in [{}, '']:
                break
            else:
                final_result.append(copy.deepcopy(iterable_result))
            iterable_keys = [x+1 if type(x)==int else x for x in iterable_keys]
        tmp = await list_to_comma_separated_string(final_result)
    else:
        tmp = await nested_get(d, key_list)
            
    if tmp == {}:
        tmp = ""

    return tmp

async def nested_set(dic, keys, value, create_missing=False):
    d = dic
    for key in keys[:-1]:
        if key in d or type(d) == list:
            d = d[key]
        elif create_missing:
            d = d.setdefault(key, {})
        else:
            return dic
    if keys[-1] in d or create_missing:
        d[keys[-1]] = value
    return dic

async def nested_append(dic, keys, value, create_missing=False):
    d = dic
    for key in keys[:-1]:
        if key in d or type(d) == list:
            d = d[key]
        elif create_missing:
            d = d.setdefault(key, {})
        else:
            return dic
    if keys[-1] in d or create_missing:
        d[keys[-1]].append(value)
    return dic

async def nested_set_append(dic, keys, value, create_missing=False):
    creation_keys = copy.deepcopy(keys)
    creation_keys = [0 if x=="append_list" or x=="create_list" else x for x in creation_keys]
    if await nested_get(dic, creation_keys[:-1]) in [{}, '']:
        for i, key in enumerate(keys):
            if key != "create_list" and key != "append_list":
                if await nested_get(dic, creation_keys[:i+1]) != '':
                    await nested_set(dic, creation_keys[:i+1], await nested_get(dic, creation_keys[:i+1]), create_missing=create_missing)
                else:
                    await nested_set(dic, creation_keys[:i+1], {}, create_missing=create_missing)
            else:
                if await nested_get(dic, creation_keys[:i+1]) != '':
                    await nested_set(dic, creation_keys[:i], [await nested_get(dic, creation_keys[:i+1])], create_missing=create_missing)
                else:
                    await nested_set(dic, creation_keys[:i], [], create_missing=create_missing)
    if keys[-1] != "append_list":
        await nested_set(dic, creation_keys, value, create_missing=create_missing)
    elif keys[-1] == "append_list":
        value_c = copy.deepcopy(value)
        if await nested_get(dic, creation_keys) == {}:
            await nested_set(dic, creation_keys, value_c, create_missing=create_missing)
        else:
            dic = await nested_append(dic, creation_keys[:-1], value_c, create_missing=False)
    return dic

async def to_json(myjson):
  try:
    json_object = json.loads(myjson)
  except (ValueError, e):
    return False
  return True, json_object