# -*- coding: utf-8 -*-
"""Task_1b_GZ_shared

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KAtPP6atjzOhCS3l4uCnuiQMhKomcuQc
"""

# First, we import necessary libraries:
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold

from google.colab import drive
import sys
import os

# Commented out IPython magic to ensure Python compatibility.
# Optional: set the directory to a folder of your Google Drive 
# A bit shaky: only execute this block once, otherwise need to disconnect runtime and refresh page

drive.mount('/content/drive', force_remount=True)

# folder path
drive_root = "/content/drive/MyDrive/Intro_to_ML/Task_1b"

# Change to the directory
print("\nColab: Changing directory to ", drive_root)
# %cd $drive_root

def transform_data(X):
    """
    This function transforms the 5 input features of matrix X (x_i denoting the i-th component of X) 
    into 21 new features phi(X) in the following manner:
    5 linear features: phi_1(X) = x_1, phi_2(X) = x_2, phi_3(X) = x_3, phi_4(X) = x_4, phi_5(X) = x_5
    5 quadratic features: phi_6(X) = x_1^2, phi_7(X) = x_2^2, phi_8(X) = x_3^2, phi_9(X) = x_4^2, phi_10(X) = x_5^2
    5 exponential features: phi_11(X) = exp(x_1), phi_12(X) = exp(x_2), phi_13(X) = exp(x_3), phi_14(X) = exp(x_4), phi_15(X) = exp(x_5)
    5 cosine features: phi_16(X) = cos(x_1), phi_17(X) = cos(x_2), phi_18(X) = cos(x_3), phi_19(X) = cos(x_4), phi_20(X) = cos(x_5)
    1 constant features: phi_21(X)=1

    Parameters
    ----------
    X: matrix of floats, dim = (700,5), inputs with 5 features

    Returns
    ----------
    X_transformed: array of floats: dim = (700,21), transformed input with 21 features
    """
    [n,m]=np.shape(X)
    X_transformed = np.zeros((n, 21))

    i=0
    while i<21:
      # Linear
      if i in {0,1,2,3,4}:
        X_transformed[:,i] = X[:,i]
      # Quadratic
      elif i in {5,6,7,8,9}:
        X_transformed[:,i] = np.multiply(X[:,i-5], X[:,i-5])
      # Exponential
      elif i in {10,11,12,13,14}:
        X_transformed[:,i] = np.exp(X[:,i-10])
      # Cosine
      elif i in {15,16,17,18,19}:
        X_transformed[:,i] = np.cos(X[:,i-15])
      # Constant
      elif i==20:
        X_transformed[:,i] = np.ones((n, 1)).reshape(-1)
      i += 1

    assert X_transformed.shape == (n, 21)
    return X_transformed

def fit(X, y, lam):
    """
    This function receives training data points, transform them, and then fits the linear regression on this 
    transformed data. Finally, it outputs the weights of the fitted linear regression. 

    Parameters
    ----------
    X: matrix of floats, dim = (700,5), inputs with 5 features
    y: array of floats, dim = (700,), input labels)

    Returns
    ----------
    w: array of floats: dim = (21,), optimal parameters of linear regression
    """
    w = np.zeros((21,))
    model = Ridge(alpha=lam,fit_intercept=False)
    model.fit(transform_data(X),y)
    w = model.coef_

    assert w.shape == (21,)
    return w

def calculate_RMSE(w, X, y):
    """This function takes test data points (X and y), and computes the empirical RMSE of 
    predicting y from X using a linear model with weights w. 

    Parameters
    ----------
    w: array of floats: dim = (13,), optimal parameters of ridge regression 
    X: matrix of floats, dim = (15,13), inputs with 13 features
    y: array of floats, dim = (15,), input labels

    Returns
    ----------
    RMSE: float: dim = 1, RMSE value
    """
    
    RMSE = mean_squared_error(y, np.matmul(X,w), squared=False)
    
    assert np.isscalar(RMSE)
    return RMSE

def average_LR_RMSE(X, y, lambdas, n_folds):
    """
    Main cross-validation loop, implementing 10-fold CV. In every iteration (for every train-test split), the RMSE for every lambda is calculated, 
    and then averaged over iterations.
    
    Parameters
    ---------- 
    X: matrix of floats, dim = (150, 13), inputs with 13 features
    y: array of floats, dim = (150, ), input labels
    lambdas: list of floats, len = 5, values of lambda for which ridge regression is fitted and RMSE estimated
    n_folds: int, number of folds (pieces in which we split the dataset), parameter K in KFold CV
    
    Returns
    ----------
    avg_RMSE: array of floats: dim = (5,), average RMSE value for every lambda
    """
    [l] = np.shape(lambdas)
    X_trans = transform_data(X) 
    RMSE_mat = np.zeros((n_folds, len(lambdas)))

    lidx = 0
    for lam in lambdas:
        kf = KFold(n_splits=n_folds)
        count = 0
        for train, test in kf.split(X):
            w = fit(X_trans[train],y[train],lam)
            run_RMSE = calculate_RMSE(w, X_trans[test],y[test])
            RMSE_mat[count][lidx] = run_RMSE
            count+=1
        lidx+=1
    avg_RMSE = np.mean(RMSE_mat, axis=0)

    assert avg_RMSE.shape == (l,)
    return avg_RMSE

# Main function. You don't have to change this
if __name__ == "__main__":
    #### Data loading ####
    data = pd.read_csv("train.csv")
    y = data["y"].to_numpy()
    data = data.drop(columns=["Id", "y"])
    # print a few data samples
    #print(data.head())
    X = data.to_numpy()

    #### Finding optimal lambda ####
    lambdas = [42.8332, 42.8333, 42.833, 42.834]
    n_folds = 10
    avg_RMSE = average_LR_RMSE(X, y, lambdas, n_folds)
    min_index = np.argmin(avg_RMSE)
    min_value = avg_RMSE[min_index]
    lambda_opt = lambdas[min_index]

    #### The function retrieving optimal LR parameters ####
    w = fit(X, y, lambda_opt)
    # Save results in the required format
    np.savetxt("./results.csv", w, fmt="%.12f")

    print("Optimal lambda was: lambda = "+str(lambda_opt))
    print("RMSE was: "+str(min_value))

