import logging

import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class GrepBot:

    def __init__(self, token: str):
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher
        self._register_handlers()

    def _register_handlers(self):
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.search))

    @staticmethod
    def search_expression(expression: str, language: str = None, path: str = None) -> list:
        # Replace with the correct API endpoint
        base_url = "https://grep.app/api/search"
        params = {"q": expression}
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        if language:
            params["lang"] = language
        if path:
            params["path"] = path

        response = requests.get(base_url, params=params, headers=headers)

        # TODO: Add debugging statement
        logger.debug(response.json())

        try:
            response_json = response.json()
            results = response_json.get('results', [])
        
            # TODO: Return top 100 results.
            return results[:100]

        except ValueError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Response content: {response.text}")
            return []

    def start(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Hi! Send me an expression to search.')

    def search(self, update: Update, context: CallbackContext) -> None:

        # TODO: separate expression language path with semi colons
        user_input = update.message.text.split(';')
        
        expression = user_input[0]
        language = user_input[1] if len(user_input) > 1 else None
        path = user_input[2] if len(user_input) > 2 else None
        
        results = self.search_expression(expression, language, path)
        
        if results:
            reply = '\n'.join([result['path'] for result in results])
        else:
            reply = 'No results found.'
            
        update.message.reply_text(reply)

    def run(self):
        self.updater.start_polling()
        self.updater.idle()


if __name__ == '__main__':
    
    # TODO: Replace 'YOUR_TOKEN' with your actual bot token
    bot = GrepBot("YOUR_TOKEN")
    
    bot.run()
