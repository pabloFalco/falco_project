from django.db import models
from django.utils.timezone import now
from django.conf import settings

# Create your models here.

class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class Learner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200, null=True)

    def __str__(self):
        return self.user.username + "," + self.occupation

class Course(models.Model):
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        return self.name

class Lesson(models.Model):
    title = models.CharField(max_length=200, default="Lesson number X")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)

    def __str__(self): 
        return f"Enrollment for user {self.user} for course {self.course}"
                
class Question(models.Model):
    # One-To-Many relationship to Course
    courses = models.ManyToManyField(Course)
    # Foreign key to lesson (REMOVED as I wanted to relate questions directly with courses, see task caption)
    # lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=False)
    # question text
    question_text = models.CharField(max_length=500, default="This is a sample question.")
    # question grade/mark
    marks = models.FloatField(default=1.0)

    # A model method to calculate if learner scored points by answering correctly
    def answered_correctly(self, selected_ids):
       all_answers = self.choice_set.filter(is_correct=True).count()
       selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
       if all_answers == selected_correct:
           return True
       else:
           return False
    
    def __str__(self):
        return self.question_text

class Choice(models.Model):
    # One-To-Many relationship with Question
    question = models.ForeignKey(Question, models.SET_NULL, null=True)
    # Choice content / text
    choice_text = models.CharField(null=False, max_length=50)
    # Indicates whether the choice is correct or not
    is_correct = models.BooleanField(default=True)

    def __str__(self):
        return self.choice_text

class Submission(models.Model):
    # One enrollment could have multiple submission
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    # Many-to-Many relationship with choices
    choices = models.ManyToManyField(Choice)
    # Time and date metadata
    date_submitted  = models.DateField(default=now, editable=False)  
    time = models.TimeField(default=now, editable=False)

    def __str__(self):
        return f"Submission posted on {self.date_submitted} at {self.time} for {self.enrollment}"
