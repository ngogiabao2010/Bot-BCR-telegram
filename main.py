import os
import threading
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Token Bot chính xác của bạn
TOKEN = '9123735744:AAFSdlWhFxrXYkv7H_QSr0Uo9emx4Y-lQg4'
bot = telebot.TeleBot(TOKEN)

# Bộ nhớ tạm lưu lịch sử cầu của từng user: {chat_id: ['B', 'P', 'T', ...]}
user_histories = {}

# --- MẠCH GIỮ KẾT NỐI CHO RENDER (CHỐNG NGỦ QUÊN & TIMEOUT PORT) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Baccarat Telegram đang hoạt động 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
# -----------------------------------------------------------------

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
    """Thuật toán phân tích tối ưu khuôn cầu, chống gãy thông & hạn chế thua liên tục"""
    if not history:
        return "⚠️ **Chưa có dữ liệu.** Hãy bấm chọn Player, Banker hoặc Tie để bắt đầu dựng cầu!"
    
    # Hiển thị chuỗi cầu gọn gàng bằng icon
    seq_str = " ".join(["🔴" if x == 'B' else ("🔵" if x == 'P' else "🟢") for x in history])
    
    b_count = history.count('B')
    p_count = history.count('P')
    t_count = history.count('T')
    total = len(history)
    
    prediction = "Chờ thêm dữ liệu..."
    reason = "Đang tích lũy mẫu cầu..."
    confidence = "Thấp"  # Mặc định độ chắc chắn

    # Lọc bỏ các nhịp Hòa (T) ra khỏi mảng phụ để soi khuôn cầu chính (Main Road)
    main_history = [x for x in history if x != 'T']
    m_len = len(main_history)

    if m_len >= 3:
        last_main = main_history[-1]
        opposite = "🔵 Player" if last_main == 'B' else "🔴 Banker"
        same = "🔴 Banker" if last_main == 'B' else "🔵 Player"
        
        # 1. Tính độ dài bệt hiện tại từ cuối mảng chính
        streak = 1
        for i in range(m_len - 2, -1, -1):
            if main_history[i] == last_main:
                streak += 1
            else:
                break
        
        # 2. Kiểm tra Cầu 1-1 (Đảo chiều liên tục chuẩn chỉnh)
        is_11 = True
        for i in range(m_len - 1, max(0, m_len - 4), -1):
            if i > 0 and main_history[i] == main_history[i-1]:
                is_11 = False
                break

        # 3. Kiểm tra Cầu 2-2 (Nhịp đôi cặp)
        is_22 = False
        if m_len >= 4:
            if main_history[-1] == main_history[-2] and main_history[-3] == main_history[-4] and main_history[-1] != main_history[-3]:
                is_22 = True

        # 4. Kiểm tra Cầu 1-2 (Nhịp bước chân)
        is_12 = False
        if m_len >= 3:
            if main_history[-1] != main_history[-2] and main_history[-2] == main_history[-3]:
                is_12 = True

        # 5. Bộ lọc chống gãy thông: Kiểm tra độ nhiễu của nhịp gần nhất
        recent_4 = main_history[-4:] if m_len >= 4 else main_history
        is_choppy = False
        if len(recent_4) == 4:
            changes = sum(1 for i in range(len(recent_4)-1) if recent_4[i] != recent_4[i+1])
            if changes >= 3 and not is_11:
                is_choppy = True

        # --- MODULE RA QUYẾT ĐỊNH THÔNG MINH, AN TOÀN, CHỐNG THUA LIÊN TỤC ---
        if history[-1] == 'T':
            if streak >= 4:
                prediction = opposite
                reason = "Gặp Hòa khi đang bệt dài ➔ **Bẻ bệt an toàn** để chốt lãi/tránh gãy."
                confidence = "Trung bình"
            else:
                prediction = same
                reason = "Gặp Hòa ➔ Tiếp tục bám nhịp cầu ổn định trước đó."
                confidence = "Thấp"
        elif is_choppy:
            prediction = opposite if last_main == 'P' else same
            reason = "⚠️ **Cầu nhiễu loạn nhịp (Nguy cơ gãy thông cao)** ➔ Khuyến nghị đứng ngoài hoặc giảm nửa vốn."
            confidence = "Thấp"
        elif streak >= 6:
            prediction = opposite
            reason = f"Cầu Bệt dài ({streak} tay) đạt đỉnh ➔ Kích hoạt chiến thuật **Bẻ bệt an toàn**."
            confidence = "Cao"
        elif streak >= 2 and not is_22:
            prediction = same
            reason = f"Phát hiện Cầu Bệt ngắn ({streak} tay) ➔ Ưu tiên đánh **Theo bệt**."
            confidence = "Cao"
        elif is_11:
            prediction = opposite
            reason = "Phát hiện khuôn chuẩn **Cầu 1-1** (Đảo chiều nhịp nhàng)."
            confidence = "Cao"
        elif is_22:
            prediction = opposite if main_history[-1] == main_history[-2] else same
            reason = "Phát hiện khuôn chuẩn **Cầu 2-2** (Nhịp đôi cặp)."
            confidence = "Cao"
        elif is_12:
            prediction = same
            reason = "Phát hiện khuôn chuẩn **Cầu 1-2** (Nhịp bước chân)."
            confidence = "Trung bình"
        else:
            recent_6 = main_history[-6:] if m_len >= 6 else main_history
            r_b = recent_6.count('B')
            r_p = recent_6.count('P')
            if r_b > r_p:
                prediction = "🔴 Banker"
                reason = "Nhịp ngắn ổn định nghiêng về Banker."
                confidence = "Trung bình"
            elif r_p > r_b:
                prediction = "🔵 Player"
                reason = "Nhịp ngắn ổn định nghiêng về Player."
                confidence = "Trung bình"
            else:
                if b_count >= p_count:
                    prediction = "🔴 Banker"
                    reason = "Cầu cân bằng, phân bổ theo tổng lịch sử Banker."
                    confidence = "Thấp"
                else:
                    prediction = "🔵 Player"
                    reason = "Cầu cân bằng, phân bổ theo tổng lịch sử Player."
                    confidence = "Thấp"
    else:
        if b_count >= p_count:
            prediction = "🔴 Banker"
        else:
            prediction = "🔵 Player"
        reason = "Đang khởi tạo mẫu cầu bàn chơi."
        confidence = "Thấp"

    # Gắn icon trực quan cho mức độ chắc chắn
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
def send_welcome(chat_id_or_message):
    chat_id = chat_id_or_message.chat.id if hasattr(chat_id_or_message, 'chat') else chat_id_or_message
    
    if chat_id not in user_histories:
        user_histories[chat_id] = []
        
    welcome_text = (
        "🤖 **BOT PHÂN TÍCH BACCARAT (TỐI ƯU AN TOÀN)**\n\n"
        "Bấm chọn kết quả (Player, Banker, Tie) bên dưới để bot dựng cầu, lọc nhiễu và dự đoán."
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
    # Khởi động luồng Flask để mở port cho Render nhận diện
    keep_alive()
    
    print("Tool BCR CRE NGB ĐÃ CHẠY...")
    bot.infinity_polling()
