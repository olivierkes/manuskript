import random
import datetime




def load_quotes(language):
    quote_file = "./resources/quotes/Quotes_"+language+".txt" # TODO translations
    with open(quote_file, "r") as file:
        quotes = file.readlines() 
        return quotes

quotes = load_quotes('English')
def get_quote():
    # Get seed
    today = datetime.date.today()
    split_date = str(today).split("-")
    seed = split_date[0]+split_date[1]+split_date[2]
    int(seed)

    random.seed(seed)
    return random.choice(quotes)
