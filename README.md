# Overview

This is a simple wrapper to the Splunk API for Python. There are two main ways in which you interact with the API, and that's via the `get` and `post` commands, although the `post` command should be used most often.

# How to use it

After loading the library with `import splunk2`, initiate the API class by calling `api = splunk2.API()`. You then need to authenticate to Splunk by calling `api.authenticate("username", "password")`. If you save your credentials in a file somewhere, you can do all of this in one seamless step by using `api = splunk2.connect("c:/path/to/cred_file.json")` (it must be a JSON file).

Once you've entered the necessary information to interact with Splunk, you're ready to start interacting with it. 

#### get

`get` is mostly used to access searches that you may have run in an asynchronous fashion. What this means is that if you have a query that you know takes a long time, you can run the query and have Splunk immediately return control back to Python while the query runs. It will pass you a search ID, and you can use that ID to query the status of the search via a `get` request.

#### post

`post` is the workhorse of the API. `post` is what you use to query the data and to populate KV store lookup tables.

# Note

In the script, on line 15, you need modify `self.host` to point to your Splunk instance. If you don't know the URL that points to your search heads, reach out to your Splunk admin(s) for this information. It's import to note that it should point to the search heads directly, and not the URL you go to when running a query via the GUI.

# Examples

#### Load Splunk and initialize the API

```
import splunk2
api = splunk2.api()
api.authenticate("username", "password")
```

#### Query Splunk

```
query = """
search source="flights.csv"
| where isnotnull(arr_delay) AND isnotnull(dep_delay)
| stats mean(arr_delay) as avg_arr_delay, mean(dep_delay) as avg_dep_delay by origin
"""
data = {"exec_mode": "oneshot", "output_mode": "json", "search": query, "earliest_time": "-3h@h"}
results = api.post("services/search/jobs", data=data)
results
```

#### Update a KV store lookup table with lots of records

```
# use the results from the above example
# batch_save is used to store 1,000 records at a time
ENDPOINT = 'servicesNS/nobody/<app name>/storage/collections/data/<kv lookup name>/batch_save'
HEADERS = {'Content-Type': 'application/json'}
DATA = []
for row in range(results.shape[0]):
    DATA.append(results.loc[row, :].to_json())
    if len(DATA) == 1000:
        print('Uploading another 1,000 records to Splunk')
        DATA = '[' + ', '.join(DATA) + ']'
        api.post(ENDPOINT, headers=HEADERS, data=DATA)
        DATA = []
# need to upload any final records (e.g. the last 434 records if there are 5,434 records) 
if len(DATA) > 0:
    DATA = '[' + ', '.join(DATA) + ']'
    api.post(ENDPOINT, headers=HEADERS, data=DATA)
```
