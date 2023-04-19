from http import server
import requests


json_1 = {
    "price": 125,
    "name": "Nike Tech Fleece Lightweight Men's Full-Zip Hooded Jacket",
    "description": "Perfect for warmer weather, this classic full-zip design gives you a dose of signature Tech Fleece DNA in a lightweight, stretchy knit fabric. Premium finishes, like the taped trim and silicone Futura logo give you a polished look you can dress up or down.",
    "image_urls": [
        "https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/e561393d-1f2e-4e99-a313-ab71136010d4/tech-fleece-lightweight-mens-full-zip-hooded-jacket-PgWWQd.png",
        "https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/9a617164-7ef0-4d91-96f7-608480b5f28b/tech-fleece-lightweight-mens-full-zip-hooded-jacket-PgWWQd.png",
        "https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/3b505f05-cfa3-434b-8c39-98f1180e19e5/tech-fleece-lightweight-mens-full-zip-hooded-jacket-PgWWQd.png",
    ],
    "tags": ["standard_fit", "roomy_hood", "taped_trim_and_hem", "machine_wash", "spacious_side_pockets"],
    "url": "https://www.nike.com/t/tech-fleece-lightweight-mens-full-zip-hooded-jacket-PgWWQd/DX0822-725"
}

json_2 = {
    "price": 105,
    "name": "Nike Tech Fleece Lightweight Men's Joggers",
    "description": "Perfect for those laid-back warm weather days, our classic fit Nike Tech Essentials joggers take their style cues from Tech Fleece. Unlike the insulating warmth of traditional Tech Fleece, however, these are made with a lightweight, stretchy knit fabric perfect for warmer months. The relaxed fit through the seat and thighs tapers down to the form-fitting, ribbed ankles for a tailored look that shows off your shoes.",
    "image_urls": [
        "https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/9cd163f9-0d0f-48bd-a46d-aeed4eb6390d/tech-fleece-lightweight-mens-joggers-Z38h70.png",
        "https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/d371a601-7ec2-4912-a7ce-d33417787702/tech-fleece-lightweight-mens-joggers-Z38h70.png",
        "https://static.nike.com/a/images/t_PDP_1728_v1/f_auto,q_auto:eco/4fd15379-a230-4bb9-aa9b-9a26e5ccd2e4/tech-fleece-lightweight-mens-joggers-Z38h70.png",
    ],
    "tags": ["standard_fit", "elastic_waistband", "tapered_leg", "machine_wash", "spacious_side_pockets"],
    "url": "https://www.nike.com/t/tech-fleece-lightweight-mens-joggers-Z38h70/DX0826-010"
}

# Send a POST request to our server with the product info
server_url = "https://y41pim9ut5.execute-api.us-west-1.amazonaws.com/dev/insert_product_info"
response = requests.post(server_url, json=json_1)
response = requests.post(server_url, json=json_2)