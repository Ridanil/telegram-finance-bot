create table if not exists income(
    id integer primary key,
    create_date datetime,
    amount integer,
    raw_text text
);


create table if not exists expenses(
    id integer primary key,
    create_date datetime,
    amount integer,
    category_name text,
    raw_text text
);


create table if not exists budget(
    sumary integer
);

insert into budget(sumary) values (500);