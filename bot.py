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

# Arquivos
ACESSO_FILE = 'acesso.json'
GRUPOS_FILE = 'grupos.json'
DESTINOS_FILE = 'destinos.json'
DESTINOS_BR_FILE = 'destinos_br.json'
BOTS_OFICIAIS_FILE = 'bots_oficiais.json'
BOTS_BR_FILE = 'bots_br.json'
DELAY_FILE = 'delay.txt'
DELAY_BR_FILE = 'delay_br.txt'

client = TelegramClient(SESSION, API_ID, API_HASH)

acesso = {}
grupos = {}
destinos = set()
destinos_br = set()
bots_oficiais = set()
bots_br = set()
delay = 30
delay_br = 30
last_like = {}

pending_responses = {}

# ========================================
# MENSAGEM DE COMPRA
# ========================================
MSG_COMPRA = (
    "Você precisa comprar acesso para usar o /like!\n\n"
    "Planos:\n"
    "• Semanal → R$ 9,00 (7 dias)\n"
    "• 2 Dias → R$ 4,00\n\n"
    "Chave Pix: werbertgamer@gmail.com\n"
    "ADM: @werbert_ofc\n\n"
    "Após pagar, envie o comprovante!"
)

# ========================================
# SALVAR/CARREGAR
# ========================================
def carregar_acesso():
    global acesso
    if os.path.exists(ACESSO_FILE):
        try:
            with open(ACESSO_FILE, 'r') as f:
                acesso = json.load(f)
        except:
            acesso = {}
    else:
        acesso = {}

def salvar_acesso():
    with open(ACESSO_FILE, 'w') as f:
        json.dump(acesso, f, indent=2)

def carregar_grupos():
    global grupos
    if os.path.exists(GRUPOS_FILE):
        with open(GRUPOS_FILE, 'r') as f:
            grupos = json.load(f)
    else:
        grupos = {}

def salvar_grupos():
    with open(GRUPOS_FILE, 'w') as f:
        json.dump(grupos, f, indent=2)

def carregar_destinos():
    global destinos
    if os.path.exists(DESTINOS_FILE):
        with open(DESTINOS_FILE, 'r') as f:
            destinos = set(json.load(f))
    else:
        destinos = set()

def salvar_destinos():
    with open(DESTINOS_FILE, 'w') as f:
        json.dump(list(destinos), f, indent=2)

def carregar_destinos_br():
    global destinos_br
    if os.path.exists(DESTINOS_BR_FILE):
        with open(DESTINOS_BR_FILE, 'r') as f:
            destinos_br = set(json.load(f))
    else:
        destinos_br = set()

def salvar_destinos_br():
    with open(DESTINOS_BR_FILE, 'w') as f:
        json.dump(list(destinos_br), f, indent=2)

def carregar_bots_oficiais():
    global bots_oficiais
    if os.path.exists(BOTS_OFICIAIS_FILE):
        with open(BOTS_OFICIAIS_FILE, 'r') as f:
            bots_oficiais = set(json.load(f))
    else:
        bots_oficiais = set()

def salvar_bots_oficiais():
    with open(BOTS_OFICIAIS_FILE, 'w') as f:
        json.dump(list(bots_oficiais), f, indent=2)

def carregar_bots_br():
    global bots_br
    if os.path.exists(BOTS_BR_FILE):
        with open(BOTS_BR_FILE, 'r') as f:
            bots_br = set(json.load(f))
    else:
        bots_br = set()

def salvar_bots_br():
    with open(BOTS_BR_FILE, 'w') as f:
        json.dump(list(bots_br), f, indent=2)

def carregar_delay():
    global delay
    if os.path.exists(DELAY_FILE):
        with open(DELAY_FILE, 'r') as f:
            try: delay = max(0, int(f.read().strip()))
            except: delay = 30
    else:
        delay = 30

def salvar_delay():
    with open(DELAY_FILE, 'w') as f:
        f.write(str(delay))

# Carregar tudo
carregar_acesso()
carregar_grupos()
carregar_destinos()
carregar_destinos_br()
carregar_bots_oficiais()
carregar_bots_br()
carregar_delay()

# ========================================
# AUXILIARES
# ========================================
def eh_dono(uid): return uid == DONO_ID

def tem_acesso(uid):
    uid = str(uid)
    if uid not in acesso:
        return False
    try:
        exp = datetime.strptime(acesso[uid], "%Y-%m-%d")
        if datetime.now() > exp:
            del acesso[uid]
            salvar_acesso()
            return False
        return True
    except:
        del acesso[uid]
        salvar_acesso()
        return False

def pode_like(uid):
    if eh_dono(uid): return True
    agora = time.time()
    ultimo = last_like.get(uid, 0)
    if agora - ultimo < delay: return False
    last_like[uid] = agora
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
    "• /like 12345678 → Todos os grupos\n"
    "• /like BR 181814612 → 100 likes (grupo BR)\n"
    "• /meuid → Seu ID\n"
    "• /idgrupo → ID do grupo\n\n"
    "Compre com @werbert_ofc"
)

@client.on(events.NewMessage(pattern='/start|/menu'))
async def start(e):
    await e.reply(MENU_PUBLICO)

# ========================================
# /meuid
# ========================================
@client.on(events.NewMessage(pattern='/meuid'))
async def meuid(e):
    await e.reply(f"Seu ID:\n`{e.sender_id}`")

# ========================================
# /idgrupo
# ========================================
@client.on(events.NewMessage(pattern='/idgrupo'))
async def idgrupo(e):
    if e.is_private:
        await e.reply("Use em grupo.")
        return
    chat = await e.get_chat()
    cid = f"-100{chat.id}" if (hasattr(chat, 'megagroup') or hasattr(chat, 'broadcast')) else f"-{chat.id}"
    titulo = chat.title or "Sem nome"
    await e.reply(f"ID: `{cid}`\nNome: {escape(titulo)}")

# ========================================
# /adduser
# ========================================
@client.on(events.NewMessage(pattern=r'(?i)^/adduser\s+(\d+)\s+(\d+)$'))
async def adduser(e):
    if not eh_dono(e.sender_id):
        await e.reply("Apenas o dono pode usar este comando.")
        return

    uid = e.pattern_match.group(1)
    dias = int(e.pattern_match.group(2))
    if dias <= 0:
        await e.reply("Dias deve ser maior que 0.")
        return

    exp = (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")
    acesso[uid] = exp
    salvar_acesso()

    await e.reply(
        f"USUÁRIO ADICIONADO!\n\n"
        f"• ID: `{uid}`\n"
        f"• Dias: `{dias}`\n"
        f"• Expira: `{exp}`"
    )

# ========================================
# MENU DO DONO
# ========================================
@client.on(events.NewMessage(pattern='/menudono'))
async def menudono(e):
    if not eh_dono(e.sender_id):
        await e.reply("Apenas o dono.")
        return
    bots_normais = "\n".join([f"• `{b}`" for b in bots_oficiais]) if bots_oficiais else "*nenhum*"
    bots_brs = "\n".join([f"• `{b}`" for b in bots_br]) if bots_br else "*nenhum*"
    texto = (
        "PAINEL DO DONO\n\n"
        "BOTS NORMAIS:\n" + bots_normais + "\n\n"
        "BOTS BR:\n" + bots_brs + "\n\n"
        "• /addbot 123456 → Adiciona bot normal\n"
        "• /addbotbr 789012 → Adiciona bot BR\n"
        "• /listabot → Lista bots normais\n"
        "• /listabotbr → Lista bots BR\n"
        "• /destino -100... → Adiciona destino normal\n"
        "• /destinobr -100... → Adiciona destino BR\n"
        "• /removerdestino -100... → Remove destino normal\n"
        "• /removerdestinobr -100... → Remove destino BR\n"
        "• /listadestinos → Lista destinos normais\n"
        "• /listadestinobr → Lista destinos BR\n"
        "• /delay 30 → Delay único\n"
        "• /adduser 123456 7 → Adiciona usuário\n\n"
        f"Usuários: {len(acesso)}\n"
        f"Destinos normais: {len(destinos)}\n"
        f"Destinos BR: {len(destinos_br)}"
    )
    await e.reply(texto)

# ========================================
# /addbot
# ========================================
@client.on(events.NewMessage(pattern=r'(?i)^/addbot\s+(\d+)$'))
async def addbot(e):
    if not eh_dono(e.sender_id): return
    bot_id = e.pattern_match.group(1)
    bots_oficiais.add(bot_id)
    salvar_bots_oficiais()
    await e.reply(f"Bot normal adicionado:\n`{bot_id}`")

# ========================================
# /addbotbr
# ========================================
@client.on(events.NewMessage(pattern=r'(?i)^/addbotbr\s+(\d+)$'))
async def addbotbr(e):
    if not eh_dono(e.sender_id): return
    bot_id = e.pattern_match.group(1)
    bots_br.add(bot_id)
    salvar_bots_br()
    await e.reply(f"Bot BR adicionado:\n`{bot_id}`")

# ========================================
# /listabot
# ========================================
@client.on(events.NewMessage(pattern='/listabot'))
async def listabot(e):
    if not eh_dono(e.sender_id): return
    if not bots_oficiais:
        await e.reply("Nenhum bot normal.")
        return
    lista = "\n".join([f"• `{b}`" for b in bots_oficiais])
    await e.reply(f"BOTS NORMAIS:\n{lista}")

# ========================================
# /listabotbr
# ========================================
@client.on(events.NewMessage(pattern='/listabotbr'))
async def listabotbr(e):
    if not eh_dono(e.sender_id): return
    if not bots_br:
        await e.reply("Nenhum bot BR.")
        return
    lista = "\n".join([f"• `{b}`" for b in bots_br])
    await e.reply(f"BOTS BR:\n{lista}")

# ========================================
# /destino (normal)
# ========================================
@client.on(events.NewMessage(pattern=r'(?i)^/destino\s+(-?\d+)$'))
async def destino_normal(e):
    if not eh_dono(e.sender_id): return
    cid = e.pattern_match.group(1)
    destinos.add(cid)
    salvar_destinos()
    await e.reply(f"Destino normal adicionado:\n`{cid}`")

# ========================================
# /destinobr
# ========================================
@client.on(events.NewMessage(pattern=r'(?i)^/destinobr\s+(-?\d+)$'))
async def destinobr(e):
    if not eh_dono(e.sender_id): return
    cid = e.pattern_match.group(1)
    destinos_br.add(cid)
    salvar_destinos_br()
    await e.reply(f"Destino BR adicionado:\n`{cid}`")

# ========================================
# /removerdestino (normal)
# ========================================
@client.on(events.NewMessage(pattern=r'(?i)^/removerdestino\s+(-?\d+)$'))
async def removerdestino_normal(e):
    if not eh_dono(e.sender_id): return
    cid = e.pattern_match.group(1)
    if cid in destinos:
        destinos.remove(cid)
        salvar_destinos()
        await e.reply(f"Destino normal removido:\n`{cid}`")
    else:
        await e.reply("Não é destino normal.")

# ========================================
# /removerdestinobr
# ========================================
@client.on(events.NewMessage(pattern=r'(?i)^/removerdestinobr\s+(-?\d+)$'))
async def removerdestinobr(e):
    if not eh_dono(e.sender_id): return
    cid = e.pattern_match.group(1)
    if cid in destinos_br:
        destinos_br.remove(cid)
        salvar_destinos_br()
        await e.reply(f"Destino BR removido:\n`{cid}`")
    else:
        await e.reply("Não é destino BR.")

# ========================================
# /listadestinos
# ========================================
@client.on(events.NewMessage(pattern='/listadestinos'))
async def listadestinos(e):
    if not eh_dono(e.sender_id): return
    if not destinos:
        await e.reply("Nenhum destino normal.")
        return
    lista = "\n".join([f"• `{d}`" for d in destinos])
    await e.reply(f"DESTINOS NORMAIS:\n{lista}")

# ========================================
# /listadestinobr
# ========================================
@client.on(events.NewMessage(pattern='/listadestinobr'))
async def listadestinobr(e):
    if not eh_dono(e.sender_id): return
    if not destinos_br:
        await e.reply("Nenhum destino BR.")
        return
    lista = "\n".join([f"• `{d}`" for d in destinos_br])
    await e.reply(f"DESTINOS BR:\n{lista}")

# ========================================
# /adduser
# ========================================
@client.on(events.NewMessage(pattern=r'(?i)^/adduser\s+(\d+)\s+(\d+)$'))
async def adduser(e):
    if not eh_dono(e.sender_id): return
    uid = e.pattern_match.group(1)
    dias = int(e.pattern_match.group(2))
    if dias <= 0: return
    exp = (datetime.now() + timedelta(days=dias)).strftime("%Y-%m-%d")
    acesso[uid] = exp; salvar_acesso()
    await e.reply(f"Usuário `{uid}` expira em `{exp}`")

# ========================================
# /delay (ÚNICO)
# ========================================
@client.on(events.NewMessage(pattern=r'(?i)^/delay\s+(\d+)$'))
async def delay_cmd(e):
    if not eh_dono(e.sender_id): return
    global delay
    delay = int(e.pattern_match.group(1)); salvar_delay()
    await e.reply(f"Delay único: {delay}s (para /like e /like BR)")

# ========================================
# /listarcanais, /addgrupo, /removergrupo, etc...
# (mantidos — não repito)

# ========================================
# /like (NORMAL)
# ========================================
@client.on(events.NewMessage(pattern=r'/like (\d+)'))
async def like(e):
    if not bots_oficiais:
        await e.reply("Nenhum bot normal! Use /addbot")
        return

    uid = e.sender_id
    pid = e.pattern_match.group(1)
    if not tem_acesso(uid) and not eh_dono(uid):
        await e.reply(MSG_COMPRA); return
    if not pode_like(uid):
        await e.reply(f"Aguarde {int(delay - (time.time() - last_like.get(uid, 0)))}s"); return
    if not destinos:
        await e.reply("Nenhum destino normal."); return

    msg = await e.reply("Enviando likes...")

    enviados = 0
    for cid in destinos:
        for bot_id in bots_oficiais:
            try:
                sent_msg = await client.send_message(int(cid), f"/like {pid}")
                key = (int(cid), sent_msg.id)
                pending_responses[key] = (e.chat_id, msg.id, "normal", bot_id)
                enviados += 1
                await asyncio.sleep(0.3)
            except: pass

    if enviados > 0:
        await msg.edit(f"Enviado para **{len(destinos)} grupo(s)**!")
    else:
        await msg.edit("Erro.")

# ========================================
# /like BR
# ========================================
@client.on(events.NewMessage(pattern=r'(?i)^/like\s+BR\s+(\d+)'))
async def like_br(e):
    if not bots_br:
        await e.reply("Nenhum bot BR! Use /addbotbr")
        return

    uid = e.sender_id
    player_id = e.pattern_match.group(1)
    if not tem_acesso(uid) and not eh_dono(uid):
        await e.reply(MSG_COMPRA); return
    if not pode_like(uid):  # MESMO DELAY!
        await e.reply(f"Aguarde {int(delay - (time.time() - last_like.get(uid, 0)))}s"); return
    if not destinos_br:
        await e.reply("Nenhum destino BR."); return

    msg = await e.reply(f"Enviando 100 likes para **{player_id}**...")

    enviados = 0
    for cid in destinos_br:
        for bot_id in bots_br:
            try:
                sent_msg = await client.send_message(int(cid), f"/like BR {player_id}")
                key = (int(cid), sent_msg.id)
                pending_responses[key] = (e.chat_id, msg.id, "br", bot_id)
                enviados += 1
                await asyncio.sleep(0.3)
            except: pass

    if enviados > 0:
        await msg.edit("Enviado! Aguarde resposta...")
    else:
        await msg.edit("Erro.")

# ========================================
# RESPOSTAS E EDIÇÕES
# ========================================
@client.on(events.NewMessage)
async def resposta(e):
    if not e.is_reply or not e.reply_to_msg_id: return
    key = (e.chat_id, e.reply_to_msg_id)
    if key not in pending_responses: return

    _, _, tipo, bot_esperado = pending_responses[key]
    if str(e.sender_id) != bot_esperado: return

    cliente_chat, cliente_msg_id = pending_responses[key][:2]
    texto = trocar_adm(e.text or "")
    try:
        await client.edit_message(cliente_chat, cliente_msg_id, texto)
    except: pass

@client.on(events.MessageEdited)
async def edicao(e):
    if not e.is_reply or not e.reply_to_msg_id: return
    key = (e.chat_id, e.reply_to_msg_id)
    if key not in pending_responses: return

    _, _, tipo, bot_esperado = pending_responses[key]
    if str(e.sender_id) != bot_esperado: return

    cliente_chat, cliente_msg_id = pending_responses[key][:2]
    texto = trocar_adm(e.text or "")
    try:
        await client.edit_message(cliente_chat, cliente_msg_id, texto)
    except: pass

# ========================================
# INICIAR
# ========================================
print(f"BOT INICIADO! | Delay único: {delay}s")
client.start()
client.run_until_disconnected()
