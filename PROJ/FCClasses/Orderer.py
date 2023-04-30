class Orderer:
  def __init__(self, slices=None):
    if slices==None or len(slices)==0:
      return print('Cannot make Orderer instance without slices to order..\n')
    self.slices  = slices
    self.size    = len(slices)

  def FindSim(self, ar1, ar2):
    ans = 0
    for k in range(len(ar1)):
      ans += abs(ar1[k]-ar2[k])
    return ans

  def SimilarityMatrix(self, prnt=1):
    self.mat = [[None for k in range(self.size)] for j in range(self.size)]
    for k in range(self.size):
      w = self.slices[k].width
      for j in range(self.size):
        self.mat[k][j] = self.FindSim(self.slices[k].data[-w*3:], self.slices[j].data[:3*w])
    if prnt==0:
      return
    for k in range(self.size):
      print("{0:<20}".format(k), end='')
      for j in range(self.size):
        print(self.mat[k][j], end =' ')
      print()
  
  def Order(self, prnt=1):
    self.order = {}
    li = []
    for k in range(self.size):
      mindif = float('inf')
      ans = k
      for c in range(self.size):
        if self.mat[k][c]<mindif:
          ans = c
          mindif = self.mat[k][c]
      self.order[self.slices[k].cno] = self.slices[ans].cno
      li.append(ans)
    if prnt!=0:
      print('Order : ', self.order)
    return self.order
  
  def GenerateImage(self, name='Newfile', picformat='.bmp', w=100, byos=0, imos=0, start=0):
    import numpy as np
    from PIL import Image
    pixels = []
    sublis = {}
    for sl in self.slices:
      sublis[sl.cno] = sl
    for c in range(self.size):
      pixels += sublis[start].data
      start = self.order[start]
    pixels.reverse()
    pixels = pixels[byos:]
    pixelarray = []
    while pixels!=[]:
      try:
        pixelarray.append((pixels[0], pixels[1], pixels[2]))
      except IndexError as e:
        pass
      if len(pixelarray[-1]) !=3:
        pixelarray = pixelarray[:-1]
        break
      pixels = pixels[3:]
    # pixelarray = pixelarray[imos:]
    nparray = []
    while pixelarray != []:
      nparray.append(list(pixelarray[:w][::-1]))
      if len(nparray[-1]) != w:
        nparray = nparray[:-1]
        break
      pixelarray = pixelarray[w:]
    # array = np.array(nparray, dtype=np.uint8)
    # new_image = Image.fromarray(array)
    # new_image.save(name+picformat)
    return nparray
