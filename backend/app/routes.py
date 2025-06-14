import os
from datetime import datetime, timedelta, timezone
import jwt
import json
import requests
from flask import Blueprint, redirect, request, session, jsonify, current_app, send_from_directory
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow
from werkzeug.utils import secure_filename
from .models import db, User, Platinado, Game, ShopItem, ItemKey, UserInventory, followers

main_bp = Blueprint('main_bp', __name__, url_prefix='/api')

# --- Constantes e Chaves ---
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'openid']
CLIENT_SECRETS_FILE = 'client_secrets.json'
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
RETRO_API_USER = os.getenv("RETRO_API_USER")
RETRO_API_KEY = os.getenv("RETRO_API_KEY")

# --- Rotas de Autenticação ---
@main_bp.route('/auth/google/login')
def google_login():
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=GOOGLE_SCOPES, redirect_uri='http://localhost:5000/api/auth/google/callback')
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='select_account')
    session['state'] = state
    return redirect(authorization_url)

@main_bp.route('/auth/google/callback')
def google_callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=GOOGLE_SCOPES, state=state, redirect_uri='http://localhost:5000/api/auth/google/callback')
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    id_info = id_token.verify_oauth2_token(id_token=credentials.id_token, request=google_requests.Request(), audience=flow.client_config['client_id'], clock_skew_in_seconds=10)
    user_email, user_name, user_picture = id_info.get('email'), id_info.get('name'), id_info.get('picture')
    user = User.query.filter_by(email=user_email).first()
    is_new_user = user is None
    if is_new_user:
        user = User(email=user_email, name=user_name, picture_url=user_picture)
        db.session.add(user)
    else:
        user.name = user_name
        if not user.picture_url or 'googleusercontent' in user.picture_url: user.picture_url = user_picture
    db.session.commit()
    payload = {'sub': str(user.id), 'email': user.email, 'name': user.name, 'iat': datetime.now(timezone.utc), 'exp': datetime.now(timezone.utc) + timedelta(hours=24)}
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    if is_new_user or not user.username:
        return redirect(f"http://localhost:3000/onboarding?token={token}")
    else:
        return redirect(f"http://localhost:3000/auth/callback?token={token}")

# --- Rotas de Dados de Usuário e Perfil ---
@main_bp.route('/me')
def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '): return jsonify({"error": "Cabeçalho de autorização ausente"}), 401
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], leeway=10)
        user = User.query.get(payload['sub'])
        if not user: return jsonify({"error": "Usuário não encontrado"}), 404
        return jsonify({"id": user.id, "username": user.username, "name": user.name, "email": user.email, "picture_url": user.picture_url, "steam_id": user.steam_id, "retro_username": user.retro_username, "total_xp": user.total_xp, "total_coins": user.total_coins})
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return jsonify({"error": "Token inválido ou expirado"}), 401


@main_bp.route('/shop/items')
def list_shop_items():
    """Retorna os itens disponíveis, incluindo a quantidade em estoque correta por tipo."""
    items = ShopItem.query.all()
    items_data = []
    for item in items:
        stock = 0
        # --- NOVA LÓGICA DE ESTOQUE ---
        if item.item_type == 'GAME_KEY':
            # Se for uma chave, contamos as unidades não resgatadas
            stock = ItemKey.query.filter_by(item_id=item.id, is_redeemed=False).count()
        elif item.item_type == 'BANNER':
            # Se for um banner, o estoque é "infinito". Usamos um número alto para representar isso.
            stock = 999 

        items_data.append({
            "id": item.id,
            "appid": item.appid,
            "name": item.name,
            "description": item.description,
            "item_type": item.item_type, # Vamos enviar o tipo para o front-end
            "price_coins": item.price_coins,
            "stock": stock
        })
    return jsonify(items_data)


@main_bp.route('/profile/link-retro', methods=['POST'])
def link_retro_account():
    # ... (lógica para pegar o usuário a partir do token JWT) ...
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], leeway=10)
        user = User.query.get(payload['sub'])
    except:
        return jsonify({"error": "Token inválido"}), 401

    retro_username = request.get_json().get('retro_username')
    if not retro_username:
        return jsonify({"error": "Nome de usuário do RA não fornecido."}), 400

    # Remove espaços em branco que podem estar causando problemas
    retro_username = retro_username.strip()

    # --- INÍCIO DA DEPURAÇÃO ---
    print("\n--- DEBUG DA API RETROACHIEVEMENTS ---")
    print(f"API User sendo usado: '{RETRO_API_USER}'")
    # Mostramos apenas os 5 primeiros caracteres da chave por segurança
    print(f"API Key sendo usada: '{RETRO_API_KEY[:5] if RETRO_API_KEY else 'None'}...'")
    print(f"Username para buscar: '{retro_username}'")
    
    # Codifica a URL para lidar com caracteres especiais
    from urllib.parse import quote
    encoded_username = quote(retro_username)
    ra_url = f"https://retroachievements.org/API/API_GetUserProfile.php?z={RETRO_API_USER}&y={RETRO_API_KEY}&u={encoded_username}"
    print(f"URL montada para a requisição: {ra_url}")
    print("------------------------------------\n")
    # --- FIM DA DEPURAÇÃO ---

    try:
        response = requests.get(ra_url)
        response.raise_for_status()
        print(f"Status da resposta: {response.status_code}")
        print(f"Conteúdo da resposta: {response.text[:500]}...")  # Primeiros 500 caracteres
        
        ra_data = response.json()
        print(f"Dados JSON recebidos: {ra_data}")
        
        # Verifica se a resposta contém erro ou se o usuário não foi encontrado
        if 'Error' in ra_data:
            return jsonify({"error": f"Erro da API RetroAchievements: {ra_data['Error']}"}), 404
        elif not ra_data or 'User' not in ra_data:
            return jsonify({"error": f"Usuário '{retro_username}' não encontrado no RetroAchievements. Verifique se o nome está correto."}), 404
    except requests.exceptions.RequestException as e:
        print(f"Erro de requisição ao RetroAchievements: {e}")
        return jsonify({"error": "Não foi possível conectar com o RetroAchievements."}), 500
    except ValueError as e:
        print(f"Erro ao fazer parse do JSON: {e}")
        print(f"Resposta recebida: {response.text}")
        return jsonify({"error": "Resposta inválida do RetroAchievements."}), 500
    except Exception as e:
        print(f"Erro inesperado ao verificar usuário no RetroAchievements: {e}")
        return jsonify({"error": "Não foi possível verificar a conta no RetroAchievements."}), 500

    user.retro_username = retro_username
    db.session.commit()
    return jsonify({"message": "Conta do RetroAchievements vinculada com sucesso!"})





@main_bp.route('/shop/buy/<int:item_id>', methods=['POST'])
def buy_item(item_id):
    # ... (A lógica de autenticação do usuário continua a mesma) ...
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], leeway=10)
        user = User.query.get(payload['sub'])
    except:
        return jsonify({"error": "Token inválido"}), 401

    item_to_buy = ShopItem.query.get_or_404(item_id)
    if user.total_coins < item_to_buy.price_coins:
        return jsonify({"error": "Fichas insuficientes."}), 403

    # --- NOVA LÓGICA BASEADA NO TIPO DE ITEM ---
    
    if item_to_buy.item_type == 'BANNER':
        # Se for um banner, verifica se já está no inventário
        if UserInventory.query.filter_by(user_id=user.id, item_id=item_id).first():
            return jsonify({"error": "Você já possui este item."}), 409
        
        # Adiciona ao inventário
        user.total_coins -= item_to_buy.price_coins
        new_inventory_item = UserInventory(user_id=user.id, item_id=item_id)
        db.session.add(new_inventory_item)
        db.session.commit()
        return jsonify({"message": f"'{item_to_buy.name}' adicionado ao seu inventário!"})

    elif item_to_buy.item_type == 'GAME_KEY':
        # Lógica para resgatar chave que já tínhamos
        available_key = ItemKey.query.filter_by(item_id=item_id, is_redeemed=False).first()
        if not available_key:
            return jsonify({"error": "Item fora de estoque."}), 409
            
        user.total_coins -= item_to_buy.price_coins
        available_key.is_redeemed = True
        available_key.redeemed_by_user_id = user.id
        available_key.redeemed_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({"message": "Chave resgatada!", "redeemed_key": available_key.key_value})

    else:
        return jsonify({"error": "Tipo de item desconhecido."}), 400

@main_bp.route('/me/inventory')
def get_my_inventory():
    # Rota protegida por JWT
    auth_header = request.headers.get('Authorization')
    if not auth_header: return jsonify({"error": "Autorização ausente"}), 401
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], leeway=10)
        user = User.query.get(payload['sub'])
    except:
        return jsonify({"error": "Token inválido"}), 401
        
    inventory_items = user.inventory
    inventory_data = [{
        "inventory_id": inv_item.id,
        "item_id": inv_item.item.id,
        "name": inv_item.item.name,
        "description": inv_item.item.description,
        "item_type": inv_item.item.item_type,
        "value": inv_item.item.value, # A URL do banner estará aqui
        "appid": inv_item.item.appid
    } for inv_item in inventory_items]
    
    return jsonify(inventory_data)


@main_bp.route('/profile/equip-banner', methods=['POST'])
def equip_banner():
    # Rota protegida por JWT
    auth_header = request.headers.get('Authorization')
    if not auth_header: return jsonify({"error": "Autorização ausente"}), 401
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], leeway=10)
        user = User.query.get(payload['sub'])
    except:
        return jsonify({"error": "Token inválido"}), 401

    # Pega o ID do item do inventário que o usuário quer equipar
    inventory_id = request.get_json().get('inventory_id')
    
    # Verifica se o usuário realmente possui este item
    item_to_equip = UserInventory.query.filter_by(id=inventory_id, owner=user).first_or_404()

    if item_to_equip.item.item_type != 'BANNER':
        return jsonify({"error": "Este item não é um banner equipável."}), 400

    # Equipa o banner atualizando a URL no perfil do usuário
    user.equipped_banner_url = item_to_equip.item.value
    db.session.commit()
    
    return jsonify({"message": "Banner equipado com sucesso!"})

@main_bp.route('/user/<int:user_id>/platinados')
def get_user_platinados(user_id):
    user = User.query.get_or_404(user_id)
    platinados = user.platinados
    platinados_data = [{"appid": p.game_appid, "name": p.game_name} for p in platinados]
    return jsonify({"games": platinados_data})

@main_bp.route('/user/<int:user_id>/follow', methods=['POST'])
def follow_user(user_id):
    # --- Verificação de Token Robusta ---
    auth_header = request.headers.get('Authorization')
    # Adicionamos a verificação se o cabeçalho começa com 'Bearer '
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Autorização ausente ou mal formatada"}), 401
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], leeway=10)
        current_user = User.query.get(payload['sub'])
        if not current_user:
            return jsonify({"error": "Usuário não encontrado"}), 404
    # Capturamos os erros específicos de JWT
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        print(f"Erro de token em /follow: {e}")
        return jsonify({"error": "Token inválido ou expirado"}), 401

    # Lógica de seguir
    user_to_follow = User.query.get_or_404(user_id)
    if user_to_follow.id == current_user.id:
        return jsonify({"error": "Você não pode seguir a si mesmo."}), 400
    
    current_user.follow(user_to_follow)
    db.session.commit()
    return jsonify({"message": f"Você agora está seguindo {user_to_follow.username or user_to_follow.name}."})

@main_bp.route('/user/<int:user_id>/unfollow', methods=['POST'])
def unfollow_user(user_id):
    # --- Verificação de Token Robusta ---
    auth_header = request.headers.get('Authorization')
    # Adicionamos a mesma verificação completa aqui
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Autorização ausente ou mal formatada"}), 401
        
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], leeway=10)
        current_user = User.query.get(payload['sub'])
        if not current_user:
            return jsonify({"error": "Usuário não encontrado"}), 404
    # Capturamos os erros específicos de JWT
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        print(f"Erro de token em /unfollow: {e}")
        return jsonify({"error": "Token inválido ou expirado"}), 401

    # Lógica de deixar de seguir
    user_to_unfollow = User.query.get_or_404(user_id)
    current_user.unfollow(user_to_unfollow)
    db.session.commit()
    return jsonify({"message": f"Você deixou de seguir {user_to_unfollow.username or user_to_unfollow.name}."})

@main_bp.route('/user/<int:user_id>')
def get_public_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    
    auth_header = request.headers.get('Authorization')
    # Prepara o dicionário de dados, agora incluindo o banner
    public_data = {
        "id": user.id, 
        "username": user.username, 
        "name": user.name, # Nome do Google como fallback
        "picture_url": user.picture_url, # Foto do Google/upload como fallback
        "steam_id": user.steam_id,
        "equipped_banner_url": user.equipped_banner_url, # <<< O CAMPO QUE FALTAVA
        "total_xp": user.total_xp, 
        "total_coins": user.total_coins,
        # Valores padrão que serão sobrepostos se a conta Steam estiver conectada
        "steam_name": None, 
        "steam_avatar_url": None,
        "total_games_count": 0,
        "followers_count": user.followers.count(),
        "following_count": user.followed.count(),
        "is_followed_by_viewer": False
    }
    public_data['followers_count'] = user.followers.count()
    public_data['following_count'] = user.followed.count()
    public_data['is_followed_by_viewer'] = False


    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], leeway=10)
            viewer = User.query.get(payload['sub'])
            if viewer:
                public_data['is_followed_by_viewer'] = viewer.is_following(user)
        except:
            pass 
    # Se o usuário vinculou a conta Steam, enriquece os dados
    if user.steam_id:
        try:
            player_summary_url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={user.steam_id}"
            summary_response = requests.get(player_summary_url).json()
            players = summary_response.get('response', {}).get('players', [])
            if players:
                player_info = players[0]
                # Atualiza os campos com os dados da Steam
                public_data.update({
                    'steam_name': player_info.get('personaname'), 
                    'steam_avatar_url': player_info.get('avatarfull')
                })
        except Exception as e:
            print(f"Erro ao buscar sumário da Steam: {e}")
        try:
            owned_games_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={user.steam_id}"
            games_response = requests.get(owned_games_url).json()
            public_data['total_games_count'] = games_response.get('response', {}).get('game_count', 0)
        except Exception as e:
            print(f"Erro ao buscar contagem de jogos da Steam: {e}")
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], leeway=10)
            viewer = User.query.get(payload['sub'])
            if viewer:
                public_data['is_followed_by_viewer'] = viewer.is_following(user)
        except:
            pass # Ignora token inválido, o visitante apenas não está logado
    # Busca a contagem de platinados do nosso banco
    public_data['perfect_games_count'] = Platinado.query.filter_by(user_id=user.id).count()
    
    return jsonify(public_data)

# --- Rotas de Atualização de Perfil (Username e Avatar) ---
@main_bp.route('/profile/username', methods=['POST'])
def update_username():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '): return jsonify({"error": "Autorização ausente"}), 401
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], leeway=10)
        user = User.query.get(payload['sub'])
        if not user: return jsonify({"error": "Usuário não encontrado"}), 404
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return jsonify({"error": "Token inválido ou expirado"}), 401
    new_username = request.get_json().get('username')
    if not new_username: return jsonify({"error": "Username não fornecido"}), 400
    existing_user = User.query.filter(User.username.ilike(new_username)).first()
    if existing_user and str(existing_user.id) != str(user.id):
        return jsonify({"error": "Este username já está em uso."}), 409
    user.username = new_username
    db.session.commit()
    return jsonify({"message": "Username atualizado com sucesso!", "username": user.username}), 200

@main_bp.route('/profile/avatar', methods=['POST'])
def upload_avatar():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '): return jsonify({"error": "Autorização ausente"}), 401
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], leeway=10)
        user = User.query.get(payload['sub'])
        if not user: return jsonify({"error": "Usuário não encontrado"}), 404
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return jsonify({"error": "Token inválido ou expirado"}), 401
    if 'avatar' not in request.files: return jsonify({"error": "Nenhum arquivo enviado"}), 400
    file = request.files['avatar']
    if file.filename == '': return jsonify({"error": "Nenhum arquivo selecionado"}), 400
    if file:
        old_picture_path = user.picture_url
        filename = secure_filename(f"user_{user.id}_{datetime.now().timestamp()}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        user.picture_url = f"/api/uploads/avatars/{filename}"
        db.session.commit()
        if old_picture_path and old_picture_path.startswith('/api/uploads/avatars/'):
            try:
                old_filename = os.path.basename(old_picture_path)
                path_to_delete = os.path.join(current_app.config['UPLOAD_FOLDER'], old_filename)
                if os.path.exists(path_to_delete): os.remove(path_to_delete)
            except Exception as e:
                print(f"ERRO ao tentar deletar o avatar antigo: {e}")
        return jsonify({"message": "Avatar atualizado com sucesso!", "picture_url": user.picture_url})
    return jsonify({"error": "Tipo de arquivo inválido."}), 400

@main_bp.route('/uploads/avatars/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(current_app.root_path, '..', current_app.config['UPLOAD_FOLDER']), filename)

# --- Rotas de Jogos e Steam ---
@main_bp.route('/steam/link')
def steam_link():
    token = request.args.get('jwt')
    if not token: return "Erro: Token JWT não fornecido.", 401
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], leeway=10)
        session['user_id_to_link'] = payload['sub']
        steam_auth_url = ("https://steamcommunity.com/openid/login?openid.ns=http://specs.openid.net/auth/2.0&openid.mode=checkid_setup&openid.return_to=http://localhost:5000/api/auth/steam/callback&openid.realm=http://localhost:5000&openid.identity=http://specs.openid.net/auth/2.0/identifier_select&openid.claimed_id=http://specs.openid.net/auth/2.0/identifier_select")
        return redirect(steam_auth_url)
    except:
        return "Erro: Token inválido ou expirado.", 401

@main_bp.route('/auth/steam/callback')
def steam_callback():
    user_id = session.get('user_id_to_link')
    if not user_id: return "Erro: Nenhuma sessão de usuário encontrada.", 400
    params = request.args.to_dict()
    params['openid.mode'] = 'check_authentication'
    response = requests.post('https://steamcommunity.com/openid/login', data=params)
    if "is_valid:true" in response.text:
        steam_id = request.args.get('openid.claimed_id').split('/')[-1]
        user_to_update = User.query.get(user_id)
        if user_to_update:
            user_to_update.steam_id = steam_id
            db.session.commit()
        else:
            return redirect("http://localhost:3000/dashboard?error=user_not_found")
        session.pop('user_id_to_link', None)
        return redirect(f"http://localhost:3000/dashboard?steam_linked=true")
    else:
        session.pop('user_id_to_link', None)
        return redirect("http://localhost:3000/dashboard?error=steam_link_failed")

@main_bp.route('/profile/games', methods=['POST'])
def add_platinado_game():
    # 1. Autenticação do usuário (padrão para rotas protegidas)
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Autorização ausente"}), 401
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], leeway=10)
        user = User.query.get(payload['sub'])
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return jsonify({"error": "Token inválido ou expirado"}), 401

    # 2. Pega os dados enviados pelo front-end
    data = request.get_json()
    platform = data.get('platform', 'steam')
    identifier = data.get('identifier')
    
    if not identifier:
        return jsonify({"error": "Nome ou ID do jogo não fornecido."}), 400

    # =================================================
    # --- BLOCO DE LÓGICA PARA A PLATAFORMA STEAM ---
    # =================================================
    if platform == 'steam':
        if not user.steam_id:
            return jsonify({"error": "Conta Steam não vinculada."}), 400

        # Tenta converter o identificador para um AppID (se for número)
        try:
            appid_to_check = int(identifier)
            game_rule = Game.query.filter_by(appid=appid_to_check, platform='steam').first()
        except ValueError:
            # Se não for número, busca pelo nome de forma flexível
            game_rule = Game.query.filter(Game.name.ilike(f"%{identifier}%"), Game.platform == 'steam').first()

        if not game_rule:
            return jsonify({"error": "Este jogo não se encontra em nosso banco de dados."}), 404
        
        appid = game_rule.appid
        official_game_name = game_rule.name

        if Platinado.query.filter_by(user_id=user.id, game_appid=appid, platform='steam').first():
            return jsonify({"message": f'"{official_game_name}" já está no seu perfil.'}), 200

        try:
            # Lógica de verificação na API da Steam (posse e conquistas)
            owned_games_url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&steamid={user.steam_id}&format=json"
            owned_games_appids = [game['appid'] for game in requests.get(owned_games_url).json().get('response', {}).get('games', [])]
            if appid not in owned_games_appids:
                return jsonify({"error": f'Você não possui "{official_game_name}" na sua conta Steam.'}), 403
            
            achievements_url = f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={STEAM_API_KEY}&steamid={user.steam_id}"
            achievements_data = requests.get(achievements_url).json().get('playerstats', {})
            if not achievements_data.get('success') or 'achievements' not in achievements_data:
                return jsonify({"error": f'Não foi possível obter conquistas para "{official_game_name}".'}), 404
            
            if all(ach.get('achieved') == 1 for ach in achievements_data['achievements']):
                user.total_xp += game_rule.xp_value
                user.total_coins += game_rule.coin_value
                db.session.add(Platinado(user_id=user.id, game_appid=appid, game_name=official_game_name, platform='steam'))
                db.session.commit()
                return jsonify({"message": f'Verificado! Você platinou "{official_game_name}" e ganhou {game_rule.xp_value} XP e {game_rule.coin_value} Fichas!'}), 200
            else:
                total = len(achievements_data['achievements'])
                achieved_count = sum(1 for ach in achievements_data['achievements'] if ach.get('achieved') == 1)
                return jsonify({"error": f'Verificação falhou. Você completou {achieved_count} de {total} conquistas.'}), 403
        except Exception as e:
            return jsonify({"error": f"Ocorreu um erro ao se comunicar com a Steam: {e}"}), 500

    # ============================================================
    # --- BLOCO DE LÓGICA PARA A PLATAFORMA RETROACHIEVEMENTS ---
    # ============================================================
    elif platform == 'retroachievements':
        if not user.retro_username:
            return jsonify({"error": "Conta do RetroAchievements não vinculada."}), 400
        
        try:
            game_id = int(identifier)
        except ValueError:
            return jsonify({"error": "Para RetroAchievements, o ID do jogo deve ser um número."}), 400

        if Platinado.query.filter_by(user_id=user.id, game_appid=game_id, platform='retroachievements').first():
            return jsonify({"message": 'Este jogo já está no seu perfil.'}), 200

        try:
            # Usamos o endpoint GetGameInfoAndUserProgress para um único jogo
            ra_url = f"https://retroachievements.org/API/API_GetGameInfoAndUserProgress.php?z={RETRO_API_USER}&y={RETRO_API_KEY}&u={user.retro_username}&g={game_id}"
            print(f"\n--- CHAMANDO A URL: {ra_url} ---\n")
            ra_data = requests.get(ra_url).json()
            print("--- RESPOSTA CRUA DA API RETROACHIEVEMENTS ---")
            # Usamos json.dumps para imprimir o JSON de forma bonita e legível
            print(json.dumps(ra_data, indent=2))
            print("------------------------------------------\n")
            # Verificação correta baseada na resposta da API
            num_achievements = int(ra_data.get('NumAchievements', 0))
            achieved_hardcore = int(ra_data.get('NumAwardedToUserHardcore', 0))
            game_name = ra_data.get('Title', f"Jogo RA ID {game_id}")
            print(f"--- DADOS INTERPRETADOS ---")
            print(f"Total de Conquistas no Jogo: {num_achievements}")
            print(f"Conquistas Hardcore Obtidas: {achieved_hardcore}")
            print("---------------------------\n")

            if num_achievements > 0 and achieved_hardcore >= num_achievements:
                game_rule = Game.query.filter_by(appid=game_id, platform='retroachievements').first()
                xp_ganho = game_rule.xp_value if game_rule else 10
                fichas_ganhas = game_rule.coin_value if game_rule else 5
                
                user.total_xp = (user.total_xp or 0) + xp_ganho
                user.total_coins = (user.total_coins or 0) + fichas_ganhas
                
                db.session.add(Platinado(user_id=user.id, game_appid=game_id, game_name=game_name, platform='retroachievements'))
                db.session.commit()
                return jsonify({"message": f'Verificado! Você masterizou "{game_name}" e ganhou {xp_ganho} XP e {fichas_ganhas} Fichas!'}), 200
            else:
                return jsonify({"error": f"Verificação falhou. Você ainda não masterizou '{game_name}' no modo Hardcore."}), 403
        except Exception as e:
            return jsonify({"error": f"Ocorreu um erro ao se comunicar com a API do RetroAchievements: {e}"}), 500

    else:
        return jsonify({"error": "Plataforma desconhecida."}), 400
    
@main_bp.route('/profile/sync-retro', methods=['POST'])
def sync_retro_achievements():
    # 1. Autenticação do usuário (sempre igual)
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"], leeway=10)
        user = User.query.get(payload['sub'])
        if not user or not user.retro_username:
            return jsonify({"error": "Usuário ou conta RA não vinculada."}), 404
    except:
        return jsonify({"error": "Token inválido"}), 401

    # 2. Chama o endpoint CORRETO da API do RA
    try:
        ra_url = f"https://retroachievements.org/API/API_GetUserCompletedGames.php?z={RETRO_API_USER}&y={RETRO_API_KEY}&u={user.retro_username}"
        response = requests.get(ra_url)
        response.raise_for_status()
        
        # A resposta é a própria lista, não um dicionário com uma chave 'response'
        mastered_games_data = response.json()
        
        # Filtramos para pegar apenas os jogos de hardcore mode
        mastered_games = [game for game in mastered_games_data if game.get('HardcoreMode') == '1']
        
    except Exception as e:
        print(f"Erro ao buscar jogos completos do RA: {e}")
        return jsonify({"error": "Não foi possível buscar os dados do RetroAchievements."}), 500

    # 3. Processa os jogos e adiciona os que forem novos
    newly_added_count = 0
    total_xp_earned = 0
    total_coins_earned = 0
    
    existing_game_ids = {p.game_appid for p in user.platinados if p.platform == 'retroachievements'}

    for game in mastered_games:
        game_id = int(game['GameID'])
        if game_id in existing_game_ids:
            continue

        game_name = game['Title']
        game_rule = Game.query.filter_by(appid=game_id, platform='retroachievements').first()
        xp_ganho = game_rule.xp_value if game_rule else 10
        fichas_ganhas = game_rule.coin_value if game_rule else 5
        
        user.total_xp += xp_ganho
        user.total_coins += fichas_ganhas
        
        new_platinado = Platinado(user_id=user.id, game_appid=game_id, game_name=game_name, platform='retroachievements')
        db.session.add(new_platinado)
        
        newly_added_count += 1
        total_xp_earned += xp_ganho
        total_coins_earned += fichas_ganhas

    if newly_added_count > 0:
        db.session.commit()
        return jsonify({
            "message": f"Sincronização concluída! {newly_added_count} novos jogos masterizados foram adicionados.",
            "xp_earned": total_xp_earned,
            "coins_earned": total_coins_earned
        })
    else:
        return jsonify({"message": "Seu perfil já está sincronizado! Nenhum jogo novo (Hardcore) encontrado."})

@main_bp.route('/profile/games/retro', methods=['GET', 'POST'])
def get_retro_achievements_games():
    username = request.json.get('username')
    api_key = request.json.get('api_key')
    
    if not username or not api_key:
        return jsonify({"error": "Username and API key are required"}), 400
    
    try:
        # First, get the user's completed games list
        games_url = f"https://retroachievements.org/API/API_GetUserCompletedGames.php?z={username}&y={api_key}&u={username}"
        games_response = requests.get(games_url, timeout=10)
        
        if games_response.status_code != 200:
            return jsonify({"error": f"Failed to fetch games list, status code: {games_response.status_code}"}), 500
        
        games_data = games_response.json()
        
        # If no games returned, return empty list
        if not games_data:
            return jsonify({"games": [], "message": "No completed games found"}), 200
        
        mastered_games = []
        
        for game in games_data:
            game_id = game.get('GameID')
            
            # Get detailed progress for each game
            progress_url = f"https://retroachievements.org/API/API_GetUserProgress.php?z={username}&y={api_key}&u={username}&i={game_id}"
            progress_response = requests.get(progress_url, timeout=10)
            
            if progress_response.status_code == 200:
                progress_data = progress_response.json()
                
                # Extract the data from the nested structure
                if str(game_id) in progress_data:
                    game_progress = progress_data[str(game_id)]
                    
                    num_possible = int(game_progress.get('NumPossibleAchievements', 0))
                    num_achieved_hardcore = int(game_progress.get('NumAchievedHardcore', 0))
                    
                    # Check if game is mastered (all achievements unlocked in hardcore mode)
                    if num_possible > 0 and num_achieved_hardcore == num_possible:
                        # Get game details
                        game_info = {
                            "id": game_id,
                            "title": game.get('Title'),
                            "console": game.get('ConsoleName'),
                            "image": f"https://retroachievements.org{game.get('ImageIcon', '')}",
                            "achievements_total": num_possible,
                            "achievements_completed": num_achieved_hardcore,
                            "completion_date": game.get('LastPlayed')
                        }
                        mastered_games.append(game_info)
        
        return jsonify({"games": mastered_games}), 200
        
    except Exception as e:
        print(f"Error fetching RetroAchievements data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@main_bp.route('/games/recent')
def get_recent_games():
    recent_platinados = Platinado.query.order_by(Platinado.achieved_at.desc()).limit(15).all()
    recent_games_data = []
    for p in recent_platinados:
        game_rule = Game.query.filter_by(appid=p.game_appid).first()
        xp = game_rule.xp_value if game_rule else 10
        coins = game_rule.coin_value if game_rule else 5
        recent_games_data.append({"appid": p.game_appid, "name": p.game_name, "achieved_at": p.achieved_at.isoformat(), "user_name": p.user.username or p.user.name, "user_picture": p.user.picture_url, "xp_earned": xp, "coin_earned": coins})
    return jsonify(recent_games_data)

@main_bp.route('/rankings/top-games')
def get_top_games():
    top_games_query = db.session.query(Platinado.game_appid, Platinado.game_name, db.func.count(Platinado.game_appid).label('total_platinados')).group_by(Platinado.game_appid, Platinado.game_name).order_by(db.desc('total_platinados')).limit(10).all()
    top_games_data = [{"appid": game.game_appid, "name": game.game_name, "count": game.total_platinados} for game in top_games_query]
    return jsonify(top_games_data)

@main_bp.route('/rankings/top-users')
def get_top_users():
    top_users_query = User.query.order_by(User.total_xp.desc()).limit(10).all()
    top_users_data = [{"id": user.id, "name": user.username or user.name, "avatar": user.picture_url, "xp": user.total_xp} for user in top_users_query]
    return jsonify(top_users_data)
