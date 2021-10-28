import argparse
import os
import zipfile
from abc import abstractmethod
from shutil import copyfile
from typing import Optional

import boto3
from botocore.exceptions import ClientError

BUILD_FOLDER = "build/"


class ArtifactToGenerate(object):
    def __init__(
        self, input_file: str, output_file_name: str, tags: Optional[dict] = None
    ):
        self.input_file = input_file
        self.output_file_name = output_file_name
        self.tags = tags

        self.output_full_path = os.path.join(BUILD_FOLDER, output_file_name)

    @abstractmethod
    def generate(self):
        raise NotImplementedError()


class FolderToZip(ArtifactToGenerate):
    """Contains details of a folder to be zipped up and sent to the build folder"""

    def generate(self):
        """Zips the contents of a folder and outputs the zip file to the build folder"""
        print(
            f" - Zipping the '{self.input_file}' folder and outputting to '{self.output_full_path}'"
        )
        zip_handle = zipfile.ZipFile(self.output_full_path, "w", zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(self.input_file):
            for file in files:
                zip_handle.write(
                    os.path.join(root, file),
                    os.path.relpath(os.path.join(root, file), self.input_file),
                )
        zip_handle.close()


class FileToCopy(ArtifactToGenerate):
    """Contains details of a file that needs copying as-is to the build folder"""

    def generate(self):
        print(f" - Copying '{self.input_file}' to '{self.output_full_path}'")
        copyfile(self.input_file, self.output_full_path)


ARTIFACTS_TO_GENERATE = [
    FolderToZip("artifacts", "release.zip"),
]

# Adds all lambda functions to the artifact list
#for lambda_function_dir in os.listdir("lambda_functions"):
#    full_path = os.path.join("lambda_functions", lambda_function_dir)
#    if os.path.isdir(full_path) and lambda_function_dir != "__pycache__":
#        ARTIFACTS_TO_GENERATE.append(
#            FolderToZip(full_path, f"{lambda_function_dir}.zip")
#        )


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
        "aws_region", help="The region the bucket resides in, e.g: 'eu-west-2'"
    )
    parser.add_argument(
        "--profile", help="The AWS profile to use for the upload, e.g: 'sb-dev-ci'"
    )
    return parser.parse_args()


def create_build_folder():
    if not os.path.isdir(BUILD_FOLDER):
        os.mkdir(BUILD_FOLDER)


def ensure_build_folder_empty():
    print(f"Clearing out the '{BUILD_FOLDER}' folder")

    for file_name in os.listdir(BUILD_FOLDER):
        os.remove(os.path.join(BUILD_FOLDER, file_name))


def generate_artifacts():
    print(f"Generating artifacts & outputting to the '{BUILD_FOLDER}' folder")

    for artifact in ARTIFACTS_TO_GENERATE:
        artifact.generate()

    print("Artifacts generated")


def upload_artifacts(s3_artifact_bucket: str, aws_region: str, profile: Optional[str]):
    """
    Uploads each generated artifact to the S3 bucket provided.
    :param s3_artifact_bucket: The name of the bucket to upload to, e.g: "sb-upn-hs1-{workspace}-artifacts"
    :param aws_region: The region the bucket resides in, e.g: "eu-west-2"
    :param profile: An optional profile to use for the upload, if not provided uses the default
    """
    session = boto3.Session(profile_name=profile, region_name=aws_region)

    s3_client = session.client("s3")

    for artifact in ARTIFACTS_TO_GENERATE:
        try:
            print(
                f" - Uploading '{artifact.output_file_name}' to '{s3_artifact_bucket}'"
            )
            s3_client.upload_file(
                artifact.output_full_path,
                s3_artifact_bucket,
                artifact.output_file_name,
                ExtraArgs=artifact.tags,
            )
        except ClientError as e:
            print(e)
            

          
def upload_release(bucket, filename, aws_region, profile): 
    session = boto3.Session(profile_name=profile, region_name=aws_region)
    s3_client = session.client("s3")
    
    s3_client.upload_file(
        "./artifacts/"+filename,
        bucket,
        "/newplace/"+filename
    )


if __name__ == "__main__":
    args = parse_arguments()
    #create_build_folder()
    #ensure_build_folder_empty()
    #generate_artifacts()
    upload_release(args.s3_artifact_bucket, args.filename, args.aws_region, args.profile)
