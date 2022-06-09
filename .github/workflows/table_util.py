import difflib
from difflib import SequenceMatcher

# Find & extract line item table (Start)
def extract_line_items(result_list):
  table_list = []
  for result in result_list:
    expense_documents = result.get('ExpenseDocuments')
    for document in expense_documents:
      table_groups = extract_table_group(document)
      table_list.extend(table_groups)

  table_list = merge_tables(table_list)  
  return table_list
  
# Extract all line item groups as table groups
def extract_table_group(document):
  table_groups = []
  line_item_groups = document.get('LineItemGroups')
  for line_item_group in line_item_groups:
    table = extract_table(line_item_group)
    table_groups.append(table)

  return table_groups

# Extract line items as table
def extract_table(line_item_group):
  table = []
  line_items = line_item_group.get('LineItems')
  for line_item in line_items:
    row = extract_row(line_item)
    table.append(row)
  return table

# Extract each line item as row
def extract_row(line_item):
  row = {}
  fields = line_item.get('LineItemExpenseFields')
  for field in fields:
    label = field.get('LabelDetection', {}).get('Text')
    label = label and label.replace('\n', ' ')
    label = label or ''
    value = field.get('ValueDetection', {}).get('Text')
    row[label] = value
  return row

# Merge similar tables and group them
def merge_tables(table_list, pointer = 0):
  host_table = table_list[pointer]
  host_header = list(host_table[0].keys())
  new_table_list = [host_table]
  
  for index in range(pointer + 1, len(table_list)):
    table = table_list[index]
    header = list(table[0].keys())
    if len(header) == len(host_header) and is_similar(header, host_header):
      new_table = restructure_table(table, host_header)
      host_table.extend(new_table)
    else:
      new_table_list.append(table)

  if pointer + 2 < len(new_table_list):
    return merge_tables(new_table_list, pointer + 1)

  return new_table_list

# Restructure table by renaming the columns as the host table
def restructure_table(table, host_headers):
  new_table = []
  for row in table:
    host_row = {}
    for host_header in host_headers:
      if host_header in row:
        host_row[host_header] = row[host_header]
      else:
        headers = list(row.keys())
        matches = difflib.get_close_matches(host_header, headers, 1)
        if len(matches) == 1:
          host_row[host_header] = row[matches[0]]          
    new_table.append(host_row)
  return new_table

# Are headers of two different tables similar?
def is_similar(x_header, y_header):
  x_header = sorted(x_header)
  y_header = sorted(y_header)
  for index, header in enumerate(x_header):
    if SequenceMatcher(None, x_header[index], y_header[index]).ratio() < 0.8:
      return False
  return True  