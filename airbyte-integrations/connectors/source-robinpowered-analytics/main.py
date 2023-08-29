#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_robinpowered_analytics import SourceRobinpoweredAnalytics

if __name__ == "__main__":
    source = SourceRobinpoweredAnalytics()
    launch(source, sys.argv[1:])
