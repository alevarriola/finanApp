class AppError(Exception):
    pass


class NotFoundError(AppError):
    pass


class UnauthorizedError(AppError):
    pass


class DuplicateError(AppError):
    pass


class ValidationError(AppError):
    pass
