import arcpy
try:
    import arcpy
    import os
    import requests 
    import urllib3, shutil
    import CalAdaptLib as cal

except ImportError:
    print('Some required Python modules are missing.')

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "CalAdapt ArcGIS Tools"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [Livneh_Data,LOCA_Data,CA_Drought_Data, Livneh_vic_Data,Loca_vic_Data,StreamFlow_Data,MC2_Data,UCLA_Data,GetDataAPI,CreateChart]

#  This function downloads NOAA data and saves the file to a
#  local folder defines by the output location (outLoc)

class Livneh_Data(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Livneh Data"
        self.description = "GRIDDED OBSERVED METEOROLOGICAL DATA"
        self.canRunInBackground = True
        self.category = "University of Colorado - Boulder"  

    def getParameterInfo(self):
        """Define parameter definitions"""
        # First parameter
        yearb = arcpy.Parameter(
            displayName="Year Between 1950-2013",
            name="start year",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        # First parameter
        yeare = arcpy.Parameter(
            displayName="Ending Year (if more than one)",
            name="end year",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        
        # Second parameter
        months = arcpy.Parameter(
            displayName="Numeric Month",
            name="months",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        months.filter.list = ['all','01','02','03','04','05','06','07','08','09','10','11','12']
        months.value = "all"

        # Third parameter
        outLoc = arcpy.Parameter(
            displayName="Output Location",
            name="outLoc",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        # Fourth parameter
        outFile = arcpy.Parameter(
            displayName="Output File",
            name="Output File",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output",
            enabled=False)
        
        params = [yearb,yeare,months,outLoc,outFile]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[0].altered:
            if int(parameters[0].valueAsText) < 1950 or int(parameters[0].valueAsText) > 2013:
                parameters[0].value = ""
        if parameters[1].altered:
            if int(parameters[1].valueAsText) < 1950 or int(parameters[1].valueAsText) > 2013:
                parameters[1].value = ""
        if parameters[0].altered or parameters[1].altered or parameters[2].altered or parameters[3].altered:
            if not parameters[1].valueAsText and not parameters[2].valueAsText == "all":
                parameters[4].value = '%s/livneh_CA_NV_15Oct2014.%s%s.nc' % (parameters[3].valueAsText, parameters[0].valueAsText, parameters[2].valueAsText)
                parameters[4].enabled = True
            else:
                parameters[4].enabled = False
                parameters[4].value = ''
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        baseurl = 'http://albers.cnr.berkeley.edu/data/noaa/livneh/CA_NV'
        #yearVar = parameters[0].valueAsText
        #monthVar = parameters[2].valueAsText
        filenameScheme = 'livneh_CA_NV_15Oct2014.%s%s.nc'
        outLoc = parameters[3].valueAsText

        if (parameters[1].valueAsText):
            year2 = int(parameters[1].valueAsText) + 1
        else:
            year2 = int(parameters[0].valueAsText) + 1
        years = range(int(parameters[0].valueAsText),year2)
        
        if (parameters[2].valueAsText == "all"):
            months = ['01','02','03','04','05','06','07','08','09','10','11','12']
        else:
            months = [parameters[2].valueAsText]

        for yearVar in years:
            for monthVar in months:
                filename = filenameScheme % (yearVar, monthVar)
                status = cal.downloadData(baseurl, outLoc, filename)
                arcpy.AddMessage([baseurl, outLoc, filename])
                #if status == 200:
                #    break
        return

#  This function downloads SCRIPPS data and saves the file to a
#  local folder defines by the output location (outLoc)
    
class LOCA_Data(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "LOCA Data"
        self.description = "LOCA Downscaled CMIP5 Climate Projections"
        self.canRunInBackground = True
        self.category = "Scripps Institution Of Oceanography"  

    def getParameterInfo(self):
        """Define parameter definitions"""
        # First parameter
        dataType = arcpy.Parameter(
            displayName="Data Type",
            name="Data Type",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        dataType.filter.list = ['met','rel_humid','solards','wspeed']
        dataType.value = 'met'

        # First parameter
        climateModel = arcpy.Parameter(
            displayName="Climate Model",
            name="Climate Model",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        climateModel.filter.list = ['ACCESS1-0','ACCESS1-3','CCSM4','CESM1-BGC','CESM1-CAM5','CMCC-CM','CMCC-CMS','CNRM-CM5','CSIRO-Mk3-6-0','CanESM2',
                                'EC-EARTH','FGOALS-g2','GFDL-CM3','GFDL-ESM2G','GFDL-ESM2M','GISS-E2-H','GISS-E2-R','HadGEM2-AO','HadGEM2-CC',
                                'HadGEM2-ES','IPSL-CM5A-LR','IPSL-CM5A-MR','MIROC-ESM','MIROC-ESM-CHEM','MIROC5','MPI-ESM-LR','MPI-ESM-MR','MRI-CGCM3',
                                'NorESM1-M','bcc-csm1-1','bcc-csm1-1-m','inmcm4']

        # First parameter
        climateScenario = arcpy.Parameter(
            displayName="Climate Scenario",
            name="Climate Scenario",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        climateScenario.filter.list = ['historical','rcp45','rcp85']

        # First parameter
        variables = arcpy.Parameter(
            displayName="variables",
            name="variables",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        variables.filter.list = ['DTR','cdd','pr','tasmax','tasmin']
                
        # First parameter
        yearb = arcpy.Parameter(
            displayName="Time Period",
            name="start year",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        # First parameter
        yeare = arcpy.Parameter(
            displayName="Ending Time Period (if more than one)",
            name="end year",
            datatype="GPString",
            parameterType="Optional",
            direction="Input",
            enabled=True)
        
        # Second parameter
        '''months = arcpy.Parameter(
            displayName="Numeric Month",
            name="months",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        months.filter.list = ['all','01','02','03','04','05','06','07','08','09','10','11','12']
        months.value = "all"
        '''

        # Third parameter
        outLoc = arcpy.Parameter(
            displayName="Output Location",
            name="outLoc",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        # Fourth parameter
        outFile = arcpy.Parameter(
            displayName="Output File",
            name="Output File",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output",
            enabled=False)
        
        params = [dataType,climateModel,climateScenario,variables,yearb,yeare,outLoc,outFile]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        if parameters[0].valueAsText == "met":
            parameters[1].filter.list = ['ACCESS1-0','ACCESS1-3','CCSM4','CESM1-BGC','CESM1-CAM5','CMCC-CM','CMCC-CMS','CNRM-CM5','CSIRO-Mk3-6-0',
            'CanESM2','EC-EARTH','FGOALS-g2','GFDL-CM3','GFDL-ESM2G','GFDL-ESM2M','GISS-E2-H','GISS-E2-R','HadGEM2-AO','HadGEM2-CC','HadGEM2-ES',
            'IPSL-CM5A-LR','IPSL-CM5A-MR','MIROC-ESM','MIROC-ESM-CHEM','MIROC5','MPI-ESM-LR','MPI-ESM-MR','MRI-CGCM3','NorESM1-M','bcc-csm1-1',
            'bcc-csm1-1-m','inmcm4']
            parameters[3].filter.list = ['DTR','cdd','pr','tasmax','tasmin']
            parameters[4].filter.list = []
            parameters[5].enabled = True
        elif parameters[0].valueAsText == "rel_humid":
            parameters[1].filter.list = ['ACCESS1-0','ACCESS1-3','CCSM4','CNRM-CM5','CanESM2','FGOALS-g2','GFDL-CM3','GFDL-ESM2G','GFDL-ESM2M',
            'GISS-E2-H','GISS-E2-R','HadGEM2-AO','HadGEM2-CC','HadGEM2-ES','IPSL-CM5A-LR','IPSL-CM5A-MR','MIROC-ESM','MIROC-ESM-CHEM','MIROC5',
            'MRI-CGCM3','NorESM1-M','bcc-csm1-1','bcc-csm1-1-m','inmcm4']
            parameters[3].filter.list = ['max','min']
            parameters[4].filter.list = ['1950-2005 daily','1950-2005 monthly','1950-2005 average_monthly','2006-2100 daily','2006-2100 monthly','2006-2100 average_monthly']
            parameters[5].enabled = False
        elif parameters[0].valueAsText == "solards":
            parameters[1].filter.list = ['ACCESS1-0','CCSM4','CMCC-CMS','CNRM-CM5','CanESM2','GFDL-CM3','HadGEM2-CC','HadGEM2-ES','MIROC5']
            parameters[3].filter.list = ['day']
            parameters[3].value = 'day'
            parameters[4].filter.list = ['19500101-20051231','20060101-21001231']
            parameters[5].enabled = False
        elif parameters[0].valueAsText == "wspeed":
            parameters[1].filter.list = ['ACCESS1-0','CMCC-CMS','CNRM-CM5','CanESM2','GFDL-CM3','HadGEM2-CC','HadGEM2-ES','MIROC5']
            parameters[3].filter.list = ['day']
            parameters[3].value = 'day'
            parameters[4].filter.list = ['19500101-20051231','20060101-20391231','20400101-20691231','20700101-21001231']
            parameters[5].enabled = False

        if parameters[2].altered and parameters[0].valueAsText == 'wspeed':
            if parameters[2].valueAsText == 'historical':
                parameters[4].filter.list = ['19500101-20051231']
                #parameters[4].value = "19500101-20051231"
            else:
                parameters[4].filter.list = ['20060101-20391231','20400101-20691231','20700101-21001231']
                #parameters[4].value = ""

        if parameters[2].altered and parameters[0].valueAsText == 'rel_humid':
            if parameters[2].valueAsText == 'historical':
                parameters[4].filter.list = ['1950-2005 daily','1950-2005 monthly','1950-2005 average_monthly']
                #parameters[4].value = "19500101-20051231"
            else:
                parameters[4].filter.list = ['2006-2100 daily','2006-2100 monthly','2006-2100 average_monthly']
                #parameters[4].value = ""

        if parameters[2].altered and parameters[0].valueAsText == 'solards':
            if parameters[2].valueAsText == 'historical':
                parameters[4].filter.list = ['19500101-20051231']
                #parameters[4].value = "19500101-20051231"
            else:
                if parameters[1].valueAsText == 'HadGEM2-ES':
                    parameters[4].filter.list = ['20060101-20991231']
                else:
                    parameters[4].filter.list = ['20060101-21001231']
                #parameters[4].value = ""
                
        if parameters[4].altered and parameters[0].valueAsText == 'met':
            if parameters[2].valueAsText == 'historical':
                if int(parameters[4].valueAsText) < 1950 or int(parameters[4].valueAsText) > 2005:
                    parameters[4].value = ""
            else:
                if int(parameters[4].valueAsText) < 2006 or int(parameters[4].valueAsText) > 2100:
                    parameters[4].value = ""           

        if parameters[5].altered and parameters[0].valueAsText == 'met':
            if parameters[2].valueAsText == 'historical':
                if int(parameters[5].valueAsText) < 1950 or int(parameters[5].valueAsText) > 2005:
                    parameters[5].value = ""
            else:
                if int(parameters[5].valueAsText) < 2006 or int(parameters[5].valueAsText) > 2100:
                    parameters[5].value = ""
                    
        '''
        if parameters[0].altered or parameters[1].altered or parameters[2].altered or parameters[3].altered:
            if not parameters[1].valueAsText and not parameters[2].valueAsText == "all":
                parameters[4].value = '%s/livneh_CA_NV_15Oct2014.%s%s.nc' % (parameters[3].valueAsText, parameters[0].valueAsText, parameters[2].valueAsText)
                parameters[4].enabled = True
            else:
                parameters[4].enabled = False
                parameters[4].value = ''
        '''
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        baseurl = 'http://albers.cnr.berkeley.edu/data/scripps/loca'
        #[dataType,climateModel,climateScenario,variables,yearb,yeare,outLoc,outFile]
        dataType = parameters[0].valueAsText
        climateModel = parameters[1].valueAsText
        climateScenario = parameters[2].valueAsText
        variable = parameters[3].valueAsText        
        outLoc = parameters[6].valueAsText

        if dataType == 'met':
            if (parameters[5].valueAsText):
                year2 = int(parameters[5].valueAsText) + 1
            else:
                year2 = int(parameters[4].valueAsText) + 1
            years = range(int(parameters[4].valueAsText),year2)

            for yearVar in years:
                names = cal.makeFileName(dataType,climateModel,climateScenario,variable,yearVar)
                for source in names[2]:
                    filename = names[0] % (source)
                    url = '%s/%s' % (baseurl, names[1])
                    status = cal.downloadData(url, outLoc, filename)
                    arcpy.AddMessage(source)
                    if status == 200:
                        break
        else:
            yearVar = parameters[4].valueAsText
            names = cal.makeFileName(dataType,climateModel,climateScenario,variable,yearVar)
            for source in names[2]:
                arcpy.AddMessage(names)
                if not source:
                    filename = names[0]
                else:
                    filename = names[0] % (source)
                url = '%s/%s' % (baseurl, names[1])
                status = cal.downloadData(url, outLoc, filename)
                arcpy.AddMessage(source)
                if status == 200:
                    break

        arcpy.AddMessage([url, outLoc, filename])
        return

class CA_Drought_Data(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "CA Drought Data"
        self.description = "California Drought data using original CMIP5 HadGEM2-ES"
        self.canRunInBackground = True
        self.category = "Scripps Institution Of Oceanography"  

    def getParameterInfo(self):
        """Define parameter definitions"""
        # First parameter
        variables = arcpy.Parameter(
            displayName="variables",
            name="variables",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        variables.filter.list = ['ET','SWE','Tair','baseflow','precip','runoff','soilMoist1','soilMoist2','soilMoist3','tasmax','tasmin']
                
        # Second parameter
        yearb = arcpy.Parameter(
            displayName="Time Period",
            name="start year",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        yearb.filter.list = ['2018-2046','2046-2074']
        
        # Third parameter
        outLoc = arcpy.Parameter(
            displayName="Output Location",
            name="outLoc",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        # Fourth parameter
        outFile = arcpy.Parameter(
            displayName="Output File",
            name="Output File",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output",
            enabled=False)
        
        params = [variables,yearb,outLoc,outFile]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        
        if parameters[0].valueAsText == "tasmin" or parameters[0].valueAsText == "tasmax":
            parameters[1].filter.list = ['2018-2047','2046-2075']
        else:
            parameters[1].filter.list = ['2018-2046','2046-2074']
            
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        baseurl = 'http://albers.cnr.berkeley.edu/data/scripps/cadrought'
        variable = parameters[0].valueAsText
        yearVar = parameters[1].valueAsText
        filenameScheme = '%s.HadGEM2-ES.rcp85.%s.drought.nc'
        outLoc = parameters[2].valueAsText

        ts = ['t']
        for t in ts:
            filename = filenameScheme % (variable, yearVar)
            status = cal.downloadData(baseurl, outLoc, filename)

            if status == 200:
                break
                
        arcpy.AddMessage(status)
        arcpy.AddMessage([baseurl, outLoc, filename])
        return

class Livneh_vic_Data(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Livneh VIC Data"
        self.description = "GRIDDED OBSERVED METEOROLOGICAL DATA"
        self.canRunInBackground = True
        self.category = "Scripps Institution Of Oceanography"  

    def getParameterInfo(self):
        """Define parameter definitions"""
        # First parameter
        variables = arcpy.Parameter(
            displayName="variables",
            name="variables",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        variables.filter.list = ['albedo','baseflow','del_SWE','ET','latent','longwave_net','pet_natveg','precip','Qair',
                                 'rainfall','relHumid','runoff','sensible','shortwave_in','shortwave_net','snow_melt','snowfall',
                                 'soilMoist1','soilMoist2','soilMoist3','sublimation_net','SWE','Tair','tot_runoff','wdew','windspeed']
                
        # Second parameter
        yearb = arcpy.Parameter(
            displayName="Time Period",
            name="start year",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        # Third parameter
        yeare = arcpy.Parameter(
            displayName="Ending Year (if more than one)",
            name="end year",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        
        # Fourth parameter
        outLoc = arcpy.Parameter(
            displayName="Output Location",
            name="outLoc",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        # Fifth parameter
        outFile = arcpy.Parameter(
            displayName="Output File",
            name="Output File",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output",
            enabled=False)
        
        params = [variables,yearb,yeare,outLoc,outFile]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        
        if parameters[1].altered:
            if int(parameters[1].valueAsText) < 1950 or int(parameters[1].valueAsText) > 2013:
                parameters[1].value = ""
        if parameters[2].altered:
            if int(parameters[2].valueAsText) < 1950 or int(parameters[2].valueAsText) > 2013:
                parameters[2].value = ""
   
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        baseurl = 'http://albers.cnr.berkeley.edu/data/scripps/livneh_vic-output'
        variable = parameters[0].valueAsText
        filenameScheme = '%s.%s.v0.nc'
        outLoc = parameters[3].valueAsText

        if (parameters[2].valueAsText):
            year2 = int(parameters[2].valueAsText) + 1
        else:
            year2 = int(parameters[1].valueAsText) + 1
        years = range(int(parameters[1].valueAsText),year2)
        
        for yearVar in years:
            filename = filenameScheme % (variable, yearVar)
            status = cal.downloadData(baseurl, outLoc, filename)
            if status == 200:
                break
            arcpy.AddMessage([baseurl, outLoc, filename])
        return
    
class Loca_vic_Data(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "LOCA VIC Data"
        self.description = "GRIDDED OBSERVED METEOROLOGICAL DATA"
        self.canRunInBackground = True
        self.category = "Scripps Institution Of Oceanography"  

    def getParameterInfo(self):
        """Define parameter definitions"""

        # First parameter
        climateModel = arcpy.Parameter(
            displayName="Climate Model",
            name="Climate Model",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        climateModel.filter.list = ['ACCESS1-0','ACCESS1-3','bcc-csm1-1','bcc-csm1-1-m','CanESM2','CCSM4','CESM1-BGC','CESM1-CAM5',
                                    'CMCC-CM','CMCC-CMS','CNRM-CM5','CSIRO-Mk3-6-0','EC-EARTH','FGOALS-g2','GFDL-CM3','GFDL-ESM2G',
                                    'GFDL-ESM2M','GISS-E2-H','GISS-E2-R','HadGEM2-AO','HadGEM2-CC','HadGEM2-ES','inmcm4','IPSL-CM5A-LR',
                                    'IPSL-CM5A-MR','MIROC5','MIROC-ESM','MIROC-ESM-CHEM','MPI-ESM-LR','MPI-ESM-MR','MRI-CGCM3','NorESM1-M']
         # Second parameter
        climateScenario = arcpy.Parameter(
            displayName="Climate Scenario",
            name="Climate Scenario",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        climateScenario.filter.list = ['historical','rcp45','rcp85']
        
        # Third parameter
        variables = arcpy.Parameter(
            displayName="variables",
            name="variables",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        variables.filter.list = ['albedo','baseflow','del_SWE','ET','latent','longwave_net','pet_natveg','precip','Qair',
                                 'rainfall','relHumid','runoff','sensible','shortwave_in','shortwave_net','snow_melt','snowfall',
                                 'soilMoist1','soilMoist2','soilMoist3','sublimation_net','SWE','Tair','tot_runoff','wdew','windspeed']
                
        # Fourth parameter
        yearb = arcpy.Parameter(
            displayName="Time Period",
            name="start year",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        # Fifth parameter
        yeare = arcpy.Parameter(
            displayName="Ending Year (if more than one)",
            name="end year",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        
        # Sixth parameter
        outLoc = arcpy.Parameter(
            displayName="Output Location",
            name="outLoc",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        # Seventh parameter
        outFile = arcpy.Parameter(
            displayName="Output File",
            name="Output File",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output",
            enabled=False)
        
        params = [climateModel,climateScenario,variables,yearb,yeare,outLoc,outFile]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        
        if parameters[1].altered:
            if parameters[1].valueAsText == 'historical':
                if int(parameters[3].valueAsText) < 1950 or int(parameters[3].valueAsText) > 2005:
                    parameters[3].value = ""
            else:
                if int(parameters[3].valueAsText) < 2006 or int(parameters[3].valueAsText) > 2100:
                    parameters[2].value = ""
            if parameters[1].valueAsText == 'historical':
                if int(parameters[4].valueAsText) < 1950 or int(parameters[4].valueAsText) > 2005:
                    parameters[4].value = ""
            else:
                if int(parameters[4].valueAsText) < 2006 or int(parameters[4].valueAsText) > 2100:
                    parameters[4].value = ""

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        baseurl = 'http://albers.cnr.berkeley.edu/data/scripps/loca_vic-output'
        model = parameters[0].valueAsText
        scenario = parameters[1].valueAsText
        variable = parameters[2].valueAsText
        filenameScheme = '%s.%s.v0.CA_NV.nc'
        outLoc = parameters[5].valueAsText

        url = '%s/%s/%s' % (baseurl,model,scenario)

        if (parameters[4].valueAsText):
            year2 = int(parameters[4].valueAsText) + 1
        else:
            year2 = int(parameters[3].valueAsText) + 1
        years = range(int(parameters[3].valueAsText),year2)
        
        for yearVar in years:
            filename = filenameScheme % (variable, yearVar)
            status = cal.downloadData(url, outLoc, filename)
            if status == 200:
                break
            arcpy.AddMessage([url, outLoc, filename])
        return

class StreamFlow_Data(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Stream Flow Data"
        self.description = "Stream Flow DATA"
        self.canRunInBackground = True
        self.category = "Scripps Institution Of Oceanography"  

    def getParameterInfo(self):
        """Define parameter definitions"""

        # First parameter
        climateModel = arcpy.Parameter(
            displayName="Climate Model",
            name="Climate Model",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        climateModel.filter.list = ['ACCESS1-0','CanESM2','CCSM4','CESM1-BGC','CMCC-CMS','CNRM-CM5','GFDL-CM3','HadGEM2-CC','HadGEM2-ES','MIROC5']

        # Second parameter
        climateScenario = arcpy.Parameter(
            displayName="Climate Scenario",
            name="Climate Scenario",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        climateScenario.filter.list = ['rcp45','rcp85']
        
        # Third parameter
        variables = arcpy.Parameter(
            displayName="variables",
            name="variables",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        variables.filter.list = ['BEARC','DPR_I','FOL_I','LK_MC','MILLE','N_HOG','N_MEL','OROVI','PRD-C','SAC_B','SMART']
        
        # Fourth parameter
        outLoc = arcpy.Parameter(
            displayName="Output Location",
            name="outLoc",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        # Fifth parameter
        outFile = arcpy.Parameter(
            displayName="Output File",
            name="Output File",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output",
            enabled=False)
        
        params = [climateModel,climateScenario,variables,outLoc,outFile]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        baseurl = 'http://albers.cnr.berkeley.edu/data/scripps/streamflow'
        model = parameters[0].valueAsText
        scenario = parameters[1].valueAsText
        variable = parameters[2].valueAsText
        filenameScheme = '%s.%s.%s.%s.monthly.BC.nc'
        outLoc = parameters[3].valueAsText

        years = ['1950-2100']
        for yearVar in years:
            arcpy.AddMessage(yearVar)
            filename = filenameScheme % (model, scenario, variable, yearVar)
            status = cal.downloadData(baseurl, outLoc, filename)
            if status == 200:
                break
            arcpy.AddMessage([baseurl, outLoc, filename])
        return

#  This function downloads MC2 data and saves the file to a
#  local folder defines by the output location (outLoc)
class MC2_Data(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "MC2 Data"
        self.description = "Unknown"
        self.canRunInBackground = True
        self.category = "MC2"  

    def getParameterInfo(self):
        """Define parameter definitions"""
        # First parameter
        Model = arcpy.Parameter(
            displayName="Model",
            name="Model",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        Model.filter.list = ['LU','PNV','PNV+FS']

        # Second parameter
        climateModel = arcpy.Parameter(
            displayName="Climate Model",
            name="Climate Model",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        climateModel.filter.list = ['CGCM3','Csiro','Miroc3']

        # Third parameter
        climateScenario = arcpy.Parameter(
            displayName="Climate Scenario",
            name="Climate Scenario",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        climateScenario.filter.list = ['A1B','A2','B1']
        
        # Fourth parameter
        variables = arcpy.Parameter(
            displayName="variables",
            name="variables",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        variables.filter.list = ['C_ECOSYS','C_SOIL_AND_LITTER','C_VEG','CONSUMED','NBP','VTYPE']
        
        # Fifth parameter
        outLoc = arcpy.Parameter(
            displayName="Output Location",
            name="outLoc",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        # Sixth parameter
        outFile = arcpy.Parameter(
            displayName="Output File",
            name="Output File",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output",
            enabled=False)
        
        params = [Model,climateModel,climateScenario,variables,outLoc,outFile]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        baseurl = 'http://albers.cnr.berkeley.edu/data/MC2'
        model = parameters[0].valueAsText
        climateModel = parameters[1].valueAsText
        climateScenario = parameters[2].valueAsText
        variable = parameters[3].valueAsText
        filenameScheme = '%s.nc'
        outLoc = parameters[4].valueAsText
        url = '%s/%s/%s/%s' % (baseurl,model,climateScenario,climateModel)

        filename = filenameScheme % (variable)
        
        ts = ['t']
        for t in ts:
            status = cal.downloadData(url, outLoc, filename)
            if status == 200:
                break
            arcpy.AddMessage([baseurl, outLoc, filename])

        return

#  This function downloads UCLA data and saves the file to a
#  local folder defines by the output location (outLoc)
class UCLA_Data(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Unknown Data"
        self.description = ""
        self.canRunInBackground = True
        self.category = "University of California - Los Angeles"  

    def getParameterInfo(self):
        """Define parameter definitions"""
        # First parameter
        climateModel = arcpy.Parameter(
            displayName="Climate Model",
            name="Climate Model",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        climateModel.filter.list = ['invariant','CNRM-CM5','GFDL-CM3','inmcm4','IPSL-CM5A-LR','MPI-ESM-LR']
        #climateModel.value = ""

        # Second parameter
        climateScenario = arcpy.Parameter(
            displayName="Climate Scenario",
            name="Climate Scenario",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        climateScenario.filter.list = ['Historic','Future']

        # First parameter
        yearb = arcpy.Parameter(
            displayName="Year Between 1991-2000 or 2091-2100",
            name="start year",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        # First parameter
        yeare = arcpy.Parameter(
            displayName="Ending Year (if more than one)",
            name="end year",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        
        # Second parameter
        months = arcpy.Parameter(
            displayName="Numeric Month",
            name="months",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        months.filter.list = ['all','01','02','03','04','05','06','07','08','09','10','11','12']
        months.value = "all"

        # Third parameter
        outLoc = arcpy.Parameter(
            displayName="Output Location",
            name="outLoc",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        # Fourth parameter
        outFile = arcpy.Parameter(
            displayName="Output File",
            name="Output File",
            datatype="DEFile",
            parameterType="Derived",
            direction="Output",
            enabled=False)
        
        params = [climateModel,climateScenario,yearb,yeare,months,outLoc,outFile]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        
        '''
        if parameters[1].altered or parameters[2].altered or parameters[3].altered:
            if parameters[1].value == "Future":
                arcpy.AddMessage(parameters[2].valueAsText)
                if int(parameters[2].valueAsText) < 2091 or int(parameters[2].valueAsText) > 2100:
                    parameters[2].value = ''
                if int(parameters[3].valueAsText) < 2091 or int(parameters[3].valueAsText) > 2100:
                    parameters[3].value = ''
            else:
                if int(parameters[2].valueAsText) < 1991 or int(parameters[2].valueAsText) > 2000:
                    parameters[2].value = ''
                if int(parameters[3].valueAsText) < 1991 or int(parameters[3].valueAsText) > 2000:
                    parameters[3].value = ''
        '''
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        #parameters[3].clearMessage()

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        #params = [climateModel,climateScenario,yearb,yeare,months,outLoc,outFile]
        baseurl = 'http://albers.cnr.berkeley.edu/data/ucla'
        climateModel = parameters[0].valueAsText
        climateScenario = parameters[1].valueAsText

        if not parameters[2].valueAsText:
            yearb = parameters[2].valueAsText
        else:
            yearb = parameters[2].valueAsText
        if not parameters[3].valueAsText:
            yeare = "None"
        else:
            yeare = parameters[3].valueAsText
        arcpy.AddMessage(yearb)
        arcpy.AddMessage(yeare)

        #filenameScheme = 'wrfpost_.%s%s.nc'
        outLoc = parameters[5].valueAsText

        if (parameters[3].valueAsText):
            year2 = int(parameters[3].valueAsText) + 1
        else:
            year2 = int(parameters[2].valueAsText) + 1
        years = range(int(parameters[2].valueAsText),year2)
        
        if (parameters[4].valueAsText == "all"):
            months = ['01','02','03','04','05','06','07','08','09','10','11','12']
        else:
            months = [parameters[2].valueAsText]

        for yearVar in years:
            for monthVar in months:
                if climateModel == 'invariant':
                    filename = 'invariant_d02.nc'
                elif climateScenario == 'Future':
                    filename = 'wrfpost_%s_d02_%s%s.nc' % (climateModel,yearVar,monthVar)
                else:
                    filename = 'wrfpost_d02_%s%s.nc' % (yearVar,monthVar)
                #filename = filenameScheme % (yearVar, monthVar)
                status = cal.downloadData(baseurl, outLoc, filename)
                arcpy.AddMessage([baseurl, outLoc, filename])
                if status == 200:
                    break
        return
#  This function queries the CalAdapy API and shows the data in the tool window
class GetDataAPI(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Get Data from API"
        self.description = ""
        self.canRunInBackground = True
        self.category = "CalAdapt - API"  

    def getParameterInfo(self):
        in_feature_set = arcpy.Parameter(
            displayName="Input Feature Set",
            name="in_feature_set",
            datatype="GPFeatureRecordSetLayer",
            parameterType="Required",
            direction="Input")
        individual_features = arcpy.Parameter(
            displayName="Process Features Individually",
            name="individual_features",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")
        catField = arcpy.Parameter(
            displayName="Category Field",
            name="catField",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        historical = arcpy.Parameter(
            displayName="Include Historical",
            name="historical",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        rcp45 = arcpy.Parameter(
            displayName="Include RCP 4.5",
            name="rcp45",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        rcp85 = arcpy.Parameter(
            displayName="Include RCP 8.5",
            name="rcp85",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        outTable = arcpy.Parameter(
            displayName="Output Table",
            name="outTable",
            datatype="DETable",
            parameterType="Required",
            direction="Output")

        
        libPath = os.path.dirname(cal.__file__)
        resourceFile = ('%s/%s') %  (libPath, 'datasets.txt')
        cal.freshResourceList(resourceFile)
        rl = cal.getvariables(resourceFile, variable="", gcm="", scenario="", period="")

        variable = arcpy.Parameter(
            displayName="Variable",
            name="Variable",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        variable.filter.list = rl[0]
        variable.value = ""

        gcm = arcpy.Parameter(
            displayName="GCM",
            name="GCM",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        gcm.filter.list = rl[1]
        gcm.value = ""

        period = arcpy.Parameter(
            displayName="Period",
            name="Period",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        period.filter.list = rl[2]
        period.value = ""

        vic = arcpy.Parameter(
            displayName="Include VIC",
            name="vic",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")

        #period = arcpy.Parameter(
        #    displayName="Period",
        #    name="Period",
        #    datatype="GPString",
        #    parameterType="Required",
        #    direction="Input")
        #period.filter.list = rl[3]

        catField.enabled = False
        historical.value = False
        rcp45.value = False
        rcp85.value = False
        vic.value = False

        # Use __file__ attribute to find the .lyr file (assuming the
        #  .pyt and .lyr files exist in the same folder)
        #param0.value = os.path.join(os.path.dirname(__file__), "Fire_Station.lyr")
        
        params = [in_feature_set,individual_features,catField,historical,rcp45,rcp85, outTable, variable, gcm, period, vic]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        
        if parameters[7].valueAsText:
            variable1 = parameters[7].valueAsText
        else:
            variable1 = ""

        if parameters[8].valueAsText:
            gcm1 = parameters[8].valueAsText
        else:
            gcm1 = ""

        if parameters[9].valueAsText:
            period1 = parameters[9].valueAsText
        else:
            period1 = ""

        libPath = os.path.dirname(cal.__file__)
        resourceFile = ('%s/%s') %  (libPath, 'datasets.txt')
        cal.freshResourceList(resourceFile)
        rl = cal.getvariables(resourceFile, variable=variable1, gcm=gcm1, scenario="", period=period1)

        if parameters[0].altered:
            # If the field is not in the new feature class
            # then switch to the first field
            try:
                li = []
                m = arcpy.ListFields(parameters[0].valueAsText)
                for i in m:
                    print(i.name)
                    li.append(i.name)
                parameters[2].filter.list = li
                
            except:
                # Could not read the field list
                parameters[2].value = ""

        if parameters[1].altered:
            try:
                if parameters[1].valueAsText == 'true':
                    parameters[2].enabled = True
                else:
                    parameters[2].enabled = False
                
            except:
                # Could not read the field list
                #parameters[2].value = ""
                pass
        
        #incorporate dropdowns and function
        #if parameters[7].altered:
        parameters[8].filter.list = rl[1]
        if not parameters[8].valueAsText in rl[1]:
            parameters[8].value = ""
        parameters[9].filter.list = rl[2]
        if not parameters[9].valueAsText in rl[2]:
            parameters[9].value = ""
        #if parameters[8].altered:
        parameters[7].filter.list = rl[0]
        if not parameters[7].valueAsText in rl[0]:
            parameters[7].value = ""

        if "rcp45" in rl[3]:
            parameters[4].enabled = True
        else:
            parameters[4].enabled = False
            parameters[4].value = False

        if "rcp85" in rl[3]:
            parameters[5].enabled = True
        else:
            parameters[5].enabled = False
            parameters[5].value = False

        if "historical" in rl[3]:
            parameters[3].enabled = True
        else:
            parameters[3].enabled = False
            parameters[3].value = False

        if "vic" in rl[3]:
            parameters[10].enabled = True
        else:
            parameters[10].enabled = False
            parameters[10].value = False
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        #parameters[3].clearMessage()

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        features = parameters[0].valueAsText
        splitfeatures = parameters[1].valueAsText
        catField = parameters[2].valueAsText
        hist = parameters[3].valueAsText
        rcp45 = parameters[4].valueAsText
        rcp85 = parameters[5].valueAsText
        outTable = parameters[6].valueAsText

        #arcpy.AddMessage(outTable)
        zz = outTable.split('\\')
        workspace = "/".join(zz[:-1])
        tableName = zz[-1]
        #arcpy.AddMessage(outTable1)

        scenarios = []
        if hist == 'true':
            scenarios.append('historical')
        if rcp45 == 'true':
            scenarios.append('rcp45')
        if rcp85 == 'true':
            scenarios.append('rcp85')
        if splitfeatures == 'true':
            splitfeatures = True
        else:
            splitfeatures = False
            
        #arcpy.AddMessage(scenarios)

        if splitfeatures == False:
            aoiArray = cal.createWKT(features, splitfeatures)
        else:
            aoiArray = cal.createWKT(features, splitfeatures, catField)
            
        for aoi in aoiArray:
            aoiTemp = aoi[0]
            for scenario in scenarios:
                arcpy.AddMessage(aoi)
                arcpy.AddMessage(scenario)
                #arcpy.AddMessage(aoiTemp)
                results = cal.returnData(aoiTemp,scenario)
                g = cal.createTable(results,workspace,tableName,aoi)
                #g = cal.createTable(outTable)
            if (splitfeatures == True):
                arcpy.AddMessage(aoi[3])
            #arcpy.AddMessage(g)

        #aprx = arcpy.mp.ArcGISProject("current")
        #map = aprx.listMaps()[0]
        #table1 = "%s/%s" % ('D:/users/stfeirer/Documents/ArcGIS/Projects/CalAdaptPy_Demo/CalAdaptPy_Demo.gdb','caladapt_data')
        #arcpy.AddMessage(table1)
        #addTab = arcpy.mp.Table(table1)
        #lyrTest = 'D:/users/stfeirer/Documents/ArcGIS/Projects/CalAdaptPy_Demo/CalAdaptPy_Demo.gdb/caladapt_data'
        #arcpy.MakeTableView_management(table1, "caladapt_data")
        
        #cal.createChart(g[0],g[1],g[2],g[3])
            #arcpy.AddMessage(msg)

        return
#  This function queries the CalAdapy API and shows the data in the tool window
class CreateChart(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Chart Data from API"
        self.description = ""
        self.canRunInBackground = True
        self.category = "CalAdapt - API"  

    def getParameterInfo(self):

        inTable = arcpy.Parameter(
            displayName="Output Table",
            name="outTable",
            #datatype="DETable",
            datatype="GPTableView",
            parameterType="Required",
            direction="Input")

        dateField = arcpy.Parameter(
            displayName="Date Field",
            name="dateField",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        catField = arcpy.Parameter(
            displayName="Category Field",
            name="catField",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        valueField = arcpy.Parameter(
            displayName="Value Field",
            name="valueField",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        dateField.filter.list = []
        catField.filter.list = []
        valueField.filter.list = []

        # Use __file__ attribute to find the .lyr file (assuming the
        #  .pyt and .lyr files exist in the same folder)
        #param0.value = os.path.join(os.path.dirname(__file__), "Fire_Station.lyr")
        
        params = [inTable, dateField, catField, valueField]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        if parameters[0].altered:
            # If the field is not in the new feature class
            # then switch to the first field
            try:
                li = []
                m = arcpy.ListFields(parameters[0].valueAsText)
                for i in m:
                    print(i.name)
                    li.append(i.name)
                parameters[1].filter.list = li
                parameters[2].filter.list = li
                parameters[3].filter.list = li

            except:
                # Could not read the field list
                parameters[1].value = ""

        return 

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        #parameters[3].clearMessage()

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        inTable = parameters[0].valueAsText
        dateField = parameters[1].valueAsText
        catField = parameters[2].valueAsText
        valueField = parameters[3].valueAsText

        zz = inTable.split('\\')
        tableName = zz[-1]
                
        cal.createChart(dateField,catField,valueField,tableName)

        return
