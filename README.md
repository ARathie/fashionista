# Fashionista


## Uploading data to backend:
Follow the example inside of [server/test_upload_product.py](https://github.com/Jomanw/fashionista/blob/main/server/test_upload_product.py) in order to upload a new product to the backend - make sure all of the relevant fields are filled in, or are at least blank (like, an empty list of tags instead of just no tags). This will embed the name, description, and tags into a single embedding, so we can use it for similarity search.

The server url for uploading data is at `https://y41pim9ut5.execute-api.us-west-1.amazonaws.com/dev/insert_product_info`.

## TODO List:
- Supabase: Get it set up with credentials and a few tables
- Zappa: Get it hosted somewhere
- Make the frontend support chats with multiple messages