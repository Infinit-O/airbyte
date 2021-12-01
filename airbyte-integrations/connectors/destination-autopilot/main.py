#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from destination_autopilot import DestinationAutopilot

if __name__ == "__main__":
    DestinationAutopilot().run(sys.argv[1:])
