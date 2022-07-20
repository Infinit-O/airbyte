#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_linkedin_marketing import SourceLinkedinMarketing

if __name__ == "__main__":
    source = SourceLinkedinMarketing()
    launch(source, sys.argv[1:])
