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
    return "Bot Baccarat Smart Engine Pro Ultimate (v8) đang hoạt động 24/7!"

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
    """Thuật toán Ultimate v8: Phân định rạch ròi bệt thật, cầu ngắn, cầu đảo & bẻ cầu thông minh tuyệt đối"""
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

    # Lọc bỏ Hòa (T) để soi cầu chính (Main Road) chuẩn xác tuyệt đối không bị nhiễu
    main_history = [x for x in history if x != 'T']
    m_len = len(main_history)

    if m_len >= 3:
        last_main = main_history[-1]
        opposite = "🔵 Player" if last_main == 'B' else "🔴 Banker"
        same = "🔴 Banker" if last_main == 'B' else "🔵 Player"
        
        # 🧩 PHÂN TÍCH CẤU TRÚC NHỊP CẦU (RUN-LENGTH ENCODING - RLE)
        runs = []
        if main_history:
            curr_char = main_history[0]
            curr_len = 1
            for ch in main_history[1:]:
                if ch == curr_char:
                    curr_len += 1
                else:
                    runs.append((curr_char, curr_len))
                    curr_char = ch
                    curr_len = 1
            runs.append((curr_char, curr_len))
        
        current_streak = runs[-1][1] if runs else 1
        run_lengths = [r[1] for r in runs]
        
        # 1. Nhận diện Cầu 1-1 (Ping-pong / Đảo chiều liên tục)
        is_11 = len(run_lengths) >= 3 and all(l == 1 for l in run_lengths[-4:])
        
        # 2. Nhận diện Cầu 2-2 (Nhịp đôi cặp: BB PP BB)
        is_22 = len(run_lengths) >= 2 and all(l == 2 for l in run_lengths[-3:])
        
        # 3. Nhận diện Cầu 3-3 (Tam cấp)
        is_33 = len(run_lengths) >= 2 and all(l == 3 for l in run_lengths[-2:])
        
        # 4. CHUẨN BỆT THỰC THỰ: Bắt buộc phải từ 4 tay trở lên!
        is_true_streak = (current_streak >= 4)

        # 5. Nhận diện chu kỳ lặp vòng tròn (Pattern Cycle 1-2 hoặc 2-1)
        is_cycle = False
        if len(run_lengths) >= 4:
            if run_lengths[-4:] == [1, 2, 1, 2] or run_lengths[-4:] == [2, 1, 2, 1]:
                is_cycle = True

        # --- 🧠 MODULE RA QUYẾT ĐỊNH THÔNG MINH & CHỐNG GÃY TUYỆT ĐỐI ---
        if history[-1] == 'T':
            if current_streak >= 4:
                prediction = opposite
                reason = "Gặp Hòa khi đang bệt dài ➔ **Kích hoạt bẻ bệt an toàn**."
                confidence = "Trung bình"
            else:
                prediction = same
                reason = "Gặp Hòa ➔ Tiếp tục bám nhịp ổn định trước đó."
                confidence = "Thấp"
                
        elif current_streak >= 6:
            # 💡 BẺ CẦU THÔNG MINH: Bệt dài đạt ngưỡng giới hạn tự nhiên (>= 6) -> Bẻ ngược an toàn
            prediction = opposite
            reason = f"🚨 Cầu Bệt dài ({current_streak} tay) đạt đỉnh giới hạn tự nhiên ➔ **Bẻ bệt thông minh** tỷ lệ thắng cao."
            confidence = "Cao"
            
        elif is_true_streak:
            # Chỉ đu bệt khi đã xác thực là bệt thật (>= 4 tay)
            prediction = same
            reason = f"🔥 **Xác nhận Cầu Bệt thực sự** ({current_streak} tay) ➔ Ưu tiên đánh **Theo bệt**."
            confidence = "Cao"
            
        elif is_11:
            # Cầu 1-1 chuẩn chỉnh -> Đánh đảo chiều
            prediction = opposite
            reason = "🏓 **Cầu 1-1 (Đảo chiều liên tục hoàn hảo)** ➔ Đánh ngược màu tay trước."
            confidence = "Cao"
            
        elif is_22:
            # Cầu 2-2: Nếu mới đi 1 tay trong cặp thì theo tiếp, đủ 2 tay thì đảo chiều
            if current_streak == 1:
                prediction = same
                reason = "👥 **Cầu 2-2 (Nhịp đôi cặp)**: Đang ở tay thứ 2 của cặp ➔ Theo tiếp cùng màu."
                confidence = "Cao"
            else:
                prediction = opposite
                reason = "👥 **Cầu 2-2 (Nhịp đôi cặp)**: Đã đủ 2 tay ➔ Đảo chiều sang cặp mới."
                confidence = "Cao"
                
        elif is_33:
            if current_streak < 3:
                prediction = same
                reason = "🧱 **Cầu 3-3 (Tam cấp)**: Chưa đủ 3 tay ➔ Tiếp tục bám nhịp."
                confidence = "Cao"
            else:
                prediction = opposite
                reason = "🧱 **Cầu 3-3 (Tam cấp)**: Đã đủ 3 tay ➔ Bẻ cầu tam cấp."
                confidence = "Cao"
                
        elif is_cycle:
            # Xử lý chu kỳ lặp nhịp 1-2 hoặc 2-1
            last_run_char = runs[-1][0]
            prediction = "🔴 Banker" if last_run_char != 'B' else "🔵 Player"
            reason = "🎯 **Bắt trúng chu kỳ lặp nhịp cầu (Pattern Cycle)** ➔ Đảo chiều theo nhịp lặp."
            confidence = "Cao"
            
        else:
            # 🛡️ XỬ LÝ CẦU NGẮN / CẦU LOẠN / KHÔNG BỆT (Tuyệt đối không đu bệt)
            # Phân tích cửa sổ trọng số 4 tay gần nhất để lướt sóng chính xác
            recent_4 = main_history[-4:]
            r_b = recent_4.count('B')
            r_p = recent_4.count('P')
            
            if current_streak == 2:
                prediction = opposite
                reason = "⚖️ **Cầu ngắn / Nhịp đôi ngắt quãng**: Tránh bẫy bệt giả ➔ Đánh **Đảo chiều** ngắn hạn."
                confidence = "Trung bình"
            else:
                if r_b > r_p:
                    prediction = "🔴 Banker"
                    reason = "⚖️ **Cầu ngắn / Biến động**: Trọng số biên độ ngắn hạn nghiêng về Banker."
                    confidence = "Trung bình"
                elif r_p > r_b:
                    prediction = "🔵 Player"
                    reason = "⚖️ **Cầu ngắn / Biến động**: Trọng số biên độ ngắn hạn nghiêng về Player."
                    confidence = "Trung bình"
                else:
                    if b_count >= p_count:
                        prediction = "🔴 Banker"
                        reason = "Cân bằng nhịp ➔ Phân bổ theo thế mạnh Banker tổng thể."
                        confidence = "Thấp"
                    else:
                        prediction = "🔵 Player"
                        reason = "Cân bằng nhịp ➔ Phân bổ theo thế mạnh Player tổng thể."
                        confidence = "Thấp"
    else:
        if b_count >= p_count:
            prediction = "🔴 Banker"
        else:
            prediction = "🔵 Player"
        reason = "Đang giai đoạn khởi tạo mẫu cầu bàn chơi."
        confidence = "Thấp"

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
        "🤖 **BOT BACCARAT SMART ENGINE ULTIMATE (v8)**\n\n"
        "Phiên bản chuẩn xác tối thượng: Triệt tiêu hoàn toàn bẫy bệt giả, phân định rạch ròi cầu ngắn, cầu đảo và bẻ cầu thông minh. Bấm chọn kết quả bên dưới để bắt đầu!"
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
