import io
import json
import pickle

experience_dict = {}
education_dict = {}

def map(filename):
    with open(filename, encoding="UTF-8") as json_file:
        for line_number, line in enumerate(json_file):
            data = json.loads(line)

            # Education mapping
            if data['education']:
                if data['education'][0]:
                    if data['education'][0]['school']:
                        if data['education'][0]['school']['name']:
                            if data['education'][0]['school']['name'].lower() in education_dict:
                                education_dict[data['education'][0]['school']['name'].lower()].append(line)
                            elif line:
                                education_dict[data['education'][0]['school']['name'].lower()] = [line]
            if data['experience']:
                if data['experience'][0]:
                    if data['experience'][0]['company']:
                        if data['experience'][0]['company']['name']:
                            if data['experience'][0]['company']['name'].lower() in experience_dict:
                                name = data['experience'][0]['company']['name'].lower()
                                experience_dict[name].append(line)
                            elif line:
                                name = data['experience'][0]['company']['name'].lower()
                                experience_dict[name] = [line]


if __name__ == "__main__":
    map("../Datasets/sample1")
    map("../Datasets/sample2")
    with open('../Results/saved_experience_dict.pkl', 'wb') as f:
        pickle.dump(experience_dict, f)
    with open('../Results/saved_education_dict.pkl', 'wb') as f:
        pickle.dump(education_dict, f)