import os

import joblib
import pandas as pd
from flask import Flask, jsonify, request
from flask.logging import create_logger
import logging

# The order the model was trained on. Requests are reindexed to it, because a
# model reads features by position: JSON object keys have no guaranteed order, so
# without this a client sending LSTAT first would have every feature fed into the
# wrong slot and get a confidently wrong prediction.
FEATURES = ['CHAS', 'RM', 'TAX', 'PTRATIO', 'B', 'LSTAT']

MODEL_PATH = os.getenv(
    'MODEL_PATH', 'model_data/boston_housing_prediction.joblib')
SCALER_PATH = os.getenv('SCALER_PATH', 'model_data/scaler.joblib')

app = Flask(__name__)
LOG = create_logger(app)
LOG.setLevel(logging.INFO)

def load_artifact(path, what):
    """Loads a joblib artifact, or explains how to produce it."""
    try:
        return joblib.load(path)
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"{what} not found at {path}. Run `python train.py` first. This repo "
            "generates the model and the scaler from model_data/housing.csv "
            "instead of committing them, so the scikit-learn you installed from "
            "requirements.txt is always the one that wrote them.") from exc


# Loaded at import time, not inside __main__. Under gunicorn or any other WSGI
# server the __main__ block never runs, which used to leave clf undefined and
# every /predict raising NameError.
clf = load_artifact(MODEL_PATH, 'Model')
scaler = load_artifact(SCALER_PATH, 'Scaler')


def scale(payload):
    """Scales a request with the statistics learned during training.

    The scaler is loaded, never fitted here. Fitting on the incoming row gives it
    zero variance, so every feature centres to 0.0 and the model sees the same
    vector for every request, whatever was asked. Run train.py to produce the
    scaler alongside the model.
    """
    LOG.info("Scaling payload with the trained scaler")
    return scaler.transform(payload.astype(float))


@app.route("/")
def home():
    return "<h3>Sklearn Prediction Home</h3>"


@app.route("/predict", methods=['POST'])
def predict():
    """Performs an sklearn prediction

        input looks like:
        {
        "CHAS":{
        "0":0
        },
        "RM":{
        "0":6.575
        },
        "TAX":{
        "0":296.0
        },
        "PTRATIO":{
        "0":15.3
        },
        "B":{
        "0":396.9
        },
        "LSTAT":{
        "0":4.98
        }

        result looks like:
        { "prediction": [ <val> ] }

        """
    json_payload = request.json
    LOG.info("Received a prediction request")
    inference_payload = pd.DataFrame(json_payload)

    # Reindex to the trained feature order before anything touches the values.
    inference_payload = inference_payload[FEATURES]

    scaled_payload = scale(inference_payload)
    prediction = list(clf.predict(scaled_payload))
    LOG.info(f"Prediction: {prediction}")

    return jsonify({'prediction': prediction})


if __name__ == "__main__":
    # debug=False: the Werkzeug debugger exposes an interactive Python console,
    # and this listens on every interface inside a container. PORT defaults to an
    # unprivileged port so the image can run as a non-root user.
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '8080')), debug=False)
