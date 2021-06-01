import pandas as pd

from celery.task import task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
import datetime


User = get_user_model()

logger = get_task_logger(__name__)

@task(name="send_confirmation_email_task")
def extract_file_and_save_info_into_db(fileinfo_id):
    from .models import FileInfo, Data

    deleted_previous_data = Data.objects.all().delete()

    file_info = FileInfo.objects.get(id=fileinfo_id)
    logger.info(f'Processing FileInfo ID: {fileinfo_id}')
    # import the excel
    df = pd.read_excel(file_info.file, sheet_name='Sheet1')
    # Remove every columns except these ones
    df = df[['Products','Delivery Date']]

    # Ignore this regex for now 
    # regex = r'^([0-9]\sx)|^(x\s\d)|([0-9]+x)|(x+[0-9])' <<< This does not work for now. 
    regex = r'(1 x|x 1|1x|x1|2 x|x 2|2x|x2|5 x|x 5|5x|x5|4 x|x 4|4x|x4|7 x|x 7|7x|x7|10 x|x 10|10x|x10)'
    # Create a new column with the quantity
    df['Quantity'] = df['Products'].str.extract(regex)
    # Clean the letters
    df['Quantity'] = df['Quantity'].str.replace(r'\D', '')
    # Cleant the Product Column
    df['Products'] = df['Products'].str.strip(regex)
    # Convert NaN to be 1
    df = df.fillna(1)
    # Convert String to Int
    df['Quantity'] = df['Quantity'].astype(int)

    # Pattern Tuple
    df_pattern = pd.read_excel('patterns.xlsx', sheet_name='Sheet1')
    # Remove every columns except these ones
    df_pattern = df_pattern[['Torturi LARA']]
    df_pattern[['Torturi LARA 2']] = df_pattern[['Torturi LARA']]
    pattern_tuples = list(df_pattern.to_records(index=False))


    def generalize(ser, match_name, default=None, regex=False, case=False):
        seen = None
        for match, name in match_name:
            mask = ser.str.contains(match, case=case, regex=regex)
            if seen is None:
                seen = mask
            else:
                seen |= mask
            ser = ser.where(~mask, name)
        if default:
            ser = ser.where(seen, default)
        else:
            ser = ser.where(seen, ser.values)
        return ser

    # We clean up all everything except the patterns
    df['Products'] = generalize(df['Products'], pattern_tuples)
    # We group duplicates and .sum() the quantity
    df2 = df.groupby(['Products', 'Delivery Date'])['Quantity'].sum().reset_index()

    dic_data = df2.to_dict(orient='list')

    instances_ls = []

    combined_data = {}
    for product, delivery_date, quantity in zip(dic_data['Products'], dic_data['Delivery Date'], dic_data['Quantity']):
        if not combined_data.get(product):
            combined_data[product] = {}
        if not combined_data[product].get(delivery_date):
            combined_data[product][delivery_date] = quantity
        else:
            combined_data[product][delivery_date] += quantity

    for product, product_value in combined_data.items():
        for delivery_date, quantity in product_value.items():
            data = {
                'file_info': file_info,
                'title': product,
                'delivery_date': datetime.datetime.strptime(delivery_date, '%d/%m/%Y'),
                'quantity': quantity
            }
            instances_ls.append(Data(**data))

    try:
        Data.objects.bulk_create(instances_ls)
    except Exception as e:
        print(e)

@task(name="remove_file_from_storage")
def remove_file_from_storage(folder_path):
    import shutil
    shutil.rmtree(folder_path)
    return True
