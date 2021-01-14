Harkirat Rakhra 

The s3 interface provides a linux like shell interface for amazon s3. 

SUPPORTED COMMANDS:
login - used to verify amazon credentials, must be logged in to run the commands 
ls - used to list files and directories. ls -l will also work.
pwd - displays working directory in bucket 
cp - used to copy files and directories across or within buckets
mv - used to move files and directories across or withing buckets
rm - used to remove files and directories
login - will parse the config file and create a s3 session
upload - upload files or directories to s3 bucket
download


PYTHON MODULES:
boto3, configparser, os, csv, sys, prettytable

HOW TO RUN: 
Place your aws credentials into the config file.
In the root directory install the above dependencies, and run python3 awsS3Shell.py
