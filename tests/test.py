import requests

base_url = "http://localhost:5000"

def create_chal():
    data = {
        "challenge_id": 1,
        "contest_id": 2,
        "user_id": 12,
        #"submission_datetime": "2021-10-10 10:10:10",
        "submitted_flag": "ctf{chaldelcazzo}",
        "solved": True
    }
    print(requests.post(base_url+"/submissions", json=data).text)

def all_subs():
     return requests.get(base_url+"/submissions?contest_id=2&user_id=12").json()

create_chal()
c = all_subs()
print(c)
#c["data"]["objects"][0]["title"] = "titolow weee"
#c["data"]["objects"][0]["points"] = 1
#print(put_chal(c["data"]["objects"][0]))
#print(get_chal())
#print(delete_chal())
#print(get_chal())


