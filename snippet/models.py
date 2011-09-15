from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete

class SnippetCache(object):
	def __init__(self):
		self.reset()

	def cache_key(self, name):
		try:
			return settings.SNIPPET_CACHE_PREFIX + name
		except:
			return "SNIPPET_CACHE"+name

	def get_cache(self, name):
		return cache.get(self.cache_key(name))

	def set_cache(self, name, value):
		return cache.set(self.cache_key(name), value)

	def del_cache(self, name):
		return cache.delete(self.cache_key(name))

	def get(self, name, default):
		ret = self.get_cache(name)
		if ret is not None:
			return ret

		try:
			snippet = Snippet.objects.get(name=name)
		except Snippet.DoesNotExist:
			snippet = Snippet.objects.create(name=name, content=default)
			snippet.save()
		self.set_cache(name, snippet.content)
		return snippet.content

	def reset(self):
		self.cache = {}

# Create your models here.
class Snippet(models.Model):
	name = models.CharField(max_length=255)
	content = models.TextField(blank=True)
	
	def __unicode__(self):
		return self.name
		
Snippet.cache = SnippetCache()

def invalidate_cache(sender, **kwargs):
	Snippet.cache.del_cache(kwargs['instance'].name)

post_save.connect(invalidate_cache, Snippet)
post_delete.connect(invalidate_cache, Snippet)
