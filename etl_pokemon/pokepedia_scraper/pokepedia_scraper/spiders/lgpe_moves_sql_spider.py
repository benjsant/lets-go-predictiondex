"""
Scrapy Spider for extracting Pokémon Let's Go move learnsets from Poképédia.

This spider scrapes Pokémon move learnsets specific to Pokémon Let's Go
Pikachu / Let's Go Eevee (LGPE) and emits normalized Scrapy items for
database persistence.

Key characteristics:
- Database-driven scraping (SQLAlchemy source of truth)
- Form-aware (base, alola, starter; mega excluded)
- Idempotent execution (safe re-runs, especially for starter forms)
- Responsible scraping (robots.txt + throttling)
- Clean separation of parsing responsibilities

Competency Block:
- E1: Data extraction, normalization, and relational persistence
"""

from __future__ import annotations

import re

import scrapy
from sqlalchemy.orm import Session

from pokepedia_scraper.items import PokemonMoveItem
from core.db.session import engine
from core.models import Form, Pokemon


class LetsGoPokemonMovesSQLSpider(scrapy.Spider):
    """
    Scrapy Spider extracting Pokémon move learnsets for LGPE from Poképédia.

    The spider reads Pokémon and their forms directly from the database,
    avoiding hardcoded lists and ensuring consistency with the ETL pipeline.

    Parsed learning methods:
    - Level-up
    - Technical Machines (CT)
    - Move Tutor (starter Pokémon only)
    """

    name = "letsgo_moves_sql"
    allowed_domains = ["pokepedia.fr"]

    # ==================================================
    # Entry point
    # ==================================================

    def start_requests(self):
        """
        Generate initial Scrapy requests based on Pokémon stored in the database.

        Behavior:
        - Mega forms are excluded (handled by a dedicated ETL)
        - Pokémon without a Poképédia name are skipped
        - Starter forms are always re-scraped (dont_filter=True)

        Yields:
            scrapy.Request: Initial request for each eligible Pokémon
        """
        with Session(engine) as session:
            form_ids = {form.name: form.id for form in session.query(Form).all()}
            starter_form_id = form_ids.get("starter")
            mega_form_id = form_ids.get("mega")

            pokemons = (
                session.query(Pokemon)
                .filter(Pokemon.form_id != mega_form_id)
                .all()
            )

            for pokemon in pokemons:
                if not pokemon.name_pokepedia:
                    continue

                url = (
                    f"https://www.pokepedia.fr/"
                    f"{pokemon.name_pokepedia}/Génération_7"
                )

                dont_filter = pokemon.form_id == starter_form_id

                self.logger.info(
                    "[START] id=%s name=%s form_id=%s",
                    pokemon.id,
                    pokemon.name_pokepedia,
                    pokemon.form_id,
                )

                yield scrapy.Request(
                    url=url,
                    callback=self.parse_all,
                    dont_filter=dont_filter,
                    meta={
                        "pokemon_id": pokemon.id,
                        "pokemon_name": pokemon.name_pokepedia,
                        "form_id": pokemon.form_id,
                        "starter_form_id": starter_form_id,
                    },
                )

    # ==================================================
    # Main dispatcher
    # ==================================================

    def parse_all(self, response):
        """
        Master parser delegating to all learning-method parsers.

        Delegates to:
        - parse_level_up
        - parse_ct
        - parse_move_tutor (starter Pokémon only)

        Args:
            response (scrapy.http.Response): Poképédia HTML response

        Yields:
            PokemonMoveItem: Normalized move learnset items
        """
        pokemon_id = response.meta["pokemon_id"]
        form_id = response.meta["form_id"]
        starter_form_id = response.meta["starter_form_id"]

        is_starter = form_id == starter_form_id

        self.logger.info(
            "[PARSE_ALL] id=%s starter=%s",
            pokemon_id,
            is_starter,
        )

        yield from self.parse_level_up(response)
        yield from self.parse_ct(response)

        if is_starter:
            yield from self.parse_move_tutor(response)

    # ==================================================
    # Level-up moves
    # ==================================================

    def parse_level_up(self, response):
        """
        Parse moves learned by leveling up in LGPE.

        Special cases:
        - "Départ" → level 0
        - "Évolution" → level -1
        - "N.xx" → integer level

        Args:
            response (scrapy.http.Response): Poképédia HTML response

        Yields:
            PokemonMoveItem: Level-up move items
        """
        pokemon_id = response.meta["pokemon_id"]

        header = response.xpath('//*[@id="Par_montée_en_niveau"]')
        if not header:
            return

        table = header.xpath("following::table[1]")
        if not table:
            return

        lgpe_col_index = self._find_lgpe_column_index(table)
        if lgpe_col_index is None:
            return

        for row in table.xpath(".//tbody/tr"):
            move_name = row.xpath(
                "./td[1]//a/text() | ./td[1]/text()"
            ).get()
            lgpe_cell = row.xpath(f"./td[{lgpe_col_index}]")

            if not move_name or not lgpe_cell:
                continue

            for level in self._parse_lgpe_levels(lgpe_cell):
                yield PokemonMoveItem(
                    pokemon_id=pokemon_id,
                    move_name=move_name.strip(),
                    learn_method="level_up",
                    learn_level=level,
                )

    @staticmethod
    def _find_lgpe_column_index(table):
        """
        Identify the LGPE column index in a level-up move table.

        Args:
            table (Selector): Scrapy selector pointing to the table

        Returns:
            int | None: 1-based LGPE column index, or None if not found
        """
        headers = table.xpath(".//thead/tr[2]/th")
        for index, header in enumerate(headers, start=1):
            title = header.xpath(".//a/@title").get()
            if title and "Let's Go, Pikachu et Let's Go, Évoli" in title:
                return index
        return None

    @staticmethod
    def _parse_lgpe_levels(cell):
        """
        Parse LGPE learning levels from a table cell.

        Args:
            cell (Selector): Scrapy selector for the LGPE cell

        Returns:
            list[int]: Parsed learning levels
        """
        levels = []

        for raw in cell.xpath(".//text()").getall():
            text = raw.strip()
            if not text or text == "—":
                continue

            if text == "Départ":
                levels.append(0)
            elif text == "Évolution":
                levels.append(-1)
            else:
                match = re.search(r"N\.(\d+)", text)
                if match:
                    levels.append(int(match.group(1)))

        return levels

    # ==================================================
    # Technical Machines
    # ==================================================

    def parse_ct(self, response):
        """
        Parse Technical Machine (CT) moves for LGPE Pokémon.

        Args:
            response (scrapy.http.Response): Poképédia HTML response

        Yields:
            PokemonMoveItem: CT move items
        """
        pokemon_id = response.meta["pokemon_id"]

        header = response.xpath('//*[@id="Par_CT"]')
        if not header:
            return

        lgpe_h4 = header.xpath(
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
    # Move Tutor (starter only)
    # ==================================================

    def parse_move_tutor(self, response):
        """
        Parse Move Tutor moves for starter Pokémon only.

        Args:
            response (scrapy.http.Response): Poképédia HTML response

        Yields:
            PokemonMoveItem: Move Tutor items
        """
        pokemon_id = response.meta["pokemon_id"]
        pokemon_name = response.meta["pokemon_name"]

        header = response.xpath('//*[@id="Par_donneur_de_capacités"]')
        if not header:
            self.logger.warning(
                "[MOVE_TUTOR] Header not found for %s",
                pokemon_name,
            )
            return

        h4 = header.xpath(
            f"""following::h4[
                .//text()[contains(., "{pokemon_name}")]
            ][1]"""
        )
        if not h4:
            self.logger.warning(
                "[MOVE_TUTOR] Section not found for %s",
                pokemon_name,
            )
            return

        table = h4.xpath("following::table[1]")
        if not table:
            self.logger.warning(
                "[MOVE_TUTOR] Table not found for %s",
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
