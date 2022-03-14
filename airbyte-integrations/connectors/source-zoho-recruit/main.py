#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_zoho_recruit import SourceZohoRecruit

if __name__ == "__main__":
    source = SourceZohoRecruit()
    launch(source, sys.argv[1:])
