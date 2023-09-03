import os
import pandas as pd 
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import spacy
import csv
import re
import io
import os
import errno
from operator import add
from spacy.lang.nl.examples import sentences
from spacy.lang.en.examples import sentences 
from datetime import datetime
from pathlib import Path

root_path = "/data/www/flora/flora-lighthouse/api/"
label_loc = "data/label_names.csv"
# basepath for all files
BasePath_f = root_path + "data/"

# reading in the label csv to assign each pattern label to a type and sub type
def load_label_meanings():
  # =============================================================================== label names is constant and used to map individual labels to the parent process
  print(str(Path(label_loc)))
  labels_df = pd.read_csv(os.path.join(root_path, label_loc))
  sub_dict = {}
  main_dict = {}
  color_dict = {}

  # reading in the type of each pattern label and creating a dictionary for mapping
  for index, row in labels_df.iterrows():
    sub_dict[row["Pattern No."]] = row["Sub-category"]
    color_dict[row["Pattern No."]] = row["color"]
    m_pattern = row["Pattern No."]
    if m_pattern[0] == "M":
      main_dict[row["Pattern No."]] = "Metacognition"
    else:
      main_dict[row["Pattern No."]] = "Cognition"
    main_dict["NO_PATTERN"] = "NO_PATTERN"

  return sub_dict, main_dict, color_dict

def load_process_features_study_f(BasePath_f, sub_dict, main_dict, color_dict, f):

  # getting the data of the specific student
  # ==================================================================================================== here we read the pattern labels from the flora server
  data = pd.read_csv(BasePath_f + f)
  data = data[data["Process End Time"] > -1]

  # scaling between 0 and 1
  # max_time = np.max(data["Process End Time"])

  # this makes 45 minutes the maximum time the bar chart is filled out to
  max_time = 2700000

  data["Process End Time"] = data["Process End Time"] / max_time  
  data["Process Start Time"] = data["Process Start Time"] / max_time

  # adding extra columns to the data frame
  data["Process_Time_Spent"] = data["Process End Time"] - data["Process Start Time"]
  data["Process_sub"] = data["Process Label"].map(sub_dict) 
  data["Process_main"] = data["Process Label"].map(main_dict) 
  data["Color"] = data["Process Label"].map(color_dict)

  time_scaler = max_time / 60000

  # return the full user df
  return data, time_scaler

# with the full data of the user we want two series
# one series of the meta and one of the cog
# a series is a list of dictionaries that contain the sub process label and the time spent on that sub process
# in between each sub process there should be a dedicated "BLANK" section for if there is no label detected
def create_series(df, cog_type, time_scaler):
  # blank colour picker:
  blank_colour = "#ebebeb"

  # selecting the correct type of labels
  if cog_type == 'Combined':
    m_df = df[(df["Process_main"] == 'Metacognition') | (df["Process_main"] == 'Cognition')]
  else:
    m_df = df[df["Process_main"] == cog_type]
  m_df = m_df[["Process Start Time",	"Process End Time",	"Process_Time_Spent",	"Process_sub", "Color"]].reset_index(inplace = False)

  # adds a blank at the start since not both meta and cog can have the first label
  line = pd.DataFrame({"Process Start Time": 0, "Process End Time": m_df.iloc[0, 1], "Process_Time_Spent": m_df.iloc[0, 1], "Process_sub": "Niet Gedetecteerd", "Color": blank_colour}, index=[0])

  # concatenate two dataframe
  m_df = pd.concat([line, m_df]).reset_index(drop = True)
  m_df = m_df[["Process Start Time",	"Process End Time",	"Process_Time_Spent",	"Process_sub", "Color"]].reset_index(drop = True)

  # now we iterate through each row of the df and if there is a gap between two processes we fill the gap with a BLANK
  m_np = []
  for i, row in m_df.iterrows():
    m_row = []
    if (row["Process Start Time"] - m_df.iloc[i-1, 1]) > 0.00001:
      m_np.append([m_df.iloc[i-1, 1], row["Process Start Time"], row["Process Start Time"] - m_df.iloc[i-1, 1], "Niet Gedetecteerd", blank_colour])
    m_np.append(row.to_list())
    
  # adding a blank at the end in case the last process is of the other type of label
  m_np.append([m_df.iloc[-1, 1], 1, 1 - m_df.iloc[-1, 1], "Niet Gedetecteerd", blank_colour])
  m_df = pd.DataFrame(m_np, columns = ["Process Start Time",	"Process End Time",	"Process_Time_Spent",	"Process_sub", "Color"])
  m_df["Process_Time_Spent"] = m_df["Process_Time_Spent"] * time_scaler
  m_df["Process End Time"] = m_df["Process End Time"] * time_scaler
  m_df["Process Start Time"] = m_df["Process Start Time"] * time_scaler


  # now we go through the data frame and attach labels that are the same to each other
  # ============================ DOESNT WORK BUT PLEASE DONT UNCOMMENT ============================

  # drop_list = []
  # cleaned = []
  # for i, row in m_df.iterrows():
  #   inp = row.to_list()
  #   if row["Process_sub"] == m_df.iloc[i-1, 3]:
  #     print("true")
  #     print("current:",inp)
  #     inp[0] = m_df.iloc[i-2, 1]
  #     inp[2] = row["Process_Time_Spent"] + m_df.iloc[i-1, 2]
  #     drop_list.append(i)
    
  #   print("final",inp)
  #   print("-----")
  #   cleaned.append(inp)
  # m_df = pd.DataFrame(m_np, columns = ["Process Start Time",	"Process End Time",	"Process_Time_Spent",	"Process_sub", "Color"])
  # ===============================================================================================

  # having created the dataframe we now just have to create the series of data
  series = []
  for i, row in m_df.iterrows():
    if (row["Process_Time_Spent"] > 0):
      row_dic = {}
      row_dic["name"] = row["Process_sub"]
      row_dic["data"] = [row["Process_Time_Spent"]]
      row_dic["color"] = row["Color"]
      series.append(row_dic)

  # the order specified
  orders = {}
  orders["Metacognition"] = ["Orientatie", "Plannen", "Evaluatie", "Monitoren"]
  orders["Cognition"] = ["Lezen", "Herlezen", "Schrijven", "Verwerking / Organisatie"]
  orders["Combined"] = ["Orientatie", "Plannen", "Evaluatie", "Monitoren", "Lezen", "Herlezen", "Schrijven", "Verwerking / Organisatie"]

  # getting the percentages of each process, along with time until started and time spent on it
  perc = []
  personal = {}
  process_order = list(m_df["Process_sub"])
  # print(m_df)

  for i in orders[cog_type]:
    row_dic = {}
    row_dic["name"] = i

    # percentage
    row_dic["data"] = m_df[m_df["Process_sub"] == i]["Process_Time_Spent"].sum() / (m_df["Process End Time"].max())

    # minutes spent on it
    personal[i+"Mins"] = m_df[m_df["Process_sub"] == i]["Process_Time_Spent"].sum()

    # started at minute:
    if (i in process_order):
      personal[i+"Start"] = m_df[m_df["Process_sub"] == i]["Process Start Time"].min()
    else:
      personal[i+"Start"] = 0

    perc.append(row_dic)
  return [series, perc, personal]

# getting and returning the pre, post and learning gain of a student:
def results(file_path, username):
  # ========================= questionnaire is a server call to moodle
  pre_test_questionnaires = ['Questionnaire B', 'Pretest_pilot4_dagstudenten_13092022', 'Pretest_pilot5_20092022']
  pre_test = None

  for questionnaire in pre_test_questionnaires:
    print('Trying pretest questionnaire: ' + questionnaire)
    if pre_test == None:
      pre_test_df = pd.read_csv(file_path + "" + questionnaire + ".csv")
      try:
        pre_test = pre_test_df[pre_test_df["First name"] == username].iloc[0,7]
      except:
        continue

      print("Pretest value: " + pre_test)
    else:
      break

  # print("aaaaaaaaaaaaaaaaa", pre_test)

  #  same here
  post_test_questionnaires = ['Questionnaire C', 'Posttest_pilot4_dagstudenten_13092022', 'Posttest_pilot5_20092022']
  post_test = None

  for questionnaire in post_test_questionnaires:
    print('Trying posttest questionnaire: ' + questionnaire)
    if post_test == None:
      post_test_df = pd.read_csv(file_path + "" + questionnaire + ".csv")
      try:
        post_test = post_test_df[post_test_df["First name"] == username].iloc[0,7]
      except:
        continue
      
      print("Posttest value: " + post_test)
    else:
      break

  try:
    diff = int(float(post_test)) - int(float(pre_test))
  except:
    diff = 0

  return [pre_test, post_test, diff]

# Susanne's script time 
def susanneScript(username):

  # Please make sure the spacy pipeline for Dutch
  # is installed (for details: https://spacy.io/models/nl) - this should have been already done in the previous step,
  # but it is still good to check
  # Note: we use the model trained on a large corpus of texts, you may want to opt for a medium or small corpus instead,
  # in case efficiency is an issue
  nlp = spacy.load("nl_core_news_md")
  # nlp = spacy.load("en_core_web_md")

  # Import source texts
  # ==================================================================================================== source texts are constant so can just be on the server
  ai = open(BasePath_f + 'spiderScript/AI_NL.rtf', 'r')
  dif = open(BasePath_f + 'spiderScript/Differentiatie_NL.rtf', 'r')
  sc = open(BasePath_f + 'spiderScript/Scaffolding_NL.rtf', 'r')

  # ai = open(BasePath_f + 'spiderScript/AI_en.rtf', 'r')
  # dif = open(BasePath_f + 'spiderScript/Differentiation_en.rtf', 'r')
  # sc = open(BasePath_f + 'spiderScript/Scaffolding_en.rtf', 'r')

  # Build nlp objects for texts
  doc_1 = nlp(ai.read())
  doc_2 = nlp(dif.read())
  doc_3 = nlp(sc.read())

  # Fetch and process each essay
  max_numberwords = 400
  es_source_overlap = []
  cohesion = []
  mean_cohesion = []
  word_count = []
  word_countrel =[]

  # ====================================================================================== essay is chosen here
  essay_file = BasePath_f + "essays/essay_" + username + ".txt"

  with io.open(essay_file, "r", encoding="utf-8") as essay:
      essay = essay.read() 
      word_count = len(essay.split())

  # essay = open(essay_file, 'r', encoding='utf-8')
  # word_count = len(open(essay_file, 'r+').read().split())
  print(word_count)
  word_countrel = word_count/ max_numberwords

  # Build nlp object for the essay
  doc_essay = nlp(essay)

  # Tokenize essay into sentences
  l=[]
  for sent in doc_essay.sents:
      l.append(sent)
      
  # Compute semantic overlap with sources
  # Loop over each sentence and compute its semantic overlap with each source text
  source_overlap_1 = []
  source_overlap_2 = []
  source_overlap_3 = []
  for sent in range(len(l)):
      source_overlap_1.append(doc_1.similarity(l[sent]))
      source_overlap_2.append(doc_2.similarity(l[sent]))
      source_overlap_3.append(doc_3.similarity(l[sent]))
      
  # Semantic overlap with sources for the essay
  es_source_overlap = (np.mean(source_overlap_1) + np.mean(source_overlap_2) + np.mean(source_overlap_3))/5

  # Compute sentence mean cohesion (combinations without repetition)
  for k in range(0,len(l)-1):
      for j in range(k+1,len(l)):
          cohesion.append(l[j].similarity(l[k]))

  # Mean cohesion for the essay
  mean_cohesion = np.mean(cohesion)

  # return the list of values
  return [es_source_overlap, mean_cohesion, word_countrel]
