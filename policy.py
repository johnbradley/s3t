from __future__ import print_function
import argparse
import json
import uuid

POLICY_VERSION = "2012-10-17"

AWS_TYPE = "AWS"
EMC_TYPE = "EMC"
POLICY_TYPES = (AWS_TYPE, EMC_TYPE)

SET_ACL_PERMISSION = "SET_ACL"
COPY_PERMISSION = "COPY"
PERMISSION_TYPES = (SET_ACL_PERMISSION, COPY_PERMISSION)

# Permissions that can be applied to an object
GET_OBJECT = "s3:GetObject"
PUT_OBJECT = "s3:PutObject"
GET_OBJECT_ACL = "s3:GetObjectAcl"
PUT_OBJECT_ACL = "s3:PutObjectAcl"
DELETE_OBJECT = "s3:DeleteObject"

# Permissions that can be applied to a bucket
DELETE_BUCKET = "s3:DeleteBucket"
LIST_BUCKET = "s3:ListBucket"
GET_BUCKET_ACL = "s3:GetBucketAcl"
PUT_BUCKET_ACL = "s3:PutBucketAcl"
GET_BUCKET_POLICY = "s3:GetBucketPolicy"
PUT_BUCKET_POLICY = "s3:PutBucketPolicy"
DELETE_BUCKET_POLICY = "s3:DeleteBucketPolicy"


def make_policy_id():
    return "Policy{}".format(uuid.uuid1())


def make_bucket_resource(type, bucket):
    if type == AWS_TYPE:
        return "arn:aws:s3:::{}".format(bucket)
    elif type == EMC_TYPE:
        return bucket
    raise NotImplemented("resource creation for {}".format(type))


def make_principal(type, user):
    if type == AWS_TYPE:
        return {
            "AWS": [user]
        }
    elif type == EMC_TYPE:
        return user
    raise NotImplemented("make_principal creation for {}".format(type))


def set_acl_permission(type, bucket, user):
    resource = make_bucket_resource(type, bucket)
    principal = make_principal(type, user)
    return [
        {
            "Action": [
                PUT_OBJECT_ACL
            ],
            "Effect": "Allow",
            "Resource": "{}/*".format(resource),
            "Principal": principal
        },
        {
            "Action": [
                LIST_BUCKET,
                PUT_OBJECT_ACL
            ],
            "Effect": "Allow",
            "Resource": resource,
            "Principal": principal
        }
    ]


def make_statements(type, bucket, permission, user):
    if permission == SET_ACL_PERMISSION:
        return set_acl_permission(type, bucket, user)
    raise NotImplemented("No support for type:{} permission:{}".format(type, permission))


def get_bucket_suffix(permission):
    if permission == SET_ACL_PERMISSION:
        return "/*"
    return ""


def create_policy(type, bucket, permission, user):
    policy_id = make_policy_id()
    statements = make_statements(type, bucket, permission, user)

    policy = {
        "Id": policy_id,
        "Version": POLICY_VERSION,
        "Statement": statements
    }
    return json.dumps(policy, indent=4, separators=(',', ': '))


def create_argparser():
    parser = argparse.ArgumentParser(description="s3 policy generator tool.")
    parser.add_argument("--bucket", type=str, dest='bucket', required=True)
    parser.add_argument("--type", type=str, dest='type', required=True, choices=POLICY_TYPES)
    parser.add_argument("--permission", type=str, dest='permission', required=True, choices=PERMISSION_TYPES)
    parser.add_argument("--user", type=str, dest='user', required=True)
    return parser


def main():
    parser = create_argparser()
    args = parser.parse_args()
    policy_str = create_policy(args.type, args.bucket, args.permission, args.user)
    print(policy_str)


if __name__ == '__main__':
    main()
