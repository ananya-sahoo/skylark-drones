from pprint import pprint
from exifpy212 import exifread
import pysrt
import sys
import subprocess
import os
import math
import csv
import pandas as pd
import folium
import simplekml
import gmplot
sys.path.append('C:\Python Codes')

##################################################################################

#READING METADATA

list1=[]
img=[]
for i in range(4, 609):
    # Open image file for reading (binary mode)
    if i in range(4,10):
        j='00'+str(i);
    if i in range(10,100):
        j='0'+str(i);
    if i in range(100,609):
        j=str(i);
    try:
        f = open('C:\Python27\image\DJI_0'+j+'.jpg', 'rb')
        img.append('DJI_0'+j)
    except:
        continue
    #Return Exif tags
    tags = exifread.process_file(f)
    temp=[]
    for key in tags.keys():
        if key in ('GPS GPSLatitude','GPS GPSLongitude'):
            #Conversion of latitude and longitude to decimal
            d = float(tags[key].values[0].num) / float(tags[key].values[0].den)
            m = float(tags[key].values[1].num) / float(tags[key].values[1].den)
            s = float(tags[key].values[2].num) / float(tags[key].values[2].den)
            y = d + (m / 60.0) + (s / 3600.0)
            temp.append(y)
    list1.append(temp) #Storing latitude and longitude of each image in list1
    
##################################################################################

#READING SRT FILE

dt, dlat, dlon, demp, dline = [], [], [], [], []
count = 0
with open('F:\Skylark Drones\DJI_0301.srt') as input_file:
    for line in input_file:
        count=count+1;
        if count%4==1:
            dt.append((int)((int(line)+9)/10)) #Storing the time(in sec) for each frame of video
        elif count%4==3:
            dtemp = line.split(',')
            #Storing longitude and latitude of drone in each frame of the video
            dlon.append(float(dtemp[0]))
            dlat.append(float(dtemp[1]))   

##################################################################################

#CALCULATION OF DISTANCE OF THE IMAGE FROM DRONE POSITION AND CHECKING WHETHER IT LIES WITHIN 35 m

result=[]
result.append(['Time(in sec)','Image Names'])
for i in range(1,18): #Time(in sec)
    temp=set()
    for j in range(0,163): #Iterating through each frame
        if dt[j]==i: #Checking which frames come within the present one second
            for k in range(0,len(list1)): #Iterating through each image(jpg)
                try:
                    earthRadius = 6371000;
                    dLat = math.radians(dlat[j]-list1[k][1]);
                    dLng = math.radians(dlon[j]-list1[k][0]);
                    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(dlat[j])) * math.cos(math.radians(list1[k][0])) * math.sin(dLng/2) * math.sin(dLng/2);
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a));
                    dist = float(earthRadius * c);
                    if dist<=35: #Checking whether image lies within 35 m
                        temp.add(img[k]) #Creating a list 'temp' for each second
                except:
                    continue
    result.append([i]+list(temp)) #Adding list of images within 35 m in the present one second

#WRITING THE RESULT INTO CSV FILE

with open("output.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(result)

##################################################################################

#FINDING IMAGES WITHIN 50 m FOR EACH OF THE LOCATION SPECIFIED IN assets.csv

fp = "F:\Skylark Drones\\assets.csv"
lati, longi = [], []
app=[]
with open( fp ) as csvfile: #Reading csv file
    rdr = csv.reader( csvfile )
    for i, row in enumerate( rdr ):
        temp1=[]
        if i == 0: continue # Skip column titles
        longi.append(float(row[1])) #Storing longitude of each location in 'longi' list
        lati.append(float(row[2]))  #Storing latitude of each location in 'lati' list
        temp1.append(row[0])
        temp1.append(row[1])
        temp1.append(row[2])
        app.append(temp1)   #Storing first 3 columns of each entry of csv in 'app' list
result=[['asset_name', 'longitude', 'latitude', 'image_names']] #Storing first row in 'result' list

###################################################################################

#CALCULATION OF DISTANCE OF EACH LOCATION OF CSV FILE FROM DRONE POSITION AND CHECKING WHETHER IT LIES WITHIN 50 m

for i in range(0,len(lati)):    #Iterating through each location in csv
    temp=[]
    for k in range(0,len(list1)):   #Iterating through each image(jpg)
        try:
            earthRadius = 6371000;
            dLat = math.radians(lati[i]-list1[k][1]);
            dLng = math.radians(longi[i]-list1[k][0]);
            a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lati[i])) * math.cos(list1[k][0]) * math.sin(dLng/2) * math.sin(dLng/2);
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a));
            dist = float(earthRadius * c);
            if dist<=50:    #Checking whether image lies within 50 m
                temp.append(img[k]) #Creating a list 'temp' for each location      
        except:
            continue
    result.append(app[i]+temp); #Adding list of images within 50 m for each location in csv

#WRITING THE RESULT INTO assets.csv

with open("F:\Skylark Drones\\assets.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerows(result)

###################################################################################

#CREATING KML FILE TO SHOW DRONE PATH

ctr=0;
lines=[]
temp=[]
imageid, dlat1, dlon1 = [], [], []
with open('F:\Skylark Drones\DJI_0301.srt') as in_file: #Reading SRT file to obtain drone position at different instances
    for line in in_file:
        ctr=ctr+1
        if ctr%4==1:
            imageid.append(line)    #Storing frame number in 'imageid' list
        if ctr%4==3:
            lines.append(line)      #Storing coordinates
for element in lines:
    temp = element.split(',')
    if temp:
        dlon1.append(float(temp[0]))    #Storing longitude
        dlat1.append(float(temp[1]))    #Storing latitude

#Creating and saving required info in KML File
        
kml=simplekml.Kml()
for i in range(len(dlon1)):
    kml.newpoint(name=imageid[i], coords=[(dlon1[i], dlat1[i])])
kml.save('F:\Skylark Drones\drone_path.kml')
