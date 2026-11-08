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
    return "Bot Baccarat Smart Engine Pro v5 đang hoạt động 24/7!"

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
    """Thuật toán RLE phân tích cấu trúc nhịp cầu chuyên sâu (2/2, 2/3, 1/2/3, Bẻ cầu thông minh)"""
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

    # Lọc bỏ Hòa (T) để soi cầu chính (Main Road) chuẩn xác tuyệt đối
    main_history = [x for x in history if x != 'T']
    m_len = len(main_history)

    if m_len >= 3:
        last_main = main_history[-1]
        opposite = "🔵 Player" if last_main == 'B' else "🔴 Banker"
        same = "🔴 Banker" if last_main == 'B' else "🔵 Player"
        
        # 🧩 PHÂN TÍCH CẤU TRÚC NHỊP CẦU (RUN-LENGTH ENCODING)
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
        
        # 1. Nhận diện Cầu 2-2 (Các nhịp gần nhất đều có độ dài bằng 2)
        is_22 = len(run_lengths) >= 2 and all(l == 2 for l in run_lengths[-3:])
        
        # 2. Nhận diện Cầu 1-1 (Ping-pong)
        is_11 = len(run_lengths) >= 3 and all(l == 1 for l in run_lengths[-4:])
        
        # 3. Nhận diện Cầu 3-3 (Tam cấp)
        is_33 = len(run_lengths) >= 2 and all(l == 3 for l in run_lengths[-2:])
        
        # 4. Nhận diện Cầu bậc thang / Cầu dạng 1/2/3 hoặc biến thiên nhịp
        is_staircase = False
        if len(run_lengths) >= 3:
            last_three = run_lengths[-3:]
            if last_three in [[1, 2, 3], [3, 2, 1], [1, 2, 2], [2, 2, 3], [1, 3, 2]]:
                is_staircase = True

        # 5. Nhận diện cầu loạn phức tạp dạng 2/3 hoặc biên độ hỗn hợp
        is_complex_mix = False
        if len(run_lengths) >= 4:
            recent_lens = run_lengths[-4:]
            if all(1 <= l <= 3 for l in recent_lens) and not is_11 and not is_22:
                is_complex_mix = True

        # --- 🧠 MODULE BẺ CẦU THÔNG MINH & RA QUYẾT ĐỊNH CHUẨN XÁC ---
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
            # 💡 BẺ CẦU THÔNG MINH: Bệt dài >= 6 tay chạm ngưỡng giới hạn xác suất tự nhiên -> Bẻ ngược an toàn
            prediction = opposite
            reason = f"🚨 Cầu Bệt dài ({current_streak} tay) đạt đỉnh giới hạn ➔ **Bẻ bệt thông minh** tỷ lệ thắng cao."
            confidence = "Cao"
            
        elif is_22:
            # Xử lý chuẩn xác nhịp 2-2: Nếu mới đi 1 tay trong cặp thì theo tiếp tay thứ 2, đủ 2 tay thì đảo chiều
            if current_streak == 1:
                prediction = same
                reason = "👥 **Cầu 2-2 (Nhịp đúp cặp)**: Đang ở tay thứ 2 của cặp ➔ Theo tiếp."
                confidence = "Cao"
            else:
                prediction = opposite
                reason = "👥 **Cầu 2-2 (Nhịp đôi cặp)**: Đã đủ 2 tay ➔ Đảo chiều sang cặp mới."
                confidence = "Cao"
                
        elif is_11:
            prediction = opposite
            reason = "🏓 **Cầu 1-1 (Đảo chiều liên tục)** chuẩn xác."
            confidence = "Cao"
            
        elif is_33:
            if current_streak < 3:
                prediction = same
                reason = "🧱 **Cầu 3-3 (Tam cấp ổn định)**: Tiếp tục bám nhịp."
                confidence = "Cao"
            else:
                prediction = opposite
                reason = "🧱 **Cầu 3-3 (Tam cấp)**: Đã đủ 3 tay ➔ Bẻ cầu tam cấp."
                confidence = "Cao"
                
        elif is_staircase:
            prediction = opposite if current_streak >= 2 else same
            reason = "📈 **Cầu bậc thang (Dạng 1/2/3 hoặc biến thiên)**: Đọc nhịp xu thế tiếp theo."
            confidence = "Trung bình"
            
        elif is_complex_mix:
            # Xử lý cầu loạn 2/3 bằng bộ lọc trọng số hướng đi gần nhất
            prediction = opposite if current_streak >= 2 else same
            reason = "⚖️ **Cầu phức tạp / Loạn nhịp (2/3, 1/2/3)**: Kích hoạt bộ lọc cân bằng xác suất thông minh."
            confidence = "Trung bình"
            
        elif current_streak >= 2:
            prediction = same
            reason = f"📈 Xác nhận bệt ngắn ({current_streak} tay) ➔ Đánh **Theo bệt**."
            confidence = "Cao"
            
        else:
            # Phân tích trọng số xu hướng trong 4 tay gần nhất
            recent_4 = main_history[-4:]
            r_b = recent_4.count('B')
            r_p = recent_4.count('P')
            if r_b > r_p:
                prediction = "🔴 Banker"
                reason = "Xu hướng ngắn hạn áp đảo nhẹ về Banker."
                confidence = "Trung bình"
            elif r_p > r_b:
                prediction = "🔵 Player"
                reason = "Xu hướng ngắn hạn áp đảo nhẹ về Player."
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
        "🤖 **BOT BACCARAT SMART ENGINE PRO v5**\n\n"
        "Đã nâng cấp thuật toán mã hóa nhịp RLE (Nhận diện Cầu 2/2, 3/3, Cầu 1/2/3, 2/3 và Bẻ cầu thông minh chống gãy). Bấm chọn kết quả bên dưới để bắt đầu!"
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
