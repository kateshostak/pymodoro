import os

from orm import ORM
from user import User
from arguments_parser import UpdateParser

def get_orm_test(type_, path):
    db = get_db(type_, path)
    os.remove(path)
    if db.type == type_:
        return True
    return False


def create_user_test(type_, path, user):
    db = get_db(type_, path)
    db.create_user(user)
    db_user = db.get_user(user.name, 'work')
    os.remove(path)
    if str(db_user) == str(user):
        return True
    return False


def get_user_test(type_, path, user):
    db = get_db(type_, path)
    db.create_user(user)
    db_user = db.get_user(user.name, 'work')
    os.remove(path)
    if str(db_user) == str(user):
        return True
    return False


def get_db(type_, path):
    orm = ORM()
    return orm.get_orm(type_, path)


def test_manager(types, paths, users, update_profile):
    for type_, path, user in zip(types, paths, users):
        if not get_orm_test(type_, path):
            print(f'get_orm_test failed with type:{type_}, db:{path}') # noqa
        if not get_user_test(type_, path, user):
            print(f'get_user_test failed with type:{type_}, user{user}, db:{path}')
        if not create_user_test(type_, path, user):
           print(f'create_user_test failed with type:{type_}, user:{user}, db:{path}')
        if not delete_user_test(type_, path, user):
            print(f'delete_user_test failed with type:{type_}, user:{user}, db:{path}')
        if not update_user_test(type_, path, user, update_profile):
            print(f'uodate_user_test failed with type:{type_}, user:{user}, db:{path}')


def delete_user_test(type_, path, user):
    db = get_db(type_, path)
    db.create_user(user)
    res = db.delete_user(user.name)
    if res:
        return True
    return False


def update_user_test(type_, path, user, params):
    db = get_db(type_, path)
    db.create_user(user)
    db.update_user(params)
    db_user = db.get_user(user.name, 'work')
    updated_user = user
    for param in params:
        user.update_param(param, value)
    if str(updated_user) == str(db_user):
        return True
    return False


def delete_test_dbs(paths):
    for path in paths:
        os.remove(path)


def main():
    sqlite_user = User(1, 'test', '25', '5', '10', '4')
    json_user = User(None, 'test', '25', '5', '10', '4')
    users = [sqlite_user, json_user]
    types = ['sqlite', 'json']
    paths_to_dbs = ['test_pom.db', 'test_data.json']
    update_params = ['--name', 'test', '--setting', 'work', '--work', '30']
    parser = UpdateParser()
    update_profile = parser.parse_args(update_params)
    test_manager(types, paths_to_dbs, users, update_profile)


if __name__ == '__main__':
    main()
