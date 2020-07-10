import arcpy, requests, urllib3, shutil, pprint, tempfile, json
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

    url = 'http://api.cal-adapt.org/api/series/tasmax_year_CNRM-CM5_%s/rasters/' % (scenario)

    # Add HTTP header
    headers = {'ContentType': 'json'}
    # Make request
    response = requests.get(url, params=params, headers=headers)
    print(response)
    # It is a good idea to check there were no problems with the request.
    if response.ok:
        data = response.json()
        # Get a list of Raster Stores
        results = data['results']
        print('First Raster Store object:')
        pprint.pprint(results[0])
        print()
        print('Timeseries for the grid cell at this point:')
        # Iterate through the list and print the event and image property of each Raster Store
        for item in results:
            print('year:', item['event'], 'value:', item['image'], item['units'])

        return results

def createTable(results, workspace, tableName1):
    data = results[0]['slug'].split("_")

    dateField = "DateTime"
    ClimateField = "Value"
    ClimateDesc1 = 'ClimateDesc'
    #ClimateField = ClimateField.replace("-", "_")

    arcpy.env.workspace = workspace
    tableName = '%s/%s' % (workspace,tableName1) 
    if arcpy.Exists(tableName) == False:
        arcpy.management.CreateTable(arcpy.env.workspace, tableName1, None, '')

    lstFields = arcpy.ListFields(tableName)
    dateFieldBool = False
    ClimateFieldBool = False
    ClimateDescBool = False
    
    for field in lstFields:  
        if field.name == dateField:  
            dateFieldBool = True
        elif field.name == ClimateField:  
            ClimateFieldBool = True
        elif field.name == ClimateDesc1:  
            ClimateDescBool = True
    
    if dateFieldBool == False:
        arcpy.management.AddField(tableName1, dateField, "DATE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    if ClimateDescBool == False:
        arcpy.management.AddField(tableName1, ClimateDesc1, "TEXT", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    if ClimateFieldBool == False:
        arcpy.management.AddField(tableName1, ClimateField, "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')

    cursor = arcpy.da.InsertCursor(tableName, [dateField, ClimateDesc1, ClimateField])

    ClimateDesc = '%s_%s_%s' % (data[0],data[2],data[3])
    for item in results:
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

def createWKT(aoi):
    aoiTemp = tempfile.gettempdir() + "/wkt.shp"
    arcpy.management.Project(aoi, aoiTemp,
                             "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")

    # Enter for loop for each feature
    count2 = 0
    wkt = ''

    t = arcpy.Describe(aoiTemp)
    shpType = t.shapeType

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
                coords = coords + '(%s %s)' % (x, y)
                count1 = 1
            else:
                coords = coords + ',(%s %s)' % (x, y)
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
            for part in row[1]:
                # Step through each vertex in the feature
                for pnt in part:
                    if pnt:
                        if count1 == 0:
                            coords = coords + '%s %s' % (pnt.X, pnt.Y)
                            count1 = 1
                        else:
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
    return wkt

#data = returnData()
t = 'D:/users/stfeirer/Documents/ArcGIS/Projects/MyProject6/MyProject6.gdb/Points'
u = 'D:/users/stfeirer/Documents/ArcGIS/Projects/MyProject6/MyProject6.gdb/Polygons'
v = 'D:/users/stfeirer/Documents/ArcGIS/Projects/MyProject6/MyProject6.gdb/Polylines'
#x = "D:/users/stfeirer/Documents/ArcGIS/Projects/CalAdaptPy_Demo/CalAdaptPy_Demo.gdb/Points_2"
#y = createGeoJson(x)
#z = '{"type":"Point","coordinates":[-120.66705243402083,37.607454931529659]}'
