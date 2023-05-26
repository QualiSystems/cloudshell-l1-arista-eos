from __future__ import annotations


class AristaEOSBaseException(Exception):
    pass


class AristaEOSWrongParams(AristaEOSBaseException):
    pass


class AristaEOSAutoloadException(AristaEOSBaseException):
    pass


class AristaEOSMappingException(AristaEOSBaseException):
    pass
