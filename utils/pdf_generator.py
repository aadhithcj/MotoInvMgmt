import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from database.models import get_setting

def generate_customer_invoice_pdf(bill_data, items_data, output_path):
    # Load Shop and Bank settings from database
    shop_name = get_setting('shop_name', 'Gearfield')
    shop_phone = get_setting('shop_phone', '99463 53623')
    shop_email = get_setting('shop_email', 'contact@gearfield.in')
    shop_address = get_setting('shop_address', 'Pallipadan Building, Karukutty P O\nKarayamparambu, Angamaly')
    shop_gstin = get_setting('shop_gstin', '32AAFFL4488E1ZD')
    shop_state = get_setting('shop_state', 'Kerala, Code: 32')
    shop_logo_path = get_setting('shop_logo_path', '')
    
    bank_name = get_setting('bank_name', 'State Bank of India')
    bank_ac_no = get_setting('bank_ac_no', '12345678901')
    bank_branch = get_setting('bank_branch', 'Angamaly')
    bank_ifsc = get_setting('bank_ifsc', 'SBIN0000000')

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Fonts and constants
    FONT_NORMAL = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"
    MARGIN = 40
    
    # Background / Title
    c.setFont(FONT_BOLD, 14)
    c.drawCentredString(width / 2, height - 30, "TAX INVOICE")
    
    # Outline box
    top_y = height - 50
    bottom_y = 50
    left_x = MARGIN
    right_x = width - MARGIN
    box_width = right_x - left_x
    
    c.rect(left_x, bottom_y, box_width, top_y - bottom_y)
    
    # ---------------- HEADER SECTION ----------------
    mid_x = left_x + box_width / 2
    header_bottom = top_y - 120
    c.line(left_x, header_bottom, right_x, header_bottom)
    c.line(mid_x, top_y, mid_x, header_bottom)
    
    # Seller Info (Left)
    draw_logo = False
    text_x_offset = 5
    if shop_logo_path and os.path.exists(shop_logo_path):
        draw_logo = True
        
    if draw_logo:
        try:
            c.drawImage(shop_logo_path, left_x + 5, top_y - 50, width=60, height=45, preserveAspectRatio=True, mask='auto')
            text_x_offset = 70
        except Exception as e:
            print(f"Failed to draw logo on PDF: {e}")
            
    c.setFont(FONT_BOLD, 12)
    c.drawString(left_x + text_x_offset, top_y - 15, shop_name)
    
    curr_y = top_y - 28
    addr_lines = [line.strip() for line in shop_address.split('\n') if line.strip()]
    c.setFont(FONT_NORMAL, 8)
    for line in addr_lines[:2]:
        c.drawString(left_x + text_x_offset, curr_y, line)
        curr_y -= 11
        
    contact_info = []
    if shop_phone: contact_info.append(f"Ph: {shop_phone}")
    if shop_email: contact_info.append(f"Email: {shop_email}")
    if contact_info:
        c.drawString(left_x + text_x_offset, curr_y, " / ".join(contact_info))
        curr_y -= 11
        
    if shop_state:
        c.drawString(left_x + text_x_offset, curr_y, f"State: {shop_state}")
        curr_y -= 11
        
    if shop_gstin:
        c.setFont(FONT_BOLD, 8)
        c.drawString(left_x + text_x_offset, curr_y, f"GSTIN/UIN: {shop_gstin}")
    
    # Invoice Info (Right)
    c.setFont(FONT_BOLD, 9)
    c.drawString(mid_x + 5, top_y - 15, "Invoice No.")
    c.setFont(FONT_NORMAL, 10)
    c.drawString(mid_x + 5, top_y - 28, str(bill_data.get('bill_number', '')))
    
    c.setFont(FONT_BOLD, 9)
    c.drawString(mid_x + 140, top_y - 15, "Dated")
    c.setFont(FONT_NORMAL, 10)
    c.drawString(mid_x + 140, top_y - 28, str(bill_data.get('bill_date', '')))
    
    c.line(mid_x, top_y - 35, right_x, top_y - 35)
    
    c.setFont(FONT_BOLD, 9)
    c.drawString(mid_x + 5, top_y - 45, "Mode/Terms of Payment")
    c.setFont(FONT_NORMAL, 9)
    c.drawString(mid_x + 5, top_y - 58, "Cash / UPI")
    
    c.line(mid_x, top_y - 65, right_x, top_y - 65)
    
    # ---------------- BUYER SECTION ----------------
    buyer_bottom = header_bottom - 60
    c.line(left_x, buyer_bottom, right_x, buyer_bottom)
    
    c.setFont(FONT_BOLD, 9)
    c.drawString(left_x + 5, header_bottom - 12, "Buyer (Bill to)")
    c.setFont(FONT_BOLD, 10)
    c.drawString(left_x + 5, header_bottom - 26, str(bill_data.get('customer_name', 'Cash Customer')))
    c.setFont(FONT_NORMAL, 9)
    c.drawString(left_x + 5, header_bottom - 40, f"Ph: {bill_data.get('customer_phone', '')}")
    c.drawString(left_x + 5, header_bottom - 52, f"State: {shop_state}")
    
    # ---------------- TABLE HEADER ----------------
    table_header_bottom = buyer_bottom - 20
    c.line(left_x, table_header_bottom, right_x, table_header_bottom)
    
    # Column definitions
    col_w = [25, 160, 45, 30, 45, 55, 40, 40, 75]
    cols = []
    curr_x = left_x
    for w in col_w:
        cols.append(curr_x)
        curr_x += w
    cols.append(right_x) # Last border
    
    headers = ["Sl No", "Description of Goods", "HSN/SAC", "Qty", "Rate", "Taxable Val", "CGST", "SGST", "Amount"]
    
    c.setFont(FONT_BOLD, 8)
    for i, h in enumerate(headers):
        c.drawCentredString(cols[i] + (col_w[i] / 2), buyer_bottom - 14, h)
        if i > 0:
            c.line(cols[i], buyer_bottom, cols[i], bottom_y + 120) # Draw vertical lines down to total area
            
    # ---------------- TABLE ROWS ----------------
    y = table_header_bottom - 15
    c.setFont(FONT_NORMAL, 8)
    
    total_taxable = 0
    total_cgst = 0
    total_sgst = 0
    total_amount = 0
    
    for idx, item in enumerate(items_data):
        # We will reverse-calculate GST assuming item['unit_price'] is inclusive of 18% GST
        qty = item['quantity']
        price_inc_tax = item['unit_price']
        total_inc_tax = qty * price_inc_tax
        
        # 18% GST (9% CGST, 9% SGST)
        taxable_value = total_inc_tax / 1.18
        cgst = taxable_value * 0.09
        sgst = taxable_value * 0.09
        rate = taxable_value / qty if qty else 0
        
        c.drawCentredString(cols[0] + col_w[0]/2, y, str(idx + 1))
        
        # Truncate description if too long
        desc = item.get('part_name', '')
        if len(desc) > 30: desc = desc[:28] + ".."
        c.drawString(cols[1] + 2, y, desc)
        
        # HSN/SAC dummy
        hsn = item.get('part_number', '')[:8]
        if not hsn: hsn = "8714"
        c.drawCentredString(cols[2] + col_w[2]/2, y, hsn)
        
        c.drawCentredString(cols[3] + col_w[3]/2, y, f"{qty} nos")
        c.drawRightString(cols[5] - 2, y, f"{rate:.2f}")
        c.drawRightString(cols[6] - 2, y, f"{taxable_value:.2f}")
        
        # CGST/SGST amounts
        c.drawRightString(cols[7] - 2, y, f"{cgst:.2f}")
        c.drawRightString(cols[8] - 2, y, f"{sgst:.2f}")
        
        c.drawRightString(cols[9] - 2, y, f"{total_inc_tax:.2f}")
        
        total_taxable += taxable_value
        total_cgst += cgst
        total_sgst += sgst
        total_amount += total_inc_tax
        
        y -= 15
        if y < bottom_y + 160: # Page break logic if too many items (simplified)
            break
            
    # Add Discount
    discount = float(bill_data.get('discount', 0))
    if discount > 0:
        total_amount -= discount
        c.setFont(FONT_NORMAL, 8)
        c.drawRightString(cols[8] - 2, y, "Less: Discount")
        c.drawRightString(cols[9] - 2, y, f"-{discount:.2f}")
            
    # ---------------- FOOTER SECTION ----------------
    totals_top = bottom_y + 120
    c.line(left_x, totals_top, right_x, totals_top)
    
    # Totals Row
    c.setFont(FONT_BOLD, 9)
    c.drawString(cols[2] + 5, totals_top - 12, "Total")
    c.drawCentredString(cols[3] + col_w[3]/2, totals_top - 12, str(sum([item['quantity'] for item in items_data])))
    c.drawRightString(cols[6] - 2, totals_top - 12, f"{total_taxable:.2f}")
    c.drawRightString(cols[7] - 2, totals_top - 12, f"{total_cgst:.2f}")
    c.drawRightString(cols[8] - 2, totals_top - 12, f"{total_sgst:.2f}")
    c.drawRightString(cols[9] - 2, totals_top - 12, f"{total_amount:.2f}")
    
    # Amount in words
    amount_words_top = totals_top - 20
    c.line(left_x, amount_words_top, right_x, amount_words_top)
    c.setFont(FONT_NORMAL, 8)
    c.drawString(left_x + 5, amount_words_top - 10, "Amount Chargeable (in words)")
    c.setFont(FONT_BOLD, 9)
    c.drawString(left_x + 5, amount_words_top - 22, f"INR {total_amount:.2f} Only") # Simplified words
    
    # Bank Details & Signatory
    bank_top = amount_words_top - 30
    c.line(left_x, bank_top, right_x, bank_top)
    c.line(mid_x, bank_top, mid_x, bottom_y)
    
    c.setFont(FONT_NORMAL, 8)
    c.drawString(left_x + 5, bank_top - 12, "Company's Bank Details")
    c.drawString(left_x + 5, bank_top - 24, f"Bank Name     : {bank_name}")
    c.drawString(left_x + 5, bank_top - 36, f"A/c No.          : {bank_ac_no}")
    c.drawString(left_x + 5, bank_top - 48, f"Branch & IFS : {bank_branch} & {bank_ifsc}")
    
    c.drawString(left_x + 5, bottom_y + 10, "Declaration: We declare that this invoice shows the actual price of the goods")
    
    c.setFont(FONT_BOLD, 9)
    c.drawRightString(right_x - 5, bank_top - 12, f"for {shop_name}")
    c.setFont(FONT_NORMAL, 8)
    c.drawRightString(right_x - 5, bottom_y + 10, "Authorised Signatory")
    
    c.save()
    return output_path
