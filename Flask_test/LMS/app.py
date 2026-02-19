import os

from flask import Flask, render_template, request, session, redirect, url_for
from LMS.common import Session

app = Flask(__name__)
app.secret_key = 'a12345678'


# -------------- Member CRUD 시작 --------------------

# --------- 로그인 ---------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    uid = request.form['uid']
    upw = request.form['upw']
    print("/login에서 넘어온 폼 데이터 출력 테스트")
    print(uid, upw)
    print("===========================")

    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT id, name, uid, email, role     \
                FROM members WHERE uid = %s AND password = %s"
            cursor.execute(sql, (uid, upw))
            user = cursor.fetchone()

            if user:
                session["user_id"] = user['id']
                session["user_name"] = user['name']
                session["user_uid"] = user['uid']
                session["user_email"] = user['email']
                session["user_role"] = user['role']

                return redirect(url_for('index'))

            else:
                return "<script>alert(아이디나 비밀번호가 일치하지 않습니다.);history.back()</script>"

    finally:
        conn.close()

# --------- 로그아웃 ---------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --------- 화원가입 ---------
@app.route('/join', methods=['GET', 'POST'])
def join():

    # 사용할 이메일 리스트
    domain_list = ['gmail.com', 'naver.com', 'daum.net']

    if request.method == 'GET':
        return render_template('join.html', domains = domain_list)

    # 1. 공통 데이터 가져오기
    action = request.form.get('action')
    uid = request.form.get('uid')
    name = request.form.get('name')
    password = request.form.get('password')
    email_id = request.form.get('email_id')
    email_domain = request.form.get('email_domain')
    email_domain_direct = request.form.get('email_domain_direct')

    another_domain = email_domain_direct if email_domain == 'direct' else email_domain

    conn = None # conn 초기화
    try:
        conn = Session.get_connection()
        with conn.cursor() as cursor:
            # ---- 아이디 중복확인 버튼을 눌렀을 시 ----
            if action == 'check_id':
                cursor.execute("SELECT id FROM members WHERE uid = %s", (uid,))
                is_duplicate = cursor.fetchone() is not None
                msg = "이미 존재하는 아이디입니다." if is_duplicate else "사용 가능한 아이디입니다."

                return render_template('join.html',
                                       msg=msg,
                                       is_duplicate=is_duplicate,
                                       uid=uid, name=name,
                                       domains=domain_list,
                                       password=password,
                                       email_id=email_id, email_domain=email_domain,
                                       email_domain_direct=email_domain_direct)

            # ---- 확인 후 가입 버튼을 눌렀을 때 ----
            elif action == 'join':
                # 가입 전 한 번 더 중복 체크 (보안상 권장)
                cursor.execute("SELECT id FROM members WHERE uid = %s", (uid,))
                if cursor.fetchone():
                    return "<script>alert('이미 사용 중인 아이디입니다.'); history.back();</script>"

                # 이메일 합치기 및 저장
                email = f"{email_id}@{another_domain}"
                sql = "INSERT INTO members (uid, password, name, email) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (uid, password, name, email))
                conn.commit()  # DB 반영

                return f"<script>alert('회원가입이 완료되었습니다. {name} 님, 환영합니다!'); location.href = '/login';</script>"

    except Exception as e:
        print(f"회원가입 에러 : {e}")
        return f"가입 중 오류가 발생했습니다."

    finally:
        if conn: conn.close()  # 무조건 연결 종료

# --------- 회원 수정 ---------

@app.route('/member/edit', methods=['GET', 'POST'])
def member_edit():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = Session.get_connection()

    try :
        with conn.cursor() as cursor:
            if request.method == 'GET':
                cursor.execute("SELECT * FROM members WHERE id = %s", (session["user_id"],))
                user_info = cursor.fetchone()
                return render_template('member_edit.html', user = user_info)

            new_name = request.form.get('name')
            new_pw = request.form.get('password')
            new_bio = request.form.get('bio')

            if new_pw:
                sql = "UPDATE members SET name = %s, password = %s, bio = %s WHERE id = %s"
                cursor.execute(sql, (new_name, new_pw, new_bio, session["user_id"]))
            else :
                sql = "UPDATE members SET name = %s, bio = %s WHERE id = %s"
                cursor.execute(sql, (new_name, new_bio, session["user_id"]))

            conn.commit()
            session['user_name'] = new_name
            session['user_bio'] = new_bio
            return "<script>alert('정보가 수정되었습니다.'); location.href = '/mypage';</script>"

    except Exception as e:
        print(f"회원수정 에러 : {e}")
        return "수정 중 오류가 발생했습니다."

@app.route('/mypage')
def mypage():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = Session.get_connection()

    try :
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM members WHERE id = %s", (session["user_id"],))
            user_info = cursor.fetchone()

            cursor.execute("SELECT COUNT(*) as board_count FROM boards WHERE id = %s", (session["user_id"],))
            board_count = cursor.fetchone()['board_count']

            return render_template('mypage.html', user = user_info, board_count = board_count)

    finally:
        conn.close()

# -------------- Member CRUD 완 --------------------
# -------------- Board CRUD ------------------------

# -------------- Board CRUD 완 ----------------------

@app.route('/')
def index():
    return render_template('main.html')


if __name__ == '__main__':
    app.run(host='192.168.0.172', port=5025, debug=True)
