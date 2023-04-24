# Fashionista


## Uploading data to backend:
Follow the example inside of [server/test_upload_product.py](https://github.com/Jomanw/fashionista/blob/main/server/test_upload_product.py) in order to upload a new product to the backend - make sure all of the relevant fields are filled in, or are at least blank (like, an empty list of tags instead of just no tags). This will embed the name, description, and tags into a single embedding, so we can use it for similarity search.

The server url for uploading data is at `https://y41pim9ut5.execute-api.us-west-1.amazonaws.com/dev/insert_product_info`.


## Running the server
It's running locally for now, so just use the command `python app.py` to run in the server directory (after sourcing local venv with `source .venv/bin/activate`)

## TODO List:
- Make it use the actual backend, not the localhost
- Inserting products should also classify the following attributes:
  - category: one of ['top', 'bottom', 'outerwear', 'dress', 'swimwear', 'underwear', 'sleepwear', 'accessory', 'footwear']
  - color: one of ['red', 'green', 'blue', 'black', 'brown', 'grey', 'yellow', 'purple', 'white', 'pink', 'orange']
  - gender: one of ['men', 'women']
  - material: one of ['cotton', 'silk', 'wool', 'linen', 'polyester', 'nylon', 'rayon', 'acrylic', 'spandex', 'leather', 'knit']
- Adjust the prompt to output these categories
- Adjust the query to filter based on these categories
- Add validation to the outputs

- 

## Appendix
- "client_id": "258654283607-0m8k8l6ghs5mo0pgr6bffrhrfsm407dt.apps.googleusercontent.com",