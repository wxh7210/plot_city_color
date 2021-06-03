# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 15:09:54 2021

This program reads the 52 cities' air quality forecast accuracy scores 
from excel and marks the scores on the map of Yangtze River Delta map.
The YRD region includes Shanghai, Zhejiang Province, Jiangsu Province,
Anhui Province and Jiangxi Province. 

@author: wangxh
"""
import pandas as pd

import shapefile
import cartopy.crs as ccrs
import cartopy.io.shapereader as shapereader
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib as mpl



def plot_underover(ax,title,citynames,lats,lons,over,under):
    """
    Mark each city's number of over- and under-estimate of 
    AQI on the YRD map.
    
    Parameters
    ----------
    ax : matplotlib.axes

    title : string
        the name of the plot
    citynames : pandas.series
        52 cities' names
    lats, lons: pandas.series
        the lat and lon of each city
    over, under: pandas.serise
        the number of over and under esitmate of 
        AQI of each city
    -------
    Return None.
    
    """

    ax.set_title(title,fontsize=15)

    #set colorbar
    cmap = mpl.colors.ListedColormap(['gray','darkred','red','tomato',
                                      'lightsalmon','cyan','deepskyblue','blue','darkblue'])
    bounds = [0,20,30,40,50,60,70,80,90,100]
    norm = mpl.colors.BoundaryNorm(bounds,cmap.N)
   
   
   #mark the over and under estimates
    for i in range(len(over)):
        ax.text(lons[i]-0.2,lats[i]+0.05,over[i],fontsize=12,c="black",weight="bold")
        ax.text(lons[i]-0.2,lats[i]-0.13,under[i],fontsize=12,c="black")
   #set legend
    cb_ax = fig.add_axes([0.78,0.14,0.02,0.2])  #(x,y,width,height)
    cb = mpl.colorbar.ColorbarBase(cb_ax,cmap=cmap,norm=norm,ticks=bounds,orientation='vertical')
    cb.set_label("预报准确率  单位：%",fontsize=10)
    ax.text(120.3,25.4,"预报偏高次数",fontsize=12,c='black')
    ax.text(120.3,25.1,"预报偏低次数",fontsize=12,c='black')
   
    #mark cities' name
    for i in range(len(citynames)):
        ax.text(lons[i]-0.05,lats[i],citynames[i],ha = "left",va="top",fontsize=7)
    #save image
    plt.savefig(r"./output/"+title+".png",dpi=300.0)
    plt.show()
    return


def plot_zql_color(ax,city,zql):
    """
     mark the forecase accuracy scores of each city

    Parameters
    ----------
    ax : matplotlib.axes
    city : string
        city name
    zql : real
      forecast accuracy score of city
    Returns
    -------
    yanse : string
        facecolor of city

    """
    shpfile=r"H:\2021\4-23 python_Rbf插值\shp_files/四省一市cities_revised202105.shp"
    sf = shapefile.Reader(shpfile,encoding='utf-8')
    vertices = []
    codes = []
    yanse = 'white'
    for shape_rec in sf.shapeRecords():
        if shape_rec.record[1] in city:  #plot the city
            pts = shape_rec.shape.points #sf.shape(0).points == sf.shapeRecord(0).shape.points
            prt = list(shape_rec.shape.parts) + [len(pts)] # the number of ploygon of the specific city
            for i in range(len(prt) - 1):
                for j in range(prt[i], prt[i + 1]):
                    vertices.append((pts[j][0], pts[j][1]))
                codes += [mpath.Path.MOVETO]  #construct the Path code
                codes += [mpath.Path.LINETO] * (prt[i + 1] - prt[i] - 2) #construct the Path code
                codes += [mpath.Path.CLOSEPOLY] #construct the Path code
            clip = mpath.Path(vertices, codes) #construct Path
            #set colorbar of zql
            if zql < 20:
                yanse = 'gray'
            elif zql < 30:
                yanse = 'darkred'
            elif zql < 40:
                yanse = 'red'
            elif zql < 50:
                yanse = 'tomato'
            elif zql < 60:
                yanse = 'lightsalmon'
            elif zql < 70:
                yanse = 'cyan'
            elif zql < 80:
                yanse = 'deepskyblue'
            elif zql < 90:
                yanse = 'blue'
            elif zql < 100:
                yanse = 'darkblue'
            #plot the facecolor of the specific city
            ax.add_patch(mpatches.PathPatch(clip,facecolor=yanse))
    
    return yanse
    



#-------------main---------------------------
plt.rcParams['font.sans-serif']=['SimSun'] #Font=Songti
plt.rcParams['axes.unicode_minus']=False #show the minus
plt.rcParams['font.weight'] = 'bold' #normal bold

fig = plt.figure(figsize=[10,10])
ax=plt.axes(projection=ccrs.PlateCarree())
ax.tick_params(labelsize=15)  #x和y轴字体大小
ax.set_extent([112.9,123,24.3,35.5],ccrs.PlateCarree()) #yrd limit the map to lon1,lon2,lat1,lat2

#plot the map
shp_path = r'H:\2021\4-23 python_Rbf插值\shp_files/'
yrd = shapereader.Reader(shp_path+r'四省一市cities_revised202105.shp').geometries()
ax.add_geometries(yrd,ccrs.PlateCarree(),edgecolor="black",facecolor="None",alpha=0.5)

#add lat and lon labels
ax.set_xticks([115,117,119,121], crs=ccrs.PlateCarree())
ax.set_yticks([27,30,33], crs=ccrs.PlateCarree())
lon_formatter = LongitudeFormatter(zero_direction_label=True)
lat_formatter = LatitudeFormatter()
ax.xaxis.set_major_formatter(lon_formatter)
ax.yaxis.set_major_formatter(lat_formatter)

#read the data of city forecast accuracy scores of 52 city in YRD region
data = pd.read_excel(r"./长三角41城市落区图5月预报准确率.xlsx",sheet_name='预报准确率')

#plot the color of each city according to the forecast accuracy scores
for i in range(len(data)):
    plot_zql_color(ax, data.城市[i], data.预报准确率[i])
    
#mark the number of over- and under-estimates of each city
plot_underover(ax=ax,title='2021年5月长三角城市24h预报准确率',
          citynames=data["city"],lats=data["lat"],lons=data['lon'],
          over=data["预报偏高"],under=data["预报偏低"])









