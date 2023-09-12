import random
import datetime


class QuoteManager:
    def __init__(self, language):
        self.language = language
        self.quotes = self.load_quotes()
        print(self.quotes)

    def load_quotes(self):
        quote_file = "./resources/quotes/Quotes_"+self.language+".txt" # TODO translations
        with open(quote_file, "r") as file:
            quotes = file.readlines() 
            return quotes

    def get_quote(self):
            # Get seed
            today = datetime.date.today()
            split_date = str(today).split("-")
            seed = split_date[0]+split_date[1]+split_date[2]
            int(seed)

            random.seed(seed)
            return random.choice(self.quotes)
