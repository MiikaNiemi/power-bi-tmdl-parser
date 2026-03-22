import re
from functions.get_indent import get_indent

# Function to parse columns
def parse_columns(model, tables):
	
    columns_data = []
	
    for table in tables:
	    
        with open(file=table, mode='r') as file:
            data = file.readlines()

        # Table name (with spaces in its name and without)
        if '\'' in data[0]:
            table_name = re.search('\'.*\'', data[0]).group(0).replace('\'', '')
        else:
            table_name = data[0].strip().split(' ')[1]

        column_rows = list(i for i, row in enumerate(data) if get_indent(row) == 2 and row.strip().split(' ')[0] == 'column')
        calculation_item_rows = list(i for i, row in enumerate(data) if get_indent(row) == 3 and row.strip().split(' ')[0] == 'calculationItem')

        for row in sorted(column_rows + calculation_item_rows):
            
            row_dict = {
                        'model': model, 
                        'table_name': table_name, 
                        'is_hidden': 0, 
                        'is_key': 0, 
                        'is_name_inferred': 0,
                        'is_calculation_item': 0
                        }
            
            # If = in row, we need to find out if it is in the column name
            if '=' in data[row]:
                column_name = '='.join(data[row].split('=')[:-1]).strip()
            else:
                column_name = data[row]

            # If column name has spaces in its name
            if '\'' in column_name:
                row_dict['column_name'] = re.search('\'.*\'', column_name).group(0).replace('\'', '')
            else:
                row_dict['column_name'] = column_name.strip().split(' ')[1]
            
            # If = is outside column name, column is calculated or calculation item
            if '=' in data[row].replace(column_name, ''):
                
                column_expression = []

                # If calculationItem
                if data[row].strip().split(' ')[0] == 'calculationItem':
                    row_dict['is_calculation_item'] = 1
                    
                    # Calculation item expression
                    for i in range(len(data[row:])):
                        # In case of next calculationItem or end of calculationGroup
                        if (i > 0 and data[row+i].strip().split(' ')[0] == 'calculationItem') or get_indent(data[row+i]) in (2, 4):
                            break
                        # If row is not empty
                        elif get_indent(data[row+i]):
                            column_expression.append(data[row+i].strip())
                    
                # Calculated column expression
                else:
                    current_expression_row = row
                    
                    while get_indent(data[current_expression_row]) != 3:
                        column_expression.append(data[current_expression_row].strip())
                        current_expression_row += 1

                # Format expression
                # Join to a single string and remove name
                column_expression = ''.join(column_expression).replace(column_name, '')
                # Take everything after =
                column_expression = column_expression[column_expression.index('=') + 1:]
                # Replace ``` and put space after comma
                column_expression = column_expression.replace('```', '').strip().replace(',', ', ')
                # Assign expression to row_dict
                row_dict['column_expression'] = column_expression
                                    
            for child_row in data[row+1:]:

                if get_indent(child_row) == 3:

                    if child_row.strip() == 'isHidden':
                        row_dict['is_hidden'] = 1

                    elif child_row.strip() == 'isKey':
                        row_dict['is_key'] = 1

                    elif child_row.strip() == 'isNameInferred':
                        row_dict['is_name_inferred'] = 1

                    # If key value pair
                    elif ':' in child_row.strip().split(' ')[0]:
                        # Modify the keys to db-naming convention
                        key = re.sub('([A-Z]{1})', r'_\1', child_row.split(':')[0].strip()).lower()
                        value = child_row.split(':')[1].strip()

                        if key == 'source_column' and value[0] == '"' and value[-1] == '"':
                            # Remove possible double quotes around sourceColumn
                            value = value.replace('"', '')

                            # Remove possible single quotes around sort_by_column
                        elif key == 'sort_by_column' and value[0] == '\'' and value[-1] == '\'':
                            value = value.replace('\'', '')
                        
                        row_dict[key] = value

                # Next main property
                elif get_indent(child_row) == 2:
                    break

            columns_data.append(row_dict)

    return columns_data