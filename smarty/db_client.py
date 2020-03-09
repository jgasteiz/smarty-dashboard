import json


class DBClient:
    db_file_name = "db.json"

    @classmethod
    def get_db(cls) -> dict:
        try:
            with open(cls.db_file_name, "r") as f:
                return json.loads(f.read())
        except FileNotFoundError:
            return {}

    @classmethod
    def update_db(cls, db):
        with open(cls.db_file_name, "w") as f:
            f.write(json.dumps(db))
