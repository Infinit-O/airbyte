#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_desktop_central import SourceDesktopCentral

if __name__ == "__main__":
    source = SourceDesktopCentral()
    launch(source, sys.argv[1:])
