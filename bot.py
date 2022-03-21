from telebot import TeleBot
import psycopg2 as sql
import keyboards
import configs

bot = TeleBot(configs.TOKEN, parse_mode=configs.PARSE_MODE)
db = sql.connect(
    database='russian_today',
    host='localhost',
    user='postgres',
    password='123456'
)
cursor = db.cursor()


@bot.message_handler(commands=['start'])
def command_start(message):
    chat_id = message.chat.id
    first_name = message.chat.first_name
    message_to_user = f'Привет, {first_name}!\nэто новостной бот'
    bot.send_message(chat_id, message_to_user)
    choose_category(message)


def choose_category(message):
    chat_id = message.chat.id
    message_to_user = 'Выберите категорию:'

    cursor.execute('''
    select category_name
    from categories
    ''')

    categories = cursor.fetchall()

    category_markup = keyboards.generate_category_markup(categories)
    msg = bot.send_message(chat_id, message_to_user,
                           reply_markup=category_markup)
    bot.register_next_step_handler(msg, show_category)


def show_category(message):
    chat_id = message.chat.id
    category_name = message.text

    cursor.execute('''
    select title, description, date, author, article_link, image_link from articles
    join categories using(category_id)
    where category_name = %s
    ''', (category_name,))

    articles = cursor.fetchall()

    if articles:

        for article in articles:
            title = article[0]
            description = article[1]
            date = article[2]
            author = article[3]
            article_link = article[4]
            image_link = article[5]

            message_to_user = f'''<i>{date}</i>

<b>{title}</b>

{description}<a href="{article_link}">Подробнее</a>

<u>{author}</u>
'''
            link_markup = keyboards.generate_link_markup(article_link)
            msg = bot.send_photo(chat_id=chat_id,
                                 photo=image_link,
                                 caption=message_to_user,
                                 reply_markup=link_markup)

    else:
        msg = bot.send_message(chat_id, 'Такой категории не существует. Выберите из того, что есть!!!')

    bot.register_next_step_handler(msg, show_category)


print('Бот работает')
bot.polling()
db.close()
