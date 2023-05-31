#######################################################################
# generate_json_fake_patients.py
#
# invoke with two arguments: 
#
#   1. number_of_fakes_to_make - a positive integer 
#   2. output_file - a filename to which to write the results
#
# Will generate a combo of patients that span Male, Female, Unknown, and Other
# genders.
#
# Will generate chart numbers that are unique within the results of a run 
#
# RJD, May 2023
#
#######################################################################
import sys
import random
from faker import Faker

# initialize
fake = Faker()
# Faker.seed(0)

# Check if the correct number of command line arguments is provided
if len(sys.argv) != 3:
    print("Usage: python generate_json_fake_patients.py <number_of_fakes_to_make> <output_file>")
    sys.exit(1)

# Extract command line arguments
number_of_fakes_to_make = int(sys.argv[1])
output_file = sys.argv[2]

# constants
TAB = '    '
TAB2 = TAB + TAB
TAB3 = TAB2 + TAB
QUOTE = '"'
QSEP = '" : "'
TAB2Q = TAB2 + QUOTE
QUOTE_COMMA = QUOTE + ','

chart_number_set = set()

def unique_chart_number():
    chart_number = fake.random_int(min=100000, max=999999)
    if chart_number in chart_number_set:
        return unique_chart_number()
    else:
        chart_number_set.add(chart_number)
        return chart_number

def realistic_fake_email(first_name, last_name):
    return f"{first_name}.{last_name}@{fake.domain_name()}"

def write_fake_details(file, gender):
    first_name = 'tbd'
    middle_name = 'tbd'
    # a little goofing around to ensure different middle and first names
    if (gender == 'Male'):
        first_name = fake.first_name_male()
        middle_name = fake.first_name_male()
        while (middle_name == first_name):
            middle_name = fake.first_name_male()
    elif (gender == 'Female'):
        first_name = fake.first_name_female()
        middle_name = fake.first_name_female()
        while (middle_name == first_name):
            middle_name = fake.first_name_female()
    elif (gender == 'Other' or gender == 'Unknown'):
        first_name = fake.first_name()
        middle_name = fake.first_name()
        while (middle_name == first_name):
            middle_name = fake.first_name()

    last_name = fake.last_name()
    email = realistic_fake_email(first_name, last_name)
    date_of_birth = fake.date_of_birth(minimum_age = 15, maximum_age = 90)
    chart_number = unique_chart_number()

    file.write(TAB2Q + 'first_name' + QSEP + first_name + QUOTE_COMMA)
    file.write(TAB2Q + 'middle_name' + QSEP + middle_name + QUOTE_COMMA)
    file.write(TAB2Q + 'last_name' + QSEP + fake.last_name() + QUOTE_COMMA)
    file.write(TAB2Q + 'gender' + QSEP + gender + QUOTE_COMMA)
    file.write(TAB2Q + 'chart_number' + QSEP + str(chart_number) + QUOTE_COMMA)
    # Generate a random date of birth. The Faker "date_of_birth" method
    # takes three arguments: minimum age, maximum age, and a specific date
    # object that the generated date will not exceed. This example will
    # generate a date of birth for a person aged between 15 and 90 years old
    # as of today.
    file.write(TAB2Q + 'date_of_birth' + QSEP + str(date_of_birth) + QUOTE_COMMA)
    file.write(TAB2Q + 'email' + QSEP + email + QUOTE_COMMA)
    file.write(TAB2Q + 'phone' + QSEP + fake.phone_number() + QUOTE_COMMA)
    file.write(TAB2Q + 'zipcode' + QSEP + fake.zipcode() + QUOTE)

# Perform the loop and write output to the file
with open(output_file, 'w') as file:
    file.write('[')
    for i in range(number_of_fakes_to_make):
        file.write(TAB + '{')

        # We want to distribute the number of male, female, unknown, and other
        # as realistically as possible, so we split the majority of random
        # number among the male and female, and leave a smaller percentage for
        # unknown (not yet captured) and another small amoount to other.
        random_number = random.randint(1, 20)
        if random_number < 9:
            write_fake_details(file, 'Male')
        elif random_number < 17:
            write_fake_details(file, 'Female')
        elif random_number < 19:
            write_fake_details(file, 'Unknown')
        elif random_number < 20:
            write_fake_details(file, 'Other')

        if (i + 1 == number_of_fakes_to_make):
            file.write(TAB + '}')
        else:
            file.write(TAB + '},')

    file.write(']')
