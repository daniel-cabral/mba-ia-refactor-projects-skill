class DomainError(Exception):
    status = 400


class UnauthorizedError(DomainError):
    status = 401


class ForbiddenError(DomainError):
    status = 403


class NotFoundError(DomainError):
    status = 404


class ConflictError(DomainError):
    status = 409
