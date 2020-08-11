import arcpy, requests, urllib3, shutil, pprint, tempfile, json, os, time, pandas as pd
arcpy.env.overwriteOutput = True
 
def downloadData(baseurl, outLoc, filename):
    try:
        url = '%s/%s' % (baseurl, filename)
        r = requests.get(url, allow_redirects=True)
        filename = '%s/%s' % (outLoc, filename)

        r.status_code

        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
        return r.status_code

    except requests.exceptions.HTTPError as err:
        print(err)

def makeFileName(dataType,climateModel,climateScenario,variable,yearVar):
    if dataType == "met":
        filenameScheme = '%s_day_%s_%s_%s%s0101-%s1231.LOCA_2016-04-02.16th.CA_NV.nc' % (variable,climateModel,climateScenario,"%s",yearVar,yearVar)
        serverLocation = '%s/%s/%s/%s' % (dataType,climateModel,climateScenario,variable)
        source = ['r1i1p1_','r2i1p1_','r6i1p1_','r6i1p3_','r8i1p1_']
    elif dataType == "rel_humid":
        yearData = yearVar.split(' ')
        yearVar = yearData[0]
        if yearData[1] == 'daily':
            data = ''
        elif yearData[1] == 'monthly':
            data = '.monthly'
        elif yearData[1] == 'average_monthly':
            data ='.monthly.clim'
        filenameScheme = '%s_%s.%s.%s.%s.LOCA_2017-04-13.CA_NV%s.nc' % (dataType,variable,climateModel,climateScenario,yearVar,data)
        serverLocation = '%s/%s/%s' % (dataType,climateModel,climateScenario)
        source = ['']
    elif dataType == "solards":
        filenameScheme = 'rsds_day_%s_%s_%s%s.crop.fixcal.bc.srs.1x1.bc.srs.ds.postds_bc.nc' % (climateModel,climateScenario,"%s",yearVar)
        serverLocation = '%s/%s' % (dataType,climateModel)
        source = ['r1i1p1_','r6i1p1_']
    elif dataType == "wspeed":
        filenameScheme = '%s_day_%s_%s_%s%s.crop.bc.srs.1x1.bc.srs.ds.postds_bc.nc' % (dataType,climateModel,climateScenario,"%s",yearVar)
        serverLocation = '%s/%s' % (dataType,climateModel)
        source = ['r1i1p1_','r2i1p1_','r6i1p1_','r6i1p3_','r8i1p1_']

    return [filenameScheme,serverLocation,source]

def returnData(wkt, scenario):
    # Query parameters dict
    params = {
        'pagesize': 100,
        'g': wkt,
        'stat': 'mean'
    }

    #period = 'month'
    period = 'year'
    
    url = 'https://api.cal-adapt.org/api/series/tasmax_%s_CNRM-CM5_%s/rasters/' % (period, scenario)

    # Add HTTP header
    headers = {'ContentType': 'json'}
    
    # Make request
    #response = requests.get(url, params=params, headers=headers)
    response = requests.post(url, data=params, headers=headers)
    
    #print(response)
    # It is a good idea to check there were no problems with the request.
    if response.ok:
        data = response.json()
        # Get a list of Raster Stores
        results = data['results']
        #print('First Raster Store object:')
        #pprint.pprint(results[0])
        #print()
        #print('Timeseries for the grid cell at this point:')
        # Iterate through the list and print the event and image property of each Raster Store
        #for item in results:
            #arcpy.AddMessage(['year:', item['event'], 'value:', item['image'], item['units']])
            #print(['year:', item['event'], 'value:', item['image'], item['units']])
        return results

def createTable(results, workspace, tableName1, fieldName):
    data = results[0]['slug'].split("_")

    dateField = "DateTime"
    ClimateField = "Value"
    ClimateDesc1 = 'ClimateDesc'
    if len(fieldName) > 1:
        CatField = fieldName[1]
    arcpy.env.workspace = workspace
    tableName = '%s/%s' % (workspace,tableName1) 
    if arcpy.Exists(tableName) == False:
        arcpy.management.CreateTable(arcpy.env.workspace, tableName1, None, '')

    lstFields = arcpy.ListFields(tableName)
    dateFieldBool = False
    ClimateFieldBool = False
    ClimateDescBool = False
    if len(fieldName) > 1:
        CatFieldBool = False

    for field in lstFields:  
        if field.name == dateField:  
            dateFieldBool = True
        elif field.name == ClimateField:  
            ClimateFieldBool = True
        elif field.name == ClimateDesc1:  
            ClimateDescBool = True
        if len(fieldName) > 1:
            if field.name == CatField:  
                CatFieldBool = True
                
    if dateFieldBool == False:
        arcpy.management.AddField(tableName1, dateField, "DATE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    if ClimateDescBool == False:
        arcpy.management.AddField(tableName1, ClimateDesc1, "TEXT", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    if ClimateFieldBool == False:
        arcpy.management.AddField(tableName1, ClimateField, "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    if len(fieldName) > 1:
        if CatFieldBool == False:
            arcpy.management.AddField(tableName1, fieldName[1], fieldName[2], None, None, None, '', "NULLABLE", "NON_REQUIRED", '')

    if len(fieldName) > 1:
        cursor = arcpy.da.InsertCursor(tableName,[dateField, ClimateDesc1, ClimateField, fieldName[1]])
    else:
        cursor = arcpy.da.InsertCursor(tableName,[dateField, ClimateDesc1, ClimateField])

    ClimateDesc = '%s_%s_%s' % (data[0],data[2],data[3])
    for item in results:
        if len(fieldName) > 1:
            row = (item['event'], ClimateDesc, item['image'], fieldName[3])
        else:
            row = (item['event'], ClimateDesc, item['image'])
        #print(row)
        cursor.insertRow(row)
        
    del cursor
    return [dateField, ClimateDesc1, ClimateField, tableName1]

def createChart(dateField, ClimateDesc1, ClimateField, tableName):

    arcpy.AddMessage([dateField,ClimateDesc1,ClimateField,tableName])
    aprx = arcpy.mp.ArcGISProject("current")
    map = aprx.listMaps()[0]
    caladapt_table = map.listTables(tableName)[0]

    c = arcpy.Chart('MyChart')
    c.type = 'line'
    #c.title = 'Population by State'
    c.xAxis.field = dateField
    c.yAxis.field = ClimateField
    c.line.splitCategory = ClimateDesc1
    #c.xAxis.title = 'State'
    #c.yAxis.title = 'Total Population'
    c.addToLayer(caladapt_table)

def createGeoJson(aoi):
    geojson = tempfile.gettempdir() + '/temp.geojson'
    arcpy.conversion.FeaturesToJSON(aoi, geojson, "NOT_FORMATTED",
                                    "NO_Z_VALUES", "NO_M_VALUES", "GEOJSON", "WGS84", "USE_FIELD_NAME")
    f = open(geojson, "r")
    t = f.read()
    f.close()
    
    return t

def createWKT(aoi, splitFeatures=False, fieldName=''):
    print(tempfile.gettempdir())
    aoiTemp = tempfile.gettempdir() + "/wkt.shp"
    arcpy.management.Project(aoi, aoiTemp,
                             "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
    # Enter for loop for each feature
    #count2 = 0
    wkt = ''
    wktArray = []

    t = arcpy.Describe(aoiTemp)
    shpType = t.shapeType

    if splitFeatures==True:
        aoiTemp1 = tempfile.gettempdir() + "/wktDissolved.shp"
        fields = arcpy.ListFields(aoiTemp)
        for field in fields:
            if field.name == fieldName:
                # Print field properties
                fldName = field.name
                fldType = field.type

        if shpType == 'Point':
            fields1 = "Shape;%s" % (fieldName)
            arcpy.management.DeleteIdentical(aoiTemp, fields1, None, 0)
        else:
            arcpy.management.Dissolve(aoiTemp, aoiTemp1, fieldName, None, "MULTI_PART", "DISSOLVE_LINES")
            aoiTemp = tempfile.gettempdir() + "/wktDissolved.shp"
    else:
        fldName = ""
        fldType = ""

    if splitFeatures==False:
        count2 = 0
        if shpType == 'Point':
            wkt = wkt + 'MULTIPOINT'
        elif shpType == 'Polygon':
            wkt = wkt + 'MULTIPOLYGON'
        elif shpType == 'Polyline':
            wkt = wkt + 'MULTILINESTRING'
        
        wkt = wkt + ' ('

        if shpType == 'Point':
            count1 = 0
            for row in arcpy.da.SearchCursor(aoiTemp, ["SHAPE@XY"]):
                coords = ''
                x, y = row[0]
                if count1 == 0:
                    #coords = coords + '(%s %s)' % (round(x,4), round(y,4))
                    coords = coords + '(%s %s)' % (x,y)
                    count1 = 1
                else:
                    #coords = coords + ',(%s %s)' % (round(x,4), round(y,4))
                    coords = coords + ',(%s %s)' % (x,y)
                wkt = wkt + coords
            wkt = wkt + ")"
        else:
            for row in arcpy.da.SearchCursor(aoiTemp, ["OID@", "SHAPE@"]):
                partnum = 0
                count1 = 0
                if shpType == 'Polygon':
                    coords = '(('
                elif shpType == 'Polyline':
                    coords = '('

                # Step through each part of the feature
                #print(row[1])
                for part in row[1]:
                    # Step through each vertex in the feature
                    for pnt in part:
                        if pnt:
                            if count1 == 0:
                                #coords = coords + '%s %s' % (round(pnt.X,4), round(pnt.Y,4))
                                coords = coords + '%s %s' % (pnt.X, pnt.Y)
                                count1 = 1
                            else:
                                #coords = coords + ',%s %s' % (round(pnt.X,4), round(pnt.Y,4))
                                coords = coords + ',%s %s' % (pnt.X, pnt.Y)
                        else:
                            pass

                if count2 == 0:
                    wkt = wkt + coords
                    count2 = 1
                else:
                    wkt = wkt + "," + coords

                if shpType == 'Polygon':
                    wkt = wkt + '))'
                elif shpType == 'Polyline':
                    wkt = wkt + ')'

            wkt = wkt + ')'
        wktArray.append([wkt])
    else:
        searchFields = ["OID@","SHAPE@","SHAPE@XY",fieldName]
        arcpy.AddMessage(searchFields)
        for row in arcpy.da.SearchCursor(aoiTemp, searchFields):
            count2 = 0
            #if count1 > 0:
            wkt = ''
            #if shpType == 'Point':
            #    wkt = wkt + 'POINT'
            #elif shpType == 'Polygon':
            #    wkt = wkt + 'POLYGON'
            #elif shpType == 'Polyline':
            #    wkt = wkt + 'LINESTRING'

            if shpType == 'Point':
                wkt = wkt + 'MULTIPOINT'
            elif shpType == 'Polygon':
                wkt = wkt + 'MULTIPOLYGON'
            elif shpType == 'Polyline':
                wkt = wkt + 'MULTILINESTRING'
        
            wkt = wkt + ' ('

            if shpType == 'Point':
                coords = ''
                x, y = row[2]
                #coords = coords + '(%s %s)' % (round(x,4), round(y,4))
                coords = coords + '(%s %s)' % (x,y)
                wkt = wkt + coords
                wkt = wkt + ")"
            else:
                partnum = 0
                if shpType == 'Polygon':
                    coords = '(('
                elif shpType == 'Polyline':
                    coords = '('

                # Step through each part of the feature
                for part in row[1]:
                    count1 = 0                    
                    # Step through each vertex in the feature
                    for pnt in part:
                        if pnt:
                            if count1 == 0:
                                #coords = coords + '%s %s' % (round(pnt.X,4), round(pnt.Y,4))
                                coords = coords + '%s %s' % (pnt.X, pnt.Y)
                                count1 = 1
                            else:
                                #coords = coords + ',%s %s' % (round(pnt.X,4), round(pnt.Y,4))
                                coords = coords + ',%s %s' % (pnt.X, pnt.Y)
                        else:
                            pass

                    if count2 == 0:
                        wkt = wkt + coords
                        count2 = 1
                    else:
                        wkt = wkt + "," + coords

                    if shpType == 'Polygon':
                        wkt = wkt + '))'
                    elif shpType == 'Polyline':
                        wkt = wkt + ')'

                wkt = wkt + ')'
            #count1 = 1
            wktArray.append([wkt,fldName,fldType,row[3]])
                
    return wktArray

def getvariables(dataFile, variable="", gcm="", period="", scenario=""):
    data = pd.read_csv(dataFile, sep=" ", header=None)
    data.columns = ["StringVariable"]
    data["counts"] = data.StringVariable.str.count("_")
    data1 = data[data["counts"] <= 3]
    data1 = data1['StringVariable'].str.split("_", n = 4, expand = True)
    data1.columns = ["Variable", "Period", "GCM", "Scenario"]
        
    if variable != "":
        print(variable)
        data1 = data1[data1.Variable.str.contains(variable)]
        
    if period != "":
        print(period)
        data1 = data1[data1.Period.str.contains(period)]
        
    if gcm != "":
        print(gcm)
        data1 = data1[data1.GCM.str.contains(gcm)]
        
    if scenario != "":
        print(scenario)
        data1 = data1[data1.Scenario.str.contains(scenario)]
    
    uniquePeriod = data1.drop_duplicates(subset=['Period'])
    uniquePeriod = uniquePeriod['Period'].to_list()
    
    uniqueGCM = data1.drop_duplicates(subset=['GCM'])
    uniqueGCM = uniqueGCM['GCM'].to_list()
    
    uniqueVariable = data1.drop_duplicates(subset=['Variable'])
    uniqueVariable = uniqueVariable['Variable'].to_list()
    
    uniqueScenario = data1.drop_duplicates(subset=['Scenario'])
    uniqueScenario = uniqueScenario['Scenario'].to_list()
    
    return [uniqueVariable,uniqueGCM,uniquePeriod,uniqueScenario]

def freshResourceList(resourceFile):
    def file_age(filepath):
        return time.time() - os.path.getmtime(filepath)

    seconds = file_age(resourceFile) # 7200 seconds
    minutes = int(seconds) / 60 # 120 minutes
    hours = minutes / 60 # 2 hours
    days = hours /24
    weeks = days/7

    if weeks > 1:
        arcpy.AddMessage("Refreshing CalAdapt Resource List")
        # Query parameters dict
        params = {'name': '', 'pagesize': 100000}

        # Use params with the url.
        response = requests.get('http://api.cal-adapt.org/api/series/', params=params)

        # It is a good idea to check there were no problems with the request.
        if response.ok:
            data = response.json()
            # Get a list of raster series from results property of data object
            results = data['results']
            
            with open(resourceFile, 'w') as outfile:
                for item in results:
                    outfile.write(item['slug'] + "\n")

#data = returnData()
t = 'D:/users/stfeirer/Documents/ArcGIS/Projects/MyProject6/MyProject6.gdb/Points'
u = 'D:/users/stfeirer/Documents/ArcGIS/Projects/MyProject6/MyProject6.gdb/Polygons'
v = 'D:/users/stfeirer/Documents/ArcGIS/Projects/MyProject6/MyProject6.gdb/Polylines'
#x = "D:/users/stfeirer/Documents/ArcGIS/Projects/CalAdaptPy_Demo/CalAdaptPy_Demo.gdb/Points_2"
#y = createGeoJson(x)
#z = '{"type":"Point","coordinates":[-120.66705243402083,37.607454931529659]}'
