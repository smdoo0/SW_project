from flask import Flask, redirect, url_for, render_template,request, abort, flash, session, escape
from pymongo import MongoClient
cluster = MongoClient("mongodb+srv://smdoo:Me2sChTXYh49P3Lk@cluster0.ydrdzo1.mongodb.net/?retryWrites=true&w=majority")
db = cluster["software_engineering"]
#유저 정보 db
users = db["test"]
#초기 코인 정보 db
initialCoin = db["initialCoin"]
#initialCoin.insert_one({"_id": 'initialCoin', "number": 100, "price": 100})

#유저 posted coin db
postedCoin = db["postedCoin"]

app = Flask(__name__)
app.secret_key = "SECRET_KEY"

#메인페이지
@app.route('/')
def index():
    return render_template('main_new.html')

#마이페이지
@app.route('/mypage')
def mypage():
    username = session['username']
    user_info = users.find_one({"_id":username})
    coin = user_info["coin"]
    money = user_info["money"]
    
    if request.method == 'POST':
        username = session['username']
        
    else:
        return render_template('mypage.html', username=username, coin = coin, money = money) 

#로그인 후 메인페이지
@app.route('/main_after_login')
def main_after_login():
    username = session.get('username')
    return render_template('main_after_login.html', username=username)

#로그인
@app.route('/login_new', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        if users.find_one({"_id":request.form['id']}):  #login_new.html에서 name='id'인 입력값과 같은 id를 db에서 찾음
            id = request.form['id']
            id_list = users.find_one({"_id":id}) #해당 id에 있는 정보 리스트
            if request.form['pw'] == id_list['pw']:
                session['username'] = id
                flash('You have logged in successfully as {}'.format(id))
                return redirect(url_for('main_after_login'))
            else:
                flash("올바르지 않은 비밀번호입니다!")
                return render_template('login_new.html')
        else:
            flash("존재하지 않는 아이디입니다! 회원가입 창으로 이동합니다.")
            return render_template('signup.html')
    else:
        return render_template('login_new.html')      

# 회원가입
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        # 폼 데이터에서 필드 값 추출
        username = request.form['username']
        id = request.form['id']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        
        # 비밀번호 확인
        if password != password_confirm:
            flash("비밀번호가 일치하지 않습니다.")
            return render_template('signup.html')
        
        # 이미 존재하는 id인지 확인
        existing_user = users.find_one({"_id": id})
        if existing_user:
            flash("이미 존재하는 id입니다.")
            return render_template('signup.html')

        # MongoDB에 데이터 삽입
        users.insert_one({"_id": id, "pw": password, "name": username, "coin": 0, "money": 0})
        flash("회원가입 성공!")

        return redirect('login_new')  # 회원가입 후 로그인 페이지로 리디렉션

    return render_template('signup.html')

#코인 판매 페이지(post)
@app.route('/sellcoin', methods = ['POST', 'GET'])
def sellcoin():
    #로그인 유지용 username 저장
    username = session.get('username')
    
    if request.method == 'POST':
        number = request.form.get('number')  #판매할 코인 개수
        price = request.form.get('price')    #판매할 코인의 개당 가격

        # 수행할 작업 수행
        coin_info = {"_id": username, "quantity": number, "price": price}
        postedCoin.insert_one(coin_info)

        return render_template('sellcoin.html', username=username)
    else:
        return render_template('sellcoin.html', username=username)


#코인 구매 페이지
@app.route('/buycoin', methods = ['POST', 'GET'])
def buycoin():
    #로그인 유지용 username 저장
    username = session.get('username')
    
    #세션에 저장된 유저가 post한 코인 정보 업데이트
    initial_list = initialCoin.find_one({"_id":initialCoin})
    cursor = db[postedCoin].find()
    post_list = []
    for post in cursor:
        post_list.append(post)  #post_list 에는 postedCoin db에 있는 딕셔너리들 저장
        
    session["initial_number"] = initial_list['number']
    session["initial_price"] = initial_list['price']
    initial_number = session["initial_number"]   #초기 코인 남은 개수
    initial_price = session["initial_price"]     #초기 코인 개당 가격
    
    if request.method == 'POST':
        return render_template('buycoin.html', username=username)
    else:
        return render_template('buycoin.html', username=username)      























#회원전용기능 알림 메세지
@app.route('/loginfirst')
def loginfirst():
    flash('로그인 후에 이용할 수 있는 기능입니다!')
    return redirect(url_for('login'))

#로그아웃
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('로그아웃 되었습니다.')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug = True)