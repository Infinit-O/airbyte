#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_google_enterprise_license_manager import SourceGoogleEnterpriseLicenseManager

if __name__ == "__main__":
    source = SourceGoogleEnterpriseLicenseManager()
    launch(source, sys.argv[1:])
