from flask import Flask,render_template,request,session,redirect,url_for,Response,send_file
import pandas as pd
from datetime import datetime, date, timedelta
import datetime as dt
from dateutil.relativedelta import relativedelta
import mysql.connector
import jpholiday
import calendar
import workdays
#おまじない
app=Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

def timedelta_to_HM(td):
    """
    timedelta型をH:Mになおすための関数
    input:timedlta型の値(ex.10:30)
    output:HourとMinute(ex.10,30)
    """
    sec = td.total_seconds()
    return (sec//3600, sec%3600//60)
def int_to_HM(s):
    """
    TODO 上のコードとインデントそろってないですねdone
            
    整数をH:Mに直す関数
    input:秒
    output:H:M
    """
    s=int(s)
    hours=s//3600
    minutes=s%3600//60
        
    if minutes==0:
        HM=str(hours)+":00"
                

    else:
                
        minutes="%02d" % minutes
        HM=str(hours)+":"+str(minutes)
               
        return HM
def int_to_HMS(s):
    """
    秒をH:M:Sに直す関数
    input:秒
    output:H:M:S
    """
    s=int(s)
    hours=s//3600
    minutes=s%3600//60
    seconds=s%60
    if minutes==0:
            if seconds==0:
                    HMS=str(hours)+":00:"+"00"
            else:
                    seconds="%02d" % seconds
                    HMS=str(hours)+":"+"00"+":"+str(seconds)

    else:
            if seconds==0:
                    minutes="%02d" % minutes
                    HMS=str(hours)+":"+str(minutes)+":00"
            else:
                    minutes="%02d" % minutes
                    seconds="%02d" % seconds
                    HMS=str(hours)+":"+str(minutes)+":"+str(seconds)
    return HMS

def int_to_HMS2(s):
    """
    秒をhour,minute,secondに分割するための関数
    input:秒
    output:hour,minute,second
    """
    s=int(s)
    hours=s//3600
    minutes=s%3600//60
    seconds=s%60
    if minutes==0:
        if seconds==0:
                minutes="00"
                seconds="00"
        else:
                minutes="00"
                seconds="%02d" % seconds
                    

    else:
        if seconds==0:
                minutes="%02d" % minutes
                seconds="00"
        else:
                minutes="%02d" % minutes
                seconds="%02d" % seconds
    return hours,minutes,seconds
#ログインIDとパスワードが合っているかチェック(一般用)
def _is_user_id_valid(input_username,input_password):
        try:
                
                conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
                cur = conn.cursor(buffered=True)
                conn.ping(reconnect=True)
                #一般ユーザーのDBからユーザーIDとパスワードを取得
                cur.execute('select loginID,password from USER_ACCOUNT')

                id_and_password = cur.fetchall()
                #print(id_and_pass)

                cur.close()
                
                conn.close()

                for i in range(len(id_and_password)):
                        if str(id_and_password[i][0]) == str(input_username) and str(id_and_password[i][1]) == str(input_password):
                                return True
                                

                return False
        except:
                print("入力内容が間違った時のエラー")
                return False

#ログインIDとパスワードが合っているかチェック(管理者用)
def admin_is_user_id_valid(input_username,input_password):
        try:
                
                conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
                
                cur = conn.cursor(buffered=True)
                conn.ping(reconnect=True)
                #管理者用ユーザーDBからユーザーIDとパスワードを取得
                cur.execute('select loginID,password from ADMIN_USER_ACCOUNT')

                id_and_password = cur.fetchall()
                #print(id_and_pass)

                cur.close()
                
                conn.close()

                for i in range(len(id_and_password)):
                        if str(id_and_password[i][0]) == str(input_username) and str(id_and_password[i][1]) == str(input_password):
                                return True
                                

                return False
        except:
                print("入力内容が間違った時のエラー")
                return False

#ログインして打刻画面へ
@app.route("/")
def login_go():
        error=[]
        if 'user_id' in session:
                """
                TODO
                大枠でいいので、何を渡したいかを書いてもらえると良いかと思いました。
                今回であれば、最終的にreturnする値が、下記なのでこの内容を拾ってくるためのコードであるように書いて頂けますと幸いです。
                name=username_and_employeeno[0],employee_no=username_and_employeeno[1],error=error[0]
                ログインした後の方がレビュー作業が出来そうなので、ここで一旦レビュー止めます。
                """
                today = datetime.today()
                year=today.year
                month=today.month
                month="%02d" % month #例)9→09へ変換

                holiday=jpholiday.month_holidays(int(year), int(month)) #祝日を取得
                numberOfdays=calendar.monthrange(int(year), int(month)) #一ヶ月の日数を取得

                start_date = dt.datetime(int(year), int(month), 1)
                end_date = dt.datetime(int(year),int(month),numberOfdays[1])
                Number_of_working_days=workdays.networkdays(start_date, end_date)-len(holiday) #所定日数を取得
                WorkTimeInMonth=Number_of_working_days*8 #所定時間
                str_WorkTimeInMonth=str(WorkTimeInMonth)+":00"
                numberOfholiday=numberOfdays[1]-workdays.networkdays(start_date, end_date)+len(holiday) #休日を取得
                
                conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
                
                conn.ping(reconnect=True)
                cur = conn.cursor(buffered=True)
                #ユーザーの社員番号と名前を取得
                cur.execute('select name,employee_no from USER_ACCOUNT where loginID= "' + str(session['user_id'][0]) + '";')
                username_and_employeeno=cur.fetchone()
                error.append(None)
                #その月の出勤状況があるかないかを確かめるために呼び出し(ATTENDANCE_STATUS:出勤状況,WORKING_HOURS:勤務時間,
                #HOLIDAY_AND_VACATION_ACQUISITION:休日・休暇取得,WORK_CLASSIFICATION:勤務区分)
                cur.execute('SELECT * FROM ATTENDANCE_STATUS WHERE employee_no="' + str(username_and_employeeno[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                attendance_status_table=cur.fetchone()
                print(attendance_status_table)
                cur.execute('SELECT * FROM WORKING_HOURS WHERE employee_no="' + str(username_and_employeeno[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                working_hours_table=cur.fetchone()
                print(working_hours_table)
                cur.execute('SELECT * FROM HOLIDAY_AND_VACATION_ACQUISITION WHERE employee_no="' + str(username_and_employeeno[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                holiday_and_vacation_acquisition_table=cur.fetchone()
                cur.execute('SELECT * FROM WORK_CLASSIFICATION WHERE employee_no="' + str(username_and_employeeno[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                work_classification_table=cur.fetchone()
                #その月の出勤状況がなければそれぞれ新しくINSERT
                if(attendance_status_table==None):
                        cur.execute('INSERT INTO ATTENDANCE_STATUS VALUES (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(username_and_employeeno[1],username_and_employeeno[0],today,Number_of_working_days,0,0,0,0,0,0,))
                        conn.commit()
                if(working_hours_table==None):
                        cur.execute('INSERT INTO WORKING_HOURS VALUES (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(username_and_employeeno[1],username_and_employeeno[0],today,0,0,str_WorkTimeInMonth,"8:00",0,0,0,0,0,0,0,0,))
                        conn.commit()
                if(holiday_and_vacation_acquisition_table==None):
                        cur.execute('INSERT INTO HOLIDAY_AND_VACATION_ACQUISITION VALUES (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(username_and_employeeno[1],username_and_employeeno[0],today,numberOfholiday,0,18,0,0,0,0,0,0,))
                        conn.commit()
                if(work_classification_table==None):
                        cur.execute('INSERT INTO WORK_CLASSIFICATION VALUES (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(username_and_employeeno[1],username_and_employeeno[0],today,0,0,0,0,0,0,0,0,0,0,0,))
                        conn.commit()
                #打刻処理を行う画面へ遷移
                return render_template("engraving.html",name=username_and_employeeno[0],employee_no=username_and_employeeno[1],error=error[0])
        return redirect('/login')

#管理者ログイン画面でログインに成功すると最初に行われる処理
@app.route("/admin_daily_attendance")
def admin_daily_attendance():
        error=[]
        if 'user_id' in session:
                today = datetime.today()
                year=today.year
                month=today.month
                month="%02d" % month
                no=[]
                day=[]
                employee_no=[]
                name=[]
                start_time_timeOnly=[]
                finish_time_timeOnly=[]
                break_start_time_timeOnly=[]
                break_finish_time_timeOnly=[]
                interval_time=[]
                approval_status=[] 
                conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
                
                conn.ping(reconnect=True)
                cur = conn.cursor(buffered=True)
                #管理者の名前と社員番号を取得
                cur.execute('select name,employee_no from ADMIN_USER_ACCOUNT where loginID= "' + str(session['user_id'][0]) + '";')
                username_and_employeeno=cur.fetchone()
                error.append(None)
                #申請・承認状況が承認待ち(一般ユーザーが申請を行っている状態)であるものを取得
                cur.execute('select * from WORK_STATUS where application_and_approval= "承認待ち" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                work_status_table=cur.fetchall()
                #一般ユーザーを全取得
                cur.execute('SELECT employee_no,name From USER_ACCOUNT')
                general_user=cur.fetchall()
                
                #表示するデータが綺麗に出力されるように前処理
                for i in range(len(work_status_table)):
                        no.append(work_status_table[i][0])
                        employee_no.append(work_status_table[i][1])
                        day.append(work_status_table[i][2].day)
                        start_time_timeOnly.append(work_status_table[i][4].time())
                        finish_time_timeOnly.append(work_status_table[i][5].time())
                        if work_status_table[i][6]==None:
                                break_start_time_timeOnly.append("0:00")
                        else:
                                break_start_time_timeOnly.append(work_status_table[i][6].time())
                        if work_status_table[i][7]==None:
                                break_finish_time_timeOnly.append("0:00")
                        else:
                                break_finish_time_timeOnly.append(work_status_table[i][7].time())
                        interval_time.append(work_status_table[i][8])
                        approval_status.append(work_status_table[i][9])
                for i in range(len(employee_no)):
                        for j in range(len(general_user)):
                                if employee_no[i]==general_user[j][0]:
                                        name.append(general_user[j][1])

                #セレクトボックスに表示する内容
                work_status_table_length=len(work_status_table)
                select1="承認待ちのみ"
                selected_value1="./admin_daily_attendance2"
                select2="全て表示"
                selected_value2="./all_employee_display"
                return render_template("admin_daily_attendance.html",admin_name=username_and_employeeno[0],admin_employee_no=username_and_employeeno[1],error=error[0],day=day,work_start_time=start_time_timeOnly,work_finish_time=finish_time_timeOnly,break_start_time=break_start_time_timeOnly,break_finish_time=break_finish_time_timeOnly,interval_time=interval_time,work_status_table_length=work_status_table_length,year=year,month=month,approval_status=approval_status,no=no,general_user_name=name,general_user_employee_no=employee_no,select1=select1,selected_value1=selected_value1,select2=select2,selected_value2=selected_value2)
        return redirect('/login')

#一般ユーザーが入力したログインIDとパスワードがDBに存在するかチェック
@app.route('/login', methods=['GET', 'POST'])
def login():
        #エラーメッセージはtitleに入れます
        title = []
        #入力内容が正しければindex()に移ります。
        if request.method == 'POST':
                
                if _is_user_id_valid(request.form['userID'],request.form['password']):
                        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
                        
                        conn.ping(reconnect=True)
                        cur = conn.cursor(buffered=True)
                        cur.execute('select loginID from USER_ACCOUNT where loginID= "' + str(request.form['userID']) + '";')
                        user_id2=cur.fetchone()       
                        session['user_id'] = user_id2
                        print(session['user_id'][0])
                        
                        return redirect(url_for('login_go'))
                else:
                        title.append("ユーザーIDまたはパスワードが間違っています")
                        return render_template('login.html')
        #正しくなければもう一度loginページを表示します

        return render_template('login.html')

#管理者が入力したログインIDとパスワードがDBに存在するかチェック
@app.route('/login2', methods=['GET', 'POST'])
def login2():
        #エラーメッセージはtitleに入れます
        title = []
        #入力内容が正しければindex()に移ります。
        if request.method == 'POST':
                
                if admin_is_user_id_valid(request.form['userID'],request.form['password']):
                        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
                        
                        conn.ping(reconnect=True)
                        cur = conn.cursor(buffered=True)
                        cur.execute('select loginID from ADMIN_USER_ACCOUNT where loginID= "' + str(request.form['userID']) + '";')
                        user_id2=cur.fetchone()       
                        session['user_id'] = user_id2
                        print(session['user_id'][0])
                        
                        return redirect(url_for('admin_daily_attendance'))
                else:
                        title.append("ユーザーIDまたはパスワードが間違っています")
                        return render_template('admin_login.html')
        #正しくなければもう一度loginページを表示します

        return render_template('admin_login.html')

#ログアウトを行う
@app.route('/logout',methods=['GET','POST'])
def logout():
        #セッションからユーザ名を取り除く (ログアウトの状態にする)
        session.pop('user_id',None)
        # ログインページにリダイレクトする
        return redirect(url_for('login'))

#一般ユーザーの新規会員登録
@app.route('/account_create',methods=['POST'])
def account_create():
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        #ユーザーが入力した情報をPOSTで取得
        name=request.form["employee_name"]
        employee_no=request.form["employee_no"]
        employment_status=request.form["employment_status"]
        department=request.form["department"]
        mail=request.form["mail"]
        loginID=request.form["loginID"]
        password=request.form["password"]
        password_confirmation=request.form["password_confirmation"]
        # print(password)
        # print(password_confirmation)
        if str(password)!=str(password_confirmation):
                error="パスワードが一致していません。"
                return render_template('account_create.html',error=error)
        if name=="" or employee_no=="" or employment_status=="" or department=="" or mail=="" or loginID=="" or password=="" or password_confirmation=="":
                error="未入力の項目があります。"
                return render_template('account_create.html',error=error)
        cur.execute('SELECT * FROM USER_ACCOUNT WHERE employee_no="' + str(employee_no) + '"')
        user_account1=cur.fetchall()
        cur.execute('SELECT * FROM USER_ACCOUNT WHERE loginID="' + str(loginID) + '"')
        user_account2=cur.fetchall()

        if user_account1==[] and user_account2==[]:
                cur.execute('INSERT INTO USER_ACCOUNT values(0,%s,%s,%s,%s,%s,%s,%s)',(name,employee_no,employment_status,department,mail,loginID,password,))
                cur.close()
                conn.commit()
                conn.close()
                return render_template('login.html')
        elif user_account1==[] and user_account2!=[]:
                error="入力されたログインIDは既に存在します。"
                return render_template('account_create.html',error=error)
        elif user_account1!=[] and user_account2==[]:
                error="入力された社員番号は既に存在します。"
                return render_template('account_create.html',error=error)
        else:
                error="入力された社員番号とログインIDは既に存在します。"
                return render_template('account_create.html',error=error)
                




#新規会員登録の画面へ遷移      
@app.route('/account_create_display')
def account_create_display():
        error=""
        return render_template('account_create.html',error=error)
#管理者ログイン画面へ遷移
@app.route('/admin_login')
def admin_login():
        return render_template('admin_login.html')
#一般ユーザーログイン画面へ遷移
@app.route('/login_display')
def login_display():
        return render_template('login.html')
#出勤ボタンが押されたときに行う処理
@app.route('/work_start',methods=['POST','GET'])
def work_start():
        error=[]
        if request.method=="POST":
                print("出勤")
                conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
                
                conn.ping(reconnect=True)
                cur = conn.cursor(buffered=True)
                name=request.form["name"]
                employee_no=request.form["employee_no"]
                date=request.form["date"]
                DayOfTheWeek=request.form["DayOfTheWeek"]
                datetime=request.form["datetime"]
                print(date)
                #ユーザーが存在するかチェック
                cur.execute('SELECT exists (SELECT employee_no FROM WORK_STATUS WHERE employee_no= "' + str(employee_no) + '")')
                user_exist=cur.fetchone()
                
                #print(user_exist[0])
                #存在しない場合初めての登録
                if(user_exist[0]==0):
                        error.append(None)
                        cur = conn.cursor(buffered=True)
                        cur.execute('INSERT INTO WORK_STATUS values(0,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(employee_no,date,DayOfTheWeek,datetime,None,None,None,"0:00","未申請",))
                        conn.commit()
                        return render_template('engraving.html',name=name,employee_no=employee_no,error=error[0])
                cur = conn.cursor(buffered=True)
                #既に出勤済でないかチェック
                cur.execute('SELECT employee_no,work_start_time FROM WORK_STATUS WHERE WORK_STATUS.work_start_time=(SELECT MAX(work_start_time) from WORK_STATUS as ws WHERE ws.employee_no= "' + str(employee_no) + '" ) AND employee_no= "' + str(employee_no) + '" AND work_finish_time IS NOT NULL AND work_start_time IS NOT NULL')
                user_status=cur.fetchone()
                print(user_status)
                #出勤できる場合の処理
                if(user_status!=None):
                        error.append(None)
                        #出勤時間などをINSERT
                        cur.execute('INSERT INTO WORK_STATUS values(0,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(employee_no,date,DayOfTheWeek,datetime,None,None,None,None,"未申請",))
                        conn.commit()
                        #前回の退勤時間を取得
                        cur.execute('select max(date),max(work_finish_time) from WORK_STATUS where employee_no="' + str(employee_no) + '"')
                        yesterday_work_finish_time=cur.fetchone()
                        #print(yesterday_work_finish_time[1])
                        #今日の出勤時間を取得
                        cur.execute('select No,max(date),max(work_start_time) from WORK_STATUS where employee_no="' + str(employee_no) + '" AND WORK_STATUS.work_start_time=(SELECT MAX(work_start_time) from WORK_STATUS as ws WHERE ws.employee_no= "' + str(employee_no) + '" )')
                        today_work_start_time=cur.fetchone()
                        print(today_work_start_time[2])
                        #勤務間インターバル時間を計算
                        interval_time=today_work_start_time[2]-yesterday_work_finish_time[1]
                        print(type(interval_time))
                        #勤務間インターバル時間を挿入
                        cur.execute('UPDATE WORK_STATUS set interval_time="' + str(interval_time) + '" WHERE No="' + str(today_work_start_time[0]) + '"')
                        conn.commit()
                        return render_template('engraving.html',name=name,employee_no=employee_no,error=error[0])
                else:
                        error.append("既に出勤中です。")
                        return render_template('engraving.html',name=name,employee_no=employee_no,error=error[0])

                cur.close()
                conn.commit()
                conn.close()

                

#休憩開始ボタンが押されたときの処理
@app.route('/break_start',methods=['POST','GET'])
def break_start():
        error=[]
        if request.method=="POST":
                #print("休憩開始")
                conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
                
                conn.ping(reconnect=True)
                cur = conn.cursor(buffered=True)
                name=request.form["name"]
                employee_no=request.form["employee_no"]
                date=request.form["date"]
                DayOfTheWeek=request.form["DayOfTheWeek"]
                datetime=request.form["datetime"]
                #休憩開始できるかチェック
                cur.execute('SELECT employee_no,break_start_time FROM WORK_STATUS WHERE WORK_STATUS.date=(SELECT MAX(date) from WORK_STATUS as ws WHERE ws.employee_no= "' + str(employee_no) + '" ) AND employee_no= "' + str(employee_no) + '" AND work_start_time IS NOT NULL AND break_finish_time IS NULL AND work_finish_time IS NULL AND break_start_time IS NULL')
                user_status=cur.fetchone()
                #休憩開始ができる場合
                if(user_status!=None):
                        error.append(None)
                        #休憩開始時刻を挿入
                        cur.execute('UPDATE WORK_STATUS set break_start_time="' + str(datetime) + '" where employee_no="' + str(employee_no) + '" AND work_start_time IS NOT NULL AND work_finish_time IS NULL;')
                        conn.commit()
                        return render_template('engraving.html',name=name,employee_no=employee_no,error=error[0])

                else:
                        error.append("休憩できません。")
                        return render_template('engraving.html',name=name,employee_no=employee_no,error=error[0])
                cur.close()
                conn.commit()
                conn.close()

#休憩終了ボタンが押されたときの処理
@app.route('/break_finish',methods=['POST','GET'])
def break_finish():
        error=[]
        if request.method=="POST":
                # print("休憩終了")
                conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
                
                conn.ping(reconnect=True)
                cur = conn.cursor(buffered=True)
                name=request.form["name"]
                employee_no=request.form["employee_no"]
                date=request.form["date"]
                DayOfTheWeek=request.form["DayOfTheWeek"]
                datetime=request.form["datetime"]
                #休憩終了できるかチェック
                cur.execute('SELECT employee_no,break_finish_time FROM WORK_STATUS WHERE WORK_STATUS.date=(SELECT MAX(date) from WORK_STATUS as ws WHERE ws.employee_no= "' + str(employee_no) + '" ) AND employee_no= "' + str(employee_no) + '" AND work_start_time IS NOT NULL AND break_start_time IS NOT NULL AND work_finish_time IS NULL AND break_finish_time IS NULL')
                user_status=cur.fetchone()
                #休憩終了できる場合
                if(user_status!=None):
                        error.append(None)
                        #休憩終了時刻を挿入
                        cur.execute('UPDATE WORK_STATUS set break_finish_time="' + str(datetime) + '" where employee_no="' + str(employee_no) + '" AND work_start_time IS NOT NULL AND break_start_time IS NOT NULL AND work_finish_time IS NULL;')
                        conn.commit()
                        return render_template('engraving.html',name=name,employee_no=employee_no,error=error[0])

                else:
                        error.append("休憩中ではありません。")
                        return render_template('engraving.html',name=name,employee_no=employee_no,error=error[0])
                cur.close()
                conn.commit()
                conn.close()

#退勤ボタンが押されたときの処理
@app.route('/work_finish',methods=['POST','GET'])
def work_finish():
        error=[]
        if request.method=="POST":
                # print("勤務終了")

                conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
                
                conn.ping(reconnect=True)
                cur = conn.cursor(buffered=True)
                name=request.form["name"]
                employee_no=request.form["employee_no"]
                date=request.form["datetime"]
                date = dt.datetime.strptime(date,'%Y/%m/%d %H:%M:%S') 
                year=date.year
                month2=date.month
                month="%02d" % month2
                day=date.day

                # tomorow_date=date+dt.timedelta(days = 1)
                #昨日の日付を取得
                yesterday_date=date-dt.timedelta(days = 1)

                # tomorow_year=tomorow_date.year
                # tomorow_month=tomorow_date.month
                # tomorow_month="%02d" % tomorow_month
                # tomorow_day=tomorow_date.day

                yesterday_year=yesterday_date.year
                yesterday_month2=yesterday_date.month
                yesterday_month="%02d" % yesterday_month2
                yesterday_day=yesterday_date.day

                DayOfTheWeek=request.form["DayOfTheWeek"] #曜日
                datetime=request.form["datetime"] #退勤時刻
                #退勤できるかチェック
                cur.execute('SELECT No,employee_no,break_finish_time FROM WORK_STATUS WHERE WORK_STATUS.date=(SELECT MAX(date) from WORK_STATUS as ws WHERE ws.employee_no= "' + str(employee_no) + '" ) AND employee_no= "' + str(employee_no) + '" AND work_start_time IS NOT NULL AND work_finish_time IS NULL AND (break_start_time IS NULL OR break_finish_time IS NOT NULL)')
                user_status=cur.fetchone()
                #退勤できる場合
                if(user_status!=None):
                        error.append(None)
                        #退勤時刻を挿入することができるnoを探す
                        cur.execute('SELECT No,employee_no,break_finish_time FROM WORK_STATUS WHERE WORK_STATUS.date=(SELECT MAX(date) from WORK_STATUS as ws WHERE ws.employee_no= "' + str(employee_no) + '" ) AND employee_no= "' + str(employee_no) + '" AND work_start_time IS NOT NULL AND work_finish_time IS NULL AND (break_start_time IS NULL OR break_finish_time IS NOT NULL)')
                        user_no=cur.fetchone()
                        #退勤時刻を挿入
                        cur.execute('UPDATE WORK_STATUS set work_finish_time="' + str(datetime) + '" WHERE No="' + str(user_no[0]) + '"')
                        conn.commit()
                        #今日の出勤時刻、休憩開始時刻、休憩終了時刻を取得
                        cur.execute('SELECT work_start_time,break_start_time,break_finish_time FROM WORK_STATUS WHERE No="' + str(user_no[0]) + '"')
                        work_status_table=cur.fetchone()
                        #退勤時刻をdatetime型に変換
                        datetime = dt.datetime.strptime(datetime, '%Y/%m/%d %H:%M:%S')
                        #労働時間を計算
                        work_time=datetime-work_status_table[0]
                        work_time_sec=work_time.total_seconds()
                        print(type(work_time_sec))
                        # cur.execute('SELECT Total_working_hours FROM WORKING_HOURS WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                        # sample=cur.fetchone()
                        #労働時間の詳細が保存されているDBを呼び出し、今月のものを取得
                        cur.execute('SELECT * FROM WORKING_HOURS WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                        working_hours_table=cur.fetchone()
                        #総労働時間に加算
                        total_work_hour=working_hours_table[4]+work_time_sec

                        #休憩をしていない場合
                        if work_status_table[1]==None and work_status_table[2]==None:
                                #実働時間に加算
                                actual_work_time=working_hours_table[5]+work_time_sec
                                today_actual_work_time=work_time_sec #今日の実働時間
                        #休憩をした場合
                        elif work_status_table[1]!=None and work_status_table[2]!=None:
                                break_time_sec=(work_status_table[2]-work_status_table[1])
                                break_time_sec=break_time_sec.total_seconds()
                                actual_work_time=working_hours_table[5]+(work_time_sec-(break_time_sec))
                                today_actual_work_time=work_time_sec-(break_time_sec) #今日の実働時間
                        #残業した場合
                        if today_actual_work_time>28800:
                                Overtime_hours=today_actual_work_time-28800
                                today_overtime_working_hours=today_actual_work_time-28800
                                total_overtime_hours=Overtime_hours+working_hours_table[8] #残業時間
                                Overtime_working_hours=today_overtime_working_hours+working_hours_table[10] #法定時間外労働時間(所定時間8hの場合)
                        #残業していない場合
                        else:
                                total_overtime_hours=working_hours_table[8]
                                Overtime_working_hours=working_hours_table[10]
                        #所定時間をdatetime型に変換
                        Scheduled_working_hours=dt.datetime.strptime(working_hours_table[7],"%H:%M")
                        Scheduled_working_hours=Scheduled_working_hours.time()
                        hours, minutes,seconds = map(int, str(Scheduled_working_hours).split(":"))
                        Scheduled_working_hours = dt.timedelta(hours=hours, minutes=minutes)
                        Scheduled_working_hours=Scheduled_working_hours.total_seconds()
                        # print(td)
                        
                        #8時間
                        _8hours=dt.datetime.strptime(str(dt.timedelta(hours=8)),"%H:%M:%S")
                        _8hours=_8hours.time()
                        print(_8hours)
                        hours, minutes,seconds = map(int, str(_8hours).split(":"))
                        time_8hours=dt.timedelta(hours=hours, minutes=minutes,seconds=seconds)
                        time_8hours=time_8hours.total_seconds()
                        print(time_8hours)
                        if Scheduled_working_hours<time_8hours: #所定時間8時間未満の場合の法定時間外労働時間と法定時間内労働時間        
                                # typeTime_today_actual_work_time=dt.datetime.strptime(str(today_actual_work_time),"%H:%M:%S")
                                # typeTime_today_actual_work_time=typeTime_today_actual_work_time.time()
                                # print(typeTime_today_actual_work_time)
                                # print(today_actual_work_time)
                                
                                if today_actual_work_time>Scheduled_working_hours and today_actual_work_time<time_8hours:
                                        Working_hours_within_legal_hours=working_hours_table[9]+(28800-today_actual_work_time) #法定時間内労働時間
                                        Overtime_working_hours=working_hours_table[10] #8時間を超えないで労働を終えたため、法定時間外労働時間は0
                                        
                                        
                                elif today_actual_work_time>Scheduled_working_hours and today_actual_work_time>time_8hours:
                                        Overtime_working_hours=working_hours_table[10]+(today_actual_work_time-28800) #法定時間外労働時間
                                        Working_hours_within_legal_hours=working_hours_table[9]+(today_actual_work_time-Scheduled_working_hours-Overtime_working_hours) #法定時間内労働時間
                                        
                        else:
                                Working_hours_within_legal_hours=working_hours_table[9]
                                Overtime_working_hours=working_hours_table[10]

                        # print(DayOfTheWeek)
                        if DayOfTheWeek=="土": #法定外休日
                                cur.execute('UPDATE ATTENDANCE_STATUS SET Number_of_days_to_work_on_nonstatutory_holidays=Number_of_days_to_work_on_nonstatutory_holidays+1 WHERE employee_no="' + str(employee_no) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                                conn.commit()
                                Nonstatutory_holiday_working_hours=working_hours_table[11]+today_actual_work_time
                        else:
                                Nonstatutory_holiday_working_hours=working_hours_table[11]
                        if DayOfTheWeek=="日": #法定休日
                                cur.execute('UPDATE ATTENDANCE_STATUS SET Statutory_holiday_attendance_days=Statutory_holiday_attendance_days+1 WHERE employee_no="' + str(employee_no) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                                conn.commit()
                                Legal_holiday_working_hours=working_hours_table[12]+today_actual_work_time
                                cur.execute('UPDATE WORK_CLASSIFICATION SET Statutory_holiday_attendance=Statutory_holiday_attendance+1 WHERE employee_no="' + str(employee_no) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                                conn.commit()
                        else:
                                Legal_holiday_working_hours=working_hours_table[12]


                        t=dt.datetime(year,month2,day,22, 00, 00)
                        t2=dt.datetime(year,month2,day,5, 00, 00)
                        # start=dt.datetime(yesterday_year,yesterday_month2,yesterday_day,23, 00, 00)
                        # datetime=dt.datetime(year,month2,day,3, 00, 00)
                        yesterday_t=dt.datetime(yesterday_year,yesterday_month2,yesterday_day,22, 00, 00)
                        # work_time=datetime-start
                        Midnight_working_hours=0
                        if datetime > t or datetime < t2: #退勤時間が22h～5hの時
                                if datetime < t2:                                       
                                        if today_actual_work_time>(datetime-yesterday_t).total_seconds():
                                                Midnight_working_hours=datetime-yesterday_t
                                                Midnight_working_hours=Midnight_working_hours.total_seconds()
                                        elif today_actual_work_time<=(datetime-yesterday_t).total_seconds():
                                                Midnight_working_hours=today_actual_work_time
                                if datetime > t:
                                        if today_actual_work_time>(datetime-t).total_seconds():
                                                Midnight_working_hours=datetime-t
                                                Midnight_working_hours=Midnight_working_hours.total_seconds()
                                        elif today_actual_work_time<=(datetime-t).total_seconds():
                                                Midnight_working_hours=today_actual_work_time

                        elif datetime > t2 and t2>work_status_table[0]>yesterday_t: #出勤時間が22時から5時の間、退勤時間は5時以降
                                Midnight_working_hours=t2-work_status_table[0]
                                Midnight_working_hours=Midnight_working_hours.total_seconds()
                        elif work_status_table[0].date()!=datetime.date(): #22時より前に出勤し、5時以降に退勤
                                if work_status_table[1]==None and work_status_table[2]==None: #休憩していない場合
                                        Midnight_working_hours=dt.timedelta(hours=7)
                                        Midnight_working_hours=Midnight_working_hours.total_seconds()
                                elif work_status_table[1]!=None and work_status_table[2]!=None: #休憩した場合
                                        Midnight_working_hours=dt.timedelta(hours=7)-(work_status_table[2]-work_status_table[1])
                                        Midnight_working_hours=Midnight_working_hours.total_seconds()
                        # print("深夜時間="+str(Midnight_working_hours))
                        if Midnight_working_hours==0:
                                Midnight_working_hours=working_hours_table[13]
                        else:
                                Midnight_working_hours=Midnight_working_hours+working_hours_table[13]

                        
                        

                        #新しくUPDATE
                        cur.execute('UPDATE WORKING_HOURS SET Total_working_hours="' + str(total_work_hour) + '",Actual_working_hours="' + str(actual_work_time) + '",Overtime_hours="' + str(total_overtime_hours) + '",Working_hours_outside_legal_hours="' + str(Working_hours_within_legal_hours) + '",Overtime_working_hours="' + str(Overtime_working_hours) + '",Nonstatutory_holiday_working_hours="' + str(Nonstatutory_holiday_working_hours) + '",Legal_holiday_working_hours="' + str(Legal_holiday_working_hours) + '",Midnight_working_hours="' + str(Midnight_working_hours) + '" WHERE employee_no="' + str(employee_no) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                        conn.commit()

                        return render_template('engraving.html',name=name,employee_no=employee_no,error=error[0])

                else:
                        error.append("退勤できません。")
                        return render_template('engraving.html',name=name,employee_no=employee_no,error=error[0])
                cur.close()
                conn.commit()
                conn.close()

#一般社員の出勤状況を確認する
@app.route('/daily_attendance',methods=['POST','GET'])
def daily_attendance():
        today = datetime.today()
        year=today.year
        month=today.month
        month="%02d" % month

        no=[]
        day=[]
        DayOfTheWeek=[] #曜日
        start_time_timeOnly=[]
        finish_time_timeOnly=[]
        break_start_time_timeOnly=[]
        break_finish_time_timeOnly=[]
        interval_time=[]
        approval_status=[]
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        #自分の会員情報を取得
        cur.execute('SELECT name,employee_no,employment_status,department FROM USER_ACCOUNT WHERE loginID= "' + str(session['user_id'][0]) + '"')
        user=cur.fetchone()
        #自分の出勤状況を取得
        cur.execute('SELECT * FROM WORK_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'" AND work_finish_time IS NOT NULL')
        work_status_table=cur.fetchall()
        #自分の出勤日数を取得
        cur.execute('SELECT * FROM ATTENDANCE_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        attendance_status_table=cur.fetchone()
        
        #出勤状況を綺麗に表示するために前処理
        for i in range(len(work_status_table)):
                no.append(work_status_table[i][0])
                day.append(work_status_table[i][2].day)
                DayOfTheWeek.append(work_status_table[i][3])
                start_time_timeOnly.append(work_status_table[i][4].time())
                finish_time_timeOnly.append(work_status_table[i][5].time())
                if work_status_table[i][6]==None:
                        break_start_time_timeOnly.append("0:00")
                else:
                        break_start_time_timeOnly.append(work_status_table[i][6].time())
                if work_status_table[i][7]==None:
                        break_finish_time_timeOnly.append("0:00")
                else:
                        break_finish_time_timeOnly.append(work_status_table[i][7].time())
                interval_time.append(work_status_table[i][8])
                approval_status.append(work_status_table[i][9])
        #勤務間インターバル時間が11時間未満かどうかチェック
        interval_time_check=[]
        if len(work_status_table)!=0:
                cur.execute('SELECT MAX(work_finish_time) FROM WORK_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")= DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, "%Y%m") AND work_finish_time IS NOT NULL')
                lastmonth_work_status=cur.fetchone()
                if lastmonth_work_status[0]!=None:
                        if work_status_table[0][4]-lastmonth_work_status[0]<timedelta(hours=11):
                                interval_time_check.append(1)
                        else:
                                interval_time_check.append(0)
                else:
                        interval_time_check.append(0)

                for i in range(len(work_status_table)-1):
                        if work_status_table[i+1][4]-work_status_table[i][5]<timedelta(hours=11):
                                interval_time_check.append(1)
                        else:
                                interval_time_check.append(0)
                
        work_status_table_length=len(work_status_table)
        #出勤日数をUPDATE
        cur.execute('UPDATE ATTENDANCE_STATUS SET Number_of_days_to_work="' + str(work_status_table_length) + '" WHERE employee_no="' + str(user[1]) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        conn.commit()
        cur.execute('UPDATE WORK_CLASSIFICATION SET Going_to_work="' + str(work_status_table_length) + '" WHERE employee_no="' + str(user[1]) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        conn.commit()

        #表示するために自分の社員番号と日付が一致するものをそれぞれ呼び出す
        cur.execute('SELECT * FROM ATTENDANCE_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        attendance_status_table=cur.fetchone()
        print(attendance_status_table)
        cur.execute('SELECT * FROM HOLIDAY_AND_VACATION_ACQUISITION WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        holiday_and_vacation_acquisition_table=cur.fetchone()
        cur.execute('SELECT * FROM WORKING_HOURS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        working_hours_table=cur.fetchone()
        working_hours_list=[]
        working_hours_list.append(working_hours_table[0])
        working_hours_list.append(working_hours_table[1])
        working_hours_list.append(working_hours_table[2])
        working_hours_list.append(working_hours_table[3])
        working_hours_list.append(int_to_HMS(working_hours_table[4]))
        working_hours_list.append(int_to_HMS(working_hours_table[5]))
        working_hours_list.append(working_hours_table[6])
        working_hours_list.append(working_hours_table[7])
        working_hours_list.append(int_to_HMS(working_hours_table[8]))
        working_hours_list.append(int_to_HMS(working_hours_table[9]))
        working_hours_list.append(int_to_HMS(working_hours_table[10]))
        working_hours_list.append(int_to_HMS(working_hours_table[11]))
        working_hours_list.append(int_to_HMS(working_hours_table[12]))
        working_hours_list.append(int_to_HMS(working_hours_table[13]))
        working_hours_list.append(int_to_HMS(working_hours_table[14]))
        working_hours_list.append(int_to_HMS(working_hours_table[15]))


        cur.execute('SELECT * FROM WORK_CLASSIFICATION WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        work_classification_table=cur.fetchone()

        return render_template('daily_attendance.html',name=user[0],employee_no=user[1],employment_status=user[2],department=user[3],day=day,work_start_time=start_time_timeOnly,work_finish_time=finish_time_timeOnly,break_start_time=break_start_time_timeOnly,break_finish_time=break_finish_time_timeOnly,interval_time=interval_time,work_status_table_length=work_status_table_length,year=year,month=month,approval_status=approval_status,no=no,attendance_status_table=attendance_status_table,work_classification_table=work_classification_table,holiday_and_vacation_acquisition_table=holiday_and_vacation_acquisition_table,working_hours_table=working_hours_list,DayOfTheWeek=DayOfTheWeek,interval_time_check=interval_time_check)

#月を進める(処理はdaily_attendanceとほぼ同じ)
@app.route('/NextMonth',methods=['POST','GET'])
def NextMonth():
        month=request.form["next"]
        year=request.form["year"]
        today = datetime.today()
        if month=="12":
                year=int(year)+1
        month = dt.datetime.strptime(month, '%m')
        nextmonth = month + relativedelta(months=1)
        month=nextmonth.month
        month="%02d" % month
        lastmonth=dt.datetime(int(year),int(month),1)- relativedelta(months=1)
        print(lastmonth)
        lastmonth_month="%02d" % lastmonth.month
        no=[]
        day=[]
        DayOfTheWeek=[]
        start_time_timeOnly=[]
        finish_time_timeOnly=[]
        break_start_time_timeOnly=[]
        break_finish_time_timeOnly=[]
        interval_time=[]
        approval_status=[]
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        cur.execute('SELECT name,employee_no,employment_status,department FROM USER_ACCOUNT WHERE loginID= "' + str(session['user_id'][0]) + '"')
        user=cur.fetchone()
        cur.execute('SELECT * FROM WORK_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'" AND work_finish_time IS NOT NULL')
        work_status_table=cur.fetchall()
        
        cur.execute('SELECT * FROM ATTENDANCE_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        attendance_status_table=cur.fetchone()
        
        for i in range(len(work_status_table)):
                day.append(work_status_table[i][2].day)
                DayOfTheWeek.append(work_status_table[i][3])
                start_time_timeOnly.append(work_status_table[i][4].time())
                finish_time_timeOnly.append(work_status_table[i][5].time())
                if work_status_table[i][6]==None:
                        break_start_time_timeOnly.append("0:00")
                else:
                        break_start_time_timeOnly.append(work_status_table[i][6].time())
                if work_status_table[i][7]==None:
                        break_finish_time_timeOnly.append("0:00")
                else:
                        break_finish_time_timeOnly.append(work_status_table[i][7].time())
                interval_time.append(work_status_table[i][8])
                approval_status.append(work_status_table[i][9])

        interval_time_check=[]
        if len(work_status_table)!=0:
                cur.execute('SELECT MAX(work_finish_time) FROM WORK_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(lastmonth.year)+str(lastmonth_month)+'"  AND work_finish_time IS NOT NULL')
                lastmonth_work_status=cur.fetchone()
                if lastmonth_work_status[0]!=None:
                        if work_status_table[0][4]-lastmonth_work_status[0]<timedelta(hours=11):
                                interval_time_check.append(1)
                        else:
                                print(work_status_table[0][4]-lastmonth_work_status[0])
                                interval_time_check.append(0)
                else:
                        interval_time_check.append(0)

                for i in range(len(work_status_table)-1):
                        if work_status_table[i+1][4]-work_status_table[i][5]<timedelta(hours=11):
                                interval_time_check.append(1)
                        else:
                                interval_time_check.append(0)
        print(interval_time_check)
        work_status_table_length=len(work_status_table)
        if attendance_status_table!=None:
                if attendance_status_table[5]!=len(work_status_table):
                        cur.execute('UPDATE ATTENDANCE_STATUS SET Number_of_days_to_work="' + str(work_status_table_length) + '" WHERE employee_no="' + str(user[1]) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                        conn.commit()
                        cur.execute('UPDATE WORK_CLASSIFICATION SET Going_to_work="' + str(work_status_table_length) + '" WHERE employee_no="' + str(user[1]) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                        conn.commit()

        cur.execute('SELECT * FROM ATTENDANCE_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        attendance_status_table=cur.fetchone()
        print(attendance_status_table)
        cur.execute('SELECT * FROM HOLIDAY_AND_VACATION_ACQUISITION WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        holiday_and_vacation_acquisition_table=cur.fetchone()
        # print(work_status_table)
        cur.execute('SELECT * FROM WORKING_HOURS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        working_hours_table=cur.fetchone()
        if working_hours_table!=None:
                working_hours_list=[]
                working_hours_list.append(working_hours_table[0])
                working_hours_list.append(working_hours_table[1])
                working_hours_list.append(working_hours_table[2])
                working_hours_list.append(working_hours_table[3])
                working_hours_list.append(int_to_HMS(working_hours_table[4]))
                working_hours_list.append(int_to_HMS(working_hours_table[5]))
                working_hours_list.append(working_hours_table[6])
                working_hours_list.append(working_hours_table[7])
                working_hours_list.append(int_to_HMS(working_hours_table[8]))
                working_hours_list.append(int_to_HMS(working_hours_table[9]))
                working_hours_list.append(int_to_HMS(working_hours_table[10]))
                working_hours_list.append(int_to_HMS(working_hours_table[11]))
                working_hours_list.append(int_to_HMS(working_hours_table[12]))
                working_hours_list.append(int_to_HMS(working_hours_table[13]))
                working_hours_list.append(int_to_HMS(working_hours_table[14]))
                working_hours_list.append(int_to_HMS(working_hours_table[15]))
        else:
                working_hours_list=cur.fetchone()
        cur.execute('SELECT * FROM WORK_CLASSIFICATION WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        work_classification_table=cur.fetchone()

        return render_template('daily_attendance.html',name=user[0],employee_no=user[1],employment_status=user[2],department=user[3],day=day,work_start_time=start_time_timeOnly,work_finish_time=finish_time_timeOnly,break_start_time=break_start_time_timeOnly,break_finish_time=break_finish_time_timeOnly,interval_time=interval_time,work_status_table_length=work_status_table_length,year=year,month=month,approval_status=approval_status,no=no,attendance_status_table=attendance_status_table,work_classification_table=work_classification_table,holiday_and_vacation_acquisition_table=holiday_and_vacation_acquisition_table,working_hours_table=working_hours_list,DayOfTheWeek=DayOfTheWeek,interval_time_check=interval_time_check)

#月を戻す(処理はdaily_attendanceとほぼ同じ)
@app.route('/LastMonth',methods=['POST','GET'])
def LastMonth():
        month=request.form["last"]
        year=request.form["year"]
        today = datetime.today()
        if month=="01":
                year=int(year)-1
        month = dt.datetime.strptime(month, '%m')
        nextmonth = month - relativedelta(months=1)
        month=nextmonth.month
        month="%02d" % month
        
        lastmonth=dt.datetime(int(year),int(month),1)- relativedelta(months=1)
        print(lastmonth)
        lastmonth_month="%02d" % lastmonth.month

        no=[]
        day=[]
        DayOfTheWeek=[]
        start_time_timeOnly=[]
        finish_time_timeOnly=[]
        break_start_time_timeOnly=[]
        break_finish_time_timeOnly=[]
        interval_time=[]
        approval_status=[]
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        cur.execute('SELECT name,employee_no,employment_status,department FROM USER_ACCOUNT WHERE loginID= "' + str(session['user_id'][0]) + '"')
        user=cur.fetchone()
        cur.execute('SELECT * FROM WORK_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'" AND work_finish_time IS NOT NULL')
        work_status_table=cur.fetchall()
        print(work_status_table)
        cur.execute('SELECT * FROM ATTENDANCE_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        attendance_status_table=cur.fetchone()
        print(attendance_status_table)

        for i in range(len(work_status_table)):
                day.append(work_status_table[i][2].day)
                DayOfTheWeek.append(work_status_table[i][3])
                start_time_timeOnly.append(work_status_table[i][4].time())
                finish_time_timeOnly.append(work_status_table[i][5].time())
                if work_status_table[i][6]==None:
                        break_start_time_timeOnly.append("0:00")
                else:
                        break_start_time_timeOnly.append(work_status_table[i][6].time())
                if work_status_table[i][7]==None:
                        break_finish_time_timeOnly.append("0:00")
                else:
                        break_finish_time_timeOnly.append(work_status_table[i][7].time())
                interval_time.append(work_status_table[i][8])
                approval_status.append(work_status_table[i][9])

        interval_time_check=[]
        if len(work_status_table)!=0:
                cur.execute('SELECT MAX(work_finish_time) FROM WORK_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(lastmonth.year)+str(lastmonth_month)+'"  AND work_finish_time IS NOT NULL')
                lastmonth_work_status=cur.fetchone()
                if lastmonth_work_status[0]!=None:
                        if work_status_table[0][4]-lastmonth_work_status[0]<timedelta(hours=11):
                                interval_time_check.append(1)
                        else:
                                interval_time_check.append(0)
                else:
                        interval_time_check.append(0)

                for i in range(len(work_status_table)-1):
                        if work_status_table[i+1][4]-work_status_table[i][5]<timedelta(hours=11):
                                interval_time_check.append(1)
                        else:
                                interval_time_check.append(0)

        work_status_table_length=len(work_status_table)
        if attendance_status_table!=None:
                if attendance_status_table[5]!=len(work_status_table):
                        cur.execute('UPDATE ATTENDANCE_STATUS SET Number_of_days_to_work="' + str(work_status_table_length) + '" WHERE employee_no="' + str(user[1]) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                        conn.commit()
                        cur.execute('UPDATE WORK_CLASSIFICATION SET Going_to_work="' + str(work_status_table_length) + '" WHERE employee_no="' + str(user[1]) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                        conn.commit()
        cur.execute('SELECT * FROM ATTENDANCE_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        attendance_status_table=cur.fetchone()
        cur.execute('SELECT * FROM HOLIDAY_AND_VACATION_ACQUISITION WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        holiday_and_vacation_acquisition_table=cur.fetchone()
        cur.execute('SELECT * FROM WORKING_HOURS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        working_hours_table=cur.fetchone()

        if working_hours_table!=None:
                working_hours_list=[]
                working_hours_list.append(working_hours_table[0])
                working_hours_list.append(working_hours_table[1])
                working_hours_list.append(working_hours_table[2])
                working_hours_list.append(working_hours_table[3])
                working_hours_list.append(int_to_HMS(working_hours_table[4]))
                working_hours_list.append(int_to_HMS(working_hours_table[5]))
                working_hours_list.append(working_hours_table[6])
                working_hours_list.append(working_hours_table[7])
                working_hours_list.append(int_to_HMS(working_hours_table[8]))
                working_hours_list.append(int_to_HMS(working_hours_table[9]))
                working_hours_list.append(int_to_HMS(working_hours_table[10]))
                working_hours_list.append(int_to_HMS(working_hours_table[11]))
                working_hours_list.append(int_to_HMS(working_hours_table[12]))
                working_hours_list.append(int_to_HMS(working_hours_table[13]))
                working_hours_list.append(int_to_HMS(working_hours_table[14]))
                working_hours_list.append(int_to_HMS(working_hours_table[15]))
        else:
                working_hours_list=cur.fetchone()
        cur.execute('SELECT * FROM WORK_CLASSIFICATION WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        work_classification_table=cur.fetchone()

        return render_template('daily_attendance.html',name=user[0],employee_no=user[1],employment_status=user[2],department=user[3],day=day,work_start_time=start_time_timeOnly,work_finish_time=finish_time_timeOnly,break_start_time=break_start_time_timeOnly,break_finish_time=break_finish_time_timeOnly,interval_time=interval_time,work_status_table_length=work_status_table_length,year=year,month=month,approval_status=approval_status,no=no,attendance_status_table=attendance_status_table,work_classification_table=work_classification_table,holiday_and_vacation_acquisition_table=holiday_and_vacation_acquisition_table,working_hours_table=working_hours_list,DayOfTheWeek=DayOfTheWeek,interval_time_check=interval_time_check)

#月を進める(処理はadmin_daily_attendanceとほぼ同じ)
@app.route('/admin_NextMonth',methods=['POST','GET'])
def admin_NextMonth():
        select1=request.form["select1"]
        select2=request.form["select2"]
        selected_value1=request.form["selected_value1"]
        selected_value2=request.form["selected_value2"] 
        month=request.form["next"]
        print(month)
        year=request.form["year"]
        today = datetime.today()
        if month=="12":
                year=int(year)+1
        month = dt.datetime.strptime(month, '%m')
        nextmonth = month + relativedelta(months=1)
        month=nextmonth.month
        month="%02d" % month
        error=[]
        no=[]
        day=[]
        employee_no=[]
        name=[]
        start_time_timeOnly=[]
        finish_time_timeOnly=[]
        break_start_time_timeOnly=[]
        break_finish_time_timeOnly=[]
        interval_time=[]
        approval_status=[] 
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        cur.execute('select name,employee_no from ADMIN_USER_ACCOUNT where loginID= "' + str(session['user_id'][0]) + '";')
        username_and_employeeno=cur.fetchone()
        error.append(None)
        cur.execute('select * from WORK_STATUS where application_and_approval= "承認待ち" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        work_status_table=cur.fetchall()
        cur.execute('SELECT employee_no,name From USER_ACCOUNT')
        general_user=cur.fetchall()
        
        for i in range(len(work_status_table)):
                no.append(work_status_table[i][0])
                employee_no.append(work_status_table[i][1])
                day.append(work_status_table[i][2].day)
                start_time_timeOnly.append(work_status_table[i][4].time())
                finish_time_timeOnly.append(work_status_table[i][5].time())
                if work_status_table[i][6]==None:
                        break_start_time_timeOnly.append("0:00")
                else:
                        break_start_time_timeOnly.append(work_status_table[i][6].time())
                if work_status_table[i][7]==None:
                        break_finish_time_timeOnly.append("0:00")
                else:
                        break_finish_time_timeOnly.append(work_status_table[i][7].time())
                interval_time.append(work_status_table[i][8])
                approval_status.append(work_status_table[i][9])
        for i in range(len(employee_no)):
                for j in range(len(general_user)):
                        if employee_no[i]==general_user[j][0]:
                                name.append(general_user[j][1])
        
        work_status_table_length=len(work_status_table)
        return render_template("admin_daily_attendance.html",admin_name=username_and_employeeno[0],admin_employee_no=username_and_employeeno[1],error=error[0],day=day,work_start_time=start_time_timeOnly,work_finish_time=finish_time_timeOnly,break_start_time=break_start_time_timeOnly,break_finish_time=break_finish_time_timeOnly,interval_time=interval_time,work_status_table_length=work_status_table_length,year=year,month=month,approval_status=approval_status,no=no,general_user_name=name,general_user_employee_no=employee_no,select1=select1,select2=select2,selected_value1=selected_value1,selected_value2=selected_value2)

#月を戻す(処理はadmin_daily_attendanceとほぼ同じ)
@app.route('/admin_LastMonth',methods=['POST','GET'])
def admin_LastMonth():
        select1=request.form["select1"]
        select2=request.form["select2"]
        selected_value1=request.form["selected_value1"]
        selected_value2=request.form["selected_value2"] 
        month=request.form["last"]
        year=request.form["year"]
        today = datetime.today()
        if month=="01":
                year=int(year)-1
        month = dt.datetime.strptime(month, '%m')
        nextmonth = month - relativedelta(months=1)
        month=nextmonth.month
        month="%02d" % month
        error=[]
        no=[]
        day=[]
        employee_no=[]
        name=[]
        start_time_timeOnly=[]
        finish_time_timeOnly=[]
        break_start_time_timeOnly=[]
        break_finish_time_timeOnly=[]
        interval_time=[]
        approval_status=[] 
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        cur.execute('select name,employee_no from ADMIN_USER_ACCOUNT where loginID= "' + str(session['user_id'][0]) + '";')
        username_and_employeeno=cur.fetchone()
        error.append(None)
        cur.execute('select * from WORK_STATUS where application_and_approval= "承認待ち" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        work_status_table=cur.fetchall()
        cur.execute('SELECT employee_no,name From USER_ACCOUNT')
        general_user=cur.fetchall()
        
        for i in range(len(work_status_table)):
                no.append(work_status_table[i][0])
                employee_no.append(work_status_table[i][1])
                day.append(work_status_table[i][2].day)
                start_time_timeOnly.append(work_status_table[i][4].time())
                finish_time_timeOnly.append(work_status_table[i][5].time())
                if work_status_table[i][6]==None:
                        break_start_time_timeOnly.append("0:00")
                else:
                        break_start_time_timeOnly.append(work_status_table[i][6].time())
                if work_status_table[i][7]==None:
                        break_finish_time_timeOnly.append("0:00")
                else:
                        break_finish_time_timeOnly.append(work_status_table[i][7].time())
                interval_time.append(work_status_table[i][8])
                approval_status.append(work_status_table[i][9])
        for i in range(len(employee_no)):
                for j in range(len(general_user)):
                        if employee_no[i]==general_user[j][0]:
                                name.append(general_user[j][1])
        
        work_status_table_length=len(work_status_table)
        return render_template("admin_daily_attendance.html",admin_name=username_and_employeeno[0],admin_employee_no=username_and_employeeno[1],error=error[0],day=day,work_start_time=start_time_timeOnly,work_finish_time=finish_time_timeOnly,break_start_time=break_start_time_timeOnly,break_finish_time=break_finish_time_timeOnly,interval_time=interval_time,work_status_table_length=work_status_table_length,year=year,month=month,approval_status=approval_status,no=no,general_user_name=name,general_user_employee_no=employee_no,select1=select1,select2=select2,selected_value1=selected_value1,selected_value2=selected_value2)

#一般社員が編集を行う画面に遷移
@app.route('/daily_attendance_registration',methods=['POST','GET'])
def daily_attendance_registration():
        weekday = ["月","火","水","木","金","土","日"]
        work_status_table_length=request.form["work_status_table_length"]
        name=request.form["name"]
        employee_no=request.form["employee_no"]
        year=request.form["year"]
        month=request.form["month2"]

        #daily_attendance.htmlで表示されている表のうち、どの行を編集すると指定したか
        for i in range(int(work_status_table_length)):
                if(request.form["index2"]=="index2_"+str(i)):
                                day=request.form["day_"+str(i)]
                                print(day)
                                approval_status=request.form["approval_status_"+str(i)]
                                no=request.form["no_"+str(i)]

        
        date=dt.date(int(year), int(month), int(day))
        print(date)
        DayOfTheWeek=weekday[date.weekday()]

        return render_template('daily_attendance_registration.html',name=name,employee_no=employee_no,date=date,DayOfTheWeek=DayOfTheWeek,approval_status=approval_status,no=no)

#daily_attendance.htmlの申請ボタンを押したときの処理
@app.route('/update',methods=['POST','GET'])
def update():
        year=request.form["year"]
        month=request.form["month2"]
        
        lastmonth=dt.datetime(int(year),int(month),1)- relativedelta(months=1)
        print(lastmonth)
        lastmonth_month="%02d" % lastmonth.month

        work_status_table_length=request.form["work_status_table_length"]
        #どの行の申請ボタンが押されたか
        for i in range(int(work_status_table_length)):
                print(request.form["index"])
                if(request.form["index"]=="index_"+str(i)):
                                update_no=request.form["no_"+str(i)]
                                print(update_no)
                                break
        
        no=[]
        day=[]
        DayOfTheWeek=[]
        start_time_timeOnly=[]
        finish_time_timeOnly=[]
        break_start_time_timeOnly=[]
        break_finish_time_timeOnly=[]
        interval_time=[]
        approval_status=[]
        status="承認待ち"
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        #申請・承認状況を承認待ちへ更新
        cur.execute('UPDATE WORK_STATUS set application_and_approval="' + str(status) + '" WHERE No="' + str(update_no) + '"')
        conn.commit()
        #ここから先の処理はdaily_attendanceとほぼ同じ
        cur.execute('SELECT name,employee_no,employment_status,department FROM USER_ACCOUNT WHERE loginID= "' + str(session['user_id'][0]) + '"')
        user=cur.fetchone()
        cur.execute('SELECT * FROM WORK_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'" AND work_finish_time IS NOT NULL')
        work_status_table=cur.fetchall()
        print(work_status_table)
        cur.execute('SELECT * FROM ATTENDANCE_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        attendance_status_table=cur.fetchone()

        for i in range(len(work_status_table)):
                no.append(work_status_table[i][0])
                day.append(work_status_table[i][2].day)
                DayOfTheWeek.append(work_status_table[i][3])
                start_time_timeOnly.append(work_status_table[i][4].time())
                finish_time_timeOnly.append(work_status_table[i][5].time())
                if work_status_table[i][6]==None:
                        break_start_time_timeOnly.append("0:00")
                else:
                        break_start_time_timeOnly.append(work_status_table[i][6].time())
                if work_status_table[i][7]==None:
                        break_finish_time_timeOnly.append("0:00")
                else:
                        break_finish_time_timeOnly.append(work_status_table[i][7].time())
                interval_time.append(work_status_table[i][8])
                approval_status.append(work_status_table[i][9])

        interval_time_check=[]
        if len(work_status_table)!=0:
                cur.execute('SELECT MAX(work_finish_time) FROM WORK_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(lastmonth.year)+str(lastmonth_month)+'"  AND work_finish_time IS NOT NULL')
                lastmonth_work_status=cur.fetchone()
                if lastmonth_work_status[0]!=None:
                        if work_status_table[0][4]-lastmonth_work_status[0]<timedelta(hours=11):
                                interval_time_check.append(1)
                        else:
                                interval_time_check.append(0)
                else:
                        interval_time_check.append(0)

                for i in range(len(work_status_table)-1):
                        if work_status_table[i+1][4]-work_status_table[i][5]<timedelta(hours=11):
                                interval_time_check.append(1)
                        else:
                                interval_time_check.append(0)

        work_status_table_length=len(work_status_table)
        if attendance_status_table!=None:
                if attendance_status_table[5]!=len(work_status_table):
                        cur.execute('UPDATE ATTENDANCE_STATUS SET Number_of_days_to_work="' + str(work_status_table_length) + '" WHERE employee_no="' + str(user[1]) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                        conn.commit()
                        cur.execute('UPDATE WORK_CLASSIFICATION SET Going_to_work="' + str(work_status_table_length) + '" WHERE employee_no="' + str(user[1]) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                        conn.commit()

        cur.execute('SELECT * FROM ATTENDANCE_STATUS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        attendance_status_table=cur.fetchone()
        cur.execute('SELECT * FROM HOLIDAY_AND_VACATION_ACQUISITION WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        holiday_and_vacation_acquisition_table=cur.fetchone()
        cur.execute('SELECT * FROM WORKING_HOURS WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        working_hours_table=cur.fetchone()
        if working_hours_table!=None:
                working_hours_list=[]
                working_hours_list.append(working_hours_table[0])
                working_hours_list.append(working_hours_table[1])
                working_hours_list.append(working_hours_table[2])
                working_hours_list.append(working_hours_table[3])
                working_hours_list.append(int_to_HMS(working_hours_table[4]))
                working_hours_list.append(int_to_HMS(working_hours_table[5]))
                working_hours_list.append(working_hours_table[6])
                working_hours_list.append(working_hours_table[7])
                working_hours_list.append(int_to_HMS(working_hours_table[8]))
                working_hours_list.append(int_to_HMS(working_hours_table[9]))
                working_hours_list.append(int_to_HMS(working_hours_table[10]))
                working_hours_list.append(int_to_HMS(working_hours_table[11]))
                working_hours_list.append(int_to_HMS(working_hours_table[12]))
                working_hours_list.append(int_to_HMS(working_hours_table[13]))
                working_hours_list.append(int_to_HMS(working_hours_table[14]))
                working_hours_list.append(int_to_HMS(working_hours_table[15]))
        else:
                working_hours_list=cur.fetchone()
        cur.execute('SELECT * FROM WORK_CLASSIFICATION WHERE employee_no="' + str(user[1]) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        work_classification_table=cur.fetchone()

        return render_template('daily_attendance.html',name=user[0],employee_no=user[1],employment_status=user[2],department=user[3],day=day,work_start_time=start_time_timeOnly,work_finish_time=finish_time_timeOnly,break_start_time=break_start_time_timeOnly,break_finish_time=break_finish_time_timeOnly,interval_time=interval_time,work_status_table_length=work_status_table_length,year=year,month=month,approval_status=approval_status,no=no,attendance_status_table=attendance_status_table,work_classification_table=work_classification_table,holiday_and_vacation_acquisition_table=holiday_and_vacation_acquisition_table,working_hours_table=working_hours_list,DayOfTheWeek=DayOfTheWeek,interval_time_check=interval_time_check)

#打刻処理を行う画面へ遷移
@app.route('/engraving',methods=['POST','GET'])
def engraving():
        return redirect(url_for('login_go'))
#管理者が承認を行うための処理
@app.route('/approval',methods=['POST','GET'])
def approval():
        year=request.form["year"]
        month=request.form["month2"]
        #admin_daily_attendance.htmlで表示されている表のうち、どの行の承認ボタンが押されたか
        work_status_table_length=request.form["work_status_table_length"]
        for i in range(int(work_status_table_length)):
                if(request.form["index"]=="index_"+str(i)):
                                update_no=request.form["no_"+str(i)]
                                
        
        no=[]
        name=[]
        employee_no=[]
        day=[]
        start_time_timeOnly=[]
        finish_time_timeOnly=[]
        break_start_time_timeOnly=[]
        break_finish_time_timeOnly=[]
        interval_time=[]
        approval_status=[]
        status="承認済み"
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        #申請・承認状況を承認済みへ更新
        cur.execute('UPDATE WORK_STATUS set application_and_approval="' + str(status) + '" WHERE No="' + str(update_no) + '"')
        conn.commit()
        #ここから先の処理はadmin_daily_attendanceとほぼ同じ
        cur.execute('select name,employee_no from ADMIN_USER_ACCOUNT where loginID= "' + str(session['user_id'][0]) + '";')
        username_and_employeeno=cur.fetchone()
        cur.execute('select * from WORK_STATUS where application_and_approval= "承認待ち"')
        work_status_table=cur.fetchall()
        cur.execute('SELECT employee_no,name From USER_ACCOUNT')
        general_user=cur.fetchall()
        for i in range(len(work_status_table)):
                no.append(work_status_table[i][0])
                employee_no.append(work_status_table[i][1])
                day.append(work_status_table[i][2].day)
                start_time_timeOnly.append(work_status_table[i][4].time())
                finish_time_timeOnly.append(work_status_table[i][5].time())
                if work_status_table[i][6]==None:
                        break_start_time_timeOnly.append("0:00")
                else:
                        break_start_time_timeOnly.append(work_status_table[i][6].time())
                if work_status_table[i][7]==None:
                        break_finish_time_timeOnly.append("0:00")
                else:
                        break_finish_time_timeOnly.append(work_status_table[i][7].time())
                interval_time.append(work_status_table[i][8])
                approval_status.append(work_status_table[i][9])
        work_status_table_length=len(work_status_table)
        for i in range(len(employee_no)):
                        for j in range(len(general_user)):
                                if employee_no[i]==general_user[j][0]:
                                        name.append(general_user[j][1])
        return render_template('admin_daily_attendance.html',admin_name=username_and_employeeno[0],admin_employee_no=username_and_employeeno[1],day=day,work_start_time=start_time_timeOnly,work_finish_time=finish_time_timeOnly,break_start_time=break_start_time_timeOnly,break_finish_time=break_finish_time_timeOnly,interval_time=interval_time,work_status_table_length=work_status_table_length,year=year,month=month,approval_status=approval_status,no=no,general_user_name=name,general_user_employee_no=employee_no)
#admin_edit.htmlへ遷移
@app.route('/admin_edit',methods=['POST','GET'])
def admin_edit():
        today = datetime.today()
        year=today.year
        month=today.month
        month="%02d" % month
        return render_template('admin_edit.html',year=year,month=month)
#編集先の検索(管理者側の処理)
@app.route('/edit',methods=['POST','GET'])
def edit():
        error=[]
        employee_no=request.form["search_employee_no"]
        name=request.form["search_name"]
        year=request.form["year"]
        month=request.form["month2"]
        check=request.form.getlist("all")[-1] #チェックボックスが押されているか
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        if check=="off": #押されていない場合、入力欄に入力されたユーザーの出勤状況の詳細を取得する
                cur.execute('select employee_no,name from USER_ACCOUNT')
                user=cur.fetchall()    
                for i in range(len(user)):
                        if str(user[i][0]) == str(employee_no) and str(user[i][1]) == str(name):
                                cur.execute('SELECT * FROM HOLIDAY_AND_VACATION_ACQUISITION WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                                holiday_and_vacation_acquisition_table=cur.fetchone()
                                # print(work_status_table)
                                cur.execute('SELECT * FROM ATTENDANCE_STATUS WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                                attendance_status_table=cur.fetchone()
                                # print(attendance_status_table)
                                cur.execute('SELECT * FROM WORKING_HOURS WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                                working_hours_table=cur.fetchone()
                                cur.execute('SELECT * FROM WORK_CLASSIFICATION WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                                work_classification_table=cur.fetchone()
                                if working_hours_table!=None:
                                        working_hours=[]
                                        working_minutes=[]
                                        working_seconds=[]
                                        for i in range(4,16):
                                                if i==6 or i==7:
                                                        hours,minutes = map(int, str(working_hours_table[i]).split(":"))
                                                        if minutes==0:
                                                                minutes="00"
                                                        seconds="00"
                                                else:
                                                        hours,minutes,seconds=int_to_HMS2(working_hours_table[i])
                                                working_hours.append(hours)
                                                working_minutes.append(minutes)
                                                working_seconds.append(seconds)
                                        
                                else:
                                        working_hours=[]
                                        working_minutes=[]
                                        working_seconds=[]
                                        for i in range(4,16):
                                                # hours,minutes,seconds=int_to_HMS2(working_hours_table[i])
                                                working_hours.append("0")
                                                working_minutes.append("00")
                                                working_seconds.append("00")
                                
                                # print(working_hours_table)
                                return render_template('edit_attendance_status.html',name=name,employee_no=employee_no,year=year,month=month,holiday_and_vacation_acquisition_table=holiday_and_vacation_acquisition_table,work_classification_table=work_classification_table,working_hours=working_hours,working_minutes=working_minutes,working_seconds=working_seconds,attendance_status_table=attendance_status_table)
                
                error.append("入力された社員は存在しませんでした。")
        #押された場合、全従業員の出勤状況の詳細を取得
        elif check=="on":
                cur.execute('SELECT SUM(Number_of_days_to_work),SUM(Number_of_days_to_work_on_nonstatutory_holidays),SUM(Statutory_holiday_attendance_days),SUM(Days_of_absence),SUM(Late_days),SUM(Number_of_early_departures) FROM ATTENDANCE_STATUS WHERE DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                all_attendance_status_table=cur.fetchone()
                #sumで取得した場合、時間は整数で出力されてしまったため、時間の合計はpython側で処理する
                cur.execute('SELECT Total_working_hours,Actual_working_hours,Overtime_hours,Working_hours_outside_legal_hours,Overtime_working_hours,Nonstatutory_holiday_working_hours,Legal_holiday_working_hours,Midnight_working_hours,Late_time,Early_departure_time FROM WORKING_HOURS WHERE DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                all_working_hours_table=cur.fetchall()
                # print(all_working_hours_table)
                Total_working_hours=0
                Actual_working_hours=0
                Overtime_hours=0
                Working_hours_outside_legal_hours=0
                Overtime_working_hours=0
                Nonstatutory_holiday_working_hours=0
                Legal_holiday_working_hours=0
                Midnight_working_hours=0
                Late_time=0
                Early_departure_time=0
                all_working_hours_list=[]
                if all_working_hours_table!=None:
                        for i in range(len(all_working_hours_table)):
                                Total_working_hours=Total_working_hours+all_working_hours_table[i][0]
                                Actual_working_hours=Actual_working_hours+all_working_hours_table[i][1]
                                Overtime_hours=Overtime_hours+all_working_hours_table[i][2]
                                Working_hours_outside_legal_hours=Working_hours_outside_legal_hours+all_working_hours_table[i][3]
                                Overtime_working_hours=Overtime_working_hours+all_working_hours_table[i][4]
                                Nonstatutory_holiday_working_hours=Nonstatutory_holiday_working_hours+all_working_hours_table[i][5]
                                Legal_holiday_working_hours=Legal_holiday_working_hours+all_working_hours_table[i][6]
                                Midnight_working_hours=Midnight_working_hours+all_working_hours_table[i][7]
                                Late_time=Late_time+all_working_hours_table[i][8]
                                Early_departure_time=Early_departure_time+all_working_hours_table[i][9]

                all_working_hours_list.append(int_to_HMS(Total_working_hours))
                all_working_hours_list.append(int_to_HMS(Actual_working_hours))
                all_working_hours_list.append(int_to_HMS(Overtime_hours))
                all_working_hours_list.append(int_to_HMS(Working_hours_outside_legal_hours))
                all_working_hours_list.append(int_to_HMS(Overtime_working_hours))
                all_working_hours_list.append(int_to_HMS(Nonstatutory_holiday_working_hours))
                all_working_hours_list.append(int_to_HMS(Legal_holiday_working_hours))
                all_working_hours_list.append(int_to_HMS(Midnight_working_hours))
                all_working_hours_list.append(int_to_HMS(Late_time))
                all_working_hours_list.append(int_to_HMS(Early_departure_time))

                if all_attendance_status_table[0]==None:
                        all_attendance_status_list=[0,0,0,0,0,0]
                        return render_template('allemployee_workingtime.html',year=year,month=month,working_hours_table=all_working_hours_list,attendance_status_table=all_attendance_status_list)
                return render_template('allemployee_workingtime.html',year=year,month=month,working_hours_table=all_working_hours_list,attendance_status_table=all_attendance_status_table)

                          
        return render_template('admin_edit.html',year=year,month=month,error=error)

#月を進める(allemployee_workingtime.html 処理はedit elif check==on以下とほぼ同じ)
@app.route('/all_NextMonth',methods=['POST','GET'])
def all_NextMonth():
        year=request.form["year"]
        month=request.form["month2"]
        if month=="12":
                year=int(year)+1
        month = dt.datetime.strptime(month, '%m')
        nextmonth = month + relativedelta(months=1)
        month=nextmonth.month
        month="%02d" % month

        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        cur.execute('SELECT SUM(Number_of_days_to_work),SUM(Number_of_days_to_work_on_nonstatutory_holidays),SUM(Statutory_holiday_attendance_days),SUM(Days_of_absence),SUM(Late_days),SUM(Number_of_early_departures) FROM ATTENDANCE_STATUS WHERE DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        all_attendance_status_table=cur.fetchone()
        #print(all_attendance_status_table)
        # cur.execute('SELECT SUM(Total_working_hours),SUM(Actual_working_hours),SUM(Overtime_hours),SUM(Working_hours_outside_legal_hours),SUM(Overtime_working_hours),SUM(Nonstatutory_holiday_working_hours),SUM(Legal_holiday_working_hours),SUM(Midnight_working_hours),SUM(Late_time),SUM(Early_departure_time) FROM WORKING_HOURS WHERE DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        cur.execute('SELECT Total_working_hours,Actual_working_hours,Overtime_hours,Working_hours_outside_legal_hours,Overtime_working_hours,Nonstatutory_holiday_working_hours,Legal_holiday_working_hours,Midnight_working_hours,Late_time,Early_departure_time FROM WORKING_HOURS WHERE DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        all_working_hours_table=cur.fetchall()
        Total_working_hours=0
        Actual_working_hours=0
        Overtime_hours=0
        Working_hours_outside_legal_hours=0
        Overtime_working_hours=0
        Nonstatutory_holiday_working_hours=0
        Legal_holiday_working_hours=0
        Midnight_working_hours=0
        Late_time=0
        Early_departure_time=0
        all_working_hours_list=[]
        if all_working_hours_table!=None:
                for i in range(len(all_working_hours_table)):
                        Total_working_hours=Total_working_hours+all_working_hours_table[i][0]
                        Actual_working_hours=Actual_working_hours+all_working_hours_table[i][1]
                        Overtime_hours=Overtime_hours+all_working_hours_table[i][2]
                        Working_hours_outside_legal_hours=Working_hours_outside_legal_hours+all_working_hours_table[i][3]
                        Overtime_working_hours=Overtime_working_hours+all_working_hours_table[i][4]
                        Nonstatutory_holiday_working_hours=Nonstatutory_holiday_working_hours+all_working_hours_table[i][5]
                        Legal_holiday_working_hours=Legal_holiday_working_hours+all_working_hours_table[i][6]
                        Midnight_working_hours=Midnight_working_hours+all_working_hours_table[i][7]
                        Late_time=Late_time+all_working_hours_table[i][8]
                        Early_departure_time=Early_departure_time+all_working_hours_table[i][9]

        all_working_hours_list.append(int_to_HMS(Total_working_hours))
        all_working_hours_list.append(int_to_HMS(Actual_working_hours))
        all_working_hours_list.append(int_to_HMS(Overtime_hours))
        all_working_hours_list.append(int_to_HMS(Working_hours_outside_legal_hours))
        all_working_hours_list.append(int_to_HMS(Overtime_working_hours))
        all_working_hours_list.append(int_to_HMS(Nonstatutory_holiday_working_hours))
        all_working_hours_list.append(int_to_HMS(Legal_holiday_working_hours))
        all_working_hours_list.append(int_to_HMS(Midnight_working_hours))
        all_working_hours_list.append(int_to_HMS(Late_time))
        all_working_hours_list.append(int_to_HMS(Early_departure_time))

        if all_attendance_status_table[0]==None:
                all_attendance_status_list=[0,0,0,0,0,0]
                return render_template('allemployee_workingtime.html',year=year,month=month,working_hours_table=all_working_hours_list,attendance_status_table=all_attendance_status_list)


        return render_template('allemployee_workingtime.html',year=year,month=month,working_hours_table=all_working_hours_list,attendance_status_table=all_attendance_status_table)

#月を戻す(allemployee_workingtime.html 処理はedit elif check==on以下とほぼ同じ)
@app.route('/all_LastMonth',methods=['POST','GET'])
def all_LastMonth():        
        year=request.form["year"]
        month=request.form["month2"]
        if month=="01":
                year=int(year)-1
        month = dt.datetime.strptime(month, '%m')
        nextmonth = month - relativedelta(months=1)
        month=nextmonth.month
        month="%02d" % month

        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        cur.execute('SELECT SUM(Number_of_days_to_work),SUM(Number_of_days_to_work_on_nonstatutory_holidays),SUM(Statutory_holiday_attendance_days),SUM(Days_of_absence),SUM(Late_days),SUM(Number_of_early_departures) FROM ATTENDANCE_STATUS WHERE DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        all_attendance_status_table=cur.fetchone()
        # print(all_attendance_status_table)
        # cur.execute('SELECT SUM(Total_working_hours),SUM(Actual_working_hours),SUM(Overtime_hours),SUM(Working_hours_outside_legal_hours),SUM(Overtime_working_hours),SUM(Nonstatutory_holiday_working_hours),SUM(Legal_holiday_working_hours),SUM(Midnight_working_hours),SUM(Late_time),SUM(Early_departure_time) FROM WORKING_HOURS WHERE DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        cur.execute('SELECT Total_working_hours,Actual_working_hours,Overtime_hours,Working_hours_outside_legal_hours,Overtime_working_hours,Nonstatutory_holiday_working_hours,Legal_holiday_working_hours,Midnight_working_hours,Late_time,Early_departure_time FROM WORKING_HOURS WHERE DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        all_working_hours_table=cur.fetchall()
        #print(all_working_hours_table)
        Total_working_hours=0
        Actual_working_hours=0
        Overtime_hours=0
        Working_hours_outside_legal_hours=0
        Overtime_working_hours=0
        Nonstatutory_holiday_working_hours=0
        Legal_holiday_working_hours=0
        Midnight_working_hours=0
        Late_time=0
        Early_departure_time=0
        all_working_hours_list=[]
        if all_working_hours_table!=None:
                for i in range(len(all_working_hours_table)):
                        Total_working_hours=Total_working_hours+all_working_hours_table[i][0]
                        Actual_working_hours=Actual_working_hours+all_working_hours_table[i][1]
                        Overtime_hours=Overtime_hours+all_working_hours_table[i][2]
                        Working_hours_outside_legal_hours=Working_hours_outside_legal_hours+all_working_hours_table[i][3]
                        Overtime_working_hours=Overtime_working_hours+all_working_hours_table[i][4]
                        Nonstatutory_holiday_working_hours=Nonstatutory_holiday_working_hours+all_working_hours_table[i][5]
                        Legal_holiday_working_hours=Legal_holiday_working_hours+all_working_hours_table[i][6]
                        Midnight_working_hours=Midnight_working_hours+all_working_hours_table[i][7]
                        Late_time=Late_time+all_working_hours_table[i][8]
                        Early_departure_time=Early_departure_time+all_working_hours_table[i][9]

        all_working_hours_list.append(int_to_HMS(Total_working_hours))
        all_working_hours_list.append(int_to_HMS(Actual_working_hours))
        all_working_hours_list.append(int_to_HMS(Overtime_hours))
        all_working_hours_list.append(int_to_HMS(Working_hours_outside_legal_hours))
        all_working_hours_list.append(int_to_HMS(Overtime_working_hours))
        all_working_hours_list.append(int_to_HMS(Nonstatutory_holiday_working_hours))
        all_working_hours_list.append(int_to_HMS(Legal_holiday_working_hours))
        all_working_hours_list.append(int_to_HMS(Midnight_working_hours))
        all_working_hours_list.append(int_to_HMS(Late_time))
        all_working_hours_list.append(int_to_HMS(Early_departure_time))


        if all_attendance_status_table[0]==None:
                all_attendance_status_list=[0,0,0,0,0,0]
                return render_template('allemployee_workingtime.html',year=year,month=month,working_hours_table=all_working_hours_list,attendance_status_table=all_attendance_status_list)

        return render_template('allemployee_workingtime.html',year=year,month=month,working_hours_table=all_working_hours_list,attendance_status_table=all_attendance_status_table)

#月を進める(edit_attendance_status.html 処理はedit if check==off以下とほぼ同じ)
@app.route('/admin_edit_NextMonth',methods=['POST','GET'])
def admin_edit_NextMonth():
        error=[]
        employee_no=request.form["employee_no"]
        name=request.form["name"]
        year=request.form["year"]
        month=request.form["month2"]

        if month=="12":
                year=int(year)+1
        month = dt.datetime.strptime(month, '%m')
        nextmonth = month + relativedelta(months=1)
        month=nextmonth.month
        month="%02d" % month

        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)

        cur.execute('SELECT * FROM HOLIDAY_AND_VACATION_ACQUISITION WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        holiday_and_vacation_acquisition_table=cur.fetchone()
        # print(work_status_table)
        cur.execute('SELECT * FROM ATTENDANCE_STATUS WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        attendance_status_table=cur.fetchone()
        # print(attendance_status_table)
        cur.execute('SELECT * FROM WORKING_HOURS WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        working_hours_table=cur.fetchone()
        
        cur.execute('SELECT * FROM WORK_CLASSIFICATION WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        work_classification_table=cur.fetchone()
        # print(working_hours_table)
        if working_hours_table!=None:
                working_hours=[]
                working_minutes=[]
                working_seconds=[]
                for i in range(4,16):
                        if i==6 or i==7:
                                hours,minutes = map(int, str(working_hours_table[i]).split(":"))
                                if minutes==0:
                                        minutes="00"
                                seconds="00"
                        else:
                                hours,minutes,seconds=int_to_HMS2(working_hours_table[i])
                        working_hours.append(hours)
                        working_minutes.append(minutes)
                        working_seconds.append(seconds)
                
        else:
                working_hours=[]
                working_minutes=[]
                working_seconds=[]
                for i in range(4,16):
                        # hours,minutes,seconds=int_to_HMS2(working_hours_table[i])
                        working_hours.append("0")
                        working_minutes.append("00")
                        working_seconds.append("00")
        
                                
        return render_template('edit_attendance_status.html',name=name,employee_no=employee_no,year=year,month=month,holiday_and_vacation_acquisition_table=holiday_and_vacation_acquisition_table,work_classification_table=work_classification_table,working_hours=working_hours,working_minutes=working_minutes,working_seconds=working_seconds,attendance_status_table=attendance_status_table)
                

#月を戻す(edit_attendance_status.html 処理はedit if check==off以下とほぼ同じ)
@app.route('/admin_edit_LastMonth',methods=['POST','GET'])
def admin_edit_LastMonth():
        error=[]
        employee_no=request.form["employee_no"]
        name=request.form["name"]
        year=request.form["year"]
        month=request.form["month2"]

        if month=="01":
                year=int(year)-1
        month = dt.datetime.strptime(month, '%m')
        nextmonth = month - relativedelta(months=1)
        month=nextmonth.month
        month="%02d" % month

        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)

        cur.execute('SELECT * FROM HOLIDAY_AND_VACATION_ACQUISITION WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        holiday_and_vacation_acquisition_table=cur.fetchone()
        # print(work_status_table)
        cur.execute('SELECT * FROM ATTENDANCE_STATUS WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        attendance_status_table=cur.fetchone()
        # print(attendance_status_table)
        cur.execute('SELECT * FROM WORKING_HOURS WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        working_hours_table=cur.fetchone()
        
        cur.execute('SELECT * FROM WORK_CLASSIFICATION WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        work_classification_table=cur.fetchone()
        # print(working_hours_table)
        if working_hours_table!=None:
                working_hours=[]
                working_minutes=[]
                working_seconds=[]
                for i in range(4,16):
                        if i==6 or i==7:
                                hours, minutes= map(int, str(working_hours_table[i]).split(":"))
                                if minutes==0:
                                        minutes="00"
                                seconds="00"
                        else:
                                hours,minutes,seconds=int_to_HMS2(working_hours_table[i])
                        working_hours.append(hours)
                        working_minutes.append(minutes)
                        working_seconds.append(seconds)
                
        else:
                working_hours=[]
                working_minutes=[]
                working_seconds=[]
                for i in range(4,16):
                        # hours,minutes,seconds=int_to_HMS2(working_hours_table[i])
                        working_hours.append("0")
                        working_minutes.append("00")
                        working_seconds.append("00")
        
                                # print(working_hours_table)
        return render_template('edit_attendance_status.html',name=name,employee_no=employee_no,year=year,month=month,holiday_and_vacation_acquisition_table=holiday_and_vacation_acquisition_table,work_classification_table=work_classification_table,working_hours=working_hours,working_minutes=working_minutes,working_seconds=working_seconds,attendance_status_table=attendance_status_table)
                

#ユーザー個々の出勤状況の詳細を変更(管理者側)
@app.route('/admin_modify',methods=['POST','GET'])
def admin_modify():
        holiday_and_vacation_acquisition_table=request.form.getlist("holiday_and_vacation_acquisition_table")
        attendance_status_table=request.form.getlist("attendance_status_table")
        working_hours=request.form.getlist("working_hours_table1")
        working_minutes=request.form.getlist("working_hours_table2")
        working_seconds=request.form.getlist("working_hours_table3")

        working_hours_table=[]
        for i in range(len(working_hours)):

                if i==2 or i==3:
                        time=dt.timedelta(hours=int(working_hours[i]), minutes=int(working_minutes[i]))
                        time=time.total_seconds()
                        time=int_to_HM(time)
                        working_hours_table.append(time)
                else:
                        time=dt.timedelta(hours=int(working_hours[i]), minutes=int(working_minutes[i]),seconds=int(working_seconds[i]))
                        working_hours_table.append(time.total_seconds())
        work_classification_table=request.form.getlist("work_classification_table")
        name=request.form["name"]
        employee_no=request.form["employee_no"]
        year=request.form["year"]
        month=request.form["month2"]
        print(holiday_and_vacation_acquisition_table)
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)

        #変更をDBにアップデート
        cur.execute('UPDATE WORKING_HOURS SET Total_working_hours="' + str(working_hours_table[0]) + '",Actual_working_hours="' + str(working_hours_table[1]) + '",Predetermined_time="' + str(working_hours_table[2]) + '",Scheduled_working_hours="' + str(working_hours_table[3]) + '",Overtime_hours="' + str(working_hours_table[4]) + '",Working_hours_outside_legal_hours="' + str(working_hours_table[5]) + '",Overtime_working_hours="' + str(working_hours_table[6]) + '",Nonstatutory_holiday_working_hours="' + str(working_hours_table[7]) + '",Legal_holiday_working_hours="' + str(working_hours_table[8]) + '",Midnight_working_hours="' + str(working_hours_table[9]) + '",Late_time="' + str(working_hours_table[10]) + '",Early_departure_time="' + str(working_hours_table[11]) + '" WHERE employee_no="' + str(employee_no) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        conn.commit()
        cur.execute('UPDATE ATTENDANCE_STATUS SET Number_of_working_days="' + str(attendance_status_table[0]) + '",Number_of_days_to_work="' + str(attendance_status_table[1]) + '",Number_of_days_to_work_on_nonstatutory_holidays="' + str(attendance_status_table[2]) + '",Statutory_holiday_attendance_days="' + str(attendance_status_table[3]) + '",Days_of_absence="' + str(attendance_status_table[4]) + '",Late_days="' + str(attendance_status_table[5]) + '",Number_of_early_departures="' + str(attendance_status_table[6]) + '" WHERE employee_no="' + str(employee_no) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        conn.commit()
        cur.execute('UPDATE HOLIDAY_AND_VACATION_ACQUISITION SET Number_of_public_holidays="' + str(holiday_and_vacation_acquisition_table[0]) + '",Paid_leave_days="' + str(holiday_and_vacation_acquisition_table[1]) + '",Remaining_paid_leave_to_date="' + str(holiday_and_vacation_acquisition_table[2]) + '",Transfer_holidays="' + str(holiday_and_vacation_acquisition_table[3]) + '",Transfer_holiday_days_until_today="' + str(holiday_and_vacation_acquisition_table[4]) + '",Number_of_substitute_holidays="' + str(holiday_and_vacation_acquisition_table[5]) + '",The_number_of_days_remaining_until_today="' + str(holiday_and_vacation_acquisition_table[6]) + '",Nonstatutory_holiday_working_hours="' + str(holiday_and_vacation_acquisition_table[7]) + '",Number_of_days_off="' + str(holiday_and_vacation_acquisition_table[8]) + '" WHERE employee_no="' + str(employee_no) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        conn.commit()
        cur.execute('UPDATE WORK_CLASSIFICATION SET Going_to_work="' + str(work_classification_table[0]) + '",Dispatch="' + str(work_classification_table[1]) + '",Paid_vacation="' + str(work_classification_table[2]) + '",Take_the_morning_off="' + str(work_classification_table[3]) + '",Take_the_afternoon_off="' + str(work_classification_table[4]) + '",Statutory_holiday_attendance="' + str(work_classification_table[5]) + '",Gyeonghui_vacation="' + str(work_classification_table[6]) + '",NonRecoverable_late="' + str(work_classification_table[7]) + '",NonRecoverable_leave_early="' + str(work_classification_table[8]) + '",Saturday_work="' + str(work_classification_table[9]) + '",Short_working_hours="' + str(work_classification_table[10]) + '" WHERE employee_no="' + str(employee_no) + '"AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        conn.commit()

        #変更後のデータを取得
        cur.execute('SELECT * FROM HOLIDAY_AND_VACATION_ACQUISITION WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        holiday_and_vacation_acquisition_table=cur.fetchone()
        # print(work_status_table)
        cur.execute('SELECT * FROM ATTENDANCE_STATUS WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        attendance_status_table=cur.fetchone()
        # print(attendance_status_table)
        cur.execute('SELECT * FROM WORKING_HOURS WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        working_hours_table=cur.fetchone()
        cur.execute('SELECT * FROM WORK_CLASSIFICATION WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        work_classification_table=cur.fetchone()
        # print(working_hours_table)

        return render_template('edit_attendance_status.html',name=name,employee_no=employee_no,year=year,month=month,holiday_and_vacation_acquisition_table=holiday_and_vacation_acquisition_table,work_classification_table=work_classification_table,working_hours=working_hours,working_minutes=working_minutes,working_seconds=working_seconds,attendance_status_table=attendance_status_table)

#daily_attendance_registration.htmlで変更された内容を更新(一般ユーザー側)
@app.route('/modify',methods=['POST','GET'])
def modify():
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        no=request.form["no"]
        name=request.form["name"]
        employee_no=request.form["employee_no"]
        date=request.form["date"]
        date=dt.datetime.strptime(date, '%Y-%m-%d')
        DayOfTheWeek=request.form["DayOfTheWeek"]
        work_classification=request.form["work_classification"]
        work_start_hour=request.form["work_start_hour"]
        work_start_minute=request.form["work_start_minute"]
        work_finish_hour=request.form["work_finish_hour"]
        work_finish_minute=request.form["work_finish_minute"]
        break_start_hour=request.form["break_start_hour"]
        break_start_minute=request.form["break_start_minute"]
        break_finish_hour=request.form["break_finish_hour"]
        break_finish_minute=request.form["break_finish_minute"]
        approval_status=request.form["approval_status"]

        yesterday_date=date-dt.timedelta(days = 1)
        yesterday_year=yesterday_date.year
        yesterday_month2=yesterday_date.month
        yesterday_month="%02d" % yesterday_month2
        yesterday_day=yesterday_date.day

        work_start_time=dt.datetime(date.year,date.month,date.day,int(work_start_hour), int(work_start_minute), 00)
        work_finish_time=dt.datetime(date.year,date.month,date.day,int(work_finish_hour), int(work_finish_minute), 00)
        if break_start_hour!="" or break_start_minute!="" or break_finish_hour!="" or break_finish_minute!="":
                break_start_time=dt.datetime(date.year,date.month,date.day,int(break_start_hour), int(break_start_minute), 00)
                break_finish_time=dt.datetime(date.year,date.month,date.day,int(break_finish_hour), int(break_finish_minute,00), 00)
        
        else:
                break_start_time=0
                break_finish_time=0
        cur.execute('SELECT work_start_time,work_finish_time,break_start_time,break_finish_time from WORK_STATUS WHERE No="' + str(no) + '" AND employee_no="' + str(employee_no) + '"')
        work_status_table=cur.fetchone()

        cur.execute('SELECT * FROM WORKING_HOURS WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(date.year)+str(date.month)+'"')
        working_hours_table=cur.fetchone()

        #更新前データの計算
        work_time=work_status_table[1]-work_status_table[0] #労働時間old
        work_time_sec=work_time.total_seconds()
        
        if work_status_table[2]==None and work_status_table[3]==None:
                actual_work_time=work_time_sec #old
        elif work_status_table[2]!=None and work_status_table[3]!=None:
                break_time=work_status_table[3]-work_status_table[2]
                break_time_sec=break_time.total_seconds()
                actual_work_time=work_time_sec-break_time_sec #old
        
                  
        if actual_work_time>28800:
                overtime_hours=actual_work_time_sec-28800 #old
                overtime_working_hours=actual_work_time-28800 #old
                
        else:
                overtime_hours=0 #old
                overtime_working_hours=0 #old

        Scheduled_working_hours=dt.datetime.strptime(working_hours_table[7],"%H:%M")
        Scheduled_working_hours=Scheduled_working_hours.time()
        hours, minutes,seconds = map(int, str(Scheduled_working_hours).split(":"))
        Scheduled_working_hours = dt.timedelta(hours=hours, minutes=minutes)
        Scheduled_working_hours=Scheduled_working_hours.total_seconds()
        # print(td)
        
        #8時間
        _8hours=dt.datetime.strptime(str(dt.timedelta(hours=8)),"%H:%M:%S")
        _8hours=_8hours.time()
        hours, minutes,seconds = map(int, str(_8hours).split(":"))
        time_8hours=dt.timedelta(hours=hours, minutes=minutes,seconds=seconds)
        time_8hours=time_8hours.total_seconds()
        

        if Scheduled_working_hours<time_8hours: #所定時間8時間未満の場合の法定時間外労働時間と法定時間内労働時間
                # typeTime_actual_work_time=dt.datetime.strptime(str(actual_work_time),"%H:%M:%S")
                # typeTime_actual_work_time=typeTime_actual_work_time.time()
               
                if actual_work_time>Scheduled_working_hours and actual_work_time<time_8hours:
                        working_hours_within_legal_hours=28800-actual_work_time #old法定時間内労働時間
                        overtime_working_hours=0 #8時間を超えないで労働を終えたため、法定時間外労働時間は0

                elif actual_work_time>Scheduled_working_hours and actual_work_time>time_8hours:
                        overtime_working_hours=actual_work_time-28800 #法定時間外労働時間
                        working_hours_within_legal_hours=actual_work_time-Scheduled_working_hours-overtime_working_hours #old法定時間内労働時間

        else:
                working_hours_within_legal_hours=0
                overtime_working_hours=0

        print(DayOfTheWeek)
        if DayOfTheWeek=="土": #法定外休日
                Nonstatutory_holiday_working_hours=actual_work_time
        else:
                Nonstatutory_holiday_working_hours=0
        if DayOfTheWeek=="日": #法定休日
                Legal_holiday_working_hours=actual_work_time
        else:
                Legal_holiday_working_hours=0

        t=dt.datetime(date.year,date.month,date.day,22, 00, 00)
        t2=dt.datetime(date.year,date.month,date.day,5, 00, 00)
        yesterday_t=dt.datetime(yesterday_year,yesterday_month2,yesterday_day,22, 00, 00)
        Midnight_working_hours=0

        if work_status_table[1] > t or work_status_table[1]< t2: #退勤時間が22h～5hの時
                if work_status_table[1] < t2:                                       
                        if actual_work_time>(work_status_table[1]-yesterday_t).total_seconds():
                                Midnight_working_hours=work_status_table[1]-yesterday_t
                                Midnight_working_hours=Midnight_working_hours.total_seconds()
                        elif actual_work_time<=(work_status_table[1]-yesterday_t).total_seconds():
                                Midnight_working_hours=actual_work_time
                if work_status_table[1] > t:
                        if actual_work_time>(work_status_table[1]-t).total_seconds():
                                Midnight_working_hours=work_status_table[1]-t
                                Midnight_working_hours=Midnight_working_hours.total_seconds()
                        elif actual_work_time<=(work_status_table[1]-t).total_seconds():
                                Midnight_working_hours=actual_work_time

        elif work_status_table[1] > t2 and t2>work_status_table[0]>yesterday_t:
                Midnight_working_hours=t2-work_start_time
                Midnight_working_hours=Midnight_working_hours.total_seconds()

        elif work_status_table[0].date()!=work_status_table[1].date():
                if work_status_table[2]==None and work_status_table[3]==None:
                        Midnight_working_hours=dt.timedelta(hours=7)
                        Midnight_working_hours=Midnight_working_hours.total_seconds()

                elif work_status_table[2]!=None and work_status_table[3]!=None:
                        Midnight_working_hours=dt.timedelta(hours=7)-(work_status_table[3]-work_status_table[2])
                        Midnight_working_hours=Midnight_working_hours.total_seconds()


        


        #更新後データの計算
        cur.execute('SELECT MAX(work_finish_time) from WORK_STATUS WHERE No<"' + str(no) + '" AND employee_no="' + str(employee_no) + '"')
        befor_work_finish_time=cur.fetchone()
        cur.execute('SELECT No,MIN(work_start_time) from WORK_STATUS WHERE No>"' + str(no) + '" AND employee_no="' + str(employee_no) + '"')
        next_work_start_time=cur.fetchone()
        if befor_work_finish_time[0]!=None:
                interval_time=work_start_time-befor_work_finish_time[0]
        else:
                interval_time="0:00"

        if next_work_start_time[1]!=None:
                next_interval_time=next_work_start_time[1]-work_finish_time
        else:
                next_work_start_time=None

        new_work_time=work_finish_time-work_start_time
        new_work_time_sec=new_work_time.total_seconds()
        new_total_work_time=new_work_time_sec+working_hours_table[4]-work_time_sec
        
        if break_start_time==0 and break_finish_time==0:
                new_actual_work_time=new_work_time_sec
                new_total_actual_work_time=working_hours_table[5]+new_actual_work_time-actual_work_time
        elif break_start_time!=0 and break_finish_time!=0:
                new_break_time=break_finish_time-break_start_time
                new_break_time_sec=new_break_time.total_seconds()
                new_actual_work_time=new_work_time_sec-new_break_time_sec
                new_total_actual_work_time=working_hours_table[5]+new_actual_work_time-actual_work_time

        if new_actual_work_time>28800:
                new_overtime_hours=new_actual_work_time-28800 #new
                new_overtime_hours=working_hours_table[8]+new_overtime_hours-over_time_hours
                new_overtime_working_hours=new_actual_work_time-28800 #new
                new_overtime_working_hours=working_hours_table[10]+new_overtime_working_hours-overtime_working_hours
                
        else:
                new_overtime_hours=working_hours_table[8] #new
                new_overtime_working_hours=working_hours_table[10] #new


        if Scheduled_working_hours<time_8hours: #所定時間8時間未満の場合の法定時間外労働時間と法定時間内労働時間
                # typeTime_new_actual_work_time=dt.datetime.strptime(str(new_actual_work_time),"%H:%M:%S")
                # typeTime_new_actual_work_time=typeTime_new_actual_work_time.time()
               
                if new_actual_work_time>Scheduled_working_hours and new_actual_work_time<time_8hours:
                        new_working_hours_within_legal_hours=28800-new_actual_work_time #new法定時間内労働時間
                        new_working_hours_within_legal_hours=working_hours_table[9]+new_working_hours_within_legal_hours-working_hours_within_legal_hours
                        new_overtime_working_hours=working_hours_table[10] #8時間を超えないで労働を終えたため、法定時間外労働時間は0

                elif new_today_actual_work_time>Scheduled_working_hours and new_today_actual_work_time>time_8hours:
                        new_overtime_working_hours=new_actual_work_time-28800 #法定時間外労働時間
                        new_overtime_working_hours=working_hours_table[10]+new_overtime_working_hours-overtime_working_hours
                        new_working_hours_within_legal_hours=new_actual_work_time-Scheduled_working_hours-new_overtime_working_hours #new法定時間内労働時間
                        new_working_hours_within_legal_hours=working_hours_table[9]+new_working_hours_within_legal_hours-working_hours_within_legal_hours

        else:
                new_working_hours_within_legal_hours=working_hours_table[9]
                new_overtime_working_hours=[10]

        # print(DayOfTheWeek)
        if DayOfTheWeek=="土": #法定外休日
                new_Nonstatutory_holiday_working_hours=new_actual_work_time
                new_Nonstatutory_holiday_working_hours=working_hours_table[11]+new_Nonstatutory_holiday_working_hours-Nonstatutory_holiday_working_hours
        else:
                new_Nonstatutory_holiday_working_hours=working_hours_table[11]
        if DayOfTheWeek=="日": #法定休日
                new_Legal_holiday_working_hours=new_actual_work_time
                new_Legal_holiday_working_hours=working_hours_table[12]+new_Legal_holiday_working_hours-Legal_holiday_working_hours
        else:
                new_Legal_holiday_working_hours=working_hours_table[12]

        # t=dt.datetime(date.year,date.month,date.day,22, 00, 00)
        # t2=dt.datetime(date.year,month2,day,5, 00, 00)
        # yesterday_t=dt.datetime(yesterday_year,yesterday_month2,yesterday_day,22, 00, 00)
        new_Midnight_working_hours=0

        if work_finish_time > t or work_finish_time< t2: #退勤時間が22h～5hの時
                if work_finish_time < t2:                                       
                        if new_actual_work_time>(work_finish_time-yesterday_t).total_seconds():
                                new_Midnight_working_hours=work_finish_time-yesterday_t
                                new_Midnight_working_hours=new_Midnight_working_hours.total_seconds()
                        elif new_actual_work_time<=(work_finish_time-yesterday_t).total_seconds():
                                new_Midnight_working_hours=new_actual_work_time
                if work_finish_time > t:
                        if new_actual_work_time>(work_finish_time-t).total_seconds():
                                new_Midnight_working_hours=work_finish_time-t
                                new_Midnight_working_hours=new_Midnight_working_hours.total_seconds()

                        elif new_actual_work_time<=(work_finish_time-t).total_seconds():
                                new_Midnight_working_hours=new_actual_work_time


        elif work_finish_time > t2 and t2>work_start_time>yesterday_t:
                new_Midnight_working_hours=t2-work_start_time
                new_Midnight_working_hours=new_Midnight_working_hours.total_seconds()

        elif work_start_time.date()!=work_finish_time.date():
                if break_start_time==None and break_finish_time==None:
                        new_Midnight_working_hours=dt.timedelta(hours=7)
                        new_Midnight_working_hours=new_Midnight_working_hours.total_seconds()

                elif break_start_time!=None and break_finish_time!=None:
                        new_Midnight_working_hours=dt.timedelta(hours=7)-(break_finish_time-break_start_time)
                        new_Midnight_working_hours=new_Midnight_working_hours.total_seconds()


        # print(new_Midnight_working_hours)
        if new_Midnight_working_hours==0:
                new_Midnight_working_hours=working_hours_table[13]
        elif Midnight_working_hours==0 and new_Midnight_working_hours!=0:
                new_Midnight_working_hours=working_hours_table[13]+new_Midnight_working_hours
        else:
                new_Midnight_working_hours=working_hours_table[13]+new_Midnight_working_hours-Midnight_working_hours
     
        # print(work_start_time)
        cur.execute('UPDATE WORK_STATUS SET work_start_time="' + str(work_start_time) + '",work_finish_time="' + str(work_finish_time) + '",break_start_time="' + str(break_start_time) + '",break_finish_time="' + str(break_finish_time) + '",application_and_approval="' + str(approval_status) + '",interval_time="' + str(interval_time) + '" WHERE No="' + str(no) + '"')
        conn.commit()

        if next_work_start_time!=None:
                cur.execute('UPDATE WORK_STATUS SET interval_time="' + str(next_interval_time) + '" WHERE No="' + str(next_work_start_time[0]) + '"')
                conn.commit()
        
        cur.execute('UPDATE WORKING_HOURS SET Total_working_hours="' + str(new_total_work_time) +'", Actual_working_hours="' + str(new_total_actual_work_time) +'",Overtime_hours="' + str(new_overtime_hours) + '",Working_hours_outside_legal_hours="' + str(new_working_hours_within_legal_hours) + '",Overtime_working_hours="' + str(new_overtime_working_hours) + '",Nonstatutory_holiday_working_hours="' + str(new_Nonstatutory_holiday_working_hours) + '",Legal_holiday_working_hours="' + str(new_Legal_holiday_working_hours) + '",Midnight_working_hours="' + str(new_Midnight_working_hours) + '" WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(date.year)+str(date.month)+'"')
        conn.commit()

        return redirect(url_for('daily_attendance'))


    
#csv出力(一般ユーザー側)
@app.route('/write_csv',methods=['POST','GET'])
def write_csv():
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        name=request.form["name"]
        employee_no=request.form["employee_no"]
        year=request.form["year"]
        month=request.form["month2"]
        date=dt.datetime(int(year),int(month),1)
        #自分の出勤状況を取得
        cur.execute('SELECT '"date"',day_of_the_week,work_start_time,work_finish_time,break_start_time,break_finish_time,interval_time,application_and_approval FROM WORK_STATUS WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        work_status_table=cur.fetchall()

        df = pd.DataFrame(work_status_table,
        columns=['日付', '曜日', '出勤時刻','退勤時刻','休憩開始時刻','休憩終了時刻','勤務間インターバル','申請状況'])
        df.to_csv("./勤怠状況csv/"+str(employee_no)+"_"+str(name)+"_"+str(year)+"年度"+str(month)+"月.csv",encoding='utf_8_sig')

        
        # return redirect(url_for('daily_attendance'))

        return send_file("./勤怠状況csv/"+str(employee_no)+"_"+str(name)+"_"+str(year)+"年度"+str(month)+"月.csv",mimetype="text/csv",attachment_filename=str(employee_no)+"_"+str(year)+"-"+str(month)+".csv",as_attachment=True)
#csv出力(管理者側)
@app.route('/writeAll_csv',methods=['POST','GET'])
def writeAll_csv():
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        # name=request.form["name"]
        # employee_no=request.form["employee_no"]
        year=request.form["year"]
        month=request.form["month2"]
        date=dt.datetime(int(year),int(month),1)
        #ユーザー個々の出勤状況を取得
        cur.execute('SELECT USER_ACCOUNT.name, WORK_STATUS.employee_no,date,day_of_the_week,work_start_time,work_finish_time,break_start_time,break_finish_time,interval_time,application_and_approval FROM WORK_STATUS INNER JOIN USER_ACCOUNT ON WORK_STATUS.employee_no=USER_ACCOUNT.employee_no WHERE DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        work_status_table=cur.fetchall()
        

        df = pd.DataFrame(work_status_table,
        columns=['名前','社員番号','日付', '曜日', '出勤時刻','退勤時刻','休憩開始時刻','休憩終了時刻','勤務間インターバル','申請状況'])
        df.to_csv("./勤怠状況csv/"+"all_employee"+"_"+str(year)+"年度"+str(month)+"月.csv",encoding='utf_8_sig')

        
        # return redirect(url_for('daily_attendance'))

        return send_file("./勤怠状況csv/"+"all_employee"+"_"+str(year)+"年度"+str(month)+"月.csv",mimetype="text/csv",attachment_filename="all_employee_"+str(year)+"-"+str(month)+".csv",as_attachment=True)

#一括申請ボタンが押されたときの処理
@app.route('/all_application',methods=['POST','GET'])
def all_application():
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        employee_no=request.form["employee_no"]
        year=request.form["year"]
        month=request.form["month2"]
        date=dt.datetime(int(year),int(month),1)
        application_and_approval="承認待ち"
        cur.execute('SELECT * FROM WORK_STATUS WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'" AND application_and_approval="未申請"')
        work_status_table=cur.fetchall()
        if work_status_table==None:
               return redirect(url_for('daily_attendance'))
        elif work_status_table!=None: 
                cur.execute('UPDATE WORK_STATUS SET application_and_approval="' + str(application_and_approval) + '" WHERE employee_no="' + str(employee_no) + '" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'" AND application_and_approval= "未申請"')
                conn.commit()
                return redirect(url_for('daily_attendance'))
#一括承認ボタンが押されたときの処理
@app.route('/all_approval',methods=['POST','GET'])
def all_approval():
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        year=request.form["year"]
        month=request.form["month2"]
        date=dt.datetime(int(year),int(month),1)
        application_and_approval="承認済み"
        cur.execute('SELECT * FROM WORK_STATUS WHERE DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'" AND application_and_approval= "承認待ち"')
        work_status_table=cur.fetchall()
        if work_status_table==None:
               return redirect(url_for('admin_daily_attendance'))
        elif work_status_table!=None: 
                cur.execute('UPDATE WORK_STATUS SET application_and_approval="' + str(application_and_approval) + '" WHERE application_and_approval= "承認待ち" AND DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
                conn.commit()
                return redirect(url_for('admin_daily_attendance'))

#admin_daily_attendance.htmlのセレクトボックスで全て表示を選んだ時の処理
@app.route('/all_employee_display',methods=['POST','GET'])
def all_employee_display():
        
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        year=request.form["year"]
        print(year)
        month=request.form["month2"]
        date=dt.datetime(int(year),int(month),1)
        cur.execute('SELECT employee_no,name From USER_ACCOUNT')
        general_user=cur.fetchall()
        cur.execute('SELECT * FROM WORK_STATUS WHERE DATE_FORMAT(date,"%Y%m")="'+str(year)+str(month)+'"')
        work_status_table=cur.fetchall()
        no=[]
        day=[]
        employee_no=[]
        name=[]
        start_time_timeOnly=[]
        finish_time_timeOnly=[]
        break_start_time_timeOnly=[]
        break_finish_time_timeOnly=[]
        interval_time=[]
        approval_status=[]
        for i in range(len(work_status_table)):
                        no.append(work_status_table[i][0])
                        employee_no.append(work_status_table[i][1])
                        day.append(work_status_table[i][2].day)
                        start_time_timeOnly.append(work_status_table[i][4].time())
                        finish_time_timeOnly.append(work_status_table[i][5].time())
                        if work_status_table[i][6]==None:
                                break_start_time_timeOnly.append("0:00")
                        else:
                                break_start_time_timeOnly.append(work_status_table[i][6].time())
                        if work_status_table[i][7]==None:
                                break_finish_time_timeOnly.append("0:00")
                        else:
                                break_finish_time_timeOnly.append(work_status_table[i][7].time())
                        interval_time.append(work_status_table[i][8])
                        approval_status.append(work_status_table[i][9])
        for i in range(len(employee_no)):
                for j in range(len(general_user)):
                        if employee_no[i]==general_user[j][0]:
                                name.append(general_user[j][1])
        
        work_status_table_length=len(work_status_table)
        print(work_status_table)
        select2="承認待ちのみ"
        selected_value2="./admin_daily_attendance2"
        select1="全て表示"
        selected_value1="./all_employee_display"

        return render_template("admin_daily_attendance.html",day=day,work_start_time=start_time_timeOnly,work_finish_time=finish_time_timeOnly,break_start_time=break_start_time_timeOnly,break_finish_time=break_finish_time_timeOnly,interval_time=interval_time,work_status_table_length=work_status_table_length,year=year,month=month,approval_status=approval_status,no=no,general_user_name=name,general_user_employee_no=employee_no,select1=select1,select2=select2,selected_value1=selected_value1,selected_value2=selected_value2)
#admin_daily_attendance.htmlのセレクトボックスで承認待ちのみを選んだ時の処理
@app.route("/admin_daily_attendance2",methods=['POST','GET'])
def admin_daily_attendance2():
        year=request.form["year"]
        month=request.form["month2"]
        date=dt.datetime(int(year),int(month),1)
        no=[]
        day=[]
        employee_no=[]
        name=[]
        start_time_timeOnly=[]
        finish_time_timeOnly=[]
        break_start_time_timeOnly=[]
        break_finish_time_timeOnly=[]
        interval_time=[]
        approval_status=[] 
        conn=mysql.connector.connect(user='admin',password='alicealice',host='dakokukun.cfkjffrk4iv5.ap-northeast-1.rds.amazonaws.com',database='dakokukun',port=3306)
        
        conn.ping(reconnect=True)
        cur = conn.cursor(buffered=True)
        cur.execute('select name,employee_no from ADMIN_USER_ACCOUNT where loginID= "' + str(session['user_id'][0]) + '";')
        username_and_employeeno=cur.fetchone()
        
        cur.execute('select * from WORK_STATUS where application_and_approval= "承認待ち"')
        work_status_table=cur.fetchall()
        cur.execute('SELECT employee_no,name From USER_ACCOUNT')
        general_user=cur.fetchall()
        
        for i in range(len(work_status_table)):
                no.append(work_status_table[i][0])
                employee_no.append(work_status_table[i][1])
                day.append(work_status_table[i][2].day)
                start_time_timeOnly.append(work_status_table[i][4].time())
                finish_time_timeOnly.append(work_status_table[i][5].time())
                if work_status_table[i][6]==None:
                        break_start_time_timeOnly.append("0:00")
                else:
                        break_start_time_timeOnly.append(work_status_table[i][6].time())
                if work_status_table[i][7]==None:
                        break_finish_time_timeOnly.append("0:00")
                else:
                        break_finish_time_timeOnly.append(work_status_table[i][7].time())
                interval_time.append(work_status_table[i][8])
                approval_status.append(work_status_table[i][9])
        for i in range(len(employee_no)):
                for j in range(len(general_user)):
                        if employee_no[i]==general_user[j][0]:
                                name.append(general_user[j][1])
        
        work_status_table_length=len(work_status_table)
        select1="承認待ちのみ"
        selected_value1="./admin_daily_attendance2"
        select2="全て表示"
        selected_value2="./all_employee_display"
        return render_template("admin_daily_attendance.html",admin_name=username_and_employeeno[0],admin_employee_no=username_and_employeeno[1],day=day,work_start_time=start_time_timeOnly,work_finish_time=finish_time_timeOnly,break_start_time=break_start_time_timeOnly,break_finish_time=break_finish_time_timeOnly,interval_time=interval_time,work_status_table_length=work_status_table_length,year=year,month=month,approval_status=approval_status,no=no,general_user_name=name,general_user_employee_no=employee_no,select1=select1,select2=select2,selected_value1=selected_value1,selected_value2=selected_value2)

        
        

if __name__ == '__main__':
        app.run(host='0.0.0.0',port=80,debug=True)