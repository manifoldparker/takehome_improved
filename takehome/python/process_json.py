# Lambda function that will take in a JSON data structure.
# From inside the structure, it should pull out first_name, middle_name, last_name, and zip_code, and store that data in S3 bucket
# JSON structure is unknown
# Data needs to be partitioned for Glue/Athena

import json
import boto3
import logging
import datetime
import uuid

## ---- Configuration Variables ---- ##
bucket_name = "kp-manifold-working-bucket" # The AWS bucket to store the data in
output_folder = "parsed_data" # The folder where the parsed results will be saved

json_folder = "raw_data" # The folder where the raw JSON will get saved. All valid JSON input is stored here
field_names = ['zip_code','first_name', 'middle_name', 'last_name'] # the fields to extract in the parsed results

## -------- / Configuration ----------

record_id_key = 'record_id' # identifier within the parsed results for each unique entry

path_format = "%Y/%m/%d" # the dateTime format to use to create an output path to auto-partition for Athena


def save_json(raw_data: dict, path: str, record_id: uuid.UUID, s3: boto3.client):
    """
    Save the JSON data off to a file for future review

    :param raw_data: a dict representing the raw JSON data
    :param path: the path to save the data to. Data will be stored at [json_folder]/[path]/[record_id].json
    :param record_id: a UUID to represent this record, tied to the parsed data
    :param s3: the S3 instance to write the data to
    :return the path that the data is saved to
    """
    file_name = record_id + ".json"
    lambda_path = json_folder + "/" + path + "/" + file_name
    logging.info("Writing raw json data to " + lambda_path)

    # write the json to the file
    s3.put_object(Bucket=bucket_name,
                  Key=lambda_path,
                  Body=json.dumps(raw_data))

    return lambda_path


def save_data(data_dict: dict, path:str, s3: boto3.client):
    """
    Saves the provided data_dict off on S3

    :param data_dict: a dict representing the data to save off, which must contain an entry for [record_id_key]
    :param path: the path to save the data to. Data will be stored at [json_folder]/[path]/[record_id].json. Record ID is pulled from the data_dict
    :param s3: the S3 instance to write the data to
    :return: the path that the data is saved to
    """
    file_name = data_dict[record_id_key]  + ".json"
    full_path = output_folder + "/" + path + "/" + file_name
    logging.info("Writing processed data to" + full_path)
    logging.debug("Writing data: " + repr(data_dict))

    # write the json to the file
    s3.put_object(Bucket=bucket_name,
                  Key=full_path,
                  Body=json.dumps(data_dict))

    return full_path


def parse_data(data: dict):
    """
    Parses a supplied dictionary to find the fields as specified in field_names

    :param data:
        the dictionary to parse
    :return:
        int: a count of the number of fields found from field_names
        dict: a dictionary containing the parsed data
    """
    # create the output data dict
    output_dict = dict.fromkeys(field_names, "")
    res_count = 0  # count the number of fields we find

    # search the data
    for field in field_names:
        results = find_field(field, data)
        if not results:
            results = ""
        output_dict[field] = results
        if output_dict[field]:
            res_count += 1

    # generate an ID to map the raw data to
    record_id = str(uuid.uuid4())
    output_dict[record_id_key] = record_id

    return res_count, output_dict


def find_field(field_name: str, data: dict):
    """
    Recursively searches the provided data dict to find the given field name. Returns the first instance found

    :param field_name: the key to search for in the supplied dictionary
    :param data: the dictionary of data to search
    :return:
        str: the resulting value, or None if not found
    """
    if isinstance(data, dict): # if the data supplied is iterable, iterate on it
        for k,v in data.items():
            if k == field_name: # if we've found our key, return the value
                if isinstance(v, list):
                    return v[0]
                else:
                    return v
            if isinstance(v, dict): # if our value is another dict, recurse, and return the recursion results
                result = find_field(field_name, v)
                if result:
                    return result


def lambda_handler(event, context):
    """
    An event handler that accepts an event, parses it out for expected fields, and saves the data off to an S3 bucket

    This function takes data in on the AWS event, which its expecting to receive a JSON-formatted dict. The function parses
    through the input to find the first_name, middle_name, last_name, and zip_code keys, which it then saves off to S3,
    along with the raw data for future analysis. If it finds even one of the fields, it will return a code 200, and the
    data that it found. If it does not find any of the fields, it returns a code 400.
    """
    #data = event['data']
    data = event

    curr_time = datetime.datetime.now()
    s3 = boto3.client('s3')

    # parse out the data
    res_count, output_dict = parse_data(data)
    
    path = curr_time.strftime(path_format)

    # if we find no values, exit here, return 400
    if res_count == 0:
        path = "unprocessed/" + path

        # as long as the JSON loads, we're going to store it for review later
        json_path = save_json(data, path, output_dict[record_id_key], s3)

        return {
            'statusCode': 400,
            'body': json.dumps("No fields found. Raw data is stored at " + json_path)
        }

    # otherwise, save off the data
    out_path = save_data(output_dict,  path, s3)
    json_path = save_json(data, "processed/" + path, output_dict[record_id_key], s3)

    # report success
    return {
        'statusCode': 200,
        'body': json.dumps({"data":output_dict, "path": out_path})
    }

if __name__ == "__main__":
    print("Hello world")