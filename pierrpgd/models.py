from django.db import models
from django.utils import timezone

class Profile(models.Model):
    identifiant = models.CharField(max_length=100, unique=True, null=False, blank=False, default='default')
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    skills = models.ManyToManyField('Skill', through='ProfileSkill', blank=True)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Skill(models.Model):
    category = models.CharField(max_length=100, blank=False)
    name = models.CharField(max_length=100, blank=False)
    
    def __str__(self):
        return f"{self.category} - {self.name}"

class ProfileSkill(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.IntegerField(default=0)

class About(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='about')
    content = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"About {self.order} for {self.profile.name}"

class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experience')
    dates = models.CharField(max_length=50)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    position = models.CharField(max_length=150)
    description = models.TextField()
    order = models.IntegerField(default=0)
    url = models.URLField(blank=True, null=True)
    skills = models.ManyToManyField('Skill', blank=True)

    class Meta:
        ordering = ['order']  # Ordonne par ordre décroissant

    def __str__(self):
        return f"{self.position} at {self.company}"

class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='education')
    dates = models.CharField(max_length=50)
    institution = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    title = models.CharField(max_length=150)
    field = models.CharField(max_length=150)
    description = models.TextField()
    order = models.IntegerField(default=0)
    url = models.URLField(blank=True, null=True)
    skills = models.ManyToManyField('Skill', blank=True)

    class Meta:
        ordering = ['order']  # Ordonne par ordre décroissant

    def __str__(self):
        return f"{self.title} at {self.institution}"

class Project(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)
    image_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    skills = models.ManyToManyField('Skill', blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title