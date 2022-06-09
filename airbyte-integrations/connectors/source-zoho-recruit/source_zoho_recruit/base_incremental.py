from abc import ABC, abstractmethod
from typing import Optional, Mapping, Any, Iterable, MutableMapping

import requests
from airbyte_cdk.sources.streams.http import HttpStream
