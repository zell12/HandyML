# Importing the libraries
import pandas as pd
import numpy as np

import json

from joblib import load

from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import PolynomialFeatures

############## GENERIC FUNCTIONS ##############
def one_hot_encode(data, indices):
    
    transformer = ColumnTransformer([('one_hot_encoder', OneHotEncoder(), indices)], remainder = 'passthrough')
    data = np.array(transformer.fit_transform(data), dtype = np.float)

    # Avoiding the Dummy Variable trap
    data = data[:, 1:]
    
    return data

def feature_scaling(data, scaler = None):

    if scaler == None:
        scaler = StandardScaler()
        data = scaler.fit_transform(data)
    else:
        data = scaler.transform(data)
    
    return data, scaler

def get_parameter_value(name, parameters, default_value):

    if len(parameters) > 0:
        parameters_dictionary = parameters.split(', ')
        for parameter in parameters_dictionary:
            key_value_pair = parameter.split('=')
            key = key_value_pair[0]
            value = key_value_pair[1]
    
            if(key == name):
                return value

    return default_value

def load_sklearn_component(component_path):

    return load(component_path, mmap_mode = None)

   ############## PREDICT FUNCTIONS ##############
def predict_polynomial (X, model, degree):

    poly_reg = PolynomialFeatures(degree)
    X = poly_reg.fit_transform(X)
    return model.predict(X)
    
def predict_proba(X, model):

    return model.predict_proba(X)
    
def predict(X, model):
    
    return model.predict(X)

def process(model_path, file_path, features, target, categorical_features, problem_type, algorithm, algorithm_parameters, path, scaler_X_path, scaler_y_path, labelencoder_path):
    
    # Loading the model from disk
    model = load_sklearn_component(model_path)

    # Converting list of features columns from string to integer    
    features = list(map(int, features.split()))
    if len(categorical_features) > 0:
        categorical_features = list(map(int, categorical_features.split()))

    # Importing the dataset
    dataset = pd.read_csv(file_path)
    X = dataset.iloc[:, features].values
    
    # Encoding categorical features
    if len(categorical_features) > 0:
        # One hot encoding on X[:, indices]
        X = one_hot_encode(X, categorical_features)

    if scaler_X_path:
        scaler_X = load_sklearn_component(scaler_X_path)
        X = scaler_X.transform(X)
        
    y_pred = None
    y_proba = None

    # Making the predictions
    if algorithm == 'polynomial_regression':
        degree = int(get_parameter_value('degree', algorithm_parameters, 2))
        y_pred = predict_polynomial(X, model, degree)

    else:
        y_pred = predict(X, model)

    # Get probability when problem type is classification
    if problem_type == 'classification':
        y_proba = predict_proba(X, model)
        y_proba = np.amax(y_proba, 1)
        y_proba = y_proba * 100
        y_proba = y_proba.tolist()
    
    # Inverse scaling on target if necessary
    if scaler_y_path:
        scaler_y = load_sklearn_component(scaler_y_path)
        y_pred = scaler_y.inverse_transform(y_pred)        
    
    # Inverse label encoding on target if necessary
    if labelencoder_path:
        labelencoder = load_sklearn_component(labelencoder_path)
        y_pred = labelencoder.inverse_transform(y_pred)
        
    y_pred = y_pred.tolist()

    json_object = {
        "y_pred": y_pred,
        "y_proba": y_proba
    }
    json_string = json.dumps(json_object)
    
    return json_string
   
if __name__ == '__main__':
    
    model = ''
    file = ''
    features = ''
    categorical_features = ''
    target = ''
    
    # classification, regression
    problem_type = 'regression'
    
    # linear_regression, polynomial_regression, support_vector_regression, decision_tree_regression, random_forest_regression
    # logistic_regression, knn, svm, kernel_svm, naive_bayes, decision_tree_classification, random_forest_classification
    algorithm = 'linear_regression'
    algorithm_parameters = ''

    path = ''

    scaler_X = ''
    scaler_y = ''
    labelencoder = ''
    
    result = process(model, file, features, target, categorical_features, problem_type, algorithm, algorithm_parameters, path, scaler_X, scaler_y, labelencoder)