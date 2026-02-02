from LMS.common import Session
from LMS.domain import Member

class MemberService:
    # 주소가 아닌, cls로 활용

    @classmethod
    def load(cls):
        conn = Session.get_connection() # lms db를 가져와서 conn에 삽입
        # 예외 발생 가능성 있음
        try :
            with conn.cursor() as cursor:
                cursor.execute("select count(*) as cnt from members")
        #                       Member 테이블에서 개수 나온 것을 cnt 변수에 넣어라
            # cursor.execute() sql문 실행용
            count = cursor.fetchone()['cnt'] # dict 타입으로 출력 -> cnt : 5
            #             .fetchone() : 1개의 결과가 나올 때 readone
            #             .fetchall() : 여러 개의 결과가 나올 때 readall
            #             .fetchmany(3) : 3개의 결과만 보고 싶을 때 (최상위 3개)
            print(f"시스템에 현재 등록된 회원 수는 {count} 명입니다.")

        except : # 예외 발생 문구
            print("MemberService.load() 메서드 오류 발생....")

        finally : # 항상 출력되는 코드
            print("데이터베이스 접속 종료됨....")
            conn.close()

    @classmethod
    def login(cls):
        print("\n[로그인]")
        uid = input("아이디 : ")
        pw = input("비밀번호 : ")

        conn = Session.get_connection()
        # print("Session.get_connection()" + conn)

        try :
            with conn.cursor() as cursor:
                # 아이디와 비밀번호가 일치하는 회원 조회
                sql = "SELECT * FROM members WHERE uid = %s AND password = %s"
                print("sql = " + sql)
                cursor.execute(sql, (uid, pw))
                row = cursor.fetchone()
                # print("row" + row[0])

                if row :
                    member = Member.from_db(row)
                # 계정 활성화 여부 체크
                    if not member.active:
                        print("비활성화된 계정입니다. 관리자에게 문의하세요.")
                        return

                    Session.login(member)
                    print(f"{member.name} 님 로그인 성공 (권한 : {member.role})")

                else :
                    print("아이디 또는 비밀번호가 일치하지 않습니다.")

        except :
            print("MemberService.login() 메서드 오류 발생....")
        finally:
            conn.close()

    @classmethod
    def logout(cls):
        # 먼저 세션에 로그인 정보가 있는지 확인
        if not Session.is_login():
            print("로그인 후 사용해 주세요.")
            return

        # 세션의 로그인 정보 삭제
        Session.logout()
        print("로그아웃 처리되었습니다. 안녕히 가세요!")

    @classmethod
    def signup(cls):
        print("\n[회원가입]")
        uid = input("아이디 : ")

        conn = Session.get_connection()
        try :
            with conn.cursor() as cursor:
                # 중복 체크
                check_sql = "SELECT id FROM members WHERE uid = %s"
                cursor.execute(check_sql, (uid,)) # 튜플은 1개여도 쉼표 필수
                # print("cursor.fetchone() : " + cursor.fetchone()[0]) < 확인용
                if cursor.fetchone() :
                    print("이미 존재하는 아이디입니다.")
                    return

                pw = input("비밀번호 : ")
                name = input("이름 : ")

                # 데이터 삽입
                insert_sql = "INSERT INTO members (uid, password, name) VALUES (%s, %s, %s)"
                cursor.execute(insert_sql, (uid, pw, name))
                conn.commit()
                print(f"회원가입 완료! {name} 님, 로그인해 주세요.")

        except Exception as e:
            conn.rollback()
            print(f"회원가입 오류 : {e}")
        finally:
            conn.close()

    @classmethod
    def modify(cls):
        if not Session.is_login():
            print("로그인 후 사용 가능합니다.")
            return

        member = Session.login_member
        print(f"내 정보 확인 : {member}") # Member.__str__()
        print("\n[내 정보 수정] \n 1. 이름 변경 2. 비밀번호 변경 3. 아이디 변경 4. 계정 비활성화 및 탈퇴 0. 취소")
        sel = input(" >>> ")

        new_name = member.name
        new_pw = member.pw
        new_id = member.uid

        if sel == "1":
            new_name = input("새 이름 : ")
        elif sel == "2":
            new_pw = input("새 비밀번호 : ")
        elif sel == "3":
            new_id = input("새 아이디 : ")

            conn = Session.get_connection()
            try :
                with conn.cursor() as cursor:
                    sql_check = "SELECT COUNT(*) as cnt FROM members WHERE uid = %s"
                    cursor.execute(sql_check, (new_id,))
                    result = cursor.fetchone()

                    if result['cnt'] > 0 :
                        print(f"{new_id} 은(는) 이미 존재하는 아이디입니다.")
                        return
                    else :
                        print("사용 가능한 아이디입니다.")
            finally:
                conn.close()
        elif sel == "4":
            print("회원 비활성화 및 탈퇴를 진행합니다.")
            cls.delete()

        else :
            return

        conn = Session.get_connection()
        try :
            with conn.cursor() as cursor:
                sql = "UPDATE members SET name = %s, uid = %s, password = %s WHERE id = %s"
                cursor.execute(sql, (new_name, new_id, new_pw, member.id))
                conn.commit()

                # 메모리 (세션) 정보도 동기화
                member.name = new_name
                member.uid = new_id
                member.password = new_pw
                print("정보 수정 완료")
                Session.logout()

        finally:
            conn.close()

    @classmethod
    def delete(cls):
        if not Session.is_login():
            member = Session.login_member

            print("\n[회원 탈퇴] \n 1. 완전 탈퇴 2. 계정 비활성화")
            sel = input(" >>> ")

            conn = Session.get_connection()
            try :
                with conn.cursor() as cursor:
                    if sel == "1":
                        sql = "DELETE FROM members WHERE id = %s"
                        cursor.execute(sql, (member.id,))
                        print("회원 탈퇴 완료")

                    elif sel == "2":
                        sql = "UPDATE members SET active = False WHERE id = %s"
                        cursor.execute(sql, (member.id,))
                        print("계정 비활성화 완료")

                    conn.commit()
                    Session.logout()

            finally:
                conn.close()

    @classmethod
    def admin_menu(cls):
        if not Session.is_login():
            print("로그인 후 이용해 주세요.")
            return
        elif not Session.is_admin():
            print("권한이 없습니다.")
            return

        print("\n[관리자 전용 메뉴] \n 1. 회원 목록 확인 2. 회원 블랙리스트 등록 3. 회원 비활성화 해제")
        sel = input(" >>> ")

        if sel == "1":

            conn = Session.get_connection()
            try :
                with conn.cursor() as cursor:
                    sql = "SELECT COUNT(*) as cnt FROM"


