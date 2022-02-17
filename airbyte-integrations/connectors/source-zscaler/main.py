#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zscaler import SourceZscaler

if __name__ == "__main__":
    source = SourceZscaler()
    launch(source, sys.argv[1:])
