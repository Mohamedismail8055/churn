# -*- coding: utf-8 -*-
"""Telecom_Churn_Deployment.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1M48A27d_kFwCmUuhn0m5E5GAFitDRxlP

#Telecom Customer Churn Prediction

## Importing Libraries
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from imblearn.over_sampling import SMOTE
import os

"""# Importing the dataset"""

df = pd.read_excel('Churn1.xlsx')
df.head()

# Dropping unnecessary column "Unnamed"
df=df.iloc[:,1:]

# first 5 rows of data
df.head()

# Drop the 'state' column
df = df.drop('state', axis=1)

# information of the dataset
df.info()

""" ### It gives us all columns names, it's data type. Here we can observe that two features daycharge and evening minutes are getting wrong data type. So we will convert it into correct data type."""

df['day.charge']=pd.to_numeric(df['day.charge'],errors='coerce')
df['eve.mins']=pd.to_numeric(df['eve.mins'],errors='coerce')

from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()

columns_to_encode = ['area.code', 'voice.plan', 'intl.plan', 'churn']

# Create mapping dictionaries
mapping_dict = {}

for col in columns_to_encode:
    df[col] = le.fit_transform(df[col])
    # Create a mapping dictionary for the current column
    mapping = dict(zip(le.classes_, le.transform(le.classes_)))
    mapping_dict[col] = mapping

# Print the mapping dictionaries
mapping_dict

df.isnull().sum()

# median imputation

# we can fill null values by mean but we have outliers so median is best prefered.

df['day.charge']=df['day.charge'].fillna(df['day.charge'].median())
df['eve.mins']=df['eve.mins'].fillna(df['eve.mins'].median())

df.isnull().sum()

df.info()

# Handling imbalance with SMOTE
X = df.drop(columns=['churn'])
y = df['churn']
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

# Recreate DataFrame
df_resampled = pd.DataFrame(X_resampled, columns=X.columns)
df_resampled['churn'] = y_resampled

# description of the dataset
df_resampled.describe()

# varaince of all numerical columns
df.var(numeric_only=True)

# skewness
df.skew(numeric_only=True)

# kurtosis
df.kurt(numeric_only=True)

# checking for duplicates if there is any
df.duplicated().any()

df[df.duplicated(keep=False)]

"""### We can see the mean values of each column grouped by the churn."""

# two way tab
pd.crosstab(df['churn'],df['intl.plan'],margins=True)

# Voice plan
pd.crosstab(df['churn'],df['voice.plan'],margins=True)

# Customer service calls
pd.crosstab(df['churn'],df["customer.calls"],margins=True)

numerical_cols = df_resampled.select_dtypes(include=np.number).columns
num_columns = len(numerical_cols)

plt.figure(figsize=(20, 20))

# Calculate rows and columns to fit all subplots
rows = (num_columns // 4) + (num_columns % 4 > 0)

for i, col in enumerate(numerical_cols):
    plt.subplot(rows, 4, i + 1)  # Adjust grid layout as needed
    sns.boxplot(y=df[col])
    plt.title(col)
    plt.tight_layout()

plt.show()

# Find columns in df_resampled with only 0s and 1s
binary_cols = []
for col in df_resampled.columns:
  if set(df_resampled[col].unique()) == {0, 1}:
    binary_cols.append(col)
print("Columns with only 0 and 1:", binary_cols)

# Outlier removal using 3-sigma rule, excluding 'voice.plan', 'intl.plan', 'churn'
for col in df_resampled.select_dtypes(include=np.number).columns:
    if col != ('voice.plan', 'intl.plan', 'churn'):  # Exclude 'voice.plan', 'intl.plan', 'churn' column. Even if its not excluded also, no issue. Since boolean columns are not considered.
        mean = df_resampled[col].mean()
        std = df_resampled[col].std()
        df_resampled = df_resampled[(df_resampled[col] > mean - 3 * std) & (df_resampled[col] < mean + 3 * std)]

plt.figure(figsize=(20, 15))  # Adjust figure size as needed
num_columns = df_resampled.select_dtypes(include=np.number).shape[1]

# Calculate rows and columns to fit all subplots
rows = (num_columns // 3) + (num_columns % 3 > 0)

for i, col in enumerate(df_resampled.select_dtypes(include=np.number).columns):
    plt.subplot(rows, 3, i + 1)  # Adjust grid layout as needed
    sns.boxplot(y=df_resampled[col])
    plt.title(col)

plt.tight_layout()
plt.show()

df_resampled  # dataframe with outliers removed

"""## Data Visualization
### To show the Percentage of churn using pie chart

* Before resampling
"""

plt.pie(df['churn'].value_counts(), labels = df['churn'].unique(), autopct='%1.1f%%',startangle=90,
         explode=(0.3,0),
         radius=1.2,
         textprops={'fontsize': 10, 'color':'k'},
         wedgeprops={'linewidth': 1, 'edgecolor': 'white'},
         center=(0,0),
         shadow=True,
         colors= sns.color_palette('Set2'))
plt.title("Before resampling")
plt.show()

"""* After resampling"""

plt.pie(df_resampled['churn'].value_counts(), labels = df_resampled['churn'].unique(), autopct='%1.1f%%',startangle=90,
         explode=(0.3,0),
         radius=1.2,
         textprops={'fontsize': 10, 'color':'k'},
         wedgeprops={'linewidth': 1, 'edgecolor': 'white'},
         center=(0,0),
         shadow=True,
         colors= sns.color_palette('Set2'))
plt.title("After resampling")
plt.show()

"""###  To show the Percentage of Charges during different time of the day using Pie Char"""

plt.figure(figsize = (5,5))
 #sns.set(rc={'figure.figsize':(3,4)})
 charge = np.array([df_resampled['intl.charge'].sum(), df_resampled['day.charge'].sum(), df_resampled['eve.charge'].sum(), df_resampled['night.charge'].sum()])
 plt.pie(charge,
         labels = ['International charge', 'Day charge', 'Evening charge','Night charge'],
         autopct= "%1.1f%%",
         explode =(0.2,0,0,0),
         radius=1.2,
         textprops={'fontsize': 10, 'color': '#5CD9BB'},
         shadow=True,
         colors =sns.color_palette("viridis"))
 plt.title("Total charge")
 plt.show()

sns.pairplot(df_resampled,hue='churn')

"""### In pairplot we can visualise the highly correlared columns like intl.mins &intl.charge and day.mins & day charge"""

sns.catplot(
    y='night.calls',
    x='intl.plan',
    hue='churn',  # Different colors for Churn status
    data=df_resampled,
    kind='violin',
    split=True )

plt.figure(figsize = (5,5))
pal = sns.color_palette("pastel")
sns.catplot(x="area.code", y="day.charge", data=df_resampled, kind='bar',hue='churn')
plt.xticks(rotation = 0, fontsize = 10)
plt.show()

plt.figure(figsize = (2, 2))
 sns.catplot(
    y="area.code",
    data=df_resampled,
    kind="count",
    hue="churn",
    col="voice.plan"  # Creates separate plots for each voice mail plan status
)
 plt.show()

#Correlation
df_resampled.corr(numeric_only=True)

plt.figure(figsize=(18,15))
 corr = df_resampled.corr(numeric_only=True)
 sns.heatmap(corr, annot=True,fmt ="0.2f")
 plt.show()

"""### Light color shows that they are strongly correlated"""

# Histogram for each variable
df_resampled.hist(figsize=(16, 20), bins=50, xlabelsize=8, ylabelsize=8)

"""# Insights
 Almost every features are weakly correlated.
 Almost all features are normally distributed except voice message, init calls, customer calls.
 International minutes and International charges, night minutes and night charges, Evening
 minutes and Evening charges are strongly positively correlated. As minutes of the talking
 time increases, charges also increases.

# t-sne visualisation
"""

# t-SNE visualization
tsne = TSNE(n_components=2, perplexity=30, random_state=42)
X_embedded = tsne.fit_transform(StandardScaler().fit_transform(X_resampled))
tsne_df = pd.DataFrame(X_embedded, columns=['TSNE1', 'TSNE2'])
tsne_df['churn'] = y_resampled.values

plt.figure(figsize=(10, 6))
sns.scatterplot(x='TSNE1', y='TSNE2', hue='churn', palette='coolwarm', data=tsne_df)
plt.title("t-SNE Visualization of Customer Data")
plt.show()

# Collinearity check using correlation matrix
plt.figure(figsize=(12, 8))
sns.heatmap(df_resampled.corr(), cmap='coolwarm', annot=True)
plt.title("Feature Correlation Matrix")
plt.show()

"""#Mutual Information Score"""

# Mutual Information score, alternative for PPS matrix using correlation
def calculate_mutual_information(df, target):
    from sklearn.feature_selection import mutual_info_classif
    X = df.drop(columns=[target])
    y = df[target]
    mi = mutual_info_classif(X, y, discrete_features='auto')
    return pd.Series(mi, index=X.columns)

mutual_info_scores = calculate_mutual_information(df_resampled, 'churn')
print("Top features based on mutual information:")
print(mutual_info_scores.sort_values(ascending=False).head(10))

# The mutual information scores are printed in descending order, showing the top 10 features based on mutual information.

"""**The above code prints the top 10 features based on their mutual information scores with the target variable 'churn'. These features are considered the most informative for predicting whether a customer will churn.**

# Non-Linear Pattern for finding top predicting features
"""

# Detect non-linear patterns using Random Forest
rf = RandomForestClassifier(random_state=42)
rf.fit(X_resampled, y_resampled)
feature_importances = pd.Series(rf.feature_importances_, index=X.columns)
print("Top features with non-linear patterns:")
print(feature_importances.sort_values(ascending=False).head(10))

from sklearn.preprocessing import MinMaxScaler

numerical_features = df_resampled.select_dtypes(include=np.number).columns
scaler = MinMaxScaler()
normalised_data = scaler.fit_transform(df_resampled[numerical_features])
normalised_df = pd.DataFrame(normalised_data, columns=numerical_features, index=df_resampled.index)
normalised_df.head()

X=normalised_df.iloc[:,:-1]
y=normalised_df.iloc[:,-1]

"""# Recursive Feature Elimination to find the top churn predicting features"""

X_rfe = normalised_df.drop(columns=['churn'])
y_rfe = normalised_df['churn']

# Recursive Feature Elimination with Logistic Regression
log_reg = LogisticRegression(max_iter=1000)
rfe = RFE(log_reg, n_features_to_select=10)
rfe.fit(X, y)
selected_features = X_rfe.columns[rfe.support_]
print("Selected features from RFE:")
print(selected_features)

"""These features have been identified by RFE as the most relevant for your predictive model, potentially improving its accuracy and performance.

# Top features based on
1. **mutual information:**
intl.charge   :   0.429700,
intl.mins     :   0.426242,
night.charge  :    0.221482,
day.charge    :    0.144500,
day.mins      :    0.129421,
eve.charge    :    0.100247,
eve.mins      :    0.066443,
night.mins    :    0.054718,
voice.plan    :    0.050531,
voice.messages:    0.032908


2. **non-linear patterns:**
 day.charge     :   0.141592,
 day.mins       :   0.125520,
 customer.calls :   0.095396,
 eve.mins       :   0.061251,
 eve.charge     :   0.059580,
 voice.messages :   0.053899,
 voice.plan     :   0.052052,
 night.charge   :   0.045311,
 intl.charge    :   0.045038,
 night.mins     :   0.043922

3. **RFE:**
 area.code, voice.plan, voice.messages, intl.mins, intl.calls,
       day.mins, day.charge, eve.charge, night.charge,
       customer.calls
"""

# Splitting into X and y based on RFE most relevant features, although i can choose mutual info score or nonlinear pattern, i selected rfe for feature selection
X_rfe_selected = normalised_df[['area.code', 'voice.plan', 'voice.messages', 'intl.mins', 'intl.calls',
       'day.mins', 'day.charge', 'eve.charge', 'night.charge',
       'customer.calls']]
y = normalised_df['churn']

X_rfe_selected.head()

y.head()

X_rfe_selected.shape,y.shape

"""X TRAIN AND Y TRAIN SPLITTING"""

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_rfe_selected, y, test_size=0.2, random_state=42)



"""# **MODEL BUILDING**

LOGISTIC REGRESSION
"""

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Initialize and train the logistic regression model
logreg = LogisticRegression(max_iter=1000)  # Increased max_iter for convergence
logreg.fit(X_train, y_train)

# Make predictions on the test set
y_pred = logreg.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy}")
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))

"""ROC CURVE AND ROC SCORE"""

import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, roc_auc_score

# Get predicted probabilities for the positive class
y_probs = logreg.predict_proba(X_test)[:, 1]

# Compute the ROC curve
fpr, tpr, _ = roc_curve(y_test, y_probs)

# Compute the AUC score
roc_auc = roc_auc_score(y_test, y_probs)

# Print AUC score
print(f"ROC AUC Score: {roc_auc:.4f}")

# Plot the ROC curve
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', lw=2, label=f'ROC Curve (AUC = {roc_auc:.4f})')
plt.plot([0, 1], [0, 1], color='gray', linestyle='--')  # Diagonal line for random guessing
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve for Logistic Regression')
plt.legend(loc='lower right')
plt.show()

"""XGBOOST MODEL"""

import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Initialize and train the XGBoost Classifier
xgb_classifier = xgb.XGBClassifier(random_state=42)
xgb_classifier.fit(X_train, y_train)

# Make predictions on the test set
y_pred_xgb = xgb_classifier.predict(X_test)

# Evaluate the XGBoost model
accuracy_xgb = accuracy_score(y_test, y_pred_xgb)
print(f"XGBoost Accuracy: {accuracy_xgb}")
print(classification_report(y_test, y_pred_xgb))
print(confusion_matrix(y_test, y_pred_xgb))

"""TUNED XGBOOST MODEL"""

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Expanded parameter grid
param_grid_xgb = {
    'n_estimators': [50, 100, 200, 300],
    'learning_rate': [0.001, 0.01, 0.1, 0.2, 0.3],
    'max_depth': [3, 5, 7, 9],
    'subsample': [0.7, 0.8, 0.9, 1.0]
}

# Use RandomizedSearchCV for efficiency
random_search_xgb = RandomizedSearchCV(
    estimator=xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42),
    param_distributions=param_grid_xgb,
    n_iter=50,  # Adjust for more trials
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=2,
    random_state=42
)

# Fit the model
random_search_xgb.fit(X_train, y_train)

# Get best parameters
best_params_xgb = random_search_xgb.best_params_
best_score_xgb = random_search_xgb.best_score_

print(f"Best hyperparameters for XGBoost: {best_params_xgb}")
print(f"Best cross-validation score for XGBoost: {best_score_xgb}")

# Train final model with best parameters
best_xgb_classifier = xgb.XGBClassifier(**best_params_xgb, use_label_encoder=False, eval_metric='mlogloss', random_state=42)
best_xgb_classifier.fit(X_train, y_train)

# Evaluate on test data
y_pred_best_xgb = best_xgb_classifier.predict(X_test)
accuracy_best_xgb = accuracy_score(y_test, y_pred_best_xgb)

print(f"XGBoost Accuracy (with best hyperparameters): {accuracy_best_xgb}")
print(classification_report(y_test, y_pred_best_xgb))
print(confusion_matrix(y_test, y_pred_best_xgb))


"""GRADIENT BOOSTING MODEL"""

from sklearn.ensemble import GradientBoostingClassifier

# Initialize and train the Gradient Boosting Classifier
gb_classifier = GradientBoostingClassifier(random_state=42)
gb_classifier.fit(X_train, y_train)

# Make predictions on the test set
y_pred_gb = gb_classifier.predict(X_test)

# Evaluate the Gradient Boosting model
accuracy_gb = accuracy_score(y_test, y_pred_gb)
print(f"Gradient Boosting Accuracy: {accuracy_gb}")
print(classification_report(y_test, y_pred_gb))
print(confusion_matrix(y_test, y_pred_gb))

"""TUNED GRADIENT BOOSTING MODEL"""

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Define hyperparameter grid
param_grid_gb = {
    'n_estimators': [50, 100, 200, 300, 500],  # Number of boosting rounds
    'learning_rate': [0.01, 0.05, 0.1, 0.2, 0.3],  # Step size
    'max_depth': [3, 5, 7, 9],  # Tree depth
    'min_samples_split': [2, 5, 10, 15],  # Min samples to split a node
    'min_samples_leaf': [1, 2, 4, 6],  # Min samples per leaf
    'subsample': [0.7, 0.8, 0.9, 1.0],  # Fraction of samples per iteration
    'max_features': ['sqrt', 'log2', None]  # Features per split
}

# Initialize RandomizedSearchCV
random_search_gb = RandomizedSearchCV(
    estimator=GradientBoostingClassifier(random_state=42),
    param_distributions=param_grid_gb,
    n_iter=50,  # Adjust for more trials
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=2,
    random_state=42
)

# Fit the model
random_search_gb.fit(X_train, y_train)

# Get best parameters and score
best_params_gb = random_search_gb.best_params_
best_score_gb = random_search_gb.best_score_

print(f"Best hyperparameters for Gradient Boosting: {best_params_gb}")
print(f"Best cross-validation score: {best_score_gb}")

# Train final model with best parameters
best_gb_classifier = GradientBoostingClassifier(**best_params_gb, random_state=42)
best_gb_classifier.fit(X_train, y_train)

# Evaluate on test data
y_pred_best_gb = best_gb_classifier.predict(X_test)
accuracy_best_gb = accuracy_score(y_test, y_pred_best_gb)

print(f"Gradient Boosting Accuracy (with best hyperparameters): {accuracy_best_gb}")
print(classification_report(y_test, y_pred_best_gb))
print(confusion_matrix(y_test, y_pred_best_gb))

import pandas as pd

data = {
    'Model': ['Logistic Regression', 'XGBoost', 'XGBoost (with best hyperparameters)', 'Decision Tree', 'Decision Tree (with best hyperparameters)', 'Random Forest (Default Parameters)', 'Random Forest (with best hyperparameters)', 'Gradient Boosting', 'Gradient Boosting (with best hyperparameters)'],
    'Accuracy': [accuracy, accuracy_xgb, accuracy_best_xgb, accuracy_dtree, accuracy_best_dtree, accuracy_rf, accuracy_best_rf, accuracy_gb, accuracy_best_gb]
}

df = pd.DataFrame(data)
df

y_pred_gb

!pip install streamlit
!pip install pandas
!pip install pickle
!pip install numpy
!pip install xgboost


import streamlit as st
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
import os

# Load dataset
def load_data():
    df = pd.read_excel("Churn1.xlsx")
    df = df.iloc[:, 1:]  # Drop index column
    df = df.drop("state", axis=1)  # Drop categorical column for simplicity
    return df

# Load model if available, otherwise train and save
def get_model(model_name):
    if os.path.exists(f"{model_name}.pkl"):
        with open(f"{model_name}.pkl", "rb") as f:
            return pickle.load(f)
    else:
        return train_models()[model_name]

# Train and save models
def train_models():
    df = load_data()
    X = df.drop("churn", axis=1)
    y = LabelEncoder().fit_transform(df["churn"])  # Encode target variable
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        "Tuned gradient boosting( highest accuracy)": GradientBoostingClassifier(),
        "LogisticRegression": LogisticRegression(max_iter=1000),
        "Tuned xgboost": xgb()
    }

    for name, model in models.items():
        model.fit(X_train, y_train)
        with open(f"{name}.pkl", "wb") as f:
            pickle.dump(model, f)

    return models

# Streamlit UI
st.title("Telecom Churn Prediction")
st.write("Upload a dataset to predict customer churn.")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv", "xlsx"])
if uploaded_file:
    if uploaded_file.name.endswith("xlsx"):
        data = pd.read_excel(uploaded_file)
    else:
        data = pd.read_csv(uploaded_file)
    st.write("Uploaded Data:")
    st.dataframe(data.head())

    model_choice = st.selectbox("Select Model", ["RandomForest", "LogisticRegression", "DecisionTree"])
    model = get_model(model_choice)

    predictions = model.predict(data)
    data["Churn Prediction"] = predictions
    st.write("Prediction Results:")
    st.dataframe(data)

    st.download_button("Download Predictions", data.to_csv(index=False), "predictions.csv")

!pip install streamlit pandas scikit-learn

!streamlit run app.py







































