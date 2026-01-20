"""
Scrapy item definition for Pokémon move learnsets
=================================================

This module defines the Scrapy Item used to represent
how a Pokémon learns a specific move in Pokémon Let's Go.

Context:
- Educational project: Pokémon Let's Go (LGPE)
- Data source: Poképédia (scraping)
- Integration target: relational database (PostgreSQL)

This item represents a single learnset rule:
- Which Pokémon
- Which move
- How the move is learned
- At which level (if applicable)

Validation strategy:
- Lightweight validation at item level
- Structural and type checks only
- Business logic handled at ETL / DB layer

Competency block:
- E1: Data extraction, validation, and normalization
"""

import scrapy


class PokemonMoveItem(scrapy.Item):
    """
    Scrapy item representing a Pokémon move acquisition rule.

    Each instance corresponds to one row in the
    Pokémon ↔ Move association table.

    Fields:
    - pokemon_id: Internal Pokémon identifier (mandatory)
    - move_name: Move name as displayed on Poképédia (mandatory)
    - learn_method: Method used to learn the move
        (e.g. level-up, ct, move_tutor)
    - learn_level: Level at which the move is learned (optional)

    This item is validated before being processed by
    the persistence pipeline.
    """

    pokemon_id = scrapy.Field()      # int (mandatory)
    move_name = scrapy.Field()       # str (mandatory)
    learn_method = scrapy.Field()    # str: level_up | ct | move_tutor
    learn_level = scrapy.Field()     # int | None

    def validate(self):
        """
        Validate and normalize item fields.

        This method acts as a guard clause before
        database persistence.

        Validation rules:
        - pokemon_id must be present
        - move_name must be present
        - learn_method must be present
        - learn_level, if provided, must be convertible to int

        Raises:
            ValueError: If any required field is missing
                        or if learn_level is invalid.

        Returns:
            PokemonMoveItem: The validated (and normalized) item.
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
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"learn_level invalide: {learn_level}"
                ) from exc

        return self
