
<!-- README.md is generated from README.Rmd. Please edit that file -->

# caladapt-py <img src="https://ucanr-igis.github.io/caladapt-py/reference/figures/caladaptpy-beta_logo.svg" align="right" width="240" />

<!-- badges: start -->
[![degree-day-challenge: passing](https://raw.githubusercontent.com/ucanr-igis/degree-day-challenge/main/badges/degree-day-challenge-passing.svg)](https://ucanr-igis.github.io/degree-day-challenge/)


[![Lifecycle:
experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://www.tidyverse.org/lifecycle/#experimental)
<!-- badges: end -->

See also: <https://ucanr-igis.github.io/caladapt-py/>

`caladapt-py` is an API client that makes it easier to work with data from [Cal-Adapt.org](https://cal-adapt.org/) in Python and ArcGIS. The role of `caladapt-py` is to bring data into Python and ArcGIS and provide high-level functions to get it into your GIS for further analysis:

`caladapt-py` allows you to:

*   download netCDF data from the Cal-Adapt Data Server using HTTPS. These data allow for custom analyzes to be conducted at the statewide scale using GIS.
*   retrieve values by user defined points, lines, or polygons
*   store results in File Geodatabase tables and other table types

**‘Beta’** status means:

*   the tool is still under development
*   the tool is being updated fairly often
*   there’s a possibility that updates will _not_ be backward compatible

[](#installation)Installation
-----------------------------

`caladapt-py` is hosted on [GitHub](https://github.com/ucanr-igis/caladapt-py). To install, download the [zip](https://github.com/UCANR-IGIS/caladapt-py/archive/refs/heads/master.zip) file from github and uncompress the zip file into your project folder. For ArcGIS, load the python toolbox into your ArcGIS Project and use the tools in the toolbox. For Python, import the CalAdaptLib package and use the different modules as needed.

[](#general-workflow)General Workflow
-------------------------------------

### ArcGIS Python Toolbox
<img src="https://ucanr-igis.github.io/caladapt-py/reference/figures/pythonToolbox.png"/>

1. Add toolbox to ArcGIS Pro Project
2. Run tool to download results from user defined areas
3. Run tools to download netCDF datasets
4. Perform additional GIS analyzes based on returned data

### Python (Jupyter Notebook)

In general, there are three steps to getting data via the Cal-Adapt API:

1. Import the ArcPy module from ArcGIS Pro
    
    `import arcpy`
    
2. Add toolbox to ArcGIS Pro Project
3. In jupyter Notebook reference both the CalAdapy.pyt toolbox and the CalAdaptLib.py module
    
    `arcpy.ImportToolbox(r'D:\Data\ArcGIS\Projects\CalAdapt_Cookbook\CalAdaptLib\CalAdapt.pyt','')`
    
    `import CalAdaptLib as cal`
    
4. After importing you can run tools from the ArcGIS Python Toolbox or the CalAdaptLib
    
    ie. `arcpy.GetDataAPI("Get Data from API Input Feature Set (Polygons)", None, '', "tair", "gfdl-cm3", "month", True, True, True, False, "mean", r"D:\Data\ArcGIS\Projects\CalAdaptpy_Test\CalAdaptpy_Test.gdb\GetDataAPI")`
