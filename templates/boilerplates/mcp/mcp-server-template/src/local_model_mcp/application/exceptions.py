from __future__ import annotations


class ApplicationException(Exception):
    code = "application_error"


class CapabilityNotAllowed(ApplicationException):
    code = "capability_not_allowed"
