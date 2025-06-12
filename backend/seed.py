# backend/seed.py
from app import create_app
from app.models import db, Game, ShopItem, ItemKey, User


# Lista de jogos para adicionar ao nosso "livro de regras"
# AppID pode ser encontrado na URL da loja Steam (ex: store.steampowered.com/app/1174180/...)
GAMES_TO_SEED = [
    {'appid': 1174180, 'name': 'Red Dead Redemption 2', 'difficulty': 'Difícil', 'xp_value': 341, 'coin_value': 85},
    {'appid': 367520, 'name': 'Hollow Knight', 'difficulty': 'Difícil', 'xp_value': 418, 'coin_value': 104},
    {'appid': 601150, 'name': 'Devil May Cry 5', 'difficulty': 'Difícil', 'xp_value': 243, 'coin_value': 61},
    {'appid': 1245620, 'name': 'Elden Ring', 'difficulty': 'Média', 'xp_value': 180, 'coin_value': 45},
    {'appid': 220240, 'name': 'Far Cry 3', 'difficulty': 'Fácil', 'xp_value': 68, 'coin_value': 17},
    {'appid': 298110, 'name': 'Far Cry 4', 'difficulty': 'Média', 'xp_value': 158, 'coin_value': 40},
    {'appid': 552520, 'name': 'Far Cry 5', 'difficulty': 'Média', 'xp_value': 201, 'coin_value': 50},
    {'appid': 2369390, 'name': 'Far Cry 6', 'difficulty': 'Média', 'xp_value': 153, 'coin_value': 38},
    {'appid': 1091500, 'name': 'Cyberpunk 2077', 'difficulty': 'Média', 'xp_value': 121, 'coin_value': 30},
    {'appid': 271590, 'name': 'Grand Theft Auto V', 'difficulty': 'Difícil', 'xp_value': 499, 'coin_value': 125},
    {'appid': 12210, 'name': 'Grand Theft Auto IV', 'difficulty': 'Difícil', 'xp_value': 426, 'coin_value': 106},
    {'appid': 1693980, 'name': 'GTA San Andreas: Definitive Edition', 'difficulty': 'Média', 'xp_value': 90, 'coin_value': 22},
    {'appid': 1685450, 'name': 'GTA III: The Definitive Edition', 'difficulty': 'Média', 'xp_value': 121, 'coin_value': 30},
    {'appid': 1642000, 'name': 'GTA Vice City: The Definitive Edition', 'difficulty': 'Média', 'xp_value': 117, 'coin_value': 29},
    {'appid': 292030, 'name': 'The Witcher 3: Wild Hunt', 'difficulty': 'Média', 'xp_value': 426, 'coin_value': 98},
    {'appid': 1145360, 'name': 'Hades', 'difficulty': 'Média', 'xp_value': 233, 'coin_value': 53},
    {'appid': 1145340, 'name': 'Hades II', 'difficulty': 'Média', 'xp_value': 103, 'coin_value': 26},
    {'appid': 883710, 'name': 'Resident Evil 2 Remake', 'difficulty': 'Difícil', 'xp_value': 188, 'coin_value': 47},
    {'appid': 952060, 'name': 'Resident Evil 3 Remake', 'difficulty': 'Média', 'xp_value': 88, 'coin_value': 22},
    {'appid': 2050650, 'name': 'Resident Evil 4 Remake', 'difficulty': 'Difícil', 'xp_value': 165, 'coin_value': 41},
    {'appid': 21690, 'name': 'Resident Evil 5', 'difficulty': 'Média', 'xp_value': 191, 'coin_value': 48},
    {'appid': 221040, 'name': 'Resident Evil 6', 'difficulty': 'Difícil', 'xp_value': 254, 'coin_value': 114},
    {'appid': 418370, 'name': 'Resident Evil 7: Biohazard', 'difficulty': 'Média', 'xp_value': 162, 'coin_value': 41},
    {'appid': 1196590, 'name': 'Resident Evil Village', 'difficulty': 'Média', 'xp_value': 140, 'coin_value': 35},
    {'appid': 268910, 'name': 'Cuphead', 'difficulty': 'Difícil', 'xp_value': 166, 'coin_value': 41},
    {'appid': 2835570, 'name': 'Buckshot Roulette', 'difficulty': 'Média', 'xp_value': 42, 'coin_value': 5},
    {'appid': 606150, 'name': 'Moonlighter', 'difficulty': 'Média', 'xp_value': 144, 'coin_value': 36},
]

# Lista de jogos para a blacklist
BLACKLIST_TO_SEED = [
    {'appid': 602520, 'reason': 'Farm de conquistas - NEKOPARA Vol. 3'},
    {'appid': 420110, 'reason': 'Farm de conquistas - NEKOPARA Vol. 2'},
    {'appid': 333600, 'reason': 'Farm de conquistas - NEKOPARA Vol. 1'},
    {'appid': 385800, 'reason': 'Farm de conquistas - NEKOPARA Vol. 0'},
    {'appid': 1593310, 'reason': 'Farm de conquistas - NEKOPARA - Catboys Paradise'},
    {'appid': 1406990, 'reason': 'Farm de conquistas - NEKOPARA Vol. 4'},
    {'appid': 1101450, 'reason': 'Farm de conquistas - Miss Neko'},
    {'appid': 899970,  'reason': 'Farm de conquistas - NEKOPARA Extra'},
    {'appid': 570840,  'reason': 'Farm de conquistas - Nekojishi'},
    {'appid': 2022180, 'reason': 'Farm de conquistas - Miss Neko 3'},
    {'appid': 1299120, 'reason': 'Farm de conquistas - Mosaique Neko Waifus 2'},
    {'appid': 1203420, 'reason': 'Farm de conquistas - Miss Neko 2'},
    {'appid': 1192640, 'reason': 'Farm de conquistas - Mosaique Neko Waifus'},
    {'appid': 469990,  'reason': 'Farm de conquistas - NEKOPALIVE'},
    {'appid': 2695270, 'reason': 'Farm de conquistas - Miss Neko: Pirates'},
    {'appid': 2165610, 'reason': 'Farm de conquistas - Mosaique Neko Waifus 5'},
    {'appid': 1504020, 'reason': 'Farm de conquistas - Mosaique Neko Waifus 4'},
    {'appid': 1385730, 'reason': 'Farm de conquistas - Mosaique Neko Waifus 3'},
    {'appid': 1212620, 'reason': 'Farm de conquistas - Pretty Neko'},
]

REDEEMABLE_ITEMS_TO_SEED = [
    {'appid': 367520, 'name': 'Chave Steam - Hollow Knight', 'description': 'Uma chave de ativação na Steam para o jogo Hollow Knight.', 'price_coins': 200},
    {'appid': 413150, 'name': 'Chave Steam - Stardew Valley', 'description': 'Uma chave de ativação na Steam para o jogo Stardew Valley.', 'price_coins': 150}
]

SHOP_ITEMS_TO_SEED = [
    {
        'name': 'Chave Steam - Hollow Knight', 
        'description': 'Uma chave de ativação na Steam para o aclamado metroidvania Hollow Knight.', 
        'price_coins': 200, 
        'item_type': 'GAME_KEY', # Define que este item é uma chave resgatável
        'appid': 367520,
        'value': None # Não tem um valor direto, pois as chaves estão em outra tabela
    },
    {
        'name': 'Chave Steam - Stardew Valley', 
        'description': 'Uma chave de ativação na Steam para o relaxante simulador de fazenda Stardew Valley.', 
        'price_coins': 150, 
        'item_type': 'GAME_KEY',
        'appid': 413150,
        'value': None
    },
    {
        'name': 'Banner Red Dead Redemption 2', 
        'description': 'Um banner épico da gangue Van der Linde para seu perfil público.', 
        'price_coins': 500, 
        'item_type': 'BANNER', # Define que este item é um banner equipável
        'appid': 1174180,
        'value': 'https://images3.alphacoders.com/948/948553.jpg' # O valor é a própria URL do banner
    },
    {
        'name': 'Banner The Witcher 3: Wild Hunt', 
        'description': 'Um banner épico da gangue Van der Linde para seu perfil público.', 
        'price_coins': 500, 
        'item_type': 'BANNER', # Define que este item é um banner equipável
        'appid': 292030,
        'value': 'https://images6.alphacoders.com/123/thumb-1920-1234456.jpg' # O valor é a própria URL do banner
    }
]


# Chaves de exemplo (em um sistema real, elas viriam de um arquivo ou banco de dados seguro)
KEYS_TO_SEED = {
    'Chave Steam - Hollow Knight': ['AAAAA-BBBBB-CCCC1', 'AAAAA-BBBBB-CCCC2', 'AAAAA-BBBBB-CCCC3'],
    'Chave Steam - Stardew Valley': ['DDDDD-EEEEE-FFFF1', 'DDDDD-EEEEE-FFFF2']
}

def seed_database():
    """Função principal para popular todas as tabelas com dados iniciais."""
    app = create_app()
    with app.app_context():
        # Popula a tabela Game (regras de XP)
        for game_data in GAMES_TO_SEED:
            game = Game.query.filter_by(appid=game_data['appid']).first()
            if not game:
                db.session.add(Game(**game_data))
        db.session.commit()
        print("Tabela 'Game' populada com sucesso.")

        # Popula a tabela ShopItem e suas chaves associadas
        for item_data in SHOP_ITEMS_TO_SEED:
            item = ShopItem.query.filter_by(name=item_data['name']).first()
            if not item:
                item = ShopItem(**item_data)
                db.session.add(item)
                print(f"Item da loja adicionado: {item_data['name']}")
                db.session.commit() # Salva para obter o ID do item

                # Se o item for uma chave de jogo, adiciona as chaves da nossa lista
                if item.item_type == 'GAME_KEY':
                    for key_val in KEYS_TO_SEED.get(item.name, []):
                        key = ItemKey.query.filter_by(key_value=key_val).first()
                        if not key:
                            new_key = ItemKey(item_id=item.id, key_value=key_val)
                            db.session.add(new_key)
                            print(f"  > Chave adicionada: {key_val}")
        
        db.session.commit()
        print("Tabela 'ShopItem' e 'ItemKey' populadas com sucesso!")


if __name__ == '__main__':
    seed_database()