import time
import glob
import sys
import os
import boto3
import configparser


# Read config file
config = configparser.ConfigParser()

# Get config file path from command line argument
config.read(sys.argv[1])
#/home/ec2-user/config.ini

# CloudWatch constants
LOG_GROUP = config['DEFAULT']['LogGroup']
LOG_STREAM = config['DEFAULT']['LogStream']

# CloudWatch variables
sequence_token = ''
log_event_timestamp = ''
log_event_message = ''

# Computation variables
log_file_path = config['DEFAULT']['LogFilePath']
log_data = ''

# Get timestamp for logEvent
log_event_timestamp = int(round(time.time() * 1000))

# Get latest log file
list_of_files = glob.glob(log_file_path)
latest_file_path = max(list_of_files, key=os.path.getmtime)

# Read latest log file
with open(latest_file_path, 'r') as f:
    log_data = f.read()
	
log_event_message = log_data

logs = boto3.client('logs', region_name=config['DEFAULT']['RegionName'])
response = logs.describe_log_streams(
    logGroupName = LOG_GROUP,
	logStreamNamePrefix = LOG_STREAM,
	orderBy = 'LogStreamName',
	descending = True,
	limit = 1
)


# Post log to an existing Log Stream using uploadSequenceToken
if len(response['logStreams']) > 0 and response['logStreams'][0] and 'uploadSequenceToken' in response['logStreams'][0]:
	sequence_token = response['logStreams'][0]['uploadSequenceToken']
	response_log_events = logs.put_log_events(
	    logGroupName = LOG_GROUP,
		logStreamName = LOG_STREAM,
		sequenceToken = sequence_token,
		logEvents=[
		    {
			    'timestamp': log_event_timestamp,
				'message': log_event_message
		    }
		]
	)
else:
    # Create Log Stream if it is not available
	if len(response('logStreams')) == 0:
		response_log_stream = logs.create_log_stream(
		    logGroupName = LOG_GROUP,
			logStreamName = LOG_STREAM
		)
		
	# Post log to a new Log Stream
	response_log_events = logs.put_log_events(
	  logGroupName = LOG_GROUP,
	  logStreamName = LOG_STREAM,
	  logEvents = [
	     {
		     'timestamp': log_event_timestamp,
			 'message': log_event_message
		 }
	  ]
	)
