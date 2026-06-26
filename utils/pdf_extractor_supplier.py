import pdfplumber
import re
import os
import json
from .helpers import clean_number, clean_quantity, parse_date
from database.models import get_setting

def extract_supplier_bill(file_path):
    """
    Extracts data from a flexible-format supplier bill PDF or Image.
    Returns: {
        'header': {'bill_number': '', 'date': '', 'supplier_name': '', 'total_amount': 0},
        'items': [{'part_number': '', 'part_name': '', 'quantity': 0, 'unit_price': 0, 'total': 0}, ...]
    }
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        return _extract_pdf(file_path)
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
    Analyze this supplier bill/invoice.
    Extract the details into this exact JSON structure:
    {
      "header": {
        "bill_number": "string",
        "date": "string (YYYY-MM-DD)",
        "supplier_name": "string",
        "total_amount": 0.0
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
        
        # Guarantee structure matches our UI
        header = data.get('header', {})
        items = data.get('items', [])
        
        final_header = {
            'bill_number': str(header.get('bill_number') or ''),
            'date': str(header.get('date') or ''),
            'supplier_name': str(header.get('supplier_name') or ''),
            'total_amount': float(header.get('total_amount') or 0.0)
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
    header_data = {
        'bill_number': '', 'date': '', 'supplier_name': '', 'total_amount': 0.0
    }
    items_data = []

    with pdfplumber.open(pdf_path) as pdf:
        all_text = ""
        all_tables = []
        
        for page in pdf.pages:
            all_text += page.extract_text() + "\n"
            page_tables = page.extract_tables()
            if page_tables:
                all_tables.extend(page_tables)

        # 1. Extract Header Fields from Raw Text
        header_data['date'] = parse_date(all_text)
        
        bill_match = re.search(r'(?i)(?:invoice no|bill no|ref no|invoice #)[\s:]*([A-Z0-9-]+)', all_text)
        if bill_match:
            header_data['bill_number'] = bill_match.group(1).strip()
            
        sup_match = re.search(r'(?i)(?:from|supplier|vendor|seller)[\s:]*([A-Za-z\s&0-9]+)', all_text)
        if sup_match:
            header_data['supplier_name'] = sup_match.group(1).split('\n')[0].strip()
        else:
            # Fallback: take the first non-empty line as supplier name
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            if lines:
                header_data['supplier_name'] = lines[0]

        total_match = re.search(r'(?i)(?:grand total|net amount|total amount)[\s:]*([\d.,]+)', all_text)
        if total_match:
            header_data['total_amount'] = clean_number(total_match.group(1))

        # 2. Score Tables to find the Items Table
        best_table = None
        best_score = -1
        best_header_idx = -1
        best_col_map = {}

        keywords = {
            'part_number': ["part no", "code", "item code", "hsn", "part number", "sn"],
            'part_name': ["description", "item", "name", "product", "particulars", "goods"],
            'quantity': ["qty", "quantity", "units", "nos", "pcs"],
            'unit_price': ["price", "rate", "unit price", "mrp", "rate/unit"],
            'total': ["total", "amount", "line total", "value"]
        }

        for table in all_tables:
            if not table or len(table) < 2:
                continue

            # Scan the first few rows looking for headers
            for r_idx in range(min(5, len(table))):
                row = table[r_idx]
                if not row: continue
                row_texts = [str(cell).lower().strip() if cell else "" for cell in row]
                
                score = 0
                col_map = {}
                
                for col_key, kw_list in keywords.items():
                    for k in kw_list:
                        for c_idx, cell_text in enumerate(row_texts):
                            if k in cell_text:
                                col_map[col_key] = c_idx
                                score += 1
                                break
                        if col_key in col_map:
                            break
                            
                if score > best_score:
                    best_score = score
                    best_table = table
                    best_header_idx = r_idx
                    best_col_map = col_map

        # 3. Parse Data Rows from Best Table
        if best_table and best_header_idx != -1 and best_score >= 2:
            for r_idx in range(best_header_idx + 1, len(best_table)):
                row = best_table[r_idx]
                if not row or all(cell is None or str(cell).strip() == "" for cell in row):
                    continue
                    
                # Skip footer rows
                row_text_joined = " ".join([str(c).lower() for c in row if c]).lower()
                if any(x in row_text_joined for x in ['total', 'subtotal', 'tax', 'discount', 'cgst', 'sgst', 'igst']):
                    continue

                item = {
                    'part_number': '',
                    'part_name': '',
                    'quantity': 0,
                    'unit_price': 0.0,
                    'total': 0.0
                }

                if 'part_number' in best_col_map and best_col_map['part_number'] < len(row):
                    item['part_number'] = str(row[best_col_map['part_number']] or '').strip()
                if 'part_name' in best_col_map and best_col_map['part_name'] < len(row):
                    item['part_name'] = str(row[best_col_map['part_name']] or '').strip()
                if 'quantity' in best_col_map and best_col_map['quantity'] < len(row):
                    item['quantity'] = clean_quantity(row[best_col_map['quantity']])
                if 'unit_price' in best_col_map and best_col_map['unit_price'] < len(row):
                    item['unit_price'] = clean_number(row[best_col_map['unit_price']])
                if 'total' in best_col_map and best_col_map['total'] < len(row):
                    item['total'] = clean_number(row[best_col_map['total']])

                # Some tables merge part name and part number. Just ensure we have a name.
                if not item['part_name'] and item['part_number']:
                    item['part_name'] = item['part_number']
                    
                # Only add if valid quantity
                if item['part_name'] and item['quantity'] > 0:
                    items_data.append(item)

    return {'header': header_data, 'items': items_data}
