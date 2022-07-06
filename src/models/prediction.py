import logging
import joblib
import pandas as pd
from tinydb import TinyDB, Query
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.linear_model import ARDRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, VotingClassifier, AdaBoostClassifier
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
                "round_time",
                "bets",
            ],
            axis=1,
        )[1:]

        return data.dropna()

    def define_goal(self, data):
        data["goal"] = self.goal

        return data

    def set_wins(self, data):
        data["win"] = pd.Series(data["result"] >= data["goal"]).astype(int)

        return data

    def get_model(self):
        # self.model = MLPRegressor(learning_rate_init=0.1, max_iter=10000, activation="logistic", random_state=0, power_t=1.5)
        # self.model = MLPClassifier(random_state=0, learning_rate='adaptive', max_iter=2000)
        self.model = RandomForestClassifier(
            n_estimators=500, min_samples_leaf=1, random_state=0
        )
        # self.model = AdaBoostClassifier(random_state=2)
        # self.model = ARDRegression()
        # self.model = RandomForestRegressor()

        logging.info(f"Training with : {len(self.data)} data")

        labelEncoder = preprocessing.LabelEncoder()
        labelEncoder.fit(self.data["create_at"])
        self.data["create_at"] = labelEncoder.transform(self.data["create_at"])
        labelEncoder.fit(self.data["update_at"])
        self.data["update_at"] = labelEncoder.transform(self.data["update_at"])

        xtrain, xtest, ytrain, ytest = train_test_split(
            self.data.drop(["result", "win"], axis=1),
            self.data["win"],
            test_size=0.1,
            random_state=42,
        )
        self.model.fit(xtrain, ytrain)
        predict = self.model.predict(xtest)
        logging.info(f"Score do treino: {round(accuracy_score(predict, ytest) * 100)}%")
        # self.model.fit(self.data.drop(["result", "win"], axis=1), self.data["win"])

        return self.model

    def release_data(self):
        self.data = []

    def predict(self, ships):
        # if self.count_predictions >= 5:
        #     self.train()

        df = []
        for ship in ships:
            df.append(
                {
                    "_id": ship["next_id"],
                    "previous_id": ship["_id"],
                    "next_id": ship["next_id"] + 1,
                    "create_at": ship["create_at"],
                    "update_at": ship["update_at"],
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
        df = df.head(1)

        labelEncoder = preprocessing.LabelEncoder()
        labelEncoder.fit(df["create_at"])
        df["create_at"] = labelEncoder.transform(df["create_at"])
        labelEncoder.fit(df["update_at"])
        df["update_at"] = labelEncoder.transform(df["update_at"])

        prediction = self.model.predict(df.drop(["result", "win"], axis=1))
        self.count_predictions += 1

        logging.info(f"Last game: {df['last_game'][0]}")
        logging.info(f"Next game prediction: {round(prediction[0], 2)}")

        return prediction
