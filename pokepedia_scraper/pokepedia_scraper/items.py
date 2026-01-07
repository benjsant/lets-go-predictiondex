import scrapy


class PokemonMoveItem(scrapy.Item):
    """
    Représente une capacité apprise par un Pokémon dans Pokémon Let's Go
    → utilisé uniquement pour l'insertion en base de données
    """
    pokemon_id = scrapy.Field()
    move_name = scrapy.Field()
    learn_method = scrapy.Field()   # level-up | ct | move_tutor
    learn_level = scrapy.Field()    # int | None
