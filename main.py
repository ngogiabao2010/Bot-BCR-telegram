import os
import threading
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
    return "Bot Baccarat Webhook đang hoạt động 24/7!"

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
    """Thuật toán phân tích tối ưu chuyên sâu: Đọc khuôn cầu chuẩn xác, chấm điểm độ tin cậy"""
    if not history:
        return "⚠️ **Chưa có dữ liệu.** Hãy bấm chọn Player, Banker hoặc Tie để bắt đầu dựng cầu!"
    
    seq_str = " ".join(["🔴" if x == 'B' else ("🔵" if x == 'P' else "🟢") for x in history])
    
    b_count = history.count('B')
    p_count = history.count('P')
    t_count = history.count('T')
    total = len(history)
    
    prediction = "Chờ thêm dữ liệu..."
    reason = "Đang tích lũy mẫu cầu..."
    confidence = "Thấp"

    # Lọc bỏ Hòa (T) để soi cầu chính (Main Road) chuẩn xác không bị nhiễu nhịp
    main_history = [x for x in history if x != 'T']
    m_len = len(main_history)

    if m_len >= 3:
        last_main = main_history[-1]
        opposite = "🔵 Player" if last_main == 'B' else "🔴 Banker"
        same = "🔴 Banker" if last_main == 'B' else "🔵 Player"
        
        # 1. Tính độ dài chuỗi bệt hiện tại từ đuôi mảng chính
        streak = 1
        for i in range(m_len - 2, -1, -1):
            if main_history[i] == last_main:
                streak += 1
            else:
                break
        
        # 2. Kiểm tra Cầu 1-1 chuẩn chỉnh (Đảo chiều liên tục trong ít nhất 3-4 tay gần nhất)
        is_11 = True
        for i in range(m_len - 1, max(0, m_len - 4), -1):
            if i > 0 and main_history[i] == main_history[i-1]:
                is_11 = False
                break

        # 3. Kiểm tra Cầu 2-2 (Nhịp đôi cặp: BB PP BB...)
        is_22 = False
        if m_len >= 4:
            if main_history[-1] == main_history[-2] and main_history[-3] == main_history[-4] and main_history[-1] != main_history[-3]:
                is_22 = True

        # 4. Kiểm tra Cầu 1-2 hoặc 2-1 (Nhịp bước chân)
        is_12 = False
        if m_len >= 3:
            if main_history[-1] != main_history[-2] and main_history[-2] == main_history[-3]:
                is_12 = True

        # 5. Bộ lọc phát hiện cầu nhiễu loạn (Cầu gãy khúc liên tục)
        recent_4 = main_history[-4:] if m_len >= 4 else main_history
        is_choppy = False
        if len(recent_4) == 4:
            changes = sum(1 for i in range(len(recent_4)-1) if recent_4[i] != recent_4[i+1])
            if changes >= 3 and not is_11:
                is_choppy = True

        # --- MODULE RA QUYẾT ĐỊNH & ĐÁNH GIÁ ĐỘ CHẮC CHẮN TỐI ƯU ---
        if history[-1] == 'T':
            if streak >= 4:
                prediction = opposite
                reason = "Gặp Hòa khi đang bệt dài ➔ **Bẻ bệt an toàn**."
                confidence = "Trung bình"
            else:
                prediction = same
                reason = "Gặp Hòa ➔ Tiếp tục bám nhịp ổn định trước đó."
                confidence = "Thấp"
                
        elif is_choppy:
            prediction = opposite if last_main == 'P' else same
            reason = "⚠️ **Cầu nhiễu loạn nhịp** ➔ Cảnh báo rủi ro gãy thông cao."
            confidence = "Thấp"
            
        elif streak >= 5:
            # Bệt dài đạt ngưỡng giới hạn an toàn -> Ra quyết định bẻ bệt tỷ lệ thắng cao
            prediction = opposite
            reason = f"Cầu Bệt dài ({streak} tay) chạm đỉnh ➔ Kích hoạt **Bẻ bệt tối ưu**."
            confidence = "Cao"
            
        elif streak >= 2 and not is_22:
            # Bệt ngắn ổn định -> Bám theo bệt
            prediction = same
            reason = f"Xác nhận Cầu Bệt ngắn ({streak} tay) ➔ Ưu tiên đánh **Theo bệt**."
            confidence = "Cao"
            
        elif is_11:
            prediction = opposite
            reason = "Bắt trúng khuôn chuẩn **Cầu 1-1** (Đảo nhịp đẹp)."
            confidence = "Cao"
            
        elif is_22:
            prediction = opposite if main_history[-1] == main_history[-2] else same
            reason = "Bắt trúng khuôn chuẩn **Cầu 2-2** (Nhịp đôi cặp)."
            confidence = "Cao"
            
        elif is_12:
            prediction = same
            reason = "Bắt trúng khuôn chuẩn **Cầu 1-2** (Nhịp bước chân)."
            confidence = "Trung bình"
            
        else:
            # Phân tích trọng số xu hướng trong 6 tay gần nhất để tối ưu hóa phán đoán
            recent_6 = main_history[-6:] if m_len >= 6 else main_history
            r_b = recent_6.count('B')
            r_p = recent_6.count('P')
            if r_b > r_p + 1:
                prediction = "🔴 Banker"
                reason = "Xu hướng ngắn hạn áp đảo mạnh về Banker."
                confidence = "Trung bình"
            elif r_p > r_b + 1:
                prediction = "🔵 Player"
                reason = "Xu hướng ngắn hạn áp đảo mạnh về Player."
                confidence = "Trung bình"
            else:
                if b_count >= p_count:
                    prediction = "🔴 Banker"
                    reason = "Cân bằng nhịp ➔ Ưu tiên phân bổ theo thế mạnh Banker."
                    confidence = "Thấp"
                else:
                    prediction = "🔵 Player"
                    reason = "Cân bằng nhịp ➔ Ưu tiên phân bổ theo thế mạnh Player."
                    confidence = "Thấp"
    else:
        if b_count >= p_count:
            prediction = "🔴 Banker"
        else:
            prediction = "🔵 Player"
        reason = "Đang giai đoạn khởi tạo mẫu cầu bàn chơi."
        confidence = "Thấp"

    # Gắn icon trực quan cho 3 mức độ chắc chắn
    conf_icon = "🟢 **CAO**" if confidence == "Cao" else ("🟡 **TRUNG BÌNH**" if confidence == "Trung bình" else "🔴 **THẤP**")

    analysis_text = (
        f"📊 **CẦU HIỆN TẠI ({total} tay):**\n"
        f"{seq_str}\n\n"
        f"📈 **Sĩ số:** B: {b_count} | P: {p_count} | T: {t_count}\n"
        f"🔍 **Phân tích:** {reason}\n\n"
        f"🎯 **DỰ ĐOÁN TIẾP THEO:**\n👉 **{prediction}**\n"
        f"🛡️ **Độ chắc chắn:** {conf_icon}"
    )
    return analysis_text

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_histories[chat_id] = []
    
    welcome_text = (
        "🤖 **BOT PHÂN TÍCH BACCARAT (CHUẨN XÁC CAO)**\n\n"
        "Bấm chọn kết quả (Player, Banker, Tie) bên dưới để bot dựng cầu, lọc nhiễu và đưa ra dự đoán tối ưu nhất."
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
