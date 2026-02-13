import pymysql

class Session:
    login_member = None
    @staticmethod
    def get_connection():
        print("get_connection() 메서드 호출 - mysql에 접속됩니다.")

        return pymysql.connect(
            host = '192.168.0.172',
            user = 'kkk',
            password = '1234',
            db = 'mbc',
            charset = 'utf8mb4',
            cursorclass = pymysql.cursors.DictCursor
            # dict 타입으로 처리함 (딕셔너리타입 k:v)
        )

    @classmethod
    def login(cls, member): # MemberService에서 로그인 객체를 담아놓음
        cls.login_member = member

    @classmethod
    def logout(cls): # 로그아웃 기능 (세션에 있는 객체를 None 처리함)
        cls.login_member = None

    @classmethod
    def is_login(cls): # 로그인 상태 확인
        return cls.login_member is not None
        # 로그인 했으면 True, None 시 False

    @classmethod
    def is_admin(cls): # 로그인한 권한이 admin
        return cls.is_login() and cls.login_member.role == "admin"

    @classmethod
    def is_manager(cls): # 로그인한 권한이 manager
        return cls.is_login() and cls.login_member.role in ("manager", "admin")
