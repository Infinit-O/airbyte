#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from destination_segmentio import DestinationSegmentio

if __name__ == "__main__":
    DestinationSegmentio().run(sys.argv[1:])
