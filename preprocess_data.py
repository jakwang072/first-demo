import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
# train_test_split is not strictly needed if we split by index for time series
# from sklearn.model_selection import train_test_split

def main():
    input_filename = 'simulated_data.csv'
    output_filename = 'processed_data.npz'

    # 1. Load data
    try:
        df = pd.read_csv(input_filename)
        print(f"Step 1/7: Data loaded successfully from {input_filename}")
    except FileNotFoundError:
        print(f"Error: Input file {input_filename} not found. Please generate it first.")
        return

    # 2. Separate features and target
    features = ['factor1', 'factor2', 'factor3']
    target = 'returns'
    X = df[features]
    y = df[target]
    print("Step 2/7: Features and target separated.")

    # 3. Scale the features
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    print("Step 3/7: Features scaled using MinMaxScaler.")

    # 4. Split the data into training and validation sets (maintaining temporal order)
    train_size = int(len(X_scaled) * 0.8)
    # val_size = len(X_scaled) - train_size # Not strictly needed

    X_train = X_scaled[:train_size]
    y_train = y.iloc[:train_size].values # Ensure y_train is a NumPy array
    X_val = X_scaled[train_size:]
    y_val = y.iloc[train_size:].values   # Ensure y_val is a NumPy array
    print(f"Step 4/7: Data split into training ({len(X_train)} samples) and validation ({len(X_val)} samples) sets.")

    # 5. Reshape the input data for LSTMs (samples, timesteps, features)
    # For this version, timesteps = 1
    X_train_reshaped = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
    X_val_reshaped = X_val.reshape((X_val.shape[0], 1, X_val.shape[1]))
    print(f"Step 5/7: Data reshaped for LSTM input. X_train shape: {X_train_reshaped.shape}, X_val shape: {X_val_reshaped.shape}")

    # 6. Save the processed data
    np.savez(output_filename,
             X_train=X_train_reshaped,
             y_train=y_train,
             X_val=X_val_reshaped,
             y_val=y_val)
    print(f"Step 6/7: Processed data saved to {output_filename}")

    print("Step 7/7: Preprocessing complete.")

if __name__ == "__main__":
    main()
