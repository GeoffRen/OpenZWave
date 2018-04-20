from pandas import read_csv
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.tree import ExtraTreeClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB


def neural_network():
    data = read_csv('geoff_water.csv')
    X = data.loc[:, ['data', 'prev_type_val', 'humidity_change_1']].astype('int').as_matrix()
    y = data.loc[:, 'type_val'].astype('int').as_matrix()
    return general_ml(MLPClassifier(hidden_layer_sizes=(30, 30, 30)), X, y, scale=True, output=False)


def general_ml(alg, X, y, scale=False, output=True, test_X=None, test_y=None):
    if scale:
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        if test_X is not None:
            test_X = scaler.transform(test_X)

    predictions = alg.fit(X, y).predict(X)
    scores = cross_val_score(alg, X, y, cv=3)

    if output:
        print("Classifier:", type(alg).__name__)
        print("Training split")
        print(confusion_matrix(y, predictions), "\n")
        print(classification_report(y, predictions))
        print("Accuracy: %0.2f (+/- %0.2f)\n" % (scores.mean(), scores.std() * 2))

    if test_X is not None and test_y is not None:
        print("Testing split")
        predictions = alg.predict(test_X)
        print(confusion_matrix(test_y, predictions), "\n")
        print(classification_report(test_y, predictions), "\n")

    return alg, scaler if scale else alg


# Read in data
# data = read_csv('geoff_water.csv')
# X = data.loc[:, ['data', 'prev_type_val', 'humidity_change_1']].astype('int').as_matrix()
# y = data.loc[:, 'type_val'].astype('int').as_matrix()
#
# test_data = read_csv('geoff_water_test.csv')
# test_X = test_data.loc[:, ['data', 'prev_type_val', 'humidity_change_1']].astype('int').as_matrix()
# test_y = test_data.loc[:, 'type_val'].astype('int').as_matrix()
#
# Run tests
# gnb = general_ml(GaussianNB(), X, y, test_X=test_X, test_y=test_y)
# nn = general_ml(MLPClassifier(hidden_layer_sizes=(30, 30, 30)), X, y, scale=True, test_X=test_X, test_y=test_y)
# svm = general_ml(SVC(), X, y, scale=True, test_X=test_X, test_y=test_y)
# dtc = general_ml(DecisionTreeClassifier(criterion='entropy'), X, y, test_X=test_X, test_y=test_y)
# rfc = general_ml(RandomForestClassifier(), X, y, test_X=test_X, test_y=test_y)
# etc = general_ml(ExtraTreeClassifier(), X, y, test_X=test_X, test_y=test_y)
