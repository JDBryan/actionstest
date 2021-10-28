import argparse
import boto3
from botocore.exceptions import ClientError


def parse_arguments():
    parser = argparse.ArgumentParser(description="Build artifacts and upload to S3")
    parser.add_argument(
        "s3_artifact_bucket",
        help="The S3 bucket to upload the artifacts into once build, e.g: 'sb-upn-hs1-{workspace}-artifacts'",
    )
    parser.add_argument(
        "filename", help="The name of the file to be uploaded"
    )
    parser.add_argument(
        "repo_name", help="The of the current repository"
    )
    return parser.parse_args()
            
        
def upload_release(bucket, filename, repo_name): 
    session = boto3.Session()
    s3_client = session.client("s3")
    
    try:
        s3_client.upload_file(
            "./" + filename,
            bucket,
            repo_name + "/" + filename
        )
    except ClientError as e:
        print(e)


if __name__ == "__main__":
    args = parse_arguments()
    upload_release(args.s3_artifact_bucket, args.filename, args.repo_name)
