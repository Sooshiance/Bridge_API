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
        self.dispatcher.add_handler(CommandHandler("help", self.help))
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.search))

    @staticmethod
    def search_expression(expression: str, language: str = None, path: str = None) -> list:
        base_url = "https://grep.app/api/search"
        params = {"q": expression}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        if language:
            params["lang"] = language
        if path:
            params["path"] = path

        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            response_json = response.json()
            results = response_json.get('results', [])
            logger.debug(f"API Response: {response_json}")
            return results[:100]  # Return top 100 results
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return []
        except ValueError as e:
            logger.error(f"Error parsing JSON: {e}")
            return []

    def start(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text('Hi! Send me an expression to search.')

    def help(self, update: Update, context: CallbackContext) -> None:
        help_text = (
            "Send me a search query in the format:n"
            "<expression>;[language];[path]nn"
            "Example:n"
            "print;python;src/nn"
            "You can omit language and path if not needed."
        )
        update.message.reply_text(help_text)

    def search(self, update: Update, context: CallbackContext) -> None:
        user_input = update.message.text.split(';')
        
        expression = user_input[0].strip()
        language = user_input[1].strip() if len(user_input) > 1 else None
        path = user_input[2].strip() if len(user_input) > 2 else None
        
        if not expression:
            update.message.reply_text('Please provide an expression to search.')
            return
        
        results = self.search_expression(expression, language, path)
        if results:
            reply = 'n'.join([f"{result['path']} - {result.get('snippet', 'No snippet available')}" for result in results])
        else:
            reply = 'No results found.'
            
        update.message.reply_text(reply)

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

if __name__ == '__main__':
    # Replace 'YOUR_TOKEN' with your actual bot token
    bot = GrepBot("YOUR_TOKEN")
    bot.run()
