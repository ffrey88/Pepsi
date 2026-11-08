import telebot
import sqlite3
import os
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ ---
BOT_TOKEN = "9199244262:AAEANMSZuo1qSQwKaemzrAWmANBx8sr8Qlo" 
GROUP_ID = -1001234567890  # СЮДА_ВСТАВЬ_СВОЙ_ID_ГРУППЫ
# -----------------

bot = telebot.TeleBot(BOT_TOKEN)

conn = sqlite3.connect('support.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS messages
                  (group_msg_id INTEGER PRIMARY KEY, user_id INTEGER)''')
conn.commit()

@bot.message_handler(func=lambda message: message.chat.type == 'private', content_types=['text', 'photo', 'voice', 'video', 'document'])
def handle_user_message(message):
    user_id = message.chat.id
    try:
        if message.content_type == 'text':
            sent_msg = bot.send_message(GROUP_ID, f"📩 Сообщение:\n\n{message.text}")
        else:
            sent_msg = bot.copy_message(GROUP_ID, user_id, message.message_id, caption="📩 Медиа-сообщение:")
        
        cursor.execute("INSERT INTO messages (group_msg_id, user_id) VALUES (?, ?)", (sent_msg.message_id, user_id))
        conn.commit()
        bot.reply_to(message, "✅ Сообщение отправлено. Ожидай ответа.")
    except Exception as e:
        bot.reply_to(message, "⚠️ Ошибка. Попробуй позже.")

@bot.message_handler(func=lambda message: message.chat.id == GROUP_ID, content_types=['text', 'photo', 'voice', 'video', 'document'])
def handle_admin_reply(message):
    if message.reply_to_message:
        replied_msg_id = message.reply_to_message.message_id
        cursor.execute("SELECT user_id FROM messages WHERE group_msg_id = ?", (replied_msg_id,))
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            try:
                if message.content_type == 'text':
                    bot.send_message(user_id, f"💬 Ответ:\n\n{message.text}")
                else:
                    bot.copy_message(user_id, GROUP_ID, message.message_id, caption="💬 Ответ:")
                bot.reply_to(message, "✅ Доставлено.")
            except Exception:
                bot.reply_to(message, "⚠️ Пользователь заблокировал бота.")
        else:
            bot.reply_to(message, "⚠️ Не найдено в базе.")

@bot.message_handler(commands=['start'], func=lambda message: message.chat.type == 'private')
def send_welcome(message):
    welcome_text = (
        "В жизни на карте всегда есть крест, указывающий путь. Возможно, даже нарисованный не вами. "
        "Но бывает, крест смывает водой после ночлега у реки, или неудачно потрётся лист. "
        "После чего наступает тупик.\n\n"
        "Здесь вы можете найти в себе силы нарисовать новый крест - или оставить карту без него "
        "и жить свободно.\n\n"
        "Просто напишите сюда всё, что вас тревожит, и админы ответят вам.\n\n"
        "⚠️ *Важно:* мы не психологи. Если вам угрожает опасность, позвоните на бесплатную линию: 8-800-2000-122"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['rules'], func=lambda message: message.chat.type == 'private')
def send_rules(message):
    rules_text = (
        "📜 *Правила для путников:*\n\n"
        "1. *Анонимность - это святое.*\n"
        "Здесь не нужно называть свое настоящее имя, показывать лицо или делиться контактами. Вы можете говорить о чем угодно, но не переходите границы личной безопасности (своей и чужой).\n\n"
        "2. *Мы не спасатели, мы - попутчики.*\n"
        "Админы здесь не психологи и не врачи. Мы можем выслушать, поддержать и дать совет, но мы не можем вылечить. Если вы чувствуете, что земля уходит из-под ног - пожалуйста, обратитесь к профессионалам.\n\n"
        "3. *Уважение к попутчикам.*\n"
        "Здесь нет \"неправильных\" чувств, любая боль реальна. Однако наши проводники (админы) - тоже люди. Оскорбления, насмешки и обесценивание запрещены. Шутки допустимы, пока они не переходят в токсичность. Если проводник просит остановиться - вы обязаны остановиться.\n\n"
        "4. *Твоя карта - только твоя.*\n"
        "Мы не даем жестких указаний «как жить». Мы можем подсветить фонариком, но крестик на карте рисуете вы сами.\n\n"
        "5. *Правило \"Стоп\".*\n"
        "Если вы чувствуете, что разговор становится для вас слишком тяжелым, и вы не хотите продолжать - вы имеете право в любой момент сказать \"стоп\" и уйти. Вам не обязательно досказывать.\n\n"
        "6. *Конфиденциальность.*\n"
        "Всё, что говорится в этом боте, остается только в боте. Мы не выносим чужие истории на всеобщее обозрение."
    )
    bot.reply_to(message, rules_text, parse_mode='Markdown')

app = Flask(__name__)

@app.route('/')
def index():
    return "Бот работает!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

if __name__ == '__main__':
    keep_alive()
    print("Бот запущен...")
    bot.infinity_polling()
