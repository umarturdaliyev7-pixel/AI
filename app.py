import re
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import httpx

app = FastAPI(title="UMAR AI Cyber")
SYSTEM = "You are UMAR AI, an Uzbek-language coding assistant for programming and authorized defensive security. Do not facilitate unauthorized intrusion."

class Chat(BaseModel):
    key: str = Field(min_length=8, max_length=500)
    messages: list[dict] = Field(min_length=1, max_length=25)

class Scan(BaseModel):
    source: str = Field(max_length=50000)

@app.get("/health")
def health():
    return {"status": "ok", "service": "umar-ai"}

@app.post("/api/chat")
async def chat(req: Chat):
    messages = [{"role": "system", "content": SYSTEM}]
    for m in req.messages[-20:]:
        if m.get("role") in ("user", "assistant") and isinstance(m.get("content"), str):
            messages.append({"role": m["role"], "content": m["content"][:8000]})
    if len(messages) == 1:
        raise HTTPException(400, "Xabar yo'q")
    try:
        async with httpx.AsyncClient(timeout=65) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": "Bearer " + req.key, "Content-Type": "application/json", "X-Title": "UMAR AI Cyber"},
                json={"model": "openrouter/free", "messages": messages, "max_tokens": 1100},
            )
        if response.status_code == 429:
            raise HTTPException(429, "OpenRouter bepul limitiga yetildi.")
        if response.status_code in (401, 403):
            raise HTTPException(401, "API kalit noto'g'ri yoki ruxsat yo'q.")
        if response.status_code >= 400:
            raise HTTPException(502, f"OpenRouter xatosi: {response.status_code}")
        data = response.json()
        return {"reply": data["choices"][0]["message"]["content"], "model": data.get("model", "openrouter/free")}
    except httpx.HTTPError:
        raise HTTPException(502, "OpenRouter bilan aloqa uzildi.")

RULES = [
    ("eval()", r"\beval\s*\(", "Ishonchsiz kodni eval bilan ishlatmang"),
    ("exec()", r"\bexec\s*\(", "Ishonchsiz kodni exec bilan ishlatmang"),
    ("Hardcoded secret", r"(?i)(password|passwd|secret)\s*[:=]\s*['\"][^'\"]{3,}", "Maxfiy ma'lumotni environment variables da saqlang"),
    ("innerHTML", r"\binnerHTML\s*=", "Tashqi matn uchun textContent ishlating"),
]
@app.post("/api/scan")
def scan(req: Scan):
    issues = []
    for name, pattern, tip in RULES:
        for match in list(re.finditer(pattern, req.source))[:8]:
            issues.append({"title": name, "line": req.source.count("\n", 0, match.start()) + 1, "tip": tip})
    return {"issues": issues, "note": "Bu faqat oddiy statik kod tekshiruvi."}

@app.get("/", response_class=HTMLResponse)
def index():
    return PAGE

PAGE = """<!doctype html><html lang="uz"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UMAR AI Cyber</title><style>
*{box-sizing:border-box}body{margin:0;background:#080f11;color:#d8f4e6;font:15px system-ui,Arial}header{padding:20px;background:#101b1d;border-bottom:1px solid #29473a}h1{margin:0;color:#6cf5b1}small{color:#9fb6ac}.layout{max-width:1100px;margin:24px auto;padding:0 16px;display:grid;grid-template-columns:270px 1fr;gap:16px}.panel{background:#122024;border:1px solid #2d5946;border-radius:14px;padding:18px}input,textarea{background:#071214;color:white;border:1px solid #3d6959;border-radius:8px;padding:11px;width:100%;font:inherit}textarea{resize:vertical}button{padding:11px 15px;background:#37c88d;color:#062417;border:0;border-radius:8px;font-weight:700;cursor:pointer}button:disabled{opacity:.5}.muted{color:#a6bdb1}.tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}.tab{background:#203c34;color:white}.tab.on{background:#50dca1;color:#00291c}.hidden{display:none}.log{height:390px;overflow-y:auto}.message{background:#1b3530;border-radius:10px;padding:12px;margin:9px 0;white-space:pre-wrap;overflow-wrap:anywhere}.message.user{background:#253a49}.entry{display:flex;gap:8px}.entry textarea{min-height:75px}.terminal{background:#020807;color:#78fdb6;border-radius:10px;min-height:220px;padding:15px;white-space:pre-wrap;font:14px Consolas,monospace}a{color:#72e9b2}label{display:block;margin:10px 0 6px}@media(max-width:750px){.layout{grid-template-columns:1fr}.log{height:320px}}
</style></head><body><header><h1>⌘ UMAR AI CYBER</h1><small>Multi-AI • Linux demo • Defensive Code Lab</small></header>
<main class="layout"><aside class="panel"><h3>⚙ Sozlamalar</h3><label>OpenRouter API kalitingiz</label><input type="password" id="key" autocomplete="off" placeholder="sk-or-v1-..."><p class="muted">Kalit faqat joriy sahifa xotirasida, serverda saqlanmaydi.</p><p>Model: <b>openrouter/free</b></p><p class="muted">Bepul model avtomatik tanlanadi. Umumiy limit tugasa, javob kelmasligi mumkin.</p><p><a href="https://openrouter.ai/settings/keys" target="_blank" rel="noopener noreferrer">API key olish</a></p><button id="reset">Chatni tozalash</button></aside>
<section class="panel"><div class="tabs"><button class="tab on" data-tab="chat">AI Chat</button><button class="tab" data-tab="lab">Security Lab</button><button class="tab" data-tab="linux">Linux Demo</button></div>
<div id="chat"><div id="log" class="log"></div><div class="entry"><textarea id="message" placeholder="React, Python yoki boshqa savol yozing..."></textarea><button id="send">Yuborish</button></div><p class="muted">Ctrl+Enter orqali yuborish mumkin.</p></div>
<div id="lab" class="hidden"><h3>O'zingizning kodingizni tekshiring</h3><p class="muted">Bu saytlarni faol skan qilmaydi.</p><textarea id="source" rows="12" placeholder="Python yoki JavaScript kodingizni joylashtiring"></textarea><p><button id="analyze">Kodni tekshirish</button></p><pre id="report" style="white-space:pre-wrap"></pre></div>
<div id="linux" class="hidden"><h3>Linux terminal o'quv rejimi</h3><p class="muted">Haqiqiy shell emas; serverda buyruqlar bajarilmaydi.</p><div id="term" class="terminal">umar@lab:~$ help</div><div class="entry"><input id="cmd" placeholder="help, pwd, ls, whoami, date, clear"><button id="run">Enter</button></div></div>
</section></main><script>
const $=id=>document.getElementById(id), messages=[];
function bubble(role,text){const el=document.createElement('div');el.className='message '+(role==='user'?'user':'');el.textContent=(role==='user'?'Siz: ':'UMAR AI: ')+text;$('log').append(el);$('log').scrollTop=$('log').scrollHeight}
bubble('assistant',"Salom! AI savolingizni yozing yoki Security Lab bo'limini oching.");
document.querySelectorAll('[data-tab]').forEach(btn=>btn.onclick=()=>{document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('on',b===btn));['chat','lab','linux'].forEach(id=>$(id).classList.toggle('hidden',id!==btn.dataset.tab))});
$('reset').onclick=()=>{messages.length=0;$('log').replaceChildren();bubble('assistant','Yangi chat boshlandi.')};
async function send(){const content=$('message').value.trim(),key=$('key').value.trim();if(!content)return;if(!key){alert('OpenRouter API kalitini kiriting');return}messages.push({role:'user',content});$('message').value='';bubble('user',content);$('send').disabled=true;try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key,messages})});const d=await r.json();if(!r.ok)throw Error(d.detail||'Xatolik');messages.push({role:'assistant',content:d.reply});bubble('assistant',d.reply+'\n\nModel: '+d.model)}catch(e){bubble('assistant','Xatolik: '+e.message)}finally{$('send').disabled=false}}
$('send').onclick=send;$('message').onkeydown=e=>{if(e.ctrlKey&&e.key==='Enter')send()};
$('analyze').onclick=async()=>{try{const r=await fetch('/api/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({source:$('source').value})});const d=await r.json();$('report').textContent=(d.issues.length?d.issues.map(x=>'Qator '+x.line+': '+x.title+' — '+x.tip).join('\n'):'Qoida bo‘yicha muammo topilmadi.')+'\n'+d.note}catch(e){$('report').textContent=e.message}};
$('run').onclick=()=>{const c=$('cmd').value.trim();$('cmd').value='';if(c==='clear'){$('term').textContent='';return}const out={help:'help, pwd, ls, whoami, date, clear',pwd:'/home/umar',ls:'projects  README.md  practice',whoami:'umar',date:new Date().toLocaleString('uz-UZ')}[c]||'Faqat o‘quv buyruqlari mavjud';$('term').textContent+='\numar@lab:~$ '+c+'\n'+out};$('cmd').onkeydown=e=>{if(e.key==='Enter')$('run').click()};
</script></body></html>"""
