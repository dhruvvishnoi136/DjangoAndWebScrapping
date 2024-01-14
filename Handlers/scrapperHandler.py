import sys
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
import random
from selenium.webdriver.common.by import By
from MongoDbAtlasHandler import pushManyData
from selenium.webdriver.chrome.service import Service
from pathlib import Path
Debug = 1

def pushToDatabase(dataDictionariesArray):
  print("Pushing Data to MongoDB Atlas")
  return pushManyData(dataDictionariesArray)


def soupInstance(driverPageSource):
  return BeautifulSoup(str(driverPageSource), 'html.parser')

def filterData(JobTDs):
  print("Filtering Data")
  if len(JobTDs) == 0:
    return []
  else:
    print(f"Total Jobs Found:- {str(len(JobTDs))}")
  # Format [{JobTitle, Salary, CompanyDetail, JobDesc, JobDeq}]
  filteredDataDictionariesArray = []  
  for indexedJobBeacon in JobTDs:
    # Filtering Detail Section
    JobTitle = ""
    CompanyDetail = ""
    Salary = ""
    JobDesc = ""
    JobReq =  ""
    InnerTables = soupInstance(indexedJobBeacon).find_all("table")
    if(InnerTables[0] != None):
      JobDetail = soupInstance(InnerTables[0]).find("td", {"class":"resultContent"}).find_all("div")
      try:
        JobTitle = soupInstance(JobDetail[0]).find('h2').find('a').text # [0] h2[0] a[0] span
      except:
        JobDetail = "N/A"
        pass
      try:
        CompanyDetail = str(soupInstance(JobDetail[3]).find('span').text) +" "+ str(soupInstance(JobDetail[4].text))  # [3] span[0] ++ [4]
      except:
        CompanyDetail = "N/A"
        pass
      try:
        Salary = str(soupInstance(JobDetail[7].text)) # [7] 
      except:
        Salary = "N/A"
        pass
      try:
        JobDesc = str(soupInstance(JobDetail[9].text)) +" "+ str(soupInstance(JobDetail[11]).text)# [9] Remove Span ++ [11]
      except:
        JobDesc = "N/A"
        pass
    else:
      continue

    # Filtering Description Section
    if(InnerTables[1] != None):
      try: 
        JobDescription = soupInstance(soupInstance(InnerTables[1]).find_all('tr')[-1]).find_all('li') # tr[-1] li
        for descriptions in JobDescription:
          JobReq += str(descriptions.text)
      except:
        JobReq = "N/A"
        pass
    else:
      continue

    filteredDataDictionariesArray.append({
      'JobTitle' : JobTitle,
      'Salary' : Salary,
      'CompanyDetail' : CompanyDetail,
      'JobDesc' : JobDesc,
      'JobReq' : JobReq
    })
  return filteredDataDictionariesArray

# If Deep = 1 then scrapper iterate very page , else only first page
def scrapHandler(jobTitle:str, location:str, Deep:int = 1,os:str ="Win"):
  print("Scrapper is Running")
  jobTitle = "+".join(jobTitle.strip().split())
  location = "+".join(location.strip().split())
  url = f"https://in.indeed.com/jobs?q={jobTitle}&l={location}"
  osConfig = "\\WinChromedriver.exe"
  if(os == "Linux"):
    osConfig = "LinuxChromedriver"
  elif (os == "Win"):
    osConfig = "\\WinChromedriver.exe"
  else:
    print("OS parameter is wrong")
    exit()
  service = Service(executable_path=(str(Path(__file__).resolve().parent) + f"{osConfig}"))
  options = webdriver.ChromeOptions()
  driver = webdriver.Chrome(service=service, options=options)
  driver.maximize_window()
  JobTDs = []
  pageCounter = 0
  while True:
    driver.get(url=url)
    pageCounter+=1
    sleep(2)
    try:
      driver.find_element(By.XPATH, '//button[@class="css-yi9ndv e8ju0x51"]').click()
    except:
      pass

    last_height = driver.execute_script("return document.body.scrollHeight")
    new_height = 0
    #Scrolling till last to load whole Page
    while new_height != last_height:
        last_height = new_height
        for i in range(1, last_height):
            sleep(random.uniform(0.125,2))
            temp = i * 1000
            if temp < last_height:
                i = temp
                driver.execute_script(f"window.scrollTo(0, {i});")
            else:
                break
        new_height = driver.execute_script("return document.body.scrollHeight")


    for beacons in soupInstance(driver.page_source).find_all("div", {"class" : "job_seen_beacon"}):
      JobTDs.append(beacons)
    if Deep == 0:
      return filterData(JobTDs=JobTDs)
    else:
      finalLink =""
      nextPageButton = (soupInstance(driver.page_source).find_all('a', {'class' : 'css-akkh0a e8ju0x50'}))[-1]
      finalLink = nextPageButton['href']
      if finalLink != None and nextPageButton['aria-label'] == "Next Page":
        url = "https://in.indeed.com" + finalLink
        sleep(random.uniform(1,3))
      else:
        break
  

  # Filtering Data (Creating Tuples)
  filteredDataDictionariesArray = filterData(JobTDs=JobTDs)
  # Pushing to Database
  return pushToDatabase(filteredDataDictionariesArray)


if __name__ == "__main__":
  
  if scrapHandler(str(sys.argv[1]), str(sys.argv[2]), int(sys.argv[3]), str(sys.argv[4])):
    print("Successfully Uploaded Data")
  else:
    print("Something Went Wrong!!")