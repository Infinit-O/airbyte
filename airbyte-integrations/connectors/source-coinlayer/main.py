#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_coinlayer import SourceCoinlayer

if __name__ == "__main__":
    source = SourceCoinlayer()
    launch(source, sys.argv[1:])
