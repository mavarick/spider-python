#!/usr/bin/env python
#encoding:utf8

URL_DB_CONFIG = {
          "type":       "mysql",     #"mysql",
          "host":       "localhost",     #"127.0.0.1",
          "port":       3306,
          "user":       "root",     #"root",
          "passwd":     "",     #3306
          "db":         "proxy",     #"liuxf",
          "charset":    "utf8",     #"utf8",
          "tablename":  "proxy1"      #"url"
}


# sql to create table
sql_create = '''
CREATE TABLE if not exists `%s` (
`id`  varchar(255) NOT NULL ,
`ip_port`  varchar(255) NOT NULL COMMENT 'with port',
`is_http`  tinyint NULL DEFAULT 1 ,
`is_https`  tinyint NULL ,
`sup_get`  tinyint not NULL DEFAULT 1,
`sup_post`  tinyint NULL ,
`class`  varchar(50) NULL ,
`addr`  varchar(100) NULL ,
`channel`  varchar(100) NULL COMMENT '电信，联通等等' ,
`resp_time`  float NULL DEFAULT 30 COMMENT 'unit is second' ,
`source`  varchar(255) NULL ,
`is_available`  tinyint NULL ,
`is_deleted`  tinyint NULL ,
`insert_time`  datetime NULL ,
`last_changed_time`  datetime NULL ,
PRIMARY KEY (`id`),
UNIQUE INDEX `ip_port_index` (`ip_port`) USING HASH
) DEFAULT CHARACTER SET=utf8;
'''%(URL_DB_CONFIG['tablename'])


sql_insert_update = '''
insert into {0} (id, ip_port, is_http, is_https, sup_get, sup_post, class, addr, channel, resp_time, source,
is_available, is_deleted, insert_time, last_changed_time) values ({1}) on duplicate key update is_http=%s,
is_https=%s, sup_get=%s, sup_post=%s, class=%s, addr=%s, channel=%s, resp_time=%s, source=%s,
is_available=%s, is_deleted=%s, last_changed_time=%s
'''.format(URL_DB_CONFIG['tablename'], ','.join(['%s']*15))







