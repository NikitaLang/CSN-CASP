import io
import json

f = open("at_risk2","w")
cnt_dict = {}
percent_dict = {}

def field_count(filename):

    with open(filename, encoding="UTF-8") as json_file:
        for line_number, line in enumerate(json_file):
            data = json.loads(line)

            for key, value in data.items():
                if value:
                    if key in cnt_dict:
                        cnt_dict[key]+=1 
                    else:
                        cnt_dict[key]=1

            if line_number % 1000 == 0:
                print(line_number)

            if line_number % 1000 == 0:
                print(line_number)

def calc_percentage():
    for key, val in cnt_dict.items():
        percent_dict[key] = val / cnt_dict['id']

if __name__ == "__main__":
    field_count("../Datasets/sample1")
    field_count("../Datasets/sample2")
    calc_percentage()

    print(cnt_dict)
    print()
    print(percent_dict)
