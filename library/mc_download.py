import requests
import json
import csv
import pandas as pd

STATUS = ["subscribed", "unsubscribed", "cleaned"]

def download_csv_contact(contact_id, apikey, file_name, status):
    data = {
        "apikey" : apikey,
        "id": contact_id,
        "status": status,
    }
    server_id = apikey.split("-")[-1]
    response = requests.post("https://" + server_id +  ".api.mailchimp.com/export/1.0/list/", data=data)
    json_data = [json.loads(s) for s in response.text.strip().split("\n")]
    with open('MC_DATA\\'+file_name,'w',encoding="utf-8") as result_file:
        wr = csv.writer(result_file, dialect='excel')
        wr.writerows(json_data)

'''
A cell to query sub,unsub,cleaned on MC
'''

def download_mc_db(apikey, list_id):
    server_id = apikey.split("-")[-1]
    response = requests.get("https://" + server_id +  ".api.mailchimp.com/3.0/lists/", auth=("someone", apikey))        

    count = 0
    fieldnames = ["list_name", "no. subscribers", "no. unsubscribers", "no. cleaned users"]
    row = []

    for status in STATUS:
        download_csv_contact(list_id, apikey, "db" + "_"+status+".csv", status)                
        

            
    data = pd.DataFrame(row, columns=fieldnames)
    


def read_mc_db():
    # Read Data from customer
    mylist = []
    for chunk in  pd.read_csv('MC_DATA\\db_subscribed.csv', sep=',', chunksize=20000,error_bad_lines=False,low_memory=False):
        mylist.append(chunk)
    mc_sub = pd.concat(mylist, axis= 0)
    mc_sub = pd.DataFrame(mc_sub)

    # Read Data from customer
    mylist = []
    for chunk in  pd.read_csv('MC_DATA\\db_unsubscribed.csv', sep=',', chunksize=20000,error_bad_lines=False,low_memory=False):
        mylist.append(chunk)
    mc_unsub = pd.concat(mylist, axis= 0)
    mc_unsub = pd.DataFrame(mc_unsub)

    # Read Data from customer
    mylist = []

    for chunk in  pd.read_csv('MC_DATA\\db_cleaned.csv', sep=',', chunksize=20000,error_bad_lines=False,low_memory=False):
        mylist.append(chunk)
    mc_cleaned = pd.concat(mylist, axis= 0)
    del mylist

    mc_cleaned = pd.DataFrame(mc_cleaned)

    mc_sub = pd.DataFrame(mc_sub['Email Address'],columns=['Email Address'])
    mc_sub['status']  = 'sub'

    mc_unsub = pd.DataFrame(mc_unsub['Email Address'],columns=['Email Address'])
    mc_unsub['status']  = 'unsub'

    mc_cleaned = pd.DataFrame(mc_cleaned['Email Address'],columns=['Email Address'])
    mc_cleaned['status']  = 'cleaned'
    db=pd.concat([mc_sub,mc_unsub,mc_cleaned], ignore_index=True)
    db['Email Address'] = db['Email Address'].str.lower()
    db['Email Address'] = db['Email Address'].str.strip()
    db = db.rename(columns={"Email Address": "Email"})
    return db