import scrapy


class PokemonMoveItem(scrapy.Item):
    pokemon_id = scrapy.Field()
    pokemon_fr = scrapy.Field()
    pokemon_pokepedia = scrapy.Field()

    move_name = scrapy.Field()
    learn_method = scrapy.Field()
    learn_level = scrapy.Field()