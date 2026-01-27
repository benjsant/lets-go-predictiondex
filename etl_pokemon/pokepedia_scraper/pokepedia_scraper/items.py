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
        pokemon_id (int): Internal Pokémon identifier (mandatory).
        move_name (str): Move name as displayed on Poképédia (mandatory).
        learn_method (str): Method used to learn the move
            (e.g. "level_up", "ct", "move_tutor").
        learn_level (int | None): Level at which the move is learned.
    """

    pokemon_id = scrapy.Field()
    move_name = scrapy.Field()
    learn_method = scrapy.Field()
    learn_level = scrapy.Field()

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
            raise ValueError("Missing required field: pokemon_id")

        if not self.get("move_name"):
            raise ValueError("Missing required field: move_name")

        if not self.get("learn_method"):
            raise ValueError("Missing required field: learn_method")

        learn_level = self.get("learn_level")
        if learn_level is not None:
            try:
                self["learn_level"] = int(learn_level)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid learn_level value: {learn_level}"
                ) from exc

        return self
