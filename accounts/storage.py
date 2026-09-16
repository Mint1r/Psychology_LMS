from django.core.files.storage import FileSystemStorage
from Psychology.settings import BASE_DIR


""" Приватное хранилище """
private_storage = FileSystemStorage(
    location=BASE_DIR / "private_media"
)