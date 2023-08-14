import tkinter as tk
import tkinter.font
import tkinter.messagebox as msgbox
import random
import serial
import serial.tools.list_ports as sp
import threading
import json
import time
import openpyxl

class ExperimentApp:

    def __init__(self, root):
        
        self.root = root
        self.root.title("실험 프로그램 프로토타입")

        self.width = root.winfo_screenwidth()
        self.height = root.winfo_screenheight()
        geometry_string = f"{self.width}x{self.height}"
        self.root.geometry(geometry_string)
        self.root.attributes("-fullscreen", True)
        self.root.resizable(True, True)

        #### JSON initialization #####

        try:
            with open('data.json', 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = {}

        ######### variables ##########

        self.numList = set()
        self.handImages = {"knuckle": tk.PhotoImage(file="knuckle.png"),
                           "back": tk.PhotoImage(file="back.png"),
                           "forearm": tk.PhotoImage(file="forearm.png")}
        self.maximum = 0

        self.idx = 0
        self.scale = 0
        
        self.problemIsStarted = False
        self.isRight = False
        self.reactionTime = int(time.time())
        self.crossings = 0

        self.countDown = 5
        self.subjectName = ""
        self.checkMaximum = False

        self.xlData = list()

        ##############################

        self.frames = []
        for _ in range(23):
            frame = tk.Frame(self.root)
            self.frames.append(frame)
        
        self.current_frame_index = 0    

        self.functionList = []
        self.functionList.append((self.initialPage, (0,)))

        self.show_frame()

        ##############################

        self.setSensor_thread = threading.Thread(target=self.setSensor)
        self.setSensor_thread.daemon = True  # 메인 스레드 종료 시 함께 종료되도록 설정
        self.setSensor_thread.start()
        
        return

    def initialPage(self, page):

        frame = self.frames[page]

        titlefont= tkinter.font.Font(size=96, weight= "bold")
        buttonfont = tkinter.font.Font(size=72, weight= "normal")

        ###############################
        
        top = tk.Frame(frame)
        top.pack(side= "top", fill= "both", expand= True)

        label = tk.Label(top, text="실험 프로그램 프로토타입", font= titlefont)
        label.pack(fill= "both", expand= True)
        
        ###############################

        bottom = tk.Frame(frame)
        bottom.pack(side= "bottom", fill= "both", expand= True)

        entry_frame = tk.Frame(bottom)

        entry = tk.Entry(entry_frame, relief= "raised", font= buttonfont)
        entry.pack(side="left", padx= 20)
        entry.focus()

        check_button = tk.Button(entry_frame, text="중복 확인", command= lambda: self.check_duplicate(str(entry.get()), next_button), font= buttonfont, repeatinterval= 1000)
        check_button.pack(side="right")

        entry_frame.pack(pady= 80)

        ###############################

        next_button = tk.Button(bottom, text="다음", state= "disable", command=self.show_next_frame, font= buttonfont)
        next_button.pack()

    def calibrationPage(self, target, page):
        frame = self.frames[page]

        titlefont= tkinter.font.Font(size= 96, weight= "bold")
        explainfont = tkinter.font.Font(size= 72, weight= "bold")
        buttonfont = tkinter.font.Font(size= 64, weight= "normal")

        ############ title ############
        
        top = tk.Frame(frame)
        top.pack(side= "top", fill= "both", expand= True)

        label = tk.Label(top, text="Calibration", font= titlefont)
        label.pack(fill= "both", expand= True)
        
        ############ image ############

        middle = tk.Frame(frame)
        middle.pack(fill= "both", expand= True)

        label=tkinter.Label(middle, image=self.handImages[target])
        label.pack(pady= 20)

        ###############################

        bottom = tk.Frame(frame)
        bottom.pack(side= "bottom", fill= "both", expand= True)

        measure_button = tk.Button(bottom, text= "측정", font= buttonfont, command= lambda: self.calibrate(next_button))
        measure_button.pack(side= "left", padx= 100)

        next_button = tk.Button(bottom, text="다음", state= "disable", command=self.show_next_frame, font= buttonfont)
        next_button.pack(side= "right", padx= 100)

        self.explain_label = tk.Label(bottom, text= target + " 부분을 측정합니다.\n 측정 버튼을 눌러주세요.", font= explainfont)
        self.explain_label.pack(anchor= "center")

    def calibrate(self, button):
        explainFont = tkinter.font.Font(size= 84, weight= "normal")
        measurementFont = tkinter.font.Font(size= 144, weight= "bold")
        buttonfont = tkinter.font.Font(size= 64, weight= "normal")

        # whenever we calibrate, should initialize maximum value and turn on the checkMaximum.
        self.maximum = 0
        self.checkMaximum = True

        popUp = tk.Toplevel(self.root)
        popUp.title("최고 힘 측정")
        geometry_string = f"{self.width}x{self.height}"
        popUp.geometry(geometry_string)

        explainLabel = tk.Label(popUp, text= "불편하지 않을 정도의 최대의 힘으로 눌러주세요.", font= explainFont)
        explainLabel.place(relx=0.5, rely= 0.25, anchor= "s")

        ##############################

        self.measurementLabel = tk.Label(popUp, text = "0.00", font= measurementFont)
        self.measurementLabel.place(relx = 0.4, rely= 0.75, anchor= "se")

        self.maximumLabel = tk.Label(popUp, text= "0.00", font= measurementFont, fg= "RoyalBlue3")
        self.maximumLabel.place(relx = 0.6, rely= 0.75, anchor= "sw")

        ##############################

        retryButton = tk.Button(popUp, text= "retry", command= lambda: self.retryCalibrateMaximumValue(), font= buttonfont)
        retryButton.place(relx= 0.5, rely= 0.75, x= -20, y= 20, anchor= "ne")

        saveButton = tk.Button(popUp, text= "설정", command= lambda: self.saveMaximumValue(popUp), font= buttonfont)
        saveButton.place(relx= 0.5, rely= 0.75, x= 20, y= 20, anchor= "nw")

        if button != None:
            button.configure(state= "active")
        
        return

    def retryCalibrateMaximumValue(self):
        self.maximum = 0
        self.measurementLabel.config(text= "0.00")

    def saveMaximumValue(self, w):
        if self.maximum > 10:
            if hasattr(self, 'explain_label'):
                self.explain_label.config(text= "측정이 완료되었습니다.\n다음 버튼을 눌러주세요.")
            self.checkMaximum = False
            w.destroy()
        else:
            msgbox.showinfo("측정 오류", "값이 매우 작습니다.\n다시 눌러주세요.")
        
        return
 
    def preExperimentPage(self, page):
        frame = self.frames[page]

        titlefont= tkinter.font.Font(size=96, weight= "bold")
        buttonfont = tkinter.font.Font(size=72, weight= "normal")
        
        top = tk.Frame(frame)
        top.pack(side= "top", fill= "both", expand= True)

        label = tk.Label(top, text= "실험 시작 버튼을 누르면 실험이 시작됩니다.", font= titlefont)
        label.pack(anchor= "s", expand= True)

        bottom = tk.Frame(frame)
        bottom.pack(side= "bottom", fill= "both", expand= True)

        startButton = tk.Button(bottom, text= "실험 시작", font= buttonfont, command= self.show_next_frame)
        startButton.pack(pady= 120)

    def experimentPage(self, target, scale, page):
        
        self.scale = scale
        frame = self.frames[page]
        self.reactionTime = int(time.time())

        # If this page is about Tutorial, do test right after calibration.
        if target == "Tutorial":
            self.calibrate(button= None)

        partFont = tkinter.font.Font(size= 72, weight = "bold")
        progressFont = tkinter.font.Font(size= 32, weight= "normal")

        ###############################

        whichPart = tk.Label(frame, text= target, font= partFont)
        whichPart.place(x= 100, y= 100)
        
        ########### Canvas ############

        self.stickCanvas = tk.Canvas(frame, width= self.width / 10, height = self.height * 0.9)
        self.stickCanvas.place(relx=0.45, rely=0.05)

        stick = self.stickCanvas.create_rectangle(0, 0, self.width / 10, self.height * 0.9, fill= "snow", width= 0)

        x1, y1, x2, y2 = self.stickCanvas.coords(stick)

        self.gapY = (y2 - y1) / scale

        ranges = [i * 0.18 * y2 for i in range(1, 6)]
        self.problems = list()

        for i in range(scale):
            addY = i * self.gapY
            if target != "Tutorial":
                for j in ranges:
                    if addY <= j < addY + self.gapY:
                        self.stickCanvas.create_rectangle(x1, y2 - addY - self.gapY, x2, y2 - addY, fill= "white smoke", width= 0)
                        self.problems.append(y2 - addY - self.gapY)
                        break
            self.stickCanvas.create_line(x1, addY, x2, addY, fill= "light grey")

        self.now = self.stickCanvas.create_rectangle(0, self.height * 0.9, self.width / 10, self.height * 0.9 / scale * (scale + 1), fill= "light pink", width= 0)
        self.sensorBox = self.stickCanvas.create_rectangle(x1, y2, x2, y2 + self.gapY, fill= "pale violet red", width= 0)
        self.sensorLine = self.stickCanvas.create_line(x1, y2, x2, y2, width= self.gapY / 20, fill= "maroon")

        ###############################

        self.progressLabel = tk.Label(frame, text= str(self.idx), font= progressFont)
        self.progressLabel.place(x = self.width - 100, y = self.height - 300, anchor= "se")

        ###############################

        self.nextButton = tk.Button(frame, text= "다음", command= lambda: self.show_problems(scale), font= partFont)
        self.nextButton.place(x = self.width - 100, y = self.height - 100, anchor= "se")

        if target == "Tutorial":
            self.problems = [2 * self.gapY for _ in range(5)]
        else:
            self.problems = self.problems * 4
            random.shuffle(self.problems)
        
        self.show_problems(scale)
    
    def endPage(self, page):
        frame = self.frames[page]

        titlefont= tkinter.font.Font(size=96, weight= "bold")
        buttonfont = tkinter.font.Font(size=72, weight= "normal")
        
        top = tk.Frame(frame)
        top.pack(side= "top", fill= "both", expand= True)

        ###############################

        label = tk.Label(top, text= "실험이 모두 끝났습니다. 감사합니다.", font= titlefont)
        label.pack(anchor= "s", expand= True)

        ###############################

        bottom = tk.Frame(frame)
        bottom.pack(side= "bottom", fill= "both", expand= True)

        endButton = tk.Button(bottom, text= "종료", font= buttonfont, command= self.root.destroy)
        endButton.pack(pady= 120)

        ###############################

        for i in range(len(self.todoList)):
            self.data[self.subjectName][self.todoList[i]] = True
        self.save_data(self.data)

        # need to write codes about analyzing and saving data.

    # In this function, we made pages to integrate.
    def add_content_to_frames(self, day):
        page = 1
        # need to shuffle to counter balance
        random.shuffle(self.todoList)

        if day == 2:
            print("둘째 날입니다. 이 순서대로 진행됩니다.")
            print(*self.todoList, sep= " ")
            for i in range(2):
                self.functionList.append((self.calibrationPage, (self.todoList[i], page))); page += 1
                for j in range(12, 21, 4):
                    self.functionList.append((self.preExperimentPage, (page,))); page += 1
                    self.functionList.append((self.experimentPage, (self.todoList[i], j, page))); page += 1
        else:
            print("첫째 날 타겟 부위는", self.todoList[0], "입니다.")
            self.functionList.append((self.experimentPage, ("Tutorial", 5, page))); page += 1
            self.functionList.append((self.calibrationPage, (self.todoList[0], page))); page += 1
            for j in range(12, 21, 4):
                self.functionList.append((self.preExperimentPage, (page,))); page += 1
                self.functionList.append((self.experimentPage, (self.todoList[0], j, page))); page += 1
        self.functionList.append((self.endPage, (page,)))

    # In this function, we add pages whenever we go to next page.
    def addPage(self, index):
        if 0 <= index < len(self.functionList):
            func, params = self.functionList[index]
            func(*params)

    # In another threads, value of sensor always calculate and change the value.
    def setSensor(self):
        connected_ports = []
        for i in sp.comports():
            connected_ports.append(i.device)
                
        with serial.Serial() as ser:
            ser.port = connected_ports[2]
            ser.baudrate = 9600
            ser.timeout = 10
            ser.write_timeout = 10
            ser.open()

            while ser.is_open:
                line = ser.readline()
                if line:
                    line = line.decode().strip()
                    try:
                        self.value = float(line)
                        if self.checkMaximum and hasattr(self, 'measurementLabel') and hasattr(self, 'maximumLabel'):
                            if self.value > 12:
                                self.maximum = max(self.value, self.maximum)
                                self.root.after(0, self.update_maximum_label, (self.value, self.maximum))

                        if hasattr(self, 'stickCanvas') and hasattr(self, 'sensorLine'):
                            self.moveSensorLine(self.scale)

                    except ValueError:
                        self.value = 0

    # This function shows realtime value and maximum value.
    def update_maximum_label(self, values):
        value, maximum = values
        self.measurementLabel.config(text= str(value))
        self.maximumLabel.config(text=str(maximum))
        self.crossings = 0
        self.isRight = False

    # This function moves line and box including line in realtime.
    def moveSensorLine(self, scale):      
        stickHeight = self.height * 0.9
        fraction = min(self.value / (self.maximum if self.maximum else 1500), 1)
        linePlace = stickHeight - stickHeight * fraction
        x1, _, x2, _ = self.stickCanvas.coords(self.sensorLine)

        for i in range(1, scale + 1):
            if (i - 1) * self.gapY <= linePlace < i * self.gapY:
                self.stickCanvas.coords(self.sensorBox, x1, (i - 1) * self.gapY, x2, i * self.gapY)
                break

        self.stickCanvas.coords(self.sensorLine, x1, linePlace, x2, linePlace)

        # check whether now the lineplace is in right place or not
        problemY = self.stickCanvas.coords(self.now)[1]
        if problemY <= linePlace < problemY + self.gapY:
            if not self.isRight:
                self.isRight = True
        else:
            if self.isRight:
                self.isRight = False
                self.crossings += 1

        
        


    def save_data(self, data):
        with open('data.json', 'w') as file:
            json.dump(data, file, indent=4)       
  
    # This function checks duplicated subject number and sets the inital experiment environments.
    def check_duplicate(self, num, button):
        self.subjectName = num
        targets = ["knuckle", "back", "forearm"]
        random.shuffle(targets)

        if self.subjectName not in self.data:
            self.data[self.subjectName] = { "knuckle": False, "back": False, "forearm": False }
            self.save_data(self.data)
        
            print(f"피험자 {self.subjectName}의 데이터를 추가했습니다.")
            msgbox.showinfo("", "사용 가능한 번호입니다.")
            self.todoList = [targets[0]]

            self.add_content_to_frames(1)
            button.config(state= "active")
        else:
            cnt = 0
            self.todoList = list()
            for i in targets:    
                if self.data[self.subjectName][i]:
                    cnt += 1
                else:
                    self.todoList.append(i)

            if cnt == 1:
                msgbox.showinfo("중복되는 번호", "진행 중인 실험이 있습니다. 이어서 시작합니다.")
                self.add_content_to_frames(2)
                button.config(state= "active")
            else:
                print(f"이미 피험자 {self.subjectName}의 데이터가 존재합니다.")
                msgbox.showinfo("중복되는 번호", "다른 번호를 사용해주세요.")         
   
    # This function shows next problem.
    def show_problems(self, scale):

        checkTime = int(time.time())

        # escape condition
        if self.idx == 20 or (scale == self.idx == 5):
            self.idx = 0

            print("정답인가요?", self.isRight, "crossings", self.crossings, "반응 시간", checkTime - self.reactionTime)
            self.xlData.append([self.isRight, self.crossings, checkTime - self.reactionTime])
            self.isRight = False
            self.crossings = 0

            self.saveXlData()

            self.show_next_frame()
            return
        
        # It does not implement at the first time.
        if self.idx:
            self.timer = tk.Toplevel(self.root)
            self.timer.title("5초 대기 화면")

            titlefont= tkinter.font.Font(size=96, weight= "bold")
            self.timerLabel = tk.Label(self.timer, text= str(self.countDown) + "초 남았습니다.", font=titlefont)
            self.timerLabel.place(relx= 0.5, rely = 0.5, anchor= "s")
            self.updateTimer()

            print("정답인가요?", self.isRight, "crossings", self.crossings, "반응 시간", checkTime - self.reactionTime)
            self.xlData.append([self.isRight, self.crossings, checkTime - self.reactionTime])
            self.isRight = False
            

            self.crossings = 0

        x1, _, x2, _ = self.stickCanvas.coords(self.now) 

        newY = self.problems[self.idx]
        self.stickCanvas.coords(self.now, x1, newY, x2, newY + self.gapY)

        self.idx += 1
        self.progressLabel.config(text= str(self.idx))

    def updateTimer(self):
        if self.countDown > 0:
            self.timerLabel.config(text= str(self.countDown) + "초 남았습니다.")
            self.countDown -= 1
            self.timer.after(1000, self.updateTimer)
        else:
            self.countDown = 5
            self.reactionTime = int(time.time())
            self.timer.destroy()

    def saveXlData(self):
        workbook = openpyxl.Workbook()
        sheet = workbook.active

        for rowIndex, rowData in enumerate(self.xlData, start= 1):
            for colIndex, value in enumerate(rowData, start= 1):
                sheet.cell(row= rowIndex, column= colIndex, value= value)
        
        workbook.save(f"{self.subjectName}번 실험자.xlsx")
        print("파일을 저장하였습니다.")

    def show_frame(self):
        self.addPage(self.current_frame_index)
        frame = self.frames[self.current_frame_index]
        frame.pack(fill=tk.BOTH, expand=True)

    def show_next_frame(self):
        self.frames[self.current_frame_index].pack_forget()
        self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
        self.show_frame()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExperimentApp(root)
    root.mainloop()
