from LMS.service import *
from LMS.common.Session import Session
from LMS.service.MemberService import MemberService


def main():
    MemberService.load()

    run = True
    while run:
        print("""
        ======================================
                MBC 아카데미 관리 시스템
        ======================================
        1. 회원 가입   2. 로그인   3. 로그아웃
        4. 회원 관리   5. 게시판   6. 성적관리
        9. 서비스 종료
        """)

        member = Session.login_member
        if member is None:
            print("현재 로그인 상태가 아닙니다.")
        else :
            print(f"{member.name} 님, 환영합니다.")

        sel = input(">>> ")

        if sel == "1":
            pass

        elif sel == "2":
            pass

        elif sel == "3":
            pass

        elif sel == "4":
            pass

        elif sel == "5":
            pass

        elif sel == "6":
            pass

        elif sel == "9":
            run = False

if __name__ == "__main__":
    main()

