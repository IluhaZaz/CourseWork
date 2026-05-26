from fastapi import FastAPI, HTTPException
from fastapi.security import HTTPBasic
from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE

app = FastAPI()
security = HTTPBasic()

LDAP_SERVER = "10.0.10.2"
LDAP_PORT = 636
LDAP_BASE_DN = "DC=todolist,DC=lan"
LDAP_ADMIN = "IliyaZaz@todolist.lan"
LDAP_ADMIN_PASS = "2222.?Iz1111"


def authenticate_by_email(email: str, password: str):
    """Аутентификация по email через userPrincipalName"""
    try:
        server = Server(LDAP_SERVER, port=LDAP_PORT, use_ssl=True)
        conn = Connection(server, user=email, password=password, auto_bind=True)
        conn.unbind()
        return True
    except Exception as e:
        print(f"Auth failed for {email}: {e}")
        return False


def check_user_exists(email):
    """Проверка существования пользователя в AD"""
    try:
        server = Server(LDAP_SERVER, port=LDAP_PORT, use_ssl=True)
        conn = Connection(server, LDAP_ADMIN, LDAP_ADMIN_PASS, auto_bind=True)

        search_filter = f"(&(objectClass=user)(userPrincipalName={email}))"
        conn.search(
            search_base=LDAP_BASE_DN,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=['cn', 'sAMAccountName', 'userPrincipalName', 'userAccountControl']
        )

        if conn.entries:
            print(f"✅ Пользователь найден: {conn.entries[0]}")
            return True
        else:
            print(f"❌ Пользователь {email} не найден")
            return False

    except Exception as e:
        print(f"Error checking user: {e}")
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.unbind()


def register_user(email, password) -> bool:
    username = email.split('@')[0]
    target_ou = "OU=Staff,DC=todolist,DC=lan"
    user_dn = f"CN={username},{target_ou}"

    try:
        server = Server(LDAP_SERVER, port=LDAP_PORT, use_ssl=True)
        admin_conn = Connection(server, user=LDAP_ADMIN, password=LDAP_ADMIN_PASS, auto_bind=True)

        check_filter = f"(sAMAccountName={username})"
        admin_conn.search(LDAP_BASE_DN, check_filter, SUBTREE)
        if admin_conn.entries:
            print(f"⚠️ Пользователь {username} уже существует")
            admin_conn.unbind()
            return False

        quoted_password = f'"{password}"'
        encoded_password = quoted_password.encode('utf-16-le')

        attrs = {
            'objectClass': ['top', 'person', 'organizationalPerson', 'user'],
            'cn': username,
            'sn': username,
            'sAMAccountName': username,
            'userPrincipalName': email,
            'displayName': username,
            'unicodePwd': encoded_password,
            'userAccountControl': '514'
        }

        success = admin_conn.add(user_dn, attributes=attrs)

        if not success:
            print(f"Ошибка создания пользователя: {admin_conn.result}")
            admin_conn.unbind()
            return False

        activation_success = admin_conn.modify(user_dn, {'userAccountControl': [(MODIFY_REPLACE, ['512'])]})

        if activation_success:
            print(f"✅ Пользователь {email} успешно создан и активирован!")
            admin_conn.unbind()
            return True
        else:
            print(f"⚠️ Пользователь создан, но не активирован: {admin_conn.result}")
            admin_conn.unbind()
            return False

    except Exception as e:
        print(f"Ошибка регистрации: {e}")
        if 'admin_conn' in locals() and admin_conn:
            admin_conn.unbind()
        return False

def ldap_auth(email: str, password: str):
    res = authenticate_by_email(email, password)
    if not res:
        raise HTTPException(status_code=402, detail="LDAP auth failed")


if __name__ == "__main__":
    print("\n=== Проверка существующих пользователей ===")
    check_user_exists("IliyaZaz@todolist.lan")
    check_user_exists("PV@todolist.lan")

    print("\n=== Регистрация нового пользователя ===")
    register_user("newuser@todolist.lan", "2222.?Iz3333")

    print("\n=== Проверка созданного пользователя ===")
    res = authenticate_by_email("newuser@todolist.lan", "2222.?Iz3333")
    print(f"Аутентификация: {res}")

    check_user_exists("newuser@todolist.lan")

