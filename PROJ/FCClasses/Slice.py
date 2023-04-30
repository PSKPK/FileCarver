class Slice:
    clusterdata = None
    data = None
    width = None
    
    def __init__(self, cls, cno:str=0):
        self.clusterdata = cls
        self.cno = cno
        self.hexify()

    def hexToDec(self, a):
        ans = 0
        vals = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7,
            '8':8, '9':9, 'a':10, 'b':11, 'c':12, 'd':13, 'e':14, 'f':15}
        mul = 1
        for ptr in range(-1,-len(a)-1,-1):
            ans += vals[a[ptr]]*mul
            mul *= 16
        return ans
        
    def litEndHexToDec(self, a):
        arr = []
        while a!='':
            arr.append(a[-2:])
            a=a[:-2]
        return self.hexToDec(''.join(arr))

    def hexify(self):
        strdata = self.clusterdata
        self.data = []
        for k in range(0, len(strdata), 2):
            self.data.append(self.hexToDec(strdata[k:k+2]))
    
    def estimateWidth(self, minW = 20, maxW = 449):
        min = float('inf')
        width = minW
        actual_width = width
        data = self.clusterdata
        while width<=maxW:
            rows = []
            imgdata=data
            
            while imgdata!='':
                rows.append(imgdata[:width*6])
                imgdata = imgdata[width*6:]
            
            if len(rows[-1])<len(rows[0]):
                rows = rows[:-1]
            
            rowbs = []
            for row in rows:
                bs = []
                while row!='':
                    bs.append(self.hexToDec(row[:2]))
                    row = row[2:]
                rowbs.append(bs)

            total=0
            for i in range(len(rowbs)-1):
                sod=0
                for j in range(len(rowbs[0])):
                    sod+=abs(rowbs[i][j]-rowbs[i+1][j])
                total+=sod
            avgsod=total
            
            if(avgsod<min):
                min=avgsod
                actual_width = width
            
            width = width+1
        self.width = actual_width

    def GenerateImage(self, name:str=None, picformat:str=''):
        if name==None:
            print('No name given')
            return
        elif picformat==None:
            print('No format given')
            return
        w = self.width
        import numpy as np
        from PIL import Image
        pixels = []+self.data
        pixels.reverse()
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
        nparray = []
        while pixelarray != []:
          nparray.append(list(pixelarray[:w][::-1]))
          if len(nparray[-1]) != w:
            nparray = nparray[:-1]
            break
          pixelarray = pixelarray[w:]
        array = np.array(nparray, dtype=np.uint8)
        new_image = Image.fromarray(array)
        new_image.save(name+picformat)

