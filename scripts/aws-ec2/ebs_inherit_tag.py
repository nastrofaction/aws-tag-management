#!/usr/bin/env python2.7

# ebs_inherit_tags
#
# ebs volumes inherit tags from ec2 instances using attachement informaiton
# boto3 credentials must be configured, run per region


import boto3
from datetime import datetime, timedelta

region = "us-east-1"
ec2 = boto3.resource("ec2", region_name=region)


def get_volumes():
    return ec2.volumes.all()


def get_attached_instance(volume):
    if len(volume.attachments) == 0:
        return None
    return volume.attachments[0].get('InstanceId')


def get_instance_tags(instance_id):
    try:
        instance = ec2.Instance(instance_id)
        tags = instance.tags
    except:
        tags = {}
    return tags


def get_tag_by_key(tags, key):
    for tag in tags:
        tag_key = tag.get('Key')
        if tag_key == key:
            return tag.get('Value')
    return None


def create_tag(resource, key, value):
    tag_list = [{'Key': key, 'Value': value}]
    return resource.create_tags(Tags=tag_list)

for volume in get_volumes():
    instance_id = get_attached_instance(volume)
    if instance_id is None:
        print("Volume: {} is not attached".format(volume.volume_id))
        continue
    instance_tags = get_instance_tags(instance_id)
    instance_function = get_tag_by_key(instance_tags, 'Function')
    instance_name = get_tag_by_key(instance_tags, 'Name')
    name_str = " ({})".format(instance_name) if instance_name else ""
    print("Instance: {}{}\tFunction: {}".format(
        instance_id, name_str, instance_function))
    volume_tags = create_tag(volume, 'Function', instance_function)
    print("VolumeId: {}\Tags: {}".format(volume.volume_id, volume_tags))
