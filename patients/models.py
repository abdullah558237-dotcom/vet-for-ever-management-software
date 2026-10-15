from django.db import models
from django.urls import reverse
from django.utils import timezone

class Owner(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True, db_index=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.get_full_name()} ({self.phone})"


class Patient(models.Model):
    class Species(models.TextChoices):
        DOG = 'DOG', 'Dog (Canine)'
        CAT = 'CAT', 'Cat (Feline)'
        BIRD = 'BIRD', 'Bird (Avian)'
        RABBIT = 'RABBIT', 'Rabbit'
        OTHER = 'OTHER', 'Other / Exotic'

    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male (Intact)'
        FEMALE = 'FEMALE', 'Female (Intact)'
        MALE_NEUTERED = 'MALE_NEUTERED', 'Male (Neutered)'
        FEMALE_SPAYED = 'FEMALE_SPAYED', 'Female (Spayed)'

    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='patients')
    name = models.CharField(max_length=100, db_index=True)
    species = models.CharField(max_length=20, choices=Species.choices, default=Species.DOG)
    breed = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=20, choices=Gender.choices, default=Gender.MALE)
    date_of_birth = models.DateField(null=True, blank=True)
    color_markings = models.CharField(max_length=150, blank=True)
    microchip_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    photo = models.ImageField(upload_to='patients/', blank=True, null=True)
    allergies_notes = models.TextField(blank=True, help_text="Critical medical alerts or allergies")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def age_display(self):
        if not self.date_of_birth:
            return "Age unknown"
        today = timezone.now().date()
        years = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        months = (today.month - self.date_of_birth.month) % 12
        if years > 0:
            return f"{years} yr{'s' if years > 1 else ''} {months} mo"
        elif months > 0:
            return f"{months} mo{'s' if months > 1 else ''}"
        else:
            days = (today - self.date_of_birth).days
            return f"{days} day{'s' if days > 1 else ''}"

    def get_absolute_url(self):
        return reverse('patient_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.name} ({self.get_species_display()}) - {self.owner.get_full_name()}"
