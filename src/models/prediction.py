import logging
import joblib
import pandas as pd
from tinydb import TinyDB, Query
from sklearn.neural_network import MLPRegressor
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

BET_AMOUNT = 1

class Model:
    def __init__(self, goal):
        self.count_predictions = 0
        self.ships = Ships()
        self.goal = goal
        self.train()

    def train(self):
        self.data = self.get_data()
        self.data = self.treat_data_columns(self.data)
        self.data = self.define_goal(self.data)
        self.data = self.set_wins(self.data)
        self.model = self.get_model()
        self.count_predictions = 0
        self.release_data()

    def get_data(self):
        table = db.table("ships")
        data = table.all()

        data.sort(key=lambda x: x["_id"])
        for _index, _data in enumerate(data.copy()):
            try:
                if data[_index + 1]["previous_id"] == _data["_id"]:
                    data[_index + 1]["last_game"] = _data["result"]
            except:
                continue

        data = pd.DataFrame(data)

        return data

    def treat_data_columns(self, data):
        data = data.drop(
            [
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
                "update_at",
                "create_at",
                "round_time",
                "bets",
            ],
            axis=1,
        )[1:]

        return data.dropna()

    def define_goal(
        self, data
    ):
        data["goal"] = self.goal

        return data

    def set_wins(self, data):
        data["win"] = pd.Series(data["result"] >= data["goal"]).astype(
            int
        )

        return data

    def get_model(self):
        self.model = RandomForestClassifier(
            n_estimators=1000, min_samples_leaf=1, random_state=0
        )

        # self.model = MLPRegressor(learning_rate_init=0.1, max_iter=10000, activation="logistic", random_state=0, power_t=1.5)

        print(f"Training with : {len(self.data)} data")
        self.model.fit(self.data.drop(["result", "win"], axis=1), self.data["win"])

        return self.model

    def release_data(self):
        self.data = []

    def predict(self, ships):
        # if self.count_predictions >= 5:
        #     self.train()

        for ship in ships:
            df = []
            df.append(
                {
                    "_id": ship["next_id"],
                    "previous_id": ship["_id"],
                    "next_id": ship["next_id"] + 1,
                    "last_game": ship["result"],
                    "goal": self.goal,
                    "win": ship["result"] >= self.goal,
                    "result": ship["result"],
                }
            )

        df = pd.DataFrame(df)
        # df = self.get_data()
        # df = self.treat_data_columns(df)
        # df = self.define_goal(df)
        # df = self.set_wins(df)
        df = df.sort_values(by="_id", ascending=False)

        prediction = self.model.predict(df.drop(['result', 'win'], axis=1))
        self.count_predictions += 1

        # logging.info(f"Last game: {df['last_game'][0]}")
        logging.info(f"Next game prediction: {round(prediction[0], 2)}")

        return prediction
