import pandas as pd
import numpy as np
from sklearn import preprocessing
import matplotlib.pyplot as plt
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics


class machinesLogreg:
    def __init__(self):
        #load data
        self.path=os.getcwd()+'/exam_files/predictive_maintenance.csv'
        self.data=pd.read_csv(self.path)
        self.X=[]
        self.y=[]

        # instantiate the model (using the default parameters)
        self.model=LogisticRegression(random_state=16)
        #split dataset in features and target variable
        feature_cols = ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']
        self.X = self.data[feature_cols] # Features
        self.y = self.data['Target'] # Target variable

        #split X and y into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.25, random_state=16)
        # fit the model with data
        self.model=self.model.fit(X_train.values, y_train)

    def predict(self,test):
        return self.model.predict(test)

""" model=machinesLogreg()
print(model.predict([[290,305,1100,10,0]])) """

""" cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
print(X_test.shape) """