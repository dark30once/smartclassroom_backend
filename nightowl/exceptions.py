from werkzeug.exceptions import (Unauthorized, InternalServerError, NotFound,
                                 BadRequest)

class MyBaseException(Exception):
    def __init__(self, description="Really unexpected error."):
        super().__init__(self)
        self.description = description

    def __str__(self):
        return "{}".format(self.description)


class NotFoundError(MyBaseException, NotFound):
    """Raised when a resource couldn't be found"""
    def __init__(self, description="The resource could not be found."):
        super().__init__(self)
        self.description = description


class InvalidDataError(MyBaseException, BadRequest):
    """Raised when we received bad data."""
    def __init__(self, description="You sent invalid data."):
        super().__init__(self)
        self.description = description


class UnauthorizedError(MyBaseException, Unauthorized):
    """Raised upon unauthorized access to the application."""
    def __init__(self, description="You are not authorized to access this page."):
        super().__init__(self)
        self.description = description


class UnexpectedError(MyBaseException, InternalServerError):
    """Raised upon unexpected errors in the application."""
    def __init__(self, description="Something went wrong on the server while trying to access this page. Please inform the administrators."):
        super().__init__(self)
        self.description = description
