from LMS.common import Session # 로그인 정보, db 정보
from LMS.domain import Board # oop Board 객체

class BoardService:
    @classmethod
    def run(cls):
        if not Session.is_login():
            print("로그인 후 이용 가능합니다.")
            return

        while True:
            print(f"\n====== MBC 게시판 ({Session.login_member.name} 접속중.) ======")
            cls.list_board()
            print("1. 글쓰기")
            print("2. 글 상세보기 (수정/삭제 가능)")
            print("0. 뒤로가기")

            sel = input(" >>> ")
            if sel == "1":
                cls.write_board()
            elif sel == "2":
                cls.view_detail()
            elif sel == "0":
                break

    @classmethod
    def write_board(cls):
        print("\n--- 새글 작성 ---")
        title = input("제목 : ")
        content = input("내용 : ")

        conn = Session.get_connection()
        try :
            with conn.cursor() as cursor:
                # create_at는 DB에서 자동으로 들어가므로 생략합니다.
                sql = "INSERT INTO boards (member_id, title, content) VALUES (%s, %s, %s)"
                cursor.execute(sql, (Session.login_member.id, title, content))
                conn.commit()
                print("글이 성공적으로 등록되었습니다.")

        finally:
            conn.close()




    @classmethod
    def list_board(cls):
        print("\n" + "=" * 60)
        print(f"{'번호':<5} | {'제목':<25} | {'작성자':<10} | {'작성일'}")
        print("-" * 60)

        conn = Session.get_connection()
        try :
            with conn.cursor() as cursor:
                sql = """
                            SELECT b.*, m.name
                            FROM boards b
                                    JOIN members m ON b.member_id = m.id
                            ORDER BY b.id DESC \
                            """
                cursor.execute(sql)
                datas = cursor.fetchall()
                for data in datas:
                    # 날짜 형식 처리 (YYYY-MM--DD 형식으로 출력)
                    date_str = data['create_at'].strftime('%Y-%m-%d')
                    print(f"{data['id']:<5} | {data['title']:<25} | {data['name']:<10} | {date_str}")

        finally:
            conn.close()
        print("="*60)

    @classmethod
    def view_detail(cls):
        board_id = input("조회할 글 번호 : ")
        conn = Session.get_connection()
        try :
            with conn.cursor() as cursor:
                sql = """
                    SELECT b.*, m.name, m.uid
                    FROM boards b
                        JOIN members m ON b.member_id = m.id
                    WHERE b.id = %s \
                    """
                cursor.execute(sql, (board_id,))
                row = cursor.fetchone()

                if not row:
                    print("존재하지 않는 글 번호입니다.")
                    return

                print("\n" + "*" * 40)
                print(f"제목 : {row['title']}")
                print(f"작성자 : {row['name']} ({row['uid']})")
                print(f"작성일 : {row['create_at']}")
                print("-" * 40)
                print(row['content'])
                print("*" * 40)

                if row['member_id'] == Session.login_member.id:
                    print("1. 수정    2. 삭제   0. 목록으로")
                    sub_se1 = input(" >>> ")
                    if sub_se1 == "1":
                        cls.update_board(board_id)
                    elif sub_se1 == "2":
                        cls.update_board(board_id)
        finally:
            conn.close()

    @classmethod
    def update_board(cls, board_id):
        new_title = input("수정할 제목 : ")
        new_content = input("수정할 내용 : ")
        conn = Session.get_connection()
        try :
            with conn.cursor() as cursor:
                sql = "UPDATE boards SET title = %s, content = %s WHERE id = %s"
                cursor.execute(sql, (new_title, new_content, board_id))
                conn.commit()
                print("수정 완료!")
        finally:
            conn.close()

    @classmethod
    def delete_board(cls, board_id):
        confirm = input("정말 삭제하시겠습니까? (y/n) : ")
        if confirm.lower() != "y": return

        conn = Session.get_connection()
        try :
            with conn.cursor() as cursor:
                # 테이블 구조에 active 컬럼이 없으므로,  실제 DELETE를 수행합니다.
                sql = "DELETE FROM boards WHERE id = %s"
                cursor.execute(sql, (board_id,))
                conn.commit()
                print("글이 삭제되었습니다.")

        finally:
            conn.close()
            