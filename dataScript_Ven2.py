# -*- coding: utf8 -*-
import json
import requests
import gspread
from lxml import etree
from apscheduler.schedulers.blocking import BlockingScheduler
from oauth2client.service_account import ServiceAccountCredentials

sched= BlockingScheduler()

@sched.scheduled_job('interval', minutes=5)
def main():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name('SechSniff-85664333b67c.json', scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("dataScript_ven2").sheet1

    result = requests.get("http://218.161.81.10/app/sub4.asp?T1=VAN02")
    result.encoding='utf-8'
    root = etree.fromstring(result.content, etree.HTMLParser())
    data_list=[]

    #split string from caption
    venRowData = root.xpath("//section/table[@class='table1']/caption/text()")
    ven =venRowData[0]
    ven =ven.split('(')
    time =ven[1].split(')')

    # add ven and time
    #jsonData = "["
    #venInfo ='{"ven":"'+ven[0]+'","time":"'+time[0]+'",'
    #jsonData +=venInfo
    
    #formate the time and date
    data_list=[]
    time_tmp=[]
    afternoonTime =12
    HTime_tmp =""
    time =time[0].split(' ')
    if time[1] == "下午":
        time_tmp =time[2].split(':')
        afternoonTime +=int(time_tmp[0])
        time_tmp[0] =str(afternoonTime)
        #print(time_tmp)
        for hms in time_tmp:
            HTime_tmp += hms + ":"
        #print(HTime_tmp[0:-1])
        time[2] =HTime_tmp[0:-1]
    elif time[1] == "上午":
        print(time)
    data_list.append(time[0])
    data_list.append(time[2])
    

    rowCounter =2
    for row in root.xpath("//section/table[@class='table1']/tbody/tr[position()>1]"):
        column = row.xpath("./td/text()")
        #tmp= '"%s":"%s",' % (column[0], column[1])
        data_list.append('%s' % (column[1]))
        #sheet.update_cell(1, rowCounter,'%s' %(column[0]))
        #sheet.update_cell(2, rowCounter,'%s' %(column[1]))
        #rowCounter += 1
        #jsonData += tmp
    #sheet.resize(1)
    sheet.append_row(data_list)
    # delete last ','
    #print(jsonData[0:-1] + '}]')
    #print(str(data_list)[1:-1])

if __name__ == "__main__":
    main()

sched.start()
