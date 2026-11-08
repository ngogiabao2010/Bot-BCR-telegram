import os
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Token Bot chính xác của bạn
TOKEN = '9123735744:AAFSdlWhFxrXYkv7H_QSr0Uo9emx4Y-lQg4'
bot = telebot.TeleBot(TOKEN)

# Bộ nhớ tạm lưu lịch sử cầu của từng user: {chat_id: ['B', 'P', 'T', ...]}
user_histories = {}

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Baccarat Smart Engine Pro v10 đang hoạt động 24/7!"

# --- NHẬN TÍN HIỆU TỪ TELEGRAM GỬI VỀ QUA WEBHOOK ---
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        return "Invalid signature", 403

def get_keyboard():
    """Tạo bộ khung nút bấm: Player bên trái, Banker bên phải"""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔵 Player", callback_data="btn_player"),
        InlineKeyboardButton("🔴 Banker", callback_data="btn_banker")
    )
    markup.add(
        InlineKeyboardButton("🟢 Tie", callback_data="btn_tie")
    )
    markup.add(
        InlineKeyboardButton("↩️ Xóa tay", callback_data="btn_undo"),
        InlineKeyboardButton("🔄 Reset", callback_data="btn_reset")
    )
    return markup

def analyze_baccarat_trend(history):
    """Thuật toán v10: Siêu gọn, thông minh sau tay Hòa, nhận diện chuẩn cầu & bẻ an toàn"""
    if not history:
        return "⚠️ **Chưa có dữ liệu.** Hãy bấm chọn Player, Banker hoặc Tie để bắt đầu!"
    
    # Rút gọn hiển thị chuỗi 12 tay gần nhất cho đỡ rối mắt
    seq_str = " ".join(["🔴" if x == 'B' else ("🔵" if x == 'P' else "🟢") for x in history[-12:]])
    total = len(history)
    
    # Lọc bỏ Hòa (T) để soi cầu chính xác tuyệt đối
    main_history = [x for x in history if x != 'T']
    m_len = len(main_history)

    prediction = "Đang xử lý..."
    reason = "Đang tích lũy mẫu..."
    confidence = "Thấp"

    # 🧠 XỬ LÝ THÔNG MINH KHI GẶP TAY HÒA (TIE)
    if history[-1] == 'T':
        last_valid = main_history[-1] if main_history else 'B'
        prediction = "🔴 Banker" if last_valid == 'B' else "🔵 Player"
        reason = "Gặp Hòa ➔ Tiếp tục bám xu hướng trước đó."
        confidence = "Trung bình"
        
    elif m_len >= 3:
        last_main = main_history[-1]
        opposite = "🔵 Player" if last_main == 'B' else "🔴 Banker"
        same = "🔴 Banker" if last_main == 'B' else "🔵 Player"
        
        # Tính độ dài chuỗi hiện tại (Streak)
        streak = 1
        for i in range(m_len - 2, -1, -1):
            if main_history[i] == last_main:
                streak += 1
            else:
                break
        
        # Phân tích cấu trúc nhịp (RLE)
        runs = []
        curr_char, curr_len = main_history[0], 1
        for ch in main_history[1:]:
            if ch == curr_char:
                curr_len += 1
            else:
                runs.append((curr_char, curr_len))
                curr_char, curr_len = ch, 1
        runs.append((curr_char, curr_len))
        run_lengths = [r[1] for r in runs]
        
        is_11 = len(run_lengths) >= 3 and all(l == 1 for l in run_lengths[-4:])
        is_22 = len(run_lengths) >= 2 and all(l == 2 for l in run_lengths[-3:])
        is_33 = len(run_lengths) >= 2 and all(l == 3 for l in run_lengths[-2:])

        # Logic ra quyết định tỷ lệ chính xác cao
        if streak >= 6:
            prediction = opposite
            reason = f"🚨 Bệt dài ({streak} tay) chạm đỉnh ➔ **Bẻ bệt an toàn**."
            confidence = "Cao"
        elif streak >= 4:
            prediction = same
            reason = f"🔥 Xác nhận Cầu Bệt ({streak} tay) ➔ **Đánh theo bệt**."
            confidence = "Cao"
        elif is_11:
            prediction = opposite
            reason = "🏓 Bắt trúng Cầu 1-1 (Đảo chiều đều đặn)."
            confidence = "Cao"
        elif is_22:
            prediction = same if streak == 1 else opposite
            reason = "👥 Bắt trúng Cầu 2-2 (Nhịp đôi cặp)."
            confidence = "Cao"
        elif is_33:
            prediction = same if streak < 3 else opposite
            reason = "🧱 Bắt trúng Cầu 3-3 (Tam cấp)."
            confidence = "Cao"
        else:
            # Quán tính ngắn hạn 4 tay
            recent = main_history[-4:]
            r_b, r_p = recent.count('B'), recent.count('P')
            if r_b > r_p:
                prediction = "🔴 Banker"
                reason = "Quán tính ngắn hạn nghiêng về Banker."
                confidence = "Trung bình"
            else:
                prediction = "🔵 Player"
                reason = "Quán tính ngắn hạn nghiêng về Player."
                confidence = "Trung bình"
    else:
        b_count = history.count('B')
        p_count = history.count('P')
        prediction = "🔴 Banker" if b_count >= p_count else "🔵 Player"
        reason = "Đang khởi tạo nhịp bàn chơi."
        confidence = "Thấp"

    conf_icon = "🟢 **CAO**" if confidence == "Cao" else ("🟡 **TB**" if confidence == "Trung bình" else "🔴 **THẤP**")

    # Khung hiển thị siêu gọn gàng (Clean & Concise)
    analysis_text = (
        f"📊 **Cầu ({total}):** {seq_str}\n"
        f"🔍 **Phân tích:** {reason}\n"
        f"🎯 **DỰ ĐOÁN:** **{prediction}** | Tin cậy: {conf_icon}"
    )
    return analysis_text

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_histories[chat_id] = []
    
    welcome_text = (
        "🤖 **SMART BACCARAT ENGINE v10**\n\n"
        "Đã tối ưu giao diện siêu gọn, xử lý thông minh sau tay Hòa và nâng cấp độ chính xác bắt cầu. Bấm chọn kết quả bên dưới để bắt đầu!"
    )
    bot.send_message(chat_id, welcome_text, reply_markup=get_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    
    if chat_id not in user_histories:
        user_histories[chat_id] = []
        
    action = call.data
    
    if action == "btn_banker":
        user_histories[chat_id].append('B')
    elif action == "btn_player":
        user_histories[chat_id].append('P')
    elif action == "btn_tie":
        user_histories[chat_id].append('T')
    elif action == "btn_undo":
        if user_histories[chat_id]:
            user_histories[chat_id].pop()
    elif action == "btn_reset":
        user_histories[chat_id] = []

    updated_text = analyze_baccarat_trend(user_histories[chat_id])
    
    try:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=updated_text,
            reply_markup=get_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        pass
    
    bot.answer_callback_query(call.id)

if __name__ == "__main__":
    RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
        print(f"Webhook đã được thiết lập tới: {RENDER_URL}/{TOKEN}")

    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
