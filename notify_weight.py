import os
import requests
import json
import datetime
import urllib.parse

def make_weight_graph_url(data):
    chart_config = {
        "type": "line",
        "data": {
            "labels": [item['date'] for item in data],
            "datasets": [{
                "label": "Body Weight",
                "borderColor": "#FF3333",
                "data": [float(item['quantity']) for item in data],
                "fill": False
            }]
        },
        "options": {
            "scales": {
                "yAxes": [{
                    "ticks": {
                        "min": 70,
                        "max": 96,
                        "stepSize": 2
                    }
                }]
            }
        }
    }

    encoded_config = urllib.parse.quote(json.dumps(chart_config))
    quick_chart_url = "https://quickchart.io/chart?c={}".format(encoded_config)

    return quick_chart_url

def get_pixela_graph_pixels_list(date_from, date_to):
    username = os.environ["PIXELA_USER_NAME"]
    url = "https://pixe.la/v1/users/{}/graphs/weight/pixels?withBody=true&from={}&to={}&withBody=true".format(username, date_from, date_to)
    headers = {
        'X-USER-TOKEN': os.environ["PIXELA_USER_TOKEN"]
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()
    return data["pixels"]

def send_slack_notification(webhook_url, message):
    payload = {
        "text": message
    }
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()

    return response.status_code

if __name__ == "__main__":

    try:

        today = datetime.date.today()
        start_of_year = datetime.date(today.year, 1, 1)

        data = get_pixela_graph_pixels_list(start_of_year.strftime('%Y%m%d'), today.strftime('%Y%m%d'))
        url = make_weight_graph_url(data)

        message = '<{}|Changes in my body weight.>'.format(url)

        webhook_url = os.environ["SLACK_WEBHOOK_URL"]
        send_slack_notification(webhook_url, message)
    except requests.HTTPError as e:
        print("error occurred: {}".format(e))

