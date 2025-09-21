import re
from functions.get_indent import get_indent

# Function to parse columns
def parse_columns(model, tables):
	
    columns_data = []
	
    for table in tables:
	    
        with open(file=table, mode='r') as file:
            data = file.readlines()
            column_rows = list(i for i, partition in enumerate(data) if get_indent(partition) == 2 and partition.strip().split(' ')[0] == 'column')
            
            for row in column_rows:
				
                row_dict = {'model': model, 
                            'table_name': table.split('/')[-1].replace('.tmdl', ''), 
                            'is_hidden': 0, 
                            'is_key': 0, 
                            'is_name_inferred': 0}
				
                # If column name has spaces in its name
                if '\'' in data[row]:
                    row_dict['column_name'] = re.search('\'.*\'', data[row]).group(0).replace('\'', '')
                else:
                    row_dict['column_name'] = data[row].strip().split(' ')[1]
                                        
                for child_row in data[row+1:]:
                    
                    if get_indent(child_row) == 3:
                    
                        if child_row.strip() == 'isHidden':
                            row_dict['is_hidden'] = 1
                            
                        elif child_row.strip() == 'isKey':
                            row_dict['is_key'] = 1
                            
                        elif child_row.strip() == 'isNameInferred':
                            row_dict['is_name_inferred'] = 1
                        
                        else:
                            # Modify the keys to naming convention,
                            key = re.sub('([A-Z]{1})', r'_\1', child_row.split(':')[0].strip()).lower()
                            value = child_row.split(':')[1].strip()

                            # Remove possible double quotes around sourceColumn
                            if key == 'source_column' and value[0] == '\"' and value[-1] == '\"':
                                value = value.replace('\"', '')
                            
                            # Remove possible single quotes around sort_by_column
                            elif key == 'sort_by_column' and value[0] == '\'' and value[-1] == '\'':
                                value = value.replace('\'', '')
                        
                            row_dict[key] = value
                    
                    elif not get_indent(child_row):
                        break

                columns_data.append(row_dict)

    return columns_data