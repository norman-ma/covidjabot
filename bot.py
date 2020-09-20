import telebot
from scraper import *
import datetime
import time, threading

bot = telebot.TeleBot("1371484351:AAHfwEo7BRGD_Z9mEdUPy0AEnwJ1UXRR7fc", parse_mode="HTML")
channel_id = "-1001360940176"

def get_data(date=datetime.datetime.today(), search=True):
    soup = scrape(date)
    count = 0
    while soup is None and search and count < 7:
        date -= datetime.timedelta(days=1)
        soup = scrape(date)
        count += 1

    if soup is None:
        return None

    return parse(date, soup)


def parse_date(string):
    x = string.split('/')
    if len(x) == 3:
        try:
            d, m, y = int(x[0]), int(x[1]), int(x[2])
            return datetime.datetime(y, m, d)
        except:
            return None
    return None


@bot.message_handler(commands=['report'])
def report(message):
    data = get_data()
    r = data.report()
    bot.send_message(message.chat.id, r)


@bot.message_handler(commands=['summary'])
def summary(message):
    data = get_data()
    r = data.summary()
    bot.send_message(message.chat.id, r)


@bot.message_handler(commands={"cases"})
def cases(message):
    data = get_data()
    r = data.get_cases()
    bot.send_message(message.chat.id, r)


@bot.message_handler(commands={"parishes"})
def parishes(message):
    data = get_data()
    r = data.get_parishes()
    bot.send_message(message.chat.id, r)


@bot.message_handler(commands={"sex"})
def sex_classification(message):
    data = get_data()
    r = data.get_sex_classification()
    bot.send_message(message.chat.id, r)


@bot.message_handler(commands={"testing"})
def testing(message):
    data = get_data()
    r = data.get_testing()
    bot.send_message(message.chat.id, r)


@bot.message_handler(commands={"deaths"})
def deaths(message):
    data = get_data()
    r = data.get_testing()
    bot.send_message(message.chat.id, r)


@bot.message_handler(commands={"recovered", "active"})
def ra(message):
    data = get_data()
    r = data.get_recoveries_active()
    bot.send_message(message.chat.id, r)


@bot.message_handler(commands={"quarantine"})
def quarantine(message):
    data = get_data()
    r = data.get_quarantine()
    bot.send_message(message.chat.id, r)


@bot.message_handler(commands={"hospials"})
def hospitals(message):
    data = get_data()
    r = data.get_hospitals()
    bot.send_message(message.chat.id, r)


@bot.message_handler(commands={"transmission"})
def transmission(message):
    data = get_data()
    r = data.get_transmission()
    bot.send_message(message.chat.id, r)


@bot.inline_handler(func=lambda chosen_inline_result: True)
def query_text(inline_query):
    date = parse_date(inline_query.query)
    if date is None:
        response = telebot.types.InlineQueryResultArticle(1, 'Improper Date Format', telebot.types.InputTextMessageContent("Please use date format: dd/mm/yyyy"))
        bot.answer_inline_query(inline_query.id, [response])
    else:
        data = get_data(date)
        if data is not None:
            response1 = telebot.types.InlineQueryResultArticle(2, 'Summary', telebot.types.InputTextMessageContent(data.summary()))
            response2 = telebot.types.InlineQueryResultArticle(3, 'Report', telebot.types.InputTextMessageContent(data.report()))
            bot.answer_inline_query(inline_query.id, [response1, response2])
        else:
            response = telebot.types.InlineQueryResultArticle(4, 'Date Not Found', telebot.types.InputTextMessageContent("No response found for " + date.strftime("%A, %B %d, %Y")))
            bot.answer_inline_query(inline_query.id, [response])


WAIT_TIME = 60 * 60 * 8


def channelPost():
    print("Posting to Channel")
    data = get_data()

    bot.send_message(channel_id, data.summary())
    bot.send_message(channel_id, data.get_sex_classification())
    bot.send_message(channel_id, data.get_parishes())
    bot.send_message(channel_id, data.get_testing())
    bot.send_message(channel_id, data.get_deaths())
    bot.send_message(channel_id, data.get_recoveries_active())
    bot.send_message(channel_id, data.get_quarantine())
    bot.send_message(channel_id, data.get_hospitals())
    bot.send_message(channel_id, data.get_transmission())

    threading.Timer(WAIT_TIME, channelPost).start()


channelPost()
bot.polling()
