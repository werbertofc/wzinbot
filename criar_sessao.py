from telethon.sync import TelegramClient

# === SEUS DADOS REAIS (CONFIRMADOS NA SUA FOTO) ===
API_ID = 28309670
API_HASH = '9e9c8b85665811e00cb8a9d686523234'
PHONE = '+5586999706879'  # SEU NÚMERO
SESSION_NAME = 'wzin_session'

print("CRIANDO SESSÃO DO BOT...")
print(f"API_ID: {API_ID}")
print(f"API_HASH: {API_HASH}")
print(f"NÚMERO: {PHONE}")
print("-" * 50)

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

try:
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(PHONE)
        print(f"\nCÓDIGO ENVIADO PARA {PHONE}")
        code = input("Digite o código de 5 dígitos que chegou no Telegram: ")
        client.sign_in(PHONE, code)
        print("\nSESSÃO CRIADA COM SUCESSO!")
    else:
        print("\nSESSÃO JÁ EXISTE! PODE USAR O BOT AGORA.")
except Exception as e:
    print(f"\nERRO: {e}")
    print("Tente novamente ou verifique seu número.")

print(f"\nArquivo criado: {SESSION_NAME}.session")
print("AGORA RODE: python bot.py")
