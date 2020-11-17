import datetime


class ToolEtc:
    @staticmethod
    def get_now_time() -> str:
        """
        현재 시간 정보를 str 로 반환함.

        :return:  str([2020-11-17][14_05_57])
        """
        _time = datetime.datetime.now()
        return f'[{_time.year}-{_time.month}-{_time.day}][{_time.hour}_{_time.minute}_{_time.second}]'

    @staticmethod
    def get_calculated_time(time_val=int) -> str:
        """
        Sec로 된 시간을 [00:00:00]으로 변환함.

        :param time_val: int(xxxx)
        :return: str([00:00:00])
        """
        t_sec = time_val % 60  # x sec
        t_min = time_val // 60  # x min
        t_hour = t_min // 60
        t_min = t_min % 60

        if t_min >= 10:
            t_min = '{}'.format(t_min)
        else:
            t_min = '0{}'.format(t_min)

        if t_sec >= 10:
            t_sec = '{}'.format(t_sec)
        else:
            t_sec = '0{}'.format(t_sec)

        if t_hour >= 10:
            t_hour = '{}'.format(t_hour)
        else:
            t_hour = '0{}'.format(t_hour)
        return '[{}:{}:{}]'.format(t_hour, t_min, t_sec)
