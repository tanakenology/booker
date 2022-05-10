import json
from urllib.parse import urlparse

import boto3


def read_jsonlines_s3(path: str):
    o = urlparse(path)
    s3 = boto3.resource(o.scheme)
    bucket = s3.Bucket(o.netloc)
    obj = bucket.Object(o.path[1:])
    res = obj.get()
    body = res["Body"].read().decode("utf-8")
    for line in body.splitlines():
        yield json.loads(line)
