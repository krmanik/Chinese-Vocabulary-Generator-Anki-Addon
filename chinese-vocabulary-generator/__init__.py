from aqt.utils import getOnlyText, tooltip

from . import templates

anki_addon_name = "Chinese Vocabulary Generator"
anki_addon_version = "1.0.0"
anki_addon_author = "Mani"
anki_addon_license = "GPL 3.0 and later"

from aqt.qt import *
from aqt import mw
from anki.notes import Note

import os
import sys
import json

folder = os.path.dirname(__file__)
libfolder = os.path.join(folder, "lib")
sys.path.insert(0, libfolder)

import requests
import sqlite3
import random
import pinyin

from gtts import gTTS
from cedict import pinyinize
from hanziconv import HanziConv
from googletrans import Translator
from playsound import playsound


optionsChecked = {'ch_sim': True, 'ch_trad': True, 'ch_pin': True, 'ch_mean': True, 'ch_aud': True, 'ch_sen': True}

class CVG_Dialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, None, Qt.Window)
        mw.setupDialogGC(self)
        self.setWindowTitle(anki_addon_name)
        layout = QVBoxLayout()

        topLayout = QFormLayout()

        self.templatesComboBox = QComboBox()
        self.templatesComboBox.addItems(['Simple', 'Colorful'])
        topLayout.addRow(QLabel("Templates"), self.templatesComboBox)

        optionsLayout = QVBoxLayout()

        # self.ch_sim_cb = QCheckBox("Simplified")
        # self.ch_sim_cb.setChecked(True)
        # optionsLayout.addWidget(self.ch_sim_cb)

        self.ch_trad_cb = QCheckBox("Traditional")
        self.ch_trad_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_trad_cb)

        self.ch_pin_cb = QCheckBox("Pinyin")
        self.ch_pin_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_pin_cb)

        self.ch_mean_cb = QCheckBox("Meaning")
        self.ch_mean_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_mean_cb)

        self.ch_aud_cb = QCheckBox("Audio")
        self.ch_aud_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_aud_cb)

        self.ch_sen_cb = QCheckBox("Sentence")
        self.ch_sen_cb.setChecked(True)
        self.ch_sen_cb.clicked.connect(self.related_sen_cb)
        optionsLayout.addWidget(self.ch_sen_cb)

        self.ch_sen_trad_cb = QCheckBox("Sentence Traditional")
        self.ch_sen_trad_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_sen_trad_cb)

        self.ch_sen_pin_cb = QCheckBox("Sentence Pinyin")
        self.ch_sen_pin_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_sen_pin_cb)

        self.ch_sen_tra_cb = QCheckBox("Sentence Translation")
        self.ch_sen_tra_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_sen_tra_cb)

        self.ch_sen_audio_cb = QCheckBox("Sentence Audio")
        self.ch_sen_audio_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_sen_audio_cb)


        self.btnBox = QDialogButtonBox()
        self.btnBox.setStandardButtons(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        self.btnBox.accepted.connect(self.show_cvg_window)
        self.btnBox.rejected.connect(self.reject)

        layout.addLayout(topLayout)
        layout.addLayout(optionsLayout)
        layout.addWidget(self.btnBox)
        self.setLayout(layout)

    def related_sen_cb(self):
        if not self.ch_sen_cb.isChecked():
            self.ch_sen_trad_cb.setChecked(False)
            optionsChecked['ch_sen_trad'] = False

            self.ch_sen_pin_cb.setChecked(False)
            optionsChecked['ch_sen_pin'] = False

            self.ch_sen_tra_cb.setChecked(False)
            optionsChecked['ch_sen_tra'] = False

            self.ch_sen_audio_cb.setChecked(False)
            optionsChecked['ch_sen_audio'] = False

    def show_cvg_window(self):

        # if self.ch_sim_cb.isChecked():
        #     optionsChecked['ch_sim'] = True
        # else:
        #     optionsChecked['ch_sim'] = False

        self.model_mn = ""
        self.model_flds = []
        self.qfmt = ""
        self.afmt = ""

        self.model_flds.append("Simplified")
        self.qfmt += "<div class='ch_sim' id='ch_sim'>{{Simplified}}</div>\n"
        self.afmt += "<div class='ch_sim' id='ch_sim'>{{Simplified}}</div>\n"

        if self.ch_trad_cb.isChecked():
            optionsChecked['ch_trad'] = True
            self.model_mn += "t"
            self.model_flds.append("Traditional")
            self.afmt += "<div class='ch_trad'>{{Traditional}}</div>\n"
        else:
            optionsChecked['ch_trad'] = False

        if self.ch_pin_cb.isChecked():
            optionsChecked['ch_pin'] = True
            self.model_mn += "p"
            self.model_flds.append("Pinyin")
            self.afmt += "<div class='ch_pin'>{{Pinyin}}</div>\n"
        else:
            optionsChecked['ch_pin'] = False

        if self.ch_mean_cb.isChecked():
            optionsChecked['ch_mean'] = True
            self.model_mn += "m"
            self.model_flds.append("Meanings")
            self.afmt += "<div class='ch_mean'>{{Meanings}}</div>\n"
        else:
            optionsChecked['ch_mean'] = False

        if self.ch_aud_cb.isChecked():
            optionsChecked['ch_aud'] = True
            self.model_mn += "a"
            self.model_flds.append("Audio")
            self.afmt += "<div class='ch_aud' id='ch_aud'>{{Audio}}</div>\n"
        else:
            optionsChecked['ch_aud'] = False

        if self.ch_sen_cb.isChecked():
            optionsChecked['ch_sen'] = True
            self.model_mn += "s"
            self.model_flds.append("Sentences")
            self.afmt += "<hr>\n<div class='ch_sen' id='ch_sen'>{{Sentences}}</div>\n"
        else:
            optionsChecked['ch_sen'] = False

        if self.ch_sen_trad_cb.isChecked():
            optionsChecked['ch_sen_trad'] = True
            self.model_mn += "t"
        else:
            optionsChecked['ch_sen_trad'] = False

        if self.ch_sen_pin_cb.isChecked():
            optionsChecked['ch_sen_pin'] = True
            self.model_mn += "p"
        else:
            optionsChecked['ch_sen_pin'] = False

        if self.ch_sen_tra_cb.isChecked():
            optionsChecked['ch_sen_tra'] = True
            self.model_mn += "tr"
        else:
            optionsChecked['ch_sen_tra'] = False

        if self.ch_sen_audio_cb.isChecked():
            optionsChecked['ch_sen_audio'] = True
            self.model_mn += "a"
        else:
            optionsChecked['ch_sen_audio'] = False

        self.hide()
        cvg_w = CVG_Window()
        cvg_w.show()


dialog = CVG_Dialog()
def showCVGEditor():
    dialog.exec_()

options_action = QAction(anki_addon_name + "...", mw)
options_action.triggered.connect(showCVGEditor)
mw.addonManager.setConfigAction(__name__, showCVGEditor)
mw.form.menuTools.addAction(options_action)


class CVG_Window(QDialog):
    def __init__(self):
        QDialog.__init__(self, None, Qt.Window)
        mw.setupDialogGC(self)

        self.deck_template = dialog.templatesComboBox.currentText()

        dname = getOnlyText("Enter Deck Name")
        self.did = mw.col.decks.id(dname)
        mw.deckBrowser.refresh()

        self.setWindowTitle(anki_addon_name)
        self.resize(600, 720)

        self.sen_i = 0

        scrolllayout = QVBoxLayout()

        scrollwidget = QWidget()
        scrollwidget.setLayout(scrolllayout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scrollwidget)

        # Simplified
        ch_sim_groupbox = QGroupBox("Enter Simplified")
        ch_sim_grouplayout = QVBoxLayout()
        self.ch_sim_group_text_edit = QTextEdit()
        # Enter Button
        enter_button = QPushButton("Enter")
        ch_sim_grouplayout.addWidget(self.ch_sim_group_text_edit)
        ch_sim_grouplayout.addWidget(enter_button)
        enter_button.clicked.connect(self.cvg_get_ch_data)

        ch_sim_groupbox.setLayout(ch_sim_grouplayout)
        scrolllayout.addWidget(ch_sim_groupbox)

        # Traditional
        if optionsChecked['ch_trad']:
            ch_trad_groupbox = QGroupBox("Traditional")
            ch_trad_grouplayout = QHBoxLayout()
            self.ch_trad_group_text_edit = QTextEdit()
            ch_trad_grouplayout.addWidget(self.ch_trad_group_text_edit)
            ch_trad_groupbox.setLayout(ch_trad_grouplayout)
            scrolllayout.addWidget(ch_trad_groupbox)


        # Pinyin
        if optionsChecked['ch_pin']:
            ch_pin_groupbox = QGroupBox("Pinyin")
            ch_pin_grouplayout = QHBoxLayout()
            self.ch_pin_group_text_edit = QTextEdit()
            ch_pin_grouplayout.addWidget(self.ch_pin_group_text_edit)
            ch_pin_groupbox.setLayout(ch_pin_grouplayout)
            scrolllayout.addWidget(ch_pin_groupbox)

        # Meaning
        if optionsChecked['ch_mean']:
            ch_mean_groupbox = QGroupBox("Meaning")
            ch_mean_grouplayout = QHBoxLayout()
            self.ch_mean_group_text_edit = QTextEdit()
            ch_mean_grouplayout.addWidget(self.ch_mean_group_text_edit)
            ch_mean_groupbox.setLayout(ch_mean_grouplayout)
            scrolllayout.addWidget(ch_mean_groupbox)

        # Audio
        if optionsChecked['ch_aud']:
            ch_aud_box_gl = QVBoxLayout()

            ch_aud_groupbox = QGroupBox("Audio")
            ch_aud_grouplayout = QHBoxLayout()
            self.ch_aud_group_text_edit = QTextEdit()
            ch_aud_grouplayout.addWidget(self.ch_aud_group_text_edit)

            ch_aud_buttons_gl = QHBoxLayout()

            ch_aud_add_button = QPushButton("Add/Change")
            ch_aud_add_button.clicked.connect(self.get_audio_ch_sim)

            ch_aud_play_button = QPushButton("Play")
            ch_aud_play_button.clicked.connect(self.ch_sim_audio_play)

            ch_aud_buttons_gl.addWidget(ch_aud_add_button)
            ch_aud_buttons_gl.addWidget(ch_aud_play_button)

            ch_aud_box_gl.addLayout(ch_aud_grouplayout)
            ch_aud_box_gl.addLayout(ch_aud_buttons_gl)

            ch_aud_groupbox.setLayout(ch_aud_box_gl)
            scrolllayout.addWidget(ch_aud_groupbox)


        # Sentence
        if optionsChecked['ch_sen']:
            # Change Button | All Sentence Button
            ch_sen_box_gl = QVBoxLayout()

            self.ch_sen_groupbox = QGroupBox("Sentence")
            self.ch_sen_grouplayout = QHBoxLayout()
            self.ch_sen_group_text_edit = QTextEdit()
            self.ch_sen_grouplayout.addWidget(self.ch_sen_group_text_edit)

            ch_sen_buttons_gl = QHBoxLayout()

            ch_sen_add_button = QPushButton("Add")
            ch_sen_add_button.clicked.connect(self.get_ch_sen_add)

            ch_sen_clear_button = QPushButton("Clear")
            ch_sen_clear_button.clicked.connect(self.clear_ch_sen)

            ch_sen_buttons_gl.addWidget(ch_sen_add_button)
            ch_sen_buttons_gl.addWidget(ch_sen_clear_button)

            ch_sen_box_gl.addLayout(self.ch_sen_grouplayout)
            ch_sen_box_gl.addLayout(ch_sen_buttons_gl)

            self.ch_sen_groupbox.setLayout(ch_sen_box_gl)
            scrolllayout.addWidget(self.ch_sen_groupbox)


        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton("Add", QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton("Clear", QDialogButtonBox.RejectRole)

        self.buttonBox.accepted.connect(self.cvg_add_notes)
        self.buttonBox.rejected.connect(self.cvg_clear_notes)

        layout = QVBoxLayout()
        layout.addWidget(scroll)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def cvg_get_ch_data(self):
        ch_sim = self.ch_sim_group_text_edit.toPlainText().strip()
        #ch_trad = HanziConv.toTraditional(ch_sim)

        char_json = folder+"/cedict/"+ ch_sim + ".json"

        if os.path.exists(char_json):
            with open(char_json, encoding="utf-8") as f:
                ch_data = json.load(f)

                if optionsChecked['ch_trad']:
                    self.ch_trad_group_text_edit.setText(ch_data['traditional'])

                if optionsChecked['ch_pin']:
                    ch_pin = ""
                    for p in ch_data['pinyin']:
                        ch_pin += pinyinize(p) + ", "
                    ch_pin.strip().rstrip(", ")
                    self.ch_pin_group_text_edit.setText(ch_pin)

                if optionsChecked['ch_mean']:
                    ch_mean = ""
                    if len(ch_data['definitions']) > 1:
                        for d in ch_data['definitions']:
                            ch_mean += d + "\n" + ch_data['definitions'][d].replace("; ", "\n").strip() + "\n\n"
                    else:
                        ch_mean += ch_data['definitions'][ch_data['pinyin'][0]].replace("; ", "\n").strip() + "\n\n"
                    self.ch_mean_group_text_edit.setText(ch_mean)

        else:
            if optionsChecked['ch_trad']:
                self.ch_trad_group_text_edit.setText(HanziConv.toTraditional(ch_sim))

            if optionsChecked['ch_pin']:
                self.ch_pin_group_text_edit.setText(pinyin.get(ch_sim))

            if optionsChecked['ch_mean']:
                translator = Translator()
                t1 = translator.translate(ch_sim, src='zh-cn', dest="en")
                self.ch_mean_group_text_edit.setText(t1.text)

    def get_audio_ch_sim(self):
        ch_sim = self.ch_sim_group_text_edit.toPlainText().strip()
        rand_file_name = str(random.randrange(1 << 30, 1 << 31)) + "-" + str(random.randrange(1 << 15, 1 << 16))
        if ch_sim != "":
            self.audio_file = "cvg-" + rand_file_name + ".mp3"
            ch_audio = "[sound:" + self.audio_file + "]"
            self.ch_aud_group_text_edit.setText(ch_audio)
            tts = gTTS(ch_sim, lang="zh-cn")
            tts.save(self.audio_file)

    def ch_sim_audio_play(self):
        ch_aud = self.ch_aud_group_text_edit.toPlainText().strip()
        ch_aud = ch_aud.replace("[sound:", "")
        ch_aud = ch_aud.replace("]", "")
        if os.path.exists(ch_aud):
            playsound(ch_aud)

    def get_ch_sen_add(self):
        ch_sim = self.ch_sim_group_text_edit.toPlainText().strip()
        if ch_sim != "":
            self.get_sentence(ch_sim)

    def clear_ch_sen(self):
        self.ch_sen_group_text_edit.clear()

    def cvg_add_notes(self):
        model_name = "cvg-" + str.lower(self.deck_template) + dialog.model_mn
        model = mw.col.models.byName(model_name)

        if not model:
            models = mw.col.models

            model = models.new(model_name)

            for fl in dialog.model_flds:
                fld = models.newField(fl)
                models.addField(model, fld)

            template = models.newTemplate(self.deck_template + dialog.model_mn)
            template['qfmt'] = dialog.qfmt
            template['afmt'] = dialog.afmt

            # ['Simple', 'Colorful']
            if self.deck_template == "Simple":
                model['css'] = templates.simple_css
            elif self.deck_template == "Colorful":
                model['css'] = templates.colorful_css

            models.addTemplate(model, template)
            models.add(model)

        model['did'] = self.did
        mw.col.decks.select(self.did)

        note = Note(mw.col, model)

        note['Simplified'] = self.ch_sim_group_text_edit.toPlainText().strip()

        if optionsChecked['ch_trad']:
            note['Traditional'] = self.ch_trad_group_text_edit.toPlainText().strip()

        if optionsChecked['ch_pin']:
            note['Pinyin'] = self.ch_pin_group_text_edit.toPlainText().strip().rstrip(", ")

        if optionsChecked['ch_mean']:
            note_meanings = ""
            ch_mean = self.ch_mean_group_text_edit.toPlainText().strip()
            meanings = ch_mean.split("\n")
            for mean in meanings:
                note_meanings += mean + "; "
            note_meanings.rstrip("; ")

            note['Meanings'] = note_meanings

        if optionsChecked['ch_aud']:
            note['Audio'] = self.ch_aud_group_text_edit.toPlainText().strip()

        if optionsChecked['ch_sen']:
            sentences = self.ch_sen_group_text_edit.toPlainText().strip()
            sentences = sentences.split("\n")
            ch_sen = ""
            ch_sim = self.ch_sim_group_text_edit.toPlainText().strip()
            ch_trad = self.ch_trad_group_text_edit.toPlainText().strip()
            for sen in sentences:
                if len(sen) > 0:
                    if "ch_sen_sim:" in sen:
                        sen = sen.replace(ch_sim, "<b>" + ch_sim + "</b>")
                        ch_sen += "<div class='ch_sen_sim'>" + sen.replace("ch_sen_sim:", "") + "</div>\n"
                    if "ch_sen_trad:" in sen:
                        sen = sen.replace(ch_trad, "<b>" + ch_trad + "</b>")
                        ch_sen += "<div class='ch_sen_trad'>" + sen.replace("ch_sen_trad:", "") + "</div>\n"
                    if "ch_sen_pin:" in sen:
                        ch_sen += "<div class='ch_sen_pin'>" + sen.replace("ch_sen_pin:", "") + "</div>\n"
                    if "ch_sen_tr:" in sen:
                        ch_sen += "<div class='ch_sen_tr'>" + sen.replace("ch_sen_tr:", "") + "</div>\n"
                    if "ch_sen_aud:" in sen:
                        ch_sen += "<div class='ch_sen_aud'>" + sen.replace("ch_sen_aud:", "") + "</div>\n"

            note['Sentences'] = ch_sen

        mw.col.add_note(note, self.did)
        # mw.col.addNote(note)
        mw.deckBrowser.refresh()

        tooltip("Notes added")

        self.cvg_clear_notes()

    def cvg_clear_notes(self):
        if optionsChecked['ch_sim']:
            self.ch_sim_group_text_edit.clear()

        if optionsChecked['ch_trad']:
            self.ch_trad_group_text_edit.clear()

        if optionsChecked['ch_pin']:
            self.ch_pin_group_text_edit.clear()

        if optionsChecked['ch_mean']:
            self.ch_mean_group_text_edit.clear()

        if optionsChecked['ch_sen']:
            self.ch_sen_group_text_edit.clear()

        if optionsChecked['ch_aud']:
            self.ch_aud_group_text_edit.clear()

    def get_sentence(self, char):
        self.sen_i += 1

        con = sqlite3.connect(folder+"/sen_data.db")
        cur = con.cursor()

        sql = "Select simplified, traditional, pinyin, english from examples where simplified like " + "'%" + char + "%'"

        cur.execute(sql)
        sent = cur.fetchall()

        r1 = random.choice(sent)
        s1 = HanziConv.toSimplified(r1[0])
        trad1 = HanziConv.toTraditional(s1)

        p1 = r1[2]

        ch_sen = self.ch_sen_group_text_edit.toPlainText().strip()
        if ch_sen != "":
            ch_sen += "\n\n"

        if optionsChecked['ch_sen']:
            ch_sen += "ch_sen_sim:" + s1 + "\n"

        if optionsChecked['ch_sen_trad']:
            ch_sen += "ch_sen_trad:" + trad1 + "\n"

        if optionsChecked['ch_sen_pin']:
            ch_sen += "ch_sen_pin:" + p1 + "\n"

        if optionsChecked['ch_sen_tra']:
            ch_sen += "ch_sen_tr:" + r1[3] + "\n"

        if optionsChecked['ch_sen_audio']:
            if s1 != "":
                rand_file_name = str(random.randrange(1 << 30, 1 << 31)) + "-" + str(random.randrange(1 << 15, 1 << 16))
                audio_file = "cvg-sen-" + rand_file_name + ".mp3"
                tts = gTTS(s1, lang="zh-cn")
                tts.save(audio_file)
                ch_sen += "ch_sen_aud:[sound:" + audio_file + "]\n"

        ch_sen += "\n"

        self.ch_sen_group_text_edit.setText(ch_sen)
