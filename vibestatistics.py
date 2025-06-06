import pandas as pd
import re
from scipy.stats import ttest_rel, wilcoxon

def load_and_sort_csv(filepath):
    """
    Load a CSV file, normalize IMU IDs (e.g., imu_104_0 to imu_105_1),
    sort, separate by intervention type, and compute grouped averages.

    Parameters:
        filepath (str): Path to the CSV file.

    Returns:
        tuple: (df_no_intervention_avg, df_yes_intervention_avg)
    """
    try:
        df = pd.read_csv(filepath)

        # Normalize IMU IDs: treat imu_104_0 and imu_105_1 as the same
        df['csv_filename'] = df['csv_filename'].replace({
            'imu_104_0': 'imu_105_1',
            'imu_105_1': 'imu_105_1'  # Explicitly keep same
        })

        # Extract numeric part of patient_id for sorting
        df['patient_id_num'] = df['patient_id'].apply(lambda x: int(re.search(r'\d+', x).group()))

        # Sort data
        sorted_df = df.sort_values(by=['patient_id_num', 'csv_filename'])
        sorted_df.drop(columns=['patient_id_num'], inplace=True)

        # Define columns to average
        avg_columns = [
            'step_duration_s', 'max_acc_ax_upright', 'time_to_max_acc_ax_upright',
            'max_acc_ay_upright', 'time_to_max_acc_ay_upright', 'max_acc_az_upright',
            'time_to_max_acc_az_upright', 'max_ang_vel_gx_upright', 'time_to_max_ang_vel_gx_upright',
            'max_ang_vel_gy_upright', 'time_to_max_ang_vel_gy_upright', 'max_ang_vel_gz_upright',
            'time_to_max_ang_vel_gz_upright'
        ]

        # Group and average
        grouped_df = sorted_df.groupby(
            ['patient_id', 'intervention_type', 'csv_filename']
        )[avg_columns].mean().reset_index()

        # Add numeric patient ID for sorting again
        grouped_df['patient_id_num'] = grouped_df['patient_id'].apply(lambda x: int(re.search(r'\d+', x).group()))

        # Separate by intervention type
        df_no = grouped_df[grouped_df['intervention_type'] == 'no'].sort_values(by=['patient_id_num', 'csv_filename']).drop(columns=['patient_id_num'])
        df_yes = grouped_df[grouped_df['intervention_type'] == 'yes'].sort_values(by=['patient_id_num', 'csv_filename']).drop(columns=['patient_id_num'])

        return df_no, df_yes

    except Exception as e:
        print(f"Error loading or processing the CSV: {e}")
        return None, None

def compare_intervention_effects(df_no, df_yes):
    """
    Perform paired statistical tests (ttest or Wilcoxon) on metrics between
    'no' and 'yes' intervention groups for the same patient and IMU.

    Parameters:
        df_no (pd.DataFrame): DataFrame for 'no' intervention.
        df_yes (pd.DataFrame): DataFrame for 'yes' intervention.

    Returns:
        pd.DataFrame: Test results including p-values and significance flags.
    """
    metrics = [
        'step_duration_s', 'max_acc_ax_upright', 'time_to_max_acc_ax_upright',
        'max_acc_ay_upright', 'time_to_max_acc_ay_upright', 'max_acc_az_upright',
        'time_to_max_acc_az_upright', 'max_ang_vel_gx_upright', 'time_to_max_ang_vel_gx_upright',
        'max_ang_vel_gy_upright', 'time_to_max_ang_vel_gy_upright', 'max_ang_vel_gz_upright',
        'time_to_max_ang_vel_gz_upright'
    ]

    results = []

    for metric in metrics:
        combined = pd.merge(
            df_no[['patient_id', 'csv_filename', metric]],
            df_yes[['patient_id', 'csv_filename', metric]],
            on=['patient_id', 'csv_filename'],
            suffixes=('_no', '_yes')
        )

        if len(combined) < 2:
            results.append({
                'metric': metric,
                'test': 'insufficient data',
                'p_value': None,
                'significant (p < 0.05)': None
            })
            continue

        try:
            stat, p = ttest_rel(combined[f"{metric}_no"], combined[f"{metric}_yes"])
            test_used = 'ttest_rel'
        except Exception:
            try:
                stat, p = wilcoxon(combined[f"{metric}_no"], combined[f"{metric}_yes"])
                test_used = 'wilcoxon'
            except Exception:
                stat, p, test_used = None, None, 'test_failed'

        results.append({
            'metric': metric,
            'test': test_used,
            'p_value': p,
            'significant (p < 0.05)': p < 0.05 if p is not None else None
        })

    return pd.DataFrame(results)

if __name__ == "__main__":
    filepath = 'metrics_summary.csv'  # Replace with actual file path

    df_no_intervention, df_yes_intervention = load_and_sort_csv(filepath)

    if df_no_intervention is not None and df_yes_intervention is not None:
        pd.set_option('display.max_rows', None)

        # Filenames to analyze separately
        filenames = ['imu_105_0.csv', 'imu_105_1.csv']

        for filename in filenames:
            print(f"\n===== Analysis for {filename} =====")

            df_no_filtered = df_no_intervention[df_no_intervention['csv_filename'] == filename]
            df_yes_filtered = df_yes_intervention[df_yes_intervention['csv_filename'] == filename]

            print("\n--- No Intervention Averages ---")
            print(df_no_filtered)

            print("\n--- Yes Intervention Averages ---")
            print(df_yes_filtered)

            print("\n--- Statistical Comparison Results ---")
            results_df = compare_intervention_effects(df_no_filtered, df_yes_filtered)
            print(results_df)

            # Optional: save results to file
            # output_filename = f'intervention_comparison_results_{filename.replace(".csv", "")}.csv'
            # results_df.to_csv(output_filename, index=False)
