# Fashionista


## Uploading data to backend:
Follow the example inside of [server/test_upload_product.py](https://github.com/Jomanw/fashionista/blob/main/server/test_upload_product.py) in order to upload a new product to the backend - make sure all of the relevant fields are filled in, or are at least blank (like, an empty list of tags instead of just no tags). This will embed the name, description, and tags into a single embedding, so we can use it for similarity search.

The server url for uploading data is at `https://y41pim9ut5.execute-api.us-west-1.amazonaws.com/dev/insert_product_info`.


## Running the server
It's running locally for now, so just use the command `python app.py` to run in the server directory (after sourcing local venv with `source .venv/bin/activate`)

## TODO List:
- Make it so that it pulls the most recent message state every time the site loads, using their email as their identifier.
- Make it use the actual backend, not the localhost


## Appendix
- "client_id": "258654283607-0m8k8l6ghs5mo0pgr6bffrhrfsm407dt.apps.googleusercontent.com",