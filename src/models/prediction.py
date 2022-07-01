import joblib
import pandas as pd
from tinydb import TinyDB, Query
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import (
    train_test_split,
    KFold,
    cross_val_score,
    LeaveOneOut,
)
from sklearn import preprocessing
from sklearn.metrics import accuracy_score
from utils.persist import db
from utils.ships import Ships


class Model:
    def __init__(self, goal):
        self.ships = Ships()
        self.goal = goal
        self.data = self.get_data()
        self.treat_data_columns()
        self.define_goal()
        self.set_wins()
        self.model = self.get_model()
        self.release_data()

    def get_data(self):
        table = db.table("ships")
        data = table.all()

        data.sort(key=lambda x: x["_id"])
        for _index, _data in enumerate(data.copy()):
            try:
                data[_index + 1]["last_game"] = _data["result"]
            except:
                continue

        data = pd.DataFrame(data)

        return data

    def treat_data_columns(self):
        self.data = self.data.drop(
            [
                "_id",
                "game_id",
                "game_name",
                "tickets",
                "progress",
                "last_time",
                "life_time",
                "count_down",
                "state",
                "ship_type",
                "f_seed",
                "previous_id",
                "next_id",
                "update_at",
                "create_at",
                "round_time",
                "bets",
            ],
            axis=1,
        )[1:]

    def define_goal(
        self,
    ):
        self.data["goal"] = self.goal

    def set_wins(self):
        self.data["win"] = pd.Series(self.data["result"] >= self.data["goal"]).astype(
            int
        )

    def get_model(self):
        self.model = RandomForestClassifier(
            n_estimators=20000, min_samples_leaf=2, random_state=0
        )
        self.model.fit(self.data.drop(["result", "win"], axis=1), self.data["win"])

        return self.model

    def release_data(self):
        self.data = []

    def predict(self, ships):
        df = []
        for ship in ships:
            df.append({"_id": ship["_id"], "last_game": ship["result"], "goal": 1.4})

        df = pd.DataFrame(df)
        df = df.sort_values(by="_id", ascending=True)

        prediction = self.model.predict(df.drop(["_id"], axis=1))

        return prediction
