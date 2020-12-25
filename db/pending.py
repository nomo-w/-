# coding: utf-8


from db.base import DBbase
from pymysql import escape_string
from db.success import SuccessDB
from db.failed import FailedDB

"""
CREATE TABLE `sms_pending` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `channel_id` int(11) NOT NULL,
  `to` varchar(100) DEFAULT NULL,
  `yzm` varchar(200) DEFAULT NULL,
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `description` varchar(200) DEFAULT 'PENDING',
  `message_id` varchar(100) DEFAULT '0' COMMENT '唯一id',
  `is_active` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
"""


class PendingDB(DBbase):
    """发送历史数据表管理"""
    def __init__(self):
        super().__init__()

    def add(self, to, yzm, channel_id,  message_id):
        new_text = escape_string(yzm)
        sql = f'insert into sms_pending (`to`,yzm,message_id,channel_id) values ("{to}","{new_text}","{message_id}",{channel_id});'
        return self.execute(sql, commit=True)

    def update(self, message_id, message, to=None):
        sql = f'select channel_id,`to`,yzm from sms_pending where message_id="{message_id}"'
        if to is None:
            sql += ';'
        else:
            sql += f' and `to`="{to}";'
        r = self.execute(sql, fetch=True)
        if r:
            keys = ['channel_id', 'to', 'yzm']
            dic = dict(zip(keys, r[0]))
            dic['message_id'] = message_id
            if message == 'success':
                with SuccessDB() as db:
                    db.add(**dic)
            else:
                with FailedDB() as db:
                    db.add(**dic, description=message)
            del_sql = f'delete from sms_pending where message_id="{message_id}"'
            if to is None:
                del_sql += ' limit 1;'
            else:
                del_sql += f' and `to`="{to}" limit 1;'
            return self.execute(del_sql, commit=True)
        return False
