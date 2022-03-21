import psycopg2 as sql

db = sql.connect(
    database='russian_today',
    host='localhost',
    user='postgres',
    password='123456'
)

cursor = db.cursor()

cursor.execute("""
drop table if exists articles;
drop table if exists categories;

create table if not exists categories(
    category_id integer generated always as identity primary key,
    category_name varchar(50) unique
);
create table if not exists articles(
    article_id integer generated always as identity primary key,
    title text,
    date text,
    author text,
    description text,
    image_link text,
    article_link text,
    category_id integer references categories(category_id)
)
""")