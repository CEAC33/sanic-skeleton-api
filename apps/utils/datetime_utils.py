from datetime import datetime

def get_current_date():
    return datetime.now()

async def change_date_format(string_date):
    if string_date:
        try:
            format_string_date = datetime.strptime(string_date, '%m/%d/%y').strftime('%m/%d/%Y')
        except ValueError:
            try:
                format_string_date = datetime.strptime(string_date, '%Y-%m-%d').strftime('%m/%d/%Y')
            except ValueError:
                format_string_date = datetime.strptime(string_date, '%m/%d/%Y').strftime('%m/%d/%Y')
        return format_string_date
    else:
        return ""

async def change_datetime_format(string_datetime):
    if string_datetime:
        try:
            format_string_datetime = datetime.strptime(string_datetime.split('+')[0], '%Y-%m-%dT%H:%M:%S.%f').strftime('%m/%d/%Y %H:%M')
        except ValueError:
            format_string_datetime = datetime.strptime(string_datetime.split('+')[0], '%Y-%m-%dT%H:%M:%S').strftime('%m/%d/%Y %H:%M')
        return format_string_datetime

    else:
        return ""