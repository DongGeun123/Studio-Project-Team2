from datasets import load_dataset
from TweetNormalizer import normalizeTweet

dataset = load_dataset("tweet_eval", "sentiment")

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

stop_words = set(stopwords.words('english'))

def remove_stopwords(text):
    word_tokens = word_tokenize(text)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    return " ".join(filtered_sentence)

X_train_1 = [remove_stopwords(normalizeTweet(x)) for x in dataset["train"]["text"]]
y_train = dataset["train"]["label"]
X_test_1 = [remove_stopwords(normalizeTweet(x)) for x in dataset["test"]["text"]]
y_test = dataset["test"]["label"]

for i in [17885]:
    from sklearn.feature_extraction.text import CountVectorizer

    cv = CountVectorizer(max_features=i)
    X_train = cv.fit_transform(X_train_1).toarray()
    X_test = cv.transform(X_test_1).toarray()

    from sklearn.ensemble import RandomForestClassifier

    rf = RandomForestClassifier(n_estimators=100, verbose=True, n_jobs=-1, class_weight={0: 10, 1: 1, 2: 10})

    # Fit the model
    rf.fit(X_train, y_train)

    # accuracy, precision, recall, f1
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

    y_pred = rf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="macro")
    rec = recall_score(y_test, y_pred, average="macro")
    f1 = f1_score(y_test, y_pred, average="macro")

    print("Results for", i)
    print("Accuracy: ", acc)
    print("Precision: ", prec)
    print("Recall: ", rec)
    print("F1: ", f1)

    from sklearn.metrics import confusion_matrix
    cf_matrix = confusion_matrix(y_test, y_pred)
    print(cf_matrix)

    from sklearn.metrics import classification_report
    print(classification_report(y_test, y_pred))

import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

# Draw a confusion matrix with labels using seaborn
ax = plt.subplot()
sns.heatmap(cf_matrix/np.sum(cf_matrix), annot=True, ax=ax, fmt='.2%', cmap='Blues') #annot=True to annotate cells

# Save figures
plt.savefig('confusion_matrix.png')

breakpoint()
    
