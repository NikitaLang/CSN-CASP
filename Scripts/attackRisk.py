import io
import json
import pickle
import datetime
import re
import math
from collections import Counter
import numpy as np
from fuzzywuzzy import fuzz


MANAGER_SET = {"Manager", "Director", "PM", "Administrator", "Supervisor"}
HR_SET = {"Human Resources", "HR", "Director of Recruiting", "Coordinator", "CHRO", "Staffing Specialist"}

education_dict = {}
experience_dict = {}
subject_to_network_dict = {}
highest_score = 0
highest_id = ""
total = 0
score_count = 0
high_scores = 0
high_match_lst = []

def months_intersection(year1, year2, month1 = 0, month2 = 0):
    end_date = datetime.datetime(year2, month2, 1)
    start_date = datetime.datetime(year1, month1, 1)
    num_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    return abs(num_months)

# def levenshtein_ratio_and_distance(s, t, ratio_calc = True):
#     """ levenshtein_ratio_and_distance:
#         Calculates levenshtein distance between two strings.
#         If ratio_calc = True, the function computes the
#         levenshtein distance ratio of similarity between two strings
#         For all i and j, distance[i,j] will contain the Levenshtein
#         distance between the first i characters of s and the
#         first j characters of t
#         Courtesy of - 
#         https://www.datacamp.com/community/tutorials/fuzzy-string-python
#     """
#     # Initialize matrix of zeros
#     rows = len(s)+1
#     cols = len(t)+1
#     distance = np.zeros((rows,cols),dtype = int)

#     for i in range(1, rows):
#         for k in range(1,cols):
#             distance[i][0] = i
#             distance[0][k] = k

#     # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions    
#     for col in range(1, cols):
#         for row in range(1, rows):
#             if s[row-1] == t[col-1]:
#                 cost = 0 # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
#             else:
#                 if ratio_calc == True:
#                     cost = 2
#                 else:
#                     cost = 1
#             distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
#                                  distance[row][col-1] + 1,          # Cost of insertions
#                                  distance[row-1][col-1] + cost)     # Cost of substitutions
#     if ratio_calc == True:
#         # Computation of the Levenshtein Distance Ratio
#         Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
#         return Ratio
#     else:
#         # print(distance) # Uncomment if you want to see the matrix showing how the algorithm computes the cost of deletions,
#         # insertions and/or substitutions
#         # This is the minimum number of edits needed to convert string a to string b
#         return "The strings are {} edits away".format(distance[row][col])

def best_lev_match(set, comparison_string):
    max = 0
    for word in set:
        lev_score = fuzz.token_set_ratio(comparison_string, word)
        if lev_score > max:
            max = lev_score
    return max/100

def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def text_to_vector(text):
    word = re.compile(r'\w+')
    words = word.findall(text)
    return Counter(words)


def get_cosine_sim(content_a, content_b):
    text1 = content_a
    text2 = content_b

    vector1 = text_to_vector(text1)
    vector2 = text_to_vector(text2)

    cosine_result = get_cosine(vector1, vector2)
    return cosine_result


def subject_to_network(filename):
    global highest_id
    global highest_score
    global total
    global score_count
    global high_scores
    global high_match_lst
    with open(filename, encoding="UTF-8") as json_file:
        for line_number, line in enumerate(json_file):
            attack_subject = json.loads(line)
            try:
                subject_company_name = attack_subject['job_company_name']
                subject_company_id = attack_subject['job_company_id']
                subject_job_title = attack_subject['job_title']
                subject_company_region = attack_subject['job_company_location_region']
                subject_linkedin_id = attack_subject['id']
                subject_start_date = attack_subject['job_start_date']

                related_individuals = experience_dict[subject_company_name.lower()]

                if (len(related_individuals) > 1):
                    for profile in related_individuals:
                        profile = json.loads(profile)
                        try:
                            if profile['id'] != subject_linkedin_id:
                                attack_risk_result = attack_risk(subject_company_name, subject_company_id, subject_job_title, subject_company_region, subject_start_date, profile)
                                total += attack_risk_result[1]
                                score_count += 1

                                if attack_risk_result[1] > 300:
                                    high_scores += 1
                                    high_match_lst.append([attack_risk_result[1],attack_risk_result[0], attack_subject, profile])

                                if attack_risk_result[1] > highest_score:
                                    highest_id = subject_linkedin_id
                                    highest_score = attack_risk_result[1]

                                if subject_linkedin_id in subject_to_network_dict:
                                    subject_to_network_dict[subject_linkedin_id].append([profile,attack_risk_result])
                                else:
                                    subject_to_network_dict[subject_linkedin_id] = [profile,attack_risk_result]
                        except:
                            pass
            except:
                pass
        print(highest_score, highest_id, total/score_count, high_scores, score_count)
            # if line_number > 1000:
            #     print(highest_score, highest_id, total/score_count, high_scores, score_count)
            #     break

def attack_risk(company_name, company_id, job_title, region, start_date, profile):
    w1 = 0.5
    w2 = 0.25
    w3 = 0.25
    c1 = 0
    c2 = 0
    c3 = 0
    attack_vector = ""
    final_score = 0

    try:
        if profile['job_company_id'] == company_id or profile['job_company_id'].lower() == 'job_company_name'.lower():
            c1 = 1
    except:
        pass
    try:
        if get_cosine_sim(job_title, profile['job_title']) > .7:
            c2 = 1
        elif profile['job_title']:
            c2 = .25
    except:
        pass
    try:
        if region == profile['job_company_location_region']:
            c3 = 1
    except:
        pass

    profile_conf = w1*c1 + w2*c2 + w3*c3

    # print(c1, c2, c3)

    m1 = 0
    m2 = 0
    m3 = 0

    try:
        m1 = best_lev_match(MANAGER_SET, profile['job_title'])
    except:
        pass

    try:
        subject_start_date = start_date.split("-")
        related_start_date = profile['job_start_date'].split("-")
        year1 = subject_start_date[0]
        year2 = related_start_date[0]
        month1 = 1
        month2 = 1

        if len(subject_start_date) > 1:
            month1 = subject_start_date[1]

        if len(related_start_date) > 1:
            month2 = related_start_date[1]

        m2 = months_intersection(int(year2), 2021, int(month2), 12)
        m3 = months_intersection(int(year1), int(year2), int(month1), int(month2))

    except:
        pass

    n1 = 0
    n2 = 0
    n3 = 2

    try:
        n1 = best_lev_match([job_title], profile['job_title'])
    except:
        pass
    try:
        if related_start_date[0] == "2020" or related_start_date[0] == "2021":
            n1 = 1
    except:
        pass

    h1 = 0
    
    try:
        h1 = best_lev_match(HR_SET, profile['job_title'])
    except:
        pass

    mng_vector_score = m1 * (m2 + m3)

    new_empl_vector_score = n1 * (n2 * n3)

    hr_vector_score = h1 * (m2 + m3)

    if mng_vector_score > new_empl_vector_score and mng_vector_score > hr_vector_score:
        attack_vector = "M"
        final_score = profile_conf * mng_vector_score
    elif new_empl_vector_score > mng_vector_score and new_empl_vector_score > hr_vector_score:
        attack_vector = "N"
        final_score = profile_conf * new_empl_vector_score
    else:
        attack_vector = "H"
        final_score = profile_conf * hr_vector_score

    return [attack_vector, final_score]
            

if __name__ == "__main__":
    with open('../Results/saved_education_dict.pkl', 'rb') as f:
        education_dict = pickle.load(f)
    with open('../Results/saved_experience_dict.pkl', 'rb') as f:
        experience_dict = pickle.load(f)

    subject_to_network("../Results/atRisk.json")

    with open('../Results/subject_to_network.pkl', 'wb') as f:
        pickle.dump(subject_to_network_dict, f)
    with open('../Results/high_match_lst.pkl', 'wb') as f:
        pickle.dump(high_match_lst, f)