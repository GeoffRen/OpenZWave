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


def gaussian_nb(X, y, output=True):
    gnb = GaussianNB()
    predictions = gnb.fit(X, y).predict(X)
    scores = cross_val_score(gnb, X, y, cv=3)

    if output:
        print("Num features:", len(X[0]), "\n")
        print(confusion_matrix(y, predictions), "\n")
        print(classification_report(y, predictions))
        print("Accuracy: %0.2f (+/- %0.2f)\n" % (scores.mean(), scores.std() * 2))

    return scores.mean()


def neural_network(X, y, output=True):
    scaler = StandardScaler()
    scaler.fit(X)

    X = scaler.transform(X)

    mlp = MLPClassifier(hidden_layer_sizes=(30, 30, 30))
    mlp.fit(X, y)
    predictions = mlp.predict(X)
    scores = cross_val_score(mlp, X, y, cv=3)

    if output:
        print("Num features:", len(X[0]), "\n")
        print(confusion_matrix(y, predictions), "\n")
        print(classification_report(y, predictions))
        print("Accuracy: %0.2f (+/- %0.2f)\n" % (scores.mean(), scores.std() * 2))

    return scores.mean()


def svm(X, y, output=True, c=1, kernel='rbf'):
    scaler = StandardScaler()
    scaler.fit(X)

    X = scaler.transform(X)

    svm = SVC(C=c, kernel=kernel)
    svm.fit(X, y)
    predictions = svm.predict(X)
    scores = cross_val_score(svm, X, y, cv=3)

    if output:
        print("Num features:", len(X[0]))
        print("C: {} Kernel: {}\n".format(c, kernel))
        print(confusion_matrix(y, predictions), "\n")
        print(classification_report(y, predictions))
        print("Accuracy: %0.2f (+/- %0.2f)\n" % (scores.mean(), scores.std() * 2))

    return scores.mean()


def decision_tree(X, y, output=True):
    dtc = DecisionTreeClassifier(criterion='entropy')
    dtc.fit(X, y)
    predictions = dtc.predict(X)
    scores = cross_val_score(dtc, X, y, cv=3)

    if output:
        print(confusion_matrix(y, predictions), "\n")
        print(classification_report(y, predictions))
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2), "\n")

    return scores.mean()


def random_forest(X, y, output=True):
    rf = RandomForestClassifier()
    rf.fit(X, y)
    predictions = rf.predict(X)
    scores = cross_val_score(rf, X, y, cv=3)

    if output:
        print(confusion_matrix(y, predictions), "\n")
        print(classification_report(y, predictions))
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2), "\n")

    return scores.mean()


def extra_trees(X, y, output=True):
    et = ExtraTreeClassifier()
    et.fit(X, y)
    predictions = et.predict(X)
    scores = cross_val_score(et, X, y, cv=3)

    if output:
        print(confusion_matrix(y, predictions), "\n")
        print(classification_report(y, predictions))
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

    return scores.mean()

# Read in data
data = read_csv('geoff_water.csv')
X = data.loc[:, ['data', 'humidity_change_1']].astype('int').as_matrix()
y = data.loc[:, 'type_val'].astype('int').as_matrix()

# Run tests
gaussian_nb(X, y)
neural_network(X, y)
svm(X, y)
decision_tree(X, y)
random_forest(X, y)
extra_trees(X, y)
