import arcpy, requests, urllib3, shutil, pprint, tempfile, json, os, time, pandas as pd, copy, warnings, math, glob
arcpy.env.overwriteOutput = True
 
def downloadData(baseurl, outLoc, filename):
    try:
        url = '%s/%s' % (baseurl, filename)
        warnings.filterwarnings("ignore")
        r = requests.get(url, allow_redirects=True, verify = False)
        warnings.filterwarnings("default")
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

#def returnData(wkt, scenario, variable, gcm, period, stat, fileName):
def returnData(wkt, stat, fileName):
    arcpy.env.addOutputsToMap = False
    # Query parameters dict
    pagesize1 = 1000
    params = {
        'pagesize': pagesize1,
        'g': wkt,
        'stat': stat
    }
    
    url = 'https://api.cal-adapt.org/api/series/%s/rasters/' % (fileName)
    # Add HTTP header
    headers = {'ContentType': 'json'}
    
    # Make request
    warnings.filterwarnings("ignore")
    response = requests.post(url, data=params, headers=headers, verify = False)
    warnings.filterwarnings("default")
    # It is a good idea to check there were no problems with the request.
    if response.ok:
        data = response.json()
        # Get a list of Raster Stores
        results = data['results']

        pagecnt = math.ceil(data['count']/pagesize1) + 1
        if data['count'] >= pagesize1:
            for i in range(2,pagecnt,1):
                params = {
                    'pagesize': pagesize1,
                    'g': wkt,
                    'stat': stat,
                    'page': i
                }           

                warnings.filterwarnings("ignore")
                response = requests.post(url, data=params, headers=headers, verify = False)
                warnings.filterwarnings("default")
                # It is a good idea to check there were no problems with the request.
                if response.ok:
                    data = response.json()
                    # Get a list of Raster Stores
                    results = results + data['results']

        arcpy.env.addOutputsToMap = True

        return [results, data['count']]

def createTable(results, workspace, tableName1, fieldName, variable, gcm, scenario, period, stat):
    dateField = "DateTime"
    ClimateField = "Value"
    ClimateDesc1 = 'ClimateDesc'
    VariableField = 'Variable'
    GCMField = 'GCM'
    ScenarioField = 'Scenario'
    PeriodField = 'Period'
    UnitsField = 'Units'
    StatsField = 'Stats'
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
    VariableBool = False
    GCMBool = False
    ScenarioBool = False
    PeriodBool = False
    UnitsBool = False
    StatsBool = False
    if len(fieldName) > 1:
        CatFieldBool = False

    for field in lstFields:  
        if field.name == dateField:  
            dateFieldBool = True
        elif field.name == ClimateField:  
            ClimateFieldBool = True
        elif field.name == ClimateDesc1:  
            ClimateDescBool = True
        elif field.name == VariableField:  
            VariableBool = True
        elif field.name == GCMField:  
            GCMBool = True
        elif field.name == ScenarioField:  
            ScenarioBool = True
        elif field.name == PeriodField:  
            PeriodBool = True
        elif field.name == UnitsField:  
            UnitsBool = True
        elif field.name == StatsField:  
            StatsBool = True
        if len(fieldName) > 1:
            if field.name == CatField:  
                CatFieldBool = True
                
    if len(fieldName) > 1:
        if CatFieldBool == False:
            arcpy.management.AddField(tableName1, fieldName[1], fieldName[2], None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    if dateFieldBool == False:
        arcpy.management.AddField(tableName1, dateField, "DATE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    if VariableBool == False:
        arcpy.management.AddField(tableName1, VariableField, "TEXT", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    if GCMBool == False:
        arcpy.management.AddField(tableName1, GCMField, "TEXT", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    if ScenarioBool == False:
        arcpy.management.AddField(tableName1, ScenarioField, "TEXT", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    if PeriodBool == False:
        arcpy.management.AddField(tableName1, PeriodField, "TEXT", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    if StatsBool == False:
        arcpy.management.AddField(tableName1, StatsField, "TEXT", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    if ClimateDescBool == False:
        arcpy.management.AddField(tableName1, ClimateDesc1, "TEXT", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    if ClimateFieldBool == False:
        arcpy.management.AddField(tableName1, ClimateField, "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    if ClimateFieldBool == False:
        arcpy.management.AddField(tableName1, UnitsField, "TEXT", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')

    if len(fieldName) > 1:
        cursor = arcpy.da.InsertCursor(tableName,[fieldName[1], dateField, VariableField, GCMField, ScenarioField, PeriodField, StatsField, ClimateDesc1, ClimateField, UnitsField])
    else:
        cursor = arcpy.da.InsertCursor(tableName,[dateField, VariableField, GCMField, ScenarioField, PeriodField, StatsField, ClimateDesc1, ClimateField, UnitsField])

    ClimateDesc = '%s_%s_%s_%s' % (variable,period,gcm,scenario)

    if period == 'year':
        for item in results[0]:
            if len(fieldName) > 1:
                ClimateDesc2 = '%s_%s' % (ClimateDesc, fieldName[3])
                row = (fieldName[3], item['event'], variable, gcm, scenario, period, stat, ClimateDesc2, item['image'], item['units'])
            else:
                row = (item['event'], variable, gcm, scenario, period, stat, ClimateDesc, item['image'], item['units'])
            cursor.insertRow(row)
    elif period == 'day':
        dates = results[0][0]["slug"]
        i = dates.split("_")
        dates1 = pd.date_range(start='1/1/' + i[-1][:4], end='12/31/' + i[-1][-4:], freq='D')

        for num, img in enumerate(results[0][0]['image'], start=0):
            if len(fieldName) > 1:
                ClimateDesc2 = '%s_%s' % (ClimateDesc, fieldName[3])
                row = (fieldName[3], dates1[num].strftime('%Y-%m-%d'), variable, gcm, scenario, period, stat, ClimateDesc2, img, results[0][0]["units"])
            else:
                row = (dates1[num].strftime('%Y-%m-%d'), variable, gcm, scenario, period, stat, ClimateDesc, img, results[0][0]["units"])
            cursor.insertRow(row)
    elif period == '30yavg':
        for item in results[0]:
            dates = item["slug"]
            i = dates.split("_")
            j = i[-1]
            dates1 = '12-31-%s' % (j[:4])
            if len(fieldName) > 1:
                ClimateDesc2 = '%s_%s' % (ClimateDesc, fieldName[3])
                row = (fieldName[3], dates1, variable, gcm, scenario, period, stat, ClimateDesc2, item['image'], item['units'])
            else:
                row = (dates1, variable, gcm, scenario, period, stat, ClimateDesc, item['image'], item['units'])
            cursor.insertRow(row)
    else:
        for item in results[0]:
            dates = item["slug"]
            i = dates.split("_")
            j = i[-1]
            dates1 = '%s-%s-%s' % (j[5:7],j[-2:],j[:4])
            if len(fieldName) > 1:
                ClimateDesc2 = '%s_%s' % (ClimateDesc, fieldName[3])
                row = (fieldName[3], dates1, variable, gcm, scenario, period, stat, ClimateDesc2, item['image'], item['units'])
            else:
                row = (dates1, variable, gcm, scenario, period, stat, ClimateDesc, item['image'], item['units'])
            cursor.insertRow(row)
    del cursor
    return [dateField, ClimateDesc1, ClimateField, tableName1]

def createChart(dateField, ClimateDesc1, ClimateField, tableName):
    aprx = arcpy.mp.ArcGISProject("current")
    maps = aprx.listMaps()

    for map in maps:
        for table in map.listTables():
            if table.name == tableName:
                caladapt_table = table

                #map = aprx.listMaps()[0]
                #caladapt_table = map.listTables(tableName)[0]

                c = arcpy.Chart('MyChart')
                c.type = 'line'
                c.xAxis.field = dateField
                c.yAxis.field = ClimateField
                c.line.splitCategory = ClimateDesc1
                c.addToLayer(caladapt_table)

def createWKT(aoi, splitFeatures=False, fieldName=''):
    aoiTemp2 = tempfile.gettempdir() + "/wkt1.shp"
    arcpy.management.Project(aoi, aoiTemp2,
                             "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
    wkt = ''
    wktArray = []

    t = arcpy.Describe(aoiTemp2)
    shpType = t.shapeType

    aoiTemp = tempfile.gettempdir() + "/wkt.shp"
    
    ###  Need to build in simplification of poly and line
    if shpType == 'Point':
        aoiTemp = aoiTemp2
    elif shpType == 'Polygon':
        arcpy.cartography.SimplifyPolygon(aoiTemp2, aoiTemp, "POINT_REMOVE", "100 Meters", "10000 SquareMeters", "RESOLVE_ERRORS", "NO_KEEP", None)
    elif shpType == 'Polyline':
        arcpy.cartography.SimplifyLine(aoiTemp2, aoiTemp, "POINT_REMOVE", "0.1 Kilometers", "RESOLVE_ERRORS", "NO_KEEP", "CHECK", None)

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
                    coords = coords + '(%s %s)' % (x,y)
                    count1 = 1
                else:
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
        wktArray.append([wkt])
    else:
        searchFields = ["OID@","SHAPE@","SHAPE@XY",fieldName]
        for row in arcpy.da.SearchCursor(aoiTemp, searchFields):
            count2 = 0
            wkt = ''

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
            wktArray.append([wkt,fldName,fldType,row[3]])
                
    return wktArray

def getVariables(dataFile, variable="", gcm="", period="", scenario=""):
    #file_exists = os.path.exists(dataFile)
    #arcpy.AddMessage(file_exists)

    #if file_exists == False:
    #    freshResourceList(dataFile, True)
    dataFile = glob.glob(dataFile + "/**/datasets.txt" , recursive = True)[0]

    data = pd.read_csv(dataFile, sep=" ", header=None)
    data.columns = ["StringVariable"]
    data["counts"] = data.StringVariable.str.count("_")
    data1 = data[data["counts"] <= 3]
    data1 = data1['StringVariable'].str.split("_", n = 4, expand = True)
    data1.columns = ["Variable", "Period", "GCM", "Scenario"]
    data1['Variable'] = data1["Variable"].str.lower()
    data1['Period'] = data1["Period"].str.lower()
    data1['GCM'] = data1["GCM"].str.lower()
    data1['Scenario'] = data1["Scenario"].str.lower()
        
    if variable != "":
        data1 = data1[data1['Variable'] == variable]
        
    if period != "":
        data1 = data1[data1['Period'] == period]
        
    if gcm != "":
        data1 = data1[data1['GCM'] == gcm]
        
    if scenario != "":
        data1 = data1[data1['Scenario'] == scenario]
    
    uniquePeriod = data1.drop_duplicates(subset=['Period'])
    uniquePeriod = uniquePeriod['Period'].to_list()
    uniquePeriod = [i for i in uniquePeriod if i] 
    sorted(uniquePeriod)
    
    uniqueGCM = data1.drop_duplicates(subset=['GCM'])
    uniqueGCM = uniqueGCM['GCM'].to_list()
    uniqueGCM = [i for i in uniqueGCM if i]
    sorted(uniqueGCM)
    
    uniqueVariable = data1.drop_duplicates(subset=['Variable'])
    uniqueVariable = uniqueVariable['Variable'].to_list()
    uniqueVariable = [i for i in uniqueVariable if i]
    sorted(uniqueVariable)
    
    uniqueScenario = data1.drop_duplicates(subset=['Scenario'])
    uniqueScenario = uniqueScenario['Scenario'].to_list()
    uniqueScenario = [i for i in uniqueScenario if i]
    sorted(uniqueScenario)
    
    return [uniqueVariable,uniqueGCM,uniquePeriod,uniqueScenario]

def getResourceName(dataFile, variable="", gcm="", period="", scenario=""):
    dataFile = glob.glob(dataFile + "/**/datasets.txt" , recursive = True)[0]
    data = pd.read_csv(dataFile, sep=" ", header=None)
    data.columns = ["StringVariable"]
    data["counts"] = data.StringVariable.str.count("_")
    data1 = data[data["counts"] <= 3]
    data1 = data1['StringVariable'].str.split("_", n = 4, expand = True)
    data1.columns = ["Variable", "Period", "GCM", "Scenario"]
    data1['Variable'] = data1["Variable"].str.lower()
    data1['Period'] = data1["Period"].str.lower()
    data1['GCM'] = data1["GCM"].str.lower()
    data1['Scenario'] = data1["Scenario"].str.lower()
    data1 = data1.merge(data, left_index=True, right_index=True)
        
    if variable != "":
        data1 = data1[data1['Variable'] == variable]
    if period != "":
        data1 = data1[data1['Period'] == period]
    if gcm != "":
        data1 = data1[data1['GCM'] == gcm]
    if scenario != "":
        data1 = data1[data1['Scenario'] == scenario]
    
    uniqueFilename = data1.drop_duplicates(subset=['StringVariable'])
    uniqueFilename = uniqueFilename['StringVariable'].to_list()
    uniqueFilename = [i for i in uniqueFilename if i] 
    sorted(uniqueFilename)
    
    return uniqueFilename

def freshResourceList(resourceFile, create=False):
    def file_age(filepath):
        return time.time() - os.path.getmtime(filepath)

    resourceFile1 = glob.glob(resourceFile + "/**/datasets.txt" , recursive = True)
    file_exists = True
    if len(resourceFile1) == 0:
        file_exists = False

    #resourceFile = glob.glob(resourceFile + "/**/datasets.txt" , recursive = True)[0]
    #arcpy.AddMessage(resourceFile)
    #print(resourceFile)

    #file_exists = os.path.exists(resourceFile)
    #arcpy.AddMessage(file_exists)

    if file_exists == False:
        #cal.freshResourceList(resourceFile, True)
        weeks = 2
        resourceFile = '%s/datasets.txt' % (resourceFile)
    else:
        #cal.freshResourceList(resourceFile)
        resourceFile = glob.glob(resourceFile + "/**/datasets.txt" , recursive = True)[0]

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
        warnings.filterwarnings("ignore")
        response = requests.get('https://api.cal-adapt.org/api/series/', params=params, verify = False)
        warnings.filterwarnings("default")

        # It is a good idea to check there were no problems with the request.
        if response.ok:
            data = response.json()
            # Get a list of raster series from results property of data object
            results = data['results']
            
            with open(resourceFile, 'w') as outfile:
                for item in results:
                    outfile.write(item['slug'] + "\n")
