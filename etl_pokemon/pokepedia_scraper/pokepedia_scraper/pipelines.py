"""
Scrapy item pipeline for Pokémon ↔ Move persistence
===================================================

This module defines the Scrapy pipeline responsible for persisting
Pokémon move learnsets scraped from Poképédia into the relational
database.

Context:
- Educational project: Pokémon Let's Go (LGPE)
- Part of the global ETL pipeline
- Integrates scraped data with previously initialized reference tables

Responsibilities:
- Validate scraped items
- Normalize move naming inconsistencies
- Resolve foreign keys using cached reference data
- Perform idempotent upserts into the PokemonMove association table

Design choices:
- SQLAlchemy Core INSERT ... ON CONFLICT for PostgreSQL
- In-memory caching of reference tables for performance
- Transaction managed at spider lifecycle level

Competency block:
- E1: Data integration, relational modeling, ETL robustness
"""

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from core.db.session import engine
from core.models import LearnMethod, Move, PokemonMove


class PokemonMovePipeline:
    """
    Scrapy pipeline for persisting Pokémon move learnsets.

    This pipeline is executed for each scraped item representing
    a Pokémon move acquisition rule (learnset entry).

    Lifecycle:
    - open_spider: initialize database session and caches
    - process_item: validate, normalize and upsert data
    - close_spider: commit or rollback and close the session

    The pipeline ensures:
    - Referential integrity
    - Idempotent inserts
    - Minimal database load during scraping
    """

    def open_spider(self, spider):
        """
        Initialize database session and reference caches.

        This method is called once when the spider starts.
        It prepares:
        - A single SQLAlchemy session for the spider lifecycle
        - In-memory caches for reference tables (Move, LearnMethod)

        Caching strategy:
        - Reduces repetitive SELECT queries
        - Ensures consistency between scraped data and DB state

        Args:
            spider (Spider): Active Scrapy spider instance.
        """
        self.session = Session(engine)

        # --- Cache reference learn methods ---
        self.learn_method_cache = {
            lm.name: lm.id
            for lm in self.session.execute(
                select(LearnMethod)
            ).scalars()
        }

        # --- Cache reference moves (case-insensitive) ---
        self.move_cache = {
            m.name.lower(): m.id
            for m in self.session.execute(
                select(Move)
            ).scalars()
        }

    def close_spider(self, spider):
        """
        Finalize database transaction and close the session.

        This method is called once when the spider finishes.
        It ensures:
        - All pending changes are committed
        - Errors during commit are handled gracefully
        - The database session is always closed

        Args:
            spider (Spider): Active Scrapy spider instance.
        """
        try:
            self.session.commit()
        except Exception as exc:
            spider.logger.warning(
                f"[CLOSE SPIDER COMMIT ERROR] {exc}"
            )
            self.session.rollback()
        finally:
            self.session.close()

    def process_item(self, item, spider):
        """
        Process a single scraped Pokémon move item.

        Steps:
        1. Validate item structure and required fields
        2. Normalize move naming for DB matching
        3. Resolve foreign keys using cached references
        4. Perform PostgreSQL upsert into PokemonMove table

        Conflict strategy:
        - Unique constraint: (pokemon_id, move_id, learn_method_id)
        - On conflict, update learn_level if necessary

        Args:
            item (Item): Scraped item representing a move learn rule.
            spider (Spider): Active Scrapy spider instance.

        Returns:
            Item: The processed (or skipped) item.
        """
        # --- Item validation guard ---
        try:
            item.validate()
        except Exception as exc:
            spider.logger.warning(
                f"[ITEM INVALID] {exc} -> {dict(item)}"
            )
            return item

        # --- Normalize move name for matching ---
        move_name = (
            item["move_name"]
            .strip()
            .lower()
            .replace("’", "'")
        )

        move_id = self.move_cache.get(move_name)
        if not move_id:
            spider.logger.info(
                f"[MOVE NOT FOUND] {item['move_name']}"
            )
            return item

        learn_method_id = self.learn_method_cache.get(
            item["learn_method"]
        )
        if not learn_method_id:
            spider.logger.info(
                f"[LEARN METHOD NOT FOUND] {item['learn_method']}"
            )
            return item

        # --- PostgreSQL upsert (idempotent) ---
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
        except Exception as exc:
            spider.logger.warning(
                f"[UPSERT ERROR] {dict(item)} -> {exc}"
            )
            self.session.rollback()

        return item
