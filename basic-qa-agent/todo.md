[x] Test old code
[ ] Refactor away tech debt
    [ ] WcsClientAdapter
        [x] retrieve_top_k_chunks
        [ ] typing
        <!-- [ ] make a different collection for each document -->
[ ] Move files into "cheats"
[ ] Add query vectorization
[ ] Write tutorial


data_rows = [{"title": f"Object {i+1}"} for i in range(5)]
vectors = [[0.1] * 1536 for i in range(5)]

collection = client.collections.get("YourCollection")

with collection.batch.dynamic() as batch:
    for i, data_row in enumerate(data_rows):
        batch.add_object(
            properties=data_row,
            vector=vectors[i]
        )


----------------------------------

from weaviate.classes.query import MetadataQuery

jeopardy = client.collections.get("JeopardyQuestion")
response = jeopardy.query.near_vector(
    near_vector=query_vector, # your query vector goes here
    limit=2,
    return_metadata=MetadataQuery(distance=True)
)

for o in response.objects:
    print(o.properties)
    print(o.metadata.distance)