import pygrib
import glob
import os
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from matplotlib.mlab import bivariate_normal
from mpl_toolkits.basemap import Basemap, cm
import numpy as np
from datetime import datetime
import argparse
parser = argparse.ArgumentParser()

parser.add_argument("-lat1", "--lat1", help="Lower left corner latitude")
parser.add_argument("-lat2", "--lat2", help="Upper right corner latitude")
parser.add_argument("-lon1", "--lon1", help="Lower Left corner longitude")
parser.add_argument("-lon2", "--lon2", help="Upper Right corner longitude")
parser.add_argument("-var", "--var", help="Variables: Example Temperature")
parser.add_argument("-model", "--model", help="Model: gfs is default")


args = parser.parse_args()


zero_celsius_in_kelvin = 273.15
var = "Total-Precipitation"
region = "NA"

def time2Zulu(t):
    """
    Convert time to Zulu time
    
    Args:
        t (integer): time of data
    """
    if 0 == t or 24 == t or 48 == t or 72 == t or 96 == t or 120 == t or 144 == t or 168 == t or 192 == t or 216 == t or 240 == t or 288 == t or 336 == t or 384 == t:
        return "00Z"
    elif 6 == t or 30 == t or 54 == t or 78 == t or 102 == t or 126 == t or 150 == t or 174 == t or 198 == t or 222 == t or 252 == t or 300 == t or 348 == t:
        return "06Z"
    elif 12 == t or 36 == t or 60 == t or 84 == t or 108 == t or 132 == t or 156 == t or 180 == t or 204 == t or 228 == t or 264 == t or 312 == t or 360 == t:
        return "12Z"
    elif 18 == t or 42 == t or 66 == t or 90 == t or 114 == t or 138 == t or 162 == t or 186 == t or 210 == t or 234 == t or 276 == t or 324 == t or 372 == t:
        return "18Z"

def kel2cel(T):
    """ 
    Convert temperatures in degrees Kelvin to degrees Celsius

    Args:
        T (numpy.ndarray): temperature in degrees Kelvin

    Returns:
        numpy.ndarray : given temperature converted to degrees Celsius
    """
    # convert to an array
    kelvin = np.asanyarray(T).astype(float)
    oldshape = kelvin.shape
    kelvin = kelvin.reshape(-1)
    invalid = kelvin < 0
    if invalid.any():
        warnings.warn("{} temperatures below 0 Kelvin masked with NaN".format(
            invalid.sum()))
        kelvin[invalid] = np.nan
    # convert to kelvin
    celsius = kelvin - zero_celsius_in_kelvin
    # replace invalid temperatures
    return celsius.reshape(oldshape)

cmap = plt.get_cmap( 'bwr' )
cmap.set_bad( color = 'k', alpha = 1. )

if args.lon1 is None:
    newlon1 = ( -155.8 % 359.7 )
elif 0 > float(args.lon1):
    newlon1 = ( float(args.lon1) % 359.7 )
else:
    newlon1 = float(args.lon1)

if args.lon2 is None:
    newlon2 = ( -56 % 359.7 )
elif 0 > float(args.lon2):
    newlon2 = ( float(args.lon2) % 359.7 )
else:
    newlon2 = float(args.lon2)
    
if args.lat1 is None:
    newlat1 = 22.85
else:
    newlat1 = float(args.lat1)

if args.lon2 is None:
    newlat2 = 73
else:
    newlat2 = float(args.lat2)

    
def plotPrecip( filename ):
    grbs=pygrib.open(filename)
    grbs.seek(0)
    grb = grbs.select(name='Total Precipitation')[0]
    #for key in grb.keys():
        #print(key)
    data, lats, lons = grb.data(lat1=newlat1, lat2=newlat2, lon1=newlon1, lon2=newlon2)
    tempdata = data
    colorBar = None
    if 0==tempdata.size:
        return
    else:
        dataDate = str(grb.dataDate)
        dataTime = grb.dataTime
        oldformatteddataObject = datetime.strptime(dataDate, '%Y%m%d')
        newformatteddataObject = oldformatteddataObject.strftime("%b %d %Y")
        validityTime = grb.validityTime
        validityDate = str(grb.validityDate)
        oldformattedDateobject = datetime.strptime(validityDate, '%Y%m%d' )
        newformat = oldformattedDateobject.strftime("%a, %b %d %Y")
        m = Basemap( llcrnrlat=newlat1,urcrnrlat=newlat2,\
        llcrnrlon=newlon1,urcrnrlon=newlon2, \
        resolution='l',projection="mill", fix_aspect=False
        )
        x, y = m(lons, lats)
        clevs = [0,1,2.5,5,7.5,10,15,20,30,40,50,70,100,150,200,250,300,400,500,600,750]
        #cs = m.pcolormesh(x, y, np.squeeze(tempdata), cmap = cmap, norm = norm )
        cs = m.contourf(x, y, np.squeeze(tempdata), clevs, cmap=cm.s3pcpn )
        if not colorBar:
            m.colorbar(cs, location='bottom', pad="10%")
            colorBar = True
        m.drawcoastlines()
        m.drawmapboundary()
        m.drawcounties()
        m.drawcountries()
        m.drawstates()
        newfilename = os.path.basename(filename.replace('.', '-').lower())
        plt.title('GFS Total Precipitation,\n Init: '+time2Zulu(dataTime)+ ' '+newformatteddataObject+' Forecast Hour:['+str(grb.forecastTime)+'] valid at '+time2Zulu(grb.forecastTime) + ' '+newformat+' bcstorms.ca', fontsize=9)
        plt.savefig(region+'gfs-'+var+'-'+newfilename+'.png')

def plotTemp( filename ):
    grbs=pygrib.open(filename)
    grbs.seek(0)
    grb = grbs.select(name='2 metre temperature')[0]
    #for key in grb.keys():
        #print(key)
    data, lats, lons = grb.data(lat1=newlat1, lat2=newlat2, lon1=newlon1, lon2=newlon2)
    tempdata = data
    colorBar = None
    if 0==tempdata.size:
        return
    else:
        dataDate = str(grb.dataDate)
        dataTime = grb.dataTime
        oldformatteddataObject = datetime.strptime(dataDate, '%Y%m%d')
        newformatteddataObject = oldformatteddataObject.strftime("%b %d %Y")
        validityTime = grb.validityTime
        validityDate = str(grb.validityDate)
        oldformattedDateobject = datetime.strptime(validityDate, '%Y%m%d' )
        newformat = oldformattedDateobject.strftime("%a, %b %d %Y")
        m = Basemap( llcrnrlat=newlat1,urcrnrlat=newlat2,\
        llcrnrlon=newlon1,urcrnrlon=newlon2, \
        resolution='l',projection="mill", fix_aspect=False
        )
        x, y = m(lons, lats)
        #clevs = [0,1,2.5,5,7.5,10,15,20,30,40,50,70,100,150,200,250,300,400,500,600,750]
        cs = m.pcolormesh(x, y, np.squeeze(tempdata) )
        if not colorBar:
            m.colorbar(cs, location='bottom', pad="10%")
            colorBar = True
        m.drawcoastlines()
        m.drawmapboundary()
        m.drawcounties()
        m.drawcountries()
        m.drawstates()
        newfilename = os.path.basename(filename.replace('.', '-').lower())
        plt.title('GFS 2m temps,\n Init: '+time2Zulu(dataTime)+ ' '+newformatteddataObject+' Forecast Hour:['+str(grb.forecastTime)+'] valid at '+time2Zulu(grb.forecastTime) + ' '+newformat+' bcstorms.ca', fontsize=9)
        plt.savefig(region+'gfs-2mtemps-'+newfilename+'.png')

for filename in glob.iglob("GFS/jan-22-2018/*"):
    cs = None
    data = None
    if "f000" in filename:
        continue
    print(filename)
    if ( args.var is None ):
        continue
    elif "Precipitation" == args.var:
        plotPrecip(filename)
    elif "tmp" == args.var:
        plotTemp(filename)
