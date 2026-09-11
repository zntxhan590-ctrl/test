import androidhelper
from flask import Flask, render_template_string, request

app = Flask(__name__)

# Инициализируем androidhelper для управления возможностями Redmi 7
droid = androidhelper.Android()

# Переменная в памяти сервера для хранения текста на экране LG
current_text_for_lg = "Ожидание текста..."

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>пульт JS-Auto</title>
    
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body { 
            font-family: sans-serif; 
            background: #000; 
            color: #00ff00; 
            text-align: center; 
            padding: 10px 5px; 
        }

        .container {
            max-width: 210px; 
            margin: 0 auto;   
        }

        h1 { 
            font-size: 13px;       
            color: #aaaaaa;        
            margin: 8px 0 3px 0; 
            text-align: left; 
        }

        /* === БЛОК ПРИНЯТОГО ТЕКСТА НА LG === */
        #displayBox { 
            font-size: 20px; /* Увеличили шрифт, чтобы было видно издалека */
            color: #0000f0; 
            background: #11f111; 
            padding: 10px; 
            border: 2px solid #00ffff; 
            margin-bottom: 5px; 
            border-radius: 5px;
            word-wrap: break-word;
            font-weight: bold;
        }

        #connectionCounter { 
            font-size: 40px;       
            color: #ffc107;        
            font-weight: bold; 
            font-family: monospace; 
            margin-bottom: 5px; 
        }

        input[type="text"] { 
            font-size: 14px;       
            padding: 8px;         
            border: 2px solid #00ff00; 
            background: #111111;   
            color: #ffffff;        
            width: 100%; 
            border-radius: 5px; 
            margin-bottom: 4px;
        }
        
        .lg-input {
            border-color: #00ffff !important;
        }

        button { 
            font-size: 14px;       
            padding: 10px 5px; 
            color: #000000;        
            font-weight: bold; 
            width: 100%; 
            border: none;                 
            border-radius: 55px; 
            margin-top: 5px; 
            margin-bottom: 8px;
            cursor: pointer; 
        }
        
        .btn-voice {
            background: #07ff09;   
            border-bottom: 4px solid #00aa00;
        }
        .btn-voice:active { 
            background: #00cc00;   
            border-bottom: none;          
            padding-top: 14px;            
        }

        .btn-text {
            background: #00ffff;   
            border-bottom: 4px solid #00aaaa;
        }
        .btn-text:active { 
            background: #00cccc;   
            border-bottom: none;          
            padding-top: 14px;            
        }

        #status { 
            font-size: 16px;       
            color: #ffffff;        
            margin-top: 5px; 
            height: 20px; 
        }
        .ping-indicator { 
            font-size: 14px;       
            margin-top: 5px; 
        }
    </style>
</head>
<body>

    <div class="container">
        <h1>Принято на LG:</h1>
        <div id="displayBox">{{ text_on_screen }}</div>

        <h1>Счетчик связи:</h1>
        <div id="connectionCounter">0</div>

        <h1>Отправить ТЕКСТ на LG:</h1>
        <input type="text" id="lgTextInput" class="lg-input" placeholder="Напиши текст для LG...">
        <button class="btn-text" onclick="sendTextToLG()">ОБНОВИТЬ ЭКРАН</button>

        <h1>Отправить ГОЛОС на Redmi:</h1>
        <input type="text" id="msgInput" value="корч что то сказал">
        <button class="btn-voice" onclick="sendMessage()">ОТПРАВИТЬ ГОЛОС</button>
        
        <div id="status"></div>
        <div class="ping-indicator" id="pingStatus">Ожидание сигнала...</div>
    </div>

    <script>
        var pingsCount = 10;

        function sendMessage() {
            var text = document.getElementById('msgInput').value;
            var statusDiv = document.getElementById('status');
            statusDiv.innerHTML = "Озвучивание...";
            statusDiv.style.color = "#00ff00";
            
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/send_msg", true);
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    statusDiv.innerHTML = "Озвучено!";
                    setTimeout(function() { statusDiv.innerHTML = ""; }, 3000);
                }
            };
            xhr.send("message=" + encodeURIComponent(text));
        }

        function sendTextToLG() {
            var text = document.getElementById('lgTextInput').value;
            var statusDiv = document.getElementById('status');
            statusDiv.innerHTML = "Отправка текста...";
            statusDiv.style.color = "#00ffff";
            
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "/set_lg_text", true);
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
            
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    statusDiv.innerHTML = "Текст обновлен!";
                    document.getElementById('lgTextInput').value = "";
                    setTimeout(function() { statusDiv.innerHTML = ""; }, 2000);
                    // Сразу запрашиваем обновление, чтобы не ждать таймаута
                    sendHeartbeat();
                }
            };
            xhr.send("new_text=" + encodeURIComponent(text));
        }

        // Упрощенный метод автообновления текста для старых телефонов
        function sendHeartbeat() {
            var xhr = new XMLHttpRequest();
            // Запрашиваем обычный текст вместо сложного JSON
            xhr.open("GET", "/get_lg_pure_text?t=" + new Date().getTime(), true);
            
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    var indicator = document.getElementById('pingStatus');
                    var counterDiv = document.getElementById('connectionCounter');
                    var displayBox = document.getElementById('displayBox');
                    
                    if (xhr.status === 200) {
                        pingsCount++;
                        counterDiv.innerHTML = pingsCount;
                        indicator.innerHTML = "Связь: ОК";
                        indicator.style.color = "#00ff00"; 
                        
                        // Просто вставляем пришедший ответ сервера в коробку напрямую
                        displayBox.innerHTML = xhr.responseText;
                    } else {
                        indicator.innerHTML = "Связь потеряна!";
                        indicator.style.color = "#ff0000"; 
                    }
                }
            };
            xhr.send();
        }

        // Быстрое обновление каждые 3 секунды под старый браузер LG
        setInterval(sendHeartbeat, 10000);
        sendHeartbeat();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    global current_text_for_lg
    return render_template_string(HTML_TEMPLATE, text_on_screen=current_text_for_lg)

# НОВЫЙ ЭНДПОИНТ: Отдает просто чистую строку текста, понятную для LG T375
@app.route("/get_lg_pure_text", methods=["GET"])
def get_lg_pure_text():
    global current_text_for_lg
    return current_text_for_lg, 200

@app.route("/set_lg_text", methods=["POST"])
def set_lg_text():
    global current_text_for_lg
    text = request.form.get("new_text", "").strip()
    if text:
        current_text_for_lg = text
        print(f"[TEXT UPDATED] {text}")
    return "OK", 200

@app.route("/send_msg", methods=["POST"])
def send_msg():
    user_message = request.form.get("message", "").strip()
    if user_message:
        try:
            droid.vibrate(200)
            droid.ttsSpeak(user_message)
        except Exception as e:
            print(f"[ERROR] {e}")
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
