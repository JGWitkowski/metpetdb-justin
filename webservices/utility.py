from django.db import connection as con
import json


#creates JSON for facets
def getFacetJSON(query):
        cursor=con.cursor()
        print query
        cursor.execute(query)
        data=cursor.fetchall()
        jsonData=[]
        for row in data:
                dataId=unicode(row[0])
                dataLabel=unicode(row[1])
		if dataLabel=='':
			dataLabel='Missing Value'
                dataCount=unicode(row[2])
                jsonValues={}
                jsonValues['id']=dataId
                jsonValues['label']=dataLabel
                jsonValues['count']=dataCount
                jsonData.append(jsonValues)
        return json.dumps(jsonData)


#creates JSON array for all data
def getAllJSON(query):
        cursor=con.cursor()
        cursor.execute(query)
        data=cursor.fetchall()
        resultSetSize=len(data)
        jsonData=[]
        str1=''
        i=0
        while i<resultSetSize:
                jsonValues={}
                if ((i+1)!=resultSetSize) and (data[i][0]==data[i+1][0] and data[i][1]==data[i+1][1] and data[i][2]==data[i+1][2] and data[i][3]==data[i+1][3]):
                        jsonValues['id']=unicode(data[i][0])
                        jsonValues['sample_number']=unicode(data[i][1])
                        jsonValues['rock_type']=unicode(data[i][2])
                        jsonValues['owner']=unicode(data[i][3])
                        jsonValues['lat']=unicode(data[i][4])
                        jsonValues['lon']=unicode(data[i][5])

                        jsonData.append(jsonValues)
                else:
                        
                        jsonValues['id']=unicode(data[i][0])
                        jsonValues['sample_number']=unicode(data[i][1])
                        jsonValues['rock_type']=unicode(data[i][2])
                        jsonValues['owner']=unicode(data[i][3])
                        jsonValues['lat']=unicode(data[i][4])
                        jsonValues['lon']=unicode(data[i][5])
                        jsonData.append(jsonValues)
                i=i+1
               
        return json.dumps(jsonData)

#create HTML table output for results (This is currently a hack. Code must be cleaned to generate HTML when format=HTML)
def getSampleResults(query):
        cursor=con.cursor()
        cursor.execute(query)
        data=cursor.fetchall()
        resultSetSize=len(data)
        htmlData="<table id='gridData'><thead><tr><th>Sample Number</th><th>Subsamples</th><th>Analyses</th><th>Images</th></tr></thead><tbody>"
        i=0
        while i<resultSetSize:
                htmlData=htmlData+"<tr><td><a href='http://metpetdb.rpi.edu/metpetweb/#sample/"+unicode(data[i][0])+"'>"+unicode(data[i][1])+"</a></td><td>"+unicode(data[i][7])+"</td><td>"+unicode(data[i][8])+"</td><td>"+unicode(data[i][9])+"</td></tr>"
                i=i+1
        htmlData=htmlData+"</tbody></table>"

        return htmlData


