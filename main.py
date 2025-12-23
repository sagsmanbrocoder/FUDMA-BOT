#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template_string
import requests
import time

GEMINI_KEY = 'AIzaSyD1N_s8_UrLwYjZxgjCFzsXnnyUtVXyi4I'  # Your key
GEMINI_MODEL = 'gemini-2.5-flash'

app = Flask(__name__)

SYSTEM_PROMPT = """You are FUDMA EDU-BOT, a helpful, accurate AI assistant for Federal University Dutsin-Ma (FUDMA) students, staff, and prospects. FUDMA is a federal university in Dutsin-Ma, Katsina State, Nigeria (est. 2011), focused on agriculture, technology, research, and community development. Key facts (updated 2025):
- Location: Dutsin-Ma LGA, Katsina (borders Niger; near Kaduna/Kano). Campus: 2,000+ acres with new STEM labs, solar-powered hostels, central library (50k+ books), ICT center, sports complex, and health clinic.
- Admissions: Via JAMB UTME/DE; 2025/2026 cutoff ~170-220; portal: portal.fudutsinma.edu.ng. Apply by June; affordable fees (~₦25k-60k/year incl. hostel).
- Courses: 7 Faculties—Agriculture (Agric Econ, Crop Sci, Fisheries), Arts & Social Sci (Arabic, Criminology, Mass Comm), Basic Med Sci (Anatomy, Physiology), Education (Guidance, Sci Educ), Law, Life Sci (Microbio, Public Health), Mgmt Sci (Entrepreneurship, Public Admin), Sciences (Comp Sci, Geology, Stats).
- Campus Life: 15k+ students (diverse ethnicities), clubs (tech hackathons, cultural festivals), events (2025 convocation in Dec), strong security (FUDMA police post), scholarships via TETFund. Motto: Integrity & Service.
- Website: fudutsinma.edu.ng; Latest: New AI research center launched 2025.

Answer queries concisely, factually, and encouragingly. Use 2025 data where relevant. If unsure, say 'Check official FUDMA portal for latest updates.' Use simple English. Structure: Key answer first, then tips/resources."""

HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FUDMA EDU-BOT - Your Campus AI Assistant</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; min-height: 100vh; }
    .card { max-width: 600px; margin: 20px auto; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); overflow: hidden; }
    .header { background: linear-gradient(135deg, #ff6b6b, #ee5a24); color: white; padding: 1.5rem; text-align: center; }
    .header h4 { margin: 0; font-weight: bold; }
    .status { font-size: 0.85rem; opacity: 0.9; margin-top: 5px; }
    .chat { height: 500px; overflow-y: auto; padding: 20px; background: #f8f9fa; }
    .msg { padding: 12px 18px; border-radius: 25px; margin: 12px 0; max-width: 80%; word-wrap: break-word; animation: fadeIn 0.3s; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .user { background: #ff6b6b; color: white; margin-left: auto; text-align: right; }
    .bot { background: white; color: #333; border: 1px solid #e9ecef; }
    .input-group { border-radius: 50px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .form-control { border: none; padding: 15px 20px; font-size: 1rem; }
    .btn-send { background: #ff6b6b; color: white; border: none; padding: 15px 25px; font-weight: bold; transition: background 0.3s; }
    .btn-send:hover { background: #ee5a24; }
    .btn-send:disabled { opacity: 0.6; cursor: not-allowed; }
    .thinking { display: none; text-align: center; padding: 10px; color: #666; font-style: italic; }
    .welcome { text-align: center; color: #666; padding: 20px; }
  </style>
</head>
<body>
  <div class="container d-flex align-items-center justify-content-center min-vh-100">
    <div class="card w-100">
      <div class="header">
        <h4>FUDMA EDU-BOT</h4>
        <div class="status">Powered by Google Gemini 2.5 Flash | Ask about 2025 Admissions, Courses, Campus Life & More!</div>
      </div>
      <div class="card-body p-0">
        <div id="chat" class="chat">
          <div class="welcome msg bot">
            <strong>Hello! 👋 I'm FUDMA EDU-BOT (Updated 2025).</strong><br>
            Your go-to AI for Federal University Dutsin-Ma.<br>
            e.g., "FUDMA 2025 cutoff marks?" or "New campus facilities."<br>
            Let's get started!
          </div>
        </div>
        <div class="p-3">
          <div class="input-group">
            <input type="text" id="q" class="form-control" placeholder="Type your question here..." autocomplete="off">
            <button class="btn-send" id="sendBtn">Send</button>
          </div>
          <div id="thinking" class="thinking"> EDU-BOT is thinking...</div>
        </div>
      </div>
    </div>
  </div>

  <script>
    const chat = document.getElementById('chat');
    const input = document.getElementById('q');
    const sendBtn = document.getElementById('sendBtn');
    const thinking = document.getElementById('thinking');
    let canSend = true;

    function add(text, type) {
      const div = document.createElement('div');
      div.className = `msg ${type}`;
      div.innerHTML = text.replace(/\n/g, '<br>');
      chat.appendChild(div);
      chat.scrollTop = chat.scrollHeight;
    }

    function showThinking() {
      thinking.style.display = 'block';
      chat.scrollTop = chat.scrollHeight;
    }

    function hideThinking() {
      thinking.style.display = 'none';
    }

    async function sendMessage() {
      if (!canSend) return;
      canSend = false;
      sendBtn.disabled = true;
      hideThinking();

      const q = input.value.trim();
      if (!q) {
        canSend = true;
        sendBtn.disabled = false;
        return;
      }

      add(q, 'user');
      input.value = '';
      showThinking();

      try {
        const res = await fetch('', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: q })
        });
        const data = await res.json();
        hideThinking();
        if (data.error) {
          add(`❌ Error: ${data.error}`, 'bot');
        } else {
          add(data.answer, 'bot');
        }
      } catch (err) {
        hideThinking();
        add('❌ Network error. Check connection and try again.', 'bot');
      }

      const isLocal = {{ is_local }};
      setTimeout(() => {
        canSend = true;
        sendBtn.disabled = false;
      }, isLocal ? 500 : 2000);  // Delay reset
    }

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', e => {
      if (e.key === 'Enter') sendMessage();
    });

    // Focus input on load
    input.focus();
  </script>
</body>
</html>
'''


@app.route('/', methods=['GET', 'POST'])
def handle_root():
    remote_addr = request.remote_addr or ''
    host = request.host or ''
    is_local = (remote_addr in ['127.0.0.1', '::1']) or ('localhost' in host)

    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        question = (data.get('question') or '').strip()
        if not question:
            return jsonify({'error': 'Ask something about FUDMA!'})
        if not GEMINI_KEY:
            return jsonify({'error': 'API key missing.'})
        if not is_local:
            time.sleep(1.8)

        payload = {
            'contents': [
                {
                    'parts': [
                        {'text': SYSTEM_PROMPT + "\n\nUser Question: " + question}
                    ]
                }
            ],
            'generationConfig': {
                'temperature': 0.2,
                'maxOutputTokens': 300,
                'topP': 0.8,
                'topK': 40
            },
            'safetySettings': [
                {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
                {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
                {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
                {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'}
            ]
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}"
        try:
            resp = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=60)
        except Exception as e:
            return jsonify({'error': f'Network issue: {e}'})

        if resp.status_code != 200:
            try:
                err = resp.json()
                msg = err.get('error', {}).get('message') or f"HTTP {resp.status_code} - Check quota at aistudio.google.com"
            except Exception:
                msg = f"HTTP {resp.status_code} - Check quota at aistudio.google.com"
            if 'not found' in msg or 'not supported' in msg:
                msg = "Model issue (deprecated). Use gemini-2.5-flash or check available models via /v1beta/models?key=..."
            if resp.status_code == 403:
                msg = "Access denied. Verify key in Google AI Studio."
            return jsonify({'error': msg})

        try:
            data = resp.json()
            answer = data.get('candidates', [])[0].get('content', {}).get('parts', [])[0].get('text', '')
        except Exception:
            answer = 'Sorry, no response. Try rephrasing!'

        return jsonify({'answer': answer.strip()})

    # GET -> render HTML with is_local injected
    return render_template_string(HTML_TEMPLATE, is_local=('true' if is_local else 'false'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
