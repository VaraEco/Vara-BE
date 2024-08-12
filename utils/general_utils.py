
class GeneralUtils:
    @staticmethod
    def get_uuid(name):
        names = name.split('_')
        return names[-1]