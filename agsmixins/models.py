from django.db import models

# Create your models here.
class _ModelURLs(object):
    @classmethod
    def appname(cls):
        return (cls.__module__).partition('.')[0]
    @classmethod
    def classname(cls):
        return cls._meta.verbose_name
    @classmethod
    def classname_plural(cls):
        return cls._meta.verbose_name_plural
    @classmethod
    def get_classname(cls):
        return cls._meta.verbose_name.replace(' ','')
    @classmethod
    def get_classname_plural(cls):
        return cls._meta.verbose_name_plural.replace(' ','')
    
    @classmethod
    def get_absolute_urlname(cls):
        return cls.appname() + '-' + cls.get_classname()
    @models.permalink
    def get_absolute_url(self):
        return(self.get_absolute_urlname(),[str(self.project.id),str(self.id)])
    
    @classmethod
    def get_list_urlname(cls):
        return cls.appname() + '-'+cls.get_classname_plural()
    @models.permalink
    def get_list_url(self):
        return(self.get_list_urlname(),[str(self.project.id),])
    
    @classmethod
    def get_new_urlname(cls):
        return cls.appname() + '-' + cls.get_classname() + '-new'
    @models.permalink
    def get_new_url(self):
        return(self.get_new_urlname(),[str(self.project.id),])
    @classmethod
    def get_newpu_urlname(cls):
        return cls.get_new_urlname() + '-pu'
    @models.permalink
    def get_newpu_url(self):
        return(self.get_newpu_urlname(),[str(self.project.id),])
    
    @classmethod
    def get_delete_urlname(cls):
        return cls.appname() + '-' + cls.get_classname() + '-del'
    @models.permalink
    def get_delete_url(self):
        return(self.get_delete_urlname(),[str(self.project.id),str(self.id)])
    class Meta:
        pusuffix = 'pu'
