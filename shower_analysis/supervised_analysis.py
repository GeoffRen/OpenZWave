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
import matplotlib.pyplot as plt


def general_ml(alg, X, y, scale_X=False, output=True):
    if scale_X:
        scaler = StandardScaler()
        scaler.fit(X)
        X = scaler.transform(X)

    predictions = alg.fit(X, y).predict(X)
    scores = cross_val_score(alg, X, y, cv=3)

    if output:
        print("Classifier:", type(alg).__name__)
        print("Num features:", len(X[0]), "\n")
        print(confusion_matrix(y, predictions), "\n")
        print(classification_report(y, predictions))
        print("Accuracy: %0.2f (+/- %0.2f)\n" % (scores.mean(), scores.std() * 2))

    return scores.mean()


def format_type_val(x):
    return x*30 + 50


# Read in data
data = read_csv('geoff_water.csv')
X = data.loc[:, ['data', 'prev_type_val', 'humidity_change_1']].astype('int').as_matrix()
y = data.loc[:, 'type_val'].astype('int').as_matrix()

# Run tests
general_ml(GaussianNB(), X, y)
general_ml(MLPClassifier(hidden_layer_sizes=(30, 30, 30)), X, y, scale_X=True)
general_ml(SVC(), X, y, scale_X=True)
general_ml(DecisionTreeClassifier(criterion='entropy'), X, y)
general_ml(RandomForestClassifier(), X, y)
general_ml(ExtraTreeClassifier(), X, y)

# plt.plot('time', 'data', 'blue', data=data)
# plt.plot('time', format_type_val(y), 'green', data=data)
# plt.show()
