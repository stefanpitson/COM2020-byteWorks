from app.forecasting.linear_regression.preprocessing import *
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
from app.core.database import engine
from sqlmodel import Session
import os


def train_lin_regression(df: pd.DataFrame, model_dir: str = "app/forecasting/linear_regression/models"):
    X, y_res, y_ns, feature_names = prepare_X_y(df)
    X_train, X_test, y_res_train, y_res_test, y_ns_train, y_ns_test = train_test_split(
        X, y_res, y_ns, test_size=0.2, random_state=42
    )
    
    # initiate the ridge model better than simpel linear regression - model for predicted reservations (res)
    model_res = Ridge(alpha=1.0)
    model_res.fit(X_train, y_res_train) # fir to the training data
    y_res_pred = model_res.predict(X_test)

    r2_res = r2_score(y_res_test, y_res_pred) # generate r2 and MAE scores to print
    mae_res = mean_absolute_error(y_res_test, y_res_pred)

    print(f"Reservation model – squared: {r2_res:.3f}, MAE: {mae_res:.2f}")
    
    # ridge model specifically for no shows (ns)
    model_ns = Ridge(alpha=1.0)
    model_ns.fit(X_train, y_ns_train)
    y_ns_pred = model_ns.predict(X_test)
    # calculate and print scores
    r2_ns = r2_score(y_ns_test, y_ns_pred) # show the correlation -> how much variance there is 1.0 is best
    mae_ns = mean_absolute_error(y_ns_test, y_ns_pred) # error between predicted vs actual lower is best

    # we make a dict and save these values for a confidence calulation later on
    metrics = {
        'reserved_r2': r2_res,
        'reserved_mae': mae_res,
        'no_show_r2': r2_ns,
        'no_show_mae': mae_ns,
    }
    joblib.dump(metrics, f"{model_dir}/metrics.pkl") # save the metrics

    print(f"No‑show model – R-squared: {r2_ns:.3f}, MAE: {mae_ns:.2f}")
    
    # save models and feature names so they can be loaded for inference
    joblib.dump(model_res, f"{model_dir}/ridge_reserved.pkl")
    joblib.dump(model_ns, f"{model_dir}/ridge_no_show.pkl")
    joblib.dump(feature_names, f"{model_dir}/feature_names.pkl")



if __name__ == "__main__":

    #python -m app.forecasting.linear_regression.train
    
    with Session(engine) as session:
        train_data = create_train_data(session)
        train_lin_regression(train_data)