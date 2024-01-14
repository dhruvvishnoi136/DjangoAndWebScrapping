import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from Handlers.MongoDbAtlasHandler import readData, connectionStatus, pushOneData, deleteEntry, updateData
import re
# Home Page
def index(request):
  return render(request, "index.html")

# To Filter Data in Post Request
def postFilter(str):
  return re.sub(r""""_id":\sObjectId\("\S*"\),""", "", str.replace('\'',"\""))

# Function to Modify (Fetch, Delete, Update) Data from Mongodb Atlas
def fetchDatabase(request):
  if request.method == 'POST':
    postData = ((request.POST).dict())
    if postData['action'] == "delete":
      if deleteEntry(json.loads(postFilter(postData['dataHolder']))):
        dataDictionariesArray = readData()
        return render(request, "DataView.html",{'parsedData':dataDictionariesArray})      
      else:
        return HttpResponse("Something Went Wrong! Try Deleting Again")

    elif postData['action'] == "update":
      return render(request, "UpdateView.html", {'parsedData': (json.loads(postFilter(postData['dataHolder'])))})
      
    elif postData['action'] == "updateFinal":
      oldData = json.loads(str(str(postData['oldData']).replace('\'','\"')))
      newData = {'JobTitle' : request.POST['JobTitle'], 'Salary' : request.POST['Salary'], 'CompanyDetail' : request.POST['CompanyDetail'], 'JobDesc' : request.POST['JobDesc'], 'JobReq' : request.POST['JobReq']}
      if updateData(old = oldData, new=newData):
        return HttpResponseRedirect("/")
      else:
        return HttpResponse("Something Went Wrong")

    else:
      return HttpResponse("Something Went Wrong")

  else:
    if connectionStatus():
      dataDictionariesArray = readData()
      return render(request, "DataView.html",{'parsedData':dataDictionariesArray})
    else:
      return HttpResponse("Something Went Wrong")

# Function to Add Value
def insertDataView(request):
  if request.method == 'GET':
    if len(request.GET) == 0:
      return render(request, "AddData.html")
    elif request.GET['JobTitle'] != '' and request.GET['Salary'] != '' and request.GET['CompanyDetail'] != '' and request.GET['JobDesc'] != '' and request.GET['JobReq'] != '':
      filteredData = {
      'JobTitle' : request.GET['JobTitle'],
      'Salary' : request.GET['Salary'],
      'CompanyDetail' : request.GET['CompanyDetail'],
      'JobDesc' : request.GET['JobDesc'],
      'JobReq' : request.GET['JobReq']
    }
      if connectionStatus():
        if pushOneData(filteredData):
          return HttpResponseRedirect("/")
        else:
          return HttpResponse("Something Went Wrong")

      else:
        return HttpResponse("Something Went Wrong")

    else:
      return HttpResponse("Something Went Wrong")
