import glob
import pandas as pd
import pathlib

from functions.parse_columns import parse_columns
from functions.parse_measures import parse_measures
from functions.parse_relationships import parse_relationships
from functions.parse_tables import parse_tables

# Parameters
pbi_repo_path = '.'
model_folders = glob.glob(pbi_repo_path + '/*/*.SemanticModel')

if __name__ == '__main__':

    for mf in model_folders:
        tables = glob.glob(mf + '/definition/tables/*.tmdl')
        model = mf.split('/')[-1].split('.')[0]

        # Write to csv just to provide some output
        output_path = pathlib.Path(f'./output/{model}')
        output_path.mkdir(parents=True, exist_ok=True)

        pd.DataFrame(parse_tables(model=model, tables=tables)).to_csv(output_path.joinpath('tables.csv'), index=False)
        pd.DataFrame(parse_columns(model=model, tables=tables)).to_csv(output_path.joinpath('columns.csv'), index=False)
        pd.DataFrame(parse_measures(model=model, tables=tables)).to_csv(output_path.joinpath('measures.csv'), index=False)
        pd.DataFrame(parse_relationships(model_folder=mf, model=model)).to_csv(output_path.joinpath('relationships.csv'), index=False)