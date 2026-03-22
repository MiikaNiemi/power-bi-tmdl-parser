import re
from functions.get_indent import get_indent

# Function to parse tables   
def parse_tables(model, tables):
 
    tables_data = []

    for table in tables:

        with open(file=table, mode='r') as file:
            data = file.readlines()
        
        # Table name (with spaces in its name and without)
        if '\'' in data[0]:
            table_name = re.search('\'.*\'', data[0]).group(0).replace('\'', '')
        else:
            table_name = data[0].strip().split(' ')[1]
    
        row_dict = {
                    'model': model, 
                    'table_name': table_name
                    }

        # Check if table is calculationGroup
        if list(row.strip() for row in data if get_indent(row) == 2 and row.strip() == 'calculationGroup'):
            row_dict['source_type'] = 'calculationGroup'
        
        # Otherwise loop the Partition section
        else:
            partition_rows = list(i for i, partition in enumerate(data) if get_indent(partition) == 2 and partition.strip().split(' ')[0] == 'partition')
            row_dict['total_partitions'] = len(partition_rows)

            for i, row in enumerate(partition_rows):

                # Partition number
                row_dict['partition_no'] =  i + 1
                
                # Partition name
                # If partition name has spaces in its name
                if '\'' in data[row]:
                    row_dict['partition_name'] = re.search('\'.*\'', data[row]).group(0).replace('\'', '')
                else:
                    row_dict['partition_name'] = data[row].strip().split(' ')[1]

                row_dict['source_type'] = data[row].split('=')[1].strip()

                for c, child_row in enumerate(data[row + 1:]):
                    
                    # Partition attributes
                    if get_indent(child_row) == 3 and ':' in child_row:
                        key = child_row.split(':')[0].strip()
                        value = child_row.split(':')[1].strip()
                    
                        row_dict[key] = value

                    # Partition source
                    elif get_indent(child_row) == 3 and child_row.split('=')[0].strip() == 'source':
                        source_expression = []
                        current_source_expr_row = row + c + 1

                        # If expression has empty lines
                        if '```' in data[current_source_expr_row]:
                            source_expression.append(data[current_source_expr_row].replace('```', ''))

                            while '```' not in data[current_source_expr_row+1]:
                                # If row is not empty
                                if get_indent(data[current_source_expr_row+1]):
                                    source_expression.append(data[current_source_expr_row+1])
                                current_source_expr_row += 1
                            
                            # Add the last row
                            source_expression.append(data[current_source_expr_row+1].replace('```', ''))

                        else:
                            while get_indent(data[current_source_expr_row]) != 2:
                                source_expression.append(data[current_source_expr_row])
                                current_source_expr_row += 1

                        # Format source expression
                        # Join to a single string and replace line changes
                        source_expression = ''.join(source_expression).replace('\n', '')
                        # Take everything after =
                        source_expression = source_expression[source_expression.index('=') + 1:]
                        # Replace ```
                        source_expression = source_expression.replace('```', '').strip()
                        # Change 2 or more spaces to one
                        source_expression = re.sub('\\s+', ' ', source_expression)
                        # Assign to row dict
                        row_dict['source_expression'] = 'source = ' + source_expression

        tables_data.append(row_dict)

    return tables_data