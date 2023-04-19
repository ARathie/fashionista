from http import server
import requests

# Send a POST request to our server with the product info
server_url = "https://y41pim9ut5.execute-api.us-west-1.amazonaws.com/dev/insert_product_info"
response = requests.post(server_url, json={
    "price": 125,
    "name": "Nike Tech Fleece Lightweight",
    "description": "Perfect for warmer weather, this classic full-zip design gives you a dose of signature Tech Fleece DNA in a lightweight, stretchy knit fabric. Premium finishes, like the taped trim and silicone Futura logo give you a polished look you can dress up or down.",
    "image_urls": [
        "https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/e561393d-1f2e-4e99-a313-ab71136010d4/tech-fleece-lightweight-mens-full-zip-hooded-jacket-PgWWQd.png",
        "https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/9a617164-7ef0-4d91-96f7-608480b5f28b/tech-fleece-lightweight-mens-full-zip-hooded-jacket-PgWWQd.png",
        "https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/3b505f05-cfa3-434b-8c39-98f1180e19e5/tech-fleece-lightweight-mens-full-zip-hooded-jacket-PgWWQd.png",
    ],
    "tags": ["standard_fit", "roomy_hood", "taped_trim_and_hem", "machine_wash", "spacious_side_pockets"],
    "url": "https://www.nike.com/t/tech-fleece-lightweight-mens-full-zip-hooded-jacket-PgWWQd/DX0822-725"
})