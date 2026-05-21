from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True, help_text="Alternatively, enter a direct image URL (e.g. from Imgur)")
    link = models.URLField(help_text="Link to LeetCode or question bank")
    question_count = models.CharField(max_length=50, default="0+ Questions")
    needs_white_bg = models.BooleanField(default=True, help_text="Check if logo needs a white background wrapper")

    @property
    def get_logo_url(self):
        if self.logo_url:
            return self.logo_url
        elif self.logo:
            return self.logo.url
        return ""

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name


class SiteSetting(models.Model):
    pyq_link = models.URLField(
        default="https://drive.google.com/drive/folders/1VT_6K9Q1zfIdbDLjf96YrsyEk3hfbMvX?usp=sharing",
        help_text="The URL for the IEM Previous Year Questions"
    )

    class Meta:
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    @classmethod
    def get_pyq_link(cls):
        setting = cls.objects.first()
        if not setting:
            return "https://drive.google.com/drive/folders/1VT_6K9Q1zfIdbDLjf96YrsyEk3hfbMvX?usp=sharing"
        return setting.pyq_link