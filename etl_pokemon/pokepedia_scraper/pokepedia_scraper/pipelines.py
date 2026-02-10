"""
Scrapy item pipeline for Pokémon ↔ Move persistence
===================================================

This module defines the Scrapy pipeline responsible for persisting
Pokémon move learnsets scraped from Poképédia into the relational
database.

Context:
- Educational project: Pokémon Let's Go (LGPE)
- Part of the global ETL pipeline
- Integrates scraped data with reference tables

Responsibilities:
- Validate scraped items
- Normalize move naming inconsistencies
- Resolve foreign keys using cached reference data
- Perform idempotent upserts into the PokemonMove association table
"""

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from core.db.session import engine
from core.models import LearnMethod, Move, PokemonMove


class PokemonMovePipeline:
    """
    Scrapy pipeline for persisting Pokémon move learnsets.

    This pipeline processes each scraped item representing
    a Pokémon move acquisition rule and ensures reliable,
    idempotent persistence in the database.
    """

    def open_spider(self, spider) -> None:
        """
        Initialize database session and reference caches.

        Called once when the spider starts.
        """
        self.session: Session = Session(engine)

        self.learn_method_cache = {
            learn_method.name: learn_method.id
            for learn_method in self.session.execute(
                select(LearnMethod)
            ).scalars()
        }

        self.move_cache = {
            move.name.lower(): move.id
            for move in self.session.execute(
                select(Move)
            ).scalars()
        }

    def close_spider(self, spider) -> None:
        """
        Commit pending changes and close the database session.

        Ensures rollback on failure and safe session cleanup.
        """
        try:
            self.session.commit()
        except Exception as exc:  # pylint: disable=broad-except
            spider.logger.warning(
                "[CLOSE SPIDER COMMIT ERROR] %s", exc
            )
            self.session.rollback()
        finally:
            self.session.close()

    def process_item(self, item, spider):
        """
        Process a single scraped Pokémon move item.

        Steps:
        - Validate item structure
        - Normalize move name
        - Resolve foreign keys
        - Perform PostgreSQL upsert

        Returns:
            Item: The processed item (or skipped item).
        """
        try:
            item.validate()
        except Exception as exc:  # pylint: disable=broad-except
            spider.logger.warning(
                "[ITEM INVALID] %s -> %s", exc, dict(item)
            )
            return item

        move_name = (
            item["move_name"]
            .strip()
            .lower()
            .replace("’", "'")
        )

        move_id = self.move_cache.get(move_name)
        if not move_id:
            spider.logger.info(
                "[MOVE NOT FOUND] %s", item["move_name"]
            )
            return item

        learn_method_id = self.learn_method_cache.get(
            item["learn_method"]
        )
        if not learn_method_id:
            spider.logger.info(
                "[LEARN METHOD NOT FOUND] %s",
                item["learn_method"],
            )
            return item

        stmt = (
            insert(PokemonMove)
            .values(
                pokemon_id=item["pokemon_id"],
                move_id=move_id,
                learn_method_id=learn_method_id,
                learn_level=item.get("learn_level"),
            )
            .on_conflict_do_update(
                index_elements=[
                    "pokemon_id",
                    "move_id",
                    "learn_method_id",
                ],
                set_={
                    "learn_level": item.get("learn_level"),
                },
            )
        )

        try:
            self.session.execute(stmt)
            self.session.flush()
        except Exception as exc:  # pylint: disable=broad-except
            spider.logger.warning(
                "[UPSERT ERROR] %s -> %s", dict(item), exc
            )
            self.session.rollback()

        return item
