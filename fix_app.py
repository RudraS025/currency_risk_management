#!/usr/bin/env python3
"""
Quick fix for app.py date format issue
"""

# Read the current app.py
with open('app.py', 'r') as f:
    content = f.read()

# Define the date conversion function
date_fix = '''
def parse_date_with_format_conversion(date_str):
    """Convert DD-MM-YYYY to YYYY-MM-DD if needed"""
    if '-' in date_str and len(date_str.split('-')[0]) == 2:
        day, month, year = date_str.split('-')
        return f"{year}-{month}-{day}"
    return date_str
'''

# Insert the function after imports
import_end = content.find('app = Flask(__name__)')
new_content = content[:import_end] + date_fix + '\n' + content[import_end:]

# Replace date parsing in get_suggested_contract_rate
old_parse1 = "issue_date = datetime.strptime(data.get('issue_date', '2025-03-03'), '%Y-%m-%d')"
new_parse1 = "issue_date = datetime.strptime(parse_date_with_format_conversion(data.get('issue_date', '2025-03-03')), '%Y-%m-%d')"

old_parse2 = "maturity_date = datetime.strptime(data.get('maturity_date', '2025-06-03'), '%Y-%m-%d')"
new_parse2 = "maturity_date = datetime.strptime(parse_date_with_format_conversion(data.get('maturity_date', '2025-06-03')), '%Y-%m-%d')"

new_content = new_content.replace(old_parse1, new_parse1)
new_content = new_content.replace(old_parse2, new_parse2)

# Add date validation
validation_code = '''
        # Validate dates
        if maturity_date <= issue_date:
            return jsonify({
                'success': False,
                'error': f'Maturity date must be after issue date'
            }), 400
        '''

# Insert validation after date parsing in both functions
new_content = new_content.replace(
    "business_type = data.get('business_type', 'import')",
    "business_type = data.get('business_type', 'import')" + validation_code
)

# Write the updated content
with open('app_fixed.py', 'w') as f:
    f.write(new_content)

print("✅ Created app_fixed.py with date format fixes")
print("Now replacing app.py...")

# Replace the original
import shutil
shutil.copy('app_fixed.py', 'app.py')
print("✅ Updated app.py with fixes")
