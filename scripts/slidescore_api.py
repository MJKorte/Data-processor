from slidescore import *

url = 'https://slidescore.umcutrecht.nl/'
apitoken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJOYW1lIjoiY2Jpb3BvcnRhbF90ZXN0X3Rva2VuIiwiSUQiOiIzNjYiLCJWZXJzaW9uIjoiMS4wIiwiQ2FuQ3JlYXRlVXBsb2FkRm9sZGVycyI6IkZhbHNlIiwiQ2FuVXBsb2FkIjoiRmFsc2UiLCJDYW5Eb3dubG9hZFNsaWRlcyI6IkZhbHNlIiwiQ2FuRGVsZXRlU2xpZGVzIjoiRmFsc2UiLCJDYW5VcGxvYWRPbmx5SW5Gb2xkZXJzIjoiIiwiQ2FuUmVhZE9ubHlTdHVkaWVzIjoiTEdSNl9FY2FkaDtLZXJhdGluMTQ7SUNSIElMQ19QRE8gbW9kZWxzO1NLT1IxIGFuZCBEQ05UMiBwcm9qZWN0IiwiQ2FuTW9kaWZ5T25seVN0dWRpZXMiOiIiLCJDYW5HZXRDb25maWciOiJUcnVlIiwiQ2FuR2V0UGl4ZWxzIjoiRmFsc2UiLCJDYW5VcGxvYWRTY29yZXMiOiJGYWxzZSIsIkNhbkNyZWF0ZVN0dWRpZXMiOiJGYWxzZSIsIkNhblJlaW1wb3J0U3R1ZGllcyI6IkZhbHNlIiwiQ2FuRGVsZXRlT3duZWRTdHVkaWVzIjoiRmFsc2UiLCJDYW5HZXRTY29yZXMiOiJGYWxzZSIsIkNhbkdldEFueVNjb3JlcyI6IkZhbHNlIiwibmJmIjoxNjE3OTY4MDgyLCJleHAiOjE2NDA5MDUyMDAsImlhdCI6MTYxNzk2ODA4Mn0.jLwHDkyUcbSqgYbQfXBsngcXVD0a0ARhAaHFpvIquUI'
client = APIClient(url, apitoken)
print(client.get_results())