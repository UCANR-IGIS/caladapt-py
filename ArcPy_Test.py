import arcpy
tableName = "D:/users/stfeirer/Documents/ArcGIS/Projects/CalAdaptPy_Demo/CalAdaptPy_Demo.gdb/GetDataAPI"
if arcpy.Exists(tableName) == False:
    print(False)
else:
    print(True)
