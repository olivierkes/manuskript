import random
import datetime



quote_file = "./resources/quotes/Quotes_English.txt" # TODO translations
def load_quotes():
    with open(quote_file, "r") as file:
        quotes = file.readlines() 
        return quotes

quotes = load_quotes()
def get_quote():
    # Get seed
    today = datetime.date.today()
    split_date = str(today).split("-")
    seed = split_date[0]+split_date[1]+split_date[2]
    int(seed)

    random.seed(seed)
    return random.choice(quotes)
