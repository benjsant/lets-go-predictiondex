"""
Spider Scrapy – Poképédia (Let's Go Pikachu / Évoli)
---------------------------------------------------
Scraping des capacités LGPE depuis la BDD (SQLAlchemy)
Level-up, CT et Move Tutor inclus
Logique basée sur les formes (model-driven)
"""

import scrapy
import re
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import engine
from app.models import Pokemon
from pokepedia_scraper.items import PokemonMoveItem


class LetsGoPokemonMovesSQLSpider(scrapy.Spider):
    name = "letsgo_moves_sql"
    allowed_domains = ["pokepedia.fr"]

    # ==================================================
    # ▶️ POINT D’ENTRÉE : BDD
    # ==================================================
    def start_requests(self):
        with Session(engine) as session:
            pokemons = session.execute(
                select(Pokemon).where(Pokemon.is_mega.is_(False))
            ).scalars()

            for pokemon in pokemons:
                if not pokemon.nom_pokepedia:
                    continue

                url = f"https://www.pokepedia.fr/{pokemon.nom_pokepedia}/Génération_7"

                # 🔑 Règle clé : on force le re-scrap uniquement pour les starters
                use_dont_filter = pokemon.is_starter

                self.logger.info(
                    f"[START] id={pokemon.id} "
                    f"name={pokemon.nom_pokepedia} "
                    f"form={pokemon.form_name} "
                    f"is_starter={pokemon.is_starter}"
                )

                yield scrapy.Request(
                    url=url,
                    callback=self.parse_all,
                    dont_filter=use_dont_filter,
                    meta={
                        "pokemon_id": pokemon.id,
                        "pokemon_name": pokemon.nom_pokepedia,
                        "is_starter": pokemon.is_starter,
                    },
                )

    # ==================================================
    # 🧠 PARSER MAÎTRE
    # ==================================================
    def parse_all(self, response):
        pokemon_id = response.meta["pokemon_id"]
        is_starter = response.meta["is_starter"]

        self.logger.info(
            f"[PARSE_ALL] id={pokemon_id} starter={is_starter}"
        )

        yield from self.parse_level_up(response)
        yield from self.parse_ct(response)

        # 🎯 Move tutor UNIQUEMENT pour les starters partenaires
        if is_starter:
            yield from self.parse_move_tutor(response)

    # ==================================================
    # 📈 LEVEL-UP LGPE
    # ==================================================
    def parse_level_up(self, response):
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
        headers = table.xpath(".//thead/tr[2]/th")
        for idx, th in enumerate(headers, start=1):
            title = th.xpath(".//a/@title").get()
            if title and "Let's Go, Pikachu et Let's Go, Évoli" in title:
                return idx
        return None

    @staticmethod
    def parse_lgpe_levels(cell):
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
    # 💿 CT LGPE
    # ==================================================
    def parse_ct(self, response):
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
    # 🧑‍🏫 MOVE TUTOR – STARTERS SEULEMENT
    # ==================================================
    def parse_move_tutor(self, response):
        pokemon_id = response.meta["pokemon_id"]
        pokemon_name = response.meta["pokemon_name"]

        tutor_header = response.xpath('//*[@id="Par_donneur_de_capacités"]')
        if not tutor_header:
            self.logger.warning(f"[MOVE_TUTOR] header not found for {pokemon_name}")
            return

        h4 = tutor_header.xpath(
            f"""following::h4[
                .//text()[contains(., "{pokemon_name}")]
            ][1]"""
        )
        if not h4:
            self.logger.warning(f"[MOVE_TUTOR] h4 not found for {pokemon_name}")
            return

        table = h4.xpath("following::table[1]")
        if not table:
            self.logger.warning(f"[MOVE_TUTOR] table not found for {pokemon_name}")
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
