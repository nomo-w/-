# coding: utf-8


from db.base import DBbase
from pymysql import escape_string

"""
CREATE TABLE `sms_failed` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `channel_id` int(11) NOT NULL,
  `to` varchar(100) DEFAULT NULL,
  `yzm` varchar(200) DEFAULT NULL,
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `description` varchar(200) DEFAULT NULL,
  `message_id` varchar(100) DEFAULT '0' COMMENT '唯一id',
  `is_active` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
"""


class FailedDB(DBbase):
    """发送历史数据表管理"""
    def __init__(self):
        super().__init__()

    def add(self, to, yzm, channel_id, description, message_id):
        new_text = escape_string(yzm)
        sql = f'insert into sms_failed (`to`,yzm,description,message_id,channel_id) values ("{to}","{new_text}",' \
              f'"{description}","{message_id}",{channel_id});'
        return self.execute(sql, commit=True)
