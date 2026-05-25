from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=100, blank=True, null=True, help_text="Domain name for Logo.dev integration (e.g. accenture.com)")
    repo_folder = models.CharField(max_length=100, blank=True, null=True, help_text="Folder name of this company in the local com/ directory (e.g. accenture)")
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

    def save(self, *args, **kwargs):
        from django.core.cache import cache
        cache.delete('sorted_companies')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        from django.core.cache import cache
        cache.delete('sorted_companies')
        super().delete(*args, **kwargs)



class SiteSetting(models.Model):
    pyq_link = models.URLField(
        blank=True,
        default="",
        help_text="The URL for the IEM Previous Year Questions. Leave blank to show 'Coming Soon' popup."
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
        return setting.pyq_link or ""