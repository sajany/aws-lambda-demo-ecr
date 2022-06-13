import json
import utils
import traceback

import get_invoice_handler
import table_extraction_handler
import entity_detection_handler
import save_invoice_label_handler
import save_line_item_handler

# Private lambda - doesn't return http response
# Input: {expenseJobId: '', expenseJsonPath: ''}
def handle(event, context):
    print(f'Event from caller: {event}')
    
    try:
        # Step 1 - Get invoice by expense job id
        invoice_response = get_invoice_handler.handle(event, context)
        print(invoice_response)
        
        table_extraction_event = invoice_response.copy()
        table_extraction_event.update({
            'expenseJsonPath': event.get('expenseJsonPath')
        })
    
        # Step 2 - Table data extraction
        table_values_response = table_extraction_handler.handle(table_extraction_event, context)
        print(table_values_response)
    
        extraction_event = table_extraction_event.copy()
        extraction_event.update({
            'tableDataPath': table_values_response['tableValuesFilePath']
        })
        
        # Step 3 - Detect entities based on supplier name
        supplier_name = invoice_response.get('name')
        table_meta_data = extraction_handler(extraction_event, supplier_name)
        print(table_meta_data)
    
        save_line_item_event = extraction_event.copy()
        save_line_item_event.update({
            'tableData': table_meta_data.get('tableData'),
            'detectedEntities': table_meta_data.get('detectedEntities')
        })
        
        # Step 4 - Create/Update invoice labels
        save_invoice_label_handler.handle(save_line_item_event, context)    
    
        save_line_item_handler.handle(save_line_item_event)
    except Exception as error:
        traceback.print_exc()
        print(error)

    return None
    
def extraction_handler(event, supplier_name):
    entities = {}
    if is_supplier_present(supplier_name) == False:
        print('Supplier name not found in invoice')
        supplier_name = utils.DEFAULT_SUPPLIER_NAME
        entities = static_extraction_handler(event)
    else:
        print(f'Detecting entities using Dynamic Extraction Engine for {supplier_name}')
        entities = dynamic_extraction_handler(event, supplier_name)
    return entities

# Dynamic extraction engine with supplier name must be provided
def dynamic_extraction_handler(event, supplier_name):
    event_copy = event.copy()
    event_copy['name'] = supplier_name
    detected_entities = entity_detection_handler.handle(event_copy)
    return detected_entities
    
# Static extraction engine with no supplier    
def static_extraction_handler(event):
    event_copy = event.copy()
    event_copy['name'] = ''
    detected_entities = entity_detection_handler.handle(event_copy)
    return detected_entities        
    
def is_supplier_present(supplier_name):
    if supplier_name is None or len(supplier_name) == 0 or supplier_name == utils.DEFAULT_SUPPLIER_NAME:
        return False
    return True