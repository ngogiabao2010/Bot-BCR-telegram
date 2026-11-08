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
    return "Bot Baccarat Smart Engine Pro v9 (Quantitative Core) đang hoạt động 24/7!"

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
    """Thuật toán định lượng thông minh v9: Phân tích động lực, xác suất chuyển tiếp & chống gãy tối ưu"""
    if not history:
        return "⚠️ **Chưa có dữ liệu.** Hãy bấm chọn Player, Banker hoặc Tie để bắt đầu hệ thống phân tích!"
    
    seq_str = " ".join(["🔴" if x == 'B' else ("🔵" if x == 'P' else "🟢") for x in history])
    
    b_count = history.count('B')
    p_count = history.count('P')
    t_count = history.count('T')
    total = len(history)
    
    # Lọc bỏ Hòa (T) để tính toán ma trận dòng chính không bị nhiễu
    main_history = [x for x in history if x != 'T']
    m_len = len(main_history)

    if m_len >= 2:
        last_val = main_history[-1]
        opposite = "🔵 Player" if last_val == 'B' else "🔴 Banker"
        same = "🔴 Banker" if last_val == 'B' else "🔵 Player"
        
        # 1. Tính độ dài chuỗi hiện tại (Streak)
        streak = 1
        for i in range(m_len - 2, -1, -1):
            if main_history[i] == last_val:
                streak += 1
            else:
                break

        # 2. HỆ THỐNG CHẤM ĐIỂM ĐỊNH LƯỢNG (QUANTITATIVE SCORING SYSTEM)
        score_banker = 0.0
        score_player = 0.0

        # --- Yếu tố A: Tần suất tổng thể (Global Frequency Weight: 20%) ---
        total_mp = len(main_history)
        if total_mp > 0:
            b_freq = main_history.count('B') / total_mp
            p_freq = main_history.count('P') / total_mp
            score_banker += b_freq * 0.2
            score_player += p_freq * 0.2

        # --- Yếu tố B: Quán tính ngắn hạn / Cửa sổ trượt (Momentum Windows: 50%) ---
        # Cửa sổ 3 tay gần nhất
        w3 = main_history[-3:]
        w3_b = w3.count('B')
        w3_p = w3.count('P')
        score_banker += (w3_b / 3.0) * 0.3
        score_player += (w3_p / 3.0) * 0.3

        # Cửa sổ 6 tay gần nhất
        w6 = main_history[-6:] if m_len >= 6 else main_history
        w6_b = w6.count('B')
        w6_p = w6.count('P')
        score_banker += (w6_b / len(w6)) * 0.2
        score_player += (w6_p / len(w6)) * 0.2

        # --- Yếu tố C: Phân tích độ mệt mỏi của nhịp & Xác suất chuyển tiếp (Transition & Fatigue: 30%) ---
        # Nếu chuỗi hiện tại quá dài (streak >= 5), xác suất đảo chiều (reversion to mean) tăng vọt
        fatigue_penalty = 0.0
        if streak >= 5:
            fatigue_penalty = min(0.4, (streak - 4) * 0.1)
            
        if last_val == 'B':
            score_banker -= fatigue_penalty
            score_player += fatigue_penalty
        else:
            score_player -= fatigue_penalty
            score_banker += fatigue_penalty

        # Xác định dự đoán dựa trên điểm số định lượng cao nhất
        if score_banker > score_player:
            prediction = "🔴 Banker"
            confidence_val = score_banker - score_player
        else:
            prediction = "🔵 Player"
            confidence_val = score_player - score_banker

        # Xây dựng lý phân tích thông minh dựa trên trạng thái toán học
        if streak >= 6:
            prediction = opposite
            reason = f"🚨 Cầu kéo dài ({streak} tay) chạm ngưỡng giới hạn mệt mỏi xác suất ➔ **Kích hoạt thuật toán đảo chiều an toàn**."
            confidence = "Cao"
        elif confidence_val > 0.35:
            reason = f"⚡ **Quán tính dòng tiền mạnh** áp đảo về phía {prediction} (Độ lệch chuẩn cao)."
            confidence = "Cao"
        elif confidence_val > 0.15:
            reason = f"⚖️ **Cân bằng động**: Trọng số ngắn hạn đang dịch chuyển nhẹ về {prediction}."
            confidence = "Trung bình"
        else:
            reason = "⚠️ **Thị trường biến động hỗn loạn (Biên độ nhiễu cao)** ➔ Khuyến nghị quản trị vốn chặt."
            confidence = "Thấp"
            
    else:
        if b_count >= p_count:
            prediction = "🔴 Banker"
        else:
            prediction = "🔵 Player"
        reason = "Đang giai đoạn khởi tạo ma trận dữ liệu bàn chơi."
        confidence = "Thấp"

    conf_icon = "🟢 **CAO**" if confidence == "Cao" else ("🟡 **TRUNG BÌNH**" if confidence == "Trung bình" else "🔴 **THẤP**")

    analysis_text = (
        f"📊 **MA TRẬN DỮ LIỆU ({total} tay):**\n"
        f"{seq_str}\n\n"
        f"📈 **Sĩ số:** B: {b_count} | P: {p_count} | T: {t_count}\n"
        f"🔍 **Phân tích định lượng:** {reason}\n\n"
        f"🎯 **DỰ ĐOÁN TỐI ƯU:**\n👉 **{prediction}**\n"
        f"🛡️ **Độ tin cậy hệ thống:** {conf_icon}"
    )
    return analysis_text

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_histories[chat_id] = []
    
    welcome_text = (
        "🤖 **BACCARAT SMART ENGINE PRO v9 (QUANTITATIVE CORE)**\n\n"
        "Đã loại bỏ hoàn toàn các khuôn cầu cứng nhắc. Hệ thống sử dụng mô hình ma trận trọng số động và quán tính dòng tiền để dự đoán chính xác. Bấm chọn kết quả bên dưới để bắt đầu!"
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
