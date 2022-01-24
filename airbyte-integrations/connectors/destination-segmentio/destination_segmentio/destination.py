#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Mapping, Any, Iterable

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, ConfiguredAirbyteCatalog, AirbyteMessage, Status, Type
import analytics


class DestinationSegmentio(Destination):
    def write(
            self,
            config: Mapping[str, Any],
            configured_catalog: ConfiguredAirbyteCatalog,
            input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:

        """
        Reads the input stream of messages, config, and catalog to write data to the destination.

        This method returns an iterable (typically a generator of AirbyteMessages via yield) containing state messages received
        in the input message stream. Outputting a state message means that every AirbyteRecordMessage which came before it has been
        successfully persisted to the destination. This is used to ensure fault tolerance in the case that a sync fails before fully completing,
        then the source is given the last state message output from this method as the starting point of the next sync.

        :param config: dict of JSON configuration matching the configuration declared in spec.json
        :param configured_catalog: The Configured Catalog describing the schema of the data being received and how it should be persisted in the
                                    destination
        :param input_messages: The stream of input messages received from the source
        :return: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs
        """
        analytics.write_key = config.get("write_key")
        successfully_written: int = 0

        for message in input_messages:
            if message.type == Type.STATE:
                yield message
            elif message.type == Type.RECORD:
                event: dict = message.record.data
                user_id: int = event["admin"]["id"]
                user_name: str = event["admin"]["name"]
                event_type: str = event["action_type"]
                # self.logger.info("Event -> {}".format(event))
                self.logger.info("User ID -> {}".format(user_id))
                self.logger.info("User name -> {}".format(user_name))
                self.logger.info("Event type -> {}".format(event_type))
                analytics.identify(user_id, {"name": user_name})
                analytics.track(user_id, event_type, event)
                successfully_written += 1
            else:
                continue

        self.logger.info("Records written: {}".format(successfully_written))

        # NOTE: Investigate the need for a call to .flush() here?
        analytics.flush()

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            key = config["write_key"]
            if not key:
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message="Write key is missing, check key and try again."
                )
            else:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
