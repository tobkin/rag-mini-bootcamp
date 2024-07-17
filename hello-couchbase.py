from datetime import timedelta
import traceback
# For exceptions
from couchbase.exceptions import CouchbaseException
# Required for any cluster connection
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
# Required for options -- cluster, timeout, SQL++ (N1QL) query, etc.
from couchbase.options import ClusterOptions
import os

CB_ENDPOINT=os.getenv("CB_ENDPOINT")
CB_USERNAME=os.getenv("CB_USERNAME")
CB_PASSWORD=os.getenv("CB_PASSWORD")
CB_BUCKET_NAME = "rag-workshop"
CB_SCOPE_NAME = "_default"
CB_COLLECTION_NAME = "_default"

sample_doc ={
    "id":1,
    "vector_1536_text_embedding_3_small":[0.8213382873243253,0.
    "text_split":"Once upon a time, there was a unicorn"
} 
key = "123"

auth = PasswordAuthenticator(CB_USERNAME, CB_PASSWORD)
options = ClusterOptions(auth)
options.apply_profile("wan_development")
try:
	cluster = Cluster(CB_ENDPOINT, options)
	cluster.wait_until_ready(timedelta(seconds=5))
	cb = cluster.bucket(CB_BUCKET_NAME)
	cb_coll = cb.scope(CB_SCOPE_NAME).collection(CB_COLLECTION_NAME)
	Simple K-V operation - to create a document with specific ID
	try:
		result = cb_coll.insert(key, sample_doc)
		print("\nCreate document success. CAS: ", result.cas)
	except CouchbaseException as e:
		print(e)
	# Simple K-V operation - to retrieve a document by ID
	try:
		result = cb_coll.get(key)
		print("\nFetch document success. Result: ", result.content_as[dict])
	except CouchbaseException as e:
		print(e)
	# Simple K-V operation - to update a document by ID
	try:
		sample_doc["name"] = "Couchbase Airways!!"
		result = cb_coll.replace(key, sample_doc)
		print("\nUpdate document success. CAS: ", result.cas)
	except CouchbaseException as e:
		print(e)
	# Simple K-V operation - to delete a document by ID
	try:
		result = cb_coll.remove(key)
		print("\nDelete document success. CAS: ", result.cas)
	except CouchbaseException as e:
		print(e)
except Exception as e:
	traceback.print_exc()
