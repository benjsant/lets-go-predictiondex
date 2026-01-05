from pathlib import Path
import csv
import re
import scrapy
from pokepedia_scraper.items import PokemonMoveItem


class LetsGoPokemonMovesSpider(scrapy.Spider):
    name = "letsgo_moves"
    allowed_domains = ["pokepedia.fr"]

    # Mapping starter → nom de base pour move tutor
    STARTER_BASE_MAP = {
        "pikachu-starter": "Pikachu",
        "eevee-starter": "Évoli",
    }
    BASE_DIR = Path(__file__).resolve().parents[4]

    csv_path = BASE_DIR / "data" / "csv" / "liste_pokemon.csv"

    # ----------------------------------
    # CSV d'entrée
    # ----------------------------------
    def start_requests(self):
        BASE_DIR = Path(__file__).resolve().parents[3]

        csv_path = BASE_DIR / "data" / "csv" / "liste_pokemon.csv"

        if not csv_path.exists():
            self.logger.error(f"CSV introuvable : {csv_path}")
            return

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                nom_pokepedia = row.get("nom_pokepedia")
                if not nom_pokepedia:
                    continue

                pokeapi_name = row.get("nom_pokeapi")
                is_starter = row.get("starter", "").strip() == "1"
                is_mega = row.get("mega", "").strip() == "1"
                starter_base_name = self.STARTER_BASE_MAP.get(pokeapi_name)

                # ❌ Méga → pas de scraping (héritage DB)
                if is_mega:
                    self.logger.info(
                        f"[{row['nom_fr']}] Méga ignorée (hérite des capacités de la forme de base)"
                    )
                    continue

                url = f"https://www.pokepedia.fr/{nom_pokepedia}/Génération_7"

                # ✅ dont_filter uniquement pour les starters partenaires
                use_dont_filter = is_starter

                yield scrapy.Request(
                    url=url,
                    callback=self.parse_all,
                    dont_filter=use_dont_filter,
                    meta={
                        "pokemon_id": int(row["id"]),
                        "pokemon_fr": row["nom_fr"],
                        "pokemon_pokepedia": nom_pokepedia,
                        "pokemon_pokeapi": pokeapi_name,
                        "is_starter": is_starter,
                        "starter_base_name": starter_base_name,
                    },
                )

    # ==========================================================
    # MASTER PARSER
    # ==========================================================
    def parse_all(self, response):
        yield from self.parse_level_up(response)
        yield from self.parse_ct(response)
        yield from self.parse_move_tutor(response)

    # ==========================================================
    # LEVEL-UP LGPE
    # ==========================================================
    def parse_level_up(self, response):
        pokemon_fr = response.meta["pokemon_fr"]
        self.logger.info(f"Analyse level-up : {pokemon_fr}")

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
            move_name = row.xpath("./td[1]//a/text()").get()
            lgpe_cell = row.xpath(f"./td[{lgpe_col_index}]")

            if not move_name or not lgpe_cell:
                continue

            for level in self.parse_lgpe_levels(lgpe_cell):
                yield PokemonMoveItem(
                    pokemon_id=response.meta["pokemon_id"],
                    pokemon_fr=pokemon_fr,
                    pokemon_pokepedia=response.meta["pokemon_pokepedia"],
                    move_name=move_name.strip(),
                    learn_method="level-up",
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

    # ==========================================================
    # CT LGPE
    # ==========================================================
    def parse_ct(self, response):
        pokemon_fr = response.meta["pokemon_fr"]

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
            ct_number = row.xpath("./td[1]//text()").get()
            move_name = row.xpath("./td[2]//a/text()").get()
            if not move_name:
                continue

            ct_level = (
                int(re.search(r"\d+", ct_number).group())
                if ct_number
                else None
            )

            yield PokemonMoveItem(
                pokemon_id=response.meta["pokemon_id"],
                pokemon_fr=pokemon_fr,
                pokemon_pokepedia=response.meta["pokemon_pokepedia"],
                move_name=move_name.strip(),
                learn_method="ct",
                learn_level=ct_level,
            )

    # ==========================================================
    # MOVE TUTOR LGPE (STARTERS PARTENAIRES SEULEMENT)
    # ==========================================================
    def parse_move_tutor(self, response):
        is_starter = response.meta.get("is_starter", False)
        starter_base_name = response.meta.get("starter_base_name")
        pokemon_fr = response.meta["pokemon_fr"]

        if not is_starter or not starter_base_name:
            self.logger.info(f"[{pokemon_fr}] Move tutor ignoré (non starter)")
            return

        tutor_header = response.xpath('//*[@id="Par_donneur_de_capacités"]')
        if not tutor_header:
            return

        h4 = tutor_header.xpath(
            f"""following::h4[
                .//text()[contains(., "{starter_base_name}")]
            ][1]"""
        )
        if not h4:
            return

        table = h4.xpath("following::table[1]")
        if not table:
            return

        for row in table.xpath(".//tbody/tr"):
            move_name = row.xpath("./td[1]//text()").get()
            if not move_name:
                continue

            yield PokemonMoveItem(
                pokemon_id=response.meta["pokemon_id"],
                pokemon_fr=pokemon_fr,
                pokemon_pokepedia=response.meta["pokemon_pokepedia"],
                move_name=move_name.strip(),
                learn_method="move_tutor",
                learn_level=None,
            )
