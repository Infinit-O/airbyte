import logging
import math
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import boto3
import botocore
import botocore.exceptions
import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from botocore.config import Config
from .streams import (list_dashboards, 
                      list_dashboard_versions, 
                      list_themes,
                      list_templates,
                      list_template_versions,
                      list_namespaces,
                      list_folders,
                      list_folder_members,
                      list_data_sources,
                      list_data_sets,
                      list_analyses,
                      list_ingestions,
                      describe_dashboard,
                      describe_analysis,
                      describe_analysis_definition
                      )

class Client:
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, aws_region_name: str):
        config = Config(
            parameter_validation=False,
            retries=dict(
                # use similar configuration as in http source
                max_attempts=5,
                # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/retries.html#adaptive-retry-mode
                mode="adaptive",
            ),
        )

        self.session: botocore.client.QuickSight = boto3.client(
            "quicksight", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region_name, config=config
        )

class SourceAwsQuicksight(AbstractSource):       
    
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        client = Client(config["aws_access_key_id"], config["aws_secret_access_key"], config["aws_region_name"], )
        try:
            client.session.list_dashboards(MaxResults=1, AwsAccountId=config["aws_account_id"])
            #response = client.session.list_folder_members(FolderId="21c6bd13-3704-413e-bcdf-3e44080eebe4", MaxResults=1, AwsAccountId=config["aws_account_id"])
            #logger.info(f"Response from list_dashboards API: {response}")
        except botocore.exceptions.ClientError as error:
            return False, error

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [list_dashboards(**config),
                list_dashboard_versions(**config),
                list_themes(**config),
                list_templates(**config),
                list_template_versions(**config),
                list_namespaces(**config),
                list_folders(**config),
                list_folder_members(**config),
                list_data_sources(**config),
                list_data_sets(**config),
                list_analyses(**config),
                list_ingestions(**config),
                describe_dashboard(**config),
                describe_analysis(**config),
                describe_analysis_definition(**config)
                ]
        