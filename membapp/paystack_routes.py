import os,random,string,json, requests
#import 3rd party 
from sqlalchemy import or_

from flask import render_template,request,session,redirect, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
#import from local files
from membapp import app ,db, csrf
from membapp.models import Party,User, Topics,Contact,Comments,Lga,State,Donation,Payment
from membapp.forms import ContactForm

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
