#!/usr/bin/env python3
import pandas
import sqlite3
import pathlib
import pickle
import argparse
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import KFold

_db_path = pathlib.Path(".", "database.sqlite")
_model_path = pathlib.Path(".", "model.bin")

def cmd_line(f):
    def wrap(*args, **kwargs):
        ap = argparse.ArgumentParser(description="KFolds HW")
        ap.add_argument("-p", "--print-scores", default=False, required=False, action="store_true", help="Print accuracy scores.")
        return f(ap.parse_args(), *args, **kwargs)
    return wrap

def get_model():
    if _model_path.exists():
        with open(str(_model_path), "rb") as f:
            model = pickle.load(f)
    else:
        model = MultinomialNB()
        with open(str(_model_path), "wb") as f:
            pickle.dump(model, f)
    return model

def get_data():
    scaler = MinMaxScaler(feature_range=(0,1))
    with sqlite3.connect(_db_path) as conn:
        raw = pandas.read_sql_query(
            "select * from county_winners",
            conn
        )
        y = raw.candidate.to_numpy()
        x = raw.drop(columns="candidate").to_numpy()
        x = scaler.fit_transform(x)
    return x, y

def get_accuracy_scores(x, y, model, print_scores=False):
    kf = KFold(n_splits=10)
    accuracy_scores = []
    for train_i, test_i in kf.split(x):
        x_train, x_test, y_train, y_test = x[train_i], x[test_i], y[train_i], y[test_i]
        model.fit(x_train, y_train)
        score = model.score(x_test, y_test)
        accuracy_scores.append(score)
        if print_scores:
            print(score)
    return accuracy_scores


@cmd_line
def main(args):
    x, y = get_data()
    get_accuracy_scores(
        x, y, get_model(), print_scores=args.print_scores
    )

    
if __name__ ==  "__main__":
    main()