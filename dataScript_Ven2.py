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
    sheet = client.open("201802_dataScript_ven2").sheet1

    result = requests.get("http://218.161.81.10/app/sub4.asp?T1=VAN02")
    result.encoding='utf-8'
    root = etree.fromstring(result.content, etree.HTMLParser())

    #split string from caption
    venRowData = root.xpath("//section/table[@class='table1']/caption/text()")
    ven =venRowData[0]
    ven =ven.split('(')
    time =ven[1].split(')')
    
    #formate the time and date
    data_list=[]
    time_tmp=[]
    afternoonTime =12
    HTime_tmp =""
    time =time[0].split(' ')

    #change time formate to HH:MM:SS
    if time[1] == "下午":
        time_tmp =time[2].split(':')
        afternoonTime +=int(time_tmp[0])
        time_tmp[0] =str(afternoonTime)
        #print(time_tmp)
        if time_tmp[0] == '24':
            time_tmp[0] = '12'
            #print(time_tmp[0])
    if time[1] == "上午":
        time_tmp =time[2].split(':')
        if time_tmp[0] == '12':
            time_tmp[0] = '00'

    #put time together
    for hms in time_tmp:
        HTime_tmp += hms + ":"
        #print(HTime_tmp[0:-1])
    time[2] =HTime_tmp[0:-1]
    data_list.append(time[0])
    data_list.append(time[2])
    
    for row in root.xpath("//section/table[@class='table1']/tbody/tr[position()>1]"):
        column = row.xpath("./td/text()")
        data_list.append('%s' % (column[1]))
    
    #reset sheet row to 1
    #sheet.resize(1)
    sheet.append_row(data_list)
    #print(data_list)


if __name__ == "__main__":
    main()

sched.start()
