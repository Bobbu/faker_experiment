#########################################################################
#
# alx_mock_carecloud_get_appointments.py
#
# This is intended to exist as a lambda function in a "fake carecloud.com API"
# and it represnts the "fake" version of the API's /appointments GET endpoint
#
# Employs our Faker-generated patient list (currently patients2000.json) and
# some rough logic to generate an apppointment schedule by pciking among the
# patients, considering the day desired, and then making and spreading out
# appointments in a sensible way.
#
# Also, if it finds a pre-exisitng json file represnting that day's
# appointments, it simply returns the content of that file rather than come up
# with an arbitrary/new appointment schedule -- this actually adds a degree of
# realism to its model since even historical apppointment schedules should stay
# fixed and not be arbitrarily regenerated.
#
# RJD, June 2023, with help from ChatGPT and Krishna Kanchinadam
#
#########################################################################
import json
import boto3
import random
from datetime import datetime, date, timedelta #, timezone
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')
test_data_bucket_name = 'alx-test-data-bucket'
test_patients_object_key = 'patients2000.json'

# doing this ultra fake just to avod needing to layer in the real Faker
fake_complaints = [
    "No complaints, really.",
    "It only hurts if I move or stand still.",
    "Unable to perform basic functions (e.g., writing or opening jars)",
    "Suspects arthritis in thumb.",
    "Fears fractured elbow.",
    "Candidate elbow replacement",
    "Not getting any more mobile",
    "Cannot throw overhand",
    "Cannot throw to save my life (never could)",
    "Got a ski pole stuck in my right bicep",
    "Suspect tennis elbow",
    "",
    "",
    "",
    "",
    ""
]

def does_s3_key_exist(bucket, key):

    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            # The object does not exist.
            return False
        else:
            # Something else has gone wrong.
            raise


def determine_desired_date(event):
    desired_date = date.today()
    
    query_string_params = event.get("queryStringParameters")
    if query_string_params != None:
        desired_date_param = query_string_params.get("desiredDate")
        if desired_date_param != None:
            desired_date = datetime.strptime(desired_date_param, '%Y-%m-%d')
            
    # desired_date = desired_date.replace(tzinfo=timezone.utc)
    return desired_date

def determine_number_of_appointments(desired_date):
    day_of_week = desired_date.strftime('%A')
    print(day_of_week)
    if day_of_week == 'Saturday':
        return 0
    if day_of_week == 'Sunday':
        return 0
    if day_of_week == 'Monday':
        return random.randint(3, 6)
    if day_of_week == 'Tuesday':
        return random.randint(20, 35)
    if day_of_week == 'Wednesday':
        return random.randint(0, 3)
    if day_of_week == 'Thursday':
        return random.randint(20, 35)
    if day_of_week == 'Friday':
        return random.randint(3, 6)

def determine_timedelta_between_appointments(total_number_of_appointments):
    if total_number_of_appointments > 20:
        return timedelta(minutes=15)
    if total_number_of_appointments > 10:
        return timedelta(minutes=30)
    if total_number_of_appointments > 5:
        return timedelta(hours=1)
    else:
        return timedelta(hours=2)

def appointments_object_key(desired_date):
    date_prefix = desired_date.strftime('%Y-%m-%d')
    result = date_prefix + "-appointments.json"
    return result
    
def load_preexisting_appointments(appointments_object_key):
    response = s3_client.get_object(Bucket=test_data_bucket_name, Key=appointments_object_key)
    #json_content = response['Body'].read().decode('utf-8')
    json_content = response['Body'].read()
    return json_content

def load_patients():
    response = s3_client.get_object(Bucket=test_data_bucket_name, Key=test_patients_object_key)
    file_content = response['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    return json_content
    
def generatedAppointments(desired_date, number_of_appointments):
    patients = load_patients()
    print(len(patients))
    print(desired_date)
    first_appointment_time = timedelta(hours=8, minutes=30)
    appointment_time = desired_date + first_appointment_time
    timedelta_between_appointments = determine_timedelta_between_appointments(number_of_appointments)
    appointments = []
    for i in range(number_of_appointments):
        random_patient = patients[random.randint(0, len(patients) - 1)]
        appointment_time = appointment_time + timedelta_between_appointments
        end_time = appointment_time + timedelta(hours = 1)
        appointment_time_safe_string = f"{appointment_time.isoformat()}"
        end_time_safe_string = f"{end_time.isoformat()}"
        random_time = datetime.now()
        new_appointment = { "appointment" : 
            {
                "id" : str(i),
                "patient" : random_patient,
                "chief_complaint" : fake_complaints[random.randint(0,len(fake_complaints) - 1)],
                "start_time" : appointment_time_safe_string,
                "end_time": end_time_safe_string,
                "created_at": random_time.isoformat(),
                "updated_at": random_time.isoformat()
            }
            
        }
        # Note our isoformat datetime strings look like this: "2023-06-01T15:30:00"
        # carecloud time strings look like this (UTC offset): "2023-06-01T08:30:00-04:00"
        appointments.append(new_appointment)
    return appointments
    

def lambda_handler(event, context):
        
    # 1. determine what day is desired. If no desired_date was passed to us, assume today
    desired_date = determine_desired_date(event)
    
    appointments_obj_key = appointments_object_key(desired_date)
    
    appointments_as_json = '[]' # TODO Learn about python variable scope rules
    
    # 2a. If an appointments file already exists in our test bucket, just return it. 
    #    Otherwise, we will geenrate a new set of appointments for the desired date.
    if does_s3_key_exist(test_data_bucket_name, appointments_obj_key):
        appointments_as_json = load_preexisting_appointments(appointments_obj_key)
        
    # 2b. Else, generate them and save for future use
    else:
        # 3. Determine the number of appointments (based on the day of the week):
        number_of_appointments = determine_number_of_appointments(desired_date)
        
        # 4. Generate the appointments
        appointments = generatedAppointments(desired_date, number_of_appointments)
        appointments_as_json = json.dumps(appointments)

        #5. Save the appointments json to an appointments object in s3.
        s3_client.put_object(Body=appointments_as_json, Bucket=test_data_bucket_name, Key=appointments_obj_key)

    return {
        'statusCode': 200,
        'body': appointments_as_json
    }
