from werkzeug.security import generate_password_hash


def init_db_data(User, Assortment, Division, db):
    # проверяем существует ли уже тестовый пользователь
    admin_user = db.session.query(User).filter_by(email='admin@admin.com').first()

    # создаем его, если не создан уже
    if not admin_user:
        admin_user = User(name='admin', email='admin@admin.com')
        admin_user.password_hash = generate_password_hash('123')
        db.session.add(admin_user)

        assortments = [
            Assortment(name="Яблоки", measureUnit="кг"),
            Assortment(name="Молоко", measureUnit="л"),
            Assortment(name="Хлеб", measureUnit="шт"),
            Assortment(name="Картофель", measureUnit="кг"),
            Assortment(name="Морковь", measureUnit="кг"),
        ]
        db.session.add_all(assortments)

        divisions = ['Подразделение 1', 'Подразделение 2', 'Подразделение 3', 'Подразделение 4', 'Подразделение 5']

        for division_name in divisions:
            division = Division(name=division_name)
            db.session.add(division)

        db.session.commit()
