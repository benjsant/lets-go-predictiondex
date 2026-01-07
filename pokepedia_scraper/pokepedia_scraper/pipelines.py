from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.db.session import engine
from app.models import Move, LearnMethod, PokemonMove


class PokemonMovePipeline:
    def open_spider(self, spider):
        self.session = Session(engine)

        # --- Cache local (performance) ---
        self.learn_method_cache = {
            lm.name: lm.id
            for lm in self.session.execute(select(LearnMethod)).scalars()
        }

        self.move_cache = {
            m.name.lower(): m.id
            for m in self.session.execute(select(Move)).scalars()
        }

    def close_spider(self, spider):
        try:
            self.session.commit()
        except Exception as e:
            spider.logger.warning(f"[CLOSE SPIDER COMMIT ERROR] {e}")
            self.session.rollback()
        finally:
            self.session.close()

    def process_item(self, item, spider):
        # --- Normalisation du nom de la capacité ---
        move_name = item["move_name"].strip().lower().replace("’", "'")

        move_id = self.move_cache.get(move_name)
        if not move_id:
            spider.logger.info(f"[MOVE NOT FOUND] {item['move_name']}")
            return item

        learn_method_id = self.learn_method_cache.get(item["learn_method"])
        if not learn_method_id:
            spider.logger.info(f"[LEARN METHOD NOT FOUND] {item['learn_method']}")
            return item

        learn_level = item.get("learn_level")

        # --- Upsert PostgreSQL ---
        stmt = insert(PokemonMove).values(
            pokemon_id=item["pokemon_id"],
            move_id=move_id,
            learn_method_id=learn_method_id,
            learn_level=learn_level,
        ).on_conflict_do_update(
            index_elements=['pokemon_id', 'move_id', 'learn_method_id'],
            set_=dict(learn_level=learn_level)
        )

        try:
            self.session.execute(stmt)
            self.session.flush()
        except Exception as e:
            spider.logger.warning(f"[UPSERT ERROR] {item} -> {e}")
            self.session.rollback()  # sécurité

        return item
