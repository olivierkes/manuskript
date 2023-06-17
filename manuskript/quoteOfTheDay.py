import random
import datetime

# Get seed
today = datetime.date.today()
split_date = str(today).split("-")
seed = split_date[0]+split_date[1]+split_date[2]
int(seed)

random.seed(seed)

quote_file = "./resources/quotes/Quotes_English.txt" # TODO translations
def load_quotes():
    file = open(quote_file, "r")
    text = file.read()
    quotes = text.split("\END")
    return quotes

quotes = load_quotes()
def get_quote():
    return random.choice(quotes)