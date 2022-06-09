import time
import json
import utils
import requests

# Private lambda - doesn't return http response
def handle(event, context):
    expense_job_id = event.get('expenseJobId')
    print(f'Job id from SNS event: {expense_job_id}')
    
    invoice = get_invoice(expense_job_id)
    print(f'Invoice detail found matching job id {expense_job_id}: {invoice}')

    # Recreate folder, file & document names
    s3HttpFilePath = invoice.get('filePath')
    document_name = s3HttpFilePath.replace(utils.S3_HOME, '', 1)
    file_name = document_name[document_name.rindex('/') + 1:]
    folder_name = document_name[:document_name.rindex('/')]
    
    invoice.update({
        'documentName': document_name,
        'folderName': folder_name,
        'fileName': file_name
    })
    return invoice
    
    
def get_invoice(expense_job_id):
    retry_attempt = 1
    while retry_attempt <= 3:
        get_response_http = requests.get(
            url = f'{utils.FETCH_INVOICE_URL}{expense_job_id}',
            headers = utils.API_V2_HEADER)
        print(get_response_http)
        get_invoice_response = get_response_http.json()
        get_invoice_status = get_invoice_response.get('status')

        if get_invoice_status is not None and get_invoice_status.lower() == 'error':
            time.sleep(10)
            retry_attempt += 1
            continue
        
        return get_invoice_response.get('data')
        
    raise Exception(f'No invoice record found for {expense_job_id}')
