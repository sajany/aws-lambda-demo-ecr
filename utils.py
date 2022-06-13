import os

# Environment variables
BUCKET_NAME = os.getenv('BUCKET_NAME')
BUCKET_REGION = os.getenv('BUCKET_REGION')
NODE_V2_URL = os.getenv('NODE_V2_URL')
ML_REST_URL = os.getenv('ML_REST_URL')
AUTH_HEADER = os.getenv('AUTH_HEADER')
OIS_BASIC_AUTH = (os.getenv('OIS_UNAME'), os.getenv('OIS_PWD'))

# Supportive constants
S3_HOME = f'https://{BUCKET_NAME}.s3.amazonaws.com/'
DEFAULT_SUPPLIER_NAME = 'N/A'
SUBSCRIBER_LOOKUP_SERVICE_TYPE = 'LOOKUP'

# Node V2 APIs
UPDATE_INVOICE_URL = f'{NODE_V2_URL}/attachment/updateInvoice'
INVOICE_LINE_ITEMS_URL = f'{NODE_V2_URL}/attachment/saveInvoiceLineItems'
FETCH_INVOICE_URL = f'{NODE_V2_URL}/attachment/getInvoiceByJobId?expenseJobId='
SAVE_INVOICE_LABEL_URL = f'{NODE_V2_URL}/attachment/saveInvoiceLabels'
GET_SUPPLIER_LIST_URL = f'{NODE_V2_URL}/attachment/getSupplierList?subscriberId='
GET_SUBSCRIBER_ERP_URL = f'{NODE_V2_URL}/attachment/getSubscriberERPDetails?subscriberId='
SAVE_LINE_ITEM_URL = f'{NODE_V2_URL}/attachment/saveInvoiceLineItems'

# Node V2 API Header
API_V2_HEADER = {
    'authorization': AUTH_HEADER,
    'Content-Type': 'application/json'
}

# ML Rest APIs
DETECT_ENTITIES_URL = f'{ML_REST_URL}/live_detect_entities/'
IDENTIFY_SUPPLIER_URL = f'{ML_REST_URL}/supplier/unseen/'

# Supportive functions
def get_http_s3_path(text_json_path):
    return f'https://{BUCKET_NAME}.s3.amazonaws.com/{text_json_path}'