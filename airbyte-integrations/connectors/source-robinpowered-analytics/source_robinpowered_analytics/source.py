#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime
from typing import Dict, Generator

import requests
import pendulum
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    AirbyteStateBlob,
    StreamDescriptor,
    SyncMode,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.sources import Source


class SourceRobinpoweredAnalytics(Source):
    # Header: "Authorization: Access-Token {}"
    def _request_desks_report(self, api_token: str, org_id: str, body: dict) -> requests.Response:
        full_url = f"https://api.robinpowered.com/v1.0/insights/exports/organizations/{org_id}/desks"
        response = self._send_request(full_url, api_token, org_id, body)
        return response

    def _request_spaces_report(self, api_token: str, org_id: str, body: dict) -> requests.Response:
        full_url = f"https://api.robinpowered.com/v1.0/insights/exports/organizations/{org_id}/spaces"
        response = self._send_request(full_url, api_token, org_id, body)
        return response

    def _send_request(self, url: str, api_token: str, org_id: str, body: dict) -> requests.Response:
        headers = {
            "Authorization": f"Access-Token {api_token}"
        }
        resp = requests.post(url=url, headers=headers, data=body)
        return resp
    
    def _get_report(self, api_token: str, export_id: str) -> str:
        full_url = f"http://api.robinpowered.com/v1.0/insights/exports/{export_id}"
        headers = {
            "Authorization": f"Access-Token {api_token}"
        }
        resp = requests.get(url=full_url, headers=headers)
        resp.raise_for_status()
        return resp.content

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the integration
            e.g: if a provided Stripe API token can be used to connect to the Stripe API.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.yaml file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        target = "https://api.robinpowered.com/v1.0/auth"
        api_key = config["api_key"]
        try:
            # Not Implemented
            headers = {
                "Authorization": f"Access-Token {api_key}"
            }
            resp = requests.get(target, headers=headers)
            resp.raise_for_status()
            logger.debug(f"response status: {resp.status_code}")
            logger.debug(f"response content: {resp.content}")

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        """
        Returns an AirbyteCatalog representing the available streams and fields in this integration.
        For example, given valid credentials to a Postgres database,
        returns an Airbyte catalog where each postgres table is a stream, and each table column is a field.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
        the properties of the spec.yaml file

        :return: AirbyteCatalog is an object describing a list of all available streams in this source.
            A stream is an AirbyteStream object that includes:
            - its stream name (or table name in the case of Postgres)
            - json_schema providing the specifications of expected schema for this stream (a list of columns described
            by their names and types)
        """

        # spec:
        # - daily reports
        # - from 00:00:00 to 11:59:59 every day
        # request reports
        # POST https://api.robinpowered.com/v1.0/insights/exports/organizations/[:id]/spaces
        # POST https://api.robinpowered.com/v1.0/insights/exports/organizations/[:id]/desks
        # get reports
        # GET https://api.robinpowered.com/v1.0/insights/exports/[:id]

        streams = []

        # spaces, desks
        json_schema = {  # Example
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"csv": {"type": "string"}},
        }
        sync_modes = [SyncMode.full_refresh]

        space_stream = AirbyteStream(name="everything",
                                     json_schema=json_schema,
                                     supported_sync_modes=sync_modes)

        streams.append(space_stream)

        return AirbyteCatalog(streams=streams)

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        """
        Returns a generator of the AirbyteMessages generated by reading the source with the given configuration,
        catalog, and state.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this source, content of this json is as specified in
            the properties of the spec.yaml file
        :param catalog: The input catalog is a ConfiguredAirbyteCatalog which is almost the same as AirbyteCatalog
            returned by discover(), but
        in addition, it's been configured in the UI! For each particular stream and field, there may have been provided
        with extra modifications such as: filtering streams and/or columns out, renaming some entities, etc
        :param state: When a Airbyte reads data from a source, it might need to keep a checkpoint cursor to resume
            replication in the future from that saved checkpoint.
            This is the object that is provided with state from previous runs and avoid replicating the entire set of
            data everytime.

        :return: A generator that produces a stream of AirbyteRecordMessage contained in AirbyteMessage object.
        """
        stream_name = catalog.streams[0].stream.name
        namespace = ""

        # 1. get list of existing report requests from state. if none, skip to 4.
        if state:
            logger.info("State found! Getting export IDs.")
            desks = state["desks_export_id"]
            spaces = state["spaces_export_id"]
            logger.info(f"desks -> {desks}")
            logger.info(f"spaces -> {spaces}")

            desks_report = self._get_report(config["api_key"], desks)
            logger.info("retrieved desks report")

            spaces_report = self._get_report(config["api_key"], spaces)
            logger.info("retrieved spaces report")

            # 2. get reports from remote API using state data
            for r in [desks_report, spaces_report]:
                # 3. send reports to S3 (yield AirbyteRecordMessage, etc)
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(
                        stream=stream_name,
                        data={
                            "csv": r
                        },
                        emitted_at=int(datetime.now().timestamp() * 1000)
                    ),
                )

        # 4. send POSTs out to remote to queue up requests for (new) reports.
        start_template = "{}T00:00:00Z"
        end_template = "{}T23:59:59Z"
        end_date = pendulum.today().date()
        start_date = end_date.subtract(months=6)

        body = {
            "from": start_template.format(start_date),
            "to": end_template.format(end_date)
            }
        desks_response = self._request_desks_report(config["api_key"], config["org_id"], body).json()
        spaces_response = self._request_spaces_report(config["api_key"], config["org_id"], body).json()

        desks_export_id = desks_response["data"]["export_id"]
        logger.info(f"requested desks report -> {desks_export_id}")
        spaces_export_id = spaces_response["data"]["export_id"]
        logger.info(f"requested spaces report -> {spaces_export_id}")

        # 5. record the new report IDs for download next run, i.e yield as state
        blob = AirbyteStateBlob(desks_export_id=desks_export_id, spaces_export_id=spaces_export_id)
        new_state = AirbyteStateMessage(data=blob)
        logger.info("Yielding state...")
        yield AirbyteMessage(type=Type.STATE, state=new_state)
