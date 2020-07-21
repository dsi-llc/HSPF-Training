# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 16:10:29 2020

@author: Anurag

This example script downloads the GLDAS data for two stations, 
adjust the time zone and saves them in a WDM file.
Please refer to the tsgettoolbox documentation for more data sources.
https://timcera.bitbucket.io/tsgettoolbox/docsrc/index.html#tsgettoolbox-documentation
"""

from tsgettoolbox import tsgettoolbox as tsget
from wdmtoolbox import wdmtoolbox as wdm

def convertunitforHSPF(constituent, df, LDAS_var):
    '''This function is for unit conversion'''
    if constituent == "ATEMP": df = (df-273)
    #From K to degC
    if constituent == "PRECIP" and 'GLDAS' in LDAS_var: 
        df = df * 3600 
        #From kg/m^2/s to mm/hour
        #Assuming that 1 kg/m^2 is close to 1 mm
        df=df*3
            #GLDAS is 3 hourly data. THis changes values from 
            #mm/hour to total precip for each times step of 3 hours.
            #There might be a better way to accomplish this task
    elif constituent == "PRECIP" and 'NLDAS' in LDAS_var:
        df=df
        #No change needed for NLDAS            
    
    return df
    
StationList=[['Allahabad', 25.43,81.84,5.5],
                ['Asmara',15.33, 38.92,3],
                ['Seattle',47.629605, -122.348941,-8]]

#Each station is a list of station name, lat, long and TimeZone
#adjustment.


Constituent=['ATEMP','PRECIP']
#Please refer to the GLDAS2 documentation below for more constituents.
#https://hydro1.gesdisc.eosdis.nasa.gov/data/GLDAS/README_GLDAS2.pdf

GLDAS_ConstituentDetails={
                    "PRECIP":["Precipitation","mm",
                    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Rainf_f_tavg","kg/m^2/s"],
                    "ATEMP":["Air Temperature","Fahrenheit",
                    "GLDAS2:GLDAS_NOAH025_3H_v2.1:Tair_f_inst","K"]
                    }

NLDAS_ConstituentDetails={
                    "PRECIP":["Precipitation","mm",
                    "NLDAS:NLDAS_FORA0125_H.002:APCPsfc","mm"],
                    "ATEMP":["Air Temperature","Fahrenheit",
                    "NLDAS:NLDAS_FORA0125_H.002:TMP2m","K"]
                    }

#If you add more constituents, you will need to expland this dict

UStop = 49.3457868 # north lat
USleft = -124.7844079 # west long
USright = -66.9513812 # east long
USbottom =  24.7433195 # south lat
#US Lat and long coordinates

WDMFileName='MetData_20200720.wdm'
wdm.createnewwdm(WDMFileName, overwrite=True)
index = 1
from datetime import datetime
with open("MetLog.txt", 'w') as Logfile:
    Logfile.write("Started Downloading the data at "
                + datetime.isoformat(datetime.now()) + " and saving in "
                + WDMFileName + "\n")
    for station in StationList:
        # Going through Each Station in the list
        TimeZoneAdjustment = station[3]
        Logfile.write("Station: " + station[0] + ", Latitude: " + str(station[1])
                        + ", Longitude: " + str(station[2])
                        + ", TimeZoneAdjustment: " + str(TimeZoneAdjustment)
                        + "\n")

        for const in Constituent:
            #Going through each constituent
            if station[1]<UStop and station[1]>USbottom and \
                station[2]>USleft and station[2]<USright:
                LDAS_variable = NLDAS_ConstituentDetails[const][2]  
                TimeStep=1  
                print('Edmonds is is USA')
            else:
                LDAS_variable = GLDAS_ConstituentDetails[const][2]
                TimeStep=3
            print(LDAS_variable)
            stationID = station
            print("Downloading " + const + " data for grid: " + station[0]) 
            df = tsget.ldas(lat=station[1], lon=station[2],
                               variable=LDAS_variable,
                               startDate="2018-12-31",
                               endDate="2019-1-31")
            column_name = df.columns[0]
            df = df[column_name]
            df.dropna()
            df = convertunitforHSPF(const,df, LDAS_variable)
            wdm.createnewdsn(WDMFileName, index,
                                constituent=const,
                                scenario="OBSERVED",location=station[0][0:8],
                                tcode=3, statid=station[0], tsstep=TimeStep,
                                description=LDAS_variable)
            #Creating an empty dataset in WDM File
            
            wdm.csvtowdm(WDMFileName, index, input_ts=df)
            #saving the data in the DSN created in previous line
            
            Logfile.write("Constituent: " + const + ", Column Name:"
            + column_name + ", DSN: " + str(index) + "\n")
            index += 1


