import telebot
from scraper import *
import datetime
import threading
from dotenv import load_dotenv
import os

load_dotenv()
bot = telebot.TeleBot(os.getenv("API_TOKEN"), parse_mode="HTML")
channel_id = os.getenv("CHANNEL_ID")

tz = datetime.timezone(datetime.timedelta(hours=-5))
post_time = datetime.time(hour=10, tzinfo=tz)


def get_delay():
    p = datetime.datetime.combine(datetime.datetime.now(tz).date(), post_time)
    now = datetime.datetime.now(tz)

    delta = p - now
    if delta.total_seconds() > 0:
        return delta.total_seconds()
    else:
        day = datetime.timedelta(days=1).total_seconds()
        return day + delta.total_seconds()


class Cache:
    date = datetime.datetime.now(tz)
    data = scrape(date)

    def update(self, date):
        data = scrape(date)
        if data is not None:
            self.date = date
            self.data = data
            return True

        return False


cache = Cache()


def check_cache(date):
    global cache
    update = False
    if date != cache.date:
        update = cache.update(date)

    return cache.data, update


def check_date(date):
    earliest = datetime.date(2020, 9, 11)
    today = datetime.date.today()
    if date < earliest or date > today:
        return False
    return True


def get_data(date=datetime.datetime.now(tz), update=False):

    if not check_date(date):
        return None

    soup, is_update = check_cache(date)
    while soup is None:
        print(date)
        date -= datetime.timedelta(days=1)
        if not check_date(date):
            return None
        soup, is_update = check_cache(date)

    if soup is None:
        return None

    out = parse(cache.date, soup)
    if update:
        return out, is_update
    return out


def parse_date(string):
    x = string.split('/')
    if len(x) == 3:
        try:
            d, m, y = int(x[0]), int(x[1]), int(x[2])
            return datetime.datetime(y, m, d)
        except:
            return None
    return None


@bot.message_handler(commands=['report', 'summary', 'cases', 'parishes', 'sex', 'testing', 'deaths', 'recovered', 'active', 'quarantine', 'hospitals', 'transmission'])
def handle_command(message):
    data = get_data()
    commands = ['report', 'summary', 'cases', 'parishes', 'sex', 'testing', 'deaths', 'recovered', 'active',
                'quarantine', 'hospitals', 'transmission']
    command = message.text.replace("/", "")
    out = ""
    for c in commands:
        if c in command:
            if c == 'report':
                out = data.report()
            elif c == 'summary':
                out = data.summary()
            else:
                out = data.get_attr(c)
            break

    bot.send_message(message.chat.id, out)


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


def setup():
    t = get_delay()
    print("Posting in " + t + "seconds ( " + t / 60 / 60 + " hours)")
    threading.Timer(t, channel_post).start()


def channel_post():
    global cache

    data, update = get_data(update=True)

    if update:
        print("Posting to Channel")
        bot.send_message(channel_id, data.summary())
        bot.send_message(channel_id, data.get_sex_classification())
        bot.send_message(channel_id, data.get_parishes())
        bot.send_message(channel_id, data.get_testing())
        bot.send_message(channel_id, data.get_deaths())
        bot.send_message(channel_id, data.get_recoveries_active())
        bot.send_message(channel_id, data.get_quarantine())
        bot.send_message(channel_id, data.get_hospitals())
        bot.send_message(channel_id, data.get_transmission())

        threading.Timer(get_delay(), channel_post).start()

    else:
        print("5 Minute Delay")
        threading.Timer(300, channel_post).start()


setup()
bot.polling()
