from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import csv

# which features will we use? lets set out some cognition features
# the two different goodness values can be knowledge gained or score in post-test
# lets first take in the process labesl

def fix(X):
    # making sure the users arent clustered on username
    try:
        X = X.drop(columns = ["Username"])
    except:
        pass
    X = (X-X.mean())/X.std()
    # filling the nan values
    X = X.fillna(0)
    return X

def load_process_features_study_f(BasePath_f, f):
  data = pd.read_csv(BasePath_f + f)

  features = {}

  features["Username"] = data['Username'][0]

  proc_labels = np.unique(np.array(data["Process Label"]))
  data["Process_Time_Spent"] = data["Process End Time"] - data["Process Start Time"]
  max_time = np.max(data["Process End Time"])
  # unsure if we want to keep no pattern because they did do something here
  # proc_labels.remove("NO_PATTERN")
  for proc in proc_labels:
      proc_rows = data[data["Process Label"] == proc]

      # feature #1 total time spent on processes
      features[("Time_spent_"+proc)] = [(proc_rows["Process_Time_Spent"]/100).sum()]

      # feature #2 mean time per session process session
      features[("Mean_time_"+proc)] = [(proc_rows["Process_Time_Spent"]/100).mean()]

      # feature #3 amount of times they did a process
      features[("Times_performed_"+proc)] = [proc_rows["Process_Time_Spent"].count()]

      # feature #4 percentage of time spent on a process
      features[("Percent_time_"+proc)] = [(proc_rows["Process_Time_Spent"]/100).sum()/max_time]
 
  # return the features as a df
  return pd.DataFrame.from_dict(features)


def load_process_features_study_3(BasePath_3, c_file):
  features = {}
  cleaned = []
  with open(BasePath_3 + c_file, newline='', encoding='utf8') as csvfile:
      spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
      for row in spamreader:
          real = (', '.join(row))
          if real.count(",") == 9:
              cleaned.append(np.array(real.split(",")))
  cleaned = np.array(cleaned)
  data = pd.DataFrame(cleaned, columns = ["logid", "actionid", "patternid", "date", "time",	"log_label", "action_label", "pattern_label", "pattern_span", "log_value"])

  features["Username"] = c_file.split(",")[0]
  # creating the time spent column

  time = list(data["time"])
  time.insert(0, time[0])
  time_spent = []
  FMT = ' %H:%M:%S'
  for i in range(1,len(time)):
      tdelta = datetime.strptime(time[i], FMT) - datetime.strptime(time[i-1], FMT)
      time_spent.append(tdelta.total_seconds())

  data["Process_Time_Spent"] = time_spent
  proc_labels = np.unique(np.array(data["pattern_label"]))


  max_time = data["Process_Time_Spent"].sum()

  proc_labels= list(filter(None, proc_labels))

  # unsure if we want to keep no pattern because they did do something here
  # proc_labels.remove("NO_PATTERN")

  for proc in proc_labels:
      proc_rows = data[data["pattern_label"] == proc]

      # feature #1 total time spent on processes
      features[("Time_spent_"+proc)] = [proc_rows["Process_Time_Spent"].sum()]

      # feature #2 mean time per session process session
      features[("Mean_time_"+proc)] = [proc_rows["Process_Time_Spent"].mean()]

      # feature #3 amount of times they did a process
      features[("Times_performed_"+proc)] = [proc_rows["Process_Time_Spent"].count()]

      # feature #4 percentage of time spent on a process
      features[("Percent_time_"+proc)] = [proc_rows["Process_Time_Spent"].sum()/max_time]

  # return the features as a df
  return pd.DataFrame.from_dict(features)

def cluster(df):
  # removing the username from the data if its there and also reducing to the features 
  # that were requested by the user (boolean map)
  df = fix(df)

  # df = df.loc[:, features]
  # creating labels for the users

  # clustering = DBSCAN(eps=7, min_samples=4).fit(X)
  # return clustering.labels_

  kmeans = KMeans(n_clusters= 3)
  clustering = kmeans.fit_predict(df)

  return clustering

def create_X(user_df, labels):

  X = fix(user_df)

  labels = pd.DataFrame(labels)

  # selecting only the features the users chose
  # X = user_df[features_chosen]

  #Load Data into pca
  pca = PCA(2)

  #Transform the data into 2 dimensions
  X = pca.fit_transform(X)
  X = pd.DataFrame(X)

  result = pd.concat([X, labels], axis=1)

  result.columns = ['x', 'y', 'label']

  return result

def plot(X):
  u_labels = X['label'].unique()

  for i in u_labels:
      plt.scatter(X['x'].loc[X['label'] == i],
                  X['y'].loc[X['label'] == i],
                  label = i)
  plt.legend()
  plt.show()

def important_features(user_df, labels):
  # how many imortant features do you want?
  num_important = 4

  # getting the unique labels of the clusters to see whats important about them
  u_labels = np.unique(labels)

  # reducing the amount of features to that chosen by the user
  df = fix(user_df)
  
  # creating the averages for each features and each label to compare them
  avgs = pd.DataFrame(columns = df.columns)
  avgs_abs = pd.DataFrame(columns = df.columns)
  avgs.loc[0] = list(df.mean(axis=0))
  important_features_lst = []

  # appending in the df the averages for each label of each feature
  for i in u_labels:
    label_avg = list(df[labels == i].mean(axis=0))
    avgs.loc[i + 1] = label_avg

    # finding which class features have the highest difference from the mean
    avgs_abs.loc[i] = np.abs(avgs.loc[0] - avgs.loc[i + 1])
    important = np.array(avgs_abs.loc[i]).argsort()[-num_important:][::-1]

    feature_list = []
    for feature in important:
      if avgs.iloc[i + 1, feature] > 0:
        feature_list.append(("High "+str(avgs.columns[feature])))
      else:
        feature_list.append(("Low "+str(avgs.columns[feature])))
    important_features_lst.append(feature_list)
  
  for i in range(len(important_features_lst)):
    print("Class",i,"has",important_features_lst[i])

  # alternatively to printing we make a list:
  return important_features_lst

def explain(important_features_lst):
  explain_df = pd.read_csv(r"../data/label_names.csv")
  features = np.array(important_features_lst).flatten()
  iso_features = []
  [iso_features.append(f.split("_")[-1]) for f in features]
  iso_features = np.unique(np.array(iso_features))

  explained = {}
  for f in iso_features:
    try:
      out =  explain_df[explain_df["Pattern No."] == f].iloc[:, 2]
      explained[f] = out.iloc[0]
    except:
      continue
  print(explained)

def reduce_df(user_df, features_chosen):
  columns = list(user_df.columns)
  remaining = np.zeros(len(columns))
  remaining[0] = 1
  for feature in features_chosen:
    keep = [col.split("_")[-1] == feature for col in columns]
    remaining = remaining + keep
  reduced = user_df.loc[:, remaining.astype(bool)]
  return reduced