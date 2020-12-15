# Overview
This package contains a script and deployment tools for an AWS Lambda function which, when deployed, allows the user to send JSON via POST request, which the script will then search for and extract the following fields:
* Zip Code (zip_code)
* First Name (first_name)
* Middle Name (middle_name)
* Last Name (last_name)

If successful, the function will return a code 200, and JSON data that shows the fields which were extracted, as well as the save location on Amazon S3 for the extracted data. If none of the fields are found, the function will return 400, and the location where the uploaded JSON data was stored for review.

This package is deployed using Terraform, which automatically configures several services, as follows:
* Creates a Lambda function using the script in /python/process_json.py
* Creates an Gateway configuration to allow the script to be queried via a POST command
* Creates an S3 bucket for the Lambda function and Athena to write to
* Creates a Glue crawler that crawl the output of the Lambda function
* Creates an Athena workgroup and saved query to interact with the output of the crawler

The package contains a script for testing the data upload, in /python/tests, but the script does not currently test the full workflow, from data upload to Athena query.

## Assumptions
The Python code reads in a JSON file, and looks for the above specified fields. It makes the following assumptions about the data:
* Only one person is in each file
* The first instance of each field will be treated as the cannonical instance
* The fields all map to a string or an array

## Package Layout
* /python - holds the python lambda script and unit tests
    * /python/tests - holds the unit tests, and an automated script to send bulk data to the API once loaded
* /terraform - holds the terraform configuration environment. Terraform initiation should be run from within this folder.
* /test_data - holds a variety of test data, primarily to supply the remote_test_driver.py script, but the data within test_data/output_data can also be uploaded directly to AWS S3 to test the crawler.

# Setting up the environment

## Pre-requisites
* Terraform installed, on your Path, and configured with your AWS credentials
    * This package was developed against v0.13.3
* To run the test script, you will need at least Python 3.7
    * The script also depends on the following libraries, which can be installed via pip:
        * requests (https://requests.readthedocs.io; tested with version 2.24.0)
        * boto3 (https://github.com/boto/boto3; tested with version 1.15.1)

## Configuration

### Common Configuration
Both the python script and terraform support configuring the AWS bucket and the folder that the scripts write to and the Glue crawler will read from. The python script and the terraform variables need to be configured in their respective files to point to the same locations.

The relevant variables are:

* AWS Bucket:  
    * Python: python/process_json.py -> bucket_name  
    * Terraform: terraform/terraform.tfvars -> bucket_name  
* Glue processing folder:  
    * Python: python/process_json.py -> output_folder  
    * Terraform: terraform/terraform.tfvars -> glue_folder  

## Python Configuration
The Python script additionally supports the following configurations:

* json_folder:  
    * The script will log all inputs to this folder. This is not currently connected to a Glue script but is retained for logging purposes. Output is written to json_folder/processed or json_folder/unprocessed depending on if the data was sucessfully parsed or not.
* field_names:  
    * This is the string list of fields that the parser searches for to extract into the processed data. 

## Terraform Configuration
The Terraform variable file additionally supports the following configurations:

* availability_zone: 
   * This is the AWS zone that all services will be deployed to.
* destroy_resources:
    * This configuration parameter determines if the S3 bucket and Athena Working Group will be destroyed even if it contains data (true) or preserved, even on a terraform destroy command (false).

## Creating the environment
Once all configuration is complete, you can open up a command prompt in the terraform folder, and run:

> terraform init

> terraform apply

When terraform is finished running, it outputs the URL for the API gateway for your reference.

# Testing the Environment
## Unit Tests
The python function has two unit test files, which can be run directly from within the python/tests folder:
* test_find_field.py
* test_parse_data.py

These scripts test the major offline functionality of the process_json script, and do not require external configuration to run. They can be run from within the python directory by calling:
> python -m unittest tests.\[modulename\]

or all tests can be run by calling:
> python -m unittest discover -s tests

There should be 25 unit tests, which all pass.

## Testing the API Gateway
The python/tests directory includes a test script for driving bulk uploads to the lambda function. The script is invoked by calling:

> python python/tests/remote_test_driver.py \[path\] \[Gateway URL\]

The Gateway URL is the URL output by the terraform script.

The path can be to a JSON or CSV file, or a directory containing those. The script will recurse through the directory and load any JSON or CSV files in the directory, parse and format them, and send them to the supplied URL.

Once the script has finished running, you can check the results on the S3 bucket. It should save all the JSON formatted raw data as well as JSON formatted parsed data on the server. If all the configuration is done as described above, the Glue crawler will be pointed to read the output of the script and can be run now to populate the database.

## Testing Glue and Athena
The Glue crawler is configured to point at the bucket as defined in the above configuration. That bucket and folder can be populated manually for testing purposes using the data in test_data/output_data or by running the remote_test_driver script. Both should produce partitioned data. The test data is in CSV format, while the script produces JSON data, but the crawler will work on either.

The Glue crawler is configured to run on demand and can be run by logging into the Glue console and running the "kp_manifold_crawler" and waiting for it to finish.

When the crawler has finished, the results can be verified by logging into the Athena console, where the crawler will have created/updated the kp_manifold_interview database, and created a table matching the name of the Glue folder configured for Terraform.

The Terraform configuration will have created a workgroup (kp_manifold_wg) and a saved query (kp_address_book_query) which will load up to 30 entries in the table that Glue has configured. This workgroup is also configured to output its results to the same S3 bucket that the rest of the data is in.

# System Design 

## Design Decisions 
### Terraform Vs. Cloud Formation
As this is an exclusively AWS deployment, both Terraform and CloudFormation are valid tools to automate the infrastructure deployment for this project. Terraform was chosen as the deployment tool for several reasons.

1. Support for modular development - as this project configures multiple different AWS services, Terraform's ease of segmenting out each service into seperate configuration files simplifies the conceptual overhead of creating the system.
2. Readability - the Terraform configuration language (HCL) is more human-readable, and easier to reason over what it does. While CloudFormation abstracts away some of the AWS detail, it also hides the configutation information, so Terraform is easier to read and understand exactly what is happening.
2. Support for a broader array of services - while this entire package is using AWS, Terraform supports a broader range of services than the AWS exclusive CloudFormation. Given that either service would be learned from the ground up, I chose the tool that had a broader utility.


### Testing decisions
The majority of the testing of the parser script is done through unit testing, with only relatively basic verification being done via the test driver script. This was done for a few reasons:

1. Ease of iteration for fixes - running the tests locally speeds up the iteration process of bugfixing, as it eliminates the networking delay necessary for sending and reciving the data from the remote endpoint. Additionally, the Terraform script is not capable of detecting a change in the local script as a reason to update the remote configuration, which means that updating the remote script must be done manually, or through a more invasive reconfiguration of the system.
2. Ease of configuration and version control - by running all tests locally, it avoids the risk of making iterative changes in the Lambda console, which have to be manually pulled back down into the offline version. 
3. Support for regression testing - automated unit tests allow a standardized set of tests which can be run after every major change, verifying no loss of functionality, and can, if necessary, be easily tied into a more significant build and test infrastructure. 

The test driver script exists to automate the process of bulk uploading data to the lambda function while the remote server. It's purpose is to test the portions of the functionality that cannot be tested in a wholly offline manner, and is not set up for any sort of automated verification. As its primary purpose is to automate a tedious upload task, automated verification was not deemed to be a priority.

### Output Data Format
As can be inferred from the data in the test_data folder, both CSV and JSON outputs were explored for this project. The final product outputs JSON primarily for simplicity of writing to the S3 bucket. Partitioning allows for a relatively straighforward mapping of raw data to parsed data via UUID, and does not add the additional overhead of needing to read, update, and overwrite a CSV file. 

# Room for Growth
There are a number of ways that this script and deployment could be further improved beyond what has been deployed here. What follows is a few specific places that this service could grow.

## Supporting multiple entries in the input json
Currently, the script assumes that there will only be one person in any given JSON file, and therefore terminates when it finds the first instance of any given field in the supplied data. However, the script could be updated to search for multiple entries within the JSON with some effort.

The current script has a simple assumption - there is one person, and all of the data pulled out is assigned to that person, regardless of level within the JSON. Adding the expectation would require a new set of assumptions, trading of potential fidelity vs. complexity. The following questions would need to be answered in order to implement this functionality:

* When do you create a new "person" record when parsing the JSON?
    * This can be implemented as simply as returning a list of all matching fields within the inported data, and each entry in the list becomes a new person.
        * Given a source where the parser returns a list of {"middle_name": "June","Anne","Mike"} and {"first_name": "Lisa", "Steve"}, we would create entries for {"first_name":"Lisa", "middle_name":"June"}, {"first_name":"Steve", "middle_name":"Anne"}, and {"middle_name":"Mike"}
    * A more intelligent approach, which would require more code refactoring, could instead chose to reset on either a specific field (i.e. "first_name") or upon field repeat. This adds more code complexity, as each field will have to be searched for iteratively until all fields are found, but is more likely to produce a result that matches the source data.
        * Given a source json that had {"data": {"first_name":"June", middle_name:"Anne", "child":{"first_name":"Mike", "middle_name":"Steve"}, "last_name":"Brown"}}, we would create entries for {"first_name":"June", "middle_name":"Anne"} and {"first_name":"Mike", "middle_name":"Steve", "last_name":"Brown"}
    * A third option would be to assume some amount of structure for the source JSON, and build individual entries out of fields that are at the same or lower levels of the first field found.
        * Given a source JSON that has { "person": {"first_name": "Jane", "last_name": "Doe", "resident_data": {"zip_code": 12345}, "middle_name": "maryanne"} }, we would create entries for {"first_name":"Lisa", "last_name":"Doe", "zip_code":12345} and {"middle_name":"maryanne"}
        * Given a source JSON that has {"data": {"first_name":"June", "middle_name":"Anne", "child":{"first_name":"Mike", "middle_name":"Steve"}, "last_name":"Brown"}}, we would create an entry for {"first_name":"June", "middle_name":"Anne", "last_name":"Brown"}
    * The above examples intentionally show edge cases, and more complicated logic can handle more of the edge cases, so multi-person parsing will need to trade of potential fidelity vs. complexity.
* How to store and relate the data? 
    * The current implementation creates a UUID for each entry, and relates that entry back to the raw JSON, which is also stored remotely. Adding a many-to-one relationship would complicate that scheme. The simplest answer is to create a record that maps the raw to parsed data, where a record contains all of the people parsed. However, this would be a good time to revisit the CVS vs. JSON output decision, as well as making smarter choices of what to do with the currently unused data.

## What to do with the rest of the data?
The current implementation does very little with the extra data it is provided beyond storing it for future reference. This provides some basic utility, allowing troubleshooting of the script, and the potential to use Glue to perform further ETL on the stored data. However, given that the expectation is that incoming JSON data formats are both unknown and will vary, using Glue to simply create tables from the data is of limited usefulness.

There are a few things we could do with the remaining data that we bring in:
* Extract and record keys and structure - saving of the structure of the supplied JSON, independent of the full data, would allow us to look for trends in the JSON formats, which could be used as an input to design decisions for a multi-name implementation.
    * At its simplest, just saving off the keys would allow us to find other data which is regularly being supplied, and analyze that for additional usefulness.
    * Saving off the more complicated structure can be used for optimizations, if the supplied JSON is regularly very complex, and for inferring structure in the future.
* Flatten the supplied JSON to create data that more easily loads into a database table, to allow us to analyze trends in the data. Although this would cost us potential fidelity in the supplied data (as it would remove duplicate keys in the same way that the current load only takes the first entry), it nonetheless enables the analysis of other data through structured querying.

# Unifying the Python and Terraform configuration
As a simple quality-of-life improvement, there is room for simplifying the configuration and deployment of the Python and Terraform configurations. Right now, they need to be configured seperately, a process which is vulnerable to copy/paste errors. A deployment script which reads from a common configuration file would simplify the process, and minimize the risk of errors.

# Automating a full, end to end test script from the client
The current remote driver only supports one part of the full processing chain - the uploading of multiple JSON objects. For a more robust testing infrastructure, that script could be updated to run the full processing chain, from uploading supplied data, to running the crawler and the Athena query, to verify that the results are as expected.