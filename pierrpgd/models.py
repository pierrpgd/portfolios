from django.db import models

class Profile(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

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

    class Meta:
        ordering = ['order']  # Ordonne par ordre décroissant

    def __str__(self):
        return f"{self.position} at {self.company}"

class Project(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title