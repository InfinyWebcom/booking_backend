import boto3


# Creating the low level functional client
s3_client = boto3.client("s3")

# Creating the high level object oriented interface
s3_resource = boto3.resource("s3")
