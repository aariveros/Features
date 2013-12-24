from sklearn import cross_validation
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
import pandas as pd

path = "/Users/cristobal/Dropbox/MSc/bases/lightcurves/output.txt"
cols = ["ent_32", "ent_16", "ent_8", "ent_4", "ent_2", "label"]
data = pd.read_table(path, names = cols, sep = '\s+')

X = data[cols[0:-1]]
y = data["label"]

X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.3, random_state=0)

clf = RandomForestClassifier(n_estimators=10)
clf.fit(X_train, y_train)

svm_clf = svm.SVC(kernel='linear', C=1)
svm_clf.fit(X_train, y_train)

svm_clf2 = svm.SVC(kernel='rbf', C=1)
svm_clf2.fit(X_train, y_train)

print clf.score(X_test, y_test)
print svm_clf.score(X_test, y_test)
print svm_clf2.score(X_test, y_test)
