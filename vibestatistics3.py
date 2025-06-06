import pandas as pd
import re
from scipy.stats import ttest_rel, wilcoxon

def compare_first_vs_last_sessions(df):
    """
    Compare first vs last session for each patient and csv_filename in the 'yes' intervention group.
    """
    df['session_dt'] = pd.to_datetime(df['session'], format='%Y-%m-%d_%H-%M-%S')
    df_yes = df[df['intervention_type'] == 'yes'].copy()

    metrics = [
        'step_duration_s',
        'avg_acc_ax_upright', 'avg_acc_ay_upright', 'avg_acc_az_upright',
        'max_acc_ax_upright', 'time_to_max_acc_ax_upright', 'min_acc_ax_upright',
        'max_acc_ay_upright', 'time_to_max_acc_ay_upright', 'min_acc_ay_upright',
        'max_acc_az_upright', 'time_to_max_acc_az_upright', 'min_acc_az_upright',
        'max_ang_vel_gx_upright', 'time_to_max_ang_vel_gx_upright',
        'max_ang_vel_gy_upright', 'time_to_max_ang_vel_gy_upright',
        'max_ang_vel_gz_upright', 'time_to_max_ang_vel_gz_upright'
    ]

    first_last_data = []

    for (pid, fname), group in df_yes.groupby(['patient_id', 'csv_filename']):
        sorted_group = group.sort_values('session_dt')
        first_row = sorted_group.iloc[0]
        last_row = sorted_group.iloc[-1]

        entry = {'patient_id': pid, 'csv_filename': fname}
        for metric in metrics:
            entry[f'{metric}_first'] = first_row[metric]
            entry[f'{metric}_last'] = last_row[metric]

        first_last_data.append(entry)

    comparison_df = pd.DataFrame(first_last_data)

    results = []
    for metric in metrics:
        col_first = f"{metric}_first"
        col_last = f"{metric}_last"
        subset = comparison_df[[col_first, col_last]].dropna()

        if len(subset) < 2:
            results.append({
                'metric': metric,
                'test': 'insufficient data',
                'p_value': None,
                'significant (p < 0.05)': None,
                'mean_first': None,
                'mean_last': None
            })
            continue

        mean_first = subset[col_first].mean()
        mean_last = subset[col_last].mean()

        try:
            stat, p = ttest_rel(subset[col_first], subset[col_last])
            test_used = 'ttest_rel'
        except:
            try:
                stat, p = wilcoxon(subset[col_first], subset[col_last])
                test_used = 'wilcoxon'
            except:
                stat, p, test_used = None, None, 'test_failed'

        results.append({
            'metric': metric,
            'test': test_used,
            'p_value': p,
            'significant (p < 0.05)': p < 0.05 if p is not None else None,
            'mean_first': mean_first,
            'mean_last': mean_last
        })

    return pd.DataFrame(results)


def load_and_sort_csv(filepath):
    """
    Load a CSV file, normalize IMU IDs, sort, separate by intervention type, and compute grouped averages.
    """
    try:
        df = pd.read_csv(filepath)

        df['csv_filename'] = df['csv_filename'].replace({
            'imu_104_0': 'imu_105_1',
            'imu_105_1': 'imu_105_1'
        })

        df['patient_id_num'] = df['patient_id'].apply(lambda x: int(re.search(r'\d+', x).group()))
        sorted_df = df.sort_values(by=['patient_id_num', 'csv_filename'])
        sorted_df.drop(columns=['patient_id_num'], inplace=True)

        avg_columns = [
            'step_duration_s',
            'avg_acc_ax_upright', 'avg_acc_ay_upright', 'avg_acc_az_upright',
            'max_acc_ax_upright', 'time_to_max_acc_ax_upright', 'min_acc_ax_upright',
            'max_acc_ay_upright', 'time_to_max_acc_ay_upright', 'min_acc_ay_upright',
            'max_acc_az_upright', 'time_to_max_acc_az_upright', 'min_acc_az_upright',
            'max_ang_vel_gx_upright', 'time_to_max_ang_vel_gx_upright',
            'max_ang_vel_gy_upright', 'time_to_max_ang_vel_gy_upright',
            'max_ang_vel_gz_upright', 'time_to_max_ang_vel_gz_upright'
        ]

        grouped_df = sorted_df.groupby(
            ['patient_id', 'intervention_type', 'csv_filename']
        )[avg_columns].mean().reset_index()

        grouped_df['patient_id_num'] = grouped_df['patient_id'].apply(lambda x: int(re.search(r'\d+', x).group()))

        df_no = grouped_df[grouped_df['intervention_type'] == 'no'].sort_values(by=['patient_id_num', 'csv_filename']).drop(columns=['patient_id_num'])
        df_yes = grouped_df[grouped_df['intervention_type'] == 'yes'].sort_values(by=['patient_id_num', 'csv_filename']).drop(columns=['patient_id_num'])

        return df_no, df_yes

    except Exception as e:
        print(f"Error loading or processing the CSV: {e}")
        return None, None


def compare_intervention_effects(df_no, df_yes):
    """
    Paired statistical tests (ttest or Wilcoxon) on metrics between
    'no' and 'yes' intervention groups for same patient and IMU.
    """
    metrics = [
        'step_duration_s',
        'avg_acc_ax_upright', 'avg_acc_ay_upright', 'avg_acc_az_upright',
        'max_acc_ax_upright', 'time_to_max_acc_ax_upright', 'min_acc_ax_upright',
        'max_acc_ay_upright', 'time_to_max_acc_ay_upright', 'min_acc_ay_upright',
        'max_acc_az_upright', 'time_to_max_acc_az_upright', 'min_acc_az_upright',
        'max_ang_vel_gx_upright', 'time_to_max_ang_vel_gx_upright',
        'max_ang_vel_gy_upright', 'time_to_max_ang_vel_gy_upright',
        'max_ang_vel_gz_upright', 'time_to_max_ang_vel_gz_upright'
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
                'significant (p < 0.05)': None,
                'mean_no': None,
                'mean_yes': None
            })
            continue

        mean_no = combined[f"{metric}_no"].mean()
        mean_yes = combined[f"{metric}_yes"].mean()

        try:
            stat, p = ttest_rel(combined[f"{metric}_no"], combined[f"{metric}_yes"])
            test_used = 'ttest_rel'
        except:
            try:
                stat, p = wilcoxon(combined[f"{metric}_no"], combined[f"{metric}_yes"])
                test_used = 'wilcoxon'
            except:
                stat, p, test_used = None, None, 'test_failed'

        results.append({
            'metric': metric,
            'test': test_used,
            'p_value': p,
            'significant (p < 0.05)': p < 0.05 if p is not None else None,
            'mean_no': mean_no,
            'mean_yes': mean_yes
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    filepath = 'metrics_summary3.csv'  # Replace with your actual CSV path

    try:
        raw_df = pd.read_csv(filepath)
        print("\n=== First vs Last Session Comparison (Intervention: Yes) ===")
        first_last_results = compare_first_vs_last_sessions(raw_df)
        print(first_last_results)
    except Exception as e:
        print(f"Error during first vs last session analysis: {e}")

    df_no_intervention, df_yes_intervention = load_and_sort_csv(filepath)

    if df_no_intervention is not None and df_yes_intervention is not None:
        pd.set_option('display.max_rows', None)
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
