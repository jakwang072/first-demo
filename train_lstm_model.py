import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

def main():
    processed_data_filename = 'processed_data.npz'
    model_output_filename = 'lstm_model.h5'

    # 1. Load preprocessed data
    try:
        data = np.load(processed_data_filename)
        X_train = data['X_train']
        y_train = data['y_train']
        X_val = data['X_val']
        y_val = data['y_val']
        print(f"Step 1/6: Data loaded successfully from {processed_data_filename}")
    except FileNotFoundError:
        print(f"Error: Processed data file {processed_data_filename} not found. Please run preprocessing first.")
        return
    except KeyError as e:
        print(f"Error: Missing key {e} in {processed_data_filename}. Ensure the file is correctly formatted.")
        return

    # Infer input_shape from loaded data
    if X_train.ndim != 3 or X_train.shape[1] != 1:
        print(f"Error: X_train shape {X_train.shape} is not suitable for LSTM (expected samples, 1, features).")
        return
    input_shape = (X_train.shape[1], X_train.shape[2]) # (timesteps, features)

    # 2. Define LSTM model architecture
    model = Sequential([
        LSTM(64, activation='relu', input_shape=input_shape, name='lstm_layer'),
        Dense(1, name='output_layer')
    ])
    print("Step 2/6: LSTM model architecture defined.")

    # 3. Compile the model
    model.compile(optimizer='adam', loss='mean_squared_error')
    print("Step 3/6: Model compiled with 'adam' optimizer and 'mean_squared_error' loss.")

    # Print model summary
    print("\nModel Summary:")
    model.summary()
    print("\n")

    # 4. Train the model
    epochs = 50
    batch_size = 32
    print(f"Step 4/6: Starting model training for {epochs} epochs with batch size {batch_size}...")
    history = model.fit(X_train, y_train,
                        epochs=epochs,
                        batch_size=batch_size,
                        validation_data=(X_val, y_val),
                        verbose=1) # verbose=1 to show progress
    print("Model training complete.")

    # 5. Save the trained model
    model.save(model_output_filename)
    print(f"Step 5/6: Trained model saved to {model_output_filename}")

    print("Step 6/6: Model training and saving process complete.")

if __name__ == "__main__":
    # Suppress TensorFlow INFO and WARNING messages for cleaner output
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
    main()
