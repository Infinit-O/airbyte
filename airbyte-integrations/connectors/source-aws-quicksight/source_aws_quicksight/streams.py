import logging
import math
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional
import boto3
import botocore
import botocore.exceptions
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from botocore.config import Config


class Client:
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, aws_region_name: str):
        config = Config(
            parameter_validation=False,
            retries=dict(
                max_attempts=5,
                mode="adaptive",
            ),
        )
        self.session = boto3.client(
            "quicksight",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region_name,
            config=config
        )

class AwsQuicksightStream(Stream, ABC):
    

    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, aws_account_id: str, aws_region_name: str, **kwargs):
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_access_key_id = aws_access_key_id
        self.aws_account_id = aws_account_id
        self.client = Client(aws_access_key_id, aws_secret_access_key, aws_region_name)
        self.records_left = kwargs.get("records_limit", math.inf)
    
    def next_page_token(self, response: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
        return response.get("NextToken")

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if self.limit is not None:
            params = {"MaxResults": self.limit, "AwsAccountId": self.aws_account_id}
        else:
            params = {"AwsAccountId": self.aws_account_id}
        if next_page_token:
           params["NextToken"] = next_page_token

        return params  

    def datetime_to_timestamp(self, date: datetime) -> int:
        return int(date.timestamp())

    @abstractmethod
    def send_request(self, **kwargs) -> Mapping[str, Any]:
        """
        This method should be overridden by subclasses to send proper request with appropriate parameters to QuickSight.
        """
        pass

    def is_read_limit_reached(self) -> bool:
        return self.records_left <= 0

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        pagination_complete = False
        next_page_token = None


        while not pagination_complete:
            params = self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
            response = self.send_request(**params)

            next_page_token = self.next_page_token(response)
            if not next_page_token:
                pagination_complete = True

            for record in self.parse_response(response):
                yield record
                self.records_left -= 1

                if self.is_read_limit_reached():
                    return iter(())

        yield from []
        
        if hasattr(self, 'records_left'):
            return self.records_left <= 0
        return False

    def parse_response(self, response: dict, **kwargs) -> Iterable[Mapping[str, Any]]:
        for event in response.get(self.data_field, []): 
            #self.logger.info(f"{self.time_field}")
            if (self.time_field in event) and (self.time_field is not None): 
                event[self.time_field] = self.datetime_to_timestamp(event[self.time_field])
            yield event       

class AwsQuicksightSubStream(Stream, ABC):
    
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, aws_account_id: str, aws_region_name: str, **kwargs):
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_access_key_id = aws_access_key_id
        self.aws_account_id = aws_account_id
        self.client = Client(aws_access_key_id, aws_secret_access_key, aws_region_name)
        self.records_left = kwargs.get("records_limit", math.inf)
    
    def next_page_token(self, response: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
        return response.get("NextToken")

    def request_params(
        self, 
        stream_state: Mapping[str, Any], 
        stream_slice: Mapping[str, Any], 
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if self.limit is not None:
            params = {"MaxResults": self.limit, "AwsAccountId": self.aws_account_id}
        else:
            params = {"AwsAccountId": self.aws_account_id}
        
        if stream_slice:
            stream_slice = ', '.join(stream_slice)
            #self.logger.info(f"parent_key: {stream_slice}")
            params[self.parent_stream.primary_key] = stream_slice 
     
        
        if next_page_token:
            params["NextToken"] = next_page_token

        return params

    def datetime_to_timestamp(self, date: datetime) -> int:
        return int(date.timestamp())

    @abstractmethod
    def send_request(self, **kwargs) -> Mapping[str, Any]:
        """
        This method should be overridden by subclasses to send proper request with appropriate parameters to QuickSight.
        """
        pass
    
    def is_read_limit_reached(self) -> bool:
        return self.records_left <= 0
    
    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        pagination_complete = False
        next_page_token = None


        while not pagination_complete:
            params = self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
            response = self.send_request(**params)   
            

            next_page_token = self.next_page_token(response)
            if not next_page_token:
                pagination_complete = True
                

            for record in self.parse_response(response):
                yield record
                self.records_left -= 1

                if self.is_read_limit_reached():
                    return iter(())

        yield from []
        
        if hasattr(self, 'records_left'):
            return self.records_left <= 0
        return False
    def parse_response(self, response: dict, **kwargs) -> Iterable[Mapping[str, Any]]:
        if self.data_field is not None:
            for event in response.get(self.data_field, []):
                if isinstance(event, str):
                    if  (self.time_field is not None): 
                        response[self.time_field] = self.datetime_to_timestamp(response[self.time_field])
                        self.logger.info(f"resp{response}")
                    yield response
            
                elif (self.time_field in event) and (self.time_field is not None): 
                    event[self.time_field] = self.datetime_to_timestamp(event[self.time_field])
                    yield event 
                
                else:
                    yield event
                
                
        elif self.data_field is None:
            if (self.time_field in response) and (self.time_field is not None): 
                event[self.time_field] = self.datetime_to_timestamp(response[self.time_field])
            yield response  

            
            

            


    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        seen = []
        pr = self.parent_stream(aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key,aws_account_id=self.aws_account_id, aws_region_name=self.client.session.meta.region_name)
        self.logger.info("Fetching records from parent stream...")
        pr_records = pr.read_records(sync_mode=SyncMode.full_refresh)
        

        self.logger.info("Sorting out unique IDs...")
        for record in pr_records:
            if record[self.parent_stream.primary_key] in seen:
                continue
            else:
                 seen.append(record[self.parent_stream.primary_key])

        self.logger.info("Yielding results...")
        for parentsid in seen:
            self.logger.debug(f"Yielding: {parentsid}")
            yield {parentsid}
        
class list_dashboards(AwsQuicksightStream):
    primary_key = "DashboardId"
    time_field = "CreatedTime"
    cursor_field = "CreatedTime"
    data_field = "DashboardSummaryList"
    limit: int = 100

    def send_request(self, **kwargs) -> Mapping[str, Any]:
        return self.client.session.list_dashboards(**kwargs)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params
    
class list_dashboard_versions(AwsQuicksightSubStream):
    primary_key = None
    time_field = "CreatedTime"
    cursor_field = "CreatedTime"
    data_field = "DashboardVersionSummaryList"
    parent_stream = list_dashboards
    limit: int = 100

    def send_request(self, **kwargs) -> Mapping[str, Any]:
        return self.client.session.list_dashboard_versions(**kwargs)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params
    
class list_themes(AwsQuicksightStream):
    primary_key = "ThemeId"
    time_field = "CreatedTime"
    cursor_field = "CreatedTime"
    data_field = "ThemeSummaryList"
    limit: int = 100

    def send_request(self, **kwargs) -> Mapping[str, Any]:
        return self.client.session.list_themes(**kwargs)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params

class list_templates(AwsQuicksightStream):
    primary_key = "TemplateId"
    time_field = "CreatedTime"
    cursor_field = "CreatedTime"
    data_field = "TemplateSummaryList"
    limit: int = 100

    def send_request(self, **kwargs) -> Mapping[str, Any]:
        return self.client.session.list_templates(**kwargs)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params
    
class list_template_versions(AwsQuicksightSubStream):
    primary_key = None
    time_field = "CreatedTime"
    cursor_field = "CreatedTime"
    data_field = "TemplateVersionSummaryList"
    limit: int = 100 # 90 days in seconds
    parent_stream = list_templates

        # Initialize the logger
        
        
    def send_request(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Mapping[str, Any]:
        return self.client.session.list_template_versions(stream_slice=stream_slice, **kwargs)

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
        ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params
    
class list_template_aliases(AwsQuicksightSubStream):
    primary_key = None
    time_field = "CreatedTime"
    cursor_field = "CreatedTime"
    data_field = "TemplateAliasList"
    limit: int = 100 # 90 days in seconds
    parent_stream = list_templates

        # Initialize the logger
        
        
    def send_request(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Mapping[str, Any]:
        return self.client.session.list_template_aliases(stream_slice=stream_slice, **kwargs)

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
        ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params
    
class list_namespaces(AwsQuicksightStream):
    primary_key = None
    time_field = None
    ####cursor_field = None
    data_field = "Namespaces"
    limit: int = 100

    def send_request(self, **kwargs) -> Mapping[str, Any]:
        return self.client.session.list_namespaces(**kwargs)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params
    
class list_data_sets(AwsQuicksightStream):
    primary_key = "DataSetId"
    time_field = "CreatedTime"
    cursor_field = "CreatedTime"
    data_field = "DataSetSummaries"
    limit: int = 100

    def send_request(self, **kwargs) -> Mapping[str, Any]:
        return self.client.session.list_data_sets(**kwargs)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params
    
class list_folders(AwsQuicksightStream):
    primary_key = "FolderId"
    time_field = "CreatedTime"
    #cursor_field = "CreatedTime"
    data_field = "FolderSummaryList"
    limit: int = 100

    def send_request(self, **kwargs) -> Mapping[str, Any]:
        return self.client.session.list_folders(**kwargs)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params


class list_folder_members(AwsQuicksightSubStream):
    primary_key = None
    time_field = None
    #cursor_field = "CreatedTime"
    data_field = "FolderMemberList"
    parent_stream = list_folders
    limit: int = 100

    def send_request(self, **kwargs) -> Mapping[str, Any]:
        return self.client.session.list_folder_members(**kwargs)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params
       
class list_ingestions(AwsQuicksightSubStream):
    primary_key = "IngestionId"
    time_field = "CreatedTime"
    cursor_field = "CreatedTime"
    data_field = "Ingestions"
    limit: int = 100 # 90 days in seconds
    parent_stream = list_data_sets

        # Initialize the logger
        
        
    def send_request(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Mapping[str, Any]:
        return self.client.session.list_ingestions(stream_slice=stream_slice, **kwargs)

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
        ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params

class list_analyses(AwsQuicksightStream):
    primary_key = "AnalysisId"
    time_field = "CreatedTime"
    cursor_field = "CreatedTime"
    data_field = "AnalysisSummaryList"
    limit: int = 100

    def send_request(self, **kwargs) -> Mapping[str, Any]:
        return self.client.session.list_analyses(**kwargs)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params

class list_data_sources(AwsQuicksightStream):
    primary_key = "DataSourceId"
    time_field = "CreatedTime"
    cursor_field = "CreatedTime"
    data_field = "DataSources"
    limit = 100

    def send_request(self, **kwargs) -> Mapping[str, Any]:
        return self.client.session.list_data_sources(**kwargs)

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params
 
 
         
class describe_dashboard(AwsQuicksightSubStream):
    primary_key = None
    time_field = None
    ##cursor_field = "CreatedTime"
    data_field = "Dashboard"
    parent_stream = list_dashboards
    #limit: int = 100
    limit = None
    
        
    def send_request(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Mapping[str, Any]:
        return self.client.session.describe_dashboard(stream_slice=stream_slice, **kwargs)

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
        ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params
    

class describe_analysis_definition(AwsQuicksightSubStream):
    primary_key = None
    time_field = None
    ##cursor_field = "CreatedTime"
    data_field = None
    parent_stream = list_analyses
    #limit: int = 100
    limit = None
    
        
    def send_request(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Mapping[str, Any]:
        return self.client.session.describe_analysis_definition(stream_slice=stream_slice, **kwargs)

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
        ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params
    
class describe_analysis(AwsQuicksightSubStream):
    primary_key = None
    time_field = None
    ##cursor_field = "CreatedTime"
    data_field = "Analysis"
    parent_stream = list_analyses
    #limit: int = 100
    limit = None
    
        
    def send_request(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> Mapping[str, Any]:
        return self.client.session.describe_analysis(stream_slice=stream_slice, **kwargs)

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
        ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        return params