import scrapy


class PokemonMoveItem(scrapy.Item):
    """
    Capacité apprise par un Pokémon dans Pokémon Let's Go
    → item strictement validé avant insertion DB
    """

    pokemon_id = scrapy.Field()      # int (obligatoire)
    move_name = scrapy.Field()       # str (obligatoire)
    learn_method = scrapy.Field()    # level-up | ct | move_tutor
    learn_level = scrapy.Field()     # int | None

    def validate(self):
        """
        Guards simples côté item
        """
        if not self.get("pokemon_id"):
            raise ValueError("pokemon_id manquant")

        if not self.get("move_name"):
            raise ValueError("move_name manquant")

        if not self.get("learn_method"):
            raise ValueError("learn_method manquant")

        learn_level = self.get("learn_level")
        if learn_level is not None:
            try:
                self["learn_level"] = int(learn_level)
            except (TypeError, ValueError):
                raise ValueError(f"learn_level invalide: {learn_level}")

        return self
