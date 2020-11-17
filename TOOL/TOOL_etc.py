import datetime


class ToolEtc:
    @staticmethod
    def _get_now_time() -> str:
        """
        현재 시간 정보를 str 로 반환함.

        :return:  [2020-11-17][14_05_57]
        """
        _time = datetime.datetime.now()
        return f'[{_time.year}-{_time.month}-{_time.day}][{_time.hour}_{_time.minute}_{_time.second}]'
