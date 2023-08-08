import tkinter as tk
import tkinter.font
import tkinter.messagebox as msgbox
import random
import serial
import serial.tools.list_ports as sp
import threading

class ExperimentApp:
    # root window, global variables initialization
    def __init__(self, root):
        
        self.root = root
        self.root.title("실험 프로그램 프로토타입")

        self.width = root.winfo_screenwidth()
        self.height = root.winfo_screenheight()
        geometry_string = f"{self.width}x{self.height}"
        self.root.geometry(geometry_string)
        self.root.attributes("-fullscreen", True)
        self.root.resizable(True, True)

        ######### variables ##########

        self.numList = set()
        self.handImages = [tk.PhotoImage(file="knuckle.png"),
                           tk.PhotoImage(file="back.png"),
                           tk.PhotoImage(file="forearm.png")]
        self.idx = 0
        self.scale = 0

        ##############################

        # 화면 전환을 위한 프레임들
        self.frames = []
        for _ in range(23):
            frame = tk.Frame(self.root)
            self.frames.append(frame)
        
        # 현재 화면 인덱스
        self.current_frame_index = 0    
        
        # 프레임들에 내용 추가
        self.add_content_to_frames()

        # 처음 화면 표시
        self.show_frame()

        self.setSensor_thread = threading.Thread(target=self.setSensor)
        self.setSensor_thread.daemon = True  # 메인 스레드 종료 시 함께 종료되도록 설정
        self.setSensor_thread.start()
        
    def add_content_to_frames(self):
        self.functionList = []
        page = 0
        self.functionList.append((self.initialPage, (page,)))  # initialPage 함수와 파라미터 저장
        page += 1
        targets = ["너클", "손등", "전완"]
        for i in range(3):
            self.functionList.append((self.calibrationPage, (targets[i], i, page)))  # calibrationPage 함수와 파라미터 저장
            page += 1
            for j in range(12, 21, 4):
                self.functionList.append((self.preExperimentPage, (page,)))  # preExperimentPage 함수와 파라미터 저장
                page += 1
                self.functionList.append((self.experimentPage, (targets[i], j, page)))  # experimentPage 함수와 파라미터 저장
                page += 1
        self.functionList.append((self.endPage, (page,)))

    # 필요한 시점에 함수 호출
    def execute_function(self, index):
        if 0 <= index < len(self.functionList):
            func, params = self.functionList[index]
            func(*params)

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
                        if hasattr(self, 'stickCanvas'):
                            self.moveSensorLine(self.scale)
                    except ValueError:
                        self.value = 0
  
    # 피험자 번호 중복 체크 후 button active
    def check_duplicate(self, num, button):
        if num not in self.numList:
            self.numList.add(num)
            msgbox.showinfo("중복 확인", "사용 가능한 번호입니다.")
            button.configure(state= "active")
            return
        
        msgbox.showinfo("중복되는 번호", "다른 번호를 사용해주세요.")
    
    # 측정 함수
    def calibrate(self, button):
        button.configure(state= "active")
        return

    # 실험 시작 화면
    def initialPage(self, page):

        frame = self.frames[page]

        titlefont= tkinter.font.Font(size=96, weight= "bold")
        buttonfont = tkinter.font.Font(size=72, weight= "normal")

        ###########
        
        top = tk.Frame(frame)
        top.pack(side= "top", fill= "both", expand= True)

        label = tk.Label(top, text="실험 프로그램 프로토타입", font= titlefont)
        label.pack(fill= "both", expand= True)
        
        ###########

        bottom = tk.Frame(frame)
        bottom.pack(side= "bottom", fill= "both", expand= True)

        entry_frame = tk.Frame(bottom)

        entry = tk.Entry(entry_frame, relief= "raised", font= buttonfont)
        entry.pack(side="left", padx= 20)
        entry.focus()

        check_button = tk.Button(entry_frame, text="중복 확인", command= lambda: self.check_duplicate(str(entry.get()), next_button), font= buttonfont, repeatinterval= 1000)
        check_button.pack(side="right")

        entry_frame.pack(pady= 80)

        next_button = tk.Button(bottom, text="다음", command=self.show_next_frame, font= buttonfont)
        next_button.pack()

        ##########

    # 측정 화면
    def calibrationPage(self, target, image, page):
        frame = self.frames[page]

        titlefont= tkinter.font.Font(size= 96, weight= "bold")
        explainfont = tkinter.font.Font(size= 72, weight= "bold")
        buttonfont = tkinter.font.Font(size= 64, weight= "normal")

        ###########
        
        top = tk.Frame(frame)
        top.pack(side= "top", fill= "both", expand= True)

        label = tk.Label(top, text="Calibration", font= titlefont)
        label.pack(fill= "both", expand= True)
        
        ###########

        middle = tk.Frame(frame)
        middle.pack(fill= "both", expand= True)

        label=tkinter.Label(middle, image=self.handImages[image])
        label.pack(pady= 20)

        ###########

        bottom = tk.Frame(frame)
        bottom.pack(side= "bottom", fill= "both", expand= True)

        measure_button = tk.Button(bottom, text= "측정", font= buttonfont, command= lambda: self.calibrate(next_button))
        measure_button.pack(side= "left", padx= 100)

        next_button = tk.Button(bottom, text="다음", state= "disable", command=self.show_next_frame, font= buttonfont)
        next_button.pack(side= "right", padx= 100)

        explain_label = tk.Label(bottom, text= target + " 부분을 측정합니다.\n 측정 버튼을 눌러주세요.", font= explainfont)
        explain_label.pack(anchor= "center")

        ##########

    def preExperimentPage(self, page):
        frame = self.frames[page]

        titlefont= tkinter.font.Font(size=96, weight= "bold")
        buttonfont = tkinter.font.Font(size=72, weight= "normal")
        
        top = tk.Frame(frame)
        top.pack(side= "top", fill= "both", expand= True)

        label = tk.Label(top, text= "실험 시작 버튼을 누르거나 (인터랙션) 으로 시작해주세요.", font= titlefont)
        label.pack(anchor= "s", expand= True)

        bottom = tk.Frame(frame)
        bottom.pack(side= "bottom", fill= "both", expand= True)

        startButton = tk.Button(bottom, text= "실험 시작", font= buttonfont, command= self.show_next_frame)
        startButton.pack(pady= 120)

    def experimentPage(self, target, scale, page):
        self.scale = scale
        frame = self.frames[page]

        partFont = tkinter.font.Font(size= 72, weight = "bold")
        progressFont = tkinter.font.Font(size= 32, weight= "normal")
        whichPart = tk.Label(frame, text= target, font= partFont)
        
        ##########
        
        whichPart.place(x= 100, y= 100)
        
        ##########
        
        self.stickCanvas = tk.Canvas(frame, width= self.width / 10, height = self.height * 0.9)
        self.stickCanvas.place(relx=0.45, rely=0.05)

        stick = self.stickCanvas.create_rectangle(0, 0, self.width / 10, self.height * 0.9, fill= "white smoke")

        self.now = self.stickCanvas.create_rectangle(0, self.height * 0.9, self.width / 10, self.height * 0.9 / scale * (scale + 1), fill= "light pink")

        x1, y1, x2, y2 = self.stickCanvas.coords(stick)

        self.gapY = (y2 - y1) / scale

        for i in range(scale):
            y = y1 + (i * self.gapY)
            self.stickCanvas.create_line(x1, y, x2, y, fill= "light grey")
        ##########
        self.progressLabel = tk.Label(frame, text= str(self.idx) + " / " + str(self.scale), font= progressFont)
        self.progressLabel.place(x = self.width - 100, y = self.height - 300, anchor= "se")
        ##########
        self.sensorBox = self.stickCanvas.create_rectangle(x1, y2, x2, y2 + self.gapY, fill= "pale violet red")
        self.sensorLine = self.stickCanvas.create_line(x1, y2, x2, y2, width= self.gapY / scale)
        
        ##########
        self.nextButton = tk.Button(frame, text= "다음", command= lambda: self.show_problems(scale), font= partFont)
        self.nextButton.place(x = self.width - 100, y = self.height - 100, anchor= "se")
        ##########
        self.problems = [y1 + i * self.gapY for i in range(scale)]
        random.shuffle(self.problems)
    
    def endPage(self, page):
        frame = self.frames[page]

        titlefont= tkinter.font.Font(size=96, weight= "bold")
        buttonfont = tkinter.font.Font(size=72, weight= "normal")
        
        top = tk.Frame(frame)
        top.pack(side= "top", fill= "both", expand= True)

        label = tk.Label(top, text= "실험이 모두 끝났습니다. 감사합니다.", font= titlefont)
        label.pack(anchor= "s", expand= True)

        bottom = tk.Frame(frame)
        bottom.pack(side= "bottom", fill= "both", expand= True)

        endButton = tk.Button(bottom, text= "종료", font= buttonfont, command= self.root.destroy)
        endButton.pack(pady= 120)
  
    def moveSensorLine(self, scale):      
        stickHeight = self.height * 0.9
        fraction = min(self.value / 1500, 1)
        linePlace = stickHeight - stickHeight * fraction
        x1, _, x2, _ = self.stickCanvas.coords(self.sensorLine)

        for i in range(1, scale + 1):
            if (i - 1) * self.gapY <= linePlace < i * self.gapY:
                self.stickCanvas.coords(self.sensorBox, x1, (i - 1) * self.gapY, x2, i * self.gapY)
                break

        self.stickCanvas.coords(self.sensorLine, x1, linePlace, x2, linePlace)
   
    def show_problems(self, scale):
        
        if self.idx == scale:
            self.idx = 0
            self.show_next_frame()
            return

        # 현재 now 사각형의 좌표를 가져옴
        x1, _, x2, _ = self.stickCanvas.coords(self.now) 

        newY = self.problems[self.idx]
        self.stickCanvas.coords(self.now, x1, newY, x2, newY + self.gapY)

        self.idx += 1
        self.progressLabel.config(text= str(self.idx) + " / " + str(self.scale))

    def show_frame(self):
        self.execute_function(self.current_frame_index)
        frame = self.frames[self.current_frame_index]
        frame.pack(fill=tk.BOTH, expand=True)

    def show_next_frame(self):
        self.frames[self.current_frame_index].pack_forget()
        self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
        self.show_frame()

    def show_prev_frame(self):
        # 이전 화면 표시
        self.frames[self.current_frame_index].pack_forget()
        self.current_frame_index = (self.current_frame_index - 1) % len(self.frames)
        self.show_frame()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExperimentApp(root)
    root.mainloop()
