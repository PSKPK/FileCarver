class Classifier():
    def __init__(self, cls):
        self.cls = cls
    
    def GetBMPRoots(self):
        res = {}
        for c in self.cls.keys():
            if self.cls[c][:4].upper()=='424D':
                res[c] = self.cls[c]
        return res