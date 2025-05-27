import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt

def main():
    processed_data_filename = 'processed_data.npz'
    model_filename = 'lstm_model.h5'
    plot_output_filename = 'return_curves.png'

    # 1. Load preprocessed validation data
    try:
        data = np.load(processed_data_filename)
        X_val = data['X_val']
        y_val_actual = data['y_val'] # Actual returns
        print(f"Step 1/6: Validation data (X_val, y_val_actual) loaded from {processed_data_filename}")
    except FileNotFoundError:
        print(f"Error: Processed data file {processed_data_filename} not found. Please run preprocessing first.")
        return
    except KeyError as e:
        print(f"Error: Missing key {e} in {processed_data_filename}. Ensure the file is correctly formatted.")
        return

    # 2. Load the trained LSTM model
    try:
        model = load_model(model_filename)
        print(f"Step 2/6: Trained LSTM model loaded successfully from {model_filename}")
    except Exception as e:
        print(f"Error loading model {model_filename}: {e}")
        return

    # 3. Make predictions on the validation data
    y_val_predicted = model.predict(X_val)
    y_val_predicted = y_val_predicted.flatten() # Ensure predictions are 1D
    print(f"Step 3/6: Predictions made on X_val. Predicted shape: {y_val_predicted.shape}")

    # 4. Calculate cumulative returns
    cumulative_actual_returns = np.cumsum(y_val_actual)
    cumulative_predicted_returns = np.cumsum(y_val_predicted)
    print("Step 4/6: Cumulative actual and predicted returns calculated.")

    # 5. Generate and save the plot
    plt.figure(figsize=(12, 6))
    plt.plot(cumulative_actual_returns, label='Cumulative Actual Returns', color='blue')
    plt.plot(cumulative_predicted_returns, label='Cumulative Predicted Returns', color='red', linestyle='--')

    plt.title('Cumulative Actual vs. Predicted Returns on Validation Data')
    plt.xlabel('Time / Sample Index')
    plt.ylabel('Cumulative Returns')
    plt.legend()
    plt.grid(True)

    try:
        plt.savefig(plot_output_filename)
        print(f"Step 5/6: Plot saved successfully as {plot_output_filename}")
    except Exception as e:
        print(f"Error saving plot: {e}")
        return

    print(f"Step 6/6: Visualization script complete. Plot saved to {plot_output_filename}")

if __name__ == "__main__":
    # Suppress TensorFlow INFO and WARNING messages for cleaner output
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
    # Set Matplotlib backend to Agg to avoid issues in environments without a display server
    import matplotlib
    matplotlib.use('Agg')
    main()
