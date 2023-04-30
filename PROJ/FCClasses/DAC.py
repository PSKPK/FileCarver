class DiskAnalyzer():
  FILE = None
  Cls0 = None
  FATData = None
  ClsData = None
  NumOfCls = None
  FreeCls = None
  UsedCls = None
  CleanCls = None
  FCCls = None
  Clusters = None

  def __init__(self, filename:str =None):
    if filename!=None and filename[-4:].upper()=='.DSK':
      self.FILE = filename
    else:
      if filename==None:
        raise Exception('Cannot initialize DiskAnalyzer without .DSK file')
      else:
        raise Exception('Passed argument is not a .DSK file : '+filename)
  
  def examine(self):
    import binascii
    with open(self.FILE, 'rb') as f:
        data = str(binascii.hexlify(f.read()))[2:-1]
    self.Cls0   = ""
    self.FATData = data[4096*2:4096*4]
    self.ClsData = data[4096*4:]
    self.NumOfCls = len(data)//(8192)
    self.Clusters = {}
    for c in range(self.NumOfCls):
      self.Clusters[c] = data[8192*c:8192*(c+1)]
    self.classifyCls()
  
  def B2D(self, Bytes:str):
    return int(Bytes[2:]+Bytes[:2], 16)

  def classifyCls(self):
    self.FreeCls = [0,[]]
    self.UsedCls = [0,[]]
    curcls = 2
    ptr = 0
    while curcls < self.NumOfCls:
      byte = self.FATData[ptr:ptr+4]
      if self.B2D(byte) != 0:
        self.UsedCls[0] += 1
        self.UsedCls[1].append(curcls)
      else:
        self.FreeCls[0] += 1
        self.FreeCls[1].append(curcls)
      curcls += 1
      ptr += 4
    self.CleanCls = [0, []]
    self.FCCls    = [0, []]
    for cno in self.FreeCls[1]:
      data = self.Clusters[cno]
      if data.count('1A') > 2048 or data.count('1a') > 2048:
        self.CleanCls[0] += 1
        self.CleanCls[1].append(cno)
      else:
        self.FCCls[0] += 1
        self.FCCls[1].append(cno)

  def getCls(self, lis:list=None):
    res = {}
    for c in lis:
      res[c] = self.Clusters[c]
    return res
