from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import asyncio
import json
import os
import re
import time
from datetime import datetime, timedelta

# ========================================
# === SEUS DADOS ===
# ========================================
API_ID = 28309670
API_HASH = '9e9c8b85665811e00cb8a9d686523234'
SESSION = 'wzin_session'
PHONE = '+5586999706879'
DONO_ID = 6430703027

# GRUPO BR (destino fixo)
GRUPO_BR = "-1003297568556"

# Arquivos
ACESSO_FILE = 'acesso.json'
GRUPOS_FILE = 'grupos.json'
DESTINOS_FILE = 'destinos.json'
DELAY_FILE = 'delay.txt'
DELAY_BR_FILE = 'delay_br.txt'
BOT_OFICIAL_FILE = 'bot_oficial.json'

client = TelegramClient(SESSION, API_ID, API_HASH)

acesso = {}
grupos = {}
destinos = {}
delay = 30
delay_br = 30
last_like = {}
last_like_br = {}
bot_oficial_id = None

# MAPEAMENTO: (chat_destino, msg_id_destino) → (chat_cliente, msg_id_cliente)
pending_responses = {}

# ========================================
# SALVAR/CARREGAR
# ========================================
def carregar_acesso():
    global acesso
    if os.path.exists(ACESSO_FILE):
        with open(ACESSO_FILE, 'r') as f:
            acesso = json.load(f)

def salvar_acesso():
    with open(ACESSO_FILE, 'w') as f:
        json.dump(acesso, f, indent=2)

def carregar_grupos():
    global grupos
    if os.path.exists(GRUPOS_FILE):
        with open(GRUPOS_FILE, 'r') as f:
            grupos = json.load(f)

def salvar_grupos():
    with open(GRUPOS_FILE, 'w') as f:
        json.dump(grupos, f, indent=2)

def carregar_destinos():
    global destinos
    if os.path.exists(DESTINOS_FILE):
        with open(DESTINOS_FILE, 'r') as f:
            destinos = json.load(f)

def salvar_destinos():
    with open(DESTINOS_FILE, 'w') as f:
        json.dump(destinos, f, indent=2)

def carregar_delay():
    global delay
    if os.path.exists(DELAY_FILE):
        with open(DELAY_FILE, 'r') as f:
            try: delay = max(0, int(f.read().strip()))
            except: delay = 30

def salvar_delay():
    with open(DELAY_FILE, 'w') as f:
        f.write(str(delay))

def carregar_delay_br():
    global delay_br
    if os.path.exists(DELAY_BR_FILE):
        with open(DELAY_BR_FILE, 'r') as f:
            try: delay_br = max(0, int(f.read().strip()))
            except: delay_br = 30

def salvar_delay_br():
    with open(DELAY_BR_FILE, 'w') as f:
        f.write(str(delay_br))

def carregar_bot_oficial():
    global bot_oficial_id
    if os.path.exists(BOT_OFICIAL_FILE):
        with open(BOT_OFICIAL_FILE, 'r') as f:
            data = json.load(f)
            bot_oficial_id = data.get('id')
    if bot_oficial_id:
        print(f"[INFO] Bot oficial carregado: {bot_oficial_id}")

def salvar_bot_oficial():
    with open(BOT_OFICIAL_FILE, 'w') as f:
        json.dump({'id': bot_oficial_id}, f, indent=2)

# Carregar tudo
carregar_acesso()
carregar_grupos()
carregar_destinos()
carregar_delay()
carregar_delay_br()
carregar_bot_oficial()

# ========================================
# AUXILIARES
# ========================================
def eh_dono(uid): return uid == DONO_ID
def tem_acesso(uid):
    uid = str(uid)
    if uid not in acesso: return False
    try:
        exp = datetime.strptime(acesso[uid], "%Y-%m-%d")
        if datetime.now() > exp:
            del acesso[uid]; salvar_acesso(); return False
        return True
    except: return False

def pode_like(uid):
    if eh_dono(uid): return True
    agora = time.time()
    ultimo = last_like.get(uid, 0)
    if agora - ultimo < delay: return False
    last_like[uid] = agora
    return True

def pode_like_br(uid):
    if eh_dono(uid): return True
    agora = time.time()
    ultimo = last_like_br.get(uid, 0)
    if agora - ultimo < delay_br: return False
    last_like_br[uid] = agora
    return True

def escape(t):
    if not t: return ""
    return re.sub(r'([_*[\]()~`>#+=|{}.!-])', r'\\\1', t)

def trocar_adm(texto):
    if not texto: return ""
    texto = re.sub(r"@leroyadmff", "@werbert_ofc", texto, flags=re.IGNORECASE)
    texto = re.sub(r"Desenvolvido por @leroyadmff", "Desenvolvido por @werbert_ofc", texto, flags=re.IGNORECASE)
    return texto

# ========================================
# MENU PÚBLICO
# ========================================
MENU_PUBLICO = (
    "BOT DE LIKES FREE FIRE\n\n"
    "Comandos disponíveis:\n"
    "• /like 12345678 → Envia para todos os grupos\n"
    "• /like BR 181814612 → Envia 100 likes para o ID (só grupo BR)\n"
    "• /meuid → Mostra seu ID\n"
    "• /idgrupo → ID do grupo (use no grupo)\n\n"
    "Para usar, você precisa de acesso pago!\n"
    "Compre com @werbert_ofc"
)

@client.on(events.NewMessage(pattern='/start|/menu'))
async def start(e):
    await e.reply(MENU_PUBLICO)

# ========================================
# MENU DO DONO
# ========================================
@client.on(events.NewMessage(pattern='/menudono'))
async def menudono(e):
    if not eh_dono(e.sender_id):
        await e.reply("Apenas o dono pode usar este comando.")
        return
    bot_status = f"Bot oficial: `{bot_oficial_id}`" if bot_oficial_id else "Bot oficial: *não configurado*"
    texto = (
        "PAINEL DO DONO\n\n"
        "Seus comandos:\n"
        "• /adduser 123456 7 → 7 dias\n"
        "• /listarcanais → Lista grupos/canais\n"
        "• /addgrupo -1001234567890 \"Nome\" → Adiciona grupo\n"
        "• /removergrupo \"Nome\" → Remove grupo\n"
        "• /destino -1001234567890 → Destino por ID\n"
        "• /destino \"Nome\" → Destino por nome\n"
        "• /removerdestino -1001234567890 → Remove por ID\n"
        "• /removerdestino \"Nome\" → Remove por nome\n"
        "• /listadestinos\n"
        "• /delay 30 → Delay geral\n"
        "• /delaybr 30 → Delay para /like BR\n"
        "• /addbot 123456789 → Define bot oficial\n"
        "• /removerbot 123456789 → Remove bot oficial\n\n"
        f"Usuários: {len(acesso)}\n"
        f"Grupos: {len(grupos)}\n"
        f"Destinos: {len(destinos)}\n"
        f"{bot_status}\n"
        f"Delay geral: {delay}s | Delay BR: {delay_br}s"
    )
    await e.reply(texto)

# ========================================
# /delaybr
# ========================================
@client.on(events.NewMessage(pattern=r'(?i)^/delaybr\s+(\d+)$'))
async def delaybr_cmd(e):
    if not eh_dono(e.sender_id):
        await e.reply("Apenas o dono.")
        return
    global delay_br
    delay_br = int(e.pattern_match.group(1))
    salvar_delay_br()
    await e.reply(f"Delay para /like BR: {delay_br}s")

# ========================================
# /like 12345678 → TODOS OS DESTINOS
# ========================================
@client.on(events.NewMessage(pattern=r'/like (\d+)'))
async def like(e):
    if bot_oficial_id is None:
        await e.reply("Bot oficial não configurado! Use /addbot")
        return

    uid = e.sender_id
    pid = e.pattern_match.group(1)
    if not tem_acesso(uid) and not eh_dono(uid):
        await e.reply(MSG_COMPRA); return
    if not pode_like(uid):
        await e.reply(f"Aguarde {int(delay - (time.time() - last_like.get(uid, 0)))}s"); return
    if not destinos:
        await e.reply("Nenhum destino configurado."); return

    msg = await e.reply("Enviando likes para os grupos...")

    enviados = 0
    for cid in destinos:
        try:
            sent_msg = await client.send_message(int(cid), f"/like {pid}")
            key = (int(cid), sent_msg.id)
            pending_responses[key] = (e.chat_id, msg.id)
            print(f"[LOG] /like → {cid}, msg_id={sent_msg.id}")
            enviados += 1
            await asyncio.sleep(0.5)
        except Exception as ex:
            print(f"[ERRO] Enviar para {cid}: {ex}")

    if enviados > 0:
        await msg.edit(f"Likes enviados para **{enviados} grupo(s)**! Aguarde a resposta...")
    else:
        await msg.edit("Erro ao enviar likes.")

# ========================================
# /like BR 181814612 → SÓ PARA GRUPO BR (envia o ID do jogador)
# ========================================
@client.on(events.NewMessage(pattern=r'(?i)^/like\s+BR\s+(\d+)$'))
async def like_br(e):
    if bot_oficial_id is None:
        await e.reply("Bot oficial não configurado! Use /addbot")
        return

    uid = e.sender_id
    player_id = e.pattern_match.group(1)

    if not tem_acesso(uid) and not eh_dono(uid):
        await e.reply(MSG_COMPRA); return
    if not pode_like_br(uid):
        await e.reply(f"Aguarde {int(delay_br - (time.time() - last_like_br.get(uid, 0)))}s"); return

    msg = await e.reply(f"Enviando 100 likes para o ID **{player_id}** no grupo BR...")

    try:
        sent_msg = await client.send_message(int(GRUPO_BR), f"/like BR {player_id}")
        key = (int(GRUPO_BR), sent_msg.id)
        pending_responses[key] = (e.chat_id, msg.id)
        print(f"[LOG] /like BR {player_id} → {GRUPO_BR}, msg_id={sent_msg.id}")
        await msg.edit("Likes enviados para o grupo BR! Aguarde a resposta...")
    except Exception as ex:
        print(f"[ERRO] Enviar BR: {ex}")
        await msg.edit("Erro ao enviar para o grupo BR.")

# ========================================
# CAPTURA RESPOSTA INICIAL
# ========================================
@client.on(events.NewMessage)
async def resposta_inicial(e):
    if bot_oficial_id is None: return
    if e.sender_id != bot_oficial_id: return
    if not e.is_reply or not e.reply_to_msg_id: return

    key = (e.chat_id, e.reply_to_msg_id)
    if key not in pending_responses: return

    cliente_chat, cliente_msg_id = pending_responses[key]
    texto =...

    print(f"[LOG] RESPOSTA INICIAL: {e.text}")
    try:
        await client.edit_message(cliente_chat, cliente_msg_id, texto)
    except Exception as ex:
        print(f"[ERRO] Editar inicial: {ex}")

# ========================================
# CAPTURA EDIÇÕES
# ========================================
@client.on(events.MessageEdited)
async def edicao_resposta(e):
    if bot_oficial_id is None: return
    if e.sender_id != bot_oficial_id: return
    if not e.is_reply or not e.reply_to_msg_id: return

    key = (e.chat_id, e.reply_to_msg_id)
    if key not in pending_responses: return

    cliente_chat, cliente_msg_id = pending_responses[key]
    texto = trocar_adm(e.text or "")

    print(f"[LOG] EDIÇÃO: {e.text}")
    try:
        await client.edit_message(cliente_chat, cliente_msg_id, texto)
    except Exception as ex:
        print(f"[ERRO] Editar edição: {ex}")

# ========================================
# COMANDOS DO DONO (mantidos)
# ========================================
@client.on(events.NewMessage(pattern=r'(?i)^/addbot\s+(\d+)$'))
async def addbot(e):
    if not eh_dono(e.sender_id): await e.reply("Apenas o dono."); return
    global bot_oficial_id
    bot_oficial_id = int(e.pattern_match.group(1))
    salvar_bot_oficial()
    await e.reply(f"Bot oficial definido!\nID: `{bot_oficial_id}`")

@client.on(events.NewMessage(pattern=r'(?i)^/removerbot\s+(\d+)$'))
async def removerbot(e):
    if not eh_dono(e.sender_id): await e.reply("Apenas o dono."); return
    global bot_oficial_id
    bid = e.pattern_match.group(1)
    if bot_oficial_id == int(bid):
        bot_oficial_id = None
        if os.path.exists(BOT_OFICIAL_FILE): os.remove(BOT_OFICIAL_FILE)
        await e.reply(f"Bot oficial removido!\nID: `{bid}`")
    else:
        await e.reply(f"Bot oficial não é `{bid}`.")

# [RESTO DOS COMANDOS DO DONO: /addgrupo, /destino, etc — mantenha os que já estavam]

# ========================================
# INICIAR
# ========================================
status = f"Bot oficial: {bot_oficial_id}" if bot_oficial_id else "Bot oficial: não configurado"
print(f"BOT INICIADO! {status} | /like BR → 100 likes no grupo BR")
client.start()
client.run_until_disconnected()
