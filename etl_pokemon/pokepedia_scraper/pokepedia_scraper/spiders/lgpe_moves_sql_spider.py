import re
import scrapy
from sqlalchemy.orm import Session
from sqlalchemy import select

from core.db.session import engine
from core.models import Pokemon, Form
from pokepedia_scraper.items import PokemonMoveItem


class LetsGoPokemonMovesSQLSpider(scrapy.Spider):
    """
    Scrapy Spider for extracting Pokémon move learnsets specific to
    Pokémon Let's Go Pikachu / Let's Go Eevee (LGPE) from Poképédia.

    This spider is database-driven, reading Pokémon and their forms from
    the PostgreSQL database using SQLAlchemy. It handles multiple
    learning methods (level-up, Technical Machines, Move Tutor) and
    emits validated Scrapy items for downstream database persistence.

    Key Features:
    - Model-driven scraping: no hardcoded Pokémon lists
    - Form-aware: handles base, mega, alola, and starter forms
    - Idempotent: can safely re-run for starter forms
    - Responsible scraping: respects throttling and robots.txt
    - Incremental persistence via PokemonMoveItem

    Competency Block:
    - E1: Data extraction, normalization, and relational persistence
    """

    name = "letsgo_moves_sql"
    allowed_domains = ["pokepedia.fr"]

    # ==================================================
    def start_requests(self):
        """
        Generate initial Scrapy requests based on Pokémon stored in the database.

        Behavior:
        - Excludes Mega forms (they inherit moves later)
        - Only Pokémon with a valid Poképédia name are processed
        - Starter forms are always re-scraped (forcing 'dont_filter')

        Each request passes metadata including:
        - pokemon_id: primary key of the Pokémon
        - pokemon_name: Poképédia page name
        - form_id: ID of the Pokémon's form
        - starter_form_id: ID of the "starter" form (used for conditional logic)
        
        Yields:
            scrapy.Request: Request object for each eligible Pokémon
        """
        with Session(engine) as session:
            # Retrieve all forms from DB and map name → ID
            form_ids = {form.name: form.id for form in session.query(Form).all()}
            starter_form_id = form_ids.get("starter")
            mega_form_id = form_ids.get("mega")

            # Filter Pokémon to exclude Mega forms
            pokemons = session.query(Pokemon).filter(Pokemon.form_id != mega_form_id).all()

            for pokemon in pokemons:
                if not pokemon.name_pokepedia:
                    continue

                url = f"https://www.pokepedia.fr/{pokemon.name_pokepedia}/Génération_7"
                use_dont_filter = pokemon.form_id == starter_form_id

                self.logger.info(
                    "[START] id=%s name=%s form_id=%s",
                    pokemon.id,
                    pokemon.name_pokepedia,
                    pokemon.form_id,
                )

                yield scrapy.Request(
                    url=url,
                    callback=self.parse_all,
                    dont_filter=use_dont_filter,
                    meta={
                        "pokemon_id": pokemon.id,
                        "pokemon_name": pokemon.name_pokepedia,
                        "form_id": pokemon.form_id,
                        "starter_form_id": starter_form_id,
                    },
                )

    # ==================================================
    def parse_all(self, response):
        """
        Master parser coordinating all move learnset parsers.

        Delegates to specialized sub-parsers:
        - Level-up moves (parse_level_up)
        - Technical Machines (parse_ct)
        - Move Tutor moves (parse_move_tutor, starter forms only)

        Determines whether the Pokémon is a starter based on its form_id.

        Args:
            response (scrapy.http.Response): HTTP response from Poképédia page

        Yields:
            PokemonMoveItem: Parsed Pokémon move learnset items
        """
        pokemon_id = response.meta["pokemon_id"]
        form_id = response.meta["form_id"]
        starter_form_id = response.meta["starter_form_id"]

        is_starter = form_id == starter_form_id
        self.logger.info("[PARSE_ALL] id=%s starter=%s", pokemon_id, is_starter)

        yield from self.parse_level_up(response)
        yield from self.parse_ct(response)

        if is_starter:
            yield from self.parse_move_tutor(response)

    # ==================================================
    def parse_level_up(self, response):
        """
        Parse Pokémon moves learned by leveling up in LGPE.

        Strategy:
        - Locate the "Par montée en niveau" section on the page
        - Identify the LGPE-specific column in the moves table
        - Parse levels (special cases: "Départ" → 0, "Évolution" → -1, "N.xx" → integer)
        
        Args:
            response (scrapy.http.Response): HTTP response from Poképédia page

        Yields:
            PokemonMoveItem: Each level-up move with corresponding learn level
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
            move_name = row.xpath("./td[1]//a/text() | ./td[1]/text()").get()
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
        Identify the column index in the moves table corresponding to LGPE.

        Args:
            table (Selector): Scrapy Selector pointing to the HTML table

        Returns:
            int | None: 1-based column index of LGPE moves, or None if not found
        """
        headers = table.xpath(".//thead/tr[2]/th")
        for idx, th in enumerate(headers, start=1):
            title = th.xpath(".//a/@title").get()
            if title and "Let's Go, Pikachu et Let's Go, Évoli" in title:
                return idx
        return None

    @staticmethod
    def parse_lgpe_levels(cell):
        """
        Parse level-up information from a table cell.

        Special cases:
        - "Départ" → level 0
        - "Évolution" → level -1
        - "N.xx" → integer level

        Args:
            cell (Selector): Scrapy Selector pointing to the LGPE table cell

        Returns:
            list[int]: Parsed level(s) at which the move is learned
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
    def parse_ct(self, response):
        """
        Parse Technical Machine (CT) moves for LGPE Pokémon.

        Strategy:
        - Locate the "Par_CT" section
        - Identify the LGPE-specific sub-section using <h4> headers
        - Extract move names from the corresponding table

        Args:
            response (scrapy.http.Response): HTTP response from Poképédia page

        Yields:
            PokemonMoveItem: Each CT move with no level (learn_level=None)
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
            move_name = row.xpath("./td[2]//a/text() | ./td[2]/text()").get()
            if not move_name:
                continue

            yield PokemonMoveItem(
                pokemon_id=pokemon_id,
                move_name=move_name.strip(),
                learn_method="ct",
                learn_level=None,
            )

    # ==================================================
    def parse_move_tutor(self, response):
        """
        Parse Move Tutor moves for starter Pokémon only.

        Strategy:
        - Locate the "Par_donneur_de_capacités" section
        - Identify the <h4> corresponding to the Pokémon's name
        - Extract move names from the subsequent table

        Args:
            response (scrapy.http.Response): HTTP response from Poképédia page

        Yields:
            PokemonMoveItem: Each move tutor move with no level (learn_level=None)
        """
        pokemon_id = response.meta["pokemon_id"]
        pokemon_name = response.meta["pokemon_name"]

        tutor_header = response.xpath('//*[@id="Par_donneur_de_capacités"]')
        if not tutor_header:
            self.logger.warning("[MOVE_TUTOR] header not found for %s", pokemon_name)
            return

        h4 = tutor_header.xpath(
            f"""following::h4[
                .//text()[contains(., "{pokemon_name}")]
            ][1]"""
        )
        if not h4:
            self.logger.warning("[MOVE_TUTOR] h4 not found for %s", pokemon_name)
            return

        table = h4.xpath("following::table[1]")
        if not table:
            self.logger.warning("[MOVE_TUTOR] table not found for %s", pokemon_name)
            return

        for row in table.xpath(".//tbody/tr"):
            move_name = row.xpath("./td[1]//a/text() | ./td[1]/text()").get()
            if not move_name:
                continue

            yield PokemonMoveItem(
                pokemon_id=pokemon_id,
                move_name=move_name.strip(),
                learn_method="move_tutor",
                learn_level=None,
            )
