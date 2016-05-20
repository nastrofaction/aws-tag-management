#!/usr/bin/env python2.7

import boto3
from botocore.exceptions import ClientError, UnknownServiceError


class AwsResource(object):
    region = None
    resources = []
    tags = []

    def __init__(self, service, region_name=None):
        if service not in boto3.Session().get_available_services():
            raise UnknownServiceError
        self.service = service
        self.region = region_name
        self.get_client()

    def get_client(self):
        self.client = boto3.client(self.service, region_name=self.region)

    def _tagset_to_dict(self, tagset, lower_case=False):
        tag_dict = {}
        if tagset is not None:
            for tag in tagset:
                key = 'Key'
                value = 'Value'
                if lower_case:
                    key = 'key'
                    value = 'value'
                tag_dict[tag.get(key)] = tag.get(value)
        return tag_dict


class DataPipelineTags(AwsResource):

    def __init__(self):
        AwsResource.__init__(self, 'datapipeline')

    def get_resources(self):
        pipelines = self._get_pipelines()
        self.resources = [pipeline.get('id') for pipeline in pipelines]
        return self

    def get_tags(self):
        tagsets = []
        dp_descriptions = []

        id_chunks = [self.resources[x:x + 25] for x in xrange(0, len(self.resources), 25)]
        for chunk in id_chunks:
            descriptions = self.client.describe_pipelines(
                pipelineIds=chunk).get('pipelineDescriptionList')
            for pipeline in descriptions:
                tagset = {
                    'identifier': pipeline.get('pipelineId'),
                    'tags': self._tagset_to_dict(pipeline.get('tags'), lower_case=True)
                }
                tagsets.append(tagset)
        self.tags = tagsets
        return self.tags

    def _get_pipelines(self, pipelines=None, marker=''):
        if pipelines is None:
            pipelines = []
        response = self.client.list_pipelines(marker=marker)
        pipelines.extend(response.get('pipelineIdList'))
        if response.get('hasMoreResults') and response.get('marker') != '':
            self._get_pipelines(pipelines, response.get('marker'))
        return pipelines


class ElbTags(AwsResource):

    def __init__(self, region='us-east-1'):
        AwsResource.__init__(self, 'elb', region)

    def get_resources(self):
        self.resources = self._get_elbs()
        return self

    def get_tags(self):
        tagsets = []
        elb_names = [elb.get('LoadBalancerName') for elb in self.resources]
        tag_descs = self.client.describe_tags(
            LoadBalancerNames=elb_names).get('TagDescriptions')
        for elb in tag_descs:
            tagset = {
                'identifier': elb.get('LoadBalancerName'),
                'tags': self._tagset_to_dict(elb.get('Tags'))
            }
            tagsets.append(tagset)
        self.tags = tagsets
        return self.tags

    def _get_elbs(self, elbs=[], marker=''):
        if marker == '':
            response = self.client.describe_load_balancers()
        else:
            response = self.client.describe_load_balancers(Marker=marker)
        elbs.extend(response.get('LoadBalancerDescriptions'))
        if response.get('NextMarker') and response.get('NextMarker') != '':
            self._get_elbs(elbs, marker=response.get('NextMarker'))
        return elbs


class Ec2InstanceTags(AwsResource):
    def __init__(self, region='us-east-1'):
        AwsResource.__init__(self, 'ec2', region)

    def get_resources(self):
        self.resources = self._get_ec2instances()
        return self

    def get_tags(self):
        tagsets = []
        for instance in self.resources:
            tagset = {
                'identifier': instance.get('InstanceId'),
                'tags': self._tagset_to_dict(instance.get('Tags'))
            }
            tagsets.append(tagset)
        self.tags = tagsets
        return self.tags

    def _get_ec2instances(self, instances=None, marker=None):
        if instances is None:
            instances = []
        if marker is None:
            response = self.client.describe_instances()
        else:
            response = self.client.describe_instances(NextToken=marker)

        for reservation in response.get('Reservations'):
            instances.extend(reservation.get('Instances'))
        if response.get('NextToken') and response.get('NextToken') != '':
            self._get_ec2instances(instances=instances, marker=response.get('NextToken'))
        return instances


class Ec2SpotRequestTags(AwsResource):
    def __init__(self, region='us-east-1'):
        AwsResource.__init__(self, 'ec2', region)

    def get_resources(self):
        response = self.client.describe_spot_instance_requests()
        self.resources = response.get('SpotInstanceRequests')
        return self

    def get_tags(self):
        tagsets = []
        for request in self.resources:
            tagset = {
                'identifier': request.get('SpotInstanceRequestId'),
                'tags': self._tagset_to_dict(request.get('Tags'))
            }
            tagsets.append(tagset)
        self.tags = tagsets
        return self.tags


class Ec2VolumeTags(AwsResource):
    def __init__(self, region='us-east-1'):
        AwsResource.__init__(self, 'ec2', region)

    def get_resources(self):
        self.resources = self._get_ec2volumes()
        return self

    def get_tags(self):
        tagsets = []
        for volume in self.resources:
            tagset = {
                'identifier': volume.get('VolumeId'),
                'tags': self._tagset_to_dict(volume.get('Tags'))
            }
            tagsets.append(tagset)
        self.tags = tagsets
        return self.tags

    def _get_ec2volumes(self, volumes=None, marker=None):
        if volumes is None:
            volumes = []
        if marker is None:
            response = self.client.describe_volumes()
        else:
            response = self.client.describe_volumes(NextToken=marker)

        volumes.extend(response.get('Volumes'))
        if response.get('NextToken') and response.get('NextToken') != '':
            self._get_ec2volumes(volumes=volumes, marker=response.get('NextToken'))
        return volumes


class EmrTags(AwsResource):
    def __init__(self, region='us-east-1'):
        AwsResource.__init__(self, 'emr', region)

    def get_resources(self):
        self.resources = self._get_emrs()
        return self

    def get_tags(self):
        tagsets = []
        emr_ids = [emr.get('Id') for emr in self.resources]
        for emr_id in emr_ids:
            emr_desc = self.client.describe_cluster(ClusterId=emr_id).get('Cluster')
            tagset = {
                'identifier': emr_id,
                'tags': self._tagset_to_dict(emr_desc.get('Tags'))
            }
            tagsets.append(tagset)
        self.tags = tagsets
        return self.tags

    def _get_emrs(self, emrs=None, marker=None):
        if emrs is None:
            emrs = []
        if marker is None:
            response = self.client.list_clusters()
        else:
            response = self.client.list_clusters(Marker=marker)
        emrs.extend(response.get('Clusters'))
        if response.get('Marker') and response.get('Marker') != '':
            self._get_emrs(emrs=emrs, marker=response.get('Marker'))
        return emrs


class GlacierTags(AwsResource):

    def __init__(self, region='us-east-1'):
        AwsResource.__init__(self, 'glacier', region)

    def get_resources(self):
        self.resources = self._get_vaults()
        return self

    def get_tags(self):
        tagsets = []
        for vault in self.resources:
            vault_tags = self.client.list_tags_for_vault(
                vaultName=vault.get('VaultName'))
            tagset = {
                'identifier': vault.get('VaultName'),
                'tags': vault_tags.get('Tags')
            }
            tagsets.append(tagset)
            # tagsets[vault.get('VaultName')] = tagset.get('Tags')
        self.tags = tagsets
        return self.tags

    def _get_vaults(self, vaults=[], marker=''):
        if marker == '':
            response = self.client.list_vaults()
        else:
            response = self.client.list_vaults(marker=marker)
        vaults.extend(response.get('VaultList'))
        if response.get('Marker') and response.get('Marker') != '':
            self._get_vaults(vaults, marker=response.get('Marker'))
        return vaults


class KinesisTags(AwsResource):

    def __init__(self, region='us-east-1'):
        AwsResource.__init__(self, 'kinesis', region)

    def get_resources(self):
        self.resources = self.client.list_streams().get('StreamNames')
        return self

    def get_tags(self):
        tagsets = []
        for stream in self.resources:
            stream_tags = client.list_tags_for_stream(StreamName=stream)
            tagset = {
                'identifier': stream,
                'tags': self._tagset_to_dict(stream_tags)
            }
            tagsets.append(tagset)
            # tagsets[stream] = self._tagset_to_dict(tagset)
        self.tags = tagsets
        return self.tags


class RedshiftTags(AwsResource):

    def __init__(self, region='us-east-1'):
        AwsResource.__init__(self, 'redshift', region)

    def get_resources(self):
        self.resources = self._get_clusters()
        return self

    def get_tags(self):
        tagsets = []
        for cluster in self.resources:
            tagset = {
                'identifier': cluster.get('ClusterIdentifier'),
                'tags': self._tagset_to_dict(cluster.get('Tags'))
            }
            tagsets.append(tagset)
            # tagsets[cluster.get('ClusterIdentifier')] = self._tagset_to_dict(
            #     cluster.get('Tags'))
        self.tags = tagsets
        return self.tags

    def _get_clusters(self, clusters=[], marker=''):
        response = self.client.describe_clusters(Marker=marker)
        clusters.extend(response.get('Clusters'))
        if response.get('Marker') and response.get('Marker') != '':
            self._get_clusters(clusters, response.get('Marker'))
        return clusters


class RdsTags(AwsResource):

    def __init__(self, region='us-east-1'):
        AwsResource.__init__(self, 'rds', region)
        ec2_client = boto3.client('ec2')
        self.account_num = ec2_client.describe_security_groups()['SecurityGroups'][
            0]['OwnerId']

    def get_resources(self):
        clusters = self.client.describe_db_clusters().get('DBClusters')
        self.resources = [cluster.get('DBClusterIdentifier')
                          for cluster in clusters]
        return self

    def get_tags(self):
        tagsets = []
        for cluster in self.resources:
            arn = "arn:aws:rds:{}:{}:db:{}".format(
                self.region, self.account_num, cluster)
            cluster_tags = self.client.list_tags_for_resource(
                ResourceName=arn).get('TagList')
            tagset = {
                'identifier': cluster,
                'tags': self._tagset_to_dict(cluster_tags)
            }
            tagsets.append(tagset)
            # tagsets[cluster] = self._tagset_to_dict(tagset)
        self.tags = tagsets
        return self.tags


class S3Tags(AwsResource):

    def __init__(self, region=None):
        AwsResource.__init__(self, 's3', region)

    def get_resources(self):
        buckets = self.client.list_buckets().get('Buckets')
        self.resources = [bucket.get('Name') for bucket in buckets]
        return self

    def get_tags(self):
        tagsets = []
        for bucket in self.resources:
            try:
                bucket_tags = self.client.get_bucket_tagging(Bucket=bucket).get('TagSet')
            except ClientError:
                bucket_tags = []
            tagset = {
                'identifier': bucket,
                'tags': self._tagset_to_dict(bucket_tags)
            }
            tagsets.append(tagset)
            # tagsets[b] = self._tagset_to_dict(tagset)
        self.tags = tagsets
        return self.tags
