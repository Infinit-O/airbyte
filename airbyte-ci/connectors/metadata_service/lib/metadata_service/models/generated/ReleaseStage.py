#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

# generated by datamodel-codegen:
#   filename:  ReleaseStage.yaml

from __future__ import annotations

from pydantic import BaseModel, Field
from typing_extensions import Literal


class ReleaseStage(BaseModel):
    __root__: Literal["alpha", "beta", "generally_available", "custom"] = Field(
        ...,
        description="enum that describes a connector's release stage",
        title="ReleaseStage",
    )
