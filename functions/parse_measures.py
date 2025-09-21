import re
from functions.get_indent import get_indent

# Function to parse measures
def parse_measures(model, tables):
    
    measures_data = []
    
    for table in tables:
            
        table_name = table.split('/')[-1].replace('.tmdl', '')
        
        with open(file=table, mode='r') as file:
            data = file.readlines()
            measure_rows = list(i for i, partition in enumerate(data) if get_indent(partition) == 2 and partition.strip().split(' ')[0] == 'measure')
            
            if measure_rows:
                
                for row in measure_rows:
                    
                    row_dict = {'model': model, 'table_name': table_name, 'is_hidden': 0}
                    
                    # If measure name has spaces in its name
                    if '\'' in data[row].split('=')[0]:
                        measure_name = re.search('\'.*\'', data[row].split('=')[0]).group(0).replace('\'', '')
                    else:
                        measure_name = data[row].strip().split(' ')[1]
                        
                    # Assign measure name
                    row_dict['measure_name'] = measure_name
                    
                    # Description has to be looked backwards
                    description = []
                    current_description_row = row - 1
                    
                    while data[current_description_row].strip().startswith('///'):
                        description.insert(0, data[current_description_row].replace('///', '').strip())
                        current_description_row -= 1
                        
                        row_dict['description'] = (' ').join(description) if description else None 
                        
                    # Measure expression
                    measure_expression = []
                    current_expression_row = row
                        
                    while get_indent(data[current_expression_row]) != 3:
                        measure_expression.append(data[current_expression_row].strip())
                        current_expression_row += 1
                    
                    # There can be measures without expression
                    try:
                        # Format the measure expression
                        measure_expression = ''.join(measure_expression)[''.join(measure_expression).index('=') + 1:]
                        measure_expression = measure_expression.replace('```', '').strip()
                        # Assign the expression
                        row_dict['expression'] = measure_expression

                    except ValueError:
                        print(f'Found measure without expression in {model}, table: {table_name}, measure name: {measure_name}')
                        
                    for child_row in data[current_expression_row:]:
                        if get_indent(child_row) == 3:
                            
                            if child_row.strip() == 'isHidden':
                                row_dict['is_hidden'] = 1
                            
                            else:
                                # Modify the keys to naming convention
                                key = re.sub('([A-Z]{1})', r'_\1', child_row.split(':')[0].strip()).lower()
                                value = child_row.split(':')[1].strip()
                                row_dict[key] = value
                                
                        elif not get_indent(child_row):
                            break
    
                    measures_data.append(row_dict)

    return measures_data