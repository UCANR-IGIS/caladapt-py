import math

cum_ddays = 0

def SiSine(ab, tmin, tmax, thresh):
    # Purpose: To calculate Degree-Days accumulated above or below a threshold 
    #          using a sine wave estimation of area under the curve
    # Calls: No external routines
    
    # Define data variables
    # ab - True = Above, False = Below
    # error - Returned error signal
    # ddays - Degree-days returned
    # tmax - Maximum temperature (yesterdays and todays)
    # tmin - Minimum temperature (todays and tomorrows)
    # thresh - Threshold
    # arg -
    # mn - Minimum temperature
    # mx - Maximum temperature
    # pi -
    # q -
    # ta -
    # tm -
    # xa -
    
    # initializations
    ddays = 0
    error = 0
    halfpi = math.pi/2
    #global ddays1
    #print(ddays1)
    
    if ab == True:
        mn = tmin
        mx = tmax
    else:
        mn = thresh - (tmax - thresh)
        mx = thresh + (thresh - tmin)
        
    #  Compute Degree-days
    if mn < mx:
        if mx <= thresh:
            return ddays
        tm = 0.5 * (mx + mn)
        ta = 0.5 * (mx - mn)
        
        arg = (thresh - tm)/ta
        if arg > 1.0:
            arg = 1.0
        if arg < -1.0:
            arg = -1.0
        # Approximate value of theta at arg
        xa = abs(arg)
        q = halfpi - math.sqrt(1.0 - xa) * (halfpi + xa * (-0.2121144 + xa * (0.0745610 - xa * 0.0187293)))
        q = abs(q)
        if arg < 0:
            q = -1 * q
        theta = q
        theta = theta + halfpi
        
        ddays = ((tm - thresh) * (math.pi - theta) + ta * math.sin(theta))/math.pi
    elif mn == mx:
        if mx > thresh:
            ddays = mx - thresh
    else:
        error = 1        
    
    ddays1 = ddays
    
    return ddays

def DoSine(ab, ci, tmin, tmax, thresh, tmin_tomm, tmax_yest):
    # Purpose: To calculate Degree-Days accumulated above or below a threshold 
    #          using a sine wave estimation of area under the curve
    # Calls: SiSine
    
    # Define data variables
    # ab - True = Above, False = Below
    # ci - Computation interval
    # error - Returned error signal
    # ddays - Degree-days returned
    # tmax - Maximum temperature (yesterdays and todays)
    # tmin - Minimum temperature (todays and tomorrowa)
    # thresh - Threshold
    
    # initializations
    ddays = 0
    error = 0
    
    # Compute Degree-Days
    if ci == 1: # Minimum to Minimum
        ddays = SiSine(ab, tmin, tmax, thresh) #, ddays, error)
        if error != 0:
            return
        temp = SiSine(ab, tmin_tomm, tmax, thresh) #, temp, error)
    else:  # Maximum to Maximum
        ddays = SiSine(ab, tmin, tmax_yest, thresh) #, ddays, error)
        if error != 0:
            return
        temp = SiSine(ab, tmin, tmax, thresh) #, temp, error)
    
    if error != 0:
        return
    
    print((ab, ci, tmin, tmin_tomm, tmax, tmax_yest, thresh, ddays, temp))

    ddays = (ddays + temp) / 2.0
    return ddays

def SiTria(ab, tmin, tmax, thresh):
    # Purpose: To calculate Degree-Days accumulated above or below a threshold 
    #          using a triangular estimation of area under the curve
    # Calls: No external routines
    
    # Define data variables
    # ab - True = Above, False = Below
    # error - Returned error signal
    # ddays - Degree-days returned
    # tmax - Maximum temperature (yesterdays and todays)
    # tmin - Minimum temperature (todays and tomorrowa)
    # mn - Minimum temperature
    # mx - Maximum temperature
    # thresh - Threshold
    
    # initializations
    ddays = 0
    error = 0
    
    if ab == True:
        mn = tmin
        mx = tmax
    else:
        mn = thresh - (tmax - thresh)
        mx = thresh + (thresh - tmin)
        
    #  Compute Degree-days
    if mn < mx:
        if mn < thresh:
            if mx > thresh:
                ddays = (0.5 * (mx-thresh) * (mx-thresh))/(mx-mn)
        else:
            ddays = 0.5 * (mx + mn - (2 * thresh))
    elif mn == mx:
        if mx > thresh:
            ddays = mx - thresh
    else:
        error = 1
    
    return ddays

def DoTria(ab, ci, tmin, tmax, thresh, tmin_tomm, tmax_yest): #, ddays, error):
    # Purpose: To calculate Degree-Days accumulated above or below a threshold 
    #          using a triangular estimation of area under the curve
    # Calls: Sitria
    
    # Define data variables
    # ab - True = Above, False = Below
    # ci - Computation interval
    # error - Returned error signal
    # ddays - Degree-days returned
    # tmax - Maximum temperature (yesterdays and todays)
    # tmin - Minimum temperature (todays and tomorrowa)
    # thresh - Threshold
    
    # initializations
    ddays = 0
    error = 0
    
    # Compute Degree-Days
    if ci == 1: # Minimum to Minimum
        ddays = SiTria(ab, tmin, tmax, thresh) #, dday, error)
        if error != 0:
            return
        temp = SiTria(ab, tmin_tomm, tmax, thresh) #, temp, error)
    else:  # Maximum to Maximum
        ddays = SiTria(ab, tmin, tmax_yest, thresh) #, dday, error)
        if error != 0:
            return
        temp = SiTria(ab, tmin, tmax, thresh) #, temp, error)
    
    if error != 0:
        return
    
    #print((ab, ci, tmin[0], tmin[1], tmax[0], tmax[1], thresh, ddays, temp))
    
    ddays = (ddays + temp) / 2.0
    return ddays

def VertCut(ab, method, tmin, tmax, thresh):
    # Purpose: Calculate the area to be substracted from Degree-Days computed with
    #          a horizontal cut off to produce a vertical cut off.
    # Calls: No external routines
    
    # Define data variables
    # ab - True = Above, False = Below
    # method - 1: sine wave 2; triangular
    # tmax - Maximum temperature (yesterdays and todays)
    # tmin - Minimum temperature (todays and tomorrowa)
    # thresh - Threshold
    # area - 
    # lt - local lower threshold
    # mn - Minimum temperature
    # mx - Maximum temperature
    # q -
    # ta =
    # thresh - Thresholds (upper and lower threshold as list)
    # tm - Average temperature
    # ut - local upper threshold
    
    # initializations
    area = 0.0
    pi = math.pi
    lt = thresh[0]
    
    if ab == 1:
        mn = tmin
        mx = tmax
        ut = thresh[1]
    else:
        mn = lt - (tmax - lt)
        mx = lt + (lt - tmin)
        ut = lt + (lt - thresh[1])
    
    # Check for appropriate conditions
    if mx <= ut:
        return area
    if ((mn == mx) or (mn >= ut)):
        return area
    
    # Compute area for sine wave
    if method == 1:
        tm = 0.5 * (mx + mn)
        ta = 0.5 * (mx - mn)
        
        theta = math.asin((ut-tm)/ta)
        q = pi - 2.0 * theta
        area = q * (ut-lt)/(pi * 2.0)
    else:
        q = (mx - ut) / (mx - mn)
        area = q * (ut-lt)
    
    #print((ab, lt, mn, mx, ut, tm, ta, theta, q, area))    
    
    return area

def DoVrct(ab, method, ci, tmin, tmax, thresh, tmin_tomm, tmax_yest): #, Area):
    # Purpose: produce vertical cutoff areas for double sine and double trianglar
    #          methods
    # Calls: VertCut
    
    # Define data variables
    # ab - True = Above, False = Below
    # method - Computation method
    # ci - Computation interval
    # tmax - Maximum temperature (yesterdays and todays)
    # tmin - Minimum temperature (todays and tomorrowa)
    # thresh - Threshold
    # area - 
    # temp - 
    
    # Compute for peak: min, max, min
    if ci == 1:
        area = VertCut(ab, method, tmin, tmax, thresh) #, area)
        temp = VertCut(ab, method, tmin_tomm, tmax, thresh) #, temp)
    else: # Compute for trough : max, min, max
        area = VertCut(ab, method, tmin, tmax_yest, thresh) #, area)
        temp = VertCut(ab, method, tmin, tmax, thresh) #, temp)
        
    area = (area + temp) / 2.0
    
    return area

def Huberm(tmin, tmax, lthres, uthres): #, HU, error):
    # Purpose: To Calculate Degree-Days accumulated above a threshold using
    #          a Sine Wave estimation of area under the curve with reduced 
    #          contributions above the upper threshold.
    # Calls: No external routines
    
    # Define data variables
    # tmax - Maximum temperature (yesterdays and todays)
    # tmin - Minimum temperature (todays and tomorrowa)
    # lthres - Lower threshold
    # uthres - Upper threshold
    # hu - Heat Units
    # error - Returned error signal
    # halfpi = a constant
    # pi - a constant
    # theta1 -
    # theta2 -
    # w -
    
    pi = math.pi
    halfpi = math.pi/2
    error = 0
    ddays = 0.0
    
    if tmin > tmax:
        error = 1
        return ddays
    
    mean = (tmax + tmin)/2.0
    
    if tmin < lthres:
        if tmax <= lthres:
            return ddays
        elif tmax <= uthres:
            w = tmax - mean
            theta1 = math.asin((lthres - mean)/w)
            ddays = (w * math.cos(theta1) - (lthres - mean) * (halfpi - theta1))/pi
        else:
            w = tmax - mean
            theta1 = math.asin((lthres - mean)/w)
            theta2 = math.asin((uthres - mean)/w)
            ddays = w * (math.cos(theta1) - math.cos(theta2)) - (lthres - mean) * (halfpi - theta1) +- (uthres - mean) * (halfpi - theta2)
            ddays = ddays / pi
    else:
        if tmin < uthres:
            if tmax <= uthres:
                ddays = mean - lthres - 0.3
                if ddays < 0.0:
                    ddays = 0.0
            else:
                w = tmax - mean
                theta2 = math.asin((uthres - mean)/w)
                ddays = (mean - lthres) - (w * math.cos(theta2) - (uthres - mean) * (halfpi - theta2))/pi
        else:
            ddays = uthres - lthres
        
    return ddays

def HeatU(lthres, cthres, cm, coff, ci, tmin, tmax, tmin_tomm = 0, tmax_yest = 0): #, ndays, ddays, accum, error)
    # Purpose: Calculate Degree-Days for one day from Max & min
    # Calls: DoSine, DoTria, DoVrct, Huberm, SiSine, SiTria, VertCut
    
    # Define data variables
    # above - True for heat units
    # cm - Computation method
    # ci - Computation interval
    # error - Returned error signal
    # ddays - Degree-days returned
    # tmax - Maximum temperature (yesterdays and todays)
    # tmin - Minimum temperature (todays and tomorrowa)
    # thresh - Thresholds
    # temp1 - DD above cutoff threshold
    # temp2 - additional DD for vertical cutoff
    
    global cum_ddays
    
    if (coff >= 2):
        if (cm <= 2):
            j = 1
        else: #if (cm > 4):
            j = 2
            
    #print ("J Value is %s" % j)
            
    above = 1
    temp1 = 0.0
            
    thresh = (lthres, cthres)
    
    if(cm == 1): # Single sine
        ddays = SiSine(above, tmin, tmax, lthres)
    elif(cm == 2): # Double sine
        ddays = DoSine(above, ci, tmin, tmax, lthres, tmin_tomm, tmax_yest)
    elif(cm == 3): # Single triangle
        ddays = SiTria(above, tmin, tmax, lthres)
    elif(cm == 4): # Double triangle
        ddays = DoTria(above, ci, tmin, tmax, lthres, tmin_tomm, tmax_yest)
    elif(cm == 5): # Huber's method
        ddays = Huberm(tmin, tmax, lthres, cthres) #, ddays[i], error)
        return ddays
             
    if (coff > 0): # Cutoff Active
        # Compute degree-days
        if(cm == 1): # Single sine
            temp1 = SiSine(above, tmin, tmax, cthres)
        elif(cm == 2): # Double sine
            temp1 = DoSine(above, ci, tmin, tmax, cthres, tmin_tomm, tmax_yest)
        elif(cm == 3): # Single triangle
            temp1 = SiTria(above, tmin, tmax, cthres)
        elif(cm == 4): # Double triangle
            temp1 = DoTria(above, ci, tmin, tmax, cthres, tmin_tomm, tmax_yest)

        ddays = ddays - temp1 # remove dd above cutoff
        if coff >= 2: # Check for 2 = Int. or 3 = Vert. Cutoff
            if((cm == 1) or (cm == 3)): # Single
                temp2 = VertCut(above, j, tmin, tmax, thresh)
            elif((cm >= 2) or (cm == 4)): # Double
                temp2 = DoVrct(above, j, ci, tmin, tmax, thresh, tmin_tomm, tmax_yest)
            #elif(cm == 3): # Single triangle
            #    temp2 = VertCut(above, j, tmin, tmax, thresh)
            #elif(cm == 4): # Double triangle
            #    temp2 = DoVrct(above, j, ci, tmin, tmax, thresh)
            
            if temp1 > temp2:
                temp1 = temp2 # IC must be <= VC
            if coff == 3: # Vertical cutoff
                temp1 = temp2
            ddays = ddays - temp1 # remove dd above cutoff
        if ddays < 0.0:
            ddays = 0.0
            
    #cum_ddays = cum_ddays + ddays
            
    return ddays
