from PySide2.QtWidgets import QApplication, QDialog, QPushButton, QTextEdit, QVBoxLayout, QWidget, QProgressBar
from PySide2 import QtWidgets as QtGui
from PySide2 import QtCore
from PySide2.QtCore import QObject, QThread, Signal, Slot
import openai
import time

# 设置http(s)代理
# import os
# os.environ["http_proxy"] = "http://localhost:10809"
# os.environ["https_proxy"] = "http://localhost:10809"

# 设置你的OpenAI API Key和其他参数
apikey = '114514'
gpt_version = 'gpt-4'
proxy_url = ''
default_prompt = '你是Houdini专家，擅长程序化生成，精通所有操作和SOP知识，擅长所有Houdini相关语言。默认情况是根据问题回答需要的节点名，直接给出节点名，不准编造任何内容，最好一个节点，若有多个节点则用+连接并另起一行解释使用方法，不准有其他任何语句。对于代码问题则需要返回代码并附上详细注释。回答的时候不准带有任何Markdown格式。'

class ChatWorker(QObject):
    message_received = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        openai.api_key = apikey
        self.chat_history = [{'role': 'system', 'content': default_prompt}]
        if proxy_url is not None and proxy_url != '':
            self.client = openai.OpenAI(base_url=proxy_url, api_key=apikey)
        else:
            api_key = apikey

    def resetContext(self):
        self.chat_history = [{'role': 'system', 'content': default_prompt}]

    @Slot(str)
    def runChat(self, prompt):
        self.chat_history.append({'role': 'user', 'content': prompt})
        # 定义初始对话
        # 使用 chat.completions.create 方法生成完成的响应，并设置 stream=True
        response = self.client.chat.completions.create(
            model=gpt_version,
            messages=self.chat_history,
            stream=True
        )

        # 处理流式响应
        response_str = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                response_str = response_str + chunk.choices[0].delta.content
                self.message_received.emit(chunk.choices[0].delta.content)

        self.chat_history.append({'role': 'system', 'content': response_str})
        return

class ChatgptPanel(QtGui.QDialog):
    # auto resize text edit
    class AutoHeightTextEdit(QTextEdit):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.document().documentLayout().documentSizeChanged.connect(self.adjustHeight)
            self.max_height = 200
            self.min_height = 125

        def setHeightLimit(self, min_value, max_value):
            self.max_height = max_value
            self.min_height = min_value

        def adjustHeight(self, *args):
            doc_height = self.document().size().height()
            if doc_height > self.max_height:
                doc_height = self.max_height
            elif doc_height < self.min_height:
                doc_height = self.min_height

            self.setFixedHeight(doc_height)


    def __init__(self):
        super().__init__()
        self.module_name = ""
        self.version = ""

        blvMain = QtGui.QVBoxLayout()
        blhMessage = QtGui.QHBoxLayout()
        blhSendMessage = QtGui.QHBoxLayout()

        self.lePrompt = QtGui.QLineEdit(self)
        self.lbPrompt = QtGui.QLabel("Prompt")

        self.teMessage = ChatgptPanel.AutoHeightTextEdit(self)
        self.teMessage.setReadOnly(True)
        self.teMessage.setHeightLimit(150, 350)

        self.pbSend = QtGui.QPushButton("Send")
        self.pbSend.clicked.connect(self.sendMessage)

        self.pbReset = QtGui.QPushButton("Reset")
        self.pbReset.clicked.connect(self.resetContext)

        blhMessage.addWidget(self.teMessage)
        blhSendMessage.addWidget(self.lePrompt)
        blhSendMessage.addWidget(self.pbSend)
        blhSendMessage.addWidget(self.pbReset)
        blvMain.addWidget(self.teMessage)
        blvMain.addLayout(blhSendMessage)

        self.setLayout(blvMain)
        self.resize(QtCore.QSize(450, 150))
        self.setWindowTitle("Houdini Master")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowCloseButtonHint)

        # chatgpt worker
        self.chat_worker = ChatWorker()
        self.chat_thread = QThread()
        self.chat_worker.moveToThread(self.chat_thread)
        self.chat_worker.message_received.connect(self.appendMessage)

    def sendMessage(self):
        prompt = self.lePrompt.text()
        if prompt:
            self.teMessage.append("You: " + prompt)
            self.teMessage.append("")
            cursor = self.teMessage.textCursor()
            cursor.insertText("Bot: ")
            self.chat_worker.runChat(prompt)
            self.lePrompt.clear()

    def resetContext(self):
        #重置聊天历史
        self.chat_worker.resetContext()
        self.teMessage.clear()

    def appendMessage(self, str):
        if str is not None and len(str) > 0:
            cursor = self.teMessage.textCursor()
            cursor.insertText(str)
            # 必须启用repaint才会重绘制
            self.teMessage.repaint()

    def closeEvent(self, event):
        self.done(0)