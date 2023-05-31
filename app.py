from flask import Flask, redirect, url_for, render_template,request, abort, flash, session, escape
from pymongo import MongoClient
cluster = MongoClient("mongodb+srv://smdoo:Me2sChTXYh49P3Lk@cluster0.ydrdzo1.mongodb.net/?retryWrites=true&w=majority")
db = cluster["software_engineering"]
#유저 정보 db
users = db["user"]
#초기 코인 정보 db
initialCoin = db["initialCoin"]
#initialCoin.insert_one({"_id": 'IC', "number": 100, "price": 100})

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

# 입금
@app.route('/add_money', methods=['GET','POST'])
def add_money():
    username = session['username']
    user_info = users.find_one({"_id":username})
    coin = user_info["coin"]
    money = user_info["money"]
    
    if request.method == 'POST' :
        add_money = int(request.form['addmoney'])
        if add_money<1:
            flash("1원보다 적은 금액은 입금할 수 없습니다!")
            return redirect(url_for('add_money')) 
        else:
            money += add_money
            users.update_one({"_id": username}, {"$set": { "money": money } })
            flash("{}원이 정상적으로 입금되었습니다!".format(add_money))
            return redirect(url_for('mypage')) 
            
    else:
        return render_template('add_money.html', username=username, coin = coin, money = money)
    
#출금
@app.route('/withdraw', methods=['GET','POST'])
def withdraw():
    username = session['username']
    user_info = users.find_one({"_id":username})
    coin = user_info["coin"]
    money = user_info["money"]
    
    if request.method == 'POST' :
        withdraw = int(request.form['withdraw'])
        if withdraw<1:
            flash("1원보다 적은 금액은 출금할 수 없습니다!")
            return redirect(url_for('withdraw')) 
        elif money<withdraw:
            flash("계좌 잔액보다 많은 금액은 출금할 수 없습니다!")
            return redirect(url_for('withdraw')) 
        
        else:
            money -= withdraw
            users.update_one({"_id": username}, {"$set": { "money": money } })
            flash("{}원이 정상적으로 출금되었습니다!".format(withdraw))
            return redirect(url_for('mypage'))
            
    else:
        return render_template('withdraw.html', username=username, coin = coin, money = money)

#코인 판매 페이지(post)
@app.route('/sellcoin', methods = ['POST', 'GET'])
def sellcoin():
    #로그인 유지용 username 저장
    username = session.get('username')
    user_list = users.find_one({"_id":username}) # 현재 로그인 된 유저의 정보
    user_coins = user_list['coin']                # 유저의 보유 코인 개수
    if request.method == 'POST':
        number = int(request.form.get('number'))  #판매할 코인 개수
        price = int(request.form.get('price'))   #판매할 코인의 개당 가격
        total_price = number * price
        if user_coins < number:
            flash("판매하려는 코인 개수가 보유 수량보다 많습니다.")
            return render_template('sellcoin.html', username=username, user_coins=user_coins)
        
        # postedCoin db에 정보 저장
        coin_info = {"sellername": username, "quantity": number, "price": price, "total_price": total_price}
        postedCoin.insert_one(coin_info)
        flash("POST Success!")

        return render_template('sellcoin.html', username=username, user_coins=user_coins)
    else:
        return render_template('sellcoin.html', username=username, user_coins=user_coins)


#코인 구매 페이지
@app.route('/buycoin', methods = ['POST', 'GET'])
def buycoin():
    #로그인 유지용 username 저장
    username = session.get('username')
    user_info = users.find_one({"_id":username})
    coin = user_info["coin"]
    money = user_info["money"]

    #세션에 저장된 유저가 post한 코인 정보 업데이트
    cursor = db.postedCoin.find()
    post_list = []
    post_index = 1
    for document in cursor:
        data = {
            "post_index": post_index,
            "sellername": document["sellername"],
            "quantity": document["quantity"],
            "price": document["price"],
            "total_price": document["total_price"]
        }
        current_post_id = document["_id"]
        postedCoin.update_one({"_id": current_post_id}, {"$set": { "post_index": post_index } })
        post_index += 1
        post_list.append(data)
    
    #marketplace에 있는 초기 코인 정보 업데이트
    initial_list = initialCoin.find_one({"_id":'IC'})
    session["initial_number"] = initial_list['number']
    session["initial_price"] = initial_list['price']
    initial_number = session["initial_number"]   #초기 코인 남은 개수
    initial_price = session["initial_price"]     #초기 코인 개당 가격
    
    # 페이지 번호 가져오기 (기본값: 1)
    page = int(request.args.get('page', 1))
    items_per_page = 6  # 페이지당 아이템 수
    
    # 페이징 처리
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    paginated_documents = post_list[start_index:end_index]
    
    # 다음 페이지 여부 체크
    has_more = len(post_list) > end_index
    
    if request.method == 'POST':
        initial_buy = int(request.form['initialbuy'])   #구매하고자하는 초기 코인 개수
        
        #마켓플레이스의 초기 코인을 구매하는 경우
        if 'buy_initial_coin' in request.form:    
            if initial_buy <1:
                flash("1개 이상의 코인을 입력해주세요.")
                return render_template('buycoin.html', username=username, page=page, initial_number=initial_number, initial_price=initial_price, documents=paginated_documents, has_more=has_more, coin=coin, money=money)
            elif initial_buy > initial_number:
                flash("마켓에 남아있는 코인이 부족합니다.")
                return render_template('buycoin.html', username=username, page=page, initial_number=initial_number, initial_price=initial_price, documents=paginated_documents, has_more=has_more, coin=coin, money=money)
            elif money<initial_buy*100:
                flash("계좌 잔액이 부족합니다!")
                return render_template('buycoin.html', username=username, page=page, initial_number=initial_number, initial_price=initial_price, documents=paginated_documents, has_more=has_more, coin=coin, money=money)
            else:
                money -= initial_buy*100
                initial_number -= initial_buy
                coin += initial_buy
                users.update_one({"_id": username}, {"$set": { "money": money, "coin":  coin} })
                initialCoin.update_one({"_id": 'IC'},{"$set": { "number": initial_number} })
                flash("{}개의 코인을 정상적으로 구매하셨습니다!".format(initial_buy))
                return render_template('buycoin.html', username=username, page=page, initial_number=initial_number, initial_price=initial_price, documents=paginated_documents, has_more=has_more, coin=coin, money=money)
        # 유저가 post한 코인을 구매하는 경우
        # 1. 게시물 total_price가 보유 금액보다 비싸다면 구매 불가
        # 2. 구매 가능하면 유저 코인 개수와 잔고, seller 코인 개수와 잔고, post 정보 업데이트
        elif 'buy_posted_coin' in request.form:
            post_index_to_buy = request.form.get('post_index')  # 구매하고자 하는 post의 index
            post_to_buy = postedCoin.find_one({"post_index": post_index_to_buy}) # 구매하고자 하는 post 정보
            quantity_to_buy = post_to_buy["quantity"]
            total_price_to_buy = post_to_buy["total_price"]
            seller_name_of_post = post_to_buy["sellername"]
            
            seller_list = users.find_one({"_id": seller_name_of_post})
            seller_coin = seller_list["coin"]
            seller_money = seller_list["money"]
            
            if money < total_price_to_buy:
                flash("잔액이 부족합니다")
                return render_template('buycoin.html', username=username, page=page, initial_number=initial_number, initial_price=initial_price, documents=paginated_documents, has_more=has_more, coin=coin, money=money)
            else:
                money -= total_price_to_buy
                coin += quantity_to_buy        #구매한 유저의 잔액, 코인 개수 업데이트
                users.update_one({"_id": username}, {"$set": { "money": money, "coin":  coin} })
                
                seller_money += total_price_to_buy
                seller_coin -= quantity_to_buy       #판매한 유저의 잔액, 코인 개수 업데이트
                users.update_one({"_id": seller_name_of_post}, {"$set": { "money": seller_money, "coin":  seller_coin} })
                
                postedCoin.delete_one({"post_index": post_index_to_buy})  #거래 완료된 post 삭제

                flash("거래 성공!")
                return render_template('buycoin.html', username=username, page=page, initial_number=initial_number, initial_price=initial_price, documents=paginated_documents, has_more=has_more, coin=coin, money=money)
    
    else:
        return render_template('buycoin.html', username=username, page=page, initial_number=initial_number, initial_price=initial_price, documents=paginated_documents, has_more=has_more, coin=coin, money=money)
    























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