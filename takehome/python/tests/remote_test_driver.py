"""
A test driver class that can take in a directory of sample data in CSV and JSON data and use it to send commands
to the remote server. It does minimal error checking, assuming that the data is in the format matching the extension,
and that the user has provided a valid input for the file and the remote URL
"""
import json
import csv
import requests
import logging
import sys
import time
import os

def send_request(data_list, url):
    """
    Sends a JSON request to the provided URL. 
    """
    for li in data_list:
        print("Sending", li, "to", url)
        out = requests.post(url, li)
        print(out.json())
        print('\n')
        time.sleep(1)

def parse_input(filename, url):
    """
    Parse through the provided file. Can handle directories and sub-directories, CSV, and JSON data.
    """
    print("Processing", filename, "\n")
    try:
        if os.path.isdir(filename): # if it's a directory
            files = os.listdir(filename)
            for file in files:
                new_path = os.path.join(filename,file)
                parse_input(new_path, url)
            return

        # check for known file extensions
        file, ext = os.path.splitext(filename)
        if ext == ".json": 
            parse_json(filename, url)

        elif ext == ".csv":
            parse_csv(filename, url)

        else: # otherwise, log and move on
            print("Not a supported file: " +filename+ "\n")
    except:
        print("Unexpected error:", sys.exc_info()[0])

def parse_json(json_file, url):
    """
    Reads in a JSON file and sends the contents directly to the remote server
    """
    with open(json_file) as file:
        data = file.read()
        send_request([data], url)

def parse_csv(csv_file, url):
    """
    Parses a CSV file, and pulls out all of the relevant fields, then passes it to the remote server
    """
    rows = []
    with open(csv_file) as file:
        reader = csv.DictReader(file)
        for row in reader:
            parsed_row = {}
            for k, v in row.items():
                parsed_row[k.strip()] = v.strip()
            data = {"data":parsed_row}
            data_str = json.dumps(data)

            rows.append(data_str)

    # send a set of requests
    send_request(rows, url)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: test_driver.py <filename> <url>")
        exit(-1)

    file = sys.argv[1]
    url = sys.argv[2]
    parse_input(file,url)