import os

files_to_patch = [
    'ui/dashboard.py',
    'ui/suppliers.py',
    'ui/settings.py',
    'ui/inventory.py',
    'ui/customers.py'
]

for file_path in files_to_patch:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patch dashboard table border
    content = content.replace(
        'self.low_stock_table.setStyleSheet("QTableWidget { border: 1px solid #EF4444; }")',
        'self.low_stock_table.setStyleSheet("QTableWidget { border: 1px solid rgba(239, 68, 68, 0.5); border-radius: 12px; }")'
    )
    
    # Patch red buttons
    content = content.replace(
        '.setStyleSheet("background-color: #EF4444; color: white;")',
        '.setStyleSheet("background-color: #EF4444; color: white; border-radius: 8px; border: none;")'
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Inline styles patched")
