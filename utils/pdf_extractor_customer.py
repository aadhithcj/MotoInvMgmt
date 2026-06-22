import pdfplumber
import json
import re
from .helpers import clean_number, clean_quantity, parse_date
from database.models import get_setting

def extract_customer_bill(pdf_path):
    """
    Extracts data from a fixed-template customer bill PDF.
    Returns: {
        'header': {'bill_number': '', 'date': '', 'customer_name': '', 'customer_phone': '', 'total_amount': 0, 'discount': 0},
        'items': [{'part_number': '', 'part_name': '', 'quantity': 0, 'unit_price': 0, 'total': 0}, ...]
    }
    """
    # Load mapping from settings
    mapping_json = get_setting('customer_bill_mapping', '{}')
    try:
        column_mapping = json.loads(mapping_json)
    except:
        column_mapping = {
            "part_number": ["part no", "part number", "code", "item code"],
            "part_name": ["description", "item", "name", "part name"],
            "quantity": ["qty", "quantity", "units"],
            "unit_price": ["price", "unit price", "rate"],
            "total": ["total", "amount", "line total"]
        }

    header_data = {
        'bill_number': '', 'date': '', 'customer_name': '', 
        'customer_phone': '', 'total_amount': 0.0, 'discount': 0.0
    }
    items_data = []

    with pdfplumber.open(pdf_path) as pdf:
        # Extract Header from page 1 text
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        if text:
            header_data['date'] = parse_date(text)
            
            # Simple regex heuristic for header fields
            bill_match = re.search(r'(?i)(?:invoice no|bill no|receipt no)[\s:]*([A-Z0-9-]+)', text)
            if bill_match:
                header_data['bill_number'] = bill_match.group(1).strip()
            
            cust_match = re.search(r'(?i)(?:customer|client|name|to)[\s:]*([A-Za-z\s]+)', text)
            if cust_match:
                # Clean up to newline
                name_candidate = cust_match.group(1).split('\n')[0].strip()
                if len(name_candidate) > 2:
                    header_data['customer_name'] = name_candidate

            phone_match = re.search(r'(?i)(?:phone|mobile|contact)[\s:]*([\d\+\-\s]{10,15})', text)
            if phone_match:
                header_data['customer_phone'] = phone_match.group(1).strip()

            discount_match = re.search(r'(?i)(?:discount)[\s:]*([\d.,]+)', text)
            if discount_match:
                header_data['discount'] = clean_number(discount_match.group(1))

            total_match = re.search(r'(?i)(?:grand total|net total|total amount)[\s:]*([\d.,]+)', text)
            if total_match:
                header_data['total_amount'] = clean_number(total_match.group(1))

        # Extract Items from tables across all pages
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue

                # Find header row
                header_row_idx = -1
                col_indices = {} # Map 'part_name' -> index
                
                for r_idx, row in enumerate(table):
                    if not row: continue
                    row_texts = [str(cell).lower().strip() if cell else "" for cell in row]
                    
                    # Check if this row looks like a header
                    match_count = 0
                    temp_indices = {}
                    
                    for col_key, keywords in column_mapping.items():
                        for k in keywords:
                            for c_idx, cell_text in enumerate(row_texts):
                                if k in cell_text:
                                    temp_indices[col_key] = c_idx
                                    match_count += 1
                                    break
                            if col_key in temp_indices:
                                break
                                
                    if match_count >= 2: # Found a likely header
                        header_row_idx = r_idx
                        col_indices = temp_indices
                        break

                if header_row_idx != -1:
                    # Parse data rows
                    for r_idx in range(header_row_idx + 1, len(table)):
                        row = table[r_idx]
                        if not row or all(cell is None or str(cell).strip() == "" for cell in row):
                            continue
                            
                        # Skip subtotal/total rows at the bottom
                        row_text_joined = " ".join([str(c).lower() for c in row if c]).lower()
                        if any(x in row_text_joined for x in ['total', 'subtotal', 'tax', 'discount']):
                            continue

                        item = {
                            'part_number': '',
                            'part_name': '',
                            'quantity': 0,
                            'unit_price': 0.0,
                            'total': 0.0
                        }

                        if 'part_number' in col_indices and col_indices['part_number'] < len(row):
                            item['part_number'] = str(row[col_indices['part_number']] or '').strip()
                        if 'part_name' in col_indices and col_indices['part_name'] < len(row):
                            item['part_name'] = str(row[col_indices['part_name']] or '').strip()
                        if 'quantity' in col_indices and col_indices['quantity'] < len(row):
                            item['quantity'] = clean_quantity(row[col_indices['quantity']])
                        if 'unit_price' in col_indices and col_indices['unit_price'] < len(row):
                            item['unit_price'] = clean_number(row[col_indices['unit_price']])
                        if 'total' in col_indices and col_indices['total'] < len(row):
                            item['total'] = clean_number(row[col_indices['total']])

                        # Only add if we have some minimal data
                        if item['part_number'] or item['part_name']:
                            items_data.append(item)

    return {'header': header_data, 'items': items_data}
