from PySide2.QtWidgets import QApplication, QDialog, QPushButton, QTextEdit, QVBoxLayout, QWidget, QProgressBar
from PySide2 import QtWidgets as QtGui
from PySide2 import QtCore
from PySide2.QtCore import QObject, QThread, Signal, Slot
import json

gpt_prompt = {"Node": '你是Houdini专家。默认情况是根据问题回答需要的节点名，包括SideFX Labs的节点，最好回答一个节点，不准有其他语句；若有多个节点则用+连接并换行解释使用方法；回答之前先对比各种节点的实现效果难易程度，择优回答。不准编造节点。回答必须简短',
          "Vex": '你是Houdini专家。默认情况是根据问题回答Vex代码，需附上详细注释，不要带有代码外的其他任何语句。不能带有Markdown格式',
          "Python": '你是Houdini专家。默认情况是根据问题回答Houdini内的Python代码，需附上详细注释不要带有代码外的其他任何语句。不能带有Markdown格式',
          "Free": '你是Houdini专家。用户会向你提问Houdini相关问题，尽力地为用户解答。如果问题比较复杂，你需要把问题进行分解然后回答。回答必须简短'}
class ChatWorker(QObject):
    message_received = Signal(str)
    apikey = ""
    gpt_version = "gpt-4"
    proxy_url = ""
    client = None
    prompt_key = "Node"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.chat_history = [{'role': 'system', 'content': gpt_prompt[self.prompt_key]}]

    def resetContext(self):
        self.chat_history = [{'role': 'system', 'content': gpt_prompt[self.prompt_key]}]

    # call this before run chat
    def setSettings(self, apikey, gpt_version, proxy_url):
        self.apikey = apikey
        self.gpt_version = gpt_version
        self.proxy_url = proxy_url
        openai.api_key = apikey
        if proxy_url is not None and proxy_url != '':
            self.client = openai.OpenAI(base_url=proxy_url, api_key=apikey)
        else:
            self.client = openai.OpenAI(api_key=apikey)

    def changePrompt(self, prompt):
        self.prompt_key = prompt

    @Slot(str)
    def runChat(self, user_prompt):
        if self.client is not None:
            self.chat_history.append({'role': 'user', 'content': user_prompt})
            # 定义初始对话
            # 使用 chat.completions.create 方法生成完成的响应，并设置 stream=True
            response = self.client.chat.completions.create(
                model=self.gpt_version,
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

def getJsonPath():
    import os
    appdata_path = os.environ['APPDATA']
    json_path = os.path.join(appdata_path, "Dolag/Houdini-Toolset/chatgpt.json")
    return json_path

class ChatgptPanel(QtGui.QDialog):
    apikey = ""
    gpt_version = "gpt-4"
    proxy_url = ""
    http_proxy = ""
    https_proxy = ""
    has_settings = False
    chat_worker = None
    chat_thread = None

    # auto resize text edit
    class AutoHeightTextEdit(QTextEdit):
        def __init__(self, *args, **kwargs):
            import openai
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

    # settings panel
    class SettingPanel(QDialog):
        apikey = ""
        gpt_version = "gpt-4"
        proxy_url = ""
        http_proxy = ""
        https_proxy = ""
        save = False
        def __init__(self):
            super().__init__()

            self.layout = QVBoxLayout(self)

            # Openai API Key
            self.api_key_label = QtGui.QLabel("Openai API Key:")
            self.api_key_edit = QtGui.QLineEdit()
            self.layout.addWidget(self.api_key_label)
            self.layout.addWidget(self.api_key_edit)

            # GPT Version
            self.gpt_version_label = QtGui.QLabel("GPT Version:")
            self.gpt_version_edit = QtGui.QLineEdit('gpt-4')
            self.layout.addWidget(self.gpt_version_label)
            self.layout.addWidget(self.gpt_version_edit)

            # API URL
            self.api_url_label = QtGui.QLabel("API URL:")
            self.api_url_edit = QtGui.QLineEdit("https://api.openai.com/v1")
            self.layout.addWidget(self.api_url_label)
            self.layout.addWidget(self.api_url_edit)

            # HTTP Proxy
            self.http_proxy_label = QtGui.QLabel("HTTP Proxy:")
            self.http_proxy_edit = QtGui.QLineEdit("http://localhost:10809")
            self.layout.addWidget(self.http_proxy_label)
            self.layout.addWidget(self.http_proxy_edit)

            # HTTPs Proxy
            self.https_proxy_label = QtGui.QLabel("HTTPs Proxy:")
            self.https_proxy_edit = QtGui.QLineEdit("http://localhost:10809")
            self.layout.addWidget(self.https_proxy_label)
            self.layout.addWidget(self.https_proxy_edit)
            # Ok and Cancel buttons
            self.ok_button = QPushButton("Save")
            self.cancel_button = QPushButton("Cancel")
            self.layout.addWidget(self.ok_button)
            self.layout.addWidget(self.cancel_button)

            self.ok_button.clicked.connect(self.saveValues)
            self.cancel_button.clicked.connect(self.close)

            self.loadJson()

            self.setLayout(self.layout)
            self.setWindowTitle("Settings")
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        def loadJson(self):
            import os
            if os.path.exists(getJsonPath()):
                settings = None
                try:
                    with open(getJsonPath()) as f:
                        settings = json.load(f)
                except Exception as e:
                    settings = None

                if settings is not None:
                    # set settings
                    self.api_key_edit.setText(settings["apikey"])
                    self.gpt_version_edit.setText(settings["gpt_version"])
                    self.api_url_edit.setText(settings["proxy_url"])
                    self.http_proxy_edit.setText(settings["http_proxy"])
                    self.https_proxy_edit.setText(settings["https_proxy"])

        def saveJson(self):
            data = {"apikey": self.apikey, "gpt_version": self.gpt_version, "proxy_url": self.proxy_url,
                    "http_proxy": self.http_proxy, "https_proxy": self.https_proxy}

            import os
            os.makedirs(os.path.dirname(getJsonPath()), exist_ok=True)
            with open(getJsonPath(), 'w') as f:
                json.dump(data, f)

        def saveValues(self):
            self.apikey = self.api_key_edit.text()
            self.gpt_version = self.gpt_version_edit.text()
            self.proxy_url = self.api_url_edit.text()
            self.http_proxy = self.http_proxy_edit.text()
            self.https_proxy = self.https_proxy_edit.text()
            self.saveJson()
            self.close()

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
        self.teMessage.setHeightLimit(150, 600)

        self.pbSend = QtGui.QPushButton("Send")
        self.pbSend.clicked.connect(self.sendMessage)
        self.pbSend.setDefault(True)

        self.pbReset = QtGui.QPushButton("Reset")
        self.pbReset.clicked.connect(self.resetContext)

        self.pbSetPanel = QtGui.QPushButton("Set")
        self.pbSetPanel.clicked.connect(self.openSettingPanel)

        self.cbMode = QtGui.QComboBox()
        for key in gpt_prompt.keys():
            self.cbMode.addItem(key)
        self.cbMode.currentIndexChanged.connect(self.changePromptMode)
        self.changePromptMode() # update to default mode

        blhMessage.addWidget(self.teMessage)
        blhSendMessage.addWidget(self.lePrompt)
        blhSendMessage.addWidget(self.pbSend)
        blhSendMessage.addWidget(self.pbReset)
        blhSendMessage.addWidget(self.cbMode)
        blhSendMessage.addWidget(self.pbSetPanel)
        blvMain.addWidget(self.teMessage)
        blvMain.addLayout(blhSendMessage)

        self.setLayout(blvMain)
        self.resize(QtCore.QSize(550, 175))
        self.setWindowTitle("Houdini Master")
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.lePrompt.setFocus()

        self.loadJson()
        # no settings warning
        self.lbNoSettings = QtGui.QLabel('No configuration, click "Settings" to config')
        self.lbNoSettings.setStyleSheet("color: red")
        blvMain.addWidget(self.lbNoSettings)

        if self.has_settings:
            self.lbNoSettings.hide()
            self.newGptWorker()

    def changePromptMode(self):
        prompt_key = self.cbMode.currentText()
        if self.has_settings and self.chat_worker is not None:
            self.chat_worker.changePrompt(prompt_key)
            self.chat_worker.resetContext()

    def newGptWorker(self):
        # chatgpt worker
        self.chat_worker = ChatWorker()
        self.chat_thread = QThread()
        self.chat_worker.moveToThread(self.chat_thread)
        self.chat_worker.message_received.connect(self.appendMessage)
        self.chat_worker.setSettings(self.apikey, self.gpt_version, self.proxy_url)

    def openSettingPanel(self):
        self.setting_panel = ChatgptPanel.SettingPanel()
        self.setting_panel.exec_()
        self.loadJson()

        if self.has_settings:
            self.lbNoSettings.hide()
            self.newGptWorker()
        else:
            self.lbNoSettings.show()

    # call this before new cpt worker
    def setSettings(self, apikey, gpt_version='gpt-4', proxy_url='', http_proxy='', https_proxy=''):
        self.apikey = apikey
        self.gpt_version = gpt_version
        self.proxy_url = proxy_url
        if http_proxy != '':
            import os
            os.environ["http_proxy"] = http_proxy
        if https_proxy != '':
            import os
            os.environ["https_proxy"] = https_proxy

    # load and set settings, call this before new gpt worker
    def loadJson(self):
        import os
        if os.path.exists(getJsonPath()):
            settings = None
            try:
                with open(getJsonPath()) as f:
                    settings = json.load(f)
            except Exception as e:
                settings = None

            if settings is not None:
                # set settings
                self.setSettings(settings["apikey"], settings["gpt_version"], settings["proxy_url"],
                                 settings["http_proxy"], settings["http_proxy"])

                self.has_settings = True

    def sendMessage(self):
        prompt = self.lePrompt.text()
        if prompt and self.chat_worker is not None and self.chat_thread is not None:
            self.teMessage.append("You: " + prompt)
            self.teMessage.append("")
            cursor = self.teMessage.textCursor()
            cursor.insertText("Bot: ")
            self.chat_worker.runChat(prompt)
            self.lePrompt.clear()
            self.lePrompt.setFocus()

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