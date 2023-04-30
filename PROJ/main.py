from kivy.app import App
from kivy.config import Config
Config.set('graphics','resizable',False)
from kivy.core.window import Window
from kivymd.app import MDApp

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image as KvImg
from kivy.clock import Clock

from FCClasses.DAC import DiskAnalyzer
from FCClasses.Classifier import Classifier
from FCClasses.Slice import Slice
from FCClasses.Orderer import Orderer

import os
import threading
import time
import numpy as np
from PIL import Image

class MyCheckBox(CheckBox):
    def __init__(self, name:str='DefaultName', **kwargs):
        super(CheckBox,self).__init__(**kwargs)
        self.name = name

class MyLabel(Label):
    def on_size(self, *args):
        self.text_size  = self.size

class UILayout(FloatLayout):
    def MakeHomeWidgets(self):
        self.IntroLabel     = Label(text ="Welcome to using the BMP_FILE_CARVING_APP!", color='black', size_hint=(1,.1), pos_hint={'x':0,'y':.7}, font_size=30)
        self.HomePathLabel  = Label(text='Enter the disk file path here :', color='black', size_hint=(.2,.1), pos_hint={'x':.2,'y':.46})
        self.FilePathInput  = TextInput(text='', hint_text='Enter path here', size_hint=(.6,.08), pos_hint={'x':.2, 'y':.4}, multiline=False, on_text_validate=self.ValidateFile)
        self.HomeSubmit     = Button(text='Submit', size_hint=(.3,.1), pos_hint={'x':.35, 'y':.1}, on_press=self.ValidateFile, color='white', background_color='black')
        self.HomeErrorLabel = Label(text="", color='red', size_hint=(1,.2), pos_hint={'x':0, 'y':.2})
        return [self.IntroLabel, self.HomePathLabel, self.FilePathInput, self.HomeSubmit, self.HomeErrorLabel]
    
    def MakeMetaWidgets(self):
        self.MetaLabel      = Label(text="Metadata of the disk file provided", color='blue', size_hint=(1,.1), pos_hint={'x':0,'y':.8}, font_size=30,)
        self.MetaFilenameL  = MyLabel(text="Name of the file ", color='black', size_hint=(.6,.1), pos_hint={'x': .1,'y': .65}, halign="left")
        self.MetaTotalClsL  = MyLabel(text="Total number of clusters in disk", color='black', size_hint=(.5,.1), pos_hint={'x': .1,'y': .60}, halign="left")
        self.MetaUsedClsL   = MyLabel(text="Total number of used clusters ", color='black', size_hint=(.5,.1), pos_hint={'x': .1,'y': .55}, halign="left")
        self.MetaFreeClsL   = MyLabel(text="Total number of free clusters ", color='black', size_hint=(.5,.1), pos_hint={'x': .1,'y': .50}, halign="left")
        self.MetaCleanClsL  = MyLabel(text="Total number of clean (useless) clusters ", color='black', size_hint=(.5,.1), pos_hint={'x': .1,'y': .45}, halign="left")
        self.MetaUsefulClsL = MyLabel(text="Total number of useful clusters for file carving ", color='black', size_hint=(.5,.1), pos_hint={'x': .1,'y': .40}, halign="left")
        self.MetaFCClsL     = MyLabel(text="Identified BMP root clusters for file carving ", color='black', size_hint=(.5,.1), pos_hint={'x': .1,'y': .30}, halign="left")
        
        self.MetaFilename   = MyLabel(text=self.Filename, color='black', size_hint=(.5,.1), pos_hint={'x': .3,'y': .65}, halign="right")
        self.MetaTotalCls   = MyLabel(text=str(self.da.NumOfCls), color='black', size_hint=(.5,.1), pos_hint={'x': .3,'y': .60}, halign="right")
        self.MetaUsedCls    = MyLabel(text=str(self.da.UsedCls[0]), color='black', size_hint=(.5,.1), pos_hint={'x': .3,'y': .55}, halign="right")
        self.MetaFreeCls    = MyLabel(text=str(self.da.FreeCls[0]), color='black', size_hint=(.5,.1), pos_hint={'x': .3,'y': .50}, halign="right")
        self.MetaCleanCls   = MyLabel(text=str(self.da.CleanCls[0]), color='black', size_hint=(.5,.1), pos_hint={'x': .3,'y': .45}, halign="right")
        self.MetaUsefulCls  = MyLabel(text=str(self.da.FCCls[0]), color='black', size_hint=(.5,.1), pos_hint={'x': .3,'y': .40}, halign="right")
        rts = Classifier(self.da.getCls(self.da.FCCls[1])).GetBMPRoots()
        self.MetaFCCls      = MyLabel(text=str(len(rts.keys()))+' : '+','.join(map(str,rts.keys())), color='black', size_hint=(.5,.1), pos_hint={'x': .3,'y': .30}, halign="right")

        return [self.MetaLabel, self.MetaFilenameL, self.MetaTotalClsL, self.MetaUsedClsL, self.MetaFreeClsL, self.MetaCleanClsL, self.MetaUsefulClsL, self.MetaFCClsL,
                    self.MetaFilename, self.MetaTotalCls, self.MetaUsedCls, self.MetaFreeCls, self.MetaCleanCls, self.MetaUsefulCls, self.MetaFCCls,
                    Button(text='Go to next screen', size_hint=(.3,.1), pos_hint={'x':.35, 'y':.1}, on_press=lambda b: self.MakeClassPage(), color='white', background_color='black')]
    
    def MakeClassWidgets(self):
        self.ClassLabel       = Label(text="Classification of the clusters into BMP clusters\nYou can opt for manual or automated classification", color='blue', size_hint=(1,.1), pos_hint={'x':0,'y':.8}, font_size=30,)
        self.ClassAutoChk     = MyCheckBox(name='Auto', size_hint=(.02,.02), pos_hint={'x':.1,'y':.7}, color='blue', on_press=self.AutoManCheck)
        self.ClassManualChk   = MyCheckBox(name='Manual', size_hint=(.02,.02), pos_hint={'x':.1,'y':.65}, color='blue', on_press=self.AutoManCheck, active=True)
        self.ClassUserChoice  = 'Manual'
        self.ClassAutoL       = MyLabel(text='Automatic Classification', color='black', size_hint=(.5,.1), pos_hint={'x': .15,'y': .7}, halign="left")
        self.ClassManualL     = MyLabel(text='Manual Classification', color='black', size_hint=(.5,.1), pos_hint={'x': .15,'y': .65}, halign="left")
        self.ClassSelBtnsL    = MyLabel(text='Select BMP clusters you want to work on : ', color='black', size_hint=(.5,.1), pos_hint={'x':.1,'y':.55}, halign="left")
        self.ClassSelBtns     = TextInput(hint_text='Selected cluster numbers will appear here', size_hint=(.4,.07), multiline=True, pos_hint={'x':.1, 'y':.47}, readonly=True)
        self.ClassErrorLabel  = MyLabel(text='', color='red', size_hint=(.5,.1), pos_hint={'x':.1,'y':.42}, halign="left")
        self.BtnsList         = []
        temp = 0
        cols = 8
        self.SelectedBtns     = []
        for cno in self.da.FCCls[1]:
            self.BtnsList.append(MyCheckBox(name=str(cno), size_hint=(.02,.02), pos_hint={'x':.1+.1*(temp%cols),'y':.35-.03*(temp//cols)}, color='blue', on_press=self.ClassSelFunc))
            self.add_widget(Label(text=str(cno), color='black', size_hint=(.1,.1), pos_hint={'x':.09+.1*(temp%cols), 'y':.31-.03*(temp//cols)}, halign='left'))
            temp+=1

        return self.BtnsList + [self.ClassLabel, self.ClassAutoChk, self.ClassAutoL, self.ClassManualChk, self.ClassManualL, self.ClassSelBtnsL, self.ClassSelBtns, self.ClassErrorLabel,
                Button(text='Go to next screen', size_hint=(.2,.1), pos_hint={'x':.7, 'y':.45}, on_press=lambda b: self.MakeWidthPage(), color='white', background_color='black')]
    
    def MakeWidthWidgets(self):
        self.WidthLabel       = Label(text="Width estimation of fragments in progress..", color='blue', size_hint=(1,.1), pos_hint={'x':0,'y':.8}, font_size=30)
        self.WidthLeave       = Button(text='Proceed', size_hint=(.2,.1), pos_hint={'x':.7, 'y':.45}, on_press=lambda b: self.MakeDisplayPage(), color='white', background_color='black', disabled=True)
        self.WidthProgress    = Label(text="Progress : 0%", color='green', size_hint=(.3,.1), pos_hint={'x':.65,'y':.55}, font_size=20)
        self.WidthEstimates   = TextInput(text='', readonly=True, multiline=True, size_hint=(.4,.6), pos_hint={'x':.15, 'y':.1})
        self.ImageSlices      = {}
        for cno in self.SelectedBtns:
            self.ImageSlices[cno] = Slice(self.da.getCls([int(cno)])[int(cno)], cno)
        self.ptr    = len(self.SelectedBtns)-1
        self.temp   = 0
        self.addlbl = []
        lock = threading.Lock()
        threads = []
        for th in range(4):
            threads.append(threading.Thread(target=self.prcfnc, args=(lock, str(th+1))))
        
        for th in threads:
            th.start()
        
        self.clock = Clock.schedule_interval(self.addlbls, 1)
        return [self.WidthLabel, self.WidthLeave, self.WidthProgress, self.WidthEstimates,
                MyLabel(text="Estimated widths : ", color='black', size_hint=(.3,.1), pos_hint={'x':.15,'y':.71})]

    def addlbls(self, *args):
        if self.temp>=len(self.SelectedBtns):
            self.clock.cancel()
            self.WidthLeave.disabled = False
            self.WidthProgress.text = 'Progress : 100%'
            self.WidthLabel.text = 'Width estimation complete !!'
            self.WidthLabel.color = 'green'
            return
        if self.addlbl==[]:
            return
        cno = self.addlbl[-1]
        self.WidthEstimates.text += 'Estimated width of cluster '+cno+' : '+str(self.ImageSlices[cno].width)+'\n'
        #self.add_widget(MyLabel(text='Estimated width of cluster '+cno+' : '+str(self.ImageSlices[cno].width), size_hint=(1,.1), pos_hint={'x':.1,'y':.7-self.temp*.05}, color='black', halign='left'))
        self.addlbl.remove(cno)
        self.temp+=1
        self.WidthProgress.text = "Progress : "+str(round((self.temp/len(self.SelectedBtns)*100), 2))+"%"
    
    def MakeDisplayWidgets(self):
        self.GeneratedImages = []
        self.imagenames = []
        self.o = Orderer(list(self.ImageSlices.values()))
        self.o.SimilarityMatrix(prnt=0)
        order = self.o.Order(prnt=0)
        time.sleep(1)
        self.DisplayProgress.text = 'Progress : 25%'
        temp = self.SelectedBtns.copy()
        groups = []
        time.sleep(1)
        self.DisplayProgress.text = 'Progress : 40%'
        while temp!=[]:
            newl = []
            head = temp[0]
            while head not in newl:
                newl.append(head)
                temp.remove(head)
                head = order[head]
            groups.append(newl)
        self.DisplayProgress.text = 'Progress : 50%'
        time.sleep(1)
        self.DisplayLabel.text = 'Clusters grouped!!\nGenerating images from clusters'
        tmp = 1
        for grp in groups:
            wd = {}
            maxw = [0,0]
            for sln in grp:
                width = self.ImageSlices[sln].width
                wd[width] = wd.get(width,0) + 1
                if maxw[1]<wd[width]:
                    maxw = [width, wd[width]]
            o2 = Orderer([self.ImageSlices[k] for k in grp])
            o2.SimilarityMatrix(prnt=0)
            o2ord = o2.Order(prnt=0)
            pix1 = []
            pix2 = []
            for k in range(3):
                pix1.append(o2.GenerateImage(name='Image'+str(tmp), w=maxw[0], picformat='.bmp', byos=k, imos=0, start=grp[0]))
            for os in range(3):
                for row in pix1[os]:
                    pix2.append(row+row)
            arr = np.array(pix2, dtype=np.uint8)
            new_image = Image.fromarray(arr)
            new_image.save('Image'+str(tmp)+'.bmp')
            self.imagenames.append('Image'+str(tmp)+'.bmp')
            tmp += 1
            time.sleep(1)
            self.DisplayProgress.text = 'Progress : '+str(50+50*round(tmp/len(groups), 2))+'%'
        self.DisplayProgress.text = 'Progress : 100%'
        self.DisplayLabel.text = 'Images generated !!!'
        self.DisplayLabel.color = 'green'
        self.DisplayBtn.disabled = False
        self.DisplayBtn.background_color = 'green'


    def __init__(self,**kwargs):
        super(UILayout,self).__init__(**kwargs)
        self.MakeHomePage()
    
    def MakeHomePage(self):
        self.CurWidgets = self.MakeHomeWidgets()
        for wid in self.CurWidgets:
            self.add_widget(wid)
    
    def MakeMetadataPage(self):
        for wid in self.CurWidgets:
            self.remove_widget(wid)
        self.da = DiskAnalyzer(self.FilePath)
        self.da.examine()
        self.Filename = ''
        for c in self.FilePath[-1::-1]:
            if c=='/' or c=='\\':
                break
            self.Filename = c+self.Filename
        self.Filename = self.Filename.upper()
        self.clear_widgets()
        self.CurWidgets = self.MakeMetaWidgets()
        for wid in self.CurWidgets:
            self.add_widget(wid)

    def MakeClassPage(self):
        for wid in self.CurWidgets:
            self.remove_widget(wid)
        self.clear_widgets()
        self.CurWidgets = self.MakeClassWidgets()
        for wid in self.CurWidgets:
            self.add_widget(wid)
    
    def MakeWidthPage(self):
        if self.SelectedBtns==[] and self.ClassUserChoice!='Auto':
            self.ClassErrorLabel.text = 'No clusters selected!!'
            return
        elif self.ClassUserChoice=='Auto':
            self.SelectedBtns = [str(cno) for cno in self.da.FCCls[1]]
        self.clear_widgets()
        self.CurWidgets = self.MakeWidthWidgets()
        for wid in self.CurWidgets:
            self.add_widget(wid)
    
    def MakeDisplayPage(self):
        self.clear_widgets()
        self.DisplayLabel = Label(text="Images are being grouped from clusters", color='blue', size_hint=(1,.1), pos_hint={'x':0,'y':.8}, font_size=30)
        self.DisplayProgress = Label(text="Progress : 0%", color='green', size_hint=(.3,.1), pos_hint={'x':.65,'y':.60}, font_size=20)
        self.DisplayBtn = Button(text='Display', size_hint=(.2,.1), pos_hint={'x':.7, 'y':.45}, on_press=self.DisplayMakeImages, color='white', background_color='black', disabled=True)
        self.add_widget(self.DisplayLabel)
        self.add_widget(self.DisplayProgress)
        self.add_widget(self.DisplayBtn)
        th = threading.Thread(target=self.MakeDisplayWidgets)
        th.start()
        self.imgptr = 0
        self.DisplayLeft = Button(text='<', size_hint=(.3,.1), pos_hint={'x':.18, 'y':.1}, on_press=self.DisplayImages, font_size=30, background_color='black', color='white')
        self.DisplayRight = Button(text='>',size_hint=(.3,.1), pos_hint={'x':.52, 'y':.1}, on_press=self.DisplayImages, font_size=30, background_color='black', color='white')
    
    def DisplayImages(self, button):
        self.clear_widgets()
        if button.text=='<':
            self.imgptr = (self.imgptr-1)%len(self.GeneratedImages)
        elif button.text=='>':
            self.imgptr = (self.imgptr+1)%len(self.GeneratedImages)
        self.add_widget(self.GeneratedImages[self.imgptr])
        self.add_widget(self.DisplayLeft)
        self.add_widget(self.DisplayRight)
    
    def DisplayMakeImages(self, button):
        self.GeneratedImages = [KvImg(source=img, size_hint=(.7,.7), pos_hint={'x':.15, 'y':.25}, opacity=1) for img in self.imagenames] #allow_stretch=True, keep_ratio=False
        self.DisplayImages(button)

    def ValidateFile(self, b:Button):
        self.FilePathInput.text = self.FilePathInput.text.strip()
        filepath = self.FilePathInput.text
        if os.path.exists(filepath):
            if filepath[-4:].upper()=='.DSK':
                self.FilePath = filepath
                self.MakeMetadataPage()
            else:
                self.HomeErrorLabel.text = 'Given file is not a .dsk file..\nPlease provide only disk file as input!'
        else:
            self.HomeErrorLabel.text = 'Given path for file is not valid or does not exist!'
    
    def AutoManCheck(self, radbtn):
        if radbtn.name=='Auto':
            self.ClassErrorLabel.text = ''
            self.ClassManualChk.active = False
            self.ClassAutoChk.active = True
            self.ClassUserChoice='Auto'
            self.ClassSelBtnsL.color='grey'
            self.ClassSelBtns.foreground_color='grey'
            for btn in self.BtnsList:
                btn.disabled=True
        elif radbtn.name=='Manual':
            self.ClassManualChk.active = True
            self.ClassAutoChk.active = False
            self.ClassUserChoice='Manual'
            self.ClassSelBtnsL.color='black'
            self.ClassSelBtns.foreground_color='black'
            for btn in self.BtnsList:
                btn.disabled=False
        else:
            print(self.ClassUserCheck)
        return True
    
    def ClassSelFunc(self, chkbox):
        if chkbox.active:
            self.SelectedBtns.append(chkbox.name)
            if self.ClassErrorLabel.text!='':
                self.ClassErrorLabel.text = ''
        else:
            self.SelectedBtns.remove(chkbox.name)
        self.ClassSelBtns.text = ','.join(self.SelectedBtns)
    
    def prcfnc(self, lock, tno):
        while True:
            lock.acquire()
            key = self.ptr
            self.ptr -= 1
            lock.release()
            if key<0:
                #print('Key value : ',key,' thus ending thread', tno)
                break
            cno = self.SelectedBtns[key]
            #print('Estimating width on cno :',cno,' by ',tno)
            self.ImageSlices[cno].estimateWidth()
            self.addlbl.append(cno)
    

    
class BMPFileCarverApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette="Green"
        return UILayout()

BMPFileCarverApp().run()

