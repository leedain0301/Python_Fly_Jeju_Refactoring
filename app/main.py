from flask import Flask, render_template, request, jsonify
from bigquery import clinet_bigquery
import func
import json



app = Flask(__name__, static_url_path="/static")

total_amount = 0

@app.route('/')
def calendar():
    return render_template('main.html')

@app.route('/demo', methods=['GET', 'POST'])
def demo():
    if request.method == 'POST':
        data = request.form.get('data')
        return "POST 요청을 받았습니다"
    else:
        sql = '''
           SELECT 
                date, 
                extract(week from DATE) as extweek,
                MIN(charge) AS mincharge,
                RANK() OVER (PARTITION BY extract(week from DATE) ORDER BY MIN(charge)) AS rankingbyweek
            FROM
                test_db.airplanecrawl
            GROUP BY
                date , extweek
            ORDER BY 
                extweek,mincharge
            LIMIT 50;
        '''
        data_list = clinet_bigquery(sql)
        json_data = data_list.to_json(orient='records')
        return jsonify(json_data)

air_data = clinet_bigquery('''
                            SELECT date, day, name, airport, leavetime, reachtime, seat,charge
                            FROM test_db.airplanecrawl
                            WHERE date = '2023-07-01'
                            ORDER BY charge ASC
                            LIMIT 20;
                            ''')
hotel_data = clinet_bigquery('''SELECT * FROM test_db.hotelcrawl
                                where rating != '평점없음' and star is not null
                                order by star desc, price asc
                                LIMIT 20;''') 
car_data = clinet_bigquery('''SELECT  carname, oiltype, seater, avg_year,
                            CAST(AVG(CAST(regular_price AS INT)) AS INT) AS avg_regular_price,
                            CAST(AVG(CAST(discounted_price AS INT)) AS INT) AS avg_discounted_price
                            FROM `fightproject.test_db.car`
                            WHERE regular_price != '마감' AND discounted_price != '마감'
                            GROUP BY carname, oiltype, seater, avg_year
                            ORDER BY avg_discounted_price, avg_regular_price
                            LIMIT 20;''') 

@app.route('/filght', methods=['GET','POST'])
def get_flight():
    air_list = air_data.to_dict(orient='records')
    hotel_list = hotel_data.to_dict(orient='records')
    car_list = car_data.to_dict(orient='records')

    if request.method=='POST':
        return jsonify(air_list=air_list, hotel_list=hotel_list, car_list=car_list)
    else:
        return render_template('filght.html', air_list=air_list, hotel_list=hotel_list, car_list=car_list)



@app.route('/filghtDate', methods=['GET','POST'])
def filghtDate(selectedDate=None,statusselect1=None, statusselect2=None):
    if request.method == 'POST':
        pass
    else:
        selectedDate = request.args.get('selectedDate')
        statusselect1 = request.args.get('statusselect1')
        statusselect2 = request.args.get('statusselect2')
        print("geT------------------------",statusselect1)
        print("geT------------------------",statusselect2)
        sql = f'''
            SELECT date, day, name, airport, leavetime, reachtime, seat,charge
            FROM test_db.airplanecrawl
            WHERE date = '{selectedDate}' AND airport = '{statusselect2}'
            AND (
                    ({statusselect1} = 0 AND charge >= 0) OR
                    ({statusselect1} = 1 AND charge >= 0 AND charge < 50000) OR
                    ({statusselect1} = 2 AND charge >= 50000 AND charge < 100000) OR
                    ({statusselect1} = 3 AND charge >= 100000 AND charge < 150000)OR
                    ({statusselect1} = 4 AND charge >= 150000 AND charge < 200000)OR
                    ({statusselect1} = 5 AND charge >= 200000 )
                )
            ORDER BY charge ASC
            LIMIT 200
            '''
        air_data = clinet_bigquery(sql)
        air_list = air_data.to_dict(orient='records')
        hotel_list = hotel_data.to_dict(orient='records')
        car_list = car_data.to_dict(orient='records')
        return render_template('filght.html', air_list=air_list, hotel_list=hotel_list, car_list=car_list)

@app.route('/hotelprice', methods=['GET','POST'])
def hotelprice(statusselect3=None,statusselect4=None ):
    if request.method == 'POST':
        pass
    else:
        statusselect3 = request.args.get('statusselect3')
        statusselect4 = request.args.get('statusselect4')
        print("geT------------------------",statusselect3)
        print("geT------------------------",statusselect4)
        sql = f'''
                SELECT * 
                FROM test_db.hotelcrawl
                where rating != '평점없음' and star is not null
                AND (
                    ({statusselect3} = 0 AND price >= 0) OR
                    ({statusselect3} = 1 AND price >= 0 AND price < 30000) OR
                    ({statusselect3} = 2 AND price >= 30000 AND price < 50000) OR
                    ({statusselect3} = 3 AND price >= 50000 AND price < 100000)OR
                    ({statusselect3} = 4 AND price >= 100000 AND price < 200000)OR
                    ({statusselect3} = 5 AND price >= 200000 )
                )
                AND  address = '{statusselect4}'
                order by star desc, price asc
                LIMIT 200;
                '''
        hotel_data = clinet_bigquery(sql)
        air_list = air_data.to_dict(orient='records')
        hotel_list = hotel_data.to_dict(orient='records')
        car_list = car_data.to_dict(orient='records')

        return render_template('filght.html', air_list=air_list, hotel_list=hotel_list, car_list=car_list)


# test 잔디 심어지는 확인용 1
@app.route('/dashboard1') 
def dashboard1():
    return render_template('dashboard1.html')

if __name__ == '__main__':
    app.run(host="localhost", port="9999", debug=True)  