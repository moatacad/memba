from datetime import datetime
from membapp import db


class Contact(db.Model):
    __table_args__ = {
        "mysql_default_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_general_ci",
    }
    __tablename__='messages'
    msg_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    msg_email=db.Column(db.String(100),nullable=False) 
    msg_content=db.Column(db.Text(),nullable=False) 
    msg_date=db.Column(db.DateTime(), default=datetime.utcnow)


class State(db.Model):
    state_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    state_name = db.Column(db.String(100),nullable=False) 
    #set relationship
    lgas = db.relationship("Lga", back_populates="state_deets")

class Lga(db.Model):
    lga_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    lga_name = db.Column(db.String(100),nullable=False)
    lga_stateid = db.Column(db.Integer, db.ForeignKey('state.state_id'))    
    #set relationships
    state_deets = db.relationship("State", back_populates="lgas")
    

class Topics(db.Model):
    topic_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    topic_title = db.Column(db.Text(),nullable=False)
    topic_date =db.Column(db.DateTime(), default=datetime.utcnow)
    topic_userid = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)  
    topic_status =db.Column(db.Enum('1','0'),nullable=False, server_default=("0"))  
    
    #set relationships
    userdeets = db.relationship("User", back_populates="topics_postedbyme")
    all_comments = db.relationship("Comments", back_populates="the_topic",cascade="all, delete-orphan")
    

class Comments(db.Model):
    comment_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    comment_text = db.Column(db.String(255),nullable=False)
    comment_date =db.Column(db.DateTime(), default=datetime.utcnow)
    comment_userid = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)  
    comment_topicid =db.Column(db.Integer, db.ForeignKey('topics.topic_id'),nullable=False)  
    
    #set relationships
    commentby = db.relationship("User", back_populates="mycomments")
    the_topic = db.relationship("Topics", back_populates="all_comments")
    
      
class User(db.Model):  
    user_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    user_fullname = db.Column(db.String(100),nullable=False)
    user_email = db.Column(db.String(120)) 
    user_pwd=db.Column(db.String(120),nullable=True)
    user_phone=db.Column(db.String(120),nullable=True) 
    user_pix=db.Column(db.String(120),nullable=True) 
    user_datereg=db.Column(db.DateTime(), default=datetime.utcnow)#default 
    #set the foreign key 
    user_partyid=db.Column(db.Integer, db.ForeignKey('party.party_id'))    
    
    #set relationships
    
    topics_postedbyme = db.relationship("Topics", back_populates="userdeets")
    mycomments = db.relationship("Comments", back_populates="commentby")
    pvcdeets = db.relationship("Pvc", back_populates="userdeets",uselist=False)
     
class Party(db.Model):
    party_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    party_name = db.Column(db.String(100),nullable=False)
    party_shortcode = db.Column(db.String(120)) 
    party_logo=db.Column(db.String(120),nullable=True)
    party_contact=db.Column(db.String(120),nullable=True)     
    #set relationship
   
    partymembers = db.relationship("User", backref="party_deets")
    
    
    
class Admin(db.Model):
    admin_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    admin_username=db.Column(db.String(20),nullable=True)
    admin_pwd=db.Column(db.String(200),nullable=True)
    
    
#many to many relationship (association table)

#one to one relationship
class Pvc(db.Model):  
    pvc_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    pvc_userid = db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    pvc_lga = db.Column(db.Integer,db.ForeignKey('lga.lga_id')) 
    pvc_status=db.Column(db.Enum('pending','ready','collected'),nullable=False,server_default=("pending"))
    #set relationship
    userdeets = db.relationship("User", back_populates="pvcdeets")
    lgadeets = db.relationship("Lga", backref="dpvc")
    
class Department(db.Model):
    dept_id=db.Column(db.Integer,autoincrement=True,primary_key=True)
    dept_name = db.Column(db.String(200),nullable=False)
    
class Volunteers(db.Model):
    vol_id =db.Column(db.Integer,autoincrement=True,primary_key=True)
    vol_userid=db.Column(db.Integer,db.ForeignKey('user.user_id')) 
    vol_deptid=db.Column(db.Integer,db.ForeignKey('department.dept_id')) 
    vol_date=db.Column(db.DateTime(), default=datetime.utcnow)
    
    #set relationships
    vol_userdeets = db.relationship("User", backref="units_volunteered")
    vol_deptdeets = db.relationship("Department", backref="users_in_unit")