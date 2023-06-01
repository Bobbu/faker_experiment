# faker_experiment
This demonstrates creating simulated CareCloud.com patients using the Python faker package. See the documentation for their API at https://developer.carecloud.com/. Notably, look at the /Appointments GET method.  Each Appointment object returned has a patient object. That is what the JSON here currently resembles.

Finally, thanks to the makers of the Faker package, the people who shared ideas on Stack Overflow, and ChatGPT for helping navigate all the important parts.

Invoke this way:
```
$ python src/generate_json_fake_patients.py 300 patients.json
```
...where 300 represents the number of fake patients that will be created and "patients.json" is the name of the resulting output file where the new fake patients will be written in JSON format.

If you would like to see a walkthrough of at least one version of the code contained in this repo, you can see a YouTube video walkthrough here: 

*2023-05-31 Demo of Faker Experiment*
https://www.youtube.com/watch?v=r6-1GqaCpto

