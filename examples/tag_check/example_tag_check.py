#!/usr/bin/env python2
import json
import AwsResources

config_path = "s3://bucket/prefix/to/config.yml"


def display_tag_failure(noncomp_list):
    for tag in noncomp_list:
        print("-----")
        print("Tag Name: {}".format(tag))
        if len(noncomp_list[tag]) > 0:
            for resource in noncomp_list[tag]:
                print("\tIdentifier:\t{}".format(resource['identifier']))
                print("\tReason:\t\t{}".format(resource['noncomp_reason']))
                print("\tTags:\t\t{}".format(json.dumps(resource['tags'])))
        else:
            print("(no mistagged resources)")
        print('')


def main():
    tagcheck = AwsResources.TagCheck(config_path)
    tagcheck.load_tag_defs()

    print("EC2 Instances")
    ec2instance_tags = AwsResources.Ec2InstanceTags().get_resources().get_tags()
    display_tag_failure(tagcheck.get_noncomp_resources(ec2instance_tags))
    # print(json.dumps(elb_tags, indent=4))

    print("EC2 Volumes")
    ec2volume_tags = AwsResources.Ec2VolumeTags().get_resources().get_tags()
    display_tag_failure(tagcheck.get_noncomp_resources(ec2volume_tags))
    # print(json.dumps(elb_tags, indent=4))

    print("Elastic Load Balancers")
    elb_tags = AwsResources.ElbTags().get_resources().get_tags()
    display_tag_failure(tagcheck.get_noncomp_resources(elb_tags))
    # print(json.dumps(elb_tags, indent=4))

    print("Elastic Map Reduce")
    emr_tags = AwsResources.EmrTags().get_resources().get_tags()
    display_tag_failure(tagcheck.get_noncomp_resources(emr_tags))

    print('Data Pipelines')
    dp_tags = AwsResources.DataPipelineTags().get_resources().get_tags()
    display_tag_failure(tagcheck.get_noncomp_resources(dp_tags))
    # print(json.dumps(dp_tags, indent=4))

    print("Glacier")
    glacier_tags = AwsResources.GlacierTags().get_resources().get_tags()
    display_tag_failure(tagcheck.get_noncomp_resources(glacier_tags))
    # print(json.dumps(glacier_tags, indent=4))

    print("Kinesis")
    kinesis_tags = AwsResources.KinesisTags().get_resources().get_tags()
    display_tag_failure(tagcheck.get_noncomp_resources(kinesis_tags))
    # print(json.dumps(kinesis_tags, indent=4))

    print('Redshift')
    rs_tags = AwsResources.RedshiftTags().get_resources().get_tags()
    display_tag_failure(tagcheck.get_noncomp_resources(rs_tags))
    # print(json.dumps(rs_tags, indent=4))

    print('RDS')
    rds_tags = AwsResources.RdsTags().get_resources().get_tags()
    display_tag_failure(tagcheck.get_noncomp_resources(rds_tags))
    # print(json.dumps(rds_tags, indent=4))

    print('S3')
    s3_tags = AwsResources.S3Tags().get_resources().get_tags()
    display_tag_failure(tagcheck.get_noncomp_resources(s3_tags))
    # print(json.dumps(s3_tags, indent=4))


if __name__ == '__main__':
    main()
