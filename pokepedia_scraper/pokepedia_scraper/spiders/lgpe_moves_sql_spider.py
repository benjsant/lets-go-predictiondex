"""
Scrapy spider – Poképédia (Pokémon Let's Go Pikachu / Évoli)
===========================================================

This spider extracts Pokémon move learnsets specific to
Pokémon Let's Go Pikachu & Let's Go Évoli (LGPE) from Poképédia.

Key characteristics:
- Database-driven spider (SQLAlchemy)
- Model-aware (Pokémon forms, starters, megas)
- Responsible scraping (robots.txt, throttling, cache)
- Incremental & idempotent persistence

Scraped learn methods:
- Level-up
- CT (Technical Machines)
- Move Tutor (starters only)

Data flow:
Database (Pokémon list)
    → Poképédia HTML pages
        → Scrapy Items (PokemonMoveItem)
            → SQLAlchemy pipeline (upsert)

Competency block:
- E1: Data extraction, normalization, relational persistence
"""

import re
import scrapy
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import engine
from app.models import Pokemon
from pokepedia_scraper.items import PokemonMoveItem


class LetsGoPokemonMovesSQLSpider(scrapy.Spider):
    """
    Scrapy spider for extracting LGPE Pokémon move learnsets.

    This spider:
    - Reads Pokémon forms directly from the database
    - Builds Poképédia URLs dynamically
    - Parses multiple learn methods from a single page
    - Emits validated Scrapy items for database insertion

    Design principles:
    - Model-driven scraping (no hardcoded Pokémon list)
    - Separation of concerns (parse vs persist)
    - Minimal logic inside Scrapy callbacks
    """

    name = "letsgo_moves_sql"
    allowed_domains = ["pokepedia.fr"]

    # ==================================================
    # ▶️ ENTRY POINT: DATABASE-DRIVEN REQUESTS
    # ==================================================
    def start_requests(self):
        """
        Generate initial requests based on Pokémon stored in database.

        Rules:
        - Mega Pokémon are excluded (they inherit moves later)
        - Pokémon without Poképédia name are skipped
        - Starter Pokémon are re-scraped even if URL was already visited

        Yields:
            scrapy.Request: Request to the Poképédia LGPE page.
        """
        with Session(engine) as session:
            pokemons = session.execute(
                select(Pokemon).where(Pokemon.is_mega.is_(False))
            ).scalars()

            for pokemon in pokemons:
                if not pokemon.name_pokepedia:
                    continue

                url = (
                    f"https://www.pokepedia.fr/"
                    f"{pokemon.name_pokepedia}/Génération_7"
                )

                # Force re-scraping only for partner starters
                use_dont_filter = pokemon.is_starter

                self.logger.info(
                    "[START] id=%s name=%s form=%s is_starter=%s",
                    pokemon.id,
                    pokemon.name_pokepedia,
                    pokemon.form_name,
                    pokemon.is_starter,
                )

                yield scrapy.Request(
                    url=url,
                    callback=self.parse_all,
                    dont_filter=use_dont_filter,
                    meta={
                        "pokemon_id": pokemon.id,
                        "pokemon_name": pokemon.name_pokepedia,
                        "is_starter": pokemon.is_starter,
                    },
                )

    # ==================================================
    # 🧠 MASTER PARSER
    # ==================================================
    def parse_all(self, response):
        """
        Master parser coordinating all learning methods.

        Delegates parsing to specialized sub-parsers:
        - Level-up
        - CT
        - Move Tutor (starters only)

        Args:
            response (scrapy.http.Response): Poképédia page response.

        Yields:
            PokemonMoveItem: Parsed and normalized move learnset items.
        """
        pokemon_id = response.meta["pokemon_id"]
        is_starter = response.meta["is_starter"]

        self.logger.info(
            "[PARSE_ALL] id=%s starter=%s",
            pokemon_id,
            is_starter,
        )

        yield from self.parse_level_up(response)
        yield from self.parse_ct(response)

        # Move tutor is exclusive to partner starters in LGPE
        if is_starter:
            yield from self.parse_move_tutor(response)

    # ==================================================
    # 📈 LEVEL-UP (LGPE)
    # ==================================================
    def parse_level_up(self, response):
        """
        Parse level-up moves specific to LGPE.

        Strategy:
        - Locate the 'Par montée en niveau' section
        - Identify the LGPE-specific column
        - Extract learning levels (including special cases)

        Args:
            response (scrapy.http.Response): Poképédia page response.

        Yields:
            PokemonMoveItem: Level-up move items.
        """
        pokemon_id = response.meta["pokemon_id"]

        level_header = response.xpath('//*[@id="Par_montée_en_niveau"]')
        if not level_header:
            return

        table = level_header.xpath("following::table[1]")
        if not table:
            return

        lgpe_col_index = self.find_lgpe_column_index(table)
        if lgpe_col_index is None:
            return

        for row in table.xpath(".//tbody/tr"):
            move_name = row.xpath(
                "./td[1]//a/text() | ./td[1]/text()"
            ).get()
            lgpe_cell = row.xpath(f"./td[{lgpe_col_index}]")

            if not move_name or not lgpe_cell:
                continue

            for level in self.parse_lgpe_levels(lgpe_cell):
                yield PokemonMoveItem(
                    pokemon_id=pokemon_id,
                    move_name=move_name.strip(),
                    learn_method="level_up",
                    learn_level=level,
                )

    @staticmethod
    def find_lgpe_column_index(table):
        """
        Identify the column index corresponding to LGPE data.

        Args:
            table (Selector): HTML table selector.

        Returns:
            int | None: Column index if found, else None.
        """
        headers = table.xpath(".//thead/tr[2]/th")
        for idx, th in enumerate(headers, start=1):
            title = th.xpath(".//a/@title").get()
            if (
                title
                and "Let's Go, Pikachu et Let's Go, Évoli" in title
            ):
                return idx
        return None

    @staticmethod
    def parse_lgpe_levels(cell):
        """
        Parse learning levels from LGPE table cells.

        Special cases:
        - "Départ" → level 0
        - "Évolution" → level -1
        - "N.xx" → integer level

        Args:
            cell (Selector): Table cell selector.

        Returns:
            list[int]: Parsed learning levels.
        """
        levels = []
        for raw in cell.xpath(".//text()").getall():
            raw = raw.strip()
            if not raw or raw == "—":
                continue

            if raw == "Départ":
                levels.append(0)
            elif raw == "Évolution":
                levels.append(-1)
            else:
                match = re.search(r"N\.(\d+)", raw)
                if match:
                    levels.append(int(match.group(1)))

        return levels

    # ==================================================
    # 💿 CT (LGPE)
    # ==================================================
    def parse_ct(self, response):
        """
        Parse CT (Technical Machine) moves for LGPE.

        Args:
            response (scrapy.http.Response): Poképédia page response.

        Yields:
            PokemonMoveItem: CT move items.
        """
        pokemon_id = response.meta["pokemon_id"]

        ct_header = response.xpath('//*[@id="Par_CT"]')
        if not ct_header:
            return

        lgpe_h4 = ct_header.xpath(
            """following::h4[
                .//a[contains(@title, "Let's Go, Pikachu et Let's Go, Évoli")]
            ][1]"""
        )
        if not lgpe_h4:
            return

        table = lgpe_h4.xpath("following::table[1]")
        if not table:
            return

        for row in table.xpath(".//tbody/tr"):
            move_name = row.xpath(
                "./td[2]//a/text() | ./td[2]/text()"
            ).get()

            if not move_name:
                continue

            yield PokemonMoveItem(
                pokemon_id=pokemon_id,
                move_name=move_name.strip(),
                learn_method="ct",
                learn_level=None,
            )

    # ==================================================
    # 🧑‍🏫 MOVE TUTOR – STARTERS ONLY
    # ==================================================
    def parse_move_tutor(self, response):
        """
        Parse Move Tutor moves (partner starters only).

        Args:
            response (scrapy.http.Response): Poképédia page response.

        Yields:
            PokemonMoveItem: Move tutor items.
        """
        pokemon_id = response.meta["pokemon_id"]
        pokemon_name = response.meta["pokemon_name"]

        tutor_header = response.xpath(
            '//*[@id="Par_donneur_de_capacités"]'
        )
        if not tutor_header:
            self.logger.warning(
                "[MOVE_TUTOR] header not found for %s",
                pokemon_name,
            )
            return

        h4 = tutor_header.xpath(
            f"""following::h4[
                .//text()[contains(., "{pokemon_name}")]
            ][1]"""
        )
        if not h4:
            self.logger.warning(
                "[MOVE_TUTOR] h4 not found for %s",
                pokemon_name,
            )
            return

        table = h4.xpath("following::table[1]")
        if not table:
            self.logger.warning(
                "[MOVE_TUTOR] table not found for %s",
                pokemon_name,
            )
            return

        for row in table.xpath(".//tbody/tr"):
            move_name = row.xpath(
                "./td[1]//a/text() | ./td[1]/text()"
            ).get()

            if not move_name:
                continue

            yield PokemonMoveItem(
                pokemon_id=pokemon_id,
                move_name=move_name.strip(),
                learn_method="move_tutor",
                learn_level=None,
            )
