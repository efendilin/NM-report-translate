# -*- coding: utf-8 -*-

import win32clipboard
import win32con
import re

from os import linesep


class Translater():

    def __init__(self):

        self.tracer = 'fdg uptake'
        self.tracer_words = {}
        self.in_parentheses = {}
        self.in_semicolon = {}

        self.totalreplace = {}
        try:
            f = open('./setting/totalsent.txt', 'r', encoding='utf-8-sig')
        except:
            f = open('./setting/totalsent.txt', 'r', encoding='cp950')
        while True:
            t = f.readline()
            if t == '': break
            if ':' in t:
                content = ''
                key = t.strip().split(':', 1)[0]
                content = t.strip().split(':', 1)[1]
                self.totalreplace[key] = content


        self.phrasemetrix = {}
        try:
            f = open('./setting/phrasemetrix.txt', 'r', encoding='utf-8-sig')
        except:
            f = open('./setting/phrasemetrix.txt', 'r', encoding='cp950')
        while True:
            t = f.readline()
            if t == '': break
            if ':' in t:
                contentlist = []
                key = t.strip().split(':', 1)[0].lower()
                content = t.strip().split(':', 1)[1]
                contentlist = content.split(',')
                self.phrasemetrix[key] = contentlist

        self.phraselist = list(self.phrasemetrix.keys())
        self.phraselist.sort(key = len, reverse = True)

        #print(self.phraselist)

        self.fdgkeyword = {}
        try:
            f = open('./setting/FDGkeyword.txt', 'r', encoding='utf-8-sig')
        except:
            f = open('./setting/FDGkeyword.txt', 'r', encoding='cp950')
        while True:
            t = f.readline()
            if t == '': break
            if ':' in t:
                contentlist = []
                key = t.strip().split(':', 1)[0]
                content = t.strip().split(':', 1)[1]
                contentlist = content.split(',')
                self.fdgkeyword[key] = contentlist


        self.verbkeyword = {}
        try:
            f = open('./setting/verb.txt', 'r', encoding='utf-8-sig')
        except:
            f = open('./setting/verb.txt', 'r', encoding='cp950')
        while True:
            t = f.readline()
            if t == '': break
            if ':' in t:
                contentlist = []
                key = t.strip().split(':', 1)[0].lower()
                content = t.strip().split(':', 1)[1]
                self.verbkeyword[key] = content

        self.verblist = list(self.verbkeyword.keys())
        self.verblist.sort(key = len, reverse = True)

        self.adjant = {}
        self.adjpost = {}

        try:
            f = open('./setting/adj.txt', 'r', encoding='utf-8-sig')
        except:
            f = open('./setting/adj.txt', 'r', encoding='cp950')
        while True:
            t = f.readline()
            if t == '': break
            if ':' in t:
                location = ''
                key = t.strip().split(':', 1)[0]
                temp = t.strip().split(':', 1)[1]
                if ',' in temp:
                    content = temp.split(',', 1)[0]
                    location = temp.split(',', 1)[1]
                else:
                    content = temp
                if location == 'post':
                    self.adjpost[key] = content
                else:
                    self.adjant[key] = content

        self.prepkeyword = {}
        try:
            f = open('./setting/prep.txt', 'r', encoding='utf-8-sig')
        except:
            f = open('./setting/prep.txt', 'r', encoding='cp950')
        while True:
            t = f.readline()
            if t == '': break
            if ':' in t:
                content = ""
                key = t.strip().split(':', 1)[0]
                content = t.strip().split(':', 1)[1]
                self.prepkeyword[key] = content

        self.notofprep = ['with']

        return

    def judge_pure_english(self, keyword):
        return all(ord(c) < 128 for c in keyword)

    def total_replace(self, sent):
        for key in self.totalreplace.keys():  # 處理完全取代
            if key in sent:
                sent = sent.replace(key,self.totalreplace[key])

        return sent

    def deal_with_tracer(self, sent): # 處理形容FDG uptake 假設所有形容詞皆相接在前方
        pattern = '\\b' + self.tracer + '\\b'
        while self.tracer in sent.lower():
            templet = self.fdgkeyword['default'][0]
            ant = ''  # 放在"葡萄糖攝取"前的句子
            deg = ''  # 放在"葡萄糖攝取"中的句子
            aft = ''  # 放在"葡萄糖攝取"後的句子
            pre_tracer_words = re.split('\s', re.split(pattern, sent, 1, re.IGNORECASE)[0])
            lens = len(pre_tracer_words)
            for index in range(lens):
                word = pre_tracer_words[lens - index - 1]
                if word.lower() in self.fdgkeyword.keys():
                    pre_tracer_words.pop(lens - index - 1)
                    if self.fdgkeyword[word.lower()][1] == 'deg':
                        if deg:
                            deg = deg + '到' + self.fdgkeyword[word.lower()][0]
                        else:
                            deg = self.fdgkeyword[word.lower()][0]
                    elif self.fdgkeyword[word.lower()][1] == 'ant':
                        ant = ant + self.fdgkeyword[word.lower()][0]
                    elif self.fdgkeyword[word.lower()][1] == 'aft':
                        aft = aft + self.fdgkeyword[word.lower()][0]
                    else:
                        print('Error: undefined key word in FDGkeyword')
                elif word.lower() == 'increased':
                    pre_tracer_words.pop(lens - index - 1)
                    templet = self.fdgkeyword['with_increased'][0]
                elif word:
                    break
            n = len(self.tracer_words)
            self.tracer_words[n] = ant + templet.format(deg) + aft
            sign = 'tracer_word[' + str(n) + ']'
            sent = " ".join(pre_tracer_words) + sign + \
                   re.split(pattern, sent, 1, re.IGNORECASE)[1]

        return sent

    def deal_with_verb(self, sent):
        for key in self.verblist:  # 處裡動詞或是動詞片語
            pattern = '\\b' + key + '\\b'
            if '{}' in self.verbkeyword[key]:
                while re.search(pattern, sent, re.IGNORECASE):
                    temp = re.split(pattern, sent, 1, re.IGNORECASE)[0]
                    if '。' in temp:
                        present = temp.rsplit('。', 1)[0]
                        verbsent = self.verbkeyword[key].format(temp.rsplit('。', 1)[1])
                        temp = present + '。' + verbsent
                    elif ' , ' in temp:
                        present = temp.rsplit(' , ', 1)[0]
                        verbsent = self.verbkeyword[key].format(temp.rsplit(' , ', 1)[1])
                        temp = present + ' , ' + verbsent
                    else:
                        temp = temp + self.verbkeyword[key].format("")
                    sent = temp + re.split(pattern, sent, 1, re.IGNORECASE)[1]
            else:
                if key in sent.lower():
                    sent = re.sub(pattern, self.verbkeyword[key], sent, 0, re.IGNORECASE)

        return sent

    def deal_with_prep(self, sent):
        prepkeylist = self.prepkeyword.keys()
        self.notofprep = self.notofprep + list(prepkeylist)
        for key in prepkeylist:  # 處理介係詞

            pattern = '\\b' + key + '\\b'
            while re.search(pattern, sent, re.IGNORECASE):  # loop 直到所有介係詞都處理
                after_prep_drop = ''
                after_preps = []
                after_prep_drops = []
                pre_prep = re.split(pattern, sent, 1, re.IGNORECASE)[0]  # 介係詞前子句
                after_prep = re.split(pattern, sent, 1, re.IGNORECASE)[1]  # 介係詞後子句

                if '。' in after_prep:
                    # print(after_prep.split(' . ',1)[0])
                    after_prep_drop = '。' + after_prep.split('。', 1)[1]
                    after_prep = after_prep.split('。', 1)[0]
                if ' , ' in after_prep:
                    after_prep_seps = after_prep.split(' , ')
                    for phrase in after_prep_seps:
                        if self.judge_pure_english(phrase):
                            notofprep = True
                            for notofprepkey in self.notofprep:
                                temppattern = '\\b' + notofprepkey + '\\b'
                                if re.search(temppattern, phrase, re.IGNORECASE):
                                    notofprep = False
                                    break
                            if notofprep:
                                after_preps.append(phrase)
                            else:
                                after_prep_drops.append(phrase)
                        else:
                            after_prep_drops.append(phrase)
                    after_prep_drop = ' , '.join(after_prep_drops) + after_prep_drop

                    if not after_preps:
                        after_prep_drops = re.split(' ', after_prep_drop, re.IGNORECASE)
                        temp = after_prep_drops
                        for word in temp:
                            if self.judge_pure_english(word) or not word in self.notofprep:
                                after_preps.append(word)
                                after_prep_drops.remove(word)
                            else:
                                break
                        after_prep_drop = ' '.join(after_prep_drops)

                    after_prep = ' , '.join(after_preps)
                    after_prep_drop = ' , ' + after_prep_drop

                if re.search('\\b' + 'and' + '\\b', after_prep, re.IGNORECASE):
                    after_prep_seps = re.split('\\b' + 'and' + '\\b', after_prep,1)
                    after_preps = []
                    for phrase in after_prep_seps:
                        if self.judge_pure_english(phrase):
                            notofprep = True
                            for notofprepkey in self.notofprep:
                                temppattern = '\\b' + notofprepkey + '\\b'
                                if re.search(temppattern, phrase, re.IGNORECASE):
                                    notofprep = False
                                    break
                            if notofprep:
                                after_preps.append(phrase.strip())
                            else:
                                after_prep_drop = ' and ' + phrase.strip() + after_prep_drop.strip()
                        else:
                            after_prep_drop = ' and ' + phrase.strip() + after_prep_drop.strip()
                    after_prep = ' and '.join(after_preps)

                if not self.judge_pure_english(after_prep):
                    temp = after_prep.rsplit(' ')
                    after_preps = []
                    after_prep_drops = []
                    word_after_verb = False
                    for word in temp:
                        if not self.judge_pure_english(word):
                            word_after_verb = True
                        if word_after_verb:
                            after_prep_drops.append(word)
                        else:
                            after_preps.append(word)

                    after_prep = ' '.join(after_preps)
                    after_prep_drop = ' '.join(after_prep_drops) + after_prep_drop

                if ';' in after_prep:
                    after_prep_seps = after_prep.split(';', 1)
                    after_prep = after_prep_seps[0]
                    after_prep_drop = ';' + after_prep_seps[1] + after_prep_drop

                if ' , ' in pre_prep and '。' in pre_prep:  # 處理介係詞前子句，假定放在前一個子句前
                    pre_prep_afterdot = pre_prep.rsplit('。', 1)[1]
                    pre_prep_beforedot = pre_prep.rsplit('。', 1)[0] + '。'
                    pre_prep_aftercomma = pre_prep.rsplit(' , ', 1)[1]
                    pre_prep_beforecomma = pre_prep.rsplit(' , ', 1)[0] + ' , '

                    if len(pre_prep_afterdot) > len(pre_prep_aftercomma):  # 看是頓號先或是句號先
                        pre_prep_after = pre_prep_aftercomma
                        pre_prep_before = pre_prep_beforecomma
                    else:
                        pre_prep_after = pre_prep_afterdot
                        pre_prep_before = pre_prep_beforedot
                elif ' , ' in pre_prep:
                    pre_prep_after = pre_prep.rsplit(' , ', 1)[1].strip()
                    pre_prep_before = pre_prep.rsplit(' , ', 1)[0].strip() + ' , '
                elif 'and' in pre_prep:
                    pre_prep_after = pre_prep.rsplit('and', 1)[1].strip()
                    pre_prep_before = pre_prep.rsplit('and', 1)[0].strip() + ' and '
                elif '。' in pre_prep:
                    pre_prep_after = pre_prep.rsplit('。', 1)[1].strip()
                    pre_prep_before = pre_prep.rsplit('。', 1)[0].strip() + '。'
                else:
                    pre_prep_after = pre_prep
                    pre_prep_before = ''

                if not self.judge_pure_english(pre_prep_after):
                    pre_prep_afters = re.split(' ', pre_prep_after, re.IGNORECASE)
                    temp = pre_prep_afters
                    for word in temp:
                        if not self.judge_pure_english(word):
                            pre_prep_before = pre_prep_before + ' ' + word
                            pre_prep_afters.remove(word)

                    if not pre_prep_afters:
                        pre_prep_afters = temp
                    pre_prep_after = ' '.join(pre_prep_afters)

                if after_prep:
                    if after_prep[-1] == '。':
                        after_prep = after_prep.rstrip('。')
                        pre_prep_after = pre_prep_after + '。'

                after_prep = after_prep.replace(' , ','、')
                sent = pre_prep_before + self.prepkeyword[key].format(
                    after_prep) + ' ' + pre_prep_after + after_prep_drop

                sent = sent.replace('  ', ' ')

        return sent

    def deal_with_in_parentheses(self):
        for key in self.in_parentheses.keys():
            self.in_parentheses[key] = self.deal_with_verb(self.in_parentheses[key])
            self.in_parentheses[key] = self.deal_with_prep(self.in_parentheses[key])
            if 'cm' in self.in_parentheses[key]:
                self.in_parentheses[key] = self.in_parentheses[key].replace('cm','公分')
        return

    def deal_with_in_semicolon(self):
        for key in self.in_semicolon.keys():
            self.in_semicolon[key] = self.deal_with_verb(self.in_semicolon[key])
            self.in_semicolon[key] = self.deal_with_prep(self.in_semicolon[key])
        return

    def add_curly_brackets(self, matched):
        word = matched.group()
        word = '{' + word + '}'
        return word
    
    def translater(self, Text):

        def _replace_dot(matched):
            temp = matched.group()
            temp = temp.replace('.', '。')
            return temp

        output = ''
        for sent in Text.splitlines():  # 分離出一句話
            sent = sent.strip()
            self.tracer_words = {}
            self.in_parentheses = {}    # 存放括弧內句子
            self.in_semicolon = {}  # 存放分號內句子
            line_number = ''

            sent = self.total_replace(sent)

            if re.match('\d[)]\.\s', sent):      # 處理標新立異的行號
                sent = sent.replace('). ', '. ',1)
            if re.match('\d.\s', sent):
                line_number = sent.split(' ',1)[0]
                sent = sent.split(' ',1)[1].strip()

            sent = re.sub('\.[^\d]', _replace_dot, sent)

            sent = self.deal_with_tracer(sent)

            #  separate () from sentence
            if '(' in sent:  # 找出括弧內句子存放
                sent = sent.replace('(', ' ( ')
                if  ')' in sent:
                    sent = sent.replace(')', ' ) ')
                    in_the_parentheses = False
                    in_the_parentheses_temp = []
                    not_in_the_parentheses_temp = []
                    sign = ''
                    n = 0
                    words = re.split('\s', sent)
                    for word in words:
                        if word == '(' or word == ')':
                            in_the_parentheses = not in_the_parentheses
                            if in_the_parentheses_temp:
                                sign = str(n)
                                self.in_parentheses[n] = ' '.join(in_the_parentheses_temp)
                                in_the_parentheses_temp = []
                                sign = '(parentheses[' + sign + '])'
                                not_in_the_parentheses_temp.append(sign)
                                n = n + 1
                        elif word:
                            if in_the_parentheses:
                                in_the_parentheses_temp.append(word)
                            else:
                                not_in_the_parentheses_temp.append(word)
                    sent = ' '.join(not_in_the_parentheses_temp)
                else:
                    print('Error: missing a )')

            if ';' in sent:  # 找出分號內句子存放
                in_the_semicolon_temp = []
                temp = ''
                n = 0
                temp = sent.split(';',1)[0].strip()
                in_the_semicolon_temp = sent.split(';',1)[1].split(';')

                for section in in_the_semicolon_temp:
                    self.in_semicolon[n] = section
                    sign = 'semicolon[' + str(n) + ']'
                    temp = temp + ';' + sign
                    n = n + 1
                sent = temp

            # 與處理符號，保護基，將來能被視為獨立字元處理，與小數點區分
            sent = sent.replace(',',' , ')
            #sent = sent.replace('. ', ' . ')

            # 開始處理動詞，介係詞 句子結構

            sent = self.deal_with_verb(sent)

            sent = self.deal_with_prep(sent)

            if self.in_semicolon: # 解壓縮分號
                self.deal_with_in_semicolon()
                sent = re.sub('semicolon\[\d*\]', self.add_curly_brackets, sent)
                sent = sent.format(semicolon=self.in_semicolon)

            if self.in_parentheses: # 解壓縮括號
                self.deal_with_in_parentheses()
                sent = re.sub('parentheses\[\d*\]', self.add_curly_brackets, sent)
                sent = sent.format(parentheses=self.in_parentheses)

            if self.tracer_words: # 解壓縮示蹤劑片語
                sent = re.sub('tracer_word\[\d*\]', self.add_curly_brackets, sent)
                sent = sent.format(tracer_word=self.tracer_words)

            for key in self.phraselist: # 處理其他詞類、片語
                if key in sent.lower():
                    pattern = '\\b' + key + '\\b'
                    sent = re.sub(pattern, self.phrasemetrix[key][0], sent, 0, re.IGNORECASE)

            for key in self.adjant.keys(): # 處理形容詞類
                if key in sent.lower():
                    pattern = '\\b' + key + '\\b'
                    sent = re.sub(pattern, self.adjant[key], sent, 0, re.IGNORECASE)

            #print(sent)

            sent = sent.replace(',', '，')
            #sent = re.sub('[^\d]\.', '。', sent)
            words = sent.split(' ')
            temp = ''
            for word in words:
                if self.judge_pure_english(word):
                    temp = temp + ' ' + word + ' '
                else:
                    temp = temp +'' + word + ''
            temp = temp.replace('  ',' ')
            temp = temp.replace(' / ', '/')
            sent = temp

            for key in self.adjpost.keys(): # 處理形容詞類
                if key in sent.lower():
                    pattern = '\\b' + key + '\\b'
                    sent = re.sub(pattern, self.adjpost[key], sent, 0, re.IGNORECASE)

            if line_number:
                sent = line_number + ' ' + sent.strip()
            else:
                sent = sent.strip()

            output = output + linesep + sent

        return output



    def GetClipboard(self):
        win32clipboard.OpenClipboard()
        temp = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return temp

    def SetClipboard(self, text):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        win32clipboard.CloseClipboard()
        return

if __name__ == '__main__':

    T = Translater()

    Text = 'Multiple nodular and patch-like pattern and miliary nodules with mottled increased FDG uptake (maxSUV:16.4) in the LLL, mainly in the superior segment and lateral segment. Active infectious/inflammatory process is suspected first. Focal atelectasis in the superior segment is also noted.'
    Text1 = 'Small foci with faint FDG uptake in the right breast, possible adenoma or fibroadenoma.'
    Text2 = 'There is mildly increased FDG uptake in the uterine cavity and right tubo-ovarian region, which could be physiologic change associated with menstrual cycle.'
    Text3 = 'CT showed several small hepatic cysts. '
    Text4 = 'Fibroinfiltrative change and some calcified nodules in the LUL; subpleural infiltration in lateral'
    Text5 = 'Normal physiological FDG-PET study of the brain'
    Text6 = 'Soft tissue swelling or semilunar-shaped mass with mild FDG uptake in the right serratus anterior muscle, r/o elastofibroma dorsi.'
    Text7 = 'CT shows a subpleural small nodule in basal lateral LLL, status post right nephrectomy, a left renal cyst in the lower pole, and L4/5 spondylolisthesis (all stationary).'
    Text8 = 'Suspected right side elastofibroma dorsi (DDx: myositis). Follow up is recommended.'
    Text9 = 'Small foci with faint FDG uptake in the right breast, possible adenoma or fibroadenoma. Regular follow up with mammography or breast ultrasound is recommended.'
    Text10 = 'There are enlarged lymph nodes with increased FDG uptake in bilateral hilar and mediastinal regions, likely due to lymphadenitis.'
    Text11 = 'Mild increased FDG uptake in bilateral hilar and mediastinal tiny lymph nodes is likely due to lymphadenitis.'
    Text12 = 'There is mildly increased FDG uptake in the distal esophagus near EC junction, which could be due to mild inflammation associated with GERD.'
    Text13 = 'Right lung tiny nodules need follow up with LDCT 1 year later.'
    Text14 = 'Mildly focal increased FDG uptake in the left portion of prostate (stationary as compared with prior study on 2015/7/22), possibly due to hyperplasia or mild inflammation.'
    Text15 = 'Mildly focal increased FDG uptake in the left portion of prostate (與前次檢查相比無變化 2015/7/22), possibly due to hyperplasia or mild inflammation.'
    Text16 = '1). Mildly focal increased FDG uptake in the L2/L3, L3/L4 and L5/S1 right facet joints and L3/L4 posterior junction, likely due to degenerative arthritis. CT shows L4/L5 spondylolisthesis.'
    Text17 = '2). Non-specific faint nodal FDG uptake in the left upper neck small LNs, likely due to lymphadenitis.'
    Text18 = '3). CT shows two tiny nodules (3/2.5 mm) in the LUL;right renal cyst (2 cm). '
    Text19 = 'CT shows accessory spleen; hypodense small nodule in the lower portion of left thyroid lobe; small right hepatic cyst; stationary nodular lesion (2.1*1.4*1.5 cm) bulging from the left anterior uterine wall, c/w uterine myoma; stationary small nodule in the LLL (0.35cm/ image 312-313).  No obvious hypermetabolic lesion is detected to suggest evidence of tumoral uptake. Suggest regular clinical follow up. '
    Text20 = '3). CT shows a tiny nodule (3.5 mm) in the RLL and a small flat nodule (4.5 mm) in the RML; fatty liver; GB stones.'
    Text21 = 'Fibrocystic change and few tiny calcifiaction in both breasts. Suggest regular follow up with breast ultrasound annually.'
    Text22 = '1. Stationary fibrotic change with very faint FDG uptake along the surgical sutures in posterior LUL, compatible with post-surgical change. '
    Text23 = '2. Stationary faint FDG uptake in the left axillary small lymph node, likely due to lymphadenitis.'
    Text24 = '3. Stationary focal mildly increased FDG uptake in the nasopharyngeal adenoid, likely due to reactive hyperplasia.'
    Text25 = '4. Stationary focal mild FDG uptake in the right costoclavicular junction, likely due to degenerative change.'
    Text26 = '5. Focal mild FDG uptake in the junctions between L2/L3 and L3/L4 spinous process, likely due to degenrative change.'
    Text27 = '6. Focal mild FDG uptake in the distal esophagus near EC junction, possibly due to reflux esophagitis.'
    Text28 = 'Infiltrations with faint to mild FDG uptake in the RML, basal-posterior RLL and basal-posterior LLL are also found, considering active inflammatory process.'
    Text29 = 'Stationary RUL, RLL and LUL tiny nodules as compared with LDCT on 2016/5/4. Suggest regular follow up with LDCT. '


    print(T.translater(Text19))