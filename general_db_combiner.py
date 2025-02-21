import pandas as pd
import time as timer
import sys
from general_db_converter import export_to_excel

'''
Created by Jan Kyle Lewis T. Nolasco
'''

def import_combine_db(combine_db_file_path):
    sheet_data=pd.read_excel(combine_db_file_path, sheet_name="Sheet Data")
    combine_db_data=pd.read_excel(combine_db_file_path, sheet_name="Combine DB Data")

    combine_db_dict={}
    fill_flag_dict={}
    pass_db_dict={}
    unique_col_db_dict={}

    # check which sheets to combine and which to pass; if pass first entry in combine data will be used
    for sheet_data_index in sheet_data.index:
        curr_sheet_name=sheet_data.loc[sheet_data_index, "Sheet"]
        curr_unique_col=sheet_data.loc[sheet_data_index, "Unique Column"]
        combine_flag = sheet_data.loc[sheet_data_index, "Combine Flag"]
        #if combine_flag is true, put all db's, and fill flags into a single list and assign to combine dictionary
        if combine_flag:
            curr_sheet_list=[]
            curr_fill_flag_list=[]
            for combine_db_data_index in combine_db_data.index:
                curr_db_file_path=combine_db_data.loc[combine_db_data_index, "DB File Path"]
                curr_fill_flag=combine_db_data.loc[combine_db_data_index, "Fill Flag"]
                curr_sheet_list.append(pd.read_excel(curr_db_file_path, sheet_name=curr_sheet_name,
                                                     dtype={curr_unique_col: str}))
                curr_fill_flag_list.append(curr_fill_flag)
            combine_db_dict[curr_sheet_name]=curr_sheet_list
            fill_flag_dict[curr_sheet_name]=curr_fill_flag_list
            unique_col_db_dict[curr_sheet_name]=curr_unique_col

        elif not combine_flag:
            curr_db_file_path=combine_db_data.loc[0, "DB File Path"]
            pass_db_dict[curr_sheet_name]=pd.read_excel(curr_db_file_path, sheet_name=curr_sheet_name,
                                                     dtype={curr_unique_col: str})

    return combine_db_dict, fill_flag_dict, pass_db_dict, unique_col_db_dict

def check_cols(db_name, db_list):
    prev_col_list=[]
    for db in db_list:
        curr_col_list=list(db.columns)
        curr_col_list.sort()

        #only check for similarity if prev_col_list has a value
        if curr_col_list != prev_col_list and prev_col_list:
            print(f"Error: {db_name} columns are different.")
            sys.exit()

        else:
            prev_col_list = curr_col_list

def fill_empty(source_db, fill_db, unique_col):
    suffix="_fill_db"
    source_db = source_db.join(fill_db.set_index(unique_col), on=unique_col, rsuffix=suffix)
    drop_cols = []
    for col_rsuffix in source_db.columns:
        if col_rsuffix.endswith(suffix):
            col = col_rsuffix.replace(suffix, "")
            drop_cols.append(col_rsuffix)
            #fill missing columns from fill_db
            source_db[col] = source_db[col].fillna(source_db[col_rsuffix])

    #drop excess columns
    source_db=source_db.drop(columns=drop_cols)

    return source_db

def concat_db(combine_db_dict, fill_flag_dict, unique_col_db_dict):
    combine_db_export_dict={}

    for combine_db_key in combine_db_dict:
        print("Current Concat: ", combine_db_key)
        #check if db columns are the same
        check_cols(combine_db_key, combine_db_dict[combine_db_key])

        #get unique column
        curr_unique_col=unique_col_db_dict[combine_db_key]

        #concat all db
        temp_concat_db=pd.concat(combine_db_dict[combine_db_key])

        #drop duplicates, first in the list has priority
        temp_concat_db.drop_duplicates(subset=[curr_unique_col], inplace=True)

        #check fill flags
        fill_flag_list=fill_flag_dict[combine_db_key]
        for fill_flag_index in range(len(fill_flag_list)):
            if fill_flag_list[fill_flag_index]:
                curr_fill_db=combine_db_dict[combine_db_key][fill_flag_index]
                temp_concat_db=fill_empty(temp_concat_db.copy(deep=True), curr_fill_db.copy(deep=True), curr_unique_col)

        combine_db_export_dict[combine_db_key]=temp_concat_db

    return combine_db_export_dict

def main():
    combine_db_file_path = "RF_simple\\RF_simple_combine.xlsx"
    combine_db_dict, fill_flag_dict, pass_db_dict, unique_col_db_dict=import_combine_db(combine_db_file_path)

    combine_db_dict=concat_db(combine_db_dict, fill_flag_dict, unique_col_db_dict)

    export_file_path = "RF_simple\\RF_database_combined.xlsx"
    export_to_excel(export_file_path, combine_db_dict, pass_db_dict)

if __name__ == "__main__":
    start = timer.time()
    main()
    end = timer.time()
    total_time = (end - start) / 60
    print(f"Elapsed Time: {total_time} mins", )