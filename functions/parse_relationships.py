import glob
import re
from functions.get_indent import get_indent

def parse_relationships(model_folder, model):
    
    relationships_data = []
    
    # All the models do not have relationships
    if glob.glob(model_folder + '/definition/relationships.tmdl'):
         
        with open(file=model_folder + '/definition/relationships.tmdl', mode='r') as file:
            data = file.readlines()
            header_row_numbers = list(i for i, header in enumerate(data) if get_indent(header) == 1)
            
            for row in header_row_numbers:
                
                row_dict = {'model': model}
                
                if get_indent(data[row]) == 1:
                    row_dict['relationship_name'] = data[row].strip().split(' ')[1]
                    
                    # Assign some default values
                    row_dict['from_cardinality'] = 'many'
                    row_dict['to_cardinality'] = 'one'
                    row_dict['is_active'] = 1
                    
                    for child in data[row+1:]:
                        
                        if get_indent(child) == 2:
                            
                            # Modify the keys to naming convention
                            key = re.sub('([A-Z]{1})', r'_\1', child.split(':')[0].strip()).lower()
                            value = child.split(':')[1].strip()
                            
                            if key == 'from_column':
                                from_table, from_column = value.split('.')
                                row_dict['from_table'] = from_table.replace('\'', '')
                                row_dict['from_column'] = from_column.replace('\'', '')
                            
                            elif key == 'to_column':
                                to_table, to_column = value.split('.')
                                row_dict['to_table'] = to_table.replace('\'', '')
                                row_dict['to_column'] = to_column.replace('\'', '')
                            
                            elif key == 'is_active':
                                row_dict['is_active'] = 0
                                
                            else:
                                row_dict[key] = value
                                
                        elif not get_indent(child):
                            break
                        
                        relationships_data.append(row_dict)

        return relationships_data
    
    else:
        print(f'Model {model} does not have any relationships.')