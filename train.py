"""Trains the model and the scaler this service serves with.

The repository shipped a .joblib model but no way to reproduce it, and that
artifact was written by a scikit-learn old enough (it references
sklearn.ensemble.gradient_boosting and sklearn.externals.joblib) that the version
pinned in requirements.txt can no longer load it. Training from the committed
housing.csv makes the service reproducible with one command.

It also saves the scaler. That is not a convenience: the API has to transform a
request with the statistics learned from the TRAINING data. Fitting a scaler on
the single incoming row, as the service used to, gives that row zero variance, so
every feature centres to 0.0 and the model receives an identical vector no matter
what was asked.

    python train.py
"""
import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# housing.csv has no header row and is whitespace separated. These are the Boston
# housing columns in file order.
ALL_COLUMNS = [
    'CRIM', 'ZN', 'INDUS', 'CHAS', 'NOX', 'RM', 'AGE', 'DIS', 'RAD', 'TAX',
    'PTRATIO', 'B', 'LSTAT', 'MEDV'
]

# The six the API accepts, in the order the model is trained on. app.py reindexes
# every request to this list, so a client sending JSON keys in another order
# still gets the right answer.
FEATURES = ['CHAS', 'RM', 'TAX', 'PTRATIO', 'B', 'LSTAT']
TARGET = 'MEDV'

DATA_PATH = 'model_data/housing.csv'
MODEL_PATH = 'model_data/boston_housing_prediction.joblib'
SCALER_PATH = 'model_data/scaler.joblib'

RANDOM_STATE = 42


def load_data(path=DATA_PATH):
    frame = pd.read_csv(path, sep=r'\s+', header=None, names=ALL_COLUMNS)
    return frame[FEATURES], frame[TARGET]


def main():
    features, target = load_data()
    print(f'Loaded {len(features)} rows, {len(FEATURES)} features')

    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=RANDOM_STATE)

    # Fit on the training split only. Fitting on everything would leak the test
    # rows' statistics into the scaler.
    scaler = StandardScaler().fit(x_train)

    model = GradientBoostingRegressor(random_state=RANDOM_STATE)
    model.fit(scaler.transform(x_train), y_train)

    predictions = model.predict(scaler.transform(x_test))
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    print(f'Holdout R2:   {r2_score(y_test, predictions):.3f}')
    print(f'Holdout RMSE: {rmse:.3f} (MEDV is in $1000s)')

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f'Wrote {MODEL_PATH} and {SCALER_PATH}')


if __name__ == '__main__':
    main()
