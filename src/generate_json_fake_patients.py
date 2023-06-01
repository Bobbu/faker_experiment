#######################################################################
# generate_json_fake_patients.py
#
# Generates flae patients that meet the JSON defined by CareCloud.com for their
# patient records via their API. Notice that they use middle_initial vs complete
# middle_name. Left some placeholders here to not lose middle_name vs first_name
# uniqeness
#
# invoke with two arguments: 
#
#   1. number_of_fakes_to_make - a positive integer 
#   2. output_file - a filename to which to write the results
#
# Will generate a combo of patients that span Male ("1"), Female ("2"), Unknown
# (null), and Other ("3") genders.
#
# Will generate chart numbers that are unique within the results of a run 
#
# RJD, May 2023
#
#######################################################################
import sys
import numpy
import json
from faker import Faker

# initialize
fake = Faker()

# Check if the correct number of command line arguments is provided
if len(sys.argv) != 3:
    print("Usage: python generate_json_fake_patients.py <number_of_fakes_to_make> <output_file>")
    sys.exit(1)

# Extract command line arguments
number_of_fakes_to_make = int(sys.argv[1])
output_file = sys.argv[2]

chart_number_set = set()
id_set = set()

def unique_chart_number():
    chart_number = fake.random_int(min=100000, max=999999)
    if chart_number in chart_number_set:
        return unique_chart_number()
    else:
        chart_number_set.add(chart_number)
        return chart_number

def unique_id():
    id = fake.random_int(min=1000, max=9999)
    if id in id_set:
        return unique_id()
    else:
        id_set.add(id)
        return id

def realistic_fake_email(first_name, last_name):
    return f"{first_name}.{last_name}@{fake.domain_name()}"

def faker_categorical(number_of_fakes_to_make=20, seed=None):
    numpy.random.seed(seed)
    fake.seed_instance(seed)
    output = []
    for i in range(number_of_fakes_to_make):
        # for carecloud, we have four real options:
        # 1 = male, 2 = female, 3 = other, null is unknown
        gender = numpy.random.choice(['1', '2', None, '3'], p=[0.4, 0.4, 0.15, 0.05])
        first_name = 'tbd'
        middle_name = fake.first_name() # just something to get us a middle initial
        last_name = fake.last_name()
        if gender == '1':
            first_name = fake.first_name_male()
            while (middle_name == first_name):
                middle_name = fake.first_name_male()
        elif gender == '2':
            first_name = fake.first_name_female()
            while (middle_name == first_name):
                middle_name = fake.first_name_female()
        elif gender == '3' or gender == None:
            first_name = fake.first_name()
            while (middle_name == first_name):
                middle_name = fake.first_name()

        output.append(
            {
                "id": str(unique_id()),
                "chart_number": str(unique_chart_number()),
                "date_of_birth": str(fake.date_of_birth(minimum_age = 15, maximum_age = 90)),
                "first_name": first_name,
                "last_name": last_name,
                "middle_initial": middle_name[0],
                "gender_id": gender,
                "email": realistic_fake_email(first_name, last_name),
                "patient_status": fake.sentence(nb_words=10),
                "primary_phone_number": fake.phone_number(),
            })
    return output

results = faker_categorical(number_of_fakes_to_make, None)
json_results = json.dumps(results, indent=4)
print(json_results)

with open(output_file, 'w') as file:
    file.write(json_results)
