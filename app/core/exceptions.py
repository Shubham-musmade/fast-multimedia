from fastapi import HTTPException, status

class MediaServiceException(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class InvalidFileType(MediaServiceException):
    pass

class FileTooLarge(MediaServiceException):
    pass

class UploadLimitExceeded(MediaServiceException):
    pass

class FileNotFound(MediaServiceException):
    def __init__(self):
        super().__init__("File not found", status.HTTP_404_NOT_FOUND)

class UnauthorizedAccess(MediaServiceException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED)