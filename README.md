![ECTSearch](https://github.com/ECTLab/Search_Service_Platform/blob/master/logo.png "ECTSearch")

# Overview
**ECTSearch** is a Python Search-as-a-Service Platform.


## API
**/seach/search.py** contains APIs designed to use ECTSearch as a live service. It can create important statistics, search and test the system by sending HTTP request to it's different routes.

Each route takes a post request. Search-as-a-Service-Requests.json file contains some sample requests and contains important scenarios.

These routes are as follows:

Routes and options:
- **/create_positional_index** : Load the documents from IBM Cloud Storage and creates positional index and some other important statistics.
    - Headers: token : 
	- Body: {"language" : " ", "ibm_credentials_url" : " "}
    
	returns "Successfully created positional_index"


- **/create_statistics** : creates a JSON file and sets the values of top_k_results and champion_lists_status variables.
    - Headers: token : 
	- Body: {"top_k_results" : " ","champion_lists_status" : " "}
	
  returns "Successfully created statistics file"


- **/create_champion_lists**: creates champion lists
    - Headers: token : 
	- Body: {"range" : " "}
  
  returns "Successfully created champion lists"



- **/search** : search 
    - Headers: token : 
	- Body: {"query" : " ", "ibm_credentials_url" : " "}

  
  returns query {#number: {'Title': '', 'URL': '', 'ID': ''} Retrieval Time: - seconds


- **/test** : load test data and tests the system with Normalized Discounted Cumulative Gain
    - Headers: token : 
	- Body: {"ibm_credentials_url" : " "}

  
  returns Accuracy: 
