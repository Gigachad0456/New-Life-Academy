from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.utils import secure_filename
import os
import time

from flask_sqlalchemy import SQLAlchemy
from flask import flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route("/")
def home():
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.timestamp.desc()).all()
    return render_template("index.html", announcements=announcements)

@app.route("/about")
def about():
    message_record = PrincipalMessage.query.first()
    # Fallback to default message if database is empty
    default_text = "Welcome to New Life Ministry School. Our commitment is to create a safe and inspiring environment where every student can thrive academically and spiritually. Together with parents and staff, we strive to build a strong foundation for lifelong success."
    principal_message = message_record.message if message_record else default_text
    
    return render_template("about.html", principal_message=principal_message, message_record=message_record)

@app.route("/academics")
def academics():
    return render_template("academics.html")

from datetime import datetime

@app.route("/admission", methods=["GET", "POST"])
def admission():
    if request.method == "POST":
        student_name = request.form.get("student_name")
        parent_name = request.form.get("parent_name")
        student_class = request.form.get("student_class")
        contact = request.form.get("contact")
        email = request.form.get("email")
        address = request.form.get("address")

        # Validation
        if not student_name or not parent_name or not student_class or not contact:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("admission"))

        new_admission = Admission(
            student_name=student_name,
            parent_name=parent_name,
            student_class=student_class,
            contact=contact,
            email=email,
            address=address,
            status="pending"
        )

        db.session.add(new_admission)
        db.session.commit()

        flash("Application submitted successfully! We will contact you soon.", "success")
        return redirect(url_for("admission"))

    return render_template("admission.html")

@app.route("/admission/form", methods=["GET", "POST"])
def admission_form():
    if request.method == "POST":

        full_name = request.form.get("full_name")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        parent_name = request.form.get("parent_name")
        contact_number = request.form.get("contact_number")
        email = request.form.get("email")
        applying_class = request.form.get("applying_class")
        address = request.form.get("address")

        new_admission = Admission(
            full_name=full_name,
            dob=dob,
            gender=gender,      
            parent_name=parent_name,
            student_class=applying_class,
            contact=contact_number,
            email=email,
            address=address
            )

        db.session.add(new_admission)
        db.session.commit()

        flash("Application submitted successfully!", "success")
        return redirect(url_for("admission"))

    return render_template("admission_form.html")

@app.route("/submit_admission", methods=["POST"])
def submit_admission():

    new_admission = Admission(
        full_name=request.form.get("full_name"),
        dob=request.form.get("dob"),
        gender=request.form.get("gender"),
        parent_name=request.form.get("parent_name"),
        contact_number=request.form.get("contact_number"),
        email=request.form.get("email"),
        applying_class=request.form.get("applying_class"),
        address=request.form.get("address")
    )

    db.session.add(new_admission)
    db.session.commit()

    return redirect(url_for("admission"))

@app.route("/gallery")
def gallery():
    images = Gallery.query.all()
    return render_template("gallery.html", images=images)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")
        
        if not name or not email or not message:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("contact"))
            
        new_inquiry = ContactInquiry(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        db.session.add(new_inquiry)
        db.session.commit()
        
        flash("Thank you for your message! We will get back to you soon.", "success")
        return redirect(url_for("contact"))
        
    return render_template("contact.html")

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if "admin" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.password == password:
            session["admin"] = admin.username
            return redirect(url_for("dashboard"))
        else:
            return render_template("adminLogin.html", error="Invalid username or password")

    return render_template("adminLogin.html")
 
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    student_class = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    admission_date = db.Column(db.String(50), nullable=False)
    
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    dob = db.Column(db.String(50))  # Store as string for simplicity, could be Date
    gender = db.Column(db.String(20), nullable=False)
    contact_number = db.Column(db.String(50))
    email = db.Column(db.String(100))
    subjects = db.Column(db.String(200), nullable=False)
    classes_assigned = db.Column(db.String(200))  # Comma separated or JSON
    hire_date = db.Column(db.String(50))
    salary = db.Column(db.Float)
    
class Admission(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(150), nullable=False)
    dob = db.Column(db.String(50))
    gender = db.Column(db.String(20))
    parent_name = db.Column(db.String(150), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    applying_class = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200))

    status = db.Column(db.String(20), default="pending")
    date_applied = db.Column(db.DateTime, default=datetime.utcnow)

class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(300), nullable=False)

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ContactInquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PrincipalMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    total_students = Student.query.count()
    total_teachers = Teacher.query.count()
    active_announcements = Announcement.query.filter_by(is_active=True).count()
    total_inquiries = ContactInquiry.query.count()

    return render_template("adminDashboard.html",
                           admin=session["admin"],
                           total_students=total_students,
                           total_teachers=total_teachers,
                           active_announcements=active_announcements,
                           total_inquiries=total_inquiries)
 
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/admin/students")
def students():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    students = Student.query.all()
    return render_template("adminStudents.html",
                           admin=session["admin"],
                           students=students)


@app.route("/admin/teachers")
def teachers():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
    teachers = Teacher.query.all()
    return render_template("adminTeachers.html", admin=session["admin"], teachers=teachers)


@app.route("/admin/teachers/add", methods=["GET", "POST"])
def add_teacher():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        full_name = request.form.get("full_name")
        gender = request.form.get("gender")
        subjects = request.form.get("subjects")
        dob = request.form.get("dob")
        contact_number = request.form.get("contact_number")
        email = request.form.get("email")
        classes_assigned = request.form.get("classes_assigned")
        hire_date = request.form.get("hire_date")
        salary = request.form.get("salary")

        # Basic backend validation
        if not full_name or not gender or not subjects:
            flash("Please fill in required fields: Full Name, Gender, Subjects.", "error")
            return redirect(url_for("add_teacher"))

        new_teacher = Teacher(
            full_name=full_name,
            gender=gender,
            subjects=subjects,
            dob=dob,
            contact_number=contact_number,
            email=email,
            classes_assigned=classes_assigned,
            hire_date=hire_date,
            salary=float(salary) if salary else None
        )

        db.session.add(new_teacher)
        db.session.commit()

        flash("Teacher added successfully!", "success")
        return redirect(url_for("add_teacher"))

    return render_template("addTeacher.html")

@app.route("/admin/teachers/edit/<int:id>", methods=["GET", "POST"])
def edit_teacher(id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    teacher = Teacher.query.get_or_404(id)

    if request.method == "POST":
        teacher.full_name = request.form.get("full_name")
        teacher.gender = request.form.get("gender")
        teacher.subjects = request.form.get("subjects")
        teacher.classes_assigned = request.form.get("classes_assigned")
        teacher.dob = request.form.get("dob")
        teacher.contact_number = request.form.get("contact_number")
        teacher.email = request.form.get("email")
        teacher.hire_date = request.form.get("hire_date")
        salary = request.form.get("salary")
        teacher.salary = float(salary) if salary else None

        db.session.commit()
        flash("Teacher updated successfully!", "success")
        return redirect(url_for("teachers"))

    return render_template("editTeacher.html", teacher=teacher)

@app.route("/admin/teachers/delete/<int:id>")
def delete_teacher(id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()

    flash("Teacher deleted successfully!", "success")
    return redirect(url_for("teachers"))


@app.route("/admin/admissions")
def admin_admissions():
    admissions = Admission.query.all()

    total = len(admissions)
    pending = len([a for a in admissions if a.status == "pending"])
    approved = len([a for a in admissions if a.status == "approved"])
    rejected = len([a for a in admissions if a.status == "rejected"])

    return render_template(
        "adminAdmissions.html",
        admissions=admissions,
        total=total,
        pending=pending,
        approved=approved,
        rejected=rejected
    )

@app.route("/admin/admission/approve/<int:id>", methods=["POST"])
def approve_admission(id):
    admission = Admission.query.get_or_404(id)
    admission.status = "Approved"
    db.session.commit()
    return redirect(url_for("admin_admissions"))


@app.route("/admin/admission/reject/<int:id>", methods=["POST"])
def reject_admission(id):
    admission = Admission.query.get_or_404(id)
    admission.status = "Rejected"
    db.session.commit()
    return redirect(url_for("admin_admissions"))

@app.route("/admin/gallery")
def gallery_admin():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
    images = Gallery.query.all()
    return render_template("adminGallery.html", admin=session["admin"], images=images)

@app.route("/admin/gallery/upload", methods=["POST"])
def upload_gallery():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
        
    if "image" not in request.files:
        flash("No file part", "error")
        return redirect(url_for("gallery_admin"))
        
    file = request.files["image"]
    if file.filename == "":
        flash("No selected file", "error")
        return redirect(url_for("gallery_admin"))
        
    if file:
        original_filename = secure_filename(file.filename)
        # Prevent overwriting files with the same name by prepending a timestamp
        filename = f"{int(time.time())}_{original_filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        
        new_image = Gallery(filename=filename)
        db.session.add(new_image)
        db.session.commit()
        flash("Image uploaded successfully!", "success")
        
    return redirect(url_for("gallery_admin"))

@app.route("/admin/gallery/delete/<int:id>")
def delete_image(id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))
        
    image = Gallery.query.get_or_404(id)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except OSError as e:
            print(f"Error removing file: {e}")
            
    db.session.delete(image)
    db.session.commit()
    flash("Image deleted successfully!", "success")
    return redirect(url_for("gallery_admin"))


@app.route("/admin/messages")
def messages():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
        
    announcements = Announcement.query.order_by(Announcement.timestamp.desc()).all()
    return render_template("adminMessages.html", admin=session["admin"], announcements=announcements)

@app.route("/admin/messages/add", methods=["POST"])
def add_message():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
        
    title = request.form.get("title")
    content = request.form.get("content")
    
    if not title or not content:
        flash("Title and Content are required", "error")
        return redirect(url_for("messages"))
        
    new_announcement = Announcement(title=title, content=content)
    db.session.add(new_announcement)
    db.session.commit()
    
    flash("Announcement created successfully!", "success")
    return redirect(url_for("messages"))

@app.route("/admin/messages/toggle/<int:id>")
def toggle_message(id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))
        
    announcement = Announcement.query.get_or_404(id)
    announcement.is_active = not announcement.is_active
    db.session.commit()
    
    flash(f"Announcement marked as {'Active' if announcement.is_active else 'Inactive'}.", "success")
    return redirect(url_for("messages"))

@app.route("/admin/messages/delete/<int:id>")
def delete_message(id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))
        
    announcement = Announcement.query.get_or_404(id)
    db.session.delete(announcement)
    db.session.commit()
    
    flash("Announcement deleted successfully!", "success")
    return redirect(url_for("messages"))
 

@app.route("/admin/students/add", methods=["GET", "POST"])
def add_student():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        full_name = request.form.get("full_name")
        student_class = request.form.get("student_class")
        gender = request.form.get("gender")
        admission_date = request.form.get("admission_date")

        # Backend validation
        if not full_name or not student_class or not gender or not admission_date:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("add_student"))

        new_student = Student(
            full_name=full_name,
            student_class=student_class,
            gender=gender,
            admission_date=admission_date
        )

        db.session.add(new_student)
        db.session.commit()

        flash("Student added successfully!", "success")
        return redirect(url_for("add_student"))

    return render_template("addStudent.html")
@app.route("/admin/students/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    student = Student.query.get_or_404(id)

    if request.method == "POST":
        full_name = request.form.get("full_name")
        student_class = request.form.get("student_class")
        gender = request.form.get("gender")
        admission_date = request.form.get("admission_date")

        if not full_name or not student_class or not gender or not admission_date:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("edit_student", id=id))

        student.full_name = full_name
        student.student_class = student_class
        student.gender = gender
        student.admission_date = admission_date

        db.session.commit()
        flash("Student updated successfully!", "success")
        return redirect(url_for("edit_student", id=id))

    return render_template("editStudent.html", student=student)
@app.route("/admin/inquiries")
def inquiries():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
        
    all_inquiries = ContactInquiry.query.order_by(ContactInquiry.timestamp.desc()).all()
    return render_template("adminInquiries.html", admin=session["admin"], inquiries=all_inquiries)

@app.route("/admin/inquiries/delete/<int:id>")
def delete_inquiry(id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))
        
    inquiry = ContactInquiry.query.get_or_404(id)
    db.session.delete(inquiry)
    db.session.commit()
    
    flash("Inquiry deleted successfully!", "success")
    return redirect(url_for("inquiries"))

@app.route("/admin/principal", methods=["GET", "POST"])
def admin_principal():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
        
    message_record = PrincipalMessage.query.first()
    
    if request.method == "POST":
        new_text = request.form.get("message")
        image = request.files.get("image")
        
        if not new_text or not new_text.strip():
            flash("Message cannot be empty.", "error")
        else:
            if not message_record:
                message_record = PrincipalMessage(message=new_text.strip())
                db.session.add(message_record)
            else:
                message_record.message = new_text.strip()
                
            if image and image.filename != "":
                filename = secure_filename(image.filename)
                # Prepend timestamp to avoid overwriting files with the same name
                unique_filename = f"{int(time.time())}_{filename}"
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
                
                try:
                    image.save(image_path)
                    
                    # Optionally, if you want to delete the old image:
                    # if message_record.image_filename:
                    #     old_image_path = os.path.join(app.config["UPLOAD_FOLDER"], message_record.image_filename)
                    #     if os.path.exists(old_image_path):
                    #         os.remove(old_image_path)
                            
                    message_record.image_filename = unique_filename
                except Exception as e:
                    flash(f"Error saving image: {e}", "error")
            
            db.session.commit()
            flash("Principal message and image updated successfully!", "success")
            
    return render_template("adminPrincipal.html", admin=session["admin"], message_record=message_record)
def delete_student(id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()

    return redirect(url_for("students"))
# -------- CREATE DEFAULT ADMINS --------
def create_default_admins():
    with app.app_context():
        if not Admin.query.first():  # Only create if table is empty
            admin1 = Admin(username="isaac", password="mypassword123")
            admin2 = Admin(username="admin2", password="1234")
            admin3 = Admin(username="admin3", password="1234")

            db.session.add_all([admin1, admin2, admin3])
            db.session.commit()
            print("Default admins created.")


# -------- MAIN --------            
if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # Make sure tables exist
    create_default_admins()  # Create admins if none exist
    
    # Read debug mode from environment, defaulting to False in production
    debug_mode = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "t")
    app.run(debug=debug_mode)