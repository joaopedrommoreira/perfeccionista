# backend/seed.py
from app import create_app
from app.models import db, Game, ShopItem, ItemKey, User


# Lista de jogos para adicionar ao nosso "livro de regras"
# AppID pode ser encontrado na URL da loja Steam (ex: store.steampowered.com/app/1174180/...)
GAMES_TO_SEED = [
    {'appid': 218620, 'name': 'Payday 2', 'difficulty': 'Muito Difícil', 'xp_value': 920, 'coin_value': 230},
    {'appid': 1174180, 'name': 'Red Dead Redemption 2', 'difficulty': 'Difícil', 'xp_value': 780, 'coin_value': 195},
    {'appid': 235460, 'name': 'Metal Gear Rising: Revengeance', 'difficulty': 'Muito Difícil', 'xp_value': 695, 'coin_value': 174},
    {'appid': 367520, 'name': 'Hollow Knight', 'difficulty': 'Muito Difícil', 'xp_value': 680, 'coin_value': 170},
    {'appid': 601150, 'name': 'Devil May Cry 5', 'difficulty': 'Extremamente Difícil', 'xp_value': 765, 'coin_value': 191},
    {'appid': 271590, 'name': 'Grand Theft Auto V', 'difficulty': 'Moderado', 'xp_value': 710, 'coin_value': 170},
    {'appid': 2835570, 'name': 'Buckshot Roulette', 'difficulty': 'Fácil', 'xp_value': 230, 'coin_value': 57},
    {'appid': 2527500, 'name': 'Miside', 'difficulty': 'Muito Fácil', 'xp_value': 250, 'coin_value': 60},
    {'appid': 220240, 'name': 'Far Cry 3', 'difficulty': 'Moderado', 'xp_value': 460, 'coin_value': 115},
    {'appid': 298110, 'name': 'Far Cry 4', 'difficulty': 'Moderado', 'xp_value': 505, 'coin_value': 126},
    {'appid': 552520, 'name': 'Far Cry 5', 'difficulty': 'Moderadamente Difícil', 'xp_value': 585, 'coin_value': 146},
    {'appid': 939960, 'name': 'Far Cry New Dawn', 'difficulty': 'Fácil', 'xp_value': 400, 'coin_value': 100},
    {'appid': 2369390, 'name': 'Far Cry 6', 'difficulty': 'Moderado', 'xp_value': 545, 'coin_value': 136},
    {'appid': 883710, 'name': 'Resident Evil 2 Remake', 'difficulty': 'Muito Difícil', 'xp_value': 625, 'coin_value': 156},
    {'appid': 952060, 'name': 'Resident Evil 3 Remake', 'difficulty': 'Difícil', 'xp_value': 540, 'coin_value': 135},
    {'appid': 2050650, 'name': 'Resident Evil 4 Remake', 'difficulty': 'Muito Difícil', 'xp_value': 635, 'coin_value': 158},
    {'appid': 21690, 'name': 'Resident Evil 5', 'difficulty': 'Difícil', 'xp_value': 555, 'coin_value': 138},
    {'appid': 221040, 'name': 'Resident Evil 6', 'difficulty': 'Moderado', 'xp_value': 500, 'coin_value': 125},
    {'appid': 418370, 'name': 'Resident Evil 7', 'difficulty': 'Difícil', 'xp_value': 575, 'coin_value': 143},
    {'appid': 1196590, 'name': 'Resident Evil Village', 'difficulty': 'Difícil', 'xp_value': 545, 'coin_value': 136},
    {'appid': 1091500, 'name': 'Cyberpunk 2077', 'difficulty': 'Moderado', 'xp_value': 525, 'coin_value': 131},
    {'appid': 292030, 'name': 'The Witcher 3: Wild Hunt', 'difficulty': 'Muito Difícil', 'xp_value': 700, 'coin_value': 175},
    {'appid': 20920, 'name': 'The Witcher 2', 'difficulty': 'Difícil', 'xp_value': 520, 'coin_value': 130},
    {'appid': 227300, 'name': 'Euro Truck Simulator 2', 'difficulty': 'Fácil', 'xp_value': 470, 'coin_value': 117},
    {'appid': 270880, 'name': 'American Truck Simulator', 'difficulty': 'Fácil', 'xp_value': 455, 'coin_value': 113},
    {'appid': 1293830, 'name': 'Forza Horizon 4', 'difficulty': 'Difícil', 'xp_value': 685, 'coin_value': 171},
    {'appid': 1551360, 'name': 'Forza Horizon 5', 'difficulty': 'Difícil', 'xp_value': 645, 'coin_value': 161},
    {'appid': 2440510, 'name': 'Forza Motorsport', 'difficulty': 'Moderado', 'xp_value': 515, 'coin_value': 128},
    {'appid': 2668510, 'name': 'Red Dead Redemption 1', 'difficulty': 'Muito Difícil', 'xp_value': 730, 'coin_value': 182},
    {'appid': 12210, 'name': 'Grand Theft Auto IV', 'difficulty': 'Extremamente Difícil', 'xp_value': 660, 'coin_value': 165},
    {'appid': 1547000, 'name': 'GTA San Andreas Definitive Edition', 'difficulty': 'Moderado', 'xp_value': 530, 'coin_value': 132},
    {'appid': 1546990, 'name': 'GTA Vice City Definitive Edition', 'difficulty': 'Moderado', 'xp_value': 520, 'coin_value': 130},
    {'appid': 1546970, 'name': 'GTA 3 Definitive Edition', 'difficulty': 'Moderado', 'xp_value': 535, 'coin_value': 133},
    {'appid': 1245620, 'name': 'Elden Ring', 'difficulty': 'Difícil', 'xp_value': 665, 'coin_value': 166},
    {'appid': 570940, 'name': 'Dark Souls', 'difficulty': 'Extremamente Difícil', 'xp_value': 735, 'coin_value': 183},
    {'appid': 335300, 'name': 'Dark Souls 2', 'difficulty': 'Extremamente Difícil', 'xp_value': 725, 'coin_value': 181},
    {'appid': 374320, 'name': 'Dark Souls 3', 'difficulty': 'Extremamente Difícil', 'xp_value': 740, 'coin_value': 185},
    {'appid': 1627720, 'name': 'Lies of P', 'difficulty': 'Difícil', 'xp_value': 695, 'coin_value': 173},
    {'appid': 814380, 'name': 'Sekiro: Shadows Die Twice', 'difficulty': 'Extremamente Difícil', 'xp_value': 705, 'coin_value': 176},
    {'appid': 268910, 'name': 'Cuphead', 'difficulty': 'Difícil', 'xp_value': 670, 'coin_value': 167},
    {'appid': 1145360, 'name': 'Hades', 'difficulty': 'Difícil', 'xp_value': 635, 'coin_value': 158},
    {'appid': 1145350, 'name': 'Hades 2', 'difficulty': 'Difícil', 'xp_value': 635, 'coin_value': 158},
    {'appid': 588650, 'name': 'Dead Cells', 'difficulty': 'Difícil', 'xp_value': 700, 'coin_value': 175},

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
    #{'appid': 367520, 'name': 'Chave Steam - Hollow Knight', 'description': 'Uma chave de ativação na Steam para o jogo Hollow Knight.', 'price_coins': 200},
    #{'appid': 413150, 'name': 'Chave Steam - Stardew Valley', 'description': 'Uma chave de ativação na Steam para o jogo Stardew Valley.', 'price_coins': 150}
]

SHOP_ITEMS_TO_SEED = [
    {
        'name': 'Wallpaper Red Dead Redemption 2', 
        'description': 'Um Background épico da gangue Van der Linde para seu perfil público.', 
        'price_coins': 500, 
        'item_type': 'BANNER', # Define que este item é um banner equipável
        'appid': 1174180,
        'value': 'https://images7.alphacoders.com/749/thumb-1920-749807.png' # O valor é a própria URL do banner
    },
    {
        'name': 'Wallpaper The Witcher 3: Wild Hunt', 
        'description': 'Um Background épico  do mundo de The Witcher 3 para seu perfil público.', 
        'price_coins': 500, 
        'item_type': 'BANNER', # Define que este item é um banner equipável
        'appid': 292030,
        'value': 'https://i.postimg.cc/VNs56pLk/tw3.png' # O valor é a própria URL do banner
    },
    {
        'name': 'Wallpaper Devil May Cry 5', 
        'description': 'Um Background épico de Dante e Vergil para seu perfil público.', 
        'price_coins': 500, 
        'item_type': 'BANNER', # Define que este item é um banner equipável
        'appid': 601150,
        'value': 'https://picfiles.alphacoders.com/320/thumb-1920-320697.png' # O valor é a própria URL do banner
    },
    {
        'name': 'Wallpaper Resident Evil 4 Remake', 
        'description': 'Um Background épico de Leon S. Kennedy enfrentando os Ganados para seu perfil público.', 
        'price_coins': 500, 
        'item_type': 'BANNER', # Define que este item é um banner equipável
        'appid': 2050650,
        'value': 'https://images7.alphacoders.com/130/thumb-1920-1306926.jpeg' # O valor é a própria URL do banner
    }
]


# Chaves de exemplo (em um sistema real, elas viriam de um arquivo ou banco de dados seguro)
KEYS_TO_SEED = {
    #'Chave Steam - Hollow Knight': ['AAAAA-BBBBB-CCCC1', 'AAAAA-BBBBB-CCCC2', 'AAAAA-BBBBB-CCCC3'],
    #'Chave Steam - Stardew Valley': ['DDDDD-EEEEE-FFFF1', 'DDDDD-EEEEE-FFFF2']
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