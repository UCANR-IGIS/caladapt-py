import arcpy
arcpy.env.overwriteOutput = False

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "CalAdapt ArcGIS Tools"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [GetDataAPI]


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
        variable = arcpy.Parameter(
            displayName="Variable",
            name="Variable",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        gcm = arcpy.Parameter(
            displayName="GCM",
            name="GCM",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        period = arcpy.Parameter(
            displayName="Period",
            name="Period",
            datatype="GPString",
            parameterType="Required",
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
        vic = arcpy.Parameter(
            displayName="Include VIC",
            name="vic",
            datatype="GPBoolean",
            parameterType="Required",
            direction="Input")
        stat = arcpy.Parameter(
            displayName="Aggregate type",
            name="Stat",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        outTable = arcpy.Parameter(
            displayName="Output Table",
            name="outTable",
            datatype="DETable",
            parameterType="Required",
            direction="Output")

        #variable.filter.list = rl[0]
        variable.value = ""
        #gcm.filter.list = rl[1]
        gcm.value = ""
        #period.filter.list = rl[2]
        period.value = ""
        catField.enabled = False
        historical.value = False
        rcp45.value = False
        rcp85.value = False
        vic.value = False
        stat.filter.list = ['max', 'mean', 'median', 'min', 'sum']
        stat.value = 'mean'

        # Use __file__ attribute to find the .lyr file (assuming the
        #  .pyt and .lyr files exist in the same folder)
        #param0.value = os.path.join(os.path.dirname(__file__), "Fire_Station.lyr")
        
        params = [in_feature_set,individual_features,catField,variable,gcm,period,historical,rcp45,rcp85,vic,stat,outTable]
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
        #parameters[3].clearMessage()

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        features = parameters[0].valueAsText
        splitfeatures = parameters[1].valueAsText
        catField = parameters[2].valueAsText
        variable1 = parameters[3].valueAsText
        gcm1 = parameters[4].valueAsText
        period1 = parameters[5].valueAsText
        hist = parameters[6].valueAsText
        rcp45 = parameters[7].valueAsText
        rcp85 = parameters[8].valueAsText
        vic = parameters[9].valueAsText
        stat = parameters[10].valueAsText
        outTable = parameters[11].valueAsText

        #arcpy.AddMessage(outTable)
        zz = outTable.split('\\')
        workspace = "/".join(zz[:-1])
        tableName = zz[-1]
        
        #arcpy.AddMessage(outTable1)
        arcpy.AddMessage(zz)
        arcpy.AddMessage(workspace)
        arcpy.AddMessage(tableName)

        scenarios = []
        if hist == 'true':
            scenarios.append('historical')
        if rcp45 == 'true':
            scenarios.append('rcp45')
        if rcp85 == 'true':
            scenarios.append('rcp85')
        if vic == 'true':
            scenarios.append('vic')
        if splitfeatures == 'true':
            splitfeatures = True
        else:
            splitfeatures = False
            
        #arcpy.AddMessage(scenarios)
        arcpy.env.workspace = workspace
        existTest = arcpy.Exists(tableName)
        arcpy.AddMessage(existTest)

        return
