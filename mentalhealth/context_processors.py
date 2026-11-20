from django.conf import settings
from detector.cloud_api import configured

def storage_status(request):
    return {"storage_enabled": settings.PERSISTENT_STORAGE_ENABLED, "cloud_enabled": configured()}
