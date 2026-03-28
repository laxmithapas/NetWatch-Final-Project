import pandas as pd
import numpy as np
import os
import joblib
import optuna
import mlflow
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_curve, auc
import shap

def load_and_preprocess(filepath):
    df = pd.read_csv(filepath)
    print("Initial shape:", df.shape)

    # 1. Clean nulls, duplicates
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    print("Cleaned shape:", df.shape)

    # Convert Label to binary class for simplistic plotting (Anomalous = 1, Benign = 0)
    df['BinaryLabel'] = df['Label'].apply(lambda x: 0 if x == 'Benign' else 1)

    # Separate features and target
    drop_cols = ['Timestamp', 'Source IP', 'Destination IP', 'Label', 'BinaryLabel']
    X = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')
    y_binary = df['BinaryLabel']

    # Encode categoricals if any left (Protocol is numeric here, but keeping for standard sake)
    # 2. Normalize numerical features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

    return train_test_split(X_scaled, y_binary, test_size=0.3, stratify=y_binary, random_state=42), scaler, X.columns

def train_rf(X_train, y_train):
    print("Training Random Forest baseline...")
    rf = RandomForestClassifier(n_estimators=50, random_state=42)
    rf.fit(X_train, y_train)
    return rf

def optimize_xgb(X_train, y_train, X_test, y_test):
    print("Optimizing XGBoost with Optuna...")
    def objective(trial):
        param = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 150),
            'max_depth': trial.suggest_int('max_depth', 3, 7),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.2),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0)
        }
        model = XGBClassifier(**param, use_label_encoder=False, eval_metric='logloss', random_state=42)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        return f1_score(y_test, preds)

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=5) # 5 for fast demo execution

    best_xgb = XGBClassifier(**study.best_params, use_label_encoder=False, eval_metric='logloss', random_state=42)
    best_xgb.fit(X_train, y_train)
    return best_xgb, study.best_params

def generate_plots(model, X_test, y_test, model_name, plot_dir):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f'{model_name} Confusion Matrix')
    plt.ylabel('True')
    plt.xlabel('Predicted')
    plt.savefig(os.path.join(plot_dir, f'{model_name}_cm.png'))
    plt.close()

    # ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    plt.figure(figsize=(6,5))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.title(f'{model_name} ROC Curve')
    plt.legend(loc='lower right')
    plt.savefig(os.path.join(plot_dir, f'{model_name}_roc.png'))
    plt.close()

def evaluate(model, X_test, y_test):
    preds = model.predict(X_test)
    return {
        'accuracy': accuracy_score(y_test, preds),
        'precision': precision_score(y_test, preds),
        'recall': recall_score(y_test, preds),
        'f1': f1_score(y_test, preds)
    }

def main():
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, "sample_dataset.csv")
    models_dir = os.path.join(base_dir, "models")
    plots_dir = os.path.join(base_dir, "plots")
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)

    uri = "file:///" + os.path.join(base_dir, 'mlruns').replace('\\', '/')
    mlflow.set_tracking_uri(uri)
    mlflow.set_experiment("NetWatch_Intrusion_Detection")

    (X_train, X_test, y_train, y_test), scaler, cols = load_and_preprocess(data_path)
    joblib.dump(scaler, os.path.join(models_dir, "scaler.pkl"))
    joblib.dump(list(cols), os.path.join(models_dir, "feature_names.pkl"))

    with mlflow.start_run(run_name="RandomForest_Baseline"):
        rf = train_rf(X_train, y_train)
        rf_metrics = evaluate(rf, X_test, y_test)
        mlflow.log_metrics({f"rf_{k}": v for k, v in rf_metrics.items()})
        generate_plots(rf, X_test, y_test, "RandomForest", plots_dir)
        joblib.dump(rf, os.path.join(models_dir, "rf_model.pkl"))

    with mlflow.start_run(run_name="XGBoost_Optimized"):
        xgb, best_params = optimize_xgb(X_train, y_train, X_test, y_test)
        mlflow.log_params(best_params)
        xgb_metrics = evaluate(xgb, X_test, y_test)
        mlflow.log_metrics({f"xgb_{k}": v for k, v in xgb_metrics.items()})
        generate_plots(xgb, X_test, y_test, "XGBoost", plots_dir)
        joblib.dump(xgb, os.path.join(models_dir, "xgb_model.pkl"))
        
        # Explainability via SHAP for XGBoost
        print("Generating SHAP plots for XGBoost explainability...")
        explainer = shap.Explainer(xgb)
        # using a small subset for speed
        shap_values = explainer(X_test.iloc[:200])
        shap.summary_plot(shap_values, X_test.iloc[:200], show=False)
        plt.savefig(os.path.join(plots_dir, "shap_summary.png"), bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    main()
