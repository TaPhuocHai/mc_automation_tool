from library.choose_account_from_hi import main as choose_account
# from library.async_semaphore import *
from dotenv import load_dotenv
from halo import Halo
from codetiming import Timer
from bs4 import BeautifulSoup
import pandas as pd 
import time
import os
from test_platform import *
import requests
# Default directories where input and output data located
from library.mc_download import *

load_dotenv()

INPUT_DIR_NAME = 'input'
OUTPUT_DIR_NAME = 'output'

# Caution: Remember to open VPN before running this program

# Constants, global variables
# NEW_DATA represent the data we want to check quality and do cleaning up
# You should have such file in input directory
NEW_DATA = "" # you should change name accordingly, excel or csv is okay!

# Credentials
CSE_EMAIL = os.getenv("CSE_EMAIL") 
CSE_PASSWORD = os.getenv("CSE_PASSWORD") 
DV_API_KEY = os.getenv("DV_API_KEY")
HIIQ_API_KEY = os.getenv("HIIQ_API_KEY")
HIIQ_URL = os.getenv("HIIQ_URL")

def clean_data(current_users):
    global NEW_DATA

    file_name, file_extension = os.path.splitext(NEW_DATA)
    file_extension = file_extension[1:]
    
    if file_extension == 'csv':
        new_user_data = pd.read_csv(INPUT_DIR_NAME + '/' + NEW_DATA)
    elif file_extension == 'xlsx' or file_extension == 'xls':
        new_user_data = pd.read_excel(INPUT_DIR_NAME + '/' + NEW_DATA)
    else:
        return -1, "error: file_extention is not supported: " + file_extension
    
    # check email header exist
    is_no_email_header = True
    email_header = None
    
    for header in list(new_user_data.columns):
        formatted_header = header.lower().strip()
        if formatted_header.find("mail") > -1:
            email_header = header
            is_no_email_header = False
            break
    
    if is_no_email_header is True:
        return -1, "error: no email header/column found in your file " + NEW_DATA
    
    new_emails = new_user_data[email_header] #E-Mail or Email
    new_emails = new_user_data.rename(columns={email_header: "Email"})['Email']
    print("Number of users in the new file: ", len(new_emails))    
    # new_emails.sort_index(inplace=True)
    new_emails = new_emails.str.lower()
    new_emails = new_emails.str.strip()
    new_emails.drop_duplicates(keep="last", inplace=True)
    print("Number of users after dedup: ", len(new_emails))
    new_emails.to_csv(OUTPUT_DIR_NAME + "/" + file_name + "_removed_dup.csv", header=True, index=False)

    """get current existing users"""
    current_users['Email'] = current_users['Email'].str.lower()
    current_users['Email'] = current_users['Email'].str.strip()
    merged = current_users.merge(new_emails, how="right", indicator=True)
    merged.to_csv(OUTPUT_DIR_NAME + "/" + file_name + "compared_with_currentdb.csv", index=False, columns=["Email", "status"])

    new_users = merged[merged['_merge']=='right_only']
    existing_sub = merged[merged['status']=='sub']
    existing_unsub = merged[merged['status']=='unsub']
    suppressed = merged[merged['status']=='excluded']

    existing_sub.to_csv(OUTPUT_DIR_NAME + "/" + file_name + "_existing_sub.csv", index=False)
    
    print("Number of new users: ", len(new_users), end=", ")
    print("along with %s existing sub, %s unsub, %s cleaned users" %(len(existing_sub), len(existing_unsub), len(suppressed)))
    
    new_users = pd.DataFrame(new_users['Email'])
    new_users.to_csv(OUTPUT_DIR_NAME + "/" + file_name + "_new_users.csv", index=False)
    sample_bad_emails = pd.read_csv("bad_emails.csv")
    new_users['Domain'] = new_users['Email'].str.split('@').str[1]
    merged = sample_bad_emails.merge(new_users, how="right", indicator=True, on="Domain")
    good_emails = merged[merged['_merge']=='right_only']
    print("Number of user after remove blacklisted domain: ", len(good_emails))
    good_emails = good_emails['Email']
    good_emails.to_csv(OUTPUT_DIR_NAME + "/" + file_name + "_to_cse2.csv", index=False, header=True)
    bad_emails  = merged[merged['_merge']=='both']
    bad_emails.to_csv(OUTPUT_DIR_NAME + "/" + file_name + "_blacklisted.csv", index=False, header=True, columns=["Email", "Domain"])


if __name__ == "__main__":
    # turn on vpn
    
    ""
    connectVPN()
    time.sleep(10)
    # Select account    
    env_file = open(".env", mode="r")
    env_data = env_file.readlines()    
    exit_code, account = choose_account(HIIQ_API_KEY, HIIQ_URL)
    if exit_code == -1:
        exit(code=-1)

    api_key, default_list_id = account['api_key'], account['default_list_id']
    # turn off vpn
    disconnectVPN()


    # ## Fetching the contacts    
    t = Timer(name="class", text="Time to fetch the contacts: {seconds:.1f} seconds")
    spinner = Halo(text="Fetching contacts via API ..", spinner='dots', text_color="grey")
    spinner.start()        
    t.start()
    
    download_mc_db(api_key, default_list_id) # Disable this if don't want to re-fetch

    spinner = spinner.succeed(text="Downloaded all contacts")
    t.stop()

    spinner.start("Processing the data")
  
    
    mc_data = read_mc_db()
    clean_data(mc_data)

    spinner.succeed(text="Done processing the data")
    spinner.succeed("Program completed!")

    # This block can be commented/removed if you don't want to connect VPN again
    print("Reconnecting to VPN again")
    connectVPN()
