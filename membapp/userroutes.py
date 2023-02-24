import os,random,string,json, requests
#import 3rd party 
from sqlalchemy import or_

from flask import render_template,request,session,redirect, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
#import from local files
from membapp import app ,db, csrf
from membapp.models import Party,User, Topics,Contact,Comments,Lga,State,Donation,Payment
from membapp.forms import ContactForm

def generate_name():
    filename = random.sample(string.ascii_lowercase,10) #will return a list
    return ''.join(filename) #join every member of the list filename together

#TO DO:
@app.route("/check_username",methods=['POST','GET'])
def check_username():
    if request.method =="GET":
        return "Please complete the form normally"
    else:
        email = request.form.get('email')
        data = db.session.query(User).filter(User.user_email==email).first()
        if data == None:
            sendback = {'status':1,'feedback':"Email is available, please register"}
            return json.dumps(sendback)
        else:
            sendback = {'status':0,'feedback':"You have registered already. Click <a href='/login'>here</a> to login"}
            return json.dumps(sendback)
    
    
    

@app.route("/")
def home(): 
    contact = ContactForm()
    #connect to the endpoint to get the list of properties in JSON format,
    #Convert to python dictionary and pass it to our template
    try:
        response = requests.get("http://127.0.0.1:8000/api/v1.0/listall")
        if response:
            rspjson = json.loads(response.text)
        else:
            rspjson = dict()
    except:
        rspjson = dict()
    return render_template('user/home.html', contact=contact,rspjson=rspjson)


@app.route("/donate",methods=["POST","GET"])
def donate():
    if session.get('user') != None:
        deets= User.query.get(session.get('user'))
    else:
        deets=None    
    if request.method =='GET':
        return render_template('user/donation_form.html',deets=deets)
    else:
        #retrieve the form data and insert into Donation table
        #ref = int(random.random() * 100000000)
        amount = request.form.get('amount')
        fullname = request.form.get('fullname')
        d = Donation(don_donor=fullname,don_amt=amount,don_userid=session.get('user'))
        db.session.add(d); db.session.commit()
        session['donation_id'] = d.don_id
        #Generate the ref no and keep in session
        refno = int(random.random()*100000000)
        session['reference'] = refno
        return  redirect("/confirm") 
 
@app.route('/confirm',methods=['POST','GET'])
def confirm():
    if session.get('donation_id')!= None:
        if request.method =='GET':  
            donor = db.session.query(Donation).get(session['donation_id'])
            return render_template('user/confirm.html',donor=donor,refno=session['reference'])
        else:
            p = Payment(pay_donid=session.get('donation_id'),pay_ref=session['reference'])
            db.session.add(p);db.session.commit()
            
            don = Donation.query.get(session['donation_id'])#details of the donation
            donor_name = don.don_donor
            amount = don.don_amt * 100
            headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_3c5244cfb8965dd000f07a4cfa97185aab2e88d5"}
            data={"amount":amount,"reference":session['reference'],"email":donor_name}
            
            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))
            rspjson= json.loads(response.text)
            if rspjson['status'] == True:
                url = rspjson['data']['authorization_url']
                return redirect(url)
            else:
                return redirect('/confirm')
    else:
        return redirect('/donate')
    

@app.route('/paystack')
def paystack():
    refid = session.get('reference')
    if refid ==None:
        return redirect('/')
    else:
        #connect to paystack verify
        headers={"Content-Type": "application/json","Authorization":"Bearer sk_test_3c5244cfb8965dd000f07a4cfa97185aab2e88d5"}
        verifyurl= "https://api.paystack.co/transaction/verify/"+str(refid)
        response= requests.get(verifyurl, headers=headers)
        rspjson = json.loads(response.text)
        if rspjson['status']== True:
            #payment was successful
            return rspjson
        else:
            #payment was not successful
            return "payment was not successful"


@app.route("/login", methods=['GET','POST'])
@csrf.exempt
def user_login(): 
    if request.method =="GET":
        return render_template('user/login.html')
    else:#retrieve the form data
        email = request.form.get('email') 
        pwd = request.form.get('pwd')
        '''run a query to know if the username exists on the database'''
        deets = db.session.query(User).filter(User.user_email==email).first()
        '''compare the password coming from the form with the hashed password in the db'''
        if deets != None:
            pwd_indb = deets.user_pwd
            #compare with the plain password from the form
            chk = check_password_hash(pwd_indb,pwd)
            if chk:
                id = deets.user_id
                session['user'] = id
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid password")
                return redirect(url_for('user_login'))
        else:
            flash("Invalid Username")
            return redirect(url_for('user_login'))

@app.route('/logout')
def user_logout():
    #pop the session and redirect to home page
    if session.get('user')!=None:
        session.pop('user',None)
    return redirect('/')



@app.route("/signup")
def user_signup():
    p = db.session.query(Party).all() #Party.query.all()
    return render_template("user/signup.html",p=p) #[<Party><Party><Party>]

@app.route("/register",methods=['POST'])
def register():
    party = request.form.get('partyid')
    email = request.form.get('email')
    pwd = request.form.get('pwd')
    hashed_pwd = generate_password_hash(pwd)
    if party !='' and email !='' and pwd !='':
        #insert into database using ORM method
        u = User(user_fullname='',user_email=email,user_pwd=hashed_pwd,user_partyid =party)
        db.session.add(u)
        db.session.commit()  
        #To get the id of the record that has just been inserted
        userid = u.user_id
        session['user'] = userid #keep the user id in session
        return redirect(url_for('dashboard')) #create function dashboard
    else:
        flash("You must complete all the fields to signup")
        return redirect(url_for('user_signup'))


@app.route('/delete_image/<file>')
def delete_image(file):
    os.remove("membapp/static/uploads/"+file)
    return "File deleted!"
    
@app.route('/profile/picture', methods=['POST','GET'])
def profile_picture():
    if session.get('user') == None:
        return redirect(url_for('user_login'))
    else:
        if request.method=='GET':
            return render_template('user/profile_picture.html')
        else:#retrieve the file
            file = request.files['pix']
            
            filename = file.filename #original filename      
        
            allowed =['.png','.jpg','.jpeg']            
            if filename !="":
                name,ext = os.path.splitext(filename) #import os on line1
                if ext.lower() in allowed:   
                    newname = generate_name()+ ext             
                    file.save("membapp/static/uploads/"+newname)  
                    
                    userobj = db.session.query(User).get(session['user'])
                    userobj.user_pix=newname
                    db.session.commit()
                    flash("Picture uploaded")                  
                    return redirect(url_for('dashboard'))                
                
                else:
                    return "File extension not allowed"
            else:
                flash("please choose a file")
                return "please choose a file"
   


@app.route("/dashboard")
def dashboard(): 
    #protect this route so that only logged in user can get here
    if session.get('user') != None:
        #retrieve the details of the logged in user
        id = session['user']
        deets = db.session.query(User).get(id)
        return render_template('user/dashboard.html',deets=deets)

    else:
        return redirect(url_for('user_login'))


@app.route('/load_lga/<stateid>')
def load_lga(stateid):
    lgas = db.session.query(Lga).filter(Lga.lga_stateid==stateid).all()
    data2send = "<select class='form-control border-success'>"    
    for s in lgas:
        data2send = data2send+"<option>"+s.lga_name +"</option>"
    
    data2send = data2send + "</select>"   
    
    return data2send








@app.route('/profile',methods=['POST','GET'])
@csrf.exempt
def profile():
    id = session.get('user')
    if id ==None:#means the person is not logged in
        return redirect(url_for('user_login'))
    else:
        if request.method =="GET":
            allstates = db.session.query(State).all()
            deets = db.session.query(User).filter(User.user_id==id).first()
            allparties = Party.query.all()
            
            return render_template('user/profile.html',deets=deets,allstates=allstates,allparties=allparties)
        
        else:#form was submitted
            fullname=request.form.get('fullname')
            phone = request.form.get('phone')
            myparty = request.form.get('myparty')
            #update the db using ORM method
            userobj = db.session.query(User).get(id)
            userobj.user_fullname=fullname
            userobj.user_phone=phone
            userobj.user_partyid=myparty
            db.session.commit()
            flash("Profile Updated!")
            return redirect("/profile")

@app.route('/blog/')
def blog(): 
    articles=db.session.query(Topics).filter(Topics.topic_status=='1').all()
    return render_template('user/blog.html',articles=articles) 


@app.route('/blog/<id>/')
def blog_details(id): 
    blog_deets =Topics.query.get_or_404(id)    
    return render_template('user/blog_details.html',blog_deets=blog_deets)

@app.route('/sendcomment')
def sendcomment():
    if session.get('user'):
        #retrieve the data coming from the request
        usermessage = request.args.get('message') #we can insert into db
        user = request.args.get('userid')
        topic = request.args.get('topicid')
        comment = Comments(comment_text=usermessage,comment_userid=user,comment_topicid=topic)
        db.session.add(comment)
        db.session.commit()
        commenter = comment.commentby.user_fullname
        dateposted = comment.comment_date
        sendback = f"{usermessage} <br>by {commenter} on {dateposted}"
        return sendback
    else:
        return "Comment was not posted, you need to be logged in"







    
@app.route('/newtopic', methods=['POST','GET'])
def newtopic():
    if session.get('user') != None:
        if request.method =='GET':
            return render_template('user/newtopic.html')  
        else:
            #retrieve form data and validate
            content = request.form.get('content')#your textarea name=content
            if len(content) > 0:
                t = Topics(topic_title=content,topic_userid=session['user'])
                db.session.add(t)
                db.session.commit()
                if t.topic_id:
                    flash("Post successfully submitted for approval")
                else:
                    flash('OOps, something went wrong. Please try again')
            else:
                flash("You cannot submit an empty post")
            return redirect('/blog')
    else:
        return redirect(url_for('user_login')) 
    
    
    
@app.route("/ajaxcontact", methods=['POST'])   
def contact_ajax():
    form = ContactForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        msg = request.form.get('message')
        #insert into database and send the feedback to AJAX/Javascript
        return f"{email} and {msg}"
    else:
        return "You need to complete the form"
    
    
    
    
    
    
    

@app.route("/contact", methods=['POST','GET'])
def contact_us():
    contact = ContactForm()
    if request.method =='GET':
        return render_template("user/contact_us.html", contact=contact)
    else:
        if contact.validate_on_submit():#True
            #retrieve form data and isert into db
            email = request.form.get('email')
            upload = contact.screenshot.data #request.files.get('sreenshot')
            msg = contact.message.data
            #insert into database            
            m = Contact(msg_email=email,msg_content=msg)
            db.session.add(m)
            db.session.commit()            
            flash('Thank you for contacting us')
            return redirect(url_for('contact_us'))
        else:#False
            return render_template("user/contact_us.html", contact=contact) 






@app.route("/demo",methods=['POST','GET'])
@csrf.exempt
def demo():
    if request.method =='GET':     
        
        return render_template("user/test.html")
    else:
        #retrieve form data 
        file = request.files.get('pix')
        picture_name = file.filename
        file.save("membapp/static/uploads/"+picture_name)
        return f'{picture_name}'
    
@app.route("/test")
def test():
    data = db.session.query(User,Party).join(Party).filter(User.user_id==1).first()
    return render_template('user/test.html',data=data)