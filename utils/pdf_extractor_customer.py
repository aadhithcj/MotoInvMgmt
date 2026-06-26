import os
import json
from .helpers import clean_number, clean_quantity, parse_date
from database.models import get_setting

def extract_customer_bill(file_path):
    """
    Extracts data from a flexible-format customer bill PDF or Image.
    Returns: {
        'header': {'bill_number': '', 'date': '', 'customer_name': '', 'customer_phone': '', 'total_amount': 0, 'discount': 0},
        'items': [{'part_number': '', 'part_name': '', 'quantity': 0, 'unit_price': 0, 'total': 0}, ...]
    }
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        return _extract_pdf(file_path) # We could pass PDFs to AI too if needed, but keeping this simple
    else:
        return _extract_image_ai(file_path)

def _extract_image_ai(file_path):
    api_key = get_setting('gemini_api_key', '')
    if not api_key:
        raise ValueError("Google Gemini API Key is missing. Please paste your free key in the Settings tab.")
        
    from google import genai
    from google.genai import types
    import PIL.Image
    
    client = genai.Client(api_key=api_key)
    
    prompt = """
    Analyze this customer bill/invoice/receipt.
    Extract the details into this exact JSON structure:
    {
      "header": {
        "bill_number": "string",
        "date": "string (YYYY-MM-DD)",
        "customer_name": "string",
        "customer_phone": "string",
        "total_amount": 0.0,
        "discount": 0.0
      },
      "items": [
        {
          "part_number": "string",
          "part_name": "string",
          "quantity": 0,
          "unit_price": 0.0,
          "total": 0.0
        }
      ]
    }
    Ensure all amounts are standard floats, and quantities are integers.
    """
    
    try:
        img = PIL.Image.open(file_path)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, img],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        data = json.loads(response.text)
        
        # Guarantee structure
        header = data.get('header', {})
        items = data.get('items', [])
        
        final_header = {
            'bill_number': str(header.get('bill_number') or ''),
            'date': str(header.get('date') or ''),
            'customer_name': str(header.get('customer_name') or ''),
            'customer_phone': str(header.get('customer_phone') or ''),
            'total_amount': float(header.get('total_amount') or 0.0),
            'discount': float(header.get('discount') or 0.0)
        }
        
        final_items = []
        for i in items:
            p_name = str(i.get('part_name') or '')
            p_num = str(i.get('part_number') or '')
            if not p_name and p_num: p_name = p_num
            if not p_name: continue
            
            final_items.append({
                'part_number': p_num,
                'part_name': p_name,
                'quantity': int(i.get('quantity') or 0),
                'unit_price': float(i.get('unit_price') or 0.0),
                'total': float(i.get('total') or 0.0)
            })
            
        return {'header': final_header, 'items': final_items}
        
    except Exception as e:
        raise ValueError(f"AI Extraction failed: {str(e)}")

def _extract_pdf(pdf_path):
    import pdfplumber
    import re
    # Fallback to the old logic without dynamic column mapping
    header_data = {
        'bill_number': '', 'date': '', 'customer_name': '', 
        'customer_phone': '', 'total_amount': 0.0, 'discount': 0.0
    }
    items_data = []

    column_mapping = {
        "part_number": ["part no", "part number", "code", "item code"],
        "part_name": ["description", "item", "name", "part name"],
        "quantity": ["qty", "quantity", "units"],
        "unit_price": ["price", "unit price", "rate"],
        "total": ["total", "amount", "line total"]
    }

    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()
        if text:
            header_data['date'] = parse_date(text)
            bill_match = re.search(r'(?i)(?:invoice no|bill no|receipt no)[\s:]*([A-Z0-9-]+)', text)
            if bill_match:
                header_data['bill_number'] = bill_match.group(1).strip()
            cust_match = re.search(r'(?i)(?:customer|client|name|to)[\s:]*([A-Za-z\s]+)', text)
            if cust_match:
                name_candidate = cust_match.group(1).split('\\n')[0].strip()
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

        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue
                header_row_idx = -1
                col_indices = {}
                for r_idx, row in enumerate(table):
                    if not row: continue
                    row_texts = [str(cell).lower().strip() if cell else "" for cell in row]
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
                    if match_count >= 2:
                        header_row_idx = r_idx
                        col_indices = temp_indices
                        break

                if header_row_idx != -1:
                    for r_idx in range(header_row_idx + 1, len(table)):
                        row = table[r_idx]
                        if not row or all(cell is None or str(cell).strip() == "" for cell in row):
                            continue
                        row_text_joined = " ".join([str(c).lower() for c in row if c]).lower()
                        if any(x in row_text_joined for x in ['total', 'subtotal', 'tax', 'discount']):
                            continue
                        item = {
                            'part_number': '', 'part_name': '',
                            'quantity': 0, 'unit_price': 0.0, 'total': 0.0
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
                        if item['part_number'] or item['part_name']:
                            items_data.append(item)

    return {'header': header_data, 'items': items_data}
