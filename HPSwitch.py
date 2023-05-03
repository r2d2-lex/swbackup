"""
    Класс для коммутатора HPE Office Connect 1820
"""
from functools import wraps
import logging
import requests
import config

logging.basicConfig(level=logging.INFO)


class HPSwitch:
    OPERATION_STATUS_UPLOAD_RESPONSE = 'successful'
    ERROR_MESSAGES_UPLOAD_RESPONSE = 'errorMsgs'
    CPU_STRING = 'id="cpu_util_prog_bar_val">'
    MEMORY_STRING = 'id="mem_util_prog_bar_val">'
    TRANSFER_STATUS = 'xferStatus'

    def __init__(self, switch_name, switch_username, switch_password, tftp_server, config_filename):
        self.switch_name = switch_name
        self.switch_username = switch_username
        self.switch_password = switch_password
        self.tftp_server = tftp_server
        self.config_filename = config_filename

        self.url = 'http://' + self.switch_name
        self.url_login = self.url + '/htdocs/login/login.lua'
        self.url_data = self.url + '/htdocs/pages/base/support.lsp'
        self.url_logout = self.url + '/htdocs/pages/main/logout.lsp'
        self.file_upload_ajax = self.url + '/htdocs/lua/ajax/file_upload_ajax.lua?protocol=1'
        self.url_status_file_transfer_tftp = self.url + '/htdocs/lua/ajax/file_transfer_ajax.lua?json=1'

    def check_authenticated(func):
        @wraps(func)
        def wrap(self, *args, **kwargs):
            if self.login_session:
                return func(self, *args, **kwargs)
            else:
                logging.info('Not authenticated...')
                return
        return wrap

    def __enter__(self):
        self.session = requests.Session()
        if self.session:
            self.session.trust_env = False
            self.login_session = self.login()
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.login_session:
            self.logout()
            logging.debug('Connection closed...')

    @check_authenticated
    def upload_to_tftp(self):
        result = ''
        file_transfer_fields = dict({
            'file_type_sel[]': 'config',
            'transfer_server_addr': self.tftp_server,
            'transfer_file_name': self.config_filename,
        })

        try:
            file_upload_result = self.session.post(self.file_upload_ajax, data=file_transfer_fields)
            print(f'Status code of url {self.file_upload_ajax}: {file_upload_result.status_code}')
            if file_upload_result.status_code == 200:

                try:
                    result_json = file_upload_result.json()
                    logging.debug(result_json)
                    if self.OPERATION_STATUS_UPLOAD_RESPONSE in result_json:
                        operation_status = bool(result_json[self.OPERATION_STATUS_UPLOAD_RESPONSE])
                        if operation_status:
                            logging.info(f'Start backup config: {self.config_filename}')

                            file_transfer_status = self.session.get(self.url_status_file_transfer_tftp)
                            logging.debug(f'Status code of url {self.url_status_file_transfer_tftp} : {file_transfer_status.status_code}')
                            if file_transfer_status.status_code == 200:
                                status_json = file_transfer_status.json()
                                logging.debug(f'status_json: {status_json}')
                                if self.TRANSFER_STATUS in status_json:
                                    result = str(status_json[self.TRANSFER_STATUS])
                                    logging.info(f'Результат передачи: {result}')
                                    return result
                        else:
                            logging.info(f'Error backup config: {result_json[self.ERROR_MESSAGES_UPLOAD_RESPONSE]}')
                except (ValueError, KeyError):
                    logging.info('Ошибка данных')
        except requests.RequestException:
            logging.info('Ошибка сети')
        return result

    @check_authenticated
    def get_cpu(self):
        html = self.login_session.text
        search_cpu_str = html.find(self.CPU_STRING)
        cpu_str_len = len(self.CPU_STRING)
        cpu_value = self.login_session.text[search_cpu_str + cpu_str_len:(search_cpu_str + cpu_str_len + 2)]
        logging.info(f'CPU_value(%): {cpu_value}')

    @check_authenticated
    def get_mem(self):
        html = self.login_session.text
        search_memory_string = html.find(self.MEMORY_STRING)
        memory_string_length = len(self.MEMORY_STRING)
        memory = self.login_session.text[search_memory_string + memory_string_length:(search_memory_string + memory_string_length + 2)]
        logging.info(f'Memory(%): {memory}')

    def login(self):
        data = {'username': self.switch_username, 'password': self.switch_password}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        login_url = self.url_login
        response_login = self.session.post(login_url, data, headers)
        if response_login.status_code == 200:
            response_data = self.session.post(self.url_data)
            return response_data

    def logout(self):
        self.session.post(self.url_logout)
        self.session.close()


if __name__ == "__main__":
    config_name = 'test123.cfg'
    with HPSwitch('127.0.0.1',
                  config.USERNAME,
                  config.PASSWORD,
                  config.TFTP_SERVER,
                  config_name
                  ) as switch:
        status = switch.upload_to_tftp()
        if status:
            message = f'Success upload config {config_name} on {config.TFTP_SERVER}'
        else:
            message = f'Error upload config {config_name} on {config.TFTP_SERVER}'
        logging.info(message)
