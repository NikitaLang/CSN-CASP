import io
import json

f = open("../Results/atRisk.json","w")

def find_at_risk(filename):

    with open(filename, encoding="UTF-8") as json_file:
        for line_number, line in enumerate(json_file):
            data = json.loads(line)

            if data['emails'] and data['job_company_name'] and data['job_company_location_name'] and data['job_title'] and data['education']:
                f.write(line)

            if line_number % 1000 == 0:
                print(line_number)

if __name__ == "__main__":
    find_at_risk("../Datasets/sample1")
    find_at_risk("../Datasets/sample2")
    total_num_lines = sum(1 for line in open("at_risk3"))
    print(total_num_lines)
