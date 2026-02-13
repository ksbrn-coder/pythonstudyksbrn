# pip install flask 필수
# flask : 파이썬으로 만든 db 연동 콘솔 프로그램을 웹으로 연결하는 프레임워크
# 프레임워크 : 미리 만들어놓은 틀 안에서 작업하는 공간
# app.py는 플라스크로 서버를 동작하기 위한 파일명 (기본 파일)
# static, templates 폴더 필수 (프론트용 파일 모이는 곳)
# static : 정적 파일을 모아 놓음 (html, css, js)
# templates : 동적 파일을 모아 놓음 (crud 화면, 레이아웃, index 등)

import os

from flask import Flask, request, render_template, session, redirect, url_for
from LMS.common import Session
from LMS.domain import Member
from LMS.service import MemberService

app = Flask(__name__)
app.secret_key = '1234567890'
# 세션을 사용하기 위해 보아키 설정 (아무 문자열이나 입력)



# ----------------- Member CRUD --------------------

@app.route('/login', methods=['GET','POST'])

def login():
    if request.method == 'GET':
        return render_template('login.html')


    uid = request.form['uid']
    upw = request.form['upw']
    print("/login에서 넘어온 폼 데이터 출력 테스트")
    print(uid,upw)
    print("===============================")

    conn = Session.get_connection()
    try :
        with conn.cursor() as cursor:
            sql = "SELECT id, name, uid, role   \
                FROM members WHERE uid = %s AND password = %s"
            cursor.execute(sql, (uid, upw))
            user = cursor.fetchone()

            if user :
                session["user_id"] = user['id']
                session["user_name"] = user['name']
                session["user_uid"] = user['uid']
                session["user_role"] = user['role']

                return redirect(url_for('index'))

            else :
                return "<script>alert('아이디나 비밀번호가 일치하지 않습니다.');history.back();</script>"

    finally:
        conn.close()

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/join', methods=['GET','POST'])
def join():
    if request.method == 'GET':
        return render_template('join.html')

    uid = request.form.get('uid')
    password = request.form.get('password')
    name = request.form.get('name')

    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM members WHERE uid = %s", (uid,))
            if cursor.fetchone() :
                return "<script>alert('이미 존재하는 아이디입니다.');history.back();</script>"

            sql = "INSERT INTO members (uid, password, name) VALUES (%s, %s, %s)"
            cursor.execute(sql, (uid, password, name))
            conn.commit()

            return"<script>alert('회원가입이 완료되었습니다!'); location.href = '/login';</script>"

    except Exception as e:
        print(f"회원가입 에러 : {e}")
        return "가입 중 오류가 발생했습니다. /n join() 메서드를 확인하세요!!!"

    finally:
        conn.close()


@app.route('/member/edit', methods=['GET','POST'])
def member_edit():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = Session.get_connection()

    try:
        with conn.cursor() as cursor:
            if request.method == 'GET':
                cursor.execute("SELECT * FROM members WHERE id = %s", (session["user_id"],))
                user_info = cursor.fetchone()
                return render_template('member_edit.html', user = user_info)

            new_name = request.form.get('name')
            new_pw = request.form.get('password')
            new_bio = request.form.get('bio') # 자기소개 데이터

            if new_pw:
                sql = "UPDATE members SET name = %s, password = %s, bio = %s WHERE id = %s"
                cursor.execute(sql, (new_name, new_pw, new_bio, session["user_id"]))
            else:
                sql = "UPDATE members SET name = %s, bio = %s WHERE id = %s"
                cursor.execute(sql, (new_name, new_bio, session["user_id"]))

            conn.commit()
            session['user_name'] = new_name
            session["user_bio"] = new_pw
            return "<script>alert('정보가 수정되었습니다.'); location.href = '/mypage';</script>"

    except Exception as e:
        print(f"회원수정 에러 : {e}")
        return "수정 중 오류가 발생했습니다. /n member_edit() 메서드를 확인하세요!!!"

    finally:
        conn.close()

@app.route('/mypage')
def mypage():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = Session.get_connection()

    try :
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM members WHERE id = %s", (session["user_id"],))
            user_info = cursor.fetchone()

            cursor.execute("SELECT COUNT(*) as board_count FROM boards WHERE member_id = %s", (session["user_id"],))
            board_count = cursor.fetchone()['board_count']

            return render_template('mypage.html', user = user_info, board_count = board_count)

    finally:
        conn.close()


# ----------------- Member CRUD 완 -----------------

@app.route('/')
def index():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(host='192.168.0.172', port = 5019, debug = True)