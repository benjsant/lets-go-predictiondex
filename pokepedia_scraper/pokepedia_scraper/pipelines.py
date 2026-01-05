from pathlib import Path
from itemadapter import ItemAdapter


class PokemonMovesPipeline:
    def open_spider(self, spider):
        project_root = Path(__file__).resolve().parents[2]
        output_dir = project_root / "data" / "csv"
        output_dir.mkdir(parents=True, exist_ok=True)

        self.file_path = output_dir / "pokemon_moves_letsgo.csv"

        self.file = open(
            self.file_path,
            "w",
            encoding="utf-8",
            newline=""
        )

        self.file.write(
            "pokemon_id,pokemon_fr,pokemon_pokepedia,"
            "move_name,learn_method,learn_level\n"
        )

    def close_spider(self, spider):
        if hasattr(self, "file"):
            self.file.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        self.file.write(
            f"{adapter.get('pokemon_id')},"
            f"{adapter.get('pokemon_fr')},"
            f"{adapter.get('pokemon_pokepedia')},"
            f"{adapter.get('move_name')},"
            f"{adapter.get('learn_method')},"
            f"{adapter.get('learn_level')}\n"
        )

        return item
