from pandas import read_csv
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB


def rf():
    """Creates a pre-trained RandomForestClassifier.
    :return: RandomForestClassifier pre-trained on humidity readings from water.csv.
    """
    data = read_csv('water.csv')
    X = data.loc[:, ['data', 'humidity_change_3', 'humidity_change_4',  'humidity_change_8', 'humidity_change_9']]\
        .astype('int').as_matrix()
    y = data.loc[:, 'type_val'].astype('int').as_matrix()
    return general_ml(RandomForestClassifier(n_estimators=100), X, y, output=False)


def general_ml(alg, X, y, scale=False, output=True, test_X=None, test_y=None):
    """Allows creation of sklearn machine learning models through one function.
    :param alg: sklearn model to use.
    :param X: Independent variable of training set.
    :param y: Dependent variable of training set.
    :param scale: Whether a scaler should be used.
    :param output: Whether accuracy metrics should be outputted.
    :param test_X: Independent variable of testing set.
    :param test_y: Dependent variable of testing set.
    :return: The trained algorithm and the associated scaler, if one was used.
    """
    if scale:
        scaler = StandardScaler()
        X = scaler.fit_transform(X)

        if test_X is not None:
            test_X = scaler.transform(test_X)

    scores = cross_val_score(alg, X, y, cv=3)
    predictions = alg.fit(X, y).predict(X)
    # Optimization: set past 4 points (last minute) to a shower instance upon shower classification.
    for i in range(len(predictions)):
        if predictions[i] == 1:
            predictions[i - 1] = 1
            predictions[i - 2] = 1
            predictions[i - 3] = 1
            predictions[i - 4] = 1

    if output:
        print("Classifier:", type(alg).__name__)
        print("Training split")
        print(confusion_matrix(y, predictions), "\n")
        print("Training Error:", 1 - accuracy_score(y, predictions))
        print("Average unweighted recall:", recall_score(y, predictions, average='macro'))
        print("Cross Validation error:", 1 - scores.mean(), "\n")

    if test_X is not None and test_y is not None:
        print("Testing split")
        test_predictions = alg.predict(test_X)
        for i in range(len(test_predictions)):
            if test_predictions[i] == 1:
                test_predictions[i-1] = 1
                test_predictions[i-2] = 1
                test_predictions[i-3] = 1
                test_predictions[i-4] = 1
        print(confusion_matrix(test_y, test_predictions), "\n")
        print("Testing Error:", 1 - accuracy_score(test_y, test_predictions))
        print("Average unweighted recall:", recall_score(test_y, test_predictions, average='macro'))

    if not scale:
        return alg
    return alg, scaler


def run_test(alg, test_X, test_y, scaler=None):
    """Tests and outputs accuracy metrics for a model.
    :param alg: Pre-trained sklearn model to test.
    :param test_X: Independent variable of the testing set.
    :param test_y: Dependent variable of the testing set.
    :param scaler: Scaler to use, if any.
    """
    print("Testing split")
    if scaler:
        test_X = scaler.transform(test_X)
    test_predictions = alg.predict(test_X)
    # Optimization: set past 4 points (last minute) to a shower instance upon shower classification.
    for i in range(len(test_predictions)):
        if test_predictions[i] == 1:
            test_predictions[i - 1] = 1
            test_predictions[i - 2] = 1
            test_predictions[i - 3] = 1
            test_predictions[i - 4] = 1
    print(confusion_matrix(test_y, test_predictions), "\n")
    print("Training Error:", 1 - accuracy_score(test_X, test_predictions))
    print("Average unweighted recall:", recall_score(test_y, test_predictions, average='macro'))


# Read in data.
data = read_csv('water.csv')
test_data = data.loc[57205:]
data = data.loc[:57205]
X = data.loc[:, ['data', 'humidity_change_1', 'humidity_change_2', 'humidity_change_3', 'humidity_change_4',  'humidity_change_8', 'humidity_change_9']].astype('int').as_matrix()
y = data.loc[:, 'type_val'].astype('int').as_matrix()
test_X = test_data.loc[:, ['data', 'humidity_change_1', 'humidity_change_2', 'humidity_change_3', 'humidity_change_4', 'humidity_change_8', 'humidity_change_9']].astype('int').as_matrix()
test_y = test_data.loc[:, 'type_val'].astype('int').as_matrix()


# Run normal tests.
gnb = general_ml(GaussianNB(), X, y, test_X=test_X, test_y=test_y)
nn = general_ml(MLPClassifier(hidden_layer_sizes=(30, 30, 30)), X, y, scale=True, test_X=test_X, test_y=test_y)
svm = general_ml(SVC(), X, y, scale=True, test_X=test_X, test_y=test_y)
dtc = general_ml(DecisionTreeClassifier(criterion='entropy'), X, y, test_X=test_X, test_y=test_y)
rfc = general_ml(RandomForestClassifier(n_estimators=100), X, y, test_X=test_X, test_y=test_y)
etc = general_ml(ExtraTreesClassifier(n_estimators=100), X, y, test_X=test_X, test_y=test_y)


# # Compare how important each feature is.
# print(dtc[0].feature_importances_)
# print(rfc[0].feature_importances_)
# print(etc[0].feature_importances_)


# # Run the tests of each model considered against each testing csv.
# hotc = read_csv('hot_closed_testing.csv')
# hotc_X = hotc.loc[:, ['data', 'humidity_change_1', 'humidity_change_2', 'humidity_change_3', 'humidity_change_4',  'humidity_change_8', 'humidity_change_9']].astype('int').as_matrix()
# hotc_y = hotc.loc[:, 'type_val'].astype('int').as_matrix()
#
# hoto = read_csv('hot_open_testing.csv')
# hoto_X = hoto.loc[:, ['data', 'humidity_change_1', 'humidity_change_2', 'humidity_change_3', 'humidity_change_4',  'humidity_change_8', 'humidity_change_9']].astype('int').as_matrix()
# hoto_y = hoto.loc[:, 'type_val'].astype('int').as_matrix()
#
# coldc = read_csv('cold_closed_testing.csv')
# coldc_X = coldc.loc[:, ['data', 'humidity_change_1', 'humidity_change_2', 'humidity_change_3', 'humidity_change_4',  'humidity_change_8', 'humidity_change_9']].astype('int').as_matrix()
# coldc_y = coldc.loc[:, 'type_val'].astype('int').as_matrix()
#
# coldo = read_csv('cold_open_testing.csv')
# coldo_X = coldo.loc[:, ['data', 'humidity_change_1', 'humidity_change_2', 'humidity_change_3', 'humidity_change_4',  'humidity_change_8', 'humidity_change_9']].astype('int').as_matrix()
# coldo_y = coldo.loc[:, 'type_val'].astype('int').as_matrix()
#
# of = read_csv('on_off_testing.csv')
# of_X = of.loc[:, ['data', 'humidity_change_1', 'humidity_change_2', 'humidity_change_3', 'humidity_change_4',  'humidity_change_8', 'humidity_change_9']].astype('int').as_matrix()
# of_y = of.loc[:, 'type_val'].astype('int').as_matrix()
#
# gnb = general_ml(GaussianNB(), X, y)
# nn = general_ml(MLPClassifier(hidden_layer_sizes=(30, 30, 30)), X, y, scale=True)
# svm = general_ml(SVC(), X, y, scale=True)
# dtc = general_ml(DecisionTreeClassifier(criterion='entropy'), X, y)
# rfc = general_ml(RandomForestClassifier(100), X, y)
# etc = general_ml(ExtraTreesClassifier(100), X, y)
#
# print("\n~~~~~~~~~~GNB~~~~~~~~~~\n")
#
# run_test(gnb[0], hotc_X, hotc_y)
# run_test(gnb[0], hoto_X, hoto_y)
# run_test(gnb[0], coldc_X, coldc_y)
# run_test(gnb[0], coldo_X, coldo_y)
# run_test(gnb[0], of_X, of_y)
#
# print("\n~~~~~~~~~~NN~~~~~~~~~~\n")
#
# run_test(nn[0], hotc_X, hotc_y, scaler=nn[1])
# run_test(nn[0], hoto_X, hoto_y, scaler=nn[1])
# run_test(nn[0], coldc_X, coldc_y, scaler=nn[1])
# run_test(nn[0], coldo_X, coldo_y, scaler=nn[1])
# run_test(nn[0], of_X, of_y, scaler=nn[1])
#
# print("\n~~~~~~~~~~SVM~~~~~~~~~~\n")
#
# run_test(svm[0], hotc_X, hotc_y, scaler=svm[1])
# run_test(svm[0], hoto_X, hoto_y, scaler=svm[1])
# run_test(svm[0], coldc_X, coldc_y, scaler=svm[1])
# run_test(svm[0], coldo_X, coldo_y, scaler=svm[1])
# run_test(svm[0], of_X, of_y, scaler=svm[1])
#
# print("\n~~~~~~~~~~DTC~~~~~~~~~~\n")
#
# run_test(dtc[0], hotc_X, hotc_y)
# run_test(dtc[0], hoto_X, hoto_y)
# run_test(dtc[0], coldc_X, coldc_y)
# run_test(dtc[0], coldo_X, coldo_y)
# run_test(dtc[0], of_X, of_y)
#
# print("\n~~~~~~~~~~RFC~~~~~~~~~~\n")
#
# run_test(rfc[0], hotc_X, hotc_y)
# run_test(rfc[0], hoto_X, hoto_y)
# run_test(rfc[0], coldc_X, coldc_y)
# run_test(rfc[0], coldo_X, coldo_y)
# run_test(rfc[0], of_X, of_y)
#
# print("\n~~~~~~~~~~ETC~~~~~~~~~~\n")
#
# run_test(etc[0], hotc_X, hotc_y)
# run_test(etc[0], hoto_X, hoto_y)
# run_test(etc[0], coldc_X, coldc_y)
# run_test(etc[0], coldo_X, coldo_y)
# run_test(etc[0], of_X, of_y)
