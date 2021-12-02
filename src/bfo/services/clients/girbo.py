import logging

from requests import HTTPError
from requests_toolbelt import MultipartEncoder

from bfo.models import Setting
from .mixins import MakeRetrySessionMixin, AuthTokenMixin

girbo_logger = logging.getLogger('girbo_client')


class GirboClient(MakeRetrySessionMixin, AuthTokenMixin):
    cache_access_token_key = 'girbo_access_token'
    cache_timeout = 60 * 25

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setting = Setting.objects.last()
        self.make_retry_session()

    def get_access_token(self):
        girbo_logger.debug('GirboClient: get_access_token - start')
        multipart_data = MultipartEncoder(
            fields={
                'username': self.setting.username,
                'password': self.setting.password,
                'grant_type': "password",
            }
        )
        response = self.post(
            path='oauth/token',
            headers={
                'Authorization': 'Basic YXBpOjEyMzQ1Njc4OTA=',
                'Content-Type': multipart_data.content_type,
            },
            data=multipart_data,
            fail_silently=False
        )
        girbo_logger.debug('GirboClient: get_access_token - response: `%s`', response)
        '''
        response = {
            "access_token": "f9ea18de-5cc7-42f3-a091-071ee3b1fa80",
            "token_type": "bearer",
            "scope": "api"
        }
        '''
        return response['access_token']

    def get_authorization_header(self):
        authorization_header = {
            'Authorization': f'Bearer {self.get_access_token_with_cache()}',
        }
        girbo_logger.debug(
            'GirboClient: get_authorization_header - authorization_header: `%s`',
            authorization_header,
        )
        return authorization_header

    def get_statement_page(self, params):
        girbo_logger.debug(
            'GirboClient: get_statement_page - params: `%s` - start',
            params,
        )
        response = self.get(
            path='api/v1/files',
            params=params,
        )
        '''        
        response = {
            "content": [
                {
                    "id": 13,
                    "inn": 1234567890,
                    "fileName": "test13",
                    "fileType": "AZ",
                    "reportType": BFO_TKS,
                    "period": "2019",
                    "uploadDate": "2020-05-22",
                    "token": " 5df1ee2d46e0fb0001ac511f"
                },
                {
                    "id": 10,
                    "inn": 1234567890,
                    "fileName": "test10",
                    "fileType": "AZ",
                    "reportType": BFO_TKS,
                    "period": "2019",
                    "uploadDate": "2020-05-22",
                    "token": " 5df1ee2d46e0fb0001ac5121"
                }
            ],
            "totalPages": 1,
            "totalElements": 2,
            "sort": "inn: DESC,uploadDate: DESC",
            "page": 0,
            "size": 2
        }
        '''
        girbo_logger.debug(
            'GirboClient: get_list_of_statement_documents - params: `%s` - successfully received. Page `%s` of `%s`.',
            params,
            response['page'],
            response['totalPages'],
        )
        return response

    def get_statement_file(self, file_token):
        girbo_logger.debug(
            'GirboClient: get_statement_file - file_token: `%s` - start',
            file_token,
        )
        file = self.get(
            path=f'api/v1/files/{file_token}/',
            return_response_obj=True,
        )
        girbo_logger.debug(
            'GirboClient: get_statement_file - file_token: `%s` - successfully received',
            file_token,
        )
        return file

    def get_response(self, path, request_type, headers, params=None):
        url = '{base_url}{path}'.format(
            base_url=self.setting.base_url,
            path=path,
        )
        default_params = {
            'url': url,
            'headers': headers,
            'verify': False,
        }

        response = None
        if request_type == 'get':
            response = self.retry_get(
                params=params,
                **default_params
            )
        if request_type == 'post':
            response = self.retry_post(
                data=params,
                **default_params
            )

        response.raise_for_status()
        return response

    def get(self, path, headers=None, params=None, fail_silently=False, return_response_obj=False):
        try:
            max_retries = 3
            for retry_step in range(1, max_retries + 1):
                if headers is None:
                    headers = {}
                headers.update(
                    **self.get_authorization_header(),
                )
                try:
                    response = self.get_response(
                        path=path,
                        request_type='get',
                        headers=headers,
                        params=params,
                    )
                    if return_response_obj:
                        return response

                    json_response = response.json()
                    if isinstance(json_response, list) and len(json_response) == 1:
                        json_response = json_response[0]
                    return json_response
                except HTTPError as e:
                    if not e.response.status_code == 401:
                        girbo_logger.error(
                            'GirboClient: Error status_code = `%s`, exception: `%s`',
                            e.response.status_code,
                            e,
                        )
                        raise e
                    self.clear_cache_token()

        except Exception as e:
            girbo_logger.error(
                'GirboClient: get - path: `%s` - exception: `%s`',
                path,
                e,
            )
            if fail_silently:
                return {}
            raise e
        return None

    def post(self, path, headers=None, data=None, fail_silently=False, return_response_obj=False):
        try:
            response = self.get_response(
                path=path,
                request_type='post',
                headers=headers,
                params=data,
            )
            if return_response_obj:
                return response

            json_response = response.json()
            if isinstance(json_response, list) and len(json_response) == 1:
                json_response = json_response[0]

        except Exception as e:
            girbo_logger.error(
                'GirboClient: post - path: `%s` - exception: `%s`',
                path,
                e,
            )
            if fail_silently:
                return {}
            raise e
        return json_response
