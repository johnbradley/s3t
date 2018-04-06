#!/usr/bin/env bash

export ENDPOINT_URL=TODO

export DELIVERY_AGENT_ID=TODO
export DELIVERY_AGENT=TODO

export FROM_USER_ID=TODO
export FROM_USER=TODO

export TO_USER_ID=TODO
export TO_USER=TODO

export SOURCE_BUCKET=mouse
export SOURCE_PATH=/tmp/mydata
export DEST_BUCKET=mouse2


echo "$FROM_USER creates bucket $SOURCE_BUCKET"
aws s3 --profile $FROM_USER --endpoint-url $ENDPOINT_URL \
    mb s3://$SOURCE_BUCKET


echo "$FROM_USER uploads $SOURCE_PATH to bucket $SOURCE_BUCKET"
aws s3 --profile $FROM_USER --endpoint-url $ENDPOINT_URL \
    sync $SOURCE_PATH s3://$SOURCE_BUCKET


echo "$FROM_USER gives full control to DELIVERY_AGENT"
aws s3api --profile $FROM_USER --endpoint-url $ENDPOINT_URL \
    put-bucket-acl --bucket $SOURCE_BUCKET \
       --grant-full-control id=$DELIVERY_AGENT_ID
# at this point the FROM_USER cannot change or delete files or the bucket, they can download the files
# should we record what files are going/manifest

exit
echo "Email sent to $TO_USER to accept"
echo "$TO_USER accepts delivery"


echo "DELIVERY_AGENT gives $TO_USER read permissions"
# TO_USER needs to be able to read the bucket to list the files
aws s3api --profile $DELIVERY_AGENT --endpoint-url $ENDPOINT_URL \
    put-bucket-acl --bucket $SOURCE_BUCKET \
        --grant-read id=$TO_USER_ID \
        --grant-full-control id=$DELIVERY_AGENT_ID

# TO_USER needs to be able to read the files to copy them
# NOTE: this is probably fragile due to spaces in filenames
for FILE in $(aws s3 --profile $DELIVERY_AGENT --endpoint-url $ENDPOINT_URL ls s3://$SOURCE_BUCKET | awk '{print $4}')
do
   aws s3api --profile $DELIVERY_AGENT --endpoint-url $ENDPOINT_URL \
       put-object-acl --bucket $SOURCE_BUCKET --key=$FILE \
          --grant-read id=$TO_USER_ID  \
          --grant-full-control id=$DELIVERY_AGENT_ID
done


echo "$TO_USER creates a bucket so he has ownership"
aws s3 --profile $TO_USER --endpoint-url $ENDPOINT_URL \
    mb s3://$DEST_BUCKET

echo "$TO_USER copies files to his bucket"
aws s3 --profile $TO_USER --endpoint-url $ENDPOINT_URL \
    sync s3://$SOURCE_BUCKET s3://$DEST_BUCKET


echo "DELIVERY_AGENT deletes bucket"
aws s3 --profile $DELIVERY_AGENT --endpoint-url $ENDPOINT_URL \
    rb --force s3://$SOURCE_BUCKET
