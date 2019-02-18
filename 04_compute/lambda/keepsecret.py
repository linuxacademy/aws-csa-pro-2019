from __future__ import print_function

import json
import boto3

print('Loading function')

s3 = boto3.client('s3')

bucket_of_interest = "secretcatpics"

# For a PutObjectAcl API Event, gets the bucket and key name from the event
# If the object is not private, then it makes the object private by making a
# PutObjectAcl call.
def lambda_handler(event, context):
	# Get bucket name from the event
	bucket = event['Records'][0]['s3']['bucket']['name']
	if (bucket != bucket_of_interest):
		print("Doing nothing for bucket = " + bucket)
		return
	
	# Get key name from the event
	key = event['Records'][0]['s3']['object']['key']
	
	# If object is not private then make it private
	if not (is_private(bucket, key)):
		print("Object with key=" + key + " in bucket=" + bucket + " is not private!")
		make_private(bucket, key)
	else:
		print("Object with key=" + key + " in bucket=" + bucket + " is already private.")
	
# Checks an object with given bucket and key is private
def is_private(bucket, key):
	# Get the object ACL from S3
	acl = s3.get_object_acl(Bucket=bucket, Key=key)
	
	# Private object should have only one grant which is the owner of the object
	if (len(acl['Grants']) > 1):
		return False
	
	# If canonical owner and grantee ids do no match, then conclude that the object
	# is not private
	owner_id = acl['Owner']['ID']
	grantee_id = acl['Grants'][0]['Grantee']['ID']
	if (owner_id != grantee_id):
		return False
	return True

# Makes an object with given bucket and key private by calling the PutObjectAcl API.
def make_private(bucket, key):
	s3.put_object_acl(Bucket=bucket, Key=key, ACL="private")
	print("Object with key=" + key + " in bucket=" + bucket + " is marked as private.")
