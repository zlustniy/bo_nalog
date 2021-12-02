from wsgiref.util import FileWrapper

from django.conf import settings
from django.db.models.fields.files import FieldFile
from django.http import HttpResponse


class FileResponse:
    @staticmethod
    async def get_response(file_obj: FieldFile) -> HttpResponse:
        if not settings.USE_NGINX_FOR_SERVE_MEDIA:
            # noinspection PyTypeChecker
            return HttpResponse(FileWrapper(file_obj))
        response = HttpResponse()
        response['X-Accel-Redirect'] = file_obj.url
        return response
