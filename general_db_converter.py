import pandas as pd
import time as timer

'''
Created by Jan Kyle Lewis T. Nolasco
'''

def export_to_excel(export_file_path, export_db_dict, pass_db_dict):
    print("Exporting . . . ")
    with pd.ExcelWriter(export_file_path) as writer:
        for key in export_db_dict:
            export_db_dict[key].to_excel(writer, sheet_name=key, index=False)
        for key in pass_db_dict:
            pass_db_dict[key].to_excel(writer, sheet_name=key, index=False)

def import_convert_db(convert_db_file_path, old_db_file_path):
    sheet_data=pd.read_excel(convert_db_file_path, sheet_name="Sheet Data")

    transform_db_dict={}
    pass_db_dict={}
    match_col_db_dict={}

    #check which sheets to transform and which to pass; if pass old sheet name will be retained
    for index in sheet_data.index:
        old_db_sheet_name=sheet_data.loc[index, "Old DB Sheet"]
        new_db_sheet_name=sheet_data.loc[index, "New DB Sheet"]
        convert_flag=sheet_data.loc[index, "Convert Flag"]
        if convert_flag:
            transform_db_dict[new_db_sheet_name]=pd.read_excel(old_db_file_path, sheet_name=old_db_sheet_name)
            match_col_db_dict[new_db_sheet_name]=pd.read_excel(convert_db_file_path, sheet_name=new_db_sheet_name)

        else:
            pass_db_dict[old_db_sheet_name]=pd.read_excel(old_db_file_path, sheet_name=old_db_sheet_name)

    return transform_db_dict, pass_db_dict, match_col_db_dict

def parse_values_to_dict(values_to_dict_str):
    values_to_dict_list=values_to_dict_str.split(",")

    values_to_dict_output={}
    for values_to_dict in values_to_dict_list:
        key_value=values_to_dict.split(":")
        values_to_dict_output[key_value[0]]=key_value[1]

    return values_to_dict_output

def transform_db(transform_db_dict, match_col_db_dict):
    #convert all databases in transform_db_dict use the column matching from match_col_db
    for transform_db_key in transform_db_dict:
        print("Current Conversion: ", transform_db_key)
        curr_match_col_db=match_col_db_dict[transform_db_key]
        new_db=pd.DataFrame(columns=curr_match_col_db["New DB Cols"].to_list())
        old_db=transform_db_dict[transform_db_key]

        for index in curr_match_col_db.index:
            if not pd.isnull(curr_match_col_db.loc[index, "Old DB Cols"]):
                new_col = curr_match_col_db.loc[index, "New DB Cols"]
                old_col = curr_match_col_db.loc[index, "Old DB Cols"]
                new_db[new_col]=old_db[old_col]
                #check for values to replace
                if not pd.isnull(curr_match_col_db.loc[index, "Values to Replace"]):
                    values_to_replace_dict=parse_values_to_dict(curr_match_col_db.loc[index, "Values to Replace"])

                    #replace values
                    new_db.replace({new_col: values_to_replace_dict}, inplace=True)

                #check for specified dtype
                if not pd.isnull(curr_match_col_db.loc[index, "Dtype"]):
                    dtype=curr_match_col_db.loc[index, "Dtype"].upper()
                    #convert to specified dtype
                    if dtype=="NUM":
                        new_db[new_col] = pd.to_numeric(new_db[new_col], errors='coerce')
                    elif dtype=="STR":
                        new_db[new_col] = new_db[new_col].astype(str)

                #check for arithmetic operations
                if not pd.isnull(curr_match_col_db.loc[index, "Arithmetic"]):
                    arithmetic_dict=parse_values_to_dict(curr_match_col_db.loc[index, "Arithmetic"])
                    #perform arithmetic
                    for arithmetic in arithmetic_dict:
                        #if arithmetic is to be performed, dtype specified must be NUM
                        arithmetic=arithmetic.upper()
                        if arithmetic=="DIV":
                            new_db[new_col]=new_db[new_col]/float(arithmetic_dict[arithmetic])
                        elif arithmetic=="MUL":
                            new_db[new_col] = new_db[new_col]*float(arithmetic_dict[arithmetic])
                        elif arithmetic=="SUB":
                            new_db[new_col] = new_db[new_col]-float(arithmetic_dict[arithmetic])
                        elif arithmetic=="ADD":
                            new_db[new_col] = new_db[new_col]+float(arithmetic_dict[arithmetic])

        #perform loop again for filters
        for index in curr_match_col_db.index:
            #filter
            if not pd.isnull(curr_match_col_db.loc[index, "Filter"]):
                new_col = curr_match_col_db.loc[index, "New DB Cols"]
                text_filter = curr_match_col_db.loc[index, "Filter"]

                #filter is not case sensitive, blank values are treated as False
                new_db = new_db[new_db[new_col].str.contains(text_filter, case=False, na=False)==True]

            #drop
            if not pd.isnull(curr_match_col_db.loc[index, "Drop"]):
                new_col = curr_match_col_db.loc[index, "New DB Cols"]
                text_drop = curr_match_col_db.loc[index, "Drop"]

                #drop is not case sensitive, blank values are treated as True
                new_db = new_db[new_db[new_col].str.contains(text_drop, case=False, na=False)==False]

        #reset index
        new_db.reset_index(drop=True, inplace=True)

        transform_db_dict[transform_db_key]=new_db

    return transform_db_dict

def main():
    convert_db_file_path = "RF_simple\\RF_simple_convesion.xlsx"
    old_db_file_path = "RF_simple\\RF_database_combined.xlsx"
    export_file_path = "RF_simple\\RF_simple.xlsx"

    transform_db_dict, pass_db_dict, match_col_db_dict=import_convert_db(convert_db_file_path, old_db_file_path)

    transform_db_dict=transform_db(transform_db_dict, match_col_db_dict)

    export_to_excel(export_file_path, transform_db_dict, pass_db_dict)

if __name__ == "__main__":
    start = timer.time()
    main()
    end = timer.time()
    total_time = (end - start) / 60
    print(f"Elapsed Time: {total_time} mins", )