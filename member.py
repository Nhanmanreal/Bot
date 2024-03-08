import telegram
import telebot
import datetime
import time
import os
import hashlib
import subprocess
import psutil
import base64
import requests
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler,CallbackQueryHandler

bot_token = '6962047277:AAHnBGVg4LTkFVVQnHmQOVHDey9gAgDH_-o'  # Thay YOUR_BOT_TOKEN bằng mã token của bot Telegram của bạn
bot = telegram.Bot(token=bot_token)

allowed_group_id = -1001897361189  # Thay YOUR_GROUP_ID bằng ID của nhóm bạn muốn bot hoạt động trong đó

allowed_users = []
processes = []
ADMIN_ID = 6622548678  # Thay 123456789 bằng ID của admin

# Kết nối đến cơ sở dữ liệu SQLite
connection = sqlite3.connect('user_data.db')
cursor = connection.cursor()

# Tạo bảng người dùng nếu chưa tồn tại
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        expiration_time TEXT
    )
''')
connection.commit()

def TimeStamp():
    now = str(datetime.date.today())
    return now

def load_users_from_database():
    cursor.execute('SELECT user_id, expiration_time FROM users')
    rows = cursor.fetchall()
    for row in rows:
        user_id = row[0]
        expiration_time = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        if expiration_time > datetime.datetime.now():
            allowed_users.append(user_id)

def save_user_to_database(connection, user_id, expiration_time):
    cursor = connection.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, expiration_time)
        VALUES (?, ?)
    ''', (user_id, expiration_time.strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()

def add_user(update, context):
    admin_id = update.message.from_user.id
    if admin_id != ADMIN_ID:
        update.message.reply_text('Bạn không có quyền sử dụng lệnh này.')
        return

    if len(context.args) == 0:
        update.message.reply_text('Vui lòng nhập ID người dùng.')
        return

    user_id = int(context.args[0])
    allowed_users.append(user_id)
    # Lưu thông tin người dùng vào cơ sở dữ liệu với thời gian hết hạn là sau 30 ngày
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=30)
    connection = sqlite3.connect('user_data.db')
    save_user_to_database(connection, user_id, expiration_time)
    connection.close()

    update.message.reply_text(f'Người dùng có ID {user_id} đã được thêm vào danh sách được phép sử dụng lệnh /sms.')

# Gọi hàm load_users_from_database để tải danh sách người dùng từ cơ sở dữ liệu
load_users_from_database()

# Dictionary to store the last used time for each phone number
last_used_times = {}

def khanh(update, context):
    # Kiểm tra xem người dùng có trong danh sách được phép hay không
    user_id = update.message.from_user.id
    if user_id not in allowed_users:
        update.message.reply_text('Bạn không có quyền sử dụng lệnh này /how để xem hướng dẫn.')
        return

    # Kiểm tra xem bot đang hoạt động trong nhóm đúng hay không
    if update.message.chat_id != allowed_group_id:
        update.message.reply_text('Bot chỉ hoạt động trong nhóm này https://t.me/kun_smsfree')
        return

    # Kiểm tra số lượng tham số đầu vào
    if len(context.args) != 2:
        update.message.reply_text("Vui lòng nhập đúng định dạng. Ví dụ: [/sms 0987654321 5]")
        return

    phone_number = context.args[0]
    spam_time = context.args[1]

    # Kiểm tra định dạng số điện thoại
    if not phone_number.isdigit() or len(phone_number) != 10:
        update.message.reply_text("Vui lòng nhập số điện thoại đúng định dạng 10 chữ số.")
        return

    # Kiểm tra định dạng thời gian spam
    if not spam_time.isdigit() or int(spam_time) > 49:
        update.message.reply_text("Vui lòng nhập số phút (nhỏ hơn 50) sau lệnh [/sms]. Ví dụ: [/sms 0987654321 5]")
        return

    if phone_number in ['113', '114', '0376349783', '0333079921', '0974707985', '0915215448', '+84397333616', '+84915215448', '+84974707985', '0978551717', '116', '911']:
        # Số điện thoại nằm trong danh sách cấm
        update.message.reply_text("Số này nằm trong danh sách cấm. Vui lòng nhập số khác.")
        return

    current_time = time.time()

    if phone_number in last_used_times:
        last_used_time = last_used_times[phone_number]
        if current_time - last_used_time < 300:
            # Thông báo cho người dùng rằng số đang trong quá trình tấn công, cần chờ thời gian
            remaining_time = int(300 - (current_time - last_used_time))
            update.message.reply_text(f"Number {phone_number} Đang Trong Quá Trình Tấn Công. Vui Lòng Chờ {remaining_time} Giây Mới Tấn Công Được Lần Hai.")
            return

    user_mention = update.message.from_user.mention_html()
    hi = f'''
-https://toolscommand-2024.000webhostapp.com/kuncrows.mp4
🚀 Attack Sent Successfully 🚀 
 Bot 🤖: @panelfree_kuncrows_bot
 Users 👤 :[ {user_mention} ]
 Target 📱 : [ {phone_number} ]
 Repeats ⚔️:[ {spam_time} ]
 Plan 💸:  [ FREE ] 
 Cooldown ⏱: [ 60s ]
 Owner & Dev 👑 : Vu Hai Lam 
'''

    update.message.reply_text(text=hi, parse_mode=telegram.ParseMode.HTML)
    last_used_times[phone_number] = current_time

    # Chạy file sms.py
    file_path = os.path.join(os.getcwd(), "sms.py")
    process = subprocess.Popen(["python", file_path, phone_number, "100"])
    processes.append(process)

def menu_to(update, context):
    help_text = '''
┏━━━━━━━━━━━━━━━━━━━━┓
┣➤ Để Sử Dụng Spam call thì dùng lệnh 
┣➤/sms 0877239630 5 
┣➤ trong đó 0877239630 là sdt muốn spam 
┣➤ còn số 5 là tựa chưng cho số phút spam
┗━━━━━━━━━━━━━━━━━━━━┛
┏━━━━━━━━━━━━━━━━━━━━┓
┣➤ Để Sử Dụng Spam Thì Lấy Key
┣➤ /getkey Để Lấy Key
┣➤ /key Để Nhập Key
┣➤ 1 Key Spam Được 24H
┗━━━━━━━━━━━━━━━━━━━━┛
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┣➤ Để Mua Key Vip 
┣➤ /muakey Để Mua Key Vip
┣➤ Để Sử Dụng Tools VIP Không Giới Hạn Gõ /muakey
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
'''

def hoatdong_to(update, context):
    help_text = '''
Bot đang hoạt động.
'''

    update.message.reply_text(text=help_text)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler, CommandHandler

def muakey(update, context):
    chat_id = update.effective_chat.id
    if update.message.chat.type == 'private':
        keyboard = [[InlineKeyboardButton("Momo", callback_data='momo'),
                     InlineKeyboardButton("Mbbank", callback_data='mbbank')]]

        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=chat_id, text='Chọn phương thức thanh toán:', reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=chat_id, text='Vui lòng sử dụng lệnh /muakey trong chat riêng để nhận được hướng dẫn thanh toán.')

def button(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id

    if query.data == 'momo':
        momo_message = f'''Thông tin thanh toán Momo:
Số tài khoản: 0333078199
Họ tên chủ tài khoản: VU HAI LAM 
Nội dung chuyển khoản của bạn: id{chat_id}
Số tiền: 15.000vnđ'''

        context.bot.send_message(chat_id=chat_id, text=momo_message)

    elif query.data == 'mbbank':
        mbbank_message = f'''Thông tin thanh toán MBBank:
Số tài khoản: 5000189408
Họ tên chủ tài khoản: VU HAI LAM  
Nội dung chuyển khoản của bạn: id{chat_id}
Số tiền: 15.000vnđ'''

        context.bot.send_message(chat_id=chat_id, text=mbbank_message)

    
def status(update, context):
    admin_id = update.message.from_user.id
    if admin_id != ADMIN_ID:
        update.message.reply_text('Bạn không có quyền sử dụng lệnh này.')
        return
    uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime_text = f"Bot đã hoạt động trong {uptime}"

    cpu_usage = psutil.cpu_percent()
    cpu_text = f"CPU Đang Dùng: {cpu_usage}%"
    
    memory_usage = psutil.virtual_memory().percent
    memory_text = f"Memory Đang Dùng: {memory_usage}%"
    
    disk_usage = psutil.disk_usage('/').percent
    disk_text = f"Disk Đang Dùng: {disk_usage}%"
    
    status_text = f"{uptime_text}\n{cpu_text}\n{memory_text}\n{disk_text}"
    update.message.reply_text(text=status_text)

def check(update, context):
    admin_id = update.message.from_user.id
    if admin_id != ADMIN_ID:
        update.message.reply_text('Bạn không có quyền sử dụng lệnh này.')
        return
    process_count = len(processes)
    update.message.reply_text(text=f'{process_count} Số điện thoại đang spam')

def admin_info(update, context):
    admin_name = '''- ADMIN 👾💻
    + Administrator : KUN CROWS
    '''
    admin_contact = '''- Thông Tin Liên Hệ 📞
    + Zalo : 0933514752'''

    message = f"{admin_name}\n {admin_contact}"
    update.message.reply_text(text=message)

def grant_permission(update, context):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        update.message.reply_text('Bạn không có quyền sử dụng lệnh này.')
        return

    if len(context.args) == 0:
        update.message.reply_text('Vui lòng nhập ID người dùng.')
        return

    user_id = int(context.args[0])
    allowed_users.append(user_id)
    update.message.reply_text(f'Người dùng có ID {user_id} đã được cấp quyền sử dụng lệnh /sms mà không cần đợi thời gian giữa các lần sử dụng.')


def stop(update, context):
    user_id = update.message.from_user.id
    if user_id not in allowed_users:
        update.message.reply_text('Bạn không có quyền sử dụng lệnh này.')
        return

    text = update.message.text.strip().replace(' ', '')
    numbers = [char for char in text if char.isdigit()]

    if len(numbers) != 10:
        update.message.reply_text('Vui lòng điền số cần dừng.')
    else:
        # Perform the action to stop the specified numbers
        # ...

        update.message.reply_text(f'Đã dừng số điện thoại: {"".join(numbers)}')



def remove_user(update, context):
    admin_id = update.message.from_user.id
    if admin_id != ADMIN_ID:
        update.message.reply_text('Bạn không có quyền sử dụng lệnh này.')
        return

    if len(context.args) == 0:
        update.message.reply_text('Vui lòng nhập ID người dùng.')
        return

    user_id = int(context.args[0])
    if user_id in allowed_users:
        allowed_users.remove(user_id)
        connection = sqlite3.connect('user_data.db')
        cursor = connection.cursor()
        cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        connection.commit()
        connection.close()
        update.message.reply_text(f'Người dùng có ID {user_id} đã được xóa khỏi danh sách được phép sử dụng lệnh /sms.')
    else:
        update.message.reply_text(f'Người dùng có ID {user_id} không tồn tại trong danh sách được phép sử dụng lệnh /sms.')

def user_list(update, context):
    admin_id = update.message.from_user.id
    if admin_id != ADMIN_ID:
        update.message.reply_text('Bạn không có quyền sử dụng lệnh này.')
        return

    if len(allowed_users) == 0:
        update.message.reply_text('Danh sách người dùng được phép sử dụng lệnh /sms hiện đang trống.')
        return

    user_list_text = 'Danh sách người dùng được phép sử dụng lệnh /sms:\n'
    for user_id in allowed_users:
        user = bot.get_chat_member(allowed_group_id, user_id)
        user_list_text += f'- ID: {user.user.id}, Tên: {user.user.first_name} {user.user.last_name}\n'
    update.message.reply_text(user_list_text)

def plan(update, context):
    reply_text = 'Giá cả của các gói dịch vụ tất cả đều chát admin @kun_dzll:\n\n'
    reply_text += '- Gói /sms: 15k/1 tháng\n'
    reply_text += '- Gói /sms: 100k/ Không giới hạn\n'
    reply_text += '- Thuê DDoS 50k/1 tháng ( time DDoS 120s - time chờ 240s)\n'
    reply_text += '- Thuê BOT tự làm admin 50k/tháng\n'
    reply_text += '- Mua src để làm bot có code getkey sẵng 150k\n'
    update.message.reply_text(reply_text)

def generate_key(user_id):
    today = datetime.date.today().strftime("%Y-%m-%d")
    key_string = f"{user_id}-{today}"
    key = hashlib.sha256(key_string.encode()).hexdigest()
    return key

def process_key(update, context):
    text = update.message.text.split()

    if len(text) >= 2 and text[0].strip() == "/key":
        key = text[1].strip()

        if key == "":
            update.message.reply_text('Vui lòng nhập key. Ví dụ: /key keycuaban\nNếu bạn chưa nhận key, vui lòng nhấp /getkey để nhận key.')
        else:
            encoded_user_id = base64.b64encode(str(update.effective_user.id).encode()).decode()

            if key == generate_key(encoded_user_id):
                # Xác thực key thành công
                connection = sqlite3.connect('user_data.db')
                expiration_time = datetime.datetime.now() + datetime.timedelta(days=1)
                user_id = update.effective_user.id
                allowed_users.append(user_id)
                save_user_to_database(connection, user_id, expiration_time)
                connection.close()

                # Số lượng người dùng đã xác thực key
                num_users = len(allowed_users)

                # Gửi id_chat của người dùng vào group_id
                group_id = "-1001897361189"  # Replace with your actual group ID
                context.bot.send_message(chat_id=group_id, text=f'Người dùng ID: {update.message.chat_id} đã xác thực key thành công')

                update.message.reply_text(f'Xác thực key thành công. Cảm ơn đã ủng hộ. Hiện có {num_users} người đã xác thực key bây giờ bạn có thể dùng lệnh /sms.')
            else:
                update.message.reply_text('Xác thực key thất bại. Nếu chưa nhận key, vui lòng nhấp /getkey để nhận key.')


  

def get_key(update, context):
    # Mã hóa id người dùng lệnh
    encoded_id = base64.b64encode(str(update.effective_user.id).encode()).decode()
    key = generate_key(encoded_id)

    # Kiểm tra xem tin nhắn được gửi từ nhóm hay riêng tư
    if update.message.chat.type == 'private':
        # Nếu là cuộc trò chuyện riêng tư, xử lý nhận key
        long_url = f"https://getkeyv2-2024.000webhostapp.com/key.html?key={key}"
        api_token = '2a518ced-fa94-433f-af99-9392b645333b'
        url = requests.get(f'https://web1s.com/api?token={api_token}&url={long_url}').json()
        link = url['shortenedUrl']

        # Gửi giá trị của biến link về cho người dùng riêng tư
        update.message.reply_text(f"-https://toolscommand-2024.000webhostapp.com/kun_dzll.mp4 || Link key Của Bạn Là: {link} Sau Khi Vượt Link Thành Công Thì [/key keyhomnay] Để Xác Thực Key.")
    else:
        # Nếu là tin nhắn từ nhóm, gửi thông báo yêu cầu nhắn riêng
        user_id = update.effective_user.id
        button_text = "Nhắn Tin Riêng Để Get Key"
        button_url = f"t.me/panelfree_kuncrows_bot?start={user_id}"
        keyboard = [[InlineKeyboardButton(button_text, url=button_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Gửi thông báo yêu cầu nhắn riêng tới nhóm
        update.message.reply_text("Vui lòng nhắn riêng với bot để nhận key.", reply_markup=reply_markup, parse_mode='HTML')




def main():
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher

    menu_handler = CommandHandler('menu', menu_to)
    dispatcher.add_handler(menu_handler)

    hoatdong_handler = CommandHandler('hoatdong', hoatdong_to)
    dispatcher.add_handler(hoatdong_handler)

    muakey_handler = CommandHandler('muakey', muakey)
    dispatcher.add_handler(muakey_handler)

    button_handler = CallbackQueryHandler(button)
    dispatcher.add_handler(button_handler)

    khanh_handler = CommandHandler('sms', khanh)
    dispatcher.add_handler(khanh_handler)

    admin_handler = CommandHandler('admin', admin_info)
    dispatcher.add_handler(admin_handler)

    grant_handler = CommandHandler('grant', grant_permission)
    dispatcher.add_handler(grant_handler)

    add_user_handler = CommandHandler('adduser', add_user)
    dispatcher.add_handler(add_user_handler)

    menu_handler = CommandHandler('menu', menu_to)
    dispatcher.add_handler(menu_handler)

    status_handler = CommandHandler('status', status)
    dispatcher.add_handler(status_handler)

    stop_handler = CommandHandler('stop', stop)
    dispatcher.add_handler(stop_handler)


    check_handler = CommandHandler('check', check)
    dispatcher.add_handler(check_handler)

    remove_user_handler = CommandHandler('removeuser', remove_user)
    dispatcher.add_handler(remove_user_handler)

    user_list_handler = CommandHandler('userlist', user_list)
    dispatcher.add_handler(user_list_handler)

    plan_handler = CommandHandler('plan', plan)
    dispatcher.add_handler(plan_handler)

    key_handler = CommandHandler('key', process_key)
    dispatcher.add_handler(key_handler)

    getkey_handler = CommandHandler('getkey', get_key)
    dispatcher.add_handler(getkey_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()