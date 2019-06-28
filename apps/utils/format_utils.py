from sanic.log import logger

async def change_to_int_format(number):
    # logger.info('INSIDE change_to_int_format')
    # logger.info(number)
    if number == "" or number == {}:
        return ""
    elif type(number) == str:
        try:
            return int(number)
        except:
            return number 
    else:
        return int(number)

async def list_to_comma_separated_string(my_list):
    if my_list == []:
        return ""
    else:
        return ", ".join(my_list)