# OOP 기반의 Member 객체용

class Member:
    def __init__(self, id, uid, pw, name, role = "user",active = True):
        self.id = id # DB의 PK -> AUTO_INCREMENT 자동번호 생성
        self.uid = uid # 아이디
        self.pw = pw # 비밀번호
        self.name = name # 이름
        self.role = role  # 권한
        self.active = active # 활성화 여부
        # 사용법
        # member = Member("kkw","1234","김기원","user")
        # Member 객체를 member 변수에 넣음

    @classmethod
    def from_db(cls, row: dict):
        #            row : dict(타입 명시) 힌트 / 필수는 아니나 적어두면 좋음
        """
        DictCursor로부터 전달받은 딕셔너리 데이터를 Member 객체로 변환합니다.
        """
        if not row: # cls로 전달된 값이 없으면
            return None

        return cls(
            id = row.get('id'), # id : 2
            uid = row.get('uid'), # uid : kkw
            pw = row.get('password'), # MySQL : pw가 아닌 password / password : 1111
            name = row.get('name'), # name : 김기원
            role = row.get('role'), # role : admin
            active = bool(row.get('active')) # active : 1 -> True
)

    def is_admin(self):
        return self.role == "admin"

    def __str__(self):
        return f"{self.name}(아이디 : {self.uid} / 비밀번호 : {self.pw}) [{self.role}]"