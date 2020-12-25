from db.base import DBbase


"""
CREATE TABLE `sms_channel` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `channel_type` varchar(100) NOT NULL,
  `is_active` tinyint(1) DEFAULT 1,
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `need_report` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
"""


class ChannelDB(DBbase):
    """发送历史数据表管理"""
    def __init__(self):
        super().__init__()

    def get_channel_info(self, channel_type):
        sql = f'select id,need_report from sms_channel where channel_type="{channel_type}";'
        r = self.execute(sql, fetch=True)
        return r[0] if r else (0, 0)

    def get_channel(self):
        data = [{'id': '0', 'name': '全部'}]
        r = self.execute(f'select id,name from sms_channel where is_active=1;', fetch=True)
        return data + [{'id': str(i[0]), 'name': i[1]} for i in r] if r else data
