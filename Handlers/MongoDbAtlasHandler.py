from pymongo.mongo_client import MongoClient
import urllib
from Handlers.Credentials import USERNAME, PASSWORD

uri = "mongodb+srv://" + urllib.parse.quote(USERNAME) +":" + urllib.parse.quote(PASSWORD) +"@cluster0.pitbuhr.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client.get_database("job_listings_from_indeed_com")
records = db.listing

def connectionStatus():
  try:
    client.admin.command('ping')
    return True
  except:
    return False


def readData():
  return list(records.find())


def pushOneData(filteredData):
  try:
    if connectionStatus() and records.insert_one(filteredData):
      return True
    else:
      return False
  except:
    return False
    
def pushManyData(filteredData):
  try:
    if connectionStatus() and records.insert_many(filteredData):
      return True
    else: 
      return False
  except:
    return False


def deleteEntry(toBeDeletedData):
  records.delete_one(toBeDeletedData)
  return True
  
def updateData(old, new):
  try:
    if connectionStatus() and records.update(old, { "$set": new }):
      return True
    else: 
      return False
  except:
    return False
