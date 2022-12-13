#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_palo_alto import SourcePaloAlto

if __name__ == "__main__":
    source = SourcePaloAlto()
    launch(source, sys.argv[1:])
