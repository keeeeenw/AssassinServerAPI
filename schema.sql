drop table if exists game;
create table game {
    id integer primary key autoincrement,
    title text not null,
    num_player not null
}
