# pylint: skip-file

#   Copyright 2021 Dynatrace LLC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import re

import jmespath
from jmespath import functions

from logs.metadata_engine import me_id


class MappingCustomFunctions(functions.Functions):

    @functions.signature({'types': ['string', 'null']},
                         {'types': ['string', 'null']},
                         {'types': ['string', 'null']})
    def _func_replace_regex(self, subject, regex, replacement):
        # replace java capture group sign ($) to python one (\)
        processed_replacement = re.sub(r'\$(\d+)+', '\\\\\\1', replacement)
        compiled_regex = re.compile(regex)
        result = compiled_regex.sub(processed_replacement, subject)
        return result

    @functions.signature({'types': []},
                         {'types': ['expref']},
                         {'types': ['expref']},
                         {'types': []})
    def _func_if(self, condition, if_true_expression, if_false_expression, node_scope):
        if condition:
            return if_true_expression.visit(if_true_expression.expression, node_scope)
        else:
            return if_false_expression.visit(if_false_expression.expression, node_scope)


    @functions.signature({'types': ['string', 'null']}, {'types': ['string', 'null']})
    def _func_starts_with(self, search, suffix):
        if(search is None or suffix is None):
            return False
        return search.startswith(suffix)

    @functions.signature({'types': ['string', 'null']},
                         {"types": ['array']})
    def _func_format(self, pattern, values):
        return self.format(pattern, values)

    def format(self, pattern, values):
        if pattern.count("{}") != len(values):
            return None

        output = pattern
        for value in values:
            if value is not None:
                output = output.replace("{}", value, 1)
        return output

    @functions.signature({'types': ['string', 'null']},
                         {"types": ['array']})
    def _func_format_arn(self, pattern, values):
        if None in values:
            # any None value in input is treated as missing required data, no complete arn can be calculated
            return None

        return self.format(pattern, values)

    @functions.signature({'types': ['string', 'null']},
                         {'types': ['string', 'null']})
    def _func_dt_meid_md5(self, entity_type, hashing_input):
        return me_id.meid_md5(entity_type, hashing_input)

    @functions.signature({'types': ['string', 'null']},
                         {'types': ['string', 'null']})
    def _func_dt_meid_murmurhash(self, entity_type, hashing_input):
        return me_id.meid_murmurhash(entity_type, hashing_input)

    #same ids across all version of aws credentials - md5
    @functions.signature({'types': ['string', 'null']})
    def _func_dt_meid_ebs_volume(self, volumeId): return me_id.meid_md5("EBS_VOLUME", volumeId)
    @functions.signature({'types': ['string', 'null']})
    def _func_dt_meid_ec2_instance(self, instanceId): return me_id.meid_md5("EC2_INSTANCE", instanceId)
    @functions.signature({'types': ['string', 'null']},{'types': ['string', 'null']},{'types': ['string', 'null']})
    def _func_dt_meid_lambda_function(self, functionName, region, accountId): return me_id.meid_md5("AWS_LAMBDA_FUNCTION", functionName, region, "_", accountId)

    # aws credentials v1 - md5
    @functions.signature({'types': ['string', 'null']})
    def _func_dt_meid_elb_v1(self, dnsName): return me_id.meid_md5("ELASTIC_LOAD_BALANCER", dnsName)
    @functions.signature({'types': ['string', 'null']})
    def _func_dt_meid_alb_v1(self, arn): return me_id.meid_md5("AWS_APPLICATION_LOAD_BALANCER", arn)
    @functions.signature({'types': ['string', 'null']})
    def _func_dt_meid_nlb_v1(self, arn): return me_id.meid_md5("AWS_NETWORK_LOAD_BALANCER", arn)
    @functions.signature({'types': ['string', 'null']})
    def _func_dt_meid_auto_scaling_group_v1(self, arn): return me_id.meid_md5("AUTO_SCALING_GROUP", arn)
    @functions.signature({'types': ['string', 'null']}, {'types': ['string', 'null']})
    def _func_dt_meid_dynamo_db_v1(self, tableName, region): return me_id.meid_md5("DYNAMO_DB_TABLE", tableName, region)
    @functions.signature({'types': ['string', 'null']}, {'types': ['string', 'null']})
    def _func_dt_meid_rds_v1(self, instanceId, region): return me_id.meid_md5("RELATIONAL_DATABASE_SERVICE", instanceId, region)
    @functions.signature({'types': ['string', 'null']})
    def _func_dt_meid_s3_bucket_v1(self, name): return me_id.meid_md5("S3BUCKET", name)

    def _func_dt_meid_supporting_service_v1(self, supporting_service_name, region, main_dimension, name):
        raise NotImplementedError("ID calculation for supporting services in Credentials version=1 is not possible without querying Dynatrace. "
                                      "It requires Credentials ID that is generated randomly by the Dynatrace cluster and not accessible here")

    # aws credentials v2 - murmurhash with special hash
    @functions.signature({'types': ['string', 'null']})
    def _func_dt_meid_elb_v2(self, arn): return me_id.meid_murmurhash_awsseed("ELASTIC_LOAD_BALANCER", arn)
    @functions.signature({'types': ['string', 'null']})
    def _func_dt_meid_alb_v2(self, arn): return me_id.meid_murmurhash_awsseed("AWS_APPLICATION_LOAD_BALANCER", arn)
    @functions.signature({'types': ['string', 'null']})
    def _func_dt_meid_nlb_v2(self, arn): return me_id.meid_murmurhash_awsseed("AWS_NETWORK_LOAD_BALANCER", arn)
    @functions.signature({'types': ['string', 'null']})
    def _func_dt_meid_auto_scaling_group_v2(self, arn): return me_id.meid_murmurhash_awsseed("AUTO_SCALING_GROUP", arn)
    @functions.signature({'types': ['string', 'null']})
    def _func_dt_meid_dynamo_db_v2(self, arn): return me_id.meid_murmurhash_awsseed("DYNAMO_DB_TABLE", arn)
    @functions.signature({'types': ['string', 'null']})
    def _func_dt_meid_rds_v2(self, arn): return me_id.meid_murmurhash_awsseed("RELATIONAL_DATABASE_SERVICE", arn)
    @functions.signature({'types': ['string', 'null']})
    def _func_dt_meid_s3_bucket_v2(self, arn): return me_id.meid_murmurhash_awsseed("S3BUCKET", arn)

    # aws credentials v2 - murmurhash with default hash
    @functions.signature({'types': ['string', 'null']}, {'types': ['string', 'null']})
    def _func_dt_meid_supporting_service_v2(self, supporting_service_short_name, arn): return me_id.meid_murmurhash("CUSTOM_DEVICE", supporting_service_short_name.lower(), arn)

jmespath.functions.REVERSE_TYPES_MAP['null'] = ('NoneType', 'None')
jmespath.functions.TYPES_MAP['NoneType'] = ('null')
jmespath.functions.TYPES_MAP['None'] = ('null')
JMESPATH_OPTIONS = jmespath.Options(custom_functions=MappingCustomFunctions())
