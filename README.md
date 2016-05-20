# aws-tag-management

These sets of Python classes and scripts aid with managing configuration and tagging of an AWS account.

Requirements
------------
- Python 2.7
- [Boto3](https://github.com/boto/boto3)


Installation
------------

Run `setup.py install`

Usage
------------
Configure AWS credentials in any fashion supported by boto3. Classes can be imported via:

    import AwsResources


AwsTags
------------
The following tagged resources are currently supported:
- Data Pipelines
- Elastic Load Balancers (ELB)
- EC2 Instances
- EC2 Spot Instance Requests
- EC2 Volumes
- Elastic Map Reduce Clusters (EMR)
- Glacier
- Kinesis
- Redshift
- Relational Database Service (RDS)
- Simple Storage Service (S3)
