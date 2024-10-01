from TimeSeriesAnalysis.config import MODELS_DIR, RAW_DATA_DIR, PREDICTED_DATA_DIR
from TimeSeriesAnalysis.features import feature_engineering
from TimeSeriesAnalysis.forecast_model import TimeSeriesForecast

from tqdm import tqdm
from loguru import logger
from pathlib import Path
import typer
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn

mlflow.set_tracking_uri("http://127.0.0.1:5000")
app = typer.Typer()


@app.command()
def main(
    # ---- Define input and output paths ----
    train_data_path: Path = RAW_DATA_DIR / "climate_data/GlobalLandTemperatures_US_train.csv",
    model_name: str = "TEMPERATURE_FORECAST",
    model_version: int = 4,
    model_type: str = "SARIMA",
    future_steps: int = 100,
    # -----------------------------------------
):
    # Load the model from MLflow

    logger.info(f"Making predictions with '{model_name}' version {model_version}...")
    logger.info(f"Loading model '{model_name}' version {model_version}...")
    model_uri = f"models:/{model_name}/{model_version}"

    # Start MLflow run for logging (optional)
    mlflow.start_run()

    # Load the features for prediction
    try:
        df = pd.read_csv(train_data_path)
        temp_series = feature_engineering(df, model_type=model_type)
        logger.success("Test data loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to preprocess temperature series: {e}")
        return

    # Make predictions
    logger.info("Making predictions...")
    # Load the model using MLflow
    if model_type == "SARIMA":
        logger.error(f"Not supported as of today")
        return
        """model = mlflow.pyfunc.load_model(model_uri)
        forecast = model.predict()
        forecast_df = forecast.summary_frame()
        forecast_values = forecast_df.loc[:, 'mean'].values"""

    elif model_type == "LSTM":
        deployed_model = mlflow.pytorch.load_model(model_uri)
        model = TimeSeriesForecast(data=temp_series.values, model_type=model_type)

        model.load_model(deployed_model)
        forecast_values = model.predict(future_steps=future_steps)

    logger.info("Forecast complete.")

    # End MLflow run
    mlflow.end_run()


if __name__ == "__main__":
    app()