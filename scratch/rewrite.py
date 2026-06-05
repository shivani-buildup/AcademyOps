import re

with open('c:\\Users\\Admin\\Desktop\\AcademyOps\\scratch\\generate_word_report.py', 'r', encoding='utf-8') as f:
    content = f.read()

# We want to replace add_styled_table calls with bullet lists except for 3 tables:
# "Objective" (Objectives)
# "Data Type" (Database Schema)
# "Work Package" (Work Package Summary)

def replacer(match):
    full_match = match.group(0)
    
    # Check if we should keep this table
    if 'Objective' in full_match or 'Data Type' in full_match or 'Work Package' in full_match or 'Project Name' in full_match:
        return full_match
        
    # Extract headers and rows
    headers_match = re.search(r'headers=\[(.*?)\]', full_match, re.DOTALL)
    rows_match = re.search(r'rows=\[(.*?)\](,\s*col_widths)?', full_match, re.DOTALL)
    
    if not headers_match or not rows_match:
        return full_match
        
    headers_str = headers_match.group(1)
    rows_str = rows_match.group(1)
    
    # Simple eval to get lists (safe enough here since we know the content)
    import ast
    try:
        headers = ast.literal_eval('[' + headers_str + ']')
        
        # Rows might have extra spaces or newlines, we need to extract each row list
        # Actually it's easier to use a dynamic regex replacement
        # Let's replace the whole block with code that adds paragraphs
        
        replacement = ""
        # We will iterate through rows. But since this is a code generator, we can just rewrite the python code to generate bullets instead of tables.
        
        # Parse the rows strings
        row_lists = re.findall(r'\[(.*?)\]', rows_str, re.DOTALL)
        
        for r_str in row_lists:
            if not r_str.strip():
                continue
            cells = [c.strip().strip("'\"") for c in r_str.split('",')]
            cells = [c.strip().strip("'\"") for c in ast.literal_eval('[' + r_str + ']')]
            
            # Format as bullet
            if len(cells) >= 2:
                bold_part = cells[0] + ": "
                rest = " | ".join(cells[1:])
                replacement += f'add_bullet(doc, "{rest}", bold_prefix="{bold_part}")\n'
            elif len(cells) == 1:
                replacement += f'add_bullet(doc, "{cells[0]}")\n'
                
        return replacement.strip()
    except Exception as e:
        print("Error parsing", e)
        return full_match

# Find all add_styled_table blocks
new_content = re.sub(r'add_styled_table\(doc,\s*headers=\[.*?\].*?\)', replacer, content, flags=re.DOTALL)

with open('c:\\Users\\Admin\\Desktop\\AcademyOps\\scratch\\generate_word_report.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
