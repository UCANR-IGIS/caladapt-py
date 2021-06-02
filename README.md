
<!-- README.md is generated from README.Rmd. Please edit that file -->

# caladapt-py <img src="https://ucanr-igis.github.io/caladapt-py/reference/figures/caladaptpy-beta_logo.svg" align="right" width="240" />

<!-- badges: start -->

[![Lifecycle:
experimental](https://img.shields.io/badge/lifecycle-experimental-orange.svg)](https://www.tidyverse.org/lifecycle/#experimental)
<!-- badges: end -->

See also: <https://ucanr-igis.github.io/caladapt-py/>

`caladapt-py` is an API client that makes it easier to work with data from
[Cal-Adapt.org](https://cal-adapt.org/) in Python and ArcGIS. The role of `caladapt-py` is
to bring data into Python and ArcGIS and provide low-level functions to get it into the
shape and format you require:

**‘Beta’** status means:

1)  the package is still under development  
2)  the package is being updated fairly often  
3)  there’s a possibility that updates will *not* be backward
    compatible  
4)  user feedback and input is welcome

*Development Status (May 2021)*

  - `caladapt-py` only supports Cal-Adapt’s raster data layers (which is
    most of them). There are no plans at present to support importing
    station data (i.e., sea level rise).
  - Retrieving values currently works. Retrieving rasters is not yet
    supported. 
  - Currently you can download the source netcdf data used in CalAdapt
  - Currently you can query locations by user-provided points, lines, and polygons.

## Installation

`caladapt-py` is hosted on
[GitHub](https://github.com/ucanr-igis/caladapt-py).
To install, download the zip  file from github and uncompress the zip file  into your project folder. For ArcGIS, load the python toolbox into your ArcGIS Project and use the tools in the toolbox. For Python, import the libarary and use the different modules as needed.

## General Workflow

### Python (Jupyter Notebook)
In general, there are three steps to getting data via the Cal-Adapt API:

1)  ...
2)  ...

3)  ...
    
### ArcGIS Python Toolbox
In general, there are three steps to getting data via the Cal-Adapt API:

1)  ...
2)  ...
3)  ...

# Convenience Features and Functions

  - You can search the Cal-Adapt catalog of raster series from within Python and ArcGIS. Download a new version of the catalog with freshResourceList().
