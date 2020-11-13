# mc_automation_tool

## How To Install
1) Python
Ensure you have Python version 3.6 or later. Kindly visit https://www.python.org/ and download Python version 3 on your system.

2) Clone the the project with git or simply download the code

3) Install dependencies for our program
> pip install -r requirements.txt

## How to Use

#### Preclean tool

First, we need to provide credentials. Kindly open the file .env_example, copy and paste in to a new file ".env" at the same root directory. Then please change the information accordingly.

You also need to have 2 folder: input and output.

In the input folder, place the data in csv or excel format (xlsx, xls). Then open the file mc_automation.py, change the constant NEW_DATA to the name of the new data file.

Open our VPN connection and run 

> python mc_automation.py

The results will be found the output folder.