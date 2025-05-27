import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_squared_error

def calculate_sharpe_ratio(returns, risk_free_rate=0.0, trading_days=252):
    """
    Calculates the Sharpe Ratio for a series of returns.
    """
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    if std_return == 0:
        return np.nan # Avoid division by zero; or could return 0 or some other indicator
    sharpe_ratio = (mean_return - risk_free_rate) / std_return * np.sqrt(trading_days)
    return sharpe_ratio

def calculate_annualized_return(returns, trading_days=252):
    """
    Calculates the annualized return.
    """
    mean_return = np.mean(returns)
    annualized_return = mean_return * trading_days
    return annualized_return

def main():
    processed_data_filename = 'processed_data.npz'
    model_filename = 'lstm_model.h5'

    # 1. Load preprocessed validation data
    try:
        data = np.load(processed_data_filename)
        X_val = data['X_val']
        y_val_actual = data['y_val'] # Actual returns
        print(f"Step 1/5: Validation data (X_val, y_val) loaded successfully from {processed_data_filename}")
    except FileNotFoundError:
        print(f"Error: Processed data file {processed_data_filename} not found. Please run preprocessing first.")
        return
    except KeyError as e:
        print(f"Error: Missing key {e} in {processed_data_filename}. Ensure the file is correctly formatted.")
        return

    # 2. Load the trained LSTM model
    try:
        model = load_model(model_filename)
        print(f"Step 2/5: Trained LSTM model loaded successfully from {model_filename}")
    except Exception as e: # More general exception for Keras model loading issues
        print(f"Error loading model {model_filename}: {e}")
        return

    # 3. Make predictions on the validation data
    y_val_predicted = model.predict(X_val)
    y_val_predicted = y_val_predicted.flatten() # Ensure predictions are 1D array like y_val_actual
    print(f"Step 3/5: Predictions made on X_val. Predicted shape: {y_val_predicted.shape}")

    # 4. Calculate performance metrics
    print("Step 4/5: Calculating performance metrics...")

    # MSE
    mse = mean_squared_error(y_val_actual, y_val_predicted)
    print(f"\nMean Squared Error (MSE): {mse:.6f}")

    # Sharpe Ratio (based on predicted returns)
    # As per clarification, using predicted returns to evaluate the model's output quality
    sharpe = calculate_sharpe_ratio(y_val_predicted)
    print(f"Sharpe Ratio (from predicted returns, risk-free rate=0): {sharpe:.4f}")

    # Annualized Return (based on predicted returns)
    annual_return = calculate_annualized_return(y_val_predicted)
    print(f"Annualized Return (from predicted returns): {annual_return:.4%}")

    print("\nStep 5/5: Model evaluation complete.")

if __name__ == "__main__":
    # Suppress TensorFlow INFO and WARNING messages for cleaner output
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
    main()
