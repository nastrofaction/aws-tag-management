import AwsResources
import boto3
import yaml


class TagCheck(object):
    tag_defs = {}

    def __init__(self, config_path):
        self._load_config(config_path)

    def _split_s3_path(self, s3_path):
        path = s3_path.split('/')
        return (path[2], '/'.join(path[3:]))

    def _read_from_s3(self, s3_path):
        bucket, key = self._split_s3_path(s3_path)
        try:
            s3 = boto3.resource('s3')
            obj = s3.Object(bucket, key)
            obj_str = obj.get()["Body"].read()
        except:
            print("Unable to read from s3://{}/{}".format(bucket, key))
        return obj_str

    def _load_config(self, s3_path):
        config_str = self._read_from_s3(s3_path)
        self.config = yaml.load(config_str)

    def _load_tag_values(self, s3_path):
        values_str = self._read_from_s3(s3_path)
        values = [value for value in values_str.splitlines()]
        return values

    def load_tag_defs(self):
        tags = self.config.get('tags')
        for tag in tags:
            values = self._load_tag_values(tag['path'])
            self.tag_defs[tag['name']] = {
                'required': tag['required'],
                'values': values
            }

    def get_noncomp_resources(self, resource_list):
        noncomp = {}
        for tag in self.tag_defs:
            noncomp[tag] = []
            if not self.tag_defs[tag].get('required'):
                continue
            for resource in resource_list:
                if resource.get('tags').get(tag) is not None:
                    if resource.get('tags').get(tag) in self.tag_defs[tag]['values']:
                        continue
                    else:
                        resource['noncomp_reason'] = 'bad_value'
                else:
                    resource['noncomp_reason'] = 'not_tagged'
                noncomp[tag].append(resource)
        return noncomp
