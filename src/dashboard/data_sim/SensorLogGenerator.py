#! /usr/bin/python
#
# Markus Schmidberger, schmidbe@amazon.de
# December 21, 2014
# Simulate SensorLog (iphone app) Data and submit to Kinesis

import json
from boto import kinesis
import time
import datetime
import multiprocessing
import random
import sys


# CONFIG
REGION = 'eu-central-1'
#REGION = 'us-west-2'
STREAMNAME = 'IoTSensorDemoEUCentral'
FNAMEACC = str(sys.argv[4])
FNAMEORI = str(sys.argv[5])
FNAMEGEO = str(sys.argv[6])
RUNS = int(sys.argv[1])
SENDTIME = int(sys.argv[3])
SIMPHONES = int(sys.argv[2])
SIMIPS = '10.0.10.'
RANDOMSTART = True;


# READ example file
# generated with 30 Hz -> 0.033sec
print "Load Simulation-Data"
f = open(FNAMEACC,'r')
ff = f.readlines()
headerACC = ff[0].replace("\n","").replace("\"","").split(',')[1:]
linesACC = ff[1:]
f.close()
f = open(FNAMEORI,'r')
ff = f.readlines()
headerORI = ff[0].replace("\n","").replace("\"","").split(',')[1:]
linesORI = ff[1:]
f.close()
f = open(FNAMEGEO,'r')
ff = f.readlines()
headerGEO = ff[0].replace("\n","").replace("\"","").split(',')[1:]
linesGEO = ff[1:]
f.close()


# Main Simulation function
# print end-start # we are to slow for 30Hz )-:   
def sim(header,linesACC,linesORI,linesGEO,SIMIP,RUNS,REGION,STREAMNAME,RANDOMSTART):
    
    # Kinesis connection
    kinesisConn = kinesis.connect_to_region(REGION)
    
    # for every line create json and send to Kinesis
    records = []
    start = time.time()
    for k in range(RUNS):
      
        count = 0
        
        if RANDOMSTART == True:
            startline = random.randint(0,len(linesACC))
        else:
            startline = 0
            
        for lineACC in linesACC[startline:]:
            jsonstr = ''
            liACC = lineACC.split(',')
            i = 0
            for l in liACC[1:]:
                l=l.replace("\n","").replace("\"","")
                if( headerACC[i] == "device" or headerACC[i] == "sensorname" or headerACC[i] == "cognitoId"):
                    dat = '"' + headerACC[i] + '":"' + l +'"'
                else:
                    dat = '"' + headerACC[i] + '":' + l
                jsonstr = jsonstr + "," + dat
                i = i +1
            jsonstr = "{"+ jsonstr[1:] + "}"
            jsonobj = json.loads(jsonstr)
            ts = time.time()
            jsonobj["recordTime"] = ts
            jsonobj["cognitoId"] = "eu-west-1:" + str(abs(hash(SIMIP)))
            record = {'Data': json.dumps(jsonobj),'PartitionKey':str('screenAccG')}
            records.append(record)
            
            lineORI = linesORI[startline+count]
            jsonstr = ''
            liORI = lineORI.split(',')
            i = 0
            for l in liORI[1:]:
                l=l.replace("\n","").replace("\"","")
                if( headerORI[i] == "device" or headerORI[i] == "sensorname" or headerORI[i] == "cognitoId"):
                    dat = '"' + headerORI[i] + '":"' + l +'"'
                else:
                    dat = '"' + headerORI[i] + '":' + l
                jsonstr = jsonstr + "," + dat
                i = i +1
            jsonstr = "{"+ jsonstr[1:] + "}"
            jsonobj = json.loads(jsonstr)
            ts = time.time()
            jsonobj["recordTime"] = ts
            jsonobj["cognitoId"] = "eu-west-1:" + str(abs(hash(SIMIP)))
            record = {'Data': json.dumps(jsonobj),'PartitionKey':str('screenAdjustedEvent')}
            records.append(record)
            
            lineGEO = linesGEO[startline+count]
            jsonstr = ''
            liGEO = lineGEO.split(',')
            i = 0
            for l in liGEO[1:]:
                l=l.replace("\n","").replace("\"","")
                if( headerGEO[i] == "device" or headerGEO[i] == "sensorname" or headerGEO[i] == "cognitoId"):
                    dat = '"' + headerGEO[i] + '":"' + l +'"'
                else:
                    dat = '"' + headerGEO[i] + '":' + l
                jsonstr = jsonstr + "," + dat
                i = i +1
            jsonstr = "{"+ jsonstr[1:] + "}"
            jsonobj = json.loads(jsonstr)
            ts = time.time()
            jsonobj["recordTime"] = ts
            jsonobj["cognitoId"] = "eu-west-1:" + str(abs(hash(SIMIP)))
            record = {'Data': json.dumps(jsonobj),'PartitionKey':str('geoLocation')}
            records.append(record)
            
            count = count + 1
            
            if( count % (SENDTIME/0.3) == 0):
                kinesisConn.put_records(records, STREAMNAME)
                records=[]                
            end = time.time()

            if ( (end - start) < 1.0/3):
                print("we are fast - make a break")
                time.sleep( (1.0/3) - (end-start) )
                start = time.time()


	
# Testing    
#sim(header,linesACC,linesORI,linesGEO,'10.0.10.1',RUNS,REGION,STREAMNAME,RANDOMSTART)



# RUN simulation
# threaded on processors
print "Simulate "+ str(SIMPHONES) + " PHONES"
jobs = []
for i in range(SIMPHONES):
    SIMIP = SIMIPS + str(i)
    p = multiprocessing.Process(target=sim, args=(headerACC,linesACC,linesORI,linesGEO,SIMIP,RUNS,REGION,STREAMNAME,RANDOMSTART))
    jobs.append(p)
    p.start()

# check for finished jonbs
i = 1
for j in jobs:
    j.join()
    print str(i) + " Done"
    i = i + 1
     