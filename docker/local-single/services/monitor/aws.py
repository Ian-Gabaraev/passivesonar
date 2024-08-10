import boto3
import os
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_sqs_queue_url = os.getenv("AWS_SQS_QUEUE_URL")
aws_region = os.getenv("AWS_REGION")

log_group_name = "sonar"
log_stream_name = "sonarlogstream"


def sed_log(log_message):
    client = boto3.client("logs", region_name=aws_region)
    response = client.describe_log_streams(
        logGroupName=log_group_name, logStreamNamePrefix=log_stream_name
    )
    sequence_token = response["logStreams"][0].get("uploadSequenceToken")
    log_event = {
        "logGroupName": log_group_name,
        "logStreamName": log_stream_name,
        "logEvents": [
            {
                "timestamp": int(datetime.now().timestamp() * 1000),
                "message": log_message,
            }
        ],
    }

    if sequence_token:
        log_event["sequenceToken"] = sequence_token

    client.put_log_events(**log_event)


def get_batch_size():
    ssm = boto3.client("ssm")
    parameter_name = "BatchSize"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value


def get_recording_duration():
    ssm = boto3.client("ssm")
    parameter_name = "RecordingDurationSec"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value


def get_loudness_threshold():
    ssm = boto3.client("ssm")
    parameter_name = "LoudnessUpperLimitRMS"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value


def get_streak_threshold():
    ssm = boto3.client("ssm")
    parameter_name = "LoudNoiseStreakUpperLimit"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value


def get_audio_q_size_threshold():
    ssm = boto3.client("ssm")
    parameter_name = "AudioQSizeUpperLimit"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value


def get_chunk_size():
    ssm = boto3.client("ssm")
    parameter_name = "ChunkSize"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value


def get_listening_duration():
    ssm = boto3.client("ssm")
    parameter_name = "ListeningDurationSec"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value


def get_sampling_rate():
    ssm = boto3.client("ssm")
    parameter_name = "SamplingRateHZ"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value


def get_tg_bot_key():
    ssm = boto3.client("ssm")
    parameter_name = "raspberry_bot_key"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value


def get_main_chat_id():
    ssm = boto3.client("ssm")
    parameter_name = "raspberry_bot_user_id"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value


def get_log_group_name():
    ssm = boto3.client("ssm")
    parameter_name = "SonarLogGroupName"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value


def get_log_stream_name():
    ssm = boto3.client("ssm")
    parameter_name = "SonarLogStreamName"
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]
    return parameter_value
