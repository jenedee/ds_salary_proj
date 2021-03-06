# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 16:34:55 2022

@author: jenni
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('eda_data.csv')

#choose relevant columns
df_model = df[['avg_salary', 'Rating', 'Size', 'Type of ownership', 'Industry', 'Sector', 'Revenue', 'num_comp', 'hourly', 'employer_provided', 'job_state', 'same_state', 'python_yn', 'aws', 'spark', 'excel', 'job_simp', 'seniority', 'desc_len']]

#get dummy data
df_dum = pd.get_dummies(df_model)

#train test split
from sklearn.model_selection import train_test_split
x = df_dum.drop('avg_salary', axis = 1)
y = df_dum.avg_salary.values
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

#multiple linear regression
import statsmodels.api as sm

x_sm = x = sm.add_constant(x)
model = sm.OLS(y,x_sm)
model.fit().summary()

from sklearn.linear_model import LinearRegression, Lasso
from sklearn.model_selection import cross_val_score

lm = LinearRegression()
lm.fit(x_train, y_train)

np.mean(cross_val_score(lm,x_train,y_train, scoring = 'neg_mean_absolute_error', cv=3))

#lasso regression
lm_l = Lasso()
lm_l.fit(x_train, y_train)
np.mean(cross_val_score(lm_l, x_train,y_train, scoring = 'neg_mean_absolute_error', cv=3))

alpha = []
error = []

for i in range(1, 100):
    alpha.append(i/100)
    lml = Lasso(alpha=(i/100))
    error.append(np.mean(cross_val_score(lml, x_train,y_train, scoring = 'neg_mean_absolute_error', cv=3)))

plt.plot(alpha, error)

err = tuple(zip(alpha, error))
df_err = pd.DataFrame(err, columns = ['alpha', 'error'])
df_err[df_err.error == max(df_err.error)]

#random forest
from sklearn.ensemble import RandomForestRegressor

rf = RandomForestRegressor()
np.mean(cross_val_score(rf,x_train,y_train, scoring = 'neg_mean_absolute_error', cv=3))

#tune models GridsearchCV
from sklearn.model_selection import GridSearchCV

parameters = {'n_estimators':range(10,100,10), 'criterion':('mse', 'mae'), 'max_features':('auto', 'sqrt', 'log2')}

gs = GridSearchCV(rf,parameters,scoring='neg_mean_absolute_error', cv=3)
gs.fit(x_train,y_train)

gs.best_score_
gs.best_estimator_

#test ensembles
tpred_lm = lm.predict(x_test)
tpred_lml = lm_l.predict(x_test)
tpred_rf = gs.best_estimator_.predict(x_test)

from sklearn.metrics import mean_absolute_error
mean_absolute_error(y_test,tpred_lm)
mean_absolute_error(y_test,tpred_lml)
mean_absolute_error(y_test,tpred_rf)

mean_absolute_error(y_test,(tpred_lm+tpred_rf)/2)