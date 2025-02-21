# db_tools
## general_db_converter
## Input:
### All input variables can be found under main.
### convert_db_file_path: Excel file containing the database conversion parameters
### old_db_file_path: Excel Database to be transformed
## Sheet Data
### The "Sheet Data" sheet is a summary of the conversion. Meaning only sheets present under "New DB Sheet" will be considered.
|Parameter|Description|
|---|---|
|New DB Sheet|New sheet to transform the Old sheet into. Must match convert sheets in the same file.|
|Old DB Sheet|Old sheet to be transformed.|
|Convert Flag|Whether or not to convert a sheet. If False, it will retain the Old sheet in the exported file.|
## Convert Sheets
### Convert sheets are sheets other than "Sheet Data". These sheets must be under the "New DB Sheet" column and have a corresponding "Old DB Sheet".
|Parameter|Description|
|---|---|
|New DB Cols|New column name to replace the old column name with.|
|Old DB Cols|Old column name to match the new column name with.|
|Values to Replace|Replace values of the old database column with new values. Format: Old Value1:New Value1,Old Value2:New Value2|
|Dtype|Set the data type of the New column|
|Arithmetic|Perform arithmetics on the Old column before assigning it to the New column (DIV/MUL/ADD/SUB). Only one of each arithmetic is allowed, and arithmetics are performed from left to right. Format: ADD:add_value,SUB:sub_value|
|Filter|Only include rows that contains any of these strings. Strings must be separated by a pipe symbol|
|Drop|Drop rows that contains any of these strings. Strings must be separated by a pipe symbol|
## Output:
### export_file_path: file path of the converted file.
## general_db_combiner
## Input:
### combine_db_file_path: Excel file containing the database conmbining parameters
## Combine DB Data
### The "Combine DB Data" sheet contains a summary of the databases to be combined. The order of the databases determines which is the primary database. The first database has the most priority while the last database has the least.
|Parameter|Description|
|---|---|
|DB Source|A name to identify the database.|
|DB File Path|File path of the databases.|
|Fill Flag|Whether or not to fill missing values. Usually only the first is False.|
## Sheet Data
### The "Sheet Data" sheet contains details of each of the sheets to be combined.
|Parameter|Description|
|---|---|
|Sheet|Name of the sheet, both databases must contain this sheet.|
|Unique Column|Unique column to serve as the index of the new database. In the event that both databases have the same indices, only the primary database index will be retained.|
|Combine Flag|Whether or not to combine the sheets. If False, only the primary database will be retained.|
## Output:
### export_file_path: file path of the combined file.
