import re
import json
import utils
import requests

def handle(event):
    detected_entities = event.get('detectedEntities')
    entity_label_map = get_entity_label_map(detected_entities)

    table_data = event.get('tableData')
    line_item_data = get_line_item_data(table_data, entity_label_map)

    filepath = event.get('filePath')
    save_line_item(filepath, line_item_data)
    

def get_entity_label_map(detected_entities):
    entity_label_map = {}
    for entity, value in detected_entities.items():
        label = value.get('label')
        entity_label_map[label] = entity
    return entity_label_map
    
def get_line_item_data(table_data, entity_label_map):
    line_item_data = []
    for row in table_data:
        record = {}
        for label, value in row.items():
            entity = entity_label_map.get(label)
            if entity is not None:
                set_entity_value(record, entity, value)
        line_item_data.append(record)
    return line_item_data

def set_entity_value(record, entity, value):
    if entity == 'unitPrice' or entity == 'extendedPrice':
        match = re.findall('[\d,]+[\.]?\d+', value)
        if len(match) > 0:
            record[entity] = float(match[0].replace(',', ''))
    else:
        record[entity] = value

def save_line_item(filepath, line_item_data):
    save_request = {
        'filepath': filepath,
        'invoiceLineItems': line_item_data
    }
    
    print(json.dumps(save_request))
    save_response_http = requests.post(
        f'{utils.SAVE_LINE_ITEM_URL}',
        headers = utils.API_V2_HEADER,
        data = json.dumps(save_request)
    )
    print(save_response_http)
    
    if save_response_http.status_code != 200:
        raise Exception('An exception occurred while saving invoice line items')
        
    print(save_response_http.content)
