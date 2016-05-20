#
# AWS Config Tag Missing
#
# Lambda script for AWS Config to validate and notify if required tags are missing
#
# Trigger Type: Change Triggered
# Scope of Changes: EC2:Instance
# Required Parameters: tags
# Example Value: tag1,tag2,tag3
# Required Parameters: emailFrom
# Example Value: sender@example.com
# Required Parameters: emailTo
# Example Value: email1@example.com,email2@example.com


import boto3
from botocore.exceptions import ClientError
import json


def is_applicable(config_item, event):
    status = config_item['configurationItemStatus']
    event_left_scope = event['eventLeftScope']
    test = ((status in ['OK', 'ResourceDiscovered']) and
            event_left_scope is False)
    return test


def send_email(sender, to, subject, message):
    response = boto3.client('ses').send_email(
        Source=sender,
        Destination={
            'ToAddresses': to
        },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': 'utf-8'
            },
            'Body': {
                'Text': {
                    'Data': str(message),
                    'Charset': 'utf-8'
                }
            }
        }
    )


def evaluate_compliance(config_item, rule_parameters):
    if (config_item['resourceType'] != 'AWS::EC2::Instance'):
        return 'NOT_APPLICABLE'
    else:
        for tag in rule_parameters['tags'].split(','):
            if tag not in config_item.get('tags'):
                return 'NON_COMPLIANT'
        return 'COMPLIANT'

def lambda_handler(event, context):
    invoking_event = json.loads(event['invokingEvent'])
    rule_parameters = json.loads(event['ruleParameters'])
    config_item = invoking_event['configurationItem']
    compliance_value = 'NOT_APPLICABLE'

    if is_applicable(config_item, event):
        compliance_value = evaluate_compliance(config_item, rule_parameters)
        if compliance_value != "COMPLIANT":
            inst_id = config_item.get('resourceId')
            inst_tags = config_item.get('tags')
            sender = rule_parameters['emailFrom']
            to = rule_parameters['emailTo'].split(',')
            subject = "Non-compliant instance launched - {}".format(inst_id)
            message = "Instance Info:\nID: {}\nTags: {}\nEvent:\n{}".format(
                inst_id, inst_tags, json.dumps(config_item, indent=4))
            send_email(sender, to, subject, message)

    config = boto3.client('config')
    try:
        response = config.put_evaluations(
            Evaluations=[
                {
                    'ComplianceResourceType': invoking_event['configurationItem']['resourceType'],
                    'ComplianceResourceId': invoking_event['configurationItem']['resourceId'],
                    'ComplianceType': compliance_value,
                    'OrderingTimestamp': invoking_event['configurationItem']['configurationItemCaptureTime']
                },
            ],
            ResultToken=event['resultToken'])
    except ClientError:
        pass
    return compliance_value
