# coding: utf-8

from config import Page
from db.base import DBbase
from pymysql import escape_string

"""
CREATE TABLE `sms_success` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `channel_id` int(11) NOT NULL,
  `to` varchar(100) DEFAULT NULL,
  `yzm` varchar(200) DEFAULT NULL,
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `description` varchar(200) DEFAULT 'SUCCESS',
  `message_id` varchar(100) DEFAULT '0' COMMENT '唯一id',
  `is_active` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
"""


class SuccessDB(DBbase):
    """发送历史数据表管理"""
    def __init__(self):
        super().__init__()

    def add(self, to, yzm, channel_id, message_id):
        new_text = escape_string(yzm)
        sql = f'insert into sms_success (`to`,yzm,message_id,channel_id) values ("{to}","{new_text}","{message_id}",{channel_id});'
        return self.execute(sql, commit=True)

    @staticmethod
    def _handle_query(channel, to, start, end, need_end=True):
        where_sql = 'where is_active=1'
        if start and end:
            where_sql += f' and create_time>="{start} 00:00:00" and create_time <="{end} 23:59:59"'
        if channel and channel != '0':
            where_sql += f' and channel_id={channel}'
        if to:
            where_sql += f' and `to` like "%{to}%"'
        return where_sql + ';' if need_end else where_sql

    def get_history(self, channel, to, status, start, end, page, limit=Page.history_limit):
        where_sql = self._handle_query(channel, to, start, end, need_end=False)
        channel_name_sql = '(select name from sms_channel where id=channel_id) as channel_name'
        base_sql = 'select %s,`to`,yzm,create_time,description from'
        if status == '0':
            # 全部
            sql = f'{base_sql % channel_name_sql} ({base_sql % "channel_id"} sms_success {where_sql} union all ' \
                  f'{base_sql % "channel_id"} sms_failed {where_sql} union all {base_sql % "channel_id"} sms_pending ' \
                  f'{where_sql}) as c'
        elif status == '1':
            # 成功
            sql = f'{base_sql % channel_name_sql} sms_success {where_sql}'
        elif status == '2':
            # 失败
            sql = f'{base_sql % channel_name_sql} sms_failed {where_sql}'
        elif status == '3':
            # 等待
            sql = f'{base_sql % channel_name_sql} sms_pending {where_sql}'
        limit_sql = ' order by create_time desc limit {},{};'.format(page * limit if page else 0, limit)
        sql += limit_sql
        return self.execute(sql, fetch=True)

    def get_page(self, channel, to, status, start, end, limit=Page.history_limit):
        where_sql = self._handle_query(channel, to, start, end, need_end=False)
        if status == '0':
            sql = f'select count(id) from (select id from sms_success {where_sql} union all select id from sms_failed' \
                  f' {where_sql} union all select id from sms_pending {where_sql}) as c;'
        elif status == '1':
            sql = f'select count(id) from sms_success {where_sql};'
        elif status == '2':
            sql = f'select count(id) from sms_failed {where_sql};'
        elif status == '3':
            sql = f'select count(id) from sms_pending {where_sql};'
        db_count = self.execute(sql, fetch=True)
        page_list = [i + 1 for i in range(db_count[0][0] // limit)]
        page_list = page_list if page_list else [1]
        if db_count[0][0] > limit and (db_count[0][0] % limit != 0):
            page_list.append(page_list[-1] + 1)
        return len(page_list), db_count[0][0]
