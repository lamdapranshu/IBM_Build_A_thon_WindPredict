from flask import Flask, render_template, request, url_for
import requests
import urllib3, json
mean = [7.58716432e+00, 1.50410828e+03, 4.94015524e+00, 6.65630013e+00,
       2.40410966e-03]
std = [1.82624194e+01, 1.88860435e+06, 9.10645741e+00, 1.10369545e+01,
       5.65751707e-01]
def mean_direction(x):
    list = []
    i = 15
    while i <= 375:
        list.append(i)
        i += 30

    for i in list:
        if x < i:
            x = i - 15
            if x == 360:
                return 0
            else:
                return x
def find_direction(x):
    if x==0:
        return 1
    if x==30:
        return 2
    if x==60:
        return 3
    if x==90:
        return 4
    if x==120:
        return 5
    if x==150:
        return 6
    if x==180:
        return 7
    if x==210:
        return 8
    if x==240:
        return 9
    if x==270:
        return 10
    if x==300:
        return 11
    if x==330:
        return 12
app = Flask(__name__)





@app.route('/', methods=['POST', 'GET'])
def hello():
    if request.method == 'POST':
        ws = request.form['a']
        tpc = request.form['b']
        wd = request.form['c']
        pws = request.form['d']
        mn = request.form['e']
        if pws=="" or pws is None:
            pws=ws


        print(ws, tpc, wd, pws, mn)
        try:
            ws = float(ws)
            tpc = float(tpc)
            wd = float(wd)
            pws = float(pws)
            mn = int(mn)
            diff = abs(ws-pws)
            wd = find_direction(mean_direction(wd))

            std_ws = (ws-mean[0])/std[0]
            std_tpc = (tpc-mean[1])/std[1]
            std_wd = (wd-mean[2])/std[2]
            std_mn = (mn-mean[3])/std[3]
            std_diff = (diff-mean[4])/std[4]

        except:
            return render_template('index.html', err_msg='Enter Valid Data')
        url = "https://iam.cloud.ibm.com/identity/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = "apikey=" + '7xRco_fAK5h3tNq12NtKj8mZLVWxE1FYze4G21UtGicE' + "&grant_type=urn:ibm:params:oauth:grant-type:apikey"
        IBM_cloud_IAM_uid = "bx"
        IBM_cloud_IAM_pwd = "bx"
        response = requests.post(url, headers=headers, data=data, auth=(IBM_cloud_IAM_uid, IBM_cloud_IAM_pwd))
        print(response)
        iam_token = response.json()["access_token"]
        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + iam_token}
        payload_scoring = {"input_data": [
            {"fields": ['Wind Speed (m/s)', 'Theoretical_Power_Curve (KWh)', 'Direction', 'month', 'diff'],
             "values": [[std_ws, std_tpc, std_wd, std_mn, std_mn]]}]}
        response_scoring = requests.post(
            'https://eu-gb.ml.cloud.ibm.com/ml/v4/deployments/c81ce699-4243-4b6d-9168-56ddd2b7e9fb/predictions?version=2020-09-01',
            json=payload_scoring, headers=header)
        print(response_scoring)
        a = json.loads(response_scoring.text)
        print(a)
        pred = a['predictions'][0]['values'][0][0]

        
        return render_template('index.html', result=pred)

    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)