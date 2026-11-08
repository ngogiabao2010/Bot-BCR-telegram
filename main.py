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
    return "Bot Baccarat Smart Engine Pro v3 đang hoạt động 24/7!"

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
    """Thuật toán phân tích siêu cấp: Đọc toàn bộ khuôn cầu Baccarat, chấm điểm trọng số chống gãy liên tục"""
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

    # Lọc bỏ Hòa (T) để soi cầu chính (Main Road) chuẩn xác tuyệt đối không bị nhiễu nhịp
    main_history = [x for x in history if x != 'T']
    m_len = len(main_history)

    if m_len >= 3:
        last_main = main_history[-1]
        opposite = "🔵 Player" if last_main == 'B' else "🔴 Banker"
        same = "🔴 Banker" if last_main == 'B' else "🔵 Player"
        
        # 1. Tính độ dài chuỗi bệt (Streak) hiện tại từ đuôi mảng chính
        streak = 1
        for i in range(m_len - 2, -1, -1):
            if main_history[i] == last_main:
                streak += 1
            else:
                break
        
        # 2. Kiểm tra các loại khuôn cầu chuẩn xác
        # 2.1. Cầu 1-1 (Ping-pong / Đảo chiều liên tục)
        is_11 = True
        for i in range(m_len - 1, max(0, m_len - 4), -1):
            if i > 0 and main_history[i] == main_history[i-1]:
                is_11 = False
                break

        # 2.2. Cầu 2-2 (Nhịp đôi cặp: BB PP BB...)
        is_22 = False
        if m_len >= 4:
            if main_history[-1] == main_history[-2] and main_history[-3] == main_history[-4] and main_history[-1] != main_history[-3]:
                is_22 = True

        # 2.3. Cầu 3-3 (Nhịp tam cấp: BBB PPP...)
        is_33 = False
        if m_len >= 6:
            if (main_history[-1] == main_history[-2] == main_history[-3]) and \
               (main_history[-4] == main_history[-5] == main_history[-6]) and \
               (main_history[-1] != main_history[-4]):
                is_33 = True

        # 2.4. Cầu 1-2 / 2-1 (Nhịp bước chân)
        is_12 = m_len >= 3 and main_history[-1] != main_history[-2] and main_history[-2] == main_history[-3]
        is_21 = m_len >= 3 and main_history[-1] == main_history[-2] and main_history[-2] != main_history[-3]

        # 2.5. Chu kỳ lặp vòng tròn (Pattern Cycle 1-2-1-2 hoặc 2-1-2-1)
        is_cycle_repeating = False
        if m_len >= 6:
            if main_history[-6:-3] == main_history[-3:]:
                is_cycle_repeating = True

        # 2.6. Bộ lọc phát hiện cầu nhiễu loạn hỗn tạp (gãy khúc liên tục không theo quy luật)
        recent_4 = main_history[-4:] if m_len >= 4 else main_history
        is_choppy = False
        if len(recent_4) == 4:
            changes = sum(1 for i in range(len(recent_4)-1) if recent_4[i] != recent_4[i+1])
            if changes >= 3 and not is_11 and not is_cycle_repeating:
                is_choppy = True

        # --- HỆ THỐNG CHẤM ĐIỂM TRỌNG SỐ VÀ RA QUYẾT ĐỊNH THÔNG MINH ---
        if history[-1] == 'T':
            if streak >= 4:
                prediction = opposite
                reason = "Gặp Hòa khi đang bệt dài ➔ **Bẻ bệt an toàn**."
                confidence = "Trung bình"
            else:
                prediction = same
                reason = "Gặp Hòa ➔ Tiếp tục bám nhịp ổn định trước đó."
                confidence = "Thấp"
                
        elif is_cycle_repeating:
            # Bắt đúng chu kỳ lặp vòng tròn -> Dự đoán theo đúng quy luật lặp
            next_val = main_history[-3]
            prediction = "🔴 Banker" if next_val == 'B' else "🔵 Player"
            reason = "🎯 **Bắt trúng chu kỳ lặp khuôn cầu chuẩn xác** (Pattern Cycle)."
            confidence = "Cao"
            
        elif is_33:
            # Đang chạy cầu 3-3 -> Bám theo nhịp tam cấp
            prediction = same if streak < 3 else opposite
            reason = "🧱 **Phát hiện khuôn Cầu 3-3 (Tam cấp ổn định)**."
            confidence = "Cao"
            
        elif streak >= 6:
            # Bệt dài đạt đỉnh -> Kích hoạt chiến thuật bẻ bệt tối ưu
            prediction = opposite
            reason = f"Cầu Bệt dài ({streak} tay) chạm ngưỡng đỉnh ➔ Kích hoạt **Bẻ bệt tỷ lệ cao**."
            confidence = "Cao"
            
        elif streak >= 2 and not is_22:
            # Bệt ngắn ổn định -> Đánh theo bệt
            prediction = same
            reason = f"Xác nhận Cầu Bệt ngắn ({streak} tay) ➔ Ưu tiên đánh **Theo bệt**."
            confidence = "Cao"
            
        elif is_11:
            prediction = opposite
            reason = "🏓 Bắt trúng khuôn chuẩn **Cầu 1-1 (Ping-pong đều đặn)**."
            confidence = "Cao"
            
        elif is_22:
            prediction = opposite if main_history[-1] == main_history[-2] else same
            reason = "👥 Bắt trúng khuôn chuẩn **Cầu 2-2 (Nhịp đôi cặp)**."
            confidence = "Cao"
            
        elif is_12 or is_21:
            prediction = opposite if streak == 2 else same
            reason = "👣 Nhận diện khuôn **Cầu bước chân (1-2 / 2-1)**."
            confidence = "Trung bình"
            
        elif is_choppy:
            prediction = opposite if last_main == 'P' else same
            reason = "⚠️ **Cầu nhiễu loạn nhịp nặng (Rủi ro gãy cao)** ➔ Khuyến nghị đứng ngoài."
            confidence = "Thấp"
            
        else:
            # Phân tích trọng số xu hướng trong 6 tay gần nhất
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
                    reason = "Cân bằng nhịp ➔ Phân bổ theo thế mạnh Banker."
                    confidence = "Thấp"
                else:
                    prediction = "🔵 Player"
                    reason = "Cân bằng nhịp ➔ Phân bổ theo thế mạnh Player."
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
        "🤖 **BOT BACCARAT SMART ENGINE PRO v3**\n\n"
        "Đã tích hợp đầy đủ các loại cầu (1-1, 2-2, 3-3, Bệt, Vòng lặp chu kỳ) và bộ lọc chống gãy thông minh. Bấm chọn kết quả bên dưới để bắt đầu phân tích!"
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
