import requests  # module for sending HTML responses
from bottle import Bottle, request as bottle_request  # accepting requests
from Files import FileHandler


class DefaultBotHandler:
    BOT_URL = None  # Bot URL for requests
    FILE_URL = None  # Bot URL for downloading files

    # Chat ID
    @staticmethod
    def get_chat_id(input_data):
        return input_data['message']['from']['id']

    # Message text
    @staticmethod
    def get_text(input_data):
        return input_data['message']['text']

    # File ID
    @staticmethod
    def get_file_id(input_data):
        pass

    # Error message
    @staticmethod
    def generate_err(chat_id, err_info):
        return {
            'chat_id': chat_id,
            'text': 'Error: \n' + err_info
        }

    # Could be used for efficiency of saving images
    def _save_file_on_servers(self, file_id):
        r = requests.post(self.BOT_URL + 'getFile', json={                  # Saving images on Telegram servers
            'file_id': file_id
        })
        return r.json()['result']['file_path']

    # Saving file from TG servers on device
    def download_image(self, file_id, result_path, file_name):
        file_path = self._save_file_on_servers(file_id)                     # Getting file path on Tg servers
        img = requests.get(self.FILE_URL + file_path, allow_redirects=True)
        FileHandler.save_image(img, result_path, file_name)                 # Saving image on device

    # Sending message method (accepting output_data as json) (Refactor needed)
    def send_message(self, output_data):
        print(output_data)

        if 'text' in output_data.keys():
            sm_url = self.BOT_URL + 'sendMessage'
            requests.post(sm_url, json=output_data)  # Sending request with json file
        elif 'document' in output_data.keys():
            sm_url = self.BOT_URL + 'sendDocument'
            r = requests.post(sm_url, data={'chat_id': output_data['chat_id']},
                              files={'document': (output_data['document'], open(output_data['document'], 'rb'))})

            FileHandler.delete_file(output_data['document'])
            print(r.text)

    # Process incoming data
    def _process_data(self, input_data):
        pass


class TestBot(DefaultBotHandler, Bottle):
    BOT_URL = 'https://api.telegram.org/bot2127420540:AAHpyxvTYSt4LNkW58t6Hn5FxyQwgb289QA/'
    FILE_URL = 'https://api.telegram.org/file/bot2127420540:AAHpyxvTYSt4LNkW58t6Hn5FxyQwgb289QA/'

    def __init__(self):
        super(TestBot, self).__init__()
        self.route('/', callback=self.post_handler, method='POST')

    # File ID
    @staticmethod
    def get_file_id(input_data):
        if 'photo' in input_data['message'].keys():
            return input_data['message']['photo'][-1]['file_id']
        elif 'document' in input_data['message'].keys():
            if input_data['message']['document']['file_name'].endswith('.png' or '.jpg' or '.jpeg'):
                return input_data['message']['document']['file_id']
            else:
                return 'Error'
        else:
            return 'Error'           # Replace with try_catch

    # Process incoming data -- Refactor saving images --
    def _process_data(self, input_data):
        chat_id = DefaultBotHandler.get_chat_id(input_data)  # User id
        # print('Accepted message from: ' + input_data['message']['from']['username'] + '(' + str(chat_id) + ')')

        if 'text' in input_data['message'].keys():
            text = DefaultBotHandler.get_text(input_data)
            dir_path = 'data_folder/' + str(chat_id) + '/'
            if text == '/compile':        # Compiling file and asking for name
                FileHandler.create_folder(dir_path + 'result/')
                FileHandler.compile_pdf(dir_path + 'photos/', dir_path + 'result/', 'temp')
                FileHandler.clear_folder('data_folder/' + str(chat_id) + '/photos/')
                return {
                    'chat_id': chat_id,
                    'text': 'Set file name'
                }

            elif text == '/clear':
                FileHandler.clear_folder(dir_path + 'photos/')
                FileHandler.clear_folder(dir_path + 'result/')
                return {
                    'chat_id': chat_id,
                    'text': 'Successfully cleared!'
                }
            elif not FileHandler.folder_size(dir_path + 'result/') == 0:        # If result already exists
                dir_path = dir_path + 'result/'
                FileHandler.rename_file(dir_path, 'temp.pdf', text + '.pdf')
                return {
                    'chat_id': chat_id,
                    'document': dir_path + text + '.pdf'
                }
            else:
                return self.generate_err(chat_id, 'Type error')
        else:
            dir_path = 'data_folder/' + str(chat_id) + '/'

            if not FileHandler.folder_size(dir_path + 'result/') == 0:              # Safety check if compiled pdf
                return self.generate_err(chat_id, 'Inappropriate type!')            # already exists

            FileHandler.create_folder(dir_path + 'photos')

            file_num = FileHandler.folder_size(dir_path + 'photos') + 1  # Number of file to be added

            if file_num > 50:  # Some another way?
                return self.generate_err(chat_id, """You can't upload more than 50 files!
                                                                      /clear previous images to send more.""")

            file_id = self.get_file_id(input_data)

            # Basic error if no format input                    # Must be replaced with try_catch
            if file_id == 'Error':
                return self.generate_err(chat_id, 'Type error')

            self.download_image(file_id, dir_path + 'photos/', str(file_num) + '.jpg')

            return {
                'chat_id': chat_id,
                'text': 'Image ' + str(file_num) + ' added successfully!'
            }

    # Post Handler
    def post_handler(self):
        input_data = bottle_request.json
        response_data = self._process_data(input_data)

        self.send_message(response_data)


if __name__ == '__main__':
    bot = TestBot()
    bot.run(host='localhost', port=8080)
