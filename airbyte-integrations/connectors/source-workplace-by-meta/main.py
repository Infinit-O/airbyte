#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_workplace_by_meta import SourceWorkplaceByMeta

if __name__ == "__main__":
    source = SourceWorkplaceByMeta()
    launch(source, sys.argv[1:])
