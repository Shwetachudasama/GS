from flask import Flask, render_template, request, redirect, url_for, session,flash
from multiprocessing import Value
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
counter=Value('i',0)
ans_counter=Value('i',0)

'''
queslist_format:
0:topic
1:correct_ans -> [0:guj, 1:english ]
2:question in Gujrati
3:question in english
4:hint1 [0->guj, 1:eng]
5:hint2[0->guj, 1:eng]
6: options 
'''




topics={'basics':0, "numbers":0,"singularPlural":0, "gender":0, "noun":0,"verb":0}
queslist=[
   ["basics", ["ચ", "cha"], "છ પહેલા કયુ વ્યંજન આવે?", "Cha pahelaa kayu vyanjan aave?", ["ન પછી કયુ વ્યંજન આવે?", "na pachi kayu vyanjan aave?"], ["ચકલી મા આ વ્યંજન આવે છે.", "chakli ma aa vyanjan aave che."], [["જ", "pha"], ["ચ", "cha"], ["ય", "ya"], ["ઝ", "jha"]]],

["basics", ["કેરી", "keri"], "નીચે આપેલ શબ્દમાંથી ફડ કયુ છે?",  "Niche aaple shabdomathi phad kayu che?", ["આ ફડ ને રાજા કેવાય છે." , "aa fad no raja kevay che."], ["આ ફડ નો રંગ પીળો છે", "aa fad no rang pidu che"], [["કાકડી", "kakdi"], ["કેરી", "keri"], ["વટાણા", "vatana"], ["ગાજર", "gajar"]]],

["numbers", ["નવ", "nav"], "આઠ પછી કયો આંકડો આવે છે?",  "Aath pachi kayo aankdo aave che?", ["દસ પેહલા કયો આક્ડો આવે છે?","das pehla kayo aakdo aave che?"], ["નવરાત્રી કેટલા રાત્રી નો સંગમ છે?", "navratri ketla ratri no sangam che?"], [["એક", "aek"], ["સાત", "saat"], ["પાંચ", "panch"], ["નવ", "nav"]]],

["numbers", ["સાત", "saat"], "દુનિયામા કેટલી અજયબી છે?",  "Duniyama ketli ajaybiao che?", ["મેઘધનુષ્ય મા કેટલા રંગ છે?", "megdhanushya ma ketla rang che?"], ["આઠ પેહલા કયો આક્ડો આવે છે?", "aath pehla kayu aankdo aave che"], [["આઠ", "aath"], ["સાત", "saat"], ["પાંચ", "panch"], ["નવ", "nav"]]],

["singularPlural", ["વૃક્ષો વૃક્ષ", "vruksho vruksh"], "અમે આજે એકવીસ ___ વાવ્યા અને એક ___ ની ભેટ આપી.",  "Ame aaje aekvis ___ vavya ane aek ___ ni bhet aapi.", ["આમાંથી કયું બહુવચન છે અને કયું એકવચન છે" , "aamathi kayu bahuvachan che ane kayu aekvachan che"], ["ક્ષ નુ બહુવચન ક્ષો થાય છે", "ksh nu bahuvachan ksho thay che"], [["વૃક્ષ વૃક્ષો", "vruksh vruksho"], ["વૃક્ષો વૃક્ષ", "vruksho vruksh"]]],

["singularPlural", ["ભાષાઓ ભાષા", "bhashao bhasha"], "અમે ત્રણ ___ બોલીએ છે. ગુજરાતી એક ___ છે.",  "Ame tran ___ boliae che. Gujarati aek ___ che.", ["આમાંથી કયું બહુવચન છે અને કયું એકવચન છે" , "aamathi kayu bahuvachan che ane kayu aekvachan che"], ["ષ નુ બહુવચન ષો થાય છે", "sh nu bahuvachan sho thay che"], [["ભાષા ભાષાઓ", "bhasha bhashao"], ["ભાષાઓ ભાષા", "bhashao bhasha"]]],

["gender", ["પિતા", "pita"], "લિંગ બદલો: માતા - ____", "Ling badlo: mata - ____", ["પ મા તમે નાનુ ઇ બોલસો કે મોટુ ઈ?", "pa ma tame nanu i bolso ke motu ee"], ["આમા અગર નાનુ ઇ આવે તોહ પ નુ પિ તસે અને મોટુ આવે તો પ નુ પી આવસે", "aama agar nanu i aave toh pa nu pi thase ane motu aave to pa nu pee aavse"], [["પિતા", "pita"], ["પીતા", "peeta"]]],

["gender", ["છોકરો", "chokaro"], "લિંગ બદલો: __ - છોકરી", "Ling badlo: ____ - chokaree", ["આમા પેહલા પુલ્લિંગ કયા આવસે અને સ્ત્રીલિંગ કયા આવસે એ સોદો", "aama pehla puling kya aavse ane striling kya aavse ae sodho"], ["આમા જો કે રો આવસે કે રૌ", "aama joao ke ro aavse ke rau"], [["છોકરો", "chokaro"], ["છોકરૌ", "chokhrau"]]],

["noun", ["ગામડુ" "ગામડા", "gaamdu gaamda"], "મહારાષ્ટ્રનુ નવાપુરનુ ___(ગામ) છોડીને ગુજરાતના ___(ગામ) શરૂ થાય છે.",  "Maharashtranu Navapurnu ___(gaam) chodine Gujaratna ___(gaam) sharu thay che.", ["આમા કયુ બહુવચન છે ને કયુ એક્વચન છે", "ama kayu bahuvachan che ne kayu aekvachan che"], ["આમા ડુ નુ બહુવચન ડા થાય છે", "aama du nu bahuvachan da thay che"], [["ગામડુ ગામડા", "gaamdu gaamda"], ["ગામડા ગામડુ", "gaamda gaamdu"]]],

["noun", ["છોકરાનુ છોકરીનુ", "chokaranu chokareenu"], "નિમિષના _(છોકર) નામ હર્ષ અને _(છોકર) નામ મનશ્રી છે.",  "Nimishna ___(chokar) naam Harsh ane ___(chokar) naam Manashree che.", ["આમા પેહલા પુલ્લિંગ કયા આવસે અને સ્ત્રીલિંગ કયા આવસે એ સોદો", "aama pehla kya puling aavse ane striling kya aavse ae sodho"], ["આમ હર્ષ પેહલા પુલ્લિંગ આવ્સે અને મનશ્રી પેહલા સ્ત્રીલિંગ આવસે", "aama Harsh pehla puling aavse ne Manashree pehla striling aavse"], [["છોકરાનુ છોકરીનુ", "chokaranu chokareenu"], ["છોકરીનુ છોકરાનુ", "chokareenu chokaranu"]]],

["verb", ["રમ્યો", "ramyo"], "હું ગઈકલે ફુટબોલ __(રમ).",  "Hu gaeekaale football ___(ram).", ["આમા કયુ કાળ આવસે?", "aama kayu kaad aavse?"], ["આ ભૂતકાળ છે.", "aa bhutkaad che."], [["રમ્યો", "ramyo"], ["રમુ છુ", "ramu chu"], ["રમીશ", "rameesh"]]],

["verb", ["દોડુ છુ", "dodu chu"], "હુ હમણા ___(દોડ).",  "Hu hamna ___(dod).", ["આમા કયુ કાળ આવસે?", "aama kayu kaad aavse?"], ["આ વર્તમાન કાળ છે.", "aa vartaman kaad che"] , [["દોડયો", "dodyo"], ["દોડુ છુ", "dodu chu"], ["દૌડીશ", "daudeesh"]]]
    ]

def pretest():
    if counter.value!=0:
        #Start to verify the answer
        qid=counter.value-1
        ans=request.form.get('option') 
        topic=queslist[qid][0] #Fetching the topic Name
        if queslist[qid][1][1]==ans: #Mathimg with the English value of ans
            topics[topic]+=1
        else:
            topics[topic]-=0.8

        hint_count=request.form.get('hint_count')
        if hint_count:
            hint_count=int(hint_count)
            topics[topic]-=(0.3)*hint_count
        #End to verify the answer


    #Start to generate questions dynamically
    with counter.get_lock():
        if counter.value<12:
            counter.value+=1
        else:
            weak_topic=""
            for  key,value in topics.items():
                if value<=0:
                    weak_topic=key
                    break
            return render_template("index.html",weak_topic=weak_topic)
    #End to generate questions dynamically
    
    return render_template("pretest.html",ques=queslist[counter.value-1])

            
        

        