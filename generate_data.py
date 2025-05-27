import pandas as pd
import numpy as np
import datetime

def generate_autocorrelated_data(num_rows, num_cols, correlation_factor=0.5):
    """
    Generates a 2D array of autocorrelated random data.
    """
    data = np.random.randn(num_rows, num_cols)
    for col in range(num_cols):
        for row in range(1, num_rows):
            data[row, col] = (correlation_factor * data[row-1, col] +
                              (1 - correlation_factor) * np.random.randn())
    return data

def main():
    num_rows = 500
    start_date = datetime.date(2022, 1, 1)

    # Generate dates
    dates = [start_date + datetime.timedelta(days=i) for i in range(num_rows)]

    # Generate factor data
    factor_data = generate_autocorrelated_data(num_rows, 3, correlation_factor=0.6)
    factor1 = factor_data[:, 0]
    factor2 = factor_data[:, 1]
    factor3 = factor_data[:, 2]

    # Generate returns
    # Assuming some linear relationship with factors + noise
    # These coefficients are arbitrary for simulation purposes
    returns = (0.5 * factor1 +
               0.3 * factor2 -
               0.2 * factor3 +
               np.random.randn(num_rows) * 0.5) # Noise component

    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'factor1': factor1,
        'factor2': factor2,
        'factor3': factor3,
        'returns': returns
    })

    # Save to CSV
    output_filename = 'simulated_data.csv'
    df.to_csv(output_filename, index=False)

    print(f"Data generation complete. Output saved to {output_filename}")

if __name__ == "__main__":
    main()
