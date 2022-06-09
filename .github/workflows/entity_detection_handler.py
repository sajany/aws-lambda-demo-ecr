import json
import boto3
import utils
import logging
import requests

# Private lambda - doesn't return http response
def handle(event):
    supplier_name = event.get('name')
    table_data_path = event.get('tableDataPath')
    
    if table_data_path is None or len(table_data_path) == 0:
        logging.error('Table data path not found')
        raise Exception('Table data path not found')

    detected_entities = None
    try:
        table_data = read_table_data(table_data_path)
        table_entities = detect_table_entities(table_data, supplier_name)
        line_item_table = detect_line_item_table(table_entities)
        
        store_table_values(line_item_table, table_data_path)
    except Exception as error:
        logging.error(str(error))
        raise Exception(error)

    return line_item_table
    
def read_table_data(table_data_path):
    # Get S3 object handle
    s3_client = boto3.client('s3', region_name = utils.BUCKET_REGION)
    table_data_s3_response = s3_client.get_object(
        Bucket = utils.BUCKET_NAME,
        Key = table_data_path
    )
    
    # Read table data from S3
    table_data_str = table_data_s3_response.get('Body').read()
    table_data = json.loads(table_data_str)
    return table_data.get('tableData')

def detect_table_entities(table_data_list, supplier_name):
    logging.info('Detecting entities from the table data..')

    table_meta_list = []
    for table_data in table_data_list:
        # Detect entities from table data with label and value
        detect_entities_request = {
            'supplierName': supplier_name,
            'datasetType': 'lineitem',
            'phraseList': list(table_data[0].keys())
        }
        print(f'Detecting entities for {detect_entities_request}')
        detected_entities_response = requests.post(
            url = utils.DETECT_ENTITIES_URL,
            data = json.dumps(detect_entities_request)
        )
        print(detected_entities_response)

        if detected_entities_response.status_code == 500:
            return {}
    
        if detected_entities_response.status_code != 200:
            raise Exception('Unable to predict invoice entities from the table')
    
        detected_entities = detected_entities_response.json()
        print(detected_entities)
        
        if is_supplier_present(supplier_name) and len(detected_entities) == 0:
            print(f'No detected entities found for the supplier {supplier_name}')
            print('Re-running with static extraction engine')
            return detect_table_entities(table_data_list, '')
        
        entity_label_dict = {}
        for entity_name, label in detected_entities.items():
            entity_label_dict[entity_name] = {
                'label': label
            }

        table_meta_list.append({
            'tableData': table_data,
            'detectedEntities': entity_label_dict
        })
    return table_meta_list

def detect_line_item_table(table_meta_list):
    max_columns = 0
    detected_line_item_table = {}
    for table_meta in table_meta_list:
        data = table_meta.get('data')
        detectedEntities = table_meta.get('detectedEntities')
        
        no_of_detected_columns = len(detectedEntities)
        if no_of_detected_columns > max_columns:
            max_columns = no_of_detected_columns
            detected_line_item_table = table_meta
            
    return detected_line_item_table

# Store form values as json in S3
def store_table_values(line_item_table, table_values_file_path):
    table_values = line_item_table.get('tableData')
    print(f'Storing table values as json in {table_values_file_path}')
    
    # Store table_values as json in S3
    s3_client = boto3.client('s3', region_name = utils.BUCKET_REGION)
    s3_client.put_object(
        Body = json.dumps(
            table_values,
            indent = 4,
            sort_keys = True
        ),
        Bucket = utils.BUCKET_NAME,
        Key = table_values_file_path
    )
    
    return table_values_file_path    
    
def is_supplier_present(supplier_name):
    if supplier_name is None or len(supplier_name) == 0 or supplier_name == utils.DEFAULT_SUPPLIER_NAME:
        return False
    return True